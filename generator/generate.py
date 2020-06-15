#! /usr/bin/env python3

# Code generator for python ctypes bindings for VLC
#
# Copyright (C) 2009-2017 the VideoLAN team
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
__all__     = ('Parser',
               'PythonGenerator', 'JavaGenerator',
               'process')

# Version number MUST have a major < 10 and a minor < 99 so that the
# generated dist version can be correctly generated.
__version__ =  '1.14'

_debug = False

import operator
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

BASEDIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATEDIR = os.path.join(BASEDIR, 'templates')

str = str

try:
    basestring = basestring    # Python 2
except NameError:
    basestring = (str, bytes)  # Python 3

try:
    unicode = unicode          # Python 2
except NameError:
    unicode = str              # Python 3

if sys.version_info[0] < 3:
    PYTHON3 = False
    bytes = str
    def opener(name, mode='r'):
        return open(name, mode)
else:  # Python 3+
    PYTHON3 = True
    bytes = bytes
    def opener(name, mode='r'):  #PYCHOK expected
        return open(name, mode, encoding='utf8')

# Functions not wrapped/not referenced
_blacklist = {
    # Deprecated functions
    'libvlc_audio_output_set_device_type': '',
    'libvlc_audio_output_get_device_type': '',
    'libvlc_set_exit_handler':    '',
    'libvlc_printerr': '',
    # Waiting for some structure wrapping
    'libvlc_dialog_set_callbacks': '',
    # Its signature is a mess
    'libvlc_video_direct3d_set_resize_cb': '',
    'libvlc_video_output_set_resize_cb' : '' ,
    # It depends on the previous one
    'libvlc_video_direct3d_set_callbacks': '',
    'libvlc_video_set_output_callbacks': '',
}

# Set of functions that return a string that the caller is
# expected to free.
free_string_funcs = set((
        'libvlc_media_discoverer_localized_name',
        'libvlc_media_get_mrl',
        'libvlc_media_get_meta',
        'libvlc_video_get_aspect_ratio',
        'libvlc_video_get_crop_geometry',
        'libvlc_video_get_marquee_string',
        'libvlc_audio_output_device_longname',
        'libvlc_audio_output_device_id',
        'libvlc_audio_output_device_get',
        'libvlc_vlm_show_media',
    ))

# some constants
_NA_     = 'N/A'
_NL_     = '\n'  # os.linesep
_OUT_    = '[OUT]'
_PNTR_   = 'pointer to get the '  # KLUDGE: see @param ... [OUT]
_INDENT_ = '    '

# special keywords in header.py
_BUILD_DATE_      = 'build_date  = '
_GENERATED_ENUMS_ = '# GENERATED_ENUMS'
_GENERATED_CALLBACKS_ = '# GENERATED_CALLBACKS'

# keywords in header files
_VLC_FORWARD_     = 'VLC_FORWARD'
_VLC_PUBLIC_API_  = 'LIBVLC_API'

# Precompiled regexps
api_re       = re.compile(r'(?:LIBVLC_DEPRECATED\s+)?' + _VLC_PUBLIC_API_ + r'\s+(\S+\s+.+?)\s*\(\s*(.+?)\s*\)')
at_param_re  = re.compile(r'(@param\s+\S+)(.+)')
bs_param_re  = re.compile(r'\\param\s+(\S+)')
class_re     = re.compile(r'class\s+(\S+):')
def_re       = re.compile(r'^\s+def\s+(\w+)', re.MULTILINE)
enum_type_re = re.compile(r'^(?:typedef\s+)?enum')
enum_re      = re.compile(r'(?:typedef\s+)?(enum)\s*(\S+)\s*\{\s*(.+)\s*\}\s*(?:\S+)?;')
enum_pair_re = re.compile(r'\s*=\s*')
callback_type_re = re.compile(r'^typedef\s+\w+(\s*\*)?\s*\(\s*\*')
callback_re  = re.compile(r'typedef\s+\*?(\w+\s*\*?)\s*\(\s*\*\s*(\w+)\s*\)\s*\((.+)\);')
struct_type_re = re.compile(r'^typedef\s+struct\s*(\S+)\s*$')
struct_re    = re.compile(r'typedef\s+(struct)\s*(\S+)?\s*\{\s*(.+)\s*\}\s*(?:\S+)?\s*;')
func_pointer_re = re.compile(r'(\(?[^\(]+)\s*\((\*\s*\S*)\)(\(.*\))') # (ret_type, *pointer_name, ([params]))
typedef_re   = re.compile(r'^typedef\s+(?:struct\s+)?(\S+)\s+(\S+);')
forward_re   = re.compile(r'.+\(\s*(.+?)\s*\)(\s*\S+)')
libvlc_re    = re.compile(r'libvlc_[a-z_]+')
decllist_re  = re.compile(r'\s*;\s*')
paramlist_re = re.compile(r'\s*,\s*')
version_re   = re.compile(r'vlc[\-]\d+[.]\d+[.]\d+.*')
LIBVLC_V_re  = re.compile(r'\s*#\s*define\s+LIBVLC_VERSION_([A-Z]+)\s+\(*(\d+)\)*')
define_re    = re.compile(r'^\s*#\s*define\s+\w+\s+.+?$')

def endot(text):
    """Terminate string with a period.
    """
    if text and text[-1] not in '.,:;?!':
        text += '.'
    return text

def errorf(fmt, *args):
    """Print error.
    """
    global _nerrors
    _nerrors += 1
    sys.stderr.write('Error: ' + (fmt % args) + "\n")

_nerrors = 0

def errors(fmt, e=0):
    """Report total number of errors.
    """
    if _nerrors > e:
        n = _nerrors - e
        x =  min(n, 9)
        errorf(fmt + '... exit(%s)', n, x)
        sys.exit(x)
    elif _debug:
        sys.stderr.write(fmt % (_NL_ + 'No') + "\n")

class _Source(object):
    """Base class for elements parsed from source.
    """
    source = ''

    def __init__(self, file_='', line=0):
        self.source = '%s:%s' % (file_, line)
        self.dump()  #PYCHOK expected

