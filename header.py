#! /usr/bin/python

# Python ctypes bindings for VLC
#
# Copyright (C) 2009-2010 the VideoLAN team
# $Id: $
#
# Authors: Olivier Aubert <olivier.aubert at liris.cnrs.fr>
#          Jean Brouwers <MrJean1 at gmail.com>
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

"""This module provides bindings for the LibVLC public API, see
U{http://wiki.videolan.org/LibVLC}.

You can find the documentation and a README file with some examples
at U{http://www.advene.org/download/python-ctypes/}.

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

# Used by EventManager in override.py
from inspect import getargspec

build_date  = ''  # build time stamp and __version__, see generate.py

# Internal guard to prevent internal classes to be directly
# instanciated.
_internal_guard = object()

def find_lib():
    dll = None
    plugin_path = None
    if sys.platform.startswith('linux'):
        p = find_library('vlc')
        try:
            dll = ctypes.CDLL(p)
        except OSError:  # may fail
            dll = ctypes.CDLL('libvlc.so.5')
    elif sys.platform.startswith('win'):
        p = find_library('libvlc.dll')
        if p is None:
            try:  # some registry settings
                import _winreg as w  # leaner than win32api, win32con
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
                for p in ('Program Files\\VideoLan\\', 'VideoLan\\',
                          'Program Files\\',           ''):
                    p = 'C:\\' + p + 'VLC\\libvlc.dll'
                    if os.path.exists(p):
                        plugin_path = os.path.dirname(p)
                        break
            if plugin_path is not None:  # try loading
                p = os.getcwd()
                os.chdir(plugin_path)
                 # if chdir failed, this will raise an exception
                dll = ctypes.CDLL('libvlc.dll')
                 # restore cwd after dll has been loaded
                os.chdir(p)
            else:  # may fail
                dll = ctypes.CDLL('libvlc.dll')
        else:
            plugin_path = os.path.dirname(p)
            dll = ctypes.CDLL(p)

    elif sys.platform.startswith('darwin'):
        # FIXME: should find a means to configure path
        d = '/Applications/VLC.app/Contents/MacOS/'
        p = d + 'lib/libvlc.dylib'
        if os.path.exists(p):
            dll = ctypes.CDLL(p)
            d += 'modules'
            if os.path.isdir(d):
                plugin_path = d
        else:  # hope, some PATH is set...
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

_Seqs = (list, tuple)

_Cfunctions = {}  # from LibVLC __version__

def _Cfunction(name, flags, errcheck, *types):
    """(INTERNAL) New ctypes function binding.
    """
    if hasattr(dll, name):
        p = ctypes.CFUNCTYPE(*types)
        f = p((name, dll), flags)
        if errcheck is not None:
            f.errcheck = errcheck
        _Cfunctions[name] = f
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

# errcheck functions for some native functions.
def string_result(result, func, arguments):
    """Errcheck function. Returns a string and frees the original pointer.

    It assumes the result is a char *.
    """
    if result:
        # make a python string copy
        s = ctypes.string_at(result)
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
        # Media instance
        ('new_position', ctypes.c_float   ),
        ('new_time',     ctypes.c_longlong),
        ('new_title',    ctypes.c_int     ),
        ('new_seekable', ctypes.c_longlong),
        ('new_pausable', ctypes.c_longlong),
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

 # End of header.py #

