#! /usr/bin/python
# -*- coding: utf-8 -*-

# Python ctypes bindings for VLC
#
# Copyright (C) 2009-2017 the VideoLAN team
# $Id: $
#
# Authors: Olivier Aubert <contact at olivieraubert.net>
#          Jean Brouwers <MrJean1 at gmail.com>
#          Geoff Salmon <geoff.salmon at gmail.com>
#
# This library is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation; either version 2.1 of the
# License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston MA 02110-1301 USA

"""This module provides bindings for the LibVLC public API, see
http://wiki.videolan.org/LibVLC.

You can find the documentation and a README file with some examples
at https://www.olivieraubert.net/vlc/python-ctypes/.

Basically, the most important class is :class:`Instance`, which is used
to create a libvlc instance. From this instance, you then create
:class:`MediaPlayer` and :class:`MediaListPlayer` instances.

Alternatively, you may create instances of the :class:`MediaPlayer` and
:class:`MediaListPlayer` class directly and an instance of :class:`Instance`
will be implicitly created. The latter can be obtained using the
:meth:`MediaPlayer.get_instance` and :class:`MediaListPlayer`.
"""

import ctypes
import functools

# Used by EventManager in override.py
import inspect as _inspect
import logging
import os
import sys
from ctypes.util import find_library

logger = logging.getLogger(__name__)

build_date = ""  # build time stamp and __version__, see generate.py

# The libvlc doc states that filenames are expected to be in UTF8, do
# not rely on sys.getfilesystemencoding() which will be confused,
# esp. on windows.
DEFAULT_ENCODING = "utf-8"

if sys.version_info[0] > 2:
    str = str
    unicode = str
    bytes = bytes
    basestring = (str, bytes)
    PYTHON3 = True

    def str_to_bytes(s):
        """Translate string or bytes to bytes."""
        if isinstance(s, str):
            return bytes(s, DEFAULT_ENCODING)
        else:
            return s

    def bytes_to_str(b):
        """Translate bytes to string."""
        if isinstance(b, bytes):
            return b.decode(DEFAULT_ENCODING)
        else:
            return b

    def len_args(func):
        """Return number of positional arguments."""
        return len(_inspect.signature(func).parameters)

else:
    str = str
    unicode = unicode
    bytes = str
    basestring = basestring
    PYTHON3 = False

    def str_to_bytes(s):
        """Translate string or bytes to bytes."""
        if isinstance(s, unicode):
            return s.encode(DEFAULT_ENCODING)
        else:
            return s

    def bytes_to_str(b):
        """Translate bytes to unicode string."""
        if isinstance(b, str):
            return unicode(b, DEFAULT_ENCODING)
        else:
            return b

    def len_args(func):
        """Return number of positional arguments."""
        return len(_inspect.getargspec(func).args)


# Internal guard to prevent internal classes to be directly
# instanciated.
_internal_guard = object()


def find_lib():
    dll = None
    plugin_path = os.environ.get("PYTHON_VLC_MODULE_PATH", None)
    if "PYTHON_VLC_LIB_PATH" in os.environ:
        try:
            dll = ctypes.CDLL(os.environ["PYTHON_VLC_LIB_PATH"])
        except OSError:
            logger.error(
                "Cannot load lib specified by PYTHON_VLC_LIB_PATH env. variable"
            )
            sys.exit(1)
    if plugin_path and not os.path.isdir(plugin_path):
        logger.error("Invalid PYTHON_VLC_MODULE_PATH specified. Please fix.")
        sys.exit(1)
    if dll is not None:
        return dll, plugin_path

    if sys.platform.startswith("win"):
        libname = "libvlc.dll"
        p = find_library(libname)
        if p is None:
            try:  # some registry settings
                # leaner than win32api, win32con
                if PYTHON3:
                    import winreg as w
                else:
                    import _winreg as w
                for r in w.HKEY_LOCAL_MACHINE, w.HKEY_CURRENT_USER:
                    try:
                        r = w.OpenKey(r, "Software\\VideoLAN\\VLC")
                        plugin_path, _ = w.QueryValueEx(r, "InstallDir")
                        w.CloseKey(r)
                        break
                    except w.error:
                        pass
            except ImportError:  # no PyWin32
                pass
            if plugin_path is None:
                # try some standard locations.
                programfiles = os.environ["ProgramFiles"]
                homedir = os.environ["HOMEDRIVE"]
                for p in (
                    "{programfiles}\\VideoLan{libname}",
                    "{homedir}:\\VideoLan{libname}",
                    "{programfiles}{libname}",
                    "{homedir}:{libname}",
                ):
                    p = p.format(
                        homedir=homedir,
                        programfiles=programfiles,
                        libname="\\VLC\\" + libname,
                    )
                    if os.path.exists(p):
                        plugin_path = os.path.dirname(p)
                        break
            if plugin_path is not None:  # try loading
                # PyInstaller Windows fix
                if "PyInstallerCDLL" in ctypes.CDLL.__name__:
                    ctypes.windll.kernel32.SetDllDirectoryW(None)
                p = os.getcwd()
                os.chdir(plugin_path)
                # if chdir failed, this will raise an exception
                dll = ctypes.CDLL(".\\" + libname)
                # restore cwd after dll has been loaded
                os.chdir(p)
            else:  # may fail
                dll = ctypes.CDLL(".\\" + libname)
        else:
            plugin_path = os.path.dirname(p)
            dll = ctypes.CDLL(p)

    elif sys.platform.startswith("darwin"):
        # FIXME: should find a means to configure path
        d = "/Applications/VLC.app/Contents/MacOS/"
        c = d + "lib/libvlccore.dylib"
        p = d + "lib/libvlc.dylib"
        if os.path.exists(p) and os.path.exists(c):
            # pre-load libvlccore VLC 2.2.8+
            ctypes.CDLL(c)
            dll = ctypes.CDLL(p)
            for p in ("modules", "plugins"):
                p = d + p
                if os.path.isdir(p):
                    plugin_path = p
                    break
        else:  # hope, some [DY]LD_LIBRARY_PATH is set...
            # pre-load libvlccore VLC 2.2.8+
            ctypes.CDLL("libvlccore.dylib")
            dll = ctypes.CDLL("libvlc.dylib")

    else:
        # All other OSes (linux, freebsd...)
        p = find_library("vlc")
        try:
            dll = ctypes.CDLL(p)
        except OSError:  # may fail
            dll = None
        if dll is None:
            try:
                dll = ctypes.CDLL("libvlc.so.5")
            except:
                raise NotImplementedError("Cannot find libvlc lib")

    return (dll, plugin_path)