class Enum(_Source):
    """Enum type.
    """
    type = 'enum'

    def __init__(self, name, type='enum', vals=(), docs='', **kwds):
        if type != self.type:
            raise TypeError('expected enum type: %s %s' % (type, name))
        self.docs = docs
        self.name = name
        self.vals = vals  # list/tuple of Val instances
        if _debug:
           _Source.__init__(self, **kwds)

    def check(self):
        """Perform some consistency checks.
        """
        if not self.docs:
            errorf('no comment for typedef %s %s', self.type, self.name)
        if self.type != 'enum':
            errorf('expected enum type: %s %s', self.type, self.name)

    def dump(self):  # for debug
        sys.stderr.write('%s (%s): %s\n' % (self.name, self.type, self.source))
        for v in self.vals:
            v.dump()

    def epydocs(self):
        """Return epydoc string.
        """
        return self.docs.replace('@see', 'See').replace('\\see', 'See')

class Struct(_Source):
    """Struct type.
    """
    type = 'struct'

    def __init__(self, name, type='struct', fields=(), docs='', **kwds):
        if type != self.type:
            raise TypeError('expected struct type: %s %s' % (type, name))
        self.docs = docs
        self.name = name
        self.fields = fields  # list/tuple of Par instances
        if _debug:
           _Source.__init__(self, **kwds)

    def check(self):
        """Perform some consistency checks.
        """
        if not self.docs:
            errorf('no comment for typedef %s %s', self.type, self.name)
        if self.type != 'struct':
            errorf('expected struct type: %s %s', self.type, self.name)

    def dump(self):  # for debug
        sys.stderr.write('STRUCT %s (%s): %s\n' % (self.name, self.type, self.source))
        for v in self.fields:
            v.dump()

    def epydocs(self):
        """Return epydoc string.
        """
        return self.docs.replace('@see', 'See').replace('\\see', 'See')

class Flag(object):
    """Enum-like, ctypes parameter direction flag constants.
    """
    In     = 1  # input only
    Out    = 2  # output only
    InOut  = 3  # in- and output
    InZero = 4  # input, default int 0
    def __init__(self):
        raise TypeError('constants only')

class Func(_Source):
    """C function.
    """
    heads   = ()  # docs lines without most @tags
    out     = ()  # [OUT] parameter names
    params  = ()  # @param lines, except [OUT]
    tails   = ()  # @return, @version, @bug lines
    wrapped =  0  # number of times wrapped

    def __init__(self, name, type, pars=(), docs='', **kwds):
        self.docs = docs
        self.name = name
        self.pars = pars  # list/tuple of Par instances
        self.type = type
        if _debug:
           _Source.__init__(self, **kwds)

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
        return [p for p in self.pars[first:] if
                p.flags(self.out)[0] != Flag.Out]

    def check(self):
        """Perform some consistency checks.
        """
        if not self.docs:
            errorf('no comment for function %s', self.name)
        elif len(self.pars) != self.nparams:
            errorf('doc parameters (%d) mismatch for function %s (%d)',
                    self.nparams, self.name, len(self.pars))
            if _debug:
                self.dump()
                sys.stderr.write(self.docs + "\n")

    def dump(self):  # for debug
        sys.stderr.write('%s (%s): %s\n' %  (self.name, self.type, self.source))
        for p in self.pars:
            p.dump(self.out)

    def epydocs(self, first=0, indent=0):
        """Return epydoc doc string with/out first parameter.
        """
        # "out-of-bounds" slices are OK, e.g. ()[1:] == ()
        t = _NL_ + (' ' * indent)
        return t.join(self.heads + self.params[first:] + self.tails)

    def __nparams_(self):
        return (len(self.params) + len(self.out)) or len(bs_param_re.findall(self.docs))
    nparams = property(__nparams_, doc='number of \\param lines in doc string')

    def xform(self):
        """Transform Doxygen to epydoc syntax.
        """
        b, c, h, o, p, r, v = [], None, [], [], [], [], []
        # see <http://epydoc.sourceforge.net/manual-fields.html>
        # (or ...replace('{', 'E{lb}').replace('}', 'E{rb}') ?)
        for t in self.docs.replace('@{', '').replace('@}', '').replace('\\ingroup', '') \
                          .replace('{', '').replace('}', '') \
                          .replace('<b>', 'B{').replace('</b>', '}') \
                          .replace('@see', 'See').replace('\\see', 'See') \
                          .replace('\\bug', '@bug').replace('\\version', '@version') \
                          .replace('\\note', '@note').replace('\\warning', '@warning') \
                          .replace('\\param', '@param').replace('\\return', '@return') \
                          .replace('NULL', 'None') \
                          .splitlines():
            if '@param' in t:
                if _OUT_ in t:
                    # KLUDGE: remove @param, some comment and [OUT]
                    t = t.replace('@param', '').replace(_PNTR_, '').replace(_OUT_, '')
                    # keep parameter name and doc string
                    o.append(' '.join(t.split()))
                    c = ['']  # drop continuation line(s)
                else:
                    p.append(at_param_re.sub(r'\1:\2', t))
                    c = p
            elif '@return' in t:
                r.append(t.replace('@return ', '@return: '))
                c = r
            elif '@bug' in t:
                b.append(t.replace('@bug ', '@bug: '))
                c = b
            elif '@version' in t:
                v.append(t.replace('@version ', '@version: '))
                c = v
            elif c is None:
                h.append(t.replace('@note ', '@note: ').replace('@warning ', '@warning: '))
            else:  # continuation, concatenate to previous @tag line
                c[-1] = '%s %s' % (c[-1], t.strip())
        if h:
            h[-1] = endot(h[-1])
            self.heads = tuple(h)
        if o:  # just the [OUT] parameter names
            self.out = tuple(t.split()[0] for t in o)
            # ctypes returns [OUT] parameters as tuple
            r = ['@return: %s' % ', '.join(o)]
        if p:
            self.params = tuple(map(endot, p))
        t = r + v + b
        if t:
            self.tails = tuple(map(endot, t))

