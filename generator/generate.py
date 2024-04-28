#! /usr/bin/env python3

# Code generator for python ctypes bindings for VLC
#
# Copyright (C) 2009-2023 the VideoLAN team
# $Id: $
#
# Authors: Olivier Aubert <contact at olivieraubert.net>
#          Jean Brouwers <MrJean1 at gmail.com>
#          Geoff Salmon <geoff.salmon at gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston MA 02110-1301, USA.

"""This module parses VLC public API include files and generates
corresponding Python/ctypes bindingsB{**} code.  Moreover, it
generates Python class and method wrappers from the VLC functions
and enum types.

There are 3 dependencies.  Files C{header.py} and C{footer.py}
contain the pre- and postamble of the generated code.  Module
C{override.py} defines a number of classes and methods overriding
the ones to be generated.

This module and the generated Python bindings have been verified
with PyChecker 0.8.18, see U{http://pychecker.sourceforge.net}
and PyFlakes 0.4.0, see U{http://pypi.python.org/pypi/pyflakes}.
The C{#PYCHOK ...} comments direct the PyChecker/-Flakes post-
processor, see U{http://code.activestate.com/recipes/546532}.

This module and the generated Python bindings have been tested with
32- and 64-bit Python 2.6, 2.7 and 3.6 on Linux, Windows XP SP3, MacOS
X 10.4.11 (Intel) and MacOS X 10.11.3 using the public API include
files from VLC 1.1.4.1, 1.1.5, 2.1.0, 2.2.2, 3.0.3.

B{**)} Java/JNA bindings for the VLC public API can be created in a
similar manner and depend on 3 Java files: C{boilerplate.java},
C{LibVlc-footer.java} and C{LibVlc-header.java}. Note that this code
has not be maintained for a while...

"""

__all__ = ("Parser", "PythonGenerator", "JavaGenerator")

# Version number MUST have a major < 10 and a minor < 99 so that the
# generated dist version can be correctly generated.
__version__ = "2.0"

_debug = False

import operator
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import NamedTuple

from tree_sitter import Language, Node
from tree_sitter import Parser as TSParser

BASEDIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATEDIR = os.path.join(BASEDIR, "templates")
PREPROCESSEDDIR = os.path.join(BASEDIR, "preprocessed")
RUFF_CFG_FILE = os.path.join(os.path.dirname(BASEDIR), "ruff.toml")

str = str

try:
    basestring = basestring  # Python 2
except NameError:
    basestring = (str, bytes)  # Python 3

try:
    unicode = unicode  # Python 2
except NameError:
    unicode = str  # Python 3

if sys.version_info[0] < 3:
    PYTHON3 = False
    bytes = str

    def opener(name, mode="r"):
        return open(name, mode)
else:  # Python 3+
    PYTHON3 = True
    bytes = bytes

    def opener(name, mode="r"):  # PYCHOK expected
        return open(name, mode, encoding="utf8")


# Functions not wrapped/not referenced
_blacklist = {
    # Deprecated functions
    "libvlc_audio_output_set_device_type": "",
    "libvlc_audio_output_get_device_type": "",
    "libvlc_set_exit_handler": "",
    "libvlc_printerr": "",
    # Waiting for some structure wrapping
    "libvlc_dialog_set_callbacks": "",
    # Its signature is a mess
    "libvlc_video_direct3d_set_resize_cb": "",
    "libvlc_video_output_set_resize_cb": "",
    # It depends on the previous one
    "libvlc_video_direct3d_set_callbacks": "",
    "libvlc_video_set_output_callbacks": "",
}

# Set of functions that return a string that the caller is
# expected to free.
free_string_funcs = set(
    (
        "libvlc_media_discoverer_localized_name",
        "libvlc_media_get_mrl",
        "libvlc_media_get_meta",
        "libvlc_video_get_aspect_ratio",
        "libvlc_video_get_crop_geometry",
        "libvlc_video_get_marquee_string",
        "libvlc_audio_output_device_longname",
        "libvlc_audio_output_device_id",
        "libvlc_audio_output_device_get",
        "libvlc_vlm_show_media",
    )
)

# some constants
_NA_ = "N/A"
_NL_ = "\n"  # os.linesep
_OUT_ = "[OUT]"
_PNTR_ = "pointer to get the "  # KLUDGE: see @param ... [OUT]
_INDENT_ = "    "

# special keywords in header.py
_BUILD_DATE_ = "build_date  = "
_GENERATED_ENUMS_ = "# GENERATED_ENUMS"
_GENERATED_STRUCTS_ = "# GENERATED_STRUCTS"
_GENERATED_CALLBACKS_ = "# GENERATED_CALLBACKS"
_GENERATED_WRAPPERS_ = "# GENERATED_WRAPPERS"

# attributes
_ATTR_DEPRECATED_ = "__attribute__((deprecated))"
_ATTR_VISIBILITY_DEFAULT_ = '__attribute__((visibility("default")))'
_ATTR_DLL_EXPORT_ = "__declspec(dllexport)"

# Precompiled regexps
at_param_re = re.compile(r"(@param\s+\S+)(.+)")
bs_param_re = re.compile(r"\\param\s+(\S+)")
class_re = re.compile(r"class\s+(\S+?)(?:\(\S+\))?:")
def_re = re.compile(r"^\s+def\s+(\w+)", re.MULTILINE)
libvlc_re = re.compile(r"libvlc_[a-z_]+")


def endot(text):
    """Terminate string with a period."""
    if text and text[-1] not in ".,:;?!":
        text += "."
    return text


def errorf(fmt, *args):
    """Print error."""
    global _nerrors
    _nerrors += 1
    sys.stderr.write("Error: " + (fmt % args) + "\n")


_nerrors = 0


def errors(fmt, e=0):
    """Report total number of errors."""
    if _nerrors > e:
        n = _nerrors - e
        x = min(n, 9)
        errorf(fmt + "... exit(%s)", n, x)
        sys.exit(x)
    elif _debug:
        sys.stderr.write(fmt % (_NL_ + "No") + "\n")


# Adapted from https://gist.github.com/TACIXAT/c5b2db4a80c812c4b4373b65e179a220
def format_sexp(s_exp, indent_size=4):
    """Formats a Tree sitter S-expression for better readability."""

    indent_level = 0
    output = ""
    i = 0
    # Initialize to False to avoid newline for the first token
    need_newline = False
    cdepth = []  # Track colons

    while i < len(s_exp):
        if s_exp[i] == "(":
            if need_newline:
                output += "\n"
            output += " " * (indent_level * indent_size) + "("
            indent_level += 1
            need_newline = False  # Avoid newline after opening parenthesis
        elif s_exp[i] == ":":
            indent_level += 1
            cdepth.append(indent_level)  # Store depth where we saw colon
            output += ":"
        elif s_exp[i] == ")":
            indent_level -= 1
            if len(cdepth) > 0 and indent_level == cdepth[-1]:
                # Unindent when we return to the depth we saw the last colon
                cdepth.pop()
                indent_level -= 1
            output += ")"
            need_newline = True  # Newline needed after closing parenthesis
        elif s_exp[i] == " ":
            output += " "
        else:
            j = i
            while j < len(s_exp) and s_exp[j] not in ["(", ")", " ", ":"]:
                j += 1
            # Add newline and indentation only when needed
            if need_newline:
                output += "\n" + " " * (indent_level * indent_size)
            output += s_exp[i:j]
            i = j - 1
            need_newline = True  # Next token should start on a new line
        i += 1

    return output


def get_tsnode_sexp(tsnode):
    return format_sexp(tsnode.sexp())


def get_tsnode_text(tsnode, encoding="utf-8"):
    return tsnode.text.decode(encoding)


def get_children_by_type(tsnode, type):
    return list(filter(lambda child: child.type == type, tsnode.named_children))


def clean_doxygen_comment_block(docs):
    """This function assumes that the Doxygen comment block syntax used
    is the Javadoc style one, which consists of the block starting with /**.
    See https://www.doxygen.nl/manual/docblocks.html#cppblock for all the ways
    to mark a comment block.
    """
    if not docs.startswith("/**"):
        return ""

    lines = docs.split("\n")
    i = 0
    while i < len(lines):
        # remove the /** at the beginning of first line
        if i == 0:
            lines[i] = re.sub(r"/\*\*\s?", "", lines[i])
        # remove the */ at the end of last line
        if i == len(lines) - 1:
            lines[i] = re.sub(r"\s*\*/\s*", "", lines[i])
        # remove the * at the begining of in-between lines
        lines[i] = re.sub(r"^\s*\*\s?", "", lines[i])

        lines[i] = lines[i].strip()
        i += 1

    # remove potential empty lines at the beginning and end of comment block
    start = 0
    while start < len(lines) and lines[start] == "":
        start += 1
    end = len(lines) - 1
    while end >= 0 and lines[end] == "":
        end -= 1

    cleaned_docs = []
    for j in range(start, end + 1):
        cleaned_docs.append(lines[j])
    cleaned_docs = "\n".join(cleaned_docs)

    return cleaned_docs


def is_deprecated_attr(s: str):
    return s == _ATTR_DEPRECATED_


def is_public_attr(s: str):
    return s in [_ATTR_VISIBILITY_DEFAULT_, _ATTR_DLL_EXPORT_]


class _Source(object):
    """Base class for elements parsed from source."""

    source = ""

    def __init__(self, file_="", line=0):
        self.source = "%s:%s" % (file_, line)
        self.dump()  # PYCHOK expected


class Enum(_Source):
    """Enum type."""

    type = "enum"

    def __init__(self, name, type="enum", vals=(), docs="", **kwds):
        if type != self.type:
            raise TypeError("expected enum type: %s %s" % (type, name))
        self.docs = docs
        self.name = name
        self.vals = vals  # list/tuple of Val instances
        if _debug:
            _Source.__init__(self, **kwds)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Enum):
            return False

        res = self.name == other.name
        res &= self.type == other.type
        res &= self.docs == other.docs
        res &= sorted(self.vals, key=lambda v: v.name) == sorted(
            other.vals, key=lambda v: v.name
        )
        return res

    def __repr__(self) -> str:
        res = format("%s (%s): %s" % (self.name, self.type, self.source))
        for v in self.vals:
            res += "\n" + _INDENT_ + str(v)
        res += "\n"
        return res

    def check(self):
        """Perform some consistency checks."""
        if not self.docs:
            errorf("no comment for typedef %s %s", self.type, self.name)
        if self.type != "enum":
            errorf("expected enum type: %s %s", self.type, self.name)

    def dump(self):
        sys.stderr.write(str(self))

    def epydocs(self):
        """Return Sphinx (Napoleon) docstring."""
        return (
            self.docs.replace("@see", ":see:")
            .replace("\\see", ":see:")
            .replace("@ingroup", ":ingroup:")
            .replace("@defgroup", ":defgroup:")
            .replace("@file", ":file:")
            .replace("@{", "")
        )