# plugin_path used on win32 and MacOS in override.py
dll, plugin_path = find_lib()


class VLCException(Exception):
    """Exception raised by libvlc methods."""

    pass


try:
    _Ints = (int, long)
except NameError:  # no long in Python 3+
    _Ints = int
_Seqs = (list, tuple)


# Used for handling *event_manager() methods.
class memoize_parameterless(object):
    """Decorator. Caches a parameterless method's return value each time it is called.

    If called later with the same arguments, the cached value is returned (not reevaluated).

    Adapted from https://wiki.python.org/moin/PythonDecoratorLibrary.
    """

    def __init__(self, func):
        self.func = func
        self._cache = {}

    def __call__(self, obj):
        try:
            return self._cache[obj]
        except KeyError:
            v = self._cache[obj] = self.func(obj)
            return v

    def __repr__(self):
        """Return the function's docstring."""
        return self.func.__doc__

    def __get__(self, obj, objtype):
        """Support instance methods."""
        return functools.partial(self.__call__, obj)


# Default instance. It is used to instanciate classes directly in the
# OO-wrapper.
_default_instance = None


def get_default_instance():
    """Returns the default :class:`Instance`."""
    global _default_instance
    if _default_instance is None:
        _default_instance = Instance()
    return _default_instance


def try_fspath(path):
    """Try calling ``os.fspath``.

    ``os.fspath`` is only available from py3.6.
    """
    try:
        return os.fspath(path)
    except (AttributeError, TypeError):
        return path


_Cfunctions = {}  # from LibVLC __version__
_Globals = globals()  # sys.modules[__name__].__dict__


def _Cfunction(name, flags, errcheck, *types):
    """(INTERNAL) New ctypes function binding."""
    if hasattr(dll, name) and name in _Globals:
        p = ctypes.CFUNCTYPE(*types)
        f = p((name, dll), flags)
        if errcheck is not None:
            f.errcheck = errcheck
        # replace the Python function
        # in this module, but only when
        # running as python -O or -OO
        if __debug__:
            _Cfunctions[name] = f
        else:
            _Globals[name] = f
        return f
    raise NameError("no function %r" % (name,))


def _Cobject(cls, ctype):
    """(INTERNAL) New instance from ctypes."""
    o = object.__new__(cls)
    o._as_parameter_ = ctype
    return o


def _Constructor(cls, ptr=_internal_guard):
    """(INTERNAL) New wrapper from ctypes."""
    if ptr == _internal_guard:
        raise VLCException(
            "(INTERNAL) ctypes class. You should get references for this class through methods of the LibVLC API."
        )
    if ptr is None or ptr == 0:
        return None
    return _Cobject(cls, ctypes.c_void_p(ptr))