class Par(object):
    """C function parameter.
    """
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

    def __repr__(self):
        return "%s (%s) %s" % (self.name, self.type, self.constness)

    def dump(self, out=()):  # for debug
        if self.name in out:
            t = _OUT_  # @param [OUT]
        else:
            t = {Flag.In:     '',  # default
                 Flag.Out:    'Out',
                 Flag.InOut:  'InOut',
                 Flag.InZero: 'InZero',
                }.get(self.flags()[0], 'FIXME_Flag')
        sys.stderr.write('%s%s %s\n' % (_INDENT_, str(self), t))

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
            f = {'int*':      Flag.Out,
                 'unsigned*': Flag.Out,
                 'unsigned char*': Flag.Out,
                 'libvlc_media_track_info_t**': Flag.Out,
                }.get(self.type, Flag.In)  # default
        else:
            f = Flag.In

        if default is None:
            return f,  # 1-tuple
        else:  # see ctypes 15.16.2.4 Function prototypes
            return f, self.name, default  #PYCHOK expected

    @classmethod
    def parse_param(cls, param_raw):
        """Parse a C parameter expression.

        It is used to parse the type/name of functions
        and type/name of the function parameters.

        @return: a Par instance.
        """
        param_raw = param_raw.strip()
        if _VLC_FORWARD_ in param_raw:
            m = forward_re.match(param_raw)
            param_raw = m.group(1) + m.group(2)

        # is this a function pointer?
        if func_pointer_re.search(param_raw):
            return None

        # is this parameter a pointer?
        split_pointer = param_raw.split('*')
        if len(split_pointer) > 1:
            param_type = split_pointer[0]
            param_name = split_pointer[-1].split(' ')[-1]
            param_deref_levels = len(split_pointer) - 1

            # it is a pointer, so it should have at least 1 level of indirection
            assert(param_deref_levels > 0)

            # POINTER SEMANTIC
            constness =     split_pointer[:-1]
            constness +=    ['const' if len(split_pointer[-1].strip().split(' ')) > 1 else '']
            param_constness = ['const' in deref_level for deref_level in constness]

            # PARAM TYPE
            param_type = split_pointer[0].replace('const ', '').strip()
            # remove the struct keyword, this information is currently not used
            param_type = param_type.replace('struct ', '').strip()

            # add back the information of how many dereference levels there are
            param_type += '*' * param_deref_levels

            # ASSUMPTION
            # just indirection level 0 and 1 can be const
            for deref_level_constness in param_constness[2:]: assert(not deref_level_constness)
        # ... or is it a simple variable?
        else:
            # WARNING: workaround for "union { struct {"
            param_raw = param_raw.split('{')[-1]

            # ASSUMPTIONs
            # these allows to constrain param_raw to these options:
            #  - named:     "type name" (e.g. "int param")
            #  - anonymous: "type"      (e.g. "int")
            assert('struct' not in param_raw)
            assert('const' not in param_raw)

            # normalize spaces
            param_raw = re.sub('\s+', ' ', param_raw)

            split_value = param_raw.split(' ')
            if len(split_value) > 1:
                param_name = split_value[-1]
                param_type = ' '.join(split_value[:-1])
            else:
                param_type = split_value[0]
                param_name = ''

            param_constness = [False]

        return Par(param_name.strip(), param_type.strip(), param_constness)

class Val(object):
    """Enum name and value.
    """
    def __init__(self, enum, value, context=None):
        self.enum = enum  # C name
        # convert name
        t = enum.split('_')
        if context is not None:
            # A context (enum type name) is provided. Strip out the
            # common prefix.
            prefix = os.path.commonprefix( (enum, re.sub(r'_t$', r'_', context)) )
            n = enum.replace(prefix, '', 1)
        else:
            # No prefix. Fallback on the previous version (which
            # considers only the last _* portion of the name)
            n = t[-1]
        # Special case for debug levels and roles (with non regular name)
        n = re.sub(r'^(LIBVLC_|role_|marquee_|adjust_|AudioChannel_|AudioOutputDevice_)', '', n)
        if n[0].isdigit():  # can't start with a number
            n = '_' + n
        if n == 'None': # can't use a reserved python keyword
            n = '_' + n
        self.name = n
        self.value = value

    def dump(self):  # for debug
        sys.stderr.write('%s%s = %s\n' % (_INDENT_, self.name, self.value))