class Struct(_Source):
    """Struct type."""

    type = "struct"

    def __init__(self, name, type="struct", fields=(), docs="", **kwds):
        if type != self.type:
            raise TypeError("expected struct type: %s %s" % (type, name))
        self.docs = docs
        self.name = name
        self.fields = fields  # list/tuple of Par instances
        if _debug:
            _Source.__init__(self, **kwds)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Struct):
            return False

        res = self.name == other.name
        res &= self.type == other.type
        res &= self.docs == other.docs
        res &= sorted(self.fields, key=lambda p: p.name) == sorted(
            other.fields, key=lambda p: p.name
        )
        return res

    def __repr__(self) -> str:
        res = format("STRUCT %s (%s): %s" % (self.name, self.type, self.source))
        for p in self.fields:
            res += "\n" + _INDENT_ + str(p)
        res += "\n"
        return res

    def check(self):
        """Perform some consistency checks."""
        if not self.docs:
            errorf("no comment for typedef %s %s", self.type, self.name)
        if self.type != "struct":
            errorf("expected struct type: %s %s", self.type, self.name)

    def dump(self, indent_lvl=0):
        for _ in range(indent_lvl):
            sys.stderr.write(_INDENT_)
        sys.stderr.write("STRUCT %s (%s): %s\n" % (self.name, self.type, self.source))
        for field in self.fields:
            field.dump(indent_lvl + 1)

    def epydocs(self):
        """Return Sphinx (Napoleon) docstring."""
        return self.docs.replace("@see", ":see:").replace("\\see", ":see:")


class Union(_Source):
    """Union type."""

    type = "union"

    def __init__(self, name, type="union", fields=(), docs="", **kwds):
        if type != self.type:
            raise TypeError("expected union type: %s %s" % (type, name))
        self.docs = docs
        self.name = name
        self.fields = fields
        if _debug:
            _Source.__init__(self, **kwds)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Union):
            return False

        res = self.name == other.name
        res &= self.type == other.type
        res &= self.docs == other.docs
        res &= sorted(self.fields, key=lambda p: p.name) == sorted(
            other.fields, key=lambda p: p.name
        )
        return res

    def __repr__(self) -> str:
        res = format("UNION %s (%s): %s" % (self.name, self.type, self.source))
        for p in self.fields:
            res += "\n" + _INDENT_ + str(p)
        res += "\n"
        return res

    def check(self):
        """Perform some consistency checks."""
        if self.type != "union":
            errorf("expected union type: %s %s", self.type, self.name)

    def dump(self, indent_lvl=0):
        for _ in range(indent_lvl):
            sys.stderr.write(_INDENT_)
        sys.stderr.write("UNION %s (%s): %s\n" % (self.name, self.type, self.source))
        for field in self.fields:
            field.dump(indent_lvl + 1)

    def epydocs(self):
        """Return Sphinx (Napoleon) docstring."""
        return self.docs.replace("@see", ":see:").replace("\\see", ":see:")


class Flag(object):
    """Enum-like, ctypes parameter direction flag constants."""

    In = 1  # input only
    Out = 2  # output only
    InOut = 3  # in- and output
    InZero = 4  # input, default int 0

    def __init__(self):
        raise TypeError("constants only")


class Func(_Source):
    """C function."""

    heads = ()  # docs lines without most @tags
    out = ()  # [OUT] parameter names
    params = ()  # @param lines, except [OUT]
    tails = ()  # @return, @version, @bug lines
    wrapped = 0  # number of times wrapped

    def __init__(self, name, type, pars=(), docs="", **kwds):
        self.docs = docs
        self.name = name
        self.pars = pars  # list/tuple of Par instances
        self.type = type
        if _debug:
            _Source.__init__(self, **kwds)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Func):
            return False

        res = self.name == other.name
        res &= self.type == other.type
        res &= self.docs == other.docs
        res &= sorted(self.pars, key=lambda x: x.name) == sorted(
            other.pars, key=lambda x: x.name
        )
        return res

    def __repr__(self) -> str:
        res = format("%s (%s): %s" % (self.name, self.type, self.source))
        for p in self.pars:
            res += "\n" + _INDENT_ + str(p)
        return res

    def args(self, first=0):
        """Return the parameter names, excluding output parameters.
        Ctypes returns all output parameter values as part of
        the returned tuple.
        """
        return [p.name for p in self.in_params(first)]

    def in_params(self, first=0):
        """Return the parameters, excluding output parameters.
        Ctypes returns all output parameter values as part of
        the returned tuple.
        """
        return [p for p in self.pars[first:] if p.flags(self.out)[0] != Flag.Out]

    def check(self):
        """Perform some consistency checks."""
        if not self.docs:
            errorf("no comment for function %s", self.name)
        elif len(self.pars) != self.nparams:
            errorf(
                "doc parameters (%d) mismatch for function %s (%d)",
                self.nparams,
                self.name,
                len(self.pars),
            )
            if _debug:
                self.dump()
                sys.stderr.write(self.docs + "\n")

    def dump(self, indent_lvl=0):
        for _ in range(indent_lvl):
            sys.stderr.write(_INDENT_)
        sys.stderr.write("%s (%s): %s\n" % (self.name, self.type, self.source))
        for p in self.pars:
            p.dump(indent_lvl + 1, self.out)

    def epydocs(self, first=0, indent=0):
        """Return epydoc doc string with/out first parameter."""
        # "out-of-bounds" slices are OK, e.g. ()[1:] == ()
        t = _NL_ + (" " * indent)
        return t.join(self.heads + self.params[first:] + self.tails)

    def __nparams_(self):
        return (len(self.params) + len(self.out)) or len(bs_param_re.findall(self.docs))

    nparams = property(__nparams_, doc="number of \\param lines in doc string")

    def xform(self):
        """Transform Doxygen to epydoc syntax."""
        b, c, h, o, p, r, v = [], None, [], [], [], [], []
        # see <http://epydoc.sourceforge.net/manual-fields.html>
        # (or ...replace('{', 'E{lb}').replace('}', 'E{rb}') ?)
        for t in (
            self.docs.replace("@{", "")
            .replace("@}", "")
            .replace("\\ingroup", "")
            .replace("{", "")
            .replace("}", "")
            .replace("<b>", "B{")
            .replace("</b>", "}")
            .replace("@see", "See")
            .replace("\\see", "See")
            .replace("\\bug", "@bug")
            .replace("\\version", "@version")
            .replace("\\note", "@note")
            .replace("\\warning", "@warning")
            .replace("\\param", "@param")
            .replace("\\return", "@return")
            .replace("NULL", "None")
            .splitlines()
        ):
            if "@param" in t:
                if _OUT_ in t:
                    # KLUDGE: remove @param, some comment and [OUT]
                    t = t.replace("@param", "").replace(_PNTR_, "").replace(_OUT_, "")
                    # keep parameter name and doc string
                    o.append(" ".join(t.split()))
                    c = [""]  # drop continuation line(s)
                else:
                    p.append(at_param_re.sub(r"\1:\2", t))
                    c = p
            elif "@return" in t:
                r.append(t.replace("@return ", "@return: "))
                c = r
            elif "@bug" in t:
                b.append(t.replace("@bug ", "@bug: "))
                c = b
            elif "@version" in t:
                v.append(t.replace("@version ", "@version: "))
                c = v
            elif c is None:
                h.append(
                    t.replace("@note ", "@note: ").replace("@warning ", "@warning: ")
                )
            else:  # continuation, concatenate to previous @tag line
                c[-1] = "%s %s" % (c[-1], t.strip())
        if h:
            h[-1] = endot(h[-1])
            self.heads = tuple(h)
        if o:  # just the [OUT] parameter names
            self.out = tuple(t.split()[0] for t in o)
            # ctypes returns [OUT] parameters as tuple
            r = ["@return: %s" % ", ".join(o)]
        if p:
            self.params = tuple(map(endot, p))
        t = r + v + b
        if t:
            self.tails = tuple(map(endot, t))

    def doxygen2sphinx(self):
        """Return Sphinx (Napoleon) docstring."""
        b, c, h, o, p, r, v = [], None, [], [], [], [], []
        param_re = re.compile(r":param\s+(?P<param_name>[^\s]+)")
        code_block_cpp = False
        # see <https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html#html-metadata>
        lines = (
            self.docs.replace("@{", "")
            .replace("@}", "")
            .replace("\\ingroup", "")
            .replace("{", "")
            .replace("}", "")
            .replace("<b>", "**")
            .replace("</b>", "**")
            .replace("@see", ":see:")
            .replace("\\see", ":see:")
            .replace("\\bug", ":bug:")
            .replace("@bug", ":bug:")
            .replace("\\version", ":version:")
            .replace("@version", ":version:")
            .replace("\\note", ":note:")
            .replace("@note", ":note:")
            .replace("\\warning", ":warning:")
            .replace("@warning", ":warning:")
            .replace("\\param", ":param")
            .replace("@param", ":param")
            .replace("\\return", ":return:")
            .replace("@return", ":return:")
            .replace("@ref", ":ref:")
            .replace("@code.mm", "\n.. code-block:: objectivec++")
            .replace("@code.m", ".. code-block:: objectivec++\n")
            .replace("@code", "\n.. code-block:: objectivec++\n")
            .replace("\@protocol", "@protocol")
            .replace("@endcode", "")
            .replace("\@end", "@end")
            .replace("NULL", "None")
            .splitlines()
        )
        for i in range(len(lines)):
            t = lines[i]
            if ".. code-block:: objectivec++" in t:
                if lines[i + 1].strip() == "":
                    code_block_cpp = True
                    empty_line_count = 0
            if code_block_cpp and t.strip() == "":
                empty_line_count += 1
                if empty_line_count == 3:
                    code_block_cpp = False
            if ":param" in t:
                if _OUT_ in t:
                    # KLUDGE: remove @param, some comment and [OUT]
                    t = t.replace(_PNTR_, "").replace(_OUT_, "")
                    # keep parameter name and doc string
                    o.append(" ".join(t.split()))
                    c = [""]  # drop continuation line(s)
                else:
                    p.append(param_re.sub(r":param \g<param_name>:", t))
                    c = p
            elif ":return:" in t:
                r.append(t)
                c = r
            elif ":bug:" in t:
                b.append(t)
                c = b
            elif ":version:" in t:
                v.append(t)
                c = v
            elif (
                code_block_cpp
                and ((empty_line_count == 1) or (empty_line_count == 2))
                and not t.startswith(".. code-block:: objectivec++")
            ):
                h.append("\t" + t)
            elif c is None:
                h.append(t)
            else:  # continuation, concatenate to previous @tag line
                c[-1] = "%s %s" % (c[-1], t.strip())
        if h:
            h[-1] = endot(h[-1])
            self.heads = tuple(h)
        if o:  # just the [OUT] parameter names
            self.out = tuple(t.split()[0] for t in o)
            # ctypes returns [OUT] parameters as tuple
            r = [":return: %s" % ", ".join(o)]
        if p:
            self.params = tuple(map(endot, p))
        t = r + v + b
        if t:
            self.tails = tuple(map(endot, t))