class _Cstruct(ctypes.Structure):
    """(INTERNAL) Base class for ctypes structures."""

    _fields_ = []  # list of 2-tuples ('name', ctypes.<type>)

    def __str__(self):
        l = [" %s:\t%s" % (n, getattr(self, n)) for n, _ in self._fields_]
        return "\n".join([self.__class__.__name__] + l)

    def __repr__(self):
        return "%s.%s" % (self.__class__.__module__, self)


class _Ctype(object):
    """(INTERNAL) Base class for ctypes."""

    @staticmethod
    def from_param(this):  # not self
        """(INTERNAL) ctypes parameter conversion method."""
        if this is None:
            return None
        return this._as_parameter_


class ListPOINTER(object):
    """Just like a POINTER but accept a list of etype elements as an argument."""

    def __init__(self, etype):
        self.etype = etype

    def from_param(self, param):
        if isinstance(param, _Seqs):
            return (self.etype * len(param))(*param)
        else:
            return ctypes.POINTER(param)


# errcheck functions for some native functions.
def string_result(result, func, arguments):
    """Errcheck function. Returns a string and frees the original pointer.

    It assumes the result is a ``char*``.
    """
    if result:
        # make a python string copy
        s = bytes_to_str(ctypes.string_at(result))
        # free original string ptr
        libvlc_free(result)
        return s
    return None


def class_result(classname):
    """Errcheck function. Returns a function that creates the specified class."""

    def wrap_errcheck(result, func, arguments):
        if result is None:
            return None
        return classname(result)

    return wrap_errcheck


# Wrapper for the opaque struct libvlc_log_t
class Log(ctypes.Structure):
    pass


Log_ptr = ctypes.POINTER(Log)


# Wrapper for the opaque struct libvlc_media_thumbnail_request_t
class MediaThumbnailRequest:
    def __new__(cls, *args):
        if len(args) == 1 and isinstance(args[0], _Ints):
            return _Constructor(cls, args[0])


# FILE* ctypes wrapper, copied from
# http://svn.python.org/projects/ctypes/trunk/ctypeslib/ctypeslib/contrib/pythonhdr.py
class FILE(ctypes.Structure):
    pass


FILE_ptr = ctypes.POINTER(FILE)

if PYTHON3:
    PyFile_FromFd = ctypes.pythonapi.PyFile_FromFd
    PyFile_FromFd.restype = ctypes.py_object
    PyFile_FromFd.argtypes = [
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.c_int,
    ]

    PyFile_AsFd = ctypes.pythonapi.PyObject_AsFileDescriptor
    PyFile_AsFd.restype = ctypes.c_int
    PyFile_AsFd.argtypes = [ctypes.py_object]
else:
    PyFile_FromFile = ctypes.pythonapi.PyFile_FromFile
    PyFile_FromFile.restype = ctypes.py_object
    PyFile_FromFile.argtypes = [
        FILE_ptr,
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.CFUNCTYPE(ctypes.c_int, FILE_ptr),
    ]

    PyFile_AsFile = ctypes.pythonapi.PyFile_AsFile
    PyFile_AsFile.restype = FILE_ptr
    PyFile_AsFile.argtypes = [ctypes.py_object]


def module_description_list(head):
    """Convert a ModuleDescription linked list to a Python list (and release the former)."""
    r = []
    if head:
        item = head
        while item:
            item = item.contents
            r.append((item.name, item.shortname, item.longname, item.help))
            item = item.next
        libvlc_module_description_list_release(head)
    return r


def track_description_list(head):
    """Convert a TrackDescription linked list to a Python list (and release the former)."""
    r = []
    if head:
        item = head
        while item:
            item = item.contents
            r.append((item.id, item.name))
            item = item.next
        try:
            libvlc_track_description_release(head)
        except NameError:
            libvlc_track_description_list_release(head)

    return r


class _Enum(ctypes.c_uint):
    """(INTERNAL) Base class"""

    _enum_names_ = {}

    def __str__(self):
        n = self._enum_names_.get(self.value, "") or ("FIXME_(%r)" % (self.value,))
        return ".".join((self.__class__.__name__, n))

    def __hash__(self):
        return self.value

    def __repr__(self):
        return ".".join((self.__class__.__module__, self.__str__()))

    def __eq__(self, other):
        return (isinstance(other, _Enum) and self.value == other.value) or (
            isinstance(other, _Ints) and self.value == other
        )

    def __ne__(self, other):
        return not self.__eq__(other)


# Generated wrappers #
# GENERATED_WRAPPERS go here  # see generate.py
# End of generated wrappers #

# Generated enum types #
# GENERATED_ENUMS go here  # see generate.py
# End of generated enum types #

# Generated structs #
# GENERATED_STRUCTS go here  # see generate.py
# End of generated structs #

# Generated callback definitions #
# GENERATED_CALLBACKS
# End of generated callback definitions #

# Generated functions #
# GENERATED_FUNCTIONS
# End of generated functions #

# End of header.py #