class Parser(object):
    """Parser of C header files.
    """
    h_file = ''

    def __init__(self, h_files, version=''):
        self.enums = []
        self.callbacks = []
        self.structs = []
        self.funcs = []
        self.typedefs = {}
        self.version = version

        if not self.version:
            self.version = self.parse_version(h_files)
        for h in h_files:
            self.h_file = h
            self.typedefs.update(self.parse_typedefs())
            self.structs.extend(self.parse_structs())
            self.enums.extend(self.parse_enums())
            self.callbacks.extend(self.parse_callbacks())
            self.funcs.extend(self.parse_funcs())

    def bindings_version(self):
        """Return the bindings version number.

        It is built from the VLC version number and the generator
        version number as:
        vlc_major.vlc_minor.(1000 * vlc_micro + 100 * generator_major + generator_minor)
        """
        major, minor = [ int(i) for i in __version__.split(".") ]
        bindings_version = "%s%d%02d" % (self.version, major, minor)
        return bindings_version

    def check(self):
        """Perform some consistency checks.
        """
        for e in self.enums:
            e.check()
        for f in self.funcs:
            f.check()
        for f in self.callbacks:
            f.check()
        for s in self.structs:
            s.check()

    def dump(self, attr):
        sys.stderr.write('%s==== %s ==== %s\n' % (_NL_, attr, self.version))
        for a in getattr(self, attr, ()):
            a.dump()

    def parse_callbacks(self):
        """Parse header file for callback signature definitions.

        @return: yield a Func instance for each callback signature, unless blacklisted.
        """
        for type_, name, pars, docs, line in self.parse_groups(callback_type_re.match, callback_re.match, ');'):
            if name in _blacklist:
                _blacklist[name] = type_
                continue

            pars = [Par.parse_param(p) for p in paramlist_re.split(pars)]

            yield Func(name, type_.replace(' ', ''), pars, docs,
                       file_=self.h_file, line=line)

    def parse_enums(self):
        """Parse header file for enum type definitions.

        @return: yield an Enum instance for each enum.
        """
        for typ, name, enum, docs, line in self.parse_groups(enum_type_re.match, enum_re.match):
            vals, locs, e = [], {}, -1  # enum value(s)
            for t in paramlist_re.split(enum):
                n = t.split('/*')[0].strip()
                if '=' in n:  # has value
                    n, v = enum_pair_re.split(n)
                    # Bit-shifted characters cannot be directly evaluated in python
                    m = re.search(r"'(.)'\s*(<<|>>)\s*(.+)", v.strip())
                    if m:
                        v = "%s %s %s" % (ord(m.group(1)), m.group(2), m.group(3))
                    try:  # handle expressions
                        e = eval(v, locs)
                    except (SyntaxError, TypeError, ValueError):
                        errorf('%s %s: %s', typ, name, t)
                        raise
                    locs[n] = e
                    # preserve hex values
                    if v[:2] in ('0x', '0X'):
                        v = hex(e)
                    else:
                        v = str(e)
                    vals.append(Val(n, v, context=name))
                elif n:  # only name
                    e += 1
                    locs[n] = e
                    vals.append(Val(n, str(e), context=name))

            name = name.strip()
            if not name:  # anonymous
                name = 'libvlc_enum_t'

            # more doc string cleanup
            docs = endot(docs).capitalize()

            yield Enum(name, typ, vals, docs,
                       file_=self.h_file, line=line)

    def parse_structs(self):
        """Parse header file for struct definitions.

        @return: yield a Struct instance for each struct.
        """
        for typ, name, body, docs, line in self.parse_groups(struct_type_re.match, struct_re.match, re.compile(r'^\}(\s*\S+)?\s*;$')):
            fields = [ Par.parse_param(t.strip()) for t in decllist_re.split(body) if t.strip() and not '%s()' % name in t ]
            fields = [ f for f in fields if f is not None ]

            name = name.strip()
            if not name:  # anonymous?
                name = 'FIXME_undefined_name'

            # more doc string cleanup
            docs = endot(docs).capitalize()
            yield Struct(name, typ, fields, docs,
                         file_=self.h_file, line=line)

    def parse_funcs(self):
        """Parse header file for public function definitions.

        @return: yield a Func instance for each function, unless blacklisted.
        """
        def match_t(t):
            return _VLC_PUBLIC_API_ in t

        for name, pars, docs, line in self.parse_groups(match_t, api_re.match, ');'):

            f = Par.parse_param(name)
            if f.name in _blacklist:
                _blacklist[f.name] = f.type
                continue

            pars = [Par.parse_param(p) for p in paramlist_re.split(pars)]

            if len(pars) == 1 and pars[0].type == 'void':
                pars = []  # no parameters

            elif any(p for p in pars if not p.name):  # list(...)
                # no or missing parameter names, peek in doc string
                n = bs_param_re.findall(docs)
                if len(n) < len(pars):
                    errorf('%d parameter(s) missing in function %s comment: %s',
                            (len(pars) - len(n)), f.name, docs.replace(_NL_, ' ') or _NA_)
                    n.extend('param%d' % i for i in range(len(n), len(pars)))  #PYCHOK false?
                # FIXME: this assumes that the order of the parameters is
                # the same in the parameter list and in the doc string
                for i, p in enumerate(pars):
                    p.name = n[i]

            yield Func(f.name, f.type, pars, docs,
                       file_=self.h_file, line=line)

    def parse_typedefs(self):
        """Parse header file for typedef definitions.

        @return: a dict instance with typedef matches
        """
        return dict( (new, original)
            for original, new, docs, line in self.parse_groups(typedef_re.match, typedef_re.match) )

    def parse_groups(self, match_t, match_re, ends=';'):
        """Parse header file for matching lines, re and ends.

        @return: yield a tuple of re groups extended with the
        doc string and the line number in the header file.
        """
        a = []  # multi-lines
        d = []  # doc lines
        n = 0   # line number
        s = False  # skip comments except doc

        f = opener(self.h_file)
        for t in f:
            n += 1
            if define_re.match(t):
                continue
            # collect doc lines
            if t.startswith('/**'):
                d =     [t[3:].rstrip()]
            elif t.startswith(' * '):  # FIXME: keep empty lines
                d.append(t[3:].rstrip())

            else:  # parse line
                t, m = t.strip(), None

                if s or t.startswith('/*'):  # in comment
                    s = not t.endswith('*/')
                    m = match_re(t.split('/*', 1)[0])
                elif a:  # accumulate multi-line
                    if '/*' in t:
                        s = not t.endswith('*/')
                    t = t.split('/*', 1)[0].rstrip()  # //?
                    a.append(t)
                    if (t.endswith(ends) if isinstance(ends, basestring) else ends.match(t)):  # end
                        t = ' '.join(a)
                        m = match_re(t)
                        a = []
                elif match_t(t):
                    if (t.endswith(ends) if isinstance(ends, basestring) else ends.match(t)):
                        m = match_re(t)  # single line
                    else:  # new multi-line
                        a = [t]

                if m:
                    # clean up doc string
                    d = _NL_.join(d).strip()
                    if d.endswith('*/'):
                        d = d[:-2].rstrip()

                    if _debug:
                        sys.stderr.write('%s==== source ==== %s:%d\n' % (_NL_, self.h_file, n))
                        sys.stderr.write(t + "\n")
                        sys.stderr.write('"""%s%s"""\n' % (d, _NL_))

                    yield m.groups() + (d, n)
                    d = []
                elif typedef_re.match(t):
                    # We have another typedef. Reset docstring.
                    d = []
        f.close()

    def parse_version(self, h_files):
        """Get the libvlc version from the C header files:
           LIBVLC_VERSION_MAJOR, _MINOR, _REVISION, _EXTRA
        """
        version = None
        version_file = [ h for h in h_files if
                         h.lower().endswith('libvlc_version.h') ]
        if version_file:
            # Version file exists. Parse the version number.
            f, v = opener(version_file[0]), []
            for t in f:
                m = LIBVLC_V_re.match(t)
                if m:
                    t, m = m.groups()
                    if t in ('MAJOR', 'MINOR', 'REVISION'):
                        v.append((t, m))
                    elif t == 'EXTRA' and m not in ('0', ''):
                        v.append((t[1:], m))
            f.close()
            if v:
                version = '.'.join(m for _, m in sorted(v))
        # Version was not found in include files themselves. Try other
        # approaches.
        if version is None:
            # Try to get version information from git describe
            git_dir = Path(h_files[0]).absolute().parents[2].joinpath('.git')
            if git_dir.is_dir():
                # We are in a git tree. Let's get the version information
                # from there if we can call git
                try:
                    version = subprocess.check_output(["git", "--git-dir=%s" % git_dir.as_posix(), "describe"]).strip().decode('utf-8')
                except:
                    pass
        return version