class Par(object):
    """C function parameter."""

    def __init__(self, name, type, constness):
        """
        constness:  a list of bools where each index refers to the constness
                    of that level of indirection.
                        [0] no indirection: is the value const?
                        [1] pointer to value: is this pointer const?
                        [2] pointer to pointer: is this pointer const?
                        ... rare to see more than two levels of indirection
        """
        self.name = name
        self.type = type  # C type
        self.constness = constness

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Par):
            return False

        res = self.name == other.name
        res &= self.type == other.type
        res &= self.constness == other.constness
        return res

    def __repr__(self):
        return "%s (%s) %s" % (self.name, self.type, self.constness)

    def dump(self, indent_lvl=0, out=()):
        for _ in range(indent_lvl):
            sys.stderr.write(_INDENT_)

        if self.name in out:
            t = _OUT_  # @param [OUT]
        else:
            t = {
                Flag.In: "",  # default
                Flag.Out: "Out",
                Flag.InOut: "InOut",
                Flag.InZero: "InZero",
            }.get(self.flags()[0], "FIXME_Flag")
        sys.stderr.write("%s %s\n" % (str(self), t))

    # Parameter passing flags for types.  This shouldn't
    # be hardcoded this way, but works all right for now.
    def flags(self, out=(), default=None):
        """Return parameter flags tuple.

        Return the parameter flags tuple for the given parameter
        type and name and a list of parameter names documented as
        [OUT].
        """
        if self.name in out:
            f = Flag.Out  # @param [OUT]
        elif not self.constness[0]:
            t_re = re.compile(
                r"(int *\*|unsigned *\*|unsigned char *\*|libvlc_media_track_info_t *\* *\*)"
            )
            f = Flag.Out if t_re.match(self.type) else Flag.In
        else:
            f = Flag.In

        if default is None:
            return (f,)  # 1-tuple
        else:  # see ctypes 15.16.2.4 Function prototypes
            return f, self.name, default  # PYCHOK expected


class Val(object):
    """Enum name and value."""

    def __init__(self, enum, value, docs="", context=None):
        self.enum = enum  # C name
        self.docs = docs
        # convert name
        t = enum.split("_")
        if context is not None:
            # A context (enum type name) is provided. Strip out the
            # common prefix.
            prefix = os.path.commonprefix((enum, re.sub(r"_t$", r"_", context)))
            n = enum.replace(prefix, "", 1)
        else:
            # No prefix. Fallback on the previous version (which
            # considers only the last _* portion of the name)
            n = t[-1]
        # Special case for debug levels and roles (with non regular name)
        n = re.sub(
            r"^(LIBVLC_|role_|marquee_|adjust_|AudioChannel_|AudioOutputDevice_)", "", n
        )
        if n[0].isdigit():  # can't start with a number
            n = "_" + n
        if n == "None":  # can't use a reserved python keyword
            n = "_" + n
        self.name = n
        self.value = value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Val):
            return False

        res = self.enum == other.enum
        res &= self.name == other.name
        res &= self.value == other.value
        res &= self.docs == other.docs
        return res

    def __repr__(self) -> str:
        return "%s = %s" % (self.name, self.value)

    def dump(self):  # for debug
        return str(self) + "\n"


class Overrides(NamedTuple):
    codes: dict
    methods: dict
    docstrs: dict


