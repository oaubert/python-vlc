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
U{http://wiki.videolan.org/LibVLC}.

You can find the documentation and a README file with some examples
at U{http://www.olivieraubert.net/vlc/python-ctypes/}.

Basically, the most important class is L{Instance}, which is used
to create a libvlc instance.  From this instance, you then create
L{MediaPlayer} and L{MediaListPlayer} instances.

Alternatively, you may create instances of the L{MediaPlayer} and
L{MediaListPlayer} class directly and an instance of L{Instance}
will be implicitly created.  The latter can be obtained using the
C{get_instance} method of L{MediaPlayer} and L{MediaListPlayer}.
"""

import ctypes
from ctypes.util import find_library
import os
import sys
import functools

# Used by EventManager in override.py
from inspect import getargspec

import logging
logger = logging.getLogger(__name__)

build_date  = ''  # build time stamp and __version__, see generate.py

# The libvlc doc states that filenames are expected to be in UTF8, do
# not rely on sys.getfilesystemencoding() which will be confused,
# esp. on windows.
DEFAULT_ENCODING = 'utf-8'

if sys.version_info[0] > 2:
    str = str
    unicode = str
    bytes = bytes
    basestring = (str, bytes)
    PYTHON3 = True
    def str_to_bytes(s):
        """Translate string or bytes to bytes.
        """
        if isinstance(s, str):
            return bytes(s, DEFAULT_ENCODING)
        else:
            return s

    def bytes_to_str(b):
        """Translate bytes to string.
        """
        if isinstance(b, bytes):
            return b.decode(DEFAULT_ENCODING)
        else:
            return b
else:
    str = str
    unicode = unicode
    bytes = str
    basestring = basestring
    PYTHON3 = False
    def str_to_bytes(s):
        """Translate string or bytes to bytes.
        """
        if isinstance(s, unicode):
            return s.encode(DEFAULT_ENCODING)
        else:
            return s

    def bytes_to_str(b):
        """Translate bytes to unicode string.
        """
        if isinstance(b, str):
            return unicode(b, DEFAULT_ENCODING)
        else:
            return b

# Internal guard to prevent internal classes to be directly
# instanciated.
_internal_guard = object()

def find_lib():
    dll = None
    plugin_path = os.environ.get('PYTHON_VLC_MODULE_PATH', None)
    if 'PYTHON_VLC_LIB_PATH' in os.environ:
        try:
            dll = ctypes.CDLL(os.environ['PYTHON_VLC_LIB_PATH'])
        except OSError:
            logger.error("Cannot load lib specified by PYTHON_VLC_LIB_PATH env. variable")
            sys.exit(1)
    if plugin_path and not os.path.isdir(plugin_path):
        logger.error("Invalid PYTHON_VLC_MODULE_PATH specified. Please fix.")
        sys.exit(1)
    if dll is not None:
        return dll, plugin_path

    if sys.platform.startswith('linux'):
        p = find_library('vlc')
        try:
            dll = ctypes.CDLL(p)
        except OSError:  # may fail
            dll = ctypes.CDLL('libvlc.so.5')
    elif sys.platform.startswith('win'):
        libname = 'libvlc.dll'
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
                        r = w.OpenKey(r, 'Software\\VideoLAN\\VLC')
                        plugin_path, _ = w.QueryValueEx(r, 'InstallDir')
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
                for p in ('{programfiles}\\VideoLan{libname}', '{homedir}:\\VideoLan{libname}',
                          '{programfiles}{libname}',           '{homedir}:{libname}'):
                    p = p.format(homedir = homedir,
                                 programfiles = programfiles,
                                 libname = '\\VLC\\' + libname)
                    if os.path.exists(p):
                        plugin_path = os.path.dirname(p)
                        break
            if plugin_path is not None:  # try loading
                p = os.getcwd()
                os.chdir(plugin_path)
                 # if chdir failed, this will raise an exception
                dll = ctypes.CDLL(libname)
                 # restore cwd after dll has been loaded
                os.chdir(p)
            else:  # may fail
                dll = ctypes.CDLL(libname)
        else:
            plugin_path = os.path.dirname(p)
            dll = ctypes.CDLL(p)

    elif sys.platform.startswith('darwin'):
        # FIXME: should find a means to configure path
        d = '/Applications/VLC.app/Contents/MacOS/'
        c = d + 'lib/libvlccore.dylib'
        p = d + 'lib/libvlc.dylib'
        if os.path.exists(p) and os.path.exists(c):
            # pre-load libvlccore VLC 2.2.8+
            ctypes.CDLL(c)
            dll = ctypes.CDLL(p)
            for p in ('modules', 'plugins'):
                p = d + p
                if os.path.isdir(p):
                    plugin_path = p
                    break
        else:  # hope, some [DY]LD_LIBRARY_PATH is set...
            # pre-load libvlccore VLC 2.2.8+
            ctypes.CDLL('libvlccore.dylib')
            dll = ctypes.CDLL('libvlc.dylib')

    else:
        raise NotImplementedError('%s: %s not supported' % (sys.argv[0], sys.platform))

    return (dll, plugin_path)

# plugin_path used on win32 and MacOS in override.py
dll, plugin_path  = find_lib()

class VLCException(Exception):
    """Exception raised by libvlc methods.
    """
    pass

try:
    _Ints = (int, long)
except NameError:  # no long in Python 3+
    _Ints =  int
_Seqs = (list, tuple)

# Used for handling *event_manager() methods.
class memoize_parameterless(object):
    """Decorator. Caches a parameterless method's return value each time it is called.

    If called later with the same arguments, the cached value is returned
    (not reevaluated).
    Adapted from https://wiki.python.org/moin/PythonDecoratorLibrary
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
        """Return the function's docstring.
        """
        return self.func.__doc__

    def __get__(self, obj, objtype):
      """Support instance methods.
      """
      return functools.partial(self.__call__, obj)

# Default instance. It is used to instanciate classes directly in the
# OO-wrapper.
_default_instance = None

def get_default_instance():
    """Return the default VLC.Instance.
    """
    global _default_instance
    if _default_instance is None:
        _default_instance = Instance()
    return _default_instance

_Cfunctions = {}  # from LibVLC __version__
_Globals = globals()  # sys.modules[__name__].__dict__

def _Cfunction(name, flags, errcheck, *types):
    """(INTERNAL) New ctypes function binding.
    """
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
    raise NameError('no function %r' % (name,))

def _Cobject(cls, ctype):
    """(INTERNAL) New instance from ctypes.
    """
    o = object.__new__(cls)
    o._as_parameter_ = ctype
    return o

def _Constructor(cls, ptr=_internal_guard):
    """(INTERNAL) New wrapper from ctypes.
    """
    if ptr == _internal_guard:
        raise VLCException("(INTERNAL) ctypes class. You should get references for this class through methods of the LibVLC API.")
    if ptr is None or ptr == 0:
        return None
    return _Cobject(cls, ctypes.c_void_p(ptr))

class _Cstruct(ctypes.Structure):
    """(INTERNAL) Base class for ctypes structures.
    """
    _fields_ = []  # list of 2-tuples ('name', ctyptes.<type>)

    def __str__(self):
        l = [' %s:\t%s' % (n, getattr(self, n)) for n, _ in self._fields_]
        return '\n'.join([self.__class__.__name__] + l)

    def __repr__(self):
        return '%s.%s' % (self.__class__.__module__, self)

class _Ctype(object):
    """(INTERNAL) Base class for ctypes.
    """
    @staticmethod
    def from_param(this):  # not self
        """(INTERNAL) ctypes parameter conversion method.
        """
        if this is None:
            return None
        return this._as_parameter_

class ListPOINTER(object):
    """Just like a POINTER but accept a list of ctype as an argument.
    """
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

    It assumes the result is a char *.
    """
    if result:
        # make a python string copy
        s = bytes_to_str(ctypes.string_at(result))
        # free original string ptr
        libvlc_free(result)
        return s
    return None

def class_result(classname):
    """Errcheck function. Returns a function that creates the specified class.
    """
    def wrap_errcheck(result, func, arguments):
        if result is None:
            return None
        return classname(result)
    return wrap_errcheck

# Wrapper for the opaque struct libvlc_log_t
class Log(ctypes.Structure):
    pass
Log_ptr = ctypes.POINTER(Log)

# FILE* ctypes wrapper, copied from
# http://svn.python.org/projects/ctypes/trunk/ctypeslib/ctypeslib/contrib/pythonhdr.py
class FILE(ctypes.Structure):
    pass
FILE_ptr = ctypes.POINTER(FILE)

if PYTHON3:
    PyFile_FromFd = ctypes.pythonapi.PyFile_FromFd
    PyFile_FromFd.restype = ctypes.py_object
    PyFile_FromFd.argtypes = [ctypes.c_int,
                              ctypes.c_char_p,
                              ctypes.c_char_p,
                              ctypes.c_int,
                              ctypes.c_char_p,
                              ctypes.c_char_p,
                              ctypes.c_char_p,
                              ctypes.c_int ]

    PyFile_AsFd = ctypes.pythonapi.PyObject_AsFileDescriptor
    PyFile_AsFd.restype = ctypes.c_int
    PyFile_AsFd.argtypes = [ctypes.py_object]
else:
    PyFile_FromFile = ctypes.pythonapi.PyFile_FromFile
    PyFile_FromFile.restype = ctypes.py_object
    PyFile_FromFile.argtypes = [FILE_ptr,
                                ctypes.c_char_p,
                                ctypes.c_char_p,
                                ctypes.CFUNCTYPE(ctypes.c_int, FILE_ptr)]

    PyFile_AsFile = ctypes.pythonapi.PyFile_AsFile
    PyFile_AsFile.restype = FILE_ptr
    PyFile_AsFile.argtypes = [ctypes.py_object]

 # Generated enum types #
# GENERATED_ENUMS go here  # see generate.py
 # End of generated enum types #

 # From libvlc_structures.h

class AudioOutput(_Cstruct):

    def __str__(self):
        return '%s(%s:%s)' % (self.__class__.__name__, self.name, self.description)

AudioOutput._fields_ = [  # recursive struct
    ('name',        ctypes.c_char_p),
    ('description', ctypes.c_char_p),
    ('next',        ctypes.POINTER(AudioOutput)),
    ]

class LogMessage(_Cstruct):
    _fields_ = [
        ('size',     ctypes.c_uint  ),
        ('severity', ctypes.c_int   ),
        ('type',     ctypes.c_char_p),
        ('name',     ctypes.c_char_p),
        ('header',   ctypes.c_char_p),
        ('message',  ctypes.c_char_p),
    ]

    def __init__(self):
        super(LogMessage, self).__init__()
        self.size = ctypes.sizeof(self)

    def __str__(self):
        return '%s(%d:%s): %s' % (self.__class__.__name__, self.severity, self.type, self.message)

class MediaEvent(_Cstruct):
    _fields_ = [
        ('media_name',    ctypes.c_char_p),
        ('instance_name', ctypes.c_char_p),
    ]

class MediaStats(_Cstruct):
    _fields_ = [
        ('read_bytes',          ctypes.c_int  ),
        ('input_bitrate',       ctypes.c_float),
        ('demux_read_bytes',    ctypes.c_int  ),
        ('demux_bitrate',       ctypes.c_float),
        ('demux_corrupted',     ctypes.c_int  ),
        ('demux_discontinuity', ctypes.c_int  ),
        ('decoded_video',       ctypes.c_int  ),
        ('decoded_audio',       ctypes.c_int  ),
        ('displayed_pictures',  ctypes.c_int  ),
        ('lost_pictures',       ctypes.c_int  ),
        ('played_abuffers',     ctypes.c_int  ),
        ('lost_abuffers',       ctypes.c_int  ),
        ('sent_packets',        ctypes.c_int  ),
        ('sent_bytes',          ctypes.c_int  ),
        ('send_bitrate',        ctypes.c_float),
    ]

class MediaTrackInfo(_Cstruct):
    _fields_ = [
        ('codec',              ctypes.c_uint32),
        ('id',                 ctypes.c_int   ),
        ('type',               TrackType      ),
        ('profile',            ctypes.c_int   ),
        ('level',              ctypes.c_int   ),
        ('channels_or_height', ctypes.c_uint  ),
        ('rate_or_width',      ctypes.c_uint  ),
    ]

class AudioTrack(_Cstruct):
    _fields_ = [
        ('channels', ctypes.c_uint),
        ('rate', ctypes.c_uint),
        ]

class VideoTrack(_Cstruct):
    _fields_ = [
        ('height', ctypes.c_uint),
        ('width', ctypes.c_uint),
        ('sar_num', ctypes.c_uint),
        ('sar_den', ctypes.c_uint),
        ('frame_rate_num', ctypes.c_uint),
        ('frame_rate_den', ctypes.c_uint),
        ]

class SubtitleTrack(_Cstruct):
    _fields_ = [
        ('encoding', ctypes.c_char_p),
        ]

class MediaTrackTracks(ctypes.Union):
    _fields_ = [
        ('audio', ctypes.POINTER(AudioTrack)),
        ('video', ctypes.POINTER(VideoTrack)),
        ('subtitle', ctypes.POINTER(SubtitleTrack)),
        ]

class MediaTrack(_Cstruct):
    _anonymous_ = ("u",)
    _fields_ = [
        ('codec',              ctypes.c_uint32),
        ('original_fourcc',    ctypes.c_uint32),
        ('id',                 ctypes.c_int   ),
        ('type',               TrackType      ),
        ('profile',            ctypes.c_int   ),
        ('level',              ctypes.c_int   ),

        ('u',                  MediaTrackTracks),
        ('bitrate',            ctypes.c_uint),
        ('language',           ctypes.c_char_p),
        ('description',        ctypes.c_char_p),
        ]

class PlaylistItem(_Cstruct):
    _fields_ = [
        ('id',   ctypes.c_int   ),
        ('uri',  ctypes.c_char_p),
        ('name', ctypes.c_char_p),
    ]

    def __str__(self):
        return '%s #%d %s (uri %s)' % (self.__class__.__name__, self.id, self.name, self.uri)

class Position(object):
    """Enum-like, immutable window position constants.

       See e.g. VideoMarqueeOption.Position.
    """
    Center       = 0
    Left         = 1
    CenterLeft   = 1
    Right        = 2
    CenterRight  = 2
    Top          = 4
    TopCenter    = 4
    TopLeft      = 5
    TopRight     = 6
    Bottom       = 8
    BottomCenter = 8
    BottomLeft   = 9
    BottomRight  = 10
    def __init__(self, *unused):
        raise TypeError('constants only')
    def __setattr__(self, *unused):  #PYCHOK expected
        raise TypeError('immutable constants')

class Rectangle(_Cstruct):
    _fields_ = [
        ('top',    ctypes.c_int),
        ('left',   ctypes.c_int),
        ('bottom', ctypes.c_int),
        ('right',  ctypes.c_int),
    ]

class TrackDescription(_Cstruct):

    def __str__(self):
        return '%s(%d:%s)' % (self.__class__.__name__, self.id, self.name)

TrackDescription._fields_ = [  # recursive struct
    ('id',   ctypes.c_int   ),
    ('name', ctypes.c_char_p),
    ('next', ctypes.POINTER(TrackDescription)),
    ]

def track_description_list(head):
    """Convert a TrackDescription linked list to a Python list (and release the former).
    """
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

class EventUnion(ctypes.Union):
    _fields_ = [
        ('meta_type',    ctypes.c_uint    ),
        ('new_child',    ctypes.c_uint    ),
        ('new_duration', ctypes.c_longlong),
        ('new_status',   ctypes.c_int     ),
        ('media',        ctypes.c_void_p  ),
        ('new_state',    ctypes.c_uint    ),
        # FIXME: Media instance
        ('new_cache', ctypes.c_float   ),
        ('new_position', ctypes.c_float   ),
        ('new_time',     ctypes.c_longlong),
        ('new_title',    ctypes.c_int     ),
        ('new_seekable', ctypes.c_longlong),
        ('new_pausable', ctypes.c_longlong),
        ('new_scrambled', ctypes.c_longlong),
        ('new_count', ctypes.c_longlong),
        # FIXME: Skipped MediaList and MediaListView...
        ('filename',     ctypes.c_char_p  ),
        ('new_length',   ctypes.c_longlong),
        ('media_event',  MediaEvent       ),
    ]

class Event(_Cstruct):
    _fields_ = [
        ('type',   EventType      ),
        ('object', ctypes.c_void_p),
        ('u',      EventUnion     ),
    ]

class ModuleDescription(_Cstruct):

    def __str__(self):
        return '%s %s (%s)' % (self.__class__.__name__, self.shortname, self.name)

ModuleDescription._fields_ = [  # recursive struct
    ('name',      ctypes.c_char_p),
    ('shortname', ctypes.c_char_p),
    ('longname',  ctypes.c_char_p),
    ('help',      ctypes.c_char_p),
    ('next',      ctypes.POINTER(ModuleDescription)),
    ]

def module_description_list(head):
    """Convert a ModuleDescription linked list to a Python list (and release the former).
    """
    r = []
    if head:
        item = head
        while item:
            item = item.contents
            r.append((item.name, item.shortname, item.longname, item.help))
            item = item.next
        libvlc_module_description_list_release(head)
    return r

class AudioOutputDevice(_Cstruct):

    def __str__(self):
        return '%s(%d:%s)' % (self.__class__.__name__, self.id, self.name)

AudioOutputDevice._fields_ = [  # recursive struct
    ('next', ctypes.POINTER(AudioOutputDevice)),
    ('device',   ctypes.c_char_p   ),
    ('description', ctypes.c_char_p),
    ]

class TitleDescription(_Cstruct):
    _fields_ = [
        ('duration', ctypes.c_longlong),
        ('name', ctypes.c_char_p),
        ('menu', ctypes.c_bool),
    ]

class ChapterDescription(_Cstruct):
    _fields_ = [
        ('time_offset', ctypes.c_longlong),
        ('duration', ctypes.c_longlong),
        ('name', ctypes.c_char_p),
    ]

class VideoViewpoint(_Cstruct):
    _fields_ = [
        ('yaw', ctypes.c_float),
        ('pitch', ctypes.c_float),
        ('roll', ctypes.c_float),
        ('field_of_view', ctypes.c_float),
    ]

class MediaDiscovererDescription(_Cstruct):
    _fields_ = [
        ('name', ctypes.c_char_p),
        ('longname', ctypes.c_char_p),
        ('cat', MediaDiscovererCategory),
    ]

    def __str__(self):
        return '%s %s (%d) - %s' % (self.__class__.__name__, self.name, self.cat, self.longname)

# This struct depends on the MediaSlaveType enum that is defined only
# in > 2.2
if 'MediaSlaveType' in locals():
    class MediaSlave(_Cstruct):
        _fields_ = [
            ('psz_uri', ctypes.c_char_p),
            ('i_type', MediaSlaveType),
            ('i_priority', ctypes.c_uint)
        ]

class RDDescription(_Cstruct):
    _fields_ = [
        ('name', ctypes.c_char_p),
        ('longname', ctypes.c_char_p)
    ]


class MediaThumbnailRequest:
    def __new__(cls, *args):
        if len(args) == 1 and isinstance(args[0], _Ints):
            return _Constructor(cls, args[0])

# End of header.py #