class _Generator(object):
    """Base class.
    """
    comment_line = '#'   # Python
    file         = None
    links        = {}    # must be overloaded
    outdir       = ''
    outpath      = ''
    type_re      = None  # must be overloaded
    type2class   = {}    # must be overloaded
    type2class_out = {}  # Specific values for OUT parameters

    def __init__(self, parser=None):
        self.parser = parser
        self.convert_classnames(parser.structs)
        self.convert_classnames(parser.enums)
        self.convert_classnames(parser.callbacks)

    def check_types(self):
        """Make sure that all types are properly translated.

        @note: This method must be called B{after} C{convert_enums},
        since the latter populates C{type2class} with enum class names.
        """
        e = _nerrors
        for f in self.parser.funcs:
            if f.type not in self.type2class:
                errorf('no type conversion for %s %s', f.type, f.name)
            for p in f.pars:
                if p.type not in self.type2class:
                    errorf('no type conversion for %s %s in %s', p.type, p.name, f.name)
        errors('%s type conversion(s) missing', e)

    def class4(self, type, flag=None):
        """Return the class name for a type or enum.
        """
        cl = None
        if flag == Flag.Out:
            cl = self.type2class_out.get(type)
        if cl is None:
            cl = self.type2class.get(type, 'FIXME_%s%s' % ('OUT_' if flag == Flag.Out else '',
                                                           type))
        return cl

    def convert_classnames(self, element_list):
        """Convert enum names to class names.

        source is either 'enum' or 'struct'.

        """
        for e in element_list:
            if e.name in self.type2class:
                # Do not override predefined values
                continue

            c = self.type_re.findall(e.name)
            if c:
                c = c[0][0]
            else:
                c = e.name
            if '_' in c:
                c = c.title().replace('_', '')
            elif c[0].islower():
                c = c.capitalize()
            self.type2class[e.name] = c

    def dump_dicts(self):  # for debug
        s = _NL_ + _INDENT_
        for n in ('type2class', 'prefixes', 'links'):
            d = getattr(self, n, None)
            if d:
                n = ['%s==== %s ==== %s' % (_NL_, n, self.parser.bindings_version())]
                sys.stderr.write(s.join(n + sorted('%s: %s\n' % t for t in d.items())))

    def epylink(self, docs, striprefix=None):
        """Link function, method and type names in doc string.
        """
        def _L(m):  # re.sub callback
            t = m.group(0)
            n = t.strip()
            k = self.links.get(n, '')
            if k:
                if striprefix:
                    k = striprefix(k)
                t = t.replace(n, 'L{%s}' % (k,))
            return t

        if self.links:
            return libvlc_re.sub(_L, docs)
        else:
            return docs

    def generate_enums(self):
        raise TypeError('must be overloaded')

    def insert_code(self, source, genums=False):
        """Include code from source file.
        """
        f = opener(source)
        for t in f:
            if genums and t.startswith(_GENERATED_ENUMS_):
                self.generate_enums()
            elif genums and t.startswith(_GENERATED_CALLBACKS_):
                self.generate_callbacks()
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
        """Close the output file.
        """
        if self.file not in (None, sys.stdout):
           self.file.close()
        self.file = None

    def outopen(self, name):
        """Open an output file.
        """
        if self.file:
            self.outclose()
            raise IOError('file left open: %s' % (self.outpath,))

        if name in ('-', 'stdout'):
            self.outpath = 'stdout'
            self.file = sys.stdout
        else:
            self.outpath = os.path.join(self.outdir, name)
            self.file = opener(self.outpath, 'w')

    def output(self, text, nl=0, nt=1):
        """Write to current output file.
        """
        if nl:  # leading newlines
            self.file.write(_NL_ * nl)
        self.file.write(text)
        if nt:  # trailing newlines
            self.file.write(_NL_ * nt)

    def unwrapped(self):
        """Report the unwrapped and blacklisted functions.
        """
        b = [f for f, t in _blacklist.items() if t]
        u = [f.name for f in self.parser.funcs if not f.wrapped]
        c = self.comment_line
        for f, t in ((b, 'blacklisted'),
                     (u, 'not wrapped as methods')):
            if f:
                self.output('%s %d function(s) %s:' % (c, len(f), t), nl=1)
                self.output(_NL_.join('%s  %s' % (c, f) for f in sorted(f)))  #PYCHOK false?