class Parser(object):
    """Parser of C header files."""

    def __init__(
        self,
        code_file: Path | str,
        version_file: Path | str,
        version: str = "",
        with_extra: bool = True,
    ):
        self.with_extra = with_extra
        if isinstance(code_file, str):
            code_file = Path(code_file)
        if isinstance(version_file, str):
            version_file = Path(version_file)
        self.code_file = code_file
        self.version_file = version_file

        Language.build_library(
            "build/c.so",
            ["vendor/tree-sitter-c"],
        )
        self.C_LANGUAGE = Language("build/c.so", "c")
        tsp = TSParser()
        tsp.set_language(self.C_LANGUAGE)

        with open(self.code_file, "rb") as file:
            self.code_tstree = tsp.parse(file.read())
        with open(self.version_file, "rb") as file:
            self.version_tstree = tsp.parse(file.read())

        self.enums = self.parse_enums()
        self.structs = self.parse_structs()
        self.funcs = self.parse_funcs()
        self.callbacks = self.parse_callbacks()
        self.version = version
        if not self.version:
            self.version = self.parse_version()

        # Sort parsed items by name as it proves
        # useful for debugging (diffing in particular)
        self.enums.sort(key=lambda x: x.name)
        self.funcs.sort(key=lambda x: x.name)
        self.callbacks.sort(key=lambda x: x.name)

        # self.dump("enums")
        # self.dump("structs")
        # self.dump("funcs")
        # self.dump("callbacks")

    def bindings_version(self):
        """Return the bindings version number.

        It is built from the VLC version number and the generator
        version number as:
        vlc_major.vlc_minor.(1000 * vlc_micro + 100 * generator_major + generator_minor)
        """
        major, minor = [int(i) for i in __version__.split(".")]
        bindings_version = "%s%d%02d" % (self.version, major, minor)
        return bindings_version

    def check(self):
        """Perform some consistency checks."""
        for e in self.enums:
            e.check()
        for f in self.funcs:
            f.check()
        for f in self.callbacks:
            f.check()
        for s in self.structs:
            s.check()

    def dump(self, attr):
        sys.stderr.write("==== %s ==== %s\n" % (attr, self.version))
        xs = getattr(self, attr)
        xs.sort(key=lambda x: x.name)
        for a in xs:
            a.dump()
        sys.stderr.write(_NL_)

    def parse_doxygen_comment(self, tsnode: Node):
        """
        @param tsnode: A Node for which to get the associated Doxygen doc
        comment.
        @return: A string containing the comment if it exists, None otherwise.
        """
        if tsnode.prev_sibling is not None and tsnode.prev_sibling.type == "comment":
            docs = get_tsnode_text(tsnode.prev_sibling)

            # Preprocessing can cause file documentation to be placed on top of an
            # enum, say, or any other item.
            # Because we assume that a Doxygen comment placed above an item is
            # documentation for that item, we can mistakenly associate a file's
            # documentation block to an item.
            # To filter out file documentation blocks, we rely on the assumption
            # that they start with "/***".
            # Indeed, libvld headers tend to start with something like:
            #   /*****************************************************************************
            #    * <filename>: <short_descrption>
            #    *****************************************************************************
            #    * Copyright (C) 1998-2008 VLC authors and VideoLAN
            #    * ...
            #    *****************************************************************************/
            if docs.startswith("/***"):
                return None

            docs = clean_doxygen_comment_block(docs)
            return docs
        return None

    def parse_type(self, tsnode: Node):
        """
        @param tsnode: A Node that is expected to have a direct
        child named _type_ (otherwise the function will throw).
        @return: A string representation of the type of `tsnode`,
        a 'constness' list of the type, and the last non-pointer
        declaration node encountered (in a tuple, in this order).
        """
        type_node = tsnode.child_by_field_name("type")
        assert (
            type_node is not None
        ), "Expected `tsnode` to have a direct child named _type_."

        constness = []
        t = get_tsnode_text(type_node)
        if (
            type_node.prev_sibling is not None
            and type_node.prev_sibling.type == "type_qualifier"
            and get_tsnode_text(type_node.prev_sibling) == "const"
        ) or (
            type_node.next_sibling is not None
            and type_node.next_sibling.type == "type_qualifier"
            and get_tsnode_text(type_node.next_sibling) == "const"
        ):
            constness.append(True)
        else:
            constness.append(False)

        decl_node = tsnode.child_by_field_name("declarator")
        while decl_node is not None and decl_node.type in [
            "pointer_declarator",
            "abstract_pointer_declarator",
        ]:
            t += "*"
            constness.append(False)
            type_qualifiers = get_children_by_type(decl_node, "type_qualifier")
            if len(type_qualifiers) > 0:
                type_qualifier_text = get_tsnode_text(type_qualifiers[0])
                if type_qualifier_text == "const":
                    constness[-1] = True
            decl_node = decl_node.child_by_field_name("declarator")

        # remove the struct keyword, this information is currently not used
        t = t.replace("struct ", "").strip()

        return t, constness, decl_node

    def parse_func_pointer(self, tsnode: Node):
        """
        @param tsnode: A Node that is expected to be a field_declaration
        with a subtree matching:
        (function_declarator
            declarator: (parenthesized_declarator (pointer_declarator))
            parameters: (parameter_list))
        @return: A Func representing a function pointer if `tsnode`
        matches the above query, or None otherwise.
        """
        query_func_p_str = """
(function_declarator
	declarator: (parenthesized_declarator (pointer_declarator))
    parameters: (parameter_list)) @func
"""
        query_func_p = self.C_LANGUAGE.query(query_func_p_str)
        func_caps = query_func_p.captures(tsnode)
        if not (len(func_caps) >= 1):
            return None
        # Assumes the first capture is the function we are
        # interested in, that is the one closest to the root of
        # `tsnode`.
        # Indeed, we can't enforce exactly one match because
        # a function pointer can have another function pointer
        # as parameter.
        func_decl = func_caps[0][0]

        query_func_id_str = """
declarator: (parenthesized_declarator
                (pointer_declarator
                    declarator: (_) @func_id))
        """
        query_func_id = self.C_LANGUAGE.query(query_func_id_str)
        func_id_caps = query_func_id.captures(func_decl)
        assert (
            len(func_id_caps) >= 1
        ), "There should be at least one identifier if we are indeed parsing a function pointer."
        # Assumes the first capture is the id of the function we are
        # interested in, that is the one closest to the root of
        # `tsnode`.
        # We can't enforce exactly one match for the same reason we
        # can't enforce exactly one match for the function
        # pointer query.
        name = get_tsnode_text(func_id_caps[0][0])

        type_node = tsnode.child_by_field_name("type")
        assert (
            type_node is not None
        ), "Expected `tsnode` to have a child of name _type_."
        return_type, _, _ = self.parse_type(tsnode)

        docs = self.parse_doxygen_comment(tsnode)
        if docs is None:
            docs = ""

        params = func_decl.child_by_field_name("parameters")
        assert (
            params is not None
        ), "Expected `func_decl` to have a child of name _parameters_."
        params = get_children_by_type(params, "parameter_declaration")
        params = [
            p for param in params for p in self.parse_param(param) if p is not None
        ]
        if len(params) == 1 and isinstance(params[0], Par) and params[0].type == "void":
            params = []

        return Func(
            name,
            return_type,
            params,
            docs,
            file_=self.code_file,
            line=tsnode.start_point[0] + 1,
        )

    def parse_callbacks(self):
        """Parse header file for callback signature definitions.

        @return: yield a Func instance for each callback signature, unless blacklisted.
        """
        typedef_query = self.C_LANGUAGE.query("""
(type_definition declarator: [
	(pointer_declarator)
    (function_declarator)
]) @typedef
""")
        typedef_captures = typedef_query.captures(self.code_tstree.root_node)
        func_query = self.C_LANGUAGE.query("(function_declarator) @func_decl")
        func_captures = []
        for typedef_node, _ in typedef_captures:
            func_decl_captures = func_query.captures(typedef_node)
            if len(func_decl_captures) >= 1:
                # Assumes the first capture is the function we are
                # interested in, that is the one closest to the root of
                # `tsnode`.
                # Indeed, we can't enforce exactly one match because
                # a callback (aka. function pointer) can have another function
                # pointer as parameter.
                func_captures.append((typedef_node, func_decl_captures[0][0]))

        funcs = []
        func_id_query = self.C_LANGUAGE.query(
            """
(function_declarator
    declarator: (parenthesized_declarator
                    (pointer_declarator
                        declarator: (type_identifier) @func_id)))
"""
        )
        for typedef_node, func_decl_node in func_captures:
            func_id_capture = func_id_query.captures(typedef_node)
            assert (
                len(func_id_capture) >= 1
            ), "Expected the query to capture at least one node."
            # Assumes the first capture is the id of the function we are
            # interested in, that is the one closest to the root of
            # `typedef_node`.
            # We can't enforce exactly one match for the same reason we
            # can't enforce exactly one match for the callback
            # (aka. function pointer) query.
            func_id_node = func_id_capture[0][0]
            assert (
                func_id_node is not None
            ), "Expected `func_id_node` to not be None. Maybe `typedef_node` doesn't have the structure assumed in `func_id_query`?"
            name = get_tsnode_text(func_id_node)

            # Make the assumption that every function of interest starts with 'libvlc_'.
            # Because the code parsed is the output of vlc.h's preprocessing, some signatures
            # come from external libraries and are not part of libvlc's API.
            if not name.startswith("libvlc_"):
                continue

            type_node = typedef_node.child_by_field_name("type")
            assert (
                type_node is not None
            ), "Expected `typedef_node` to have a child of name _type_."
            return_type, _, _ = self.parse_type(typedef_node)

            # Ignore if in blacklist
            if name in _blacklist:
                _blacklist[name] = return_type
                continue

            docs = self.parse_doxygen_comment(typedef_node)
            if docs is None:
                docs = ""

            params_nodes = func_decl_node.child_by_field_name("parameters")
            assert (
                params_nodes is not None
            ), "Expected `func_decl_node` to have a child of name _parameters_. Wrong query? Wrong field name for child?"
            params_decls = get_children_by_type(params_nodes, "parameter_declaration")
            params = [
                p
                for param_decl in params_decls
                for p in self.parse_param(param_decl)
                if p is not None
            ]
            if (
                len(params) == 1
                and isinstance(params[0], Par)
                and params[0].type == "void"
            ):
                params = []

            funcs.append(
                Func(
                    name,
                    return_type,
                    params,
                    docs,
                    file_=self.code_file,
                    line=typedef_node.start_point[0] + 1,
                )
            )

        return funcs

    def parse_enums(self):
        enum_query = self.C_LANGUAGE.query("(enum_specifier) @enum")
        enum_captures = enum_query.captures(self.code_tstree.root_node)

        enums = []
        for node, _ in enum_captures:
            parent = node.parent
            name = ""
            typ = "enum"
            docs = ""
            vals = []
            # add one because starts from zero by default
            line = node.start_point[0] + 1
            e = -1
            locs = {}

            # find enum's name
            if parent is not None and parent.type == "type_definition":
                type_id = parent.child_by_field_name("declarator")
                if type_id is not None and not type_id.is_missing:
                    name = get_tsnode_text(type_id)
            else:
                type_id = node.child_by_field_name("name")
                if type_id is not None:
                    name = get_tsnode_text(type_id)
            # ignore if anonymous enum
            if name == "":
                continue
            # Make the assumption that every enum of interest starts with 'libvlc_'.
            # Because the code parsed is the output of vlc.h's preprocessing, some signatures
            # come from external libraries and are not part of libvlc's API.
            if not name.startswith("libvlc_"):
                continue

            # find enum's docs
            if parent is not None and parent.type == "type_definition":
                docs = self.parse_doxygen_comment(parent)
            else:
                docs = self.parse_doxygen_comment(node)
            if docs is None:
                docs = ""

            # find enum's values
            body = node.child_by_field_name("body")
            if body is None:
                # we are dealing with an empty typedef enum
                continue
            for child in body.named_children:
                if child.type != "enumerator":
                    continue

                # Since libvlc v4.0.0, there are enum values
                # annotated with LIBVLC_DEPRECATED.
                # Tree-sitter fails to parse that attribute at
                # that place, producing an error in the subtree.
                # To workaround this problem, we assume that
                # when the `child` contains an error or is
                # followed by an error, it is because
                # LIBVLC_DEPRECATED is present.
                if child.has_error or (
                    child.next_sibling is not None and child.next_sibling.is_error
                ):
                    continue

                vname = child.child_by_field_name("name")
                assert (
                    vname is not None
                ), "Expected `child` to have a child of name _name_. `child` is not of type _enumerator_? Parsing malformed C code?"
                vname = get_tsnode_text(vname)

                vdocs = self.parse_doxygen_comment(child)
                if vdocs is None:
                    vdocs = ""

                vvalue = child.child_by_field_name("value")
                if vvalue is not None:
                    vvalue = get_tsnode_text(vvalue)

                    # Handle bit-shifted values.
                    # Bit-shifted characters cannot be directly evaluated in Python.
                    m = re.search(r"'(.)'\s*(<<|>>)\s*(.+)", vvalue)
                    if m:
                        vvalue = "%s %s %s" % (ord(m.group(1)), m.group(2), m.group(3))

                    # Handle expressions.
                    try:
                        e = eval(vvalue, locs)
                    except (SyntaxError, TypeError, ValueError):
                        errorf("%s %s (l.%s)", typ, name, line)
                        raise
                    locs[vname] = e

                    # Preserve hex values.
                    if vvalue[:2] in ("0x", "0X"):
                        vvalue = hex(e)
                    else:
                        vvalue = str(e)

                    vals.append(Val(vname, vvalue, vdocs, context=name))
                else:
                    e += 1
                    locs[vname] = e
                    vals.append(Val(vname, str(e), vdocs, context=name))

            enums.append(
                Enum(name, typ, vals, docs, file_=self.code_file.absolute(), line=line)
            )

        return enums

    def parse_param(self, tsnode: Node):
        """Returns a list of Par, Struct, Union and/or None.

        When `tsnode` is a parameter_declaration, the list returned will only contain
        one element being an instance of Par or Func.

        When `tsnode` is a field_declaration, the element can be a Struct/Union
        as well.
        Furthermore, if it happens to be an anonymous Struct/Union, a list containing
        the Struct/Union's fields will be returned instead of a list containing the
        Struct/Union.

        None can be part of the list only when the Parser option `with_extra` is False.
        In this case, nested structs/unions and function pointers as parameter/field are
        ignored, meaning None is returned instead.

        @param tsnode: A Node of type parameter_declaration or field_declaration.
        @return: A list of Par, Struct, Union and/or None
        """
        accepted_node_types = [
            "parameter_declaration",
            "field_declaration",
        ]
        accepted_node_types_list = " or ".join(accepted_node_types)
        assert (
            tsnode.type in accepted_node_types
        ), f"Expected `tsnode` to have type {accepted_node_types_list}, but got {tsnode.type}."

        type_node = tsnode.child_by_field_name("type")
        assert (
            type_node is not None
        ), "Expected `tsnode` to have a child of name _type_. Typo? Wrong assumption about `tsnode`?"

        result = None
        if type_node.type == "struct_specifier":
            result = self.parse_nested_struct(tsnode)
        elif type_node.type == "union_specifier":
            result = self.parse_nested_union(tsnode)
        if result is not None:
            if self.with_extra:
                # if anonymous struct/union, return the fields directly
                if len(result.name) == 0:
                    return result.fields
                else:
                    return [result]
            else:
                return [None]

        t, constness, decl_node = self.parse_type(tsnode)

        name = ""
        if decl_node is not None:
            # Check if we are dealing with a function pointer.
            if decl_node.type == "function_declarator":
                if self.with_extra:
                    return [self.parse_func_pointer(tsnode)]
                else:
                    return [None]

            # Otherwise assume that the first non-pointer declaration is the declaration
            # for the identifier/field_identifier, or is None.
            name = get_tsnode_text(decl_node)

        return [Par(name, t, constness)]

    def parse_nested_struct(self, tsnode: Node):
        """Returns a Struct representing a nested structure if `tsnode`
        has the right structure, or None otherwise.

        @param tsnode: An instance of Node that is expected to match:
        (field_declaration
            type:
                (struct_specifier body: (field_declaration_list)))
        @return: A Struct if `tsnode` matches the above query, or
        None otherwise.
        """
        query_str = """
(field_declaration
	type:
        (struct_specifier body: (field_declaration_list))) @field
"""
        query_nested_struct_or_union = self.C_LANGUAGE.query(query_str)
        caps = query_nested_struct_or_union.captures(tsnode)

        # We don't want to match subtrees, we only want to match `tsnode`.
        # Unfortunately, there is no way to do this given the current Tree sitter API,
        # so we assume that the first match of type field_declaration is `tsnode`.
        if not (len(caps) != 0 and caps[0][0].type == "field_declaration"):
            return None

        assert (
            caps[0][0].id == tsnode.id
        ), "Assumed that the first capture was `tsnode`, but it is not the case."

        type_node = tsnode.child_by_field_name("type")
        assert (
            type_node is not None
        ), "Child _type_ should exist if `tsnode` matched the query."
        body = type_node.child_by_field_name("body")
        assert (
            body is not None
        ), "Child _body_ should exist if `tsnode` matched the query."

        docs = self.parse_doxygen_comment(tsnode)
        if docs is None:
            docs = ""

        declarator = tsnode.child_by_field_name("declarator")
        name = "" if declarator is None else get_tsnode_text(declarator)

        fields = [
            f
            for decl in get_children_by_type(body, "field_declaration")
            for f in self.parse_param(decl)
            if f is not None
        ]

        return Struct(
            name,
            "struct",
            fields,
            docs,
            file_=self.code_file.absolute(),
            line=tsnode.start_point[0] + 1,
        )

    def parse_nested_union(self, tsnode: Node):
        """Returns a Union representing a nested union if `tsnode`
        has the right structure, or None otherwise.

        @param tsnode: An instance of Node that is expected to match:
        (field_declaration
            type:
                (union_specifier body: (field_declaration_list)))
        @return: A Union if `tsnode` matches the above query, or
        None otherwise.
        """
        query_str = """
(field_declaration
	type:
        (union_specifier body: (field_declaration_list))) @field
"""
        query_nested_struct_or_union = self.C_LANGUAGE.query(query_str)
        caps = query_nested_struct_or_union.captures(tsnode)

        # We don't want to match subtrees, we only want to match `tsnode`.
        # Unfortunately, there is no way to do this given the current Tree sitter API,
        # so we assume that the first match of type field_declaration is `tsnode`.
        if not (len(caps) != 0 and caps[0][0].type == "field_declaration"):
            return None

        assert (
            caps[0][0].id == tsnode.id
        ), "Assumed that the first capture was `tsnode`, but it is not the case."

        type_node = tsnode.child_by_field_name("type")
        assert (
            type_node is not None
        ), "Child _type_ should exist if `tsnode` matched the query."
        body = type_node.child_by_field_name("body")
        assert (
            body is not None
        ), "Child _body_ should exist if `tsnode` matched the query."

        docs = self.parse_doxygen_comment(tsnode)
        if docs is None:
            docs = ""

        declarator = tsnode.child_by_field_name("declarator")
        name = "" if declarator is None else get_tsnode_text(declarator)

        fields = [
            f
            for decl in get_children_by_type(body, "field_declaration")
            for f in self.parse_param(decl)
            if f is not None
        ]

        return Union(
            name,
            "union",
            fields,
            docs,
            file_=self.code_file.absolute(),
            line=tsnode.start_point[0] + 1,
        )

    def parse_structs(self):
        """Parse header file for struct definitions.

        @return: yield a Struct instance for each struct.
        """

        struct_query = self.C_LANGUAGE.query("(struct_specifier) @struct")
        struct_captures = struct_query.captures(self.code_tstree.root_node)

        structs = []
        for node, _ in struct_captures:
            parent = node.parent
            name = ""
            typ = "struct"
            docs = ""
            fields = []

            # Add one because starts from zero by default
            line = node.start_point[0] + 1

            # Find and extract struct name
            if parent is not None and parent.type == "type_definition":
                type_id = parent.child_by_field_name("declarator")
                if type_id is not None and not type_id.is_missing:
                    name = get_tsnode_text(type_id)
            else:
                type_id = node.child_by_field_name("name")
                if type_id is not None:
                    name = get_tsnode_text(type_id)
            # ignore if anonymous struct
            if name == "":
                continue
            # ignore if not a struct from libvlc
            if not name.startswith("libvlc_"):
                continue

            # Find structs documentation
            if parent is not None and parent.type == "type_definition":
                docs = self.parse_doxygen_comment(parent)
            else:
                docs = self.parse_doxygen_comment(node)
            if docs is None:
                docs = ""

            # Find struct's fields
            body = node.child_by_field_name("body")
            if body is not None:
                fields = [
                    f
                    for decl in get_children_by_type(body, "field_declaration")
                    for f in self.parse_param(decl)
                    if f is not None
                ]

            # Ignore empty structs
            if len(fields) == 0:
                continue

            structs.append(
                Struct(
                    name, typ, fields, docs, file_=self.code_file.absolute(), line=line
                )
            )

        return structs

    def parse_funcs(self):
        """Parse header file for public function definitions.

        @return: yield a Func instance for each function, unless blacklisted.
        """
        decl_query = self.C_LANGUAGE.query("(declaration) @decl")
        decl_captures = decl_query.captures(self.code_tstree.root_node)
        func_query = self.C_LANGUAGE.query("(function_declarator) @func_decl")
        func_captures = []
        for decl_node, _ in decl_captures:
            func_decl_captures = func_query.captures(decl_node)
            if len(func_decl_captures) >= 1:
                func_captures.append((decl_node, func_decl_captures[0][0]))

        funcs = []
        for decl_node, func_decl_node in func_captures:
            func_id_node = func_decl_node.child_by_field_name("declarator")
            assert (
                func_id_node is not None
            ), "Expected `func_decl_node` to have a child of name _declarator_. Wrong query? Typo for child field name?"
            name = get_tsnode_text(func_id_node)

            # Make the assumption that every function of interest starts with 'libvlc_'.
            # Because the code parsed is the output of vlc.h's preprocessing, some signatures
            # come from external libraries and are not part of libvlc's API.
            if not name.startswith("libvlc_"):
                continue

            type_node = decl_node.child_by_field_name("type")
            assert (
                type_node is not None
            ), "Expected `decl_node` to have a child of name _type_."
            return_type, _, _ = self.parse_type(decl_node)

            # Ignore if in blacklist
            if name in _blacklist:
                _blacklist[name] = return_type
                continue

            _deprecated = False
            in_api = False
            attributes = get_children_by_type(decl_node, "attribute_specifier")
            ms_declspecs = get_children_by_type(decl_node, "ms_declspec_modifier")
            for a in attributes + ms_declspecs:
                a_txt = get_tsnode_text(a)
                if is_deprecated_attr(a_txt):
                    _deprecated = True
                if is_public_attr(a_txt):
                    in_api = True

            if not in_api:
                continue

            docs = self.parse_doxygen_comment(decl_node)
            if docs is None:
                docs = ""

            params_nodes = func_decl_node.child_by_field_name("parameters")
            assert (
                params_nodes is not None
            ), "Expected `func_decl_node` to have a child of name _parameters_. Wrong query? Typo for child field name?"
            params_decls = get_children_by_type(params_nodes, "parameter_declaration")
            params = [
                p
                for param_decl in params_decls
                for p in self.parse_param(param_decl)
                if p is not None
            ]
            if (
                len(params) == 1
                and isinstance(params[0], Par)
                and params[0].type == "void"
            ):
                params = []

            funcs.append(
                Func(
                    name,
                    return_type,
                    params,
                    docs,
                    file_=self.code_file.absolute(),
                    line=decl_node.start_point[0] + 1,
                )
            )

        return funcs

    def parse_version(self):
        """Get the libvlc version from the C header files:
        LIBVLC_VERSION_MAJOR, _MINOR, _REVISION, _EXTRA
        """
        macro_query = self.C_LANGUAGE.query("(preproc_def) @macro")
        macros = macro_query.captures(self.version_tstree.root_node)

        version = None
        version_numbers = {
            "LIBVLC_VERSION_MAJOR": -1,
            "LIBVLC_VERSION_MINOR": -1,
            "LIBVLC_VERSION_REVISION": -1,
            "LIBVLC_VERSION_EXTRA": -1,
        }
        for macro, _ in macros:
            name = get_tsnode_text(macro.child_by_field_name("name"))
            if name in version_numbers:
                version_numbers[name] = int(
                    get_tsnode_text(macro.child_by_field_name("value"))[1:-1]
                )

        if (
            version_numbers["LIBVLC_VERSION_MAJOR"] >= 0
            and version_numbers["LIBVLC_VERSION_MINOR"] >= 0
            and version_numbers["LIBVLC_VERSION_REVISION"] >= 0
        ):
            version = f"{version_numbers['LIBVLC_VERSION_MAJOR']}.{version_numbers['LIBVLC_VERSION_MINOR']}.{version_numbers['LIBVLC_VERSION_REVISION']}"
            if version_numbers["LIBVLC_VERSION_EXTRA"] > 0:
                version += f".{version_numbers['LIBVLC_VERSION_EXTRA']}"

        # Version was not found in include files themselves. Try other
        # approaches.
        if version is None:
            # Try to get version information from git describe
            git_dir = self.version_file.absolute().parents[2].joinpath(".git")
            if git_dir.is_dir():
                # We are in a git tree. Let's get the version information
                # from there if we can call git
                try:
                    version = (
                        subprocess.check_output(
                            ["git", "--git-dir=%s" % git_dir.as_posix(), "describe"]
                        )
                        .strip()
                        .decode("utf-8")
                    )
                except:
                    pass

        return version


class _Generator(object):
    """Base class."""

    comment_line = "#"  # Python
    file = None
    links = {}  # must be overloaded
    outdir = ""
    outpath = ""
    type_re = None  # must be overloaded
    type2class = {}  # must be overloaded
    type2class_out = {}  # Specific values for OUT parameters

    def __init__(self, parser: Parser):
        self.parser = parser
        for struct in parser.structs:
            self.name_to_classname(struct)
        for enum in parser.enums:
            self.name_to_classname(enum)
        for cb in parser.callbacks:
            self.name_to_classname(cb)

    def check_types(self):
        """Make sure that all types are properly translated.

        @note: This method must be called B{after} C{convert_enums},
        since the latter populates C{type2class} with enum class names.
        """
        e = _nerrors
        for f in self.parser.funcs:
            if f.type not in self.type2class:
                errorf("no type conversion for %s %s", f.type, f.name)
            for p in f.pars:
                if p.type not in self.type2class:
                    errorf("no type conversion for %s %s in %s", p.type, p.name, f.name)
        errors("%s type conversion(s) missing", e)

    def class4(self, type, flag=None):
        """Return the class name for a type or enum."""
        cl = None
        if flag == Flag.Out:
            cl = self.type2class_out.get(type)
        if cl is None:
            cl = self.type2class.get(
                type, "FIXME_%s%s" % ("OUT_" if flag == Flag.Out else "", type)
            )
        return cl

    def name_to_classname(self, item):
        """Puts the Python class name corresponding to the
        `item`'s name in `self.type2class`.

        @param: An `Enum`, `Struct`, `Union` or `Func`.
        """
        if item.name in self.type2class:
            # Do not override predefined values
            return

        c = self.type_re.findall(item.name)
        if c:
            c = c[0][0]
        else:
            c = item.name
        if "_" in c:
            c = c.title().replace("_", "")
        elif c[0].islower():
            c = c.capitalize()
        self.type2class[item.name] = c
        self.type2class[item.name + "*"] = f"ctypes.POINTER({c})"
        self.type2class[item.name + "**"] = f"ctypes.POINTER(ctypes.POINTER({c}))"

    def dump_dicts(self):  # for debug
        s = _NL_ + _INDENT_
        for n in ("type2class", "prefixes", "links"):
            d = getattr(self, n, None)
            if d:
                n = ["%s==== %s ==== %s" % (_NL_, n, self.parser.bindings_version())]
                sys.stderr.write(s.join(n + sorted("%s: %s\n" % t for t in d.items())))

    def epylink(self, docs, striprefix=None):
        """Link function, method and type names in doc string."""

        def _L(m):  # re.sub callback
            t = m.group(0)
            n = t.strip()
            k = self.links.get(n, "")
            if k:
                if striprefix:
                    k = striprefix(k)
                t = t.replace(n, "L{%s}" % (k,))
            return t

        if self.links:
            return libvlc_re.sub(_L, docs)
        else:
            return docs

    def generate_enums(self):
        raise TypeError("must be overloaded")

    def generate_structs(self):
        raise TypeError("must be overloaded")

    def generate_callbacks(self):
        raise TypeError("must be overloaded")

    def generate_wrappers(self):
        raise TypeError("must be overloaded")

    def insert_code(self, source, genums=False):
        """Include code from source file."""
        f = opener(source)
        for t in f:
            if genums and t.startswith(_GENERATED_ENUMS_):
                self.generate_enums()
            elif genums and t.startswith(_GENERATED_STRUCTS_):
                self.generate_structs()
            elif genums and t.startswith(_GENERATED_CALLBACKS_):
                self.generate_callbacks()
            elif genums and t.startswith(_GENERATED_WRAPPERS_):
                self.generate_wrappers()
            elif t.startswith(_BUILD_DATE_):
                v = self.parser.version or _NA_
                self.output('__version__ = "%s"' % (self.parser.bindings_version(),))
                self.output('__libvlc_version__ = "%s"' % (v,))
                self.output('__generator_version__ = "%s"' % (__version__,))
                self.output('%s"%s %s"' % (_BUILD_DATE_, time.ctime(), v))
            else:
                self.output(t, nt=0)
        f.close()

    def outclose(self):
        """Close the output file."""
        if self.file not in (None, sys.stdout):
            self.file.close()
        self.file = None

    def outopen(self, name):
        """Open an output file."""
        if self.file:
            self.outclose()
            raise IOError("file left open: %s" % (self.outpath,))

        if name in ("-", "stdout"):
            self.outpath = "stdout"
            self.file = sys.stdout
        else:
            self.outpath = os.path.join(self.outdir, name)
            self.file = opener(self.outpath, "w")

    def output(self, text, nl=0, nt=1):
        """Write to current output file."""
        if nl:  # leading newlines
            self.file.write(_NL_ * nl)
        self.file.write(text)
        if nt:  # trailing newlines
            self.file.write(_NL_ * nt)

    def unwrapped(self):
        """Report the unwrapped and blacklisted functions."""
        b = [f for f, t in _blacklist.items() if t]
        u = [f.name for f in self.parser.funcs if not f.wrapped]
        c = self.comment_line
        for f, t in ((b, "blacklisted"), (u, "not wrapped as methods")):
            if f:
                self.output("%s %d function(s) %s:" % (c, len(f), t), nl=1)
                self.output(
                    _NL_.join("%s  %s" % (c, f) for f in sorted(f))
                )  # PYCHOK false?