class PythonGenerator(_Generator):
    """Generate Python bindings.
    """
    type_re = re.compile(r'libvlc_(.+?)(_t)?$')  # Python

    # C-type to Python/ctypes type conversion.  Note, enum
    # type conversions are generated (cf convert_enums).
    type2class = {
        'libvlc_audio_output_t*':      'ctypes.POINTER(AudioOutput)',
        'libvlc_event_t*':              'ctypes.c_void_p',
        #'libvlc_callback_t':           'ctypes.c_void_p',
        'libvlc_dialog_id*':            'ctypes.c_void_p',
        'libvlc_drawable_t':           'ctypes.c_uint',  # FIXME?
        'libvlc_event_type_t':         'ctypes.c_uint',
        'libvlc_event_manager_t*':     'EventManager',
        'libvlc_instance_t*':          'Instance',
        'libvlc_log_t*':               'Log_ptr',
        'libvlc_log_iterator_t*':      'LogIterator',
        'libvlc_log_subscriber_t*':    'ctypes.c_void_p', # Opaque struct, do not mess with it.
        'libvlc_log_message_t*':       'ctypes.POINTER(LogMessage)',
        'libvlc_media_track_t**':      'ctypes.POINTER(MediaTrack)',
        'libvlc_media_track_t***':     'ctypes.POINTER(ctypes.POINTER(MediaTrack))',
        'libvlc_media_t*':             'Media',
        'libvlc_media_discoverer_t*':  'MediaDiscoverer',
        'libvlc_media_discoverer_description_t**': 'ctypes.POINTER(MediaDiscovererDescription)',
        'libvlc_media_discoverer_description_t***': 'ctypes.POINTER(ctypes.POINTER(MediaDiscovererDescription))',
        'libvlc_media_library_t*':     'MediaLibrary',
        'libvlc_media_list_t*':        'MediaList',
        'libvlc_media_list_player_t*': 'MediaListPlayer',
        'libvlc_media_list_view_t*':   'MediaListView',
        'libvlc_media_player_t*':      'MediaPlayer',
        'libvlc_video_viewpoint_t*':   'ctypes.POINTER(VideoViewpoint)',
        'libvlc_media_stats_t*':       'ctypes.POINTER(MediaStats)',
        'libvlc_picture_t*':           'Picture',
        'libvlc_media_thumbnail_request_t*':  'MediaThumbnailRequest', # Opaque struct, do not mess with it.
        'libvlc_renderer_item_t*':    'Renderer',
        'libvlc_renderer_discoverer_t*':    'RendererDiscoverer',
        'libvlc_rd_description_t**': 'ctypes.POINTER(RDDescription)',
        'libvlc_rd_description_t***': 'ctypes.POINTER(ctypes.POINTER(RDDescription))',
        'libvlc_media_track_info_t**': 'ctypes.POINTER(ctypes.c_void_p)',
        'libvlc_rectangle_t*':         'ctypes.POINTER(Rectangle)',
        'libvlc_time_t':               'ctypes.c_longlong',
        'libvlc_track_description_t*': 'ctypes.POINTER(TrackDescription)',
        'libvlc_title_description_t**': 'ctypes.POINTER(TitleDescription)',
        'libvlc_title_description_t***': 'ctypes.POINTER(ctypes.POINTER(TitleDescription))',
        'libvlc_chapter_description_t**': 'ctypes.POINTER(ChapterDescription)',
        'libvlc_chapter_description_t***': 'ctypes.POINTER(ctypes.POINTER(ChapterDescription))',
        'libvlc_module_description_t*': 'ctypes.POINTER(ModuleDescription)',
        'libvlc_audio_output_device_t*': 'ctypes.POINTER(AudioOutputDevice)',
        'libvlc_equalizer_t*':         'AudioEqualizer',
        'libvlc_media_slave_t**':    'ctypes.POINTER(MediaSlave)',
        'libvlc_media_slave_t***':    'ctypes.POINTER(ctypes.POINTER(MediaSlave))',
        'libvlc_video_direct3d_device_setup_t*': 'Direct3dDeviceSetup',
        'libvlc_video_direct3d_device_cfg_t*': 'Direct3dDeviceCfg',
        'libvlc_video_direct3d_cfg_t*': 'Direct3dCfg',
        'libvlc_video_output_cfg_t*': 'VideoOutputCfg',
        'libvlc_video_setup_device_cfg_t*': 'VideoSetupDeviceCfg',
        'libvlc_video_setup_device_info_t*': 'VideoSetupDeviceInfo',
        'libvlc_video_render_cfg_t*': 'VideoRenderCfg',
        'libvlc_video_direct3d_hdr10_metadata_t*': 'Direct3dHdr10Metadata',

        'FILE*':                       'FILE_ptr',

        '...':       'ctypes.c_void_p',
        'va_list':   'ctypes.c_void_p',
        'char*':     'ctypes.c_char_p',
        'unsigned char*':     'ctypes.c_char_p',
        'bool':      'ctypes.c_bool',
        'bool*':      'ctypes.POINTER(ctypes.c_bool)',
        'char**':    'ListPOINTER(ctypes.c_char_p)',
        'float':     'ctypes.c_float',
        'int':       'ctypes.c_int',
        'int*':      'ctypes.POINTER(ctypes.c_int)',  # _video_get_cursor
        'uintptr_t*':      'ctypes.POINTER(ctypes.c_uint)',
        'int64_t':   'ctypes.c_int64',
        'uint64_t':   'ctypes.c_uint64',
        'uint64_t*':   'ctypes.POINTER(ctypes.c_uint64)',
        'short':     'ctypes.c_short',
        'uint32_t':  'ctypes.c_uint32',
        'ssize_t':   'ctypes.c_ssize_t',
        'size_t':    'ctypes.c_size_t',
        'size_t*':   'ctypes.POINTER(ctypes.c_size_t)',
        'ssize_t*':   'ctypes.POINTER(ctypes.c_ssize_t)',
        'unsigned':  'ctypes.c_uint',
        'unsigned int':  'ctypes.c_uint',
        'unsigned*': 'ctypes.POINTER(ctypes.c_uint)',  # _video_get_size
        'void':      'None',
        'void*':     'ctypes.c_void_p',
        'void**':    'ctypes.POINTER(ctypes.c_void_p)',

        'WINDOWHANDLE': 'ctypes.c_ulong',
    }

    type2class_out = {
        'char**':    'ctypes.POINTER(ctypes.c_char_p)',
        'unsigned char*':    'ctypes.POINTER(ctypes.c_char)',
    }

    # Python classes, i.e. classes for which we want to
    # generate class wrappers around libvlc functions
    defined_classes = (
        'AudioEqualizer',
        'EventManager',
        'Instance',
        'Log',
        'LogIterator',
        'Media',
        'MediaDiscoverer',
        'MediaLibrary',
        'MediaList',
        'MediaListPlayer',
        'MediaListView',
        'MediaPlayer',
        'Picture',
        'Renderer',
        'RendererDiscoverer'
    )

    def __init__(self, parser=None):
        """New instance.

        @param parser: a L{Parser} instance.
        """
        _Generator.__init__(self, parser)
        # one special enum type class
        self.type2class['libvlc_event_e'] = 'EventType'
        # doc links to functions, methods and types
        self.links = {'libvlc_event_e': 'EventType'}
        # link enum value names to enum type/class
        for t in self.parser.enums:
            self.links[t.name] = self.class4(t.name)
        # prefixes to strip from method names
        # when wrapping them into class methods
        self.prefixes = {}
        for t, c in self.type2class.items():
            t = t.rstrip('*')
            if c in self.defined_classes:
                self.links[t] = c
                self.prefixes[c] = t[:-1]
            elif c.startswith('ctypes.POINTER('):
                c = c.replace('ctypes.POINTER(', '') \
                     .rstrip(')')
                if c[:1].isupper():
                    self.links[t] = c
        # We have to hardcode this one, which is not regular in vlc headers
        self.prefixes['AudioEqualizer'] = 'libvlc_audio_equalizer_'

        # xform docs to epydoc lines
        for f in self.parser.funcs:
            f.xform()
            self.links[f.name] = f.name
        for f in self.parser.callbacks:
            f.xform()
        self.check_types()

    def generate_ctypes(self):
        """Generate a ctypes decorator for all functions.
        """
        self.output("""
 # LibVLC __version__ functions #
""")
        for f in self.parser.funcs:
            name = f.name  #PYCHOK flake

            # arg names, excluding output args
            args = ', '.join(f.args())  #PYCHOK flake

            # tuples of arg flags
            flags = ', '.join(str(p.flags(f.out)) for p in f.pars)  #PYCHOK false?
            if flags:
                flags += ','

            # arg classes
            types = [self.class4(p.type, p.flags(f.out)[0]) for p in f.pars]

            # result type
            rtype = self.class4(f.type)

            if name in free_string_funcs:
                # some functions that return strings need special treatment
                if rtype != 'ctypes.c_char_p':
                    raise TypeError('Function %s expected to return char* not %s' % (name, f.type))
                errcheck = 'string_result'
                types = ['ctypes.c_void_p'] + types
            elif rtype in self.defined_classes:
                # if the result is a pointer to one of the defined
                # classes then we tell ctypes that the return type is
                # ctypes.c_void_p so that 64-bit pointers are handled
                # correctly, and then create a Python object of the
                # result
                errcheck = 'class_result(%s)' % rtype
                types = [ 'ctypes.c_void_p'] + types
            else:
                errcheck = 'None'
                types.insert(0, rtype)

            types = ', '.join(types)

            # xformed doc string with first @param
            docs = self.epylink(f.epydocs(0, 4))  #PYCHOK flake
            self.output("""def %(name)s(%(args)s):
    '''%(docs)s
    '''
    f = _Cfunctions.get('%(name)s', None) or \\
        _Cfunction('%(name)s', (%(flags)s), %(errcheck)s,
                    %(types)s)
    return f(%(args)s)
""" % locals())

    def generate_enums(self):
        """Generate classes for all enum types.
        """
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
            self.output("""class %s(_Enum):
    '''%s
    '''
    _enum_names_ = {""" % (cls, e.epydocs() or _NA_))

            for v in e.vals:
                self.output("        %s: '%s'," % (v.value, v.name))
            self.output('    }')

            # align on '=' signs
            w = -max(len(v.name) for v in e.vals)
            t = ['%s.%*s = %s(%s)' % (cls, w,v.name, cls, v.value) for v in e.vals]

            self.output(_NL_.join(sorted(t)), nt=2)

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
            name = self.class4(f.name)  #PYCHOK flake
            docs = self.epylink(f.epydocs(0, 4))
            self.output('''class %(name)s(ctypes.c_void_p):
    """%(docs)s
    """
    pass''' % locals())

        self.output("class CallbackDecorators(object):")
        self.output('    "Class holding various method decorators for callback functions."')
        for f in self.parser.callbacks:
            name = self.class4(f.name)  #PYCHOK flake

            # return value and arg classes
            types = ', '.join([self.class4(f.type)] +  #PYCHOK flake
                              [self.class4(p.type, p.flags(f.out)[0]) for p in f.pars])

            # xformed doc string with first @param
            docs = self.epylink(f.epydocs(0, 8))

            self.output("""    %(name)s = ctypes.CFUNCTYPE(%(types)s)
    %(name)s.__doc__ = '''%(docs)s
    '''""" % locals())
        self.output("cb = CallbackDecorators")

    def generate_wrappers(self):
        """Generate class wrappers for all appropriate functions.
        """
        def striprefix(name):
            return name.replace(x, '').replace('libvlc_', '')

        codes, methods, docstrs = self.parse_override(os.path.join(TEMPLATEDIR, 'override.py'))

        # sort functions on the type/class
        # of their first parameter
        t = []
        for f in self.parser.funcs:
             if f.pars:
                 p = f.pars[0]
                 c = self.class4(p.type)
                 if c in self.defined_classes:
                     t.append((c, f))
        cls = x = ''  # wrap functions in class methods
        for c, f in sorted(t, key=operator.itemgetter(0)):
            if cls != c:
                cls = c
                self.output("""class %s(_Ctype):
    '''%s
    '''""" % (cls, docstrs.get(cls, '') or _NA_)) # """ emacs-mode is confused...

                c = codes.get(cls, '')
                if not 'def __new__' in c:
                    self.output("""
    def __new__(cls, ptr=_internal_guard):
        '''(INTERNAL) ctypes wrapper constructor.
        '''
        return _Constructor(cls, ptr)""")

                if c:
                    self.output(c)
                x = self.prefixes.get(cls, 'libvlc_')

            f.wrapped += 1
            name = f.name

            # method name is function name less prefix
            meth = striprefix(name)
            if meth in methods.get(cls, []):
                continue  # overridden

            # arg names, excluding output args
            # and rename first arg to 'self'
            args = ', '.join(['self'] + f.args(1))  #PYCHOK flake "
            wrapped_args = ', '.join(['self'] + [ ('str_to_bytes(%s)' % pa.name
                                                   if pa.type == 'char*'
                                                   else pa.name)
                                                  for pa in f.in_params(1) ])  #PYCHOK flake

            # xformed doc string without first @param
            docs = self.epylink(f.epydocs(1, 8), striprefix)  #PYCHOK flake
            decorator = ""
            if meth.endswith('event_manager'):
                decorator = '    @memoize_parameterless'
            self.output("""%(decorator)s
    def %(meth)s(%(args)s):
        '''%(docs)s
        '''
        return %(name)s(%(wrapped_args)s)
""" % locals())

            # check for some standard methods
            if meth == 'count':
                # has a count method, generate __len__
                self.output("""    def __len__(self):
        return %s(self)
""" % (name,))
            elif meth.endswith('item_at_index'):
                # indexable (and thus iterable)
                self.output("""    def __getitem__(self, i):
        return %s(self, i)

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]
""" % (name,))

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
                    codes[k] = ''.join(v)
                k, v = m.group(1), []
            else:
                v.append(t)
        if k is not None:
            codes[k] = ''.join(v)
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

        return codes, methods, docstrs

    def save(self, path=None):
        """Write Python bindings to a file or C{stdout}.
        """
        self.outopen(path or '-')
        self.insert_code(os.path.join(TEMPLATEDIR, 'header.py'), genums=True)

        self.generate_wrappers()
        self.generate_ctypes()

        self.unwrapped()

        self.insert_code(os.path.join(TEMPLATEDIR, 'footer.py'))
        self.outclose()