class PythonGenerator(_Generator):
    """Generate Python bindings."""

    type_re = re.compile(r"libvlc_(.+?)(_t)?$")  # Python

    # C-type to Python/ctypes type conversion.  Note, enum
    # type conversions are generated (cf convert_enums).
    type2class = {
        "libvlc_audio_output_t*": "ctypes.POINTER(AudioOutput)",
        "libvlc_event_t*": "ctypes.c_void_p",
        #'libvlc_callback_t':           'ctypes.c_void_p',
        "libvlc_dialog_id*": "ctypes.c_void_p",
        "libvlc_drawable_t": "ctypes.c_uint",  # FIXME?
        "libvlc_event_type_t": "ctypes.c_uint",
        "libvlc_event_manager_t*": "EventManager",
        "libvlc_instance_t*": "Instance",
        "libvlc_log_t*": "Log_ptr",
        "libvlc_log_iterator_t*": "LogIterator",
        "libvlc_log_subscriber_t*": "ctypes.c_void_p",  # Opaque struct, do not mess with it.
        "libvlc_log_message_t*": "ctypes.POINTER(LogMessage)",
        "libvlc_media_track_t**": "ctypes.POINTER(MediaTrack)",
        "libvlc_media_track_t***": "ctypes.POINTER(ctypes.POINTER(MediaTrack))",
        "libvlc_media_t*": "Media",
        "libvlc_media_discoverer_t*": "MediaDiscoverer",
        "libvlc_media_discoverer_description_t**": "ctypes.POINTER(ctypes.POINTER(MediaDiscovererDescription))",
        "libvlc_media_discoverer_description_t***": "ctypes.POINTER(ctypes.POINTER(ctypes.POINTER(MediaDiscovererDescription)))",
        "libvlc_media_library_t*": "MediaLibrary",
        "libvlc_media_list_t*": "MediaList",
        "libvlc_media_list_player_t*": "MediaListPlayer",
        "libvlc_media_list_view_t*": "MediaListView",
        "libvlc_media_player_t*": "MediaPlayer",
        "libvlc_video_viewpoint_t*": "ctypes.POINTER(VideoViewpoint)",
        "libvlc_media_stats_t*": "ctypes.POINTER(MediaStats)",
        "libvlc_picture_t*": "Picture",
        "libvlc_media_thumbnail_request_t*": "MediaThumbnailRequest",  # Opaque struct, do not mess with it.
        "libvlc_renderer_item_t*": "Renderer",
        "libvlc_renderer_discoverer_t*": "RendererDiscoverer",
        "libvlc_rd_description_t**": "ctypes.POINTER(ctypes.POINTER(RdDescription))",
        "libvlc_rd_description_t***": "ctypes.POINTER(ctypes.POINTER(ctypes.POINTER(RdDescription)))",
        "libvlc_media_track_info_t**": "ctypes.POINTER(ctypes.c_void_p)",
        "libvlc_rectangle_t*": "ctypes.POINTER(Rectangle)",
        "libvlc_time_t": "ctypes.c_longlong",
        "libvlc_track_description_t*": "ctypes.POINTER(TrackDescription)",
        "libvlc_title_description_t**": "ctypes.POINTER(TitleDescription)",
        "libvlc_title_description_t***": "ctypes.POINTER(ctypes.POINTER(TitleDescription))",
        "libvlc_chapter_description_t**": "ctypes.POINTER(ChapterDescription)",
        "libvlc_chapter_description_t***": "ctypes.POINTER(ctypes.POINTER(ChapterDescription))",
        "libvlc_module_description_t*": "ctypes.POINTER(ModuleDescription)",
        "libvlc_audio_output_device_t*": "ctypes.POINTER(AudioOutputDevice)",
        "libvlc_equalizer_t*": "AudioEqualizer",
        "libvlc_media_slave_t**": "ctypes.POINTER(MediaSlave)",
        "libvlc_media_slave_t***": "ctypes.POINTER(ctypes.POINTER(MediaSlave))",
        "libvlc_video_direct3d_device_setup_t*": "Direct3dDeviceSetup",
        "libvlc_video_direct3d_device_cfg_t*": "Direct3dDeviceCfg",
        "libvlc_video_direct3d_cfg_t*": "Direct3dCfg",
        "libvlc_video_output_cfg_t*": "VideoOutputCfg",
        "libvlc_video_setup_device_cfg_t*": "VideoSetupDeviceCfg",
        "libvlc_video_setup_device_info_t*": "VideoSetupDeviceInfo",
        "libvlc_video_render_cfg_t*": "VideoRenderCfg",
        "libvlc_video_direct3d_hdr10_metadata_t*": "Direct3dHdr10Metadata",
        "libvlc_media_tracklist_t*": "ctypes.c_void_p",  # Opaque struct, do not mess with it.
        "libvlc_media_programlist_t*": "ctypes.c_void_p",  # Opaque struct, do not mess with it.
        "libvlc_player_programlist_t*": "ctypes.c_void_p",  # Opaque struct, do not mess with it.
        "libvlc_picture_list_t*": "ctypes.c_void_p",  # Opaque struct, do not mess with it.
        # FIXME Temporary fix to generate valid code for the mapping of
        # libvlc_media_read_cb
        "ptrdiff_t": "ctypes.c_void_p",
        "FILE*": "FILE_ptr",
        "...": "ctypes.c_void_p",
        "va_list": "ctypes.c_void_p",
        "char*": "ctypes.c_char_p",
        "unsigned char*": "ctypes.c_char_p",
        "_Bool": "ctypes.c_bool",
        "_Bool*": "ctypes.POINTER(ctypes.c_bool)",
        "char**": "ListPOINTER(ctypes.c_char_p)",
        "char***": "ctypes.POINTER(ListPOINTER(ctypes.c_char_p))",
        "double": "ctypes.c_double",
        "double*": "ctypes.POINTER(ctypes.c_double)",
        "float": "ctypes.c_float",
        "int": "ctypes.c_int",
        "int*": "ctypes.POINTER(ctypes.c_int)",  # _video_get_cursor
        "uintptr_t*": "ctypes.POINTER(ctypes.c_uint)",
        "uint16_t": "ctypes.c_uint16",
        "int64_t": "ctypes.c_int64",
        "int64_t*": "ctypes.POINTER(ctypes.c_int64)",
        "uint64_t": "ctypes.c_uint64",
        "uint64_t*": "ctypes.POINTER(ctypes.c_uint64)",
        "short": "ctypes.c_short",
        "uint32_t": "ctypes.c_uint32",
        "ssize_t": "ctypes.c_ssize_t",
        "size_t": "ctypes.c_size_t",
        "size_t*": "ctypes.POINTER(ctypes.c_size_t)",
        "ssize_t*": "ctypes.POINTER(ctypes.c_ssize_t)",
        "unsigned": "ctypes.c_uint",
        "unsigned int": "ctypes.c_uint",
        "unsigned*": "ctypes.POINTER(ctypes.c_uint)",  # _video_get_size
        "void": "None",
        "void*": "ctypes.c_void_p",
        "void**": "ctypes.POINTER(ctypes.c_void_p)",
        "WINDOWHANDLE": "ctypes.c_ulong",
    }

    type2class_out = {
        "char**": "ctypes.POINTER(ctypes.c_char_p)",
        "unsigned char*": "ctypes.POINTER(ctypes.c_char)",
    }

    # Python classes, i.e. classes for which we want to
    # generate class wrappers around libvlc functions
    defined_classes = (
        "AudioEqualizer",
        "EventManager",
        "Instance",
        "Log",
        "LogIterator",
        "Media",
        "MediaDiscoverer",
        "MediaLibrary",
        "MediaList",
        "MediaListPlayer",
        "MediaListView",
        "MediaPlayer",
        "Picture",
        "Renderer",
        "RendererDiscoverer",
    )

    def __init__(self, parser: Parser):
        """New instance.

        @param parser: a L{Parser} instance.
        """
        _Generator.__init__(self, parser)

        # Load override definitions
        self.overrides = self.parse_override(os.path.join(TEMPLATEDIR, "override.py"))

        # one special enum type class
        self.type2class["libvlc_event_e"] = "EventType"
        # doc links to functions, methods and types
        self.links = {"libvlc_event_e": "EventType"}
        # link enum value names to enum type/class
        for t in self.parser.enums:
            self.links[t.name] = self.class4(t.name)
        # prefixes to strip from method names
        # when wrapping them into class methods
        self.prefixes = {}
        for t, c in self.type2class.items():
            t = t.rstrip("*")
            if c in self.defined_classes:
                self.links[t] = c
                self.prefixes[c] = t[:-1]
            elif c.startswith("ctypes.POINTER("):
                c = c.replace("ctypes.POINTER(", "").rstrip(")")
                if c[:1].isupper():
                    self.links[t] = c
        # We have to hardcode this one, which is not regular in vlc headers
        self.prefixes["AudioEqualizer"] = "libvlc_audio_equalizer_"

        # xform docs to epydoc lines
        for f in self.parser.funcs:
            # f.xform()
            f.doxygen2sphinx()
            self.links[f.name] = f.name
        for f in self.parser.callbacks:
            # f.xform()
            f.doxygen2sphinx()
        self.check_types()

    def generate_ctypes(self):
        """Generate a ctypes decorator for all functions."""
        self.output("""
 # LibVLC __version__ functions #
""")
        for f in self.parser.funcs:
            name = f.name  # PYCHOK flake

            # arg names, excluding output args
            args = ", ".join(f.args())  # PYCHOK flake

            # tuples of arg flags
            flags = ", ".join(str(p.flags(f.out)) for p in f.pars)  # PYCHOK false?
            if flags:
                flags += ","

            # arg classes
            types = [self.class4(p.type, p.flags(f.out)[0]) for p in f.pars]

            # result type
            rtype = self.class4(f.type)

            if name in free_string_funcs:
                # some functions that return strings need special treatment
                if rtype != "ctypes.c_char_p":
                    raise TypeError(
                        "Function %s expected to return char* not %s" % (name, f.type)
                    )
                errcheck = "string_result"
                types = ["ctypes.c_void_p"] + types
            elif rtype in self.defined_classes:
                # if the result is a pointer to one of the defined
                # classes then we tell ctypes that the return type is
                # ctypes.c_void_p so that 64-bit pointers are handled
                # correctly, and then create a Python object of the
                # result
                errcheck = "class_result(%s)" % rtype
                types = ["ctypes.c_void_p"] + types
            else:
                errcheck = "None"
                types.insert(0, rtype)

            types = ", ".join(types)

            # xformed doc string with first @param
            docs = self.epylink(f.epydocs(0, 4))  # PYCHOK flake
            self.output(
                """def %(name)s(%(args)s):
    '''%(docs)s
    '''
    f = _Cfunctions.get('%(name)s', None) or \\
        _Cfunction('%(name)s', (%(flags)s), %(errcheck)s,
                    %(types)s)
    return f(%(args)s)
"""
                % locals()
            )

    def generate_enums(self):
        """Generate classes for all enum types."""
        self.output("""
class _Enum(ctypes.c_uint):
    '''(INTERNAL) Base class
    '''
    _enum_names_ = {}

    def __str__(self):
        n = self._enum_names_.get(self.value, '') or ('FIXME_(%r)' % (self.value,))
        return '.'.join((self.__class__.__name__, n))

    def __hash__(self):
        return self.value

    def __repr__(self):
        return '.'.join((self.__class__.__module__, self.__str__()))

    def __eq__(self, other):
        return ( (isinstance(other, _Enum) and self.value == other.value)
              or (isinstance(other, _Ints) and self.value == other) )

    def __ne__(self, other):
        return not self.__eq__(other)
""")
        for e in self.parser.enums:
            cls = self.class4(e.name)
            self.output(
                """class %s(_Enum):
    '''%s
    '''
    _enum_names_ = {"""
                % (cls, e.epydocs() or _NA_)
            )

            for v in e.vals:
                self.output("        %s: '%s'," % (v.value, v.name))
            self.output("    }")

            # align on '=' signs
            w = -max(len(v.name) for v in e.vals)
            t = ["%s.%*s = %s(%s)" % (cls, w, v.name, cls, v.value) for v in e.vals]

            self.output(_NL_.join(sorted(t)), nt=2)

    def generate_func_pointer_decorator(self, pf: Func, indent_lvl: int = 0):
        """Generates a declarator for a struct/union field that is a function pointer.

        @param pf: A field that is a function pointer (instance of Func).
        @param indent_lvl: A positive integer representing how many indentations
        should precede each line generated.
        """
        indent = _INDENT_ * indent_lvl
        name = self.class4(pf.name)
        # return value and arg classes
        types = ", ".join(
            [self.class4(pf.type)]  # PYCHOK flake
            + [self.class4(p.type, p.flags(pf.out)[0]) for p in pf.pars]
        )
        docs = pf.epydocs()
        self.output(f"""{indent}{_INDENT_}{name} = ctypes.CFUNCTYPE({types})
{indent}{_INDENT_}{name}.__doc__ = '''{docs}'''""")
        self.output("")

    def generate_struct(self, struct: Struct, indent_lvl: int = 0):
        """Outputs a binding for `struct`.

        @param struct: The `Struct` instance for which to output the binding.
        @param indent_lvl: A positive integer representing how many indentations
        should precede each line generated.
        """
        indent = _INDENT_ * indent_lvl
        cls = self.class4(struct.name)

        # We use a forward declaration here to allow for self-referencing structures - cf
        # https://docs.python.org/3/library/ctypes.html#ctypes.Structure._fields_
        self.output(f"""{indent}class {cls}(_Cstruct):
{indent}{_INDENT_}'''{struct.epydocs() or _NA_}
{indent}{_INDENT_}'''""")

        for field in struct.fields:
            if isinstance(field, Struct):
                self.name_to_classname(field)
                self.generate_struct(field, indent_lvl + 1)
            elif isinstance(field, Union):
                self.name_to_classname(field)
                self.generate_union(field, indent_lvl + 1)
            elif isinstance(field, Func):
                self.name_to_classname(field)
                self.generate_func_pointer_decorator(field, indent_lvl)

        self.output(f"""
{indent}{_INDENT_}pass
""")

        # We can override struct definitions (for tricky ones) in override.py
        if cls in self.overrides.codes:
            # Assume the overriding definition contains all code in .codes
            self.output(self.overrides.codes[cls])
        else:
            self.output(f"{indent}{cls}._fields_ = (")

            for field in struct.fields:
                field_type = self.class4(field.type)
                if (
                    isinstance(field, Struct)
                    or isinstance(field, Union)
                    or isinstance(field, Func)
                ):
                    field_type = f"{cls}.{self.class4(field.name)}"

                # Special case!
                #
                # For the struct 'Event', the field 'type' is given the
                # type 'int' in libvlc, but it should be an 'EventType'.
                #
                # It was handled in override.py before, also because the
                # field 'u' was a complicated nested union to parse for
                # the regex-based version of this generator (that union
                # was hardcoded in header.py, and called 'EventUnion').
                #
                # Now we can handle the complicated union but still
                # want to keep the little fix of 'type', which can't
                # be applied generally.
                if cls == "Event" and field.name == "type":
                    field_type = "EventType"

                # FIXME: For now, ignore field if it's type is one of the wrapper classes.
                if field_type in self.defined_classes:
                    continue

                # Strip the polish-notation prefixes from entries, to
                # preserve compatibility in 3.x series.
                # Preserve them in 4.x series, because it will be more consistent with the native libvlc API.
                # See https://github.com/oaubert/python-vlc/issues/174
                self.output(
                    "%s%s('%s', %s),"
                    % (
                        indent,
                        _INDENT_,
                        re.sub("^(i_|f_|p_|psz_)", "", field.name)
                        if self.parser.version < "4"
                        else field.name,
                        field_type,
                    )
                )
            self.output(f"{indent})")
            self.output("")

    def generate_union(self, union: Union, indent_lvl: int = 0):
        """Outputs a binding for `union`.

        @param union: The `Union` instance for which to output the binding.
        @param indent_lvl: A positive integer representing how many indentations
        should precede each line generated.
        """
        indent = _INDENT_ * indent_lvl
        cls = self.class4(union.name)

        # We use a forward declaration here to allow for self-referencing structures - cf
        # https://docs.python.org/3/library/ctypes.html#ctypes.Structure._fields_
        self.output(f"""{indent}class {cls}(ctypes.Union):
{indent}{_INDENT_}'''{union.epydocs() or _NA_}
{indent}{_INDENT_}'''""")

        for field in union.fields:
            if isinstance(field, Struct):
                self.name_to_classname(field)
                self.generate_struct(field, indent_lvl + 1)
            elif isinstance(field, Union):
                self.name_to_classname(field)
                self.generate_union(field, indent_lvl + 1)
            elif isinstance(field, Func):
                self.name_to_classname(field)
                self.generate_func_pointer_decorator(field, indent_lvl)

        self.output(f"""
{indent}{_INDENT_}pass
""")

        self.output(f"{indent}{cls}._fields_ = (")

        for field in union.fields:
            field_type = self.class4(field.type)
            if (
                isinstance(field, Struct)
                or isinstance(field, Union)
                or isinstance(field, Func)
            ):
                field_type = f"{cls}.{self.class4(field.name)}"

            # FIXME: For now, ignore field if it's type is one of the wrapper classes.
            if field_type in self.defined_classes:
                continue

            # Strip the polish-notation prefixes from entries, to
            # preserve compatibility in 3.x series.
            # Preserve them in 4.x series, because it will be more consistent with the native libvlc API.
            # See https://github.com/oaubert/python-vlc/issues/174
            self.output(
                "%s%s('%s', %s),"
                % (
                    indent,
                    _INDENT_,
                    re.sub("^(i_|f_|p_|psz_)", "", field.name)
                    if self.parser.version < "4"
                    else field.name,
                    field_type,
                )
            )
        self.output(f"{indent})")
        self.output("")

    def generate_structs(self):
        """Generate classes for all structs types."""
        for struct in self.parser.structs:
            self.generate_struct(struct)

    def generate_callbacks(self):
        """Generate decorators for callback functions.

        We generate both decorators (for defining functions) and
        associated classes, to help in defining function signatures.
        """
        if not self.parser.callbacks:
            return
        # Generate classes
        for f in self.parser.callbacks:
            if f.name in _blacklist:
                continue
            name = self.class4(f.name)  # PYCHOK flake
            docs = self.epylink(f.epydocs(0, 4))
            self.output(
                '''class %(name)s(ctypes.c_void_p):
    """%(docs)s
    """
    pass'''
                % locals()
            )

        self.output("class CallbackDecorators(object):")
        self.output(
            '    "Class holding various method decorators for callback functions."'
        )
        for f in self.parser.callbacks:
            name = self.class4(f.name)  # PYCHOK flake

            # return value and arg classes
            types = ", ".join(
                [self.class4(f.type)]  # PYCHOK flake
                + [self.class4(p.type, p.flags(f.out)[0]) for p in f.pars]
            )

            # xformed doc string with first @param
            docs = self.epylink(f.epydocs(0, 8))

            self.output(
                """    %(name)s = ctypes.CFUNCTYPE(%(types)s)
    %(name)s.__doc__ = '''%(docs)s
    '''"""
                % locals()
            )
        self.output("cb = CallbackDecorators")

    def generate_wrappers(self):
        """Generate class wrappers for all appropriate functions."""

        def striprefix(name):
            return name.replace(x, "").replace("libvlc_", "")

        # sort functions on the type/class
        # of their first parameter
        t = []
        for f in self.parser.funcs:
            if f.pars:
                p = f.pars[0]
                c = self.class4(p.type)
                if c in self.defined_classes:
                    t.append((c, f))
        cls = x = ""  # wrap functions in class methods
        for c, f in sorted(t, key=operator.itemgetter(0)):
            if cls != c:
                cls = c
                self.output(
                    """class %s(_Ctype):
    '''%s
    '''"""
                    % (cls, self.overrides.docstrs.get(cls, "") or _NA_)
                )  # """ emacs-mode is confused...

                c = self.overrides.codes.get(cls, "")
                if "def __new__" not in c:
                    self.output("""
    def __new__(cls, ptr=_internal_guard):
        '''(INTERNAL) ctypes wrapper constructor.
        '''
        return _Constructor(cls, ptr)""")

                if c:
                    self.output(c)
                x = self.prefixes.get(cls, "libvlc_")

            f.wrapped += 1
            name = f.name

            # method name is function name less prefix
            meth = striprefix(name)
            if meth in self.overrides.methods.get(cls, []):
                continue  # overridden

            # arg names, excluding output args
            # and rename first arg to 'self'
            args = ", ".join(["self"] + f.args(1))  # PYCHOK flake "
            wrapped_args = ", ".join(
                ["self"]
                + [
                    ("str_to_bytes(%s)" % pa.name if pa.type == "char*" else pa.name)
                    for pa in f.in_params(1)
                ]
            )  # PYCHOK flake

            # xformed doc string without first @param
            docs = self.epylink(f.epydocs(1, 8), striprefix)  # PYCHOK flake
            decorator = ""
            if meth.endswith("event_manager"):
                decorator = "    @memoize_parameterless"
            self.output(
                """%(decorator)s
    def %(meth)s(%(args)s):
        '''%(docs)s
        '''
        return %(name)s(%(wrapped_args)s)
"""
                % locals()
            )

            # check for some standard methods
            if meth == "count":
                # has a count method, generate __len__
                self.output(
                    """    def __len__(self):
        return %s(self)
"""
                    % (name,)
                )
            elif meth.endswith("item_at_index"):
                # indexable (and thus iterable)
                self.output(
                    """    def __getitem__(self, i):
        return %s(self, i)

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]
"""
                    % (name,)
                )

    def parse_override(self, override):
        """Parse the override definitions file.

        It is possible to override methods definitions in classes.

        @param override: the C{override.py} file name.

        @return: a tuple (codes, methods, docstrs) of 3 dicts
        containing the source code, the method names and the
        class-level doc strings for each of the classes defined
        in the B{override} file.
        """
        codes = {}
        k, v = None, []
        f = opener(override)
        for t in f:
            m = class_re.match(t)
            if m:  # new class
                if k is not None:
                    codes[k] = "".join(v)
                k, v = m.group(1), []
            else:
                v.append(t)
        if k is not None:
            codes[k] = "".join(v)
        f.close()

        docstrs, methods = {}, {}
        for k, v in codes.items():
            q = v.lstrip()[:3]
            if q in ('"""', "'''"):
                # use class comment as doc string
                _, docstrs[k], v = v.split(q, 2)
                codes[k] = v
            # FIXME: not robust wrt. internal methods
            methods[k] = def_re.findall(v)

        return Overrides(codes=codes, methods=methods, docstrs=docstrs)

    def save(self, path=None, format=True):
        """Write Python bindings to a file or C{stdout}."""
        if format:
            # Write to temporary file
            tmp_path = os.path.join(BASEDIR, ".tmp")
            self.outopen(tmp_path)
            self.insert_code(os.path.join(TEMPLATEDIR, "header.py"), genums=True)
            self.generate_ctypes()
            self.unwrapped()
            self.insert_code(os.path.join(TEMPLATEDIR, "footer.py"))
            self.outclose()

            # Format the temporary file using ruff
            completed_process = subprocess.run(
                [
                    "ruff",
                    "format",
                    "--config",
                    RUFF_CFG_FILE,
                    tmp_path,
                ],
                stdout=subprocess.DEVNULL,
            )
            completed_process.check_returncode()
            completed_process = subprocess.run(
                [
                    "ruff",
                    "check",
                    "--fix",
                    "--exit-zero",
                    "--config",
                    RUFF_CFG_FILE,
                    tmp_path,
                ],
                stdout=subprocess.DEVNULL,
            )
            completed_process.check_returncode()

            # Write to the actual `path`
            self.outopen(path or "-")
            self.insert_code(tmp_path)
            self.outclose()

            # Delete temporary file
            os.remove(tmp_path)
        else:
            self.outopen(path or "-")
            self.insert_code(os.path.join(TEMPLATEDIR, "header.py"), genums=True)
            self.generate_ctypes()
            self.unwrapped()
            self.insert_code(os.path.join(TEMPLATEDIR, "footer.py"))
            self.outclose()


class JavaGenerator(_Generator):
    """Generate Java/JNA bindings."""

    comment_line = "//"
    type_re = re.compile(r"libvlc_(.+?)(_[te])?$")

    # C-type to Java/JNA type conversion.
    type2class = {
        "libvlc_audio_output_t*": "LibVlcAudioOutput",
        "libvlc_callback_t": "LibVlcCallback",
        "libvlc_event_type_t": "LibvlcEventType",
        "libvlc_event_manager_t*": "LibVlcEventManager",
        "libvlc_instance_t*": "LibVlcInstance",
        "libvlc_log_t*": "LibVlcLog",
        "libvlc_log_iterator_t*": "LibVlcLogIterator",
        "libvlc_log_message_t*": "LibvlcLogMessage",
        "libvlc_media_t*": "LibVlcMedia",
        "libvlc_media_discoverer_t*": "LibVlcMediaDiscoverer",
        "libvlc_media_library_t*": "LibVlcMediaLibrary",
        "libvlc_media_list_t*": "LibVlcMediaList",
        "libvlc_media_list_player_t*": "LibVlcMediaListPlayer",
        "libvlc_media_list_view_t*": "LibVlcMediaListView",
        "libvlc_media_player_t*": "LibVlcMediaPlayer",
        "libvlc_media_stats_t*": "LibVlcMediaStats",
        "libvlc_media_track_info_t**": "LibVlcMediaTrackInfo",
        "libvlc_time_t": "long",
        "libvlc_track_description_t*": "LibVlcTrackDescription",
        "...": "FIXME_va_list",
        "char*": "String",
        "char**": "String[]",
        "float": "float",
        "int": "int",
        "int*": "Pointer",
        "int64_t": "long",
        "short": "short",
        "uint32_t": "uint32",
        "unsigned": "int",
        "unsigned*": "Pointer",
        "void": "void",
        "void*": "Pointer",
    }

    def __init__(self, parser: Parser):
        """New instance.

        @param parser: a L{Parser} instance.
        """
        _Generator.__init__(self, parser)
        self.check_types()

    def generate_enums(self):
        """Generate Java/JNA glue code for enums."""
        for e in self.parser.enums:
            j = self.class4(e.name)
            self.outopen(j + ".java")

            self.insert_code(os.path.join(TEMPLATEDIR, "boilerplate.java"))
            self.output(
                """package org.videolan.jvlc.internal;

public enum %s
{"""
                % (j,)
            )
            # FIXME: write comment
            for v in e.vals:
                self.output("        %s (%s)," % (v.name, v.value))
            self.output(
                """
        private final int _value;
        %s(int value) { this._value = value; }
        public int value() { return this._value; }
}"""
                % (j,)
            )
            self.outclose()

    def generate_header(self):
        """Generate LibVlc header."""
        for c, j in sorted(self.type2class.items()):
            if c.endswith("*") and j.startswith("LibVlc"):
                self.output(
                    """
    public class %s extends PointerType
    {
    }"""
                    % (j,)
                )

    def generate_libvlc(self):
        """Generate LibVlc.java Java/JNA glue code."""
        self.outopen("LibVlc.java")

        self.insert_code(os.path.join(TEMPLATEDIR, "boilerplate.java"))
        self.insert_code(os.path.join(TEMPLATEDIR, "LibVlc-header.java"))

        self.generate_header()
        for f in self.parser.funcs:
            f.wrapped = 1  # for now
            p = ", ".join("%s %s" % (self.class4(p.type), p.name) for p in f.pars)
            self.output("%s %s(%s);" % (self.class4(f.type), f.name, p), nt=2)

        self.insert_code(os.path.join(TEMPLATEDIR, "LibVlc-footer.java"))

        self.unwrapped()
        self.outclose()

    def save(self, dir=None, format=True):
        """Write Java bindings into the given directory."""
        if dir in (None, "-"):
            d = "internal"
            if not os.path.isdir(d):
                os.makedirs(d)  # os.mkdir(d)
        else:
            d = dir or os.curdir
        self.outdir = d

        sys.stderr.write("Generating Java code in %s...\n" % os.path.join(d, ""))

        self.generate_enums()
        self.generate_libvlc()