class JavaGenerator(_Generator):
    """Generate Java/JNA bindings.
    """
    comment_line = '//'
    type_re      = re.compile(r'libvlc_(.+?)(_[te])?$')

    # C-type to Java/JNA type conversion.
    type2class = {
        'libvlc_audio_output_t*':      'LibVlcAudioOutput',
        'libvlc_callback_t':           'LibVlcCallback',
        'libvlc_event_type_t':         'LibvlcEventType',
        'libvlc_event_manager_t*':     'LibVlcEventManager',
        'libvlc_instance_t*':          'LibVlcInstance',
        'libvlc_log_t*':               'LibVlcLog',
        'libvlc_log_iterator_t*':      'LibVlcLogIterator',
        'libvlc_log_message_t*':       'LibvlcLogMessage',
        'libvlc_media_t*':             'LibVlcMedia',
        'libvlc_media_discoverer_t*':  'LibVlcMediaDiscoverer',
        'libvlc_media_library_t*':     'LibVlcMediaLibrary',
        'libvlc_media_list_t*':        'LibVlcMediaList',
        'libvlc_media_list_player_t*': 'LibVlcMediaListPlayer',
        'libvlc_media_list_view_t*':   'LibVlcMediaListView',
        'libvlc_media_player_t*':      'LibVlcMediaPlayer',
        'libvlc_media_stats_t*':       'LibVlcMediaStats',
        'libvlc_media_track_info_t**': 'LibVlcMediaTrackInfo',
        'libvlc_time_t':               'long',
        'libvlc_track_description_t*': 'LibVlcTrackDescription',

        '...':       'FIXME_va_list',
        'char*':     'String',
        'char**':    'String[]',
        'float':     'float',
        'int':       'int',
        'int*':      'Pointer',
        'int64_t':   'long',
        'short':     'short',
        'uint32_t':  'uint32',
        'unsigned':  'int',
        'unsigned*': 'Pointer',
        'void':      'void',
        'void*':     'Pointer',
    }

    def __init__(self, parser=None):
        """New instance.

        @param parser: a L{Parser} instance.
        """
        _Generator.__init__(self, parser)
        self.check_types()

    def generate_enums(self):
        """Generate Java/JNA glue code for enums.
        """
        for e in self.parser.enums:

            j = self.class4(e.name)
            self.outopen(j + '.java')

            self.insert_code(os.path.join(TEMPLATEDIR, 'boilerplate.java'))
            self.output("""package org.videolan.jvlc.internal;

public enum %s
{""" % (j,))
            # FIXME: write comment
            for v in e.vals:
                self.output('        %s (%s),' % (v.name, v.value))
            self.output("""
        private final int _value;
        %s(int value) { this._value = value; }
        public int value() { return this._value; }
}""" % (j,))
            self.outclose()

    def generate_header(self):
        """Generate LibVlc header.
        """
        for c, j in sorted(self.type2class.items()):
            if c.endswith('*') and j.startswith('LibVlc'):
                self.output("""
    public class %s extends PointerType
    {
    }""" % (j,))

    def generate_libvlc(self):
        """Generate LibVlc.java Java/JNA glue code.
        """
        self.outopen('LibVlc.java')

        self.insert_code(os.path.join(TEMPLATEDIR, 'boilerplate.java'))
        self.insert_code(os.path.join(TEMPLATEDIR, 'LibVlc-header.java'))

        self.generate_header()
        for f in self.parser.funcs:
            f.wrapped = 1  # for now
            p =    ', '.join('%s %s' % (self.class4(p.type), p.name) for p in f.pars)
            self.output('%s %s(%s);' % (self.class4(f.type), f.name, p), nt=2)

        self.insert_code(os.path.join(TEMPLATEDIR, 'LibVlc-footer.java'))

        self.unwrapped()
        self.outclose()

    def save(self, dir=None):
        """Write Java bindings into the given directory.
        """
        if dir in (None, '-'):
            d = 'internal'
            if not os.path.isdir(d):
                os.makedirs(d)  # os.mkdir(d)
        else:
            d = dir or os.curdir
        self.outdir = d

        sys.stderr.write('Generating Java code in %s...\n' % os.path.join(d, ''))

        self.generate_enums()
        self.generate_libvlc()