def preprocess(vlc_h: Path) -> Path:
    if vlc_h.name != "vlc.h":
        raise Exception(
            f"Except input file to be (and end with) vlc.h, but got {vlc_h.absolute()}."
        )

    preprocessed_dir = Path(PREPROCESSEDDIR)
    if not (preprocessed_dir.exists() and preprocessed_dir.is_dir()):
        preprocessed_dir.mkdir(parents=True)

    preprocessed_file = Path(f"{PREPROCESSEDDIR}/vlc.preprocessed")
    # call C preprocessor on vlc.h
    completed_process = subprocess.run(
        [
            "gcc",
            "-E",
            "-P",
            "-C",
            "-I",
            vlc_h.parent.parent.absolute(),
            vlc_h,
            "-o",
            preprocessed_file.absolute(),
        ]
    )
    completed_process.check_returncode()

    return preprocessed_file


def prepare_package(output):
    """Prepare a python-vlc package for the designated module.

    output is the location of the generated vlc.py file.
    """
    # Parse the module for VLC version number
    bindings_version = None
    libvlc_version = None
    with open(output, "r") as f:
        for l in f:
            m = re.search(r'__version__\s*=\s*"(.+)"', l)
            if m:
                bindings_version = m.group(1)
            m = re.search(r'__libvlc_version__\s*=\s*"(.+)"', l)
            if m:
                libvlc_version = m.group(1)
            if bindings_version and libvlc_version:
                break

    if bindings_version is None:
        sys.stderr.write("Unable to determine bindings version.")
        sys.exit(1)

    # Write the versioned setup.py file
    outdir = os.path.dirname(output)
    with open(os.path.join(TEMPLATEDIR, "setup.py")) as f:
        setup = f.read()
    # Fill in the template fields
    setup = setup.format(
        libvlc_version=libvlc_version,
        generator_version=__version__,
        bindings_version=bindings_version,
    )
    with open(os.path.join(outdir, "setup.py"), "w") as f:
        f.write(setup)

    # Copy other files for distribution
    shutil.copyfile(
        os.path.join(TEMPLATEDIR, "MANIFEST.in"), os.path.join(outdir, "MANIFEST.in")
    )
    examples = os.path.join(outdir, "examples")
    if os.path.isdir(examples):
        shutil.rmtree(examples)
    shutil.copytree(os.path.join(BASEDIR, "..", "examples"), examples)
    for fname in ("COPYING", "README.module", "distribute_setup.py"):
        shutil.copyfile(os.path.join(BASEDIR, "..", fname), os.path.join(outdir, fname))


if __name__ == "__main__":
    from optparse import OptionParser

    opt = OptionParser(
        usage="""%prog  [options]  <include_vlc_directory> | <include_file.h> [...]

Parse VLC include files and generate bindings code for Python or Java."""
    )

    opt.add_option(
        "-c",
        "--check",
        dest="check",
        action="store_true",
        default=False,
        help="Check mode, generates no bindings",
    )

    opt.add_option(
        "-d",
        "--debug",
        dest="debug",
        action="store_true",
        default=False,
        help="Debug mode, generate no bindings",
    )

    opt.add_option(
        "-j",
        "--java",
        dest="java",
        action="store_true",
        default=False,
        help="Generate Java bindings (default is Python)",
    )

    opt.add_option(
        "-o",
        "--output",
        dest="output",
        action="store",
        type="str",
        default="-",
        help="Output filename (for Python) or directory (for Java)",
    )

    opt.add_option(
        "-v",
        "--version",
        dest="version",
        action="store",
        type="str",
        default="",
        help="Version string for __version__ global",
    )

    opt.add_option(
        "-p",
        "--package",
        dest="package",
        action="store",
        type="str",
        default="",
        help="Prepare a package for the given python module.",
    )

    opts, args = opt.parse_args()

    if "--debug" in sys.argv:
        _debug = True  # show source

    if opts.package:
        prepare_package(opts.package)
        sys.exit(0)

    if not args:
        opt.print_help()
        sys.exit(1)
    elif len(args) == 1:  # get .h files
        # get .h files from .../include/vlc dir
        # or .../include/vlc/*.h (especially
        # useful on Windows, where cmd does
        # not provide wildcard expansion)
        p = args[0]
        if os.path.isdir(p):
            p = os.path.join(p, "*.h")
        import glob

        args = glob.glob(p)

    vlc_h = ""
    libvlc_version_h = ""
    for h_file in args:
        p = Path(h_file)
        if p.name == "vlc.h":
            vlc_h = h_file
        if p.name == "libvlc_version.h":
            libvlc_version_h = h_file
    if vlc_h == "":
        raise Exception(
            "Didn't found vlc.h amongst header files, but need it for preprocessing."
        )
    if libvlc_version_h == "":
        raise Exception(
            "Didn't found libvlc_version.h amongst header files, but need it for finding libvlc version."
        )
    vlc_h = Path(vlc_h)
    libvlc_version_h = Path(libvlc_version_h)
    vlc_preprocessed = preprocess(vlc_h)
    p = Parser(vlc_preprocessed, libvlc_version_h, opts.version, False)
    if opts.debug:
        for t in ("structs", "enums", "funcs", "callbacks"):
            p.dump(t)
    if opts.java:
        g = JavaGenerator(p)
    else:
        g = PythonGenerator(p)

    if opts.check:
        p.check()
    elif opts.debug:
        g.dump_dicts()
    elif not _nerrors:
        g.save(opts.output)

    errors("%s error(s) reported")