def process(output, h_files):
    """Generate Python bindings.
    """
    p = Parser(h_files)
    g = PythonGenerator(p)
    g.save(output)


def prepare_package(output):
    """Prepare a python-vlc package for the designated module.

    output is the location of the generated vlc.py file.
    """
    # Parse the module for VLC version number
    bindings_version = None
    libvlc_version = None
    with open(output, 'r') as f:
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
    with open(os.path.join(TEMPLATEDIR, 'setup.py')) as f:
        setup = f.read()
    # Fill in the template fields
    setup = setup.format(libvlc_version=libvlc_version,
                         generator_version=__version__,
                         bindings_version=bindings_version)
    with open(os.path.join(outdir, 'setup.py'), 'w') as f:
        f.write(setup)

    # Copy other files for distribution
    shutil.copyfile(os.path.join(TEMPLATEDIR, 'MANIFEST.in'),
                    os.path.join(outdir, 'MANIFEST.in'))
    examples = os.path.join(outdir, 'examples')
    if os.path.isdir(examples):
        shutil.rmtree(examples)
    shutil.copytree(os.path.join(BASEDIR, '..', 'examples'), examples)
    for fname in ('COPYING', 'README.module', 'distribute_setup.py'):
        shutil.copyfile(os.path.join(BASEDIR, '..', fname),
                        os.path.join(outdir, fname))

if __name__ == '__main__':

    from optparse import OptionParser

    opt = OptionParser(usage="""%prog  [options]  <include_vlc_directory> | <include_file.h> [...]

Parse VLC include files and generate bindings code for Python or Java.""")

    opt.add_option('-c', '--check', dest='check', action='store_true',
                   default=False,
                   help='Check mode, generates no bindings')

    opt.add_option('-d', '--debug', dest='debug', action='store_true',
                   default=False,
                   help='Debug mode, generate no bindings')

    opt.add_option('-j', '--java', dest='java', action='store_true',
                   default=False,
                   help='Generate Java bindings (default is Python)')

    opt.add_option('-o', '--output', dest='output', action='store', type='str',
                   default='-',
                   help='Output filename (for Python) or directory (for Java)')

    opt.add_option('-v', '--version', dest='version', action='store', type='str',
                   default='',
                   help='Version string for __version__ global')

    opt.add_option('-p', '--package', dest='package', action='store', type='str',
                   default='',
                   help='Prepare a package for the given python module.')

    opts, args = opt.parse_args()

    if '--debug' in sys.argv:
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
            p = os.path.join(p, '*.h')
        import glob
        args = glob.glob(p)

    p = Parser(args, opts.version)
    if opts.debug:
        for t in ('structs', 'enums', 'funcs', 'callbacks'):
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

    errors('%s error(s) reported')
