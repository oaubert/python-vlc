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
at U{https://www.olivieraubert.net/vlc/python-ctypes/}.

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
import inspect as _inspect
import logging
logger = logging.getLogger(__name__)

__version__ = "4.0.0122"
__libvlc_version__ = "4.0.0"
__generator_version__ = "1.22"
build_date  = "Wed Apr 19 17:27:22 2023 4.0.0"

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

    def len_args(func):
        """Return number of positional arguments.
        """
        return len(_inspect.signature(func).parameters)

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

    def len_args(func):
        """Return number of positional arguments.
        """
        return len(_inspect.getargspec(func).args)

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

    if sys.platform.startswith('win'):
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
                 # PyInstaller Windows fix
                if 'PyInstallerCDLL' in ctypes.CDLL.__name__:
                    ctypes.windll.kernel32.SetDllDirectoryW(None)
                p = os.getcwd()
                os.chdir(plugin_path)
                 # if chdir failed, this will raise an exception
                dll = ctypes.CDLL('.\\' + libname)
                 # restore cwd after dll has been loaded
                os.chdir(p)
            else:  # may fail
                dll = ctypes.CDLL('.\\' + libname)
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
        # All other OSes (linux, freebsd...)
        p = find_library('vlc')
        try:
            dll = ctypes.CDLL(p)
        except OSError:  # may fail
            dll = None
        if dll is None:
            try:
                dll = ctypes.CDLL('libvlc.so.5')
            except:
                raise NotImplementedError('Cannot find libvlc lib')

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

def try_fspath(path):
    """Try calling os.fspath
    os.fspath is only available from py3.6
    """
    try:
        return os.fspath(path)
    except (AttributeError, TypeError):
        return path

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
    _fields_ = []  # list of 2-tuples ('name', ctypes.<type>)

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
    """Just like a POINTER but accept a list of etype elements as an argument.
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

# Generated enum types #

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

class LogLevel(_Enum):
    '''Logging messages level.
\note future libvlc versions may define new levels.
    '''
    _enum_names_ = {
        0: 'DEBUG',
        2: 'NOTICE',
        3: 'WARNING',
        4: 'ERROR',
    }
LogLevel.DEBUG   = LogLevel(0)
LogLevel.ERROR   = LogLevel(4)
LogLevel.NOTICE  = LogLevel(2)
LogLevel.WARNING = LogLevel(3)

class DialogQuestionType(_Enum):
    '''@defgroup libvlc_dialog libvlc dialog
@ingroup libvlc
@{
@file
libvlc dialog external api.
    '''
    _enum_names_ = {
        0: 'DIALOG_QUESTION_NORMAL',
        1: 'DIALOG_QUESTION_WARNING',
        2: 'DIALOG_QUESTION_CRITICAL',
    }
DialogQuestionType.DIALOG_QUESTION_CRITICAL = DialogQuestionType(2)
DialogQuestionType.DIALOG_QUESTION_NORMAL   = DialogQuestionType(0)
DialogQuestionType.DIALOG_QUESTION_WARNING  = DialogQuestionType(1)

class EventType(_Enum):
    '''Event types.
    '''
    _enum_names_ = {
        0: 'MediaMetaChanged',
        1: 'MediaSubItemAdded',
        2: 'MediaDurationChanged',
        3: 'MediaParsedChanged',
        6: 'MediaSubItemTreeAdded',
        7: 'MediaThumbnailGenerated',
        8: 'MediaAttachedThumbnailsFound',
        0x100: 'MediaPlayerMediaChanged',
        257: 'MediaPlayerNothingSpecial',
        258: 'MediaPlayerOpening',
        259: 'MediaPlayerBuffering',
        260: 'MediaPlayerPlaying',
        261: 'MediaPlayerPaused',
        262: 'MediaPlayerStopped',
        263: 'MediaPlayerForward',
        264: 'MediaPlayerBackward',
        265: 'MediaPlayerStopping',
        266: 'MediaPlayerEncounteredError',
        267: 'MediaPlayerTimeChanged',
        268: 'MediaPlayerPositionChanged',
        269: 'MediaPlayerSeekableChanged',
        270: 'MediaPlayerPausableChanged',
        272: 'MediaPlayerSnapshotTaken',
        273: 'MediaPlayerLengthChanged',
        274: 'MediaPlayerVout',
        276: 'MediaPlayerESAdded',
        277: 'MediaPlayerESDeleted',
        278: 'MediaPlayerESSelected',
        279: 'MediaPlayerCorked',
        280: 'MediaPlayerUncorked',
        281: 'MediaPlayerMuted',
        282: 'MediaPlayerUnmuted',
        283: 'MediaPlayerAudioVolume',
        284: 'MediaPlayerAudioDevice',
        285: 'MediaPlayerESUpdated',
        286: 'MediaPlayerProgramAdded',
        287: 'MediaPlayerProgramDeleted',
        288: 'MediaPlayerProgramSelected',
        289: 'MediaPlayerProgramUpdated',
        290: 'MediaPlayerTitleListChanged',
        291: 'MediaPlayerTitleSelectionChanged',
        292: 'MediaPlayerChapterChanged',
        293: 'MediaPlayerRecordChanged',
        0x200: 'MediaListItemAdded',
        513: 'MediaListWillAddItem',
        514: 'MediaListItemDeleted',
        515: 'MediaListWillDeleteItem',
        516: 'MediaListEndReached',
        0x300: 'MediaListViewItemAdded',
        769: 'MediaListViewWillAddItem',
        770: 'MediaListViewItemDeleted',
        771: 'MediaListViewWillDeleteItem',
        0x400: 'MediaListPlayerPlayed',
        1025: 'MediaListPlayerNextItemSet',
        1026: 'MediaListPlayerStopped',
        0x502: 'RendererDiscovererItemAdded',
        1283: 'RendererDiscovererItemDeleted',
    }
EventType.MediaAttachedThumbnailsFound     = EventType(8)
EventType.MediaDurationChanged             = EventType(2)
EventType.MediaListEndReached              = EventType(516)
EventType.MediaListItemAdded               = EventType(0x200)
EventType.MediaListItemDeleted             = EventType(514)
EventType.MediaListPlayerNextItemSet       = EventType(1025)
EventType.MediaListPlayerPlayed            = EventType(0x400)
EventType.MediaListPlayerStopped           = EventType(1026)
EventType.MediaListViewItemAdded           = EventType(0x300)
EventType.MediaListViewItemDeleted         = EventType(770)
EventType.MediaListViewWillAddItem         = EventType(769)
EventType.MediaListViewWillDeleteItem      = EventType(771)
EventType.MediaListWillAddItem             = EventType(513)
EventType.MediaListWillDeleteItem          = EventType(515)
EventType.MediaMetaChanged                 = EventType(0)
EventType.MediaParsedChanged               = EventType(3)
EventType.MediaPlayerAudioDevice           = EventType(284)
EventType.MediaPlayerAudioVolume           = EventType(283)
EventType.MediaPlayerBackward              = EventType(264)
EventType.MediaPlayerBuffering             = EventType(259)
EventType.MediaPlayerChapterChanged        = EventType(292)
EventType.MediaPlayerCorked                = EventType(279)
EventType.MediaPlayerESAdded               = EventType(276)
EventType.MediaPlayerESDeleted             = EventType(277)
EventType.MediaPlayerESSelected            = EventType(278)
EventType.MediaPlayerESUpdated             = EventType(285)
EventType.MediaPlayerEncounteredError      = EventType(266)
EventType.MediaPlayerForward               = EventType(263)
EventType.MediaPlayerLengthChanged         = EventType(273)
EventType.MediaPlayerMediaChanged          = EventType(0x100)
EventType.MediaPlayerMuted                 = EventType(281)
EventType.MediaPlayerNothingSpecial        = EventType(257)
EventType.MediaPlayerOpening               = EventType(258)
EventType.MediaPlayerPausableChanged       = EventType(270)
EventType.MediaPlayerPaused                = EventType(261)
EventType.MediaPlayerPlaying               = EventType(260)
EventType.MediaPlayerPositionChanged       = EventType(268)
EventType.MediaPlayerProgramAdded          = EventType(286)
EventType.MediaPlayerProgramDeleted        = EventType(287)
EventType.MediaPlayerProgramSelected       = EventType(288)
EventType.MediaPlayerProgramUpdated        = EventType(289)
EventType.MediaPlayerRecordChanged         = EventType(293)
EventType.MediaPlayerSeekableChanged       = EventType(269)
EventType.MediaPlayerSnapshotTaken         = EventType(272)
EventType.MediaPlayerStopped               = EventType(262)
EventType.MediaPlayerStopping              = EventType(265)
EventType.MediaPlayerTimeChanged           = EventType(267)
EventType.MediaPlayerTitleListChanged      = EventType(290)
EventType.MediaPlayerTitleSelectionChanged = EventType(291)
EventType.MediaPlayerUncorked              = EventType(280)
EventType.MediaPlayerUnmuted               = EventType(282)
EventType.MediaPlayerVout                  = EventType(274)
EventType.MediaSubItemAdded                = EventType(1)
EventType.MediaSubItemTreeAdded            = EventType(6)
EventType.MediaThumbnailGenerated          = EventType(7)
EventType.RendererDiscovererItemAdded      = EventType(0x502)
EventType.RendererDiscovererItemDeleted    = EventType(1283)

class Meta(_Enum):
    '''Meta data types.
    '''
    _enum_names_ = {
        0: 'Title',
        1: 'Artist',
        2: 'Genre',
        3: 'Copyright',
        4: 'Album',
        5: 'TrackNumber',
        6: 'Description',
        7: 'Rating',
        8: 'Date',
        9: 'Setting',
        10: 'URL',
        11: 'Language',
        12: 'NowPlaying',
        13: 'Publisher',
        14: 'EncodedBy',
        15: 'ArtworkURL',
        16: 'TrackID',
        17: 'TrackTotal',
        18: 'Director',
        19: 'Season',
        20: 'Episode',
        21: 'ShowName',
        22: 'Actors',
        23: 'AlbumArtist',
        24: 'DiscNumber',
        25: 'DiscTotal',
    }
Meta.Actors      = Meta(22)
Meta.Album       = Meta(4)
Meta.AlbumArtist = Meta(23)
Meta.Artist      = Meta(1)
Meta.ArtworkURL  = Meta(15)
Meta.Copyright   = Meta(3)
Meta.Date        = Meta(8)
Meta.Description = Meta(6)
Meta.Director    = Meta(18)
Meta.DiscNumber  = Meta(24)
Meta.DiscTotal   = Meta(25)
Meta.EncodedBy   = Meta(14)
Meta.Episode     = Meta(20)
Meta.Genre       = Meta(2)
Meta.Language    = Meta(11)
Meta.NowPlaying  = Meta(12)
Meta.Publisher   = Meta(13)
Meta.Rating      = Meta(7)
Meta.Season      = Meta(19)
Meta.Setting     = Meta(9)
Meta.ShowName    = Meta(21)
Meta.Title       = Meta(0)
Meta.TrackID     = Meta(16)
Meta.TrackNumber = Meta(5)
Meta.TrackTotal  = Meta(17)
Meta.URL         = Meta(10)

class State(_Enum):
    '''Libvlc media or media_player state.
    '''
    _enum_names_ = {
        0: 'NothingSpecial',
        1: 'Opening',
        2: 'Buffering',
        3: 'Playing',
        4: 'Paused',
        5: 'Stopped',
        6: 'Stopping',
        7: 'Error',
    }
State.Buffering      = State(2)
State.Error          = State(7)
State.NothingSpecial = State(0)
State.Opening        = State(1)
State.Paused         = State(4)
State.Playing        = State(3)
State.Stopped        = State(5)
State.Stopping       = State(6)

class MediaType(_Enum):
    '''Media type
See libvlc_media_get_type.
    '''
    _enum_names_ = {
        0: 'unknown',
        1: 'file',
        2: 'directory',
        3: 'disc',
        4: 'stream',
        5: 'playlist',
    }
MediaType.directory = MediaType(2)
MediaType.disc      = MediaType(3)
MediaType.file      = MediaType(1)
MediaType.playlist  = MediaType(5)
MediaType.stream    = MediaType(4)
MediaType.unknown   = MediaType(0)

class MediaParseFlag(_Enum):
    '''Parse flags used by libvlc_media_parse_request().
    '''
    _enum_names_ = {
        0x0: 'local',
        0x1: 'network',
        0x2: 'fetch_local',
        0x4: 'fetch_network',
        0x8: 'do_interact',
        0x10: 'no_skip',
    }
MediaParseFlag.do_interact   = MediaParseFlag(0x8)
MediaParseFlag.fetch_local   = MediaParseFlag(0x2)
MediaParseFlag.fetch_network = MediaParseFlag(0x4)
MediaParseFlag.local         = MediaParseFlag(0x0)
MediaParseFlag.network       = MediaParseFlag(0x1)
MediaParseFlag.no_skip       = MediaParseFlag(0x10)

class MediaParsedStatus(_Enum):
    '''Parse status used sent by libvlc_media_parse_request() or returned by
libvlc_media_get_parsed_status().
    '''
    _enum_names_ = {
        0: 'none',
        1: 'pending',
        2: 'skipped',
        3: 'failed',
        4: 'timeout',
        5: 'done',
    }
MediaParsedStatus.done    = MediaParsedStatus(5)
MediaParsedStatus.failed  = MediaParsedStatus(3)
MediaParsedStatus.none    = MediaParsedStatus(0)
MediaParsedStatus.pending = MediaParsedStatus(1)
MediaParsedStatus.skipped = MediaParsedStatus(2)
MediaParsedStatus.timeout = MediaParsedStatus(4)

class MediaSlaveType(_Enum):
    '''Type of a media slave: subtitle or audio.
    '''
    _enum_names_ = {
        0: 'subtitle',
        1: 'generic',
        1: 'audio',
    }
MediaSlaveType.audio    = MediaSlaveType(1)
MediaSlaveType.generic  = MediaSlaveType(1)
MediaSlaveType.subtitle = MediaSlaveType(0)

class ThumbnailerSeekSpeed(_Enum):
    '''N/A
    '''
    _enum_names_ = {
        0: 'media_thumbnail_seek_precise',
        1: 'media_thumbnail_seek_fast',
    }
ThumbnailerSeekSpeed.media_thumbnail_seek_fast    = ThumbnailerSeekSpeed(1)
ThumbnailerSeekSpeed.media_thumbnail_seek_precise = ThumbnailerSeekSpeed(0)

class MediaDiscovererCategory(_Enum):
    '''Category of a media discoverer
See libvlc_media_discoverer_list_get().
    '''
    _enum_names_ = {
        0: 'devices',
        1: 'lan',
        2: 'podcasts',
        3: 'localdirs',
    }
MediaDiscovererCategory.devices   = MediaDiscovererCategory(0)
MediaDiscovererCategory.lan       = MediaDiscovererCategory(1)
MediaDiscovererCategory.localdirs = MediaDiscovererCategory(3)
MediaDiscovererCategory.podcasts  = MediaDiscovererCategory(2)

class PlaybackMode(_Enum):
    '''Defines playback modes for playlist.
    '''
    _enum_names_ = {
        0: 'default',
        1: 'loop',
        2: 'repeat',
    }
PlaybackMode.default = PlaybackMode(0)
PlaybackMode.loop    = PlaybackMode(1)
PlaybackMode.repeat  = PlaybackMode(2)

class VideoMarqueeOption(_Enum):
    '''Marq options definition.
    '''
    _enum_names_ = {
        0: 'Enable',
        1: 'Text',
        2: 'Color',
        3: 'Opacity',
        4: 'Position',
        5: 'Refresh',
        6: 'Size',
        7: 'Timeout',
        8: 'X',
        9: 'Y',
    }
VideoMarqueeOption.Color    = VideoMarqueeOption(2)
VideoMarqueeOption.Enable   = VideoMarqueeOption(0)
VideoMarqueeOption.Opacity  = VideoMarqueeOption(3)
VideoMarqueeOption.Position = VideoMarqueeOption(4)
VideoMarqueeOption.Refresh  = VideoMarqueeOption(5)
VideoMarqueeOption.Size     = VideoMarqueeOption(6)
VideoMarqueeOption.Text     = VideoMarqueeOption(1)
VideoMarqueeOption.Timeout  = VideoMarqueeOption(7)
VideoMarqueeOption.X        = VideoMarqueeOption(8)
VideoMarqueeOption.Y        = VideoMarqueeOption(9)

class NavigateMode(_Enum):
    '''Navigation mode.
    '''
    _enum_names_ = {
        0: 'activate',
        1: 'up',
        2: 'down',
        3: 'left',
        4: 'right',
        5: 'popup',
    }
NavigateMode.activate = NavigateMode(0)
NavigateMode.down     = NavigateMode(2)
NavigateMode.left     = NavigateMode(3)
NavigateMode.popup    = NavigateMode(5)
NavigateMode.right    = NavigateMode(4)
NavigateMode.up       = NavigateMode(1)

class Position(_Enum):
    '''Enumeration of values used to set position (e.g. of video title).
    '''
    _enum_names_ = {
        -1: 'disable',
        0: 'center',
        1: 'left',
        2: 'right',
        3: 'top',
        4: 'top_left',
        5: 'top_right',
        6: 'bottom',
        7: 'bottom_left',
        8: 'bottom_right',
    }
Position.bottom       = Position(6)
Position.bottom_left  = Position(7)
Position.bottom_right = Position(8)
Position.center       = Position(0)
Position.disable      = Position(-1)
Position.left         = Position(1)
Position.right        = Position(2)
Position.top          = Position(3)
Position.top_left     = Position(4)
Position.top_right    = Position(5)

class TeletextKey(_Enum):
    '''Enumeration of teletext keys than can be passed via
libvlc_video_set_teletext().
    '''
    _enum_names_ = {
        7471104: 'red',
        6750208: 'green',
        7929856: 'yellow',
        6422528: 'blue',
        6881280: 'index',
    }
TeletextKey.blue   = TeletextKey(6422528)
TeletextKey.green  = TeletextKey(6750208)
TeletextKey.index  = TeletextKey(6881280)
TeletextKey.red    = TeletextKey(7471104)
TeletextKey.yellow = TeletextKey(7929856)

class VideoColorPrimaries(_Enum):
    '''Enumeration of the video color primaries.
    '''
    _enum_names_ = {
        1: 'primaries_BT601_525',
        2: 'primaries_BT601_625',
        3: 'primaries_BT709',
        4: 'primaries_BT2020',
        5: 'primaries_DCI_P3',
        6: 'primaries_BT470_M',
    }
VideoColorPrimaries.primaries_BT2020    = VideoColorPrimaries(4)
VideoColorPrimaries.primaries_BT470_M   = VideoColorPrimaries(6)
VideoColorPrimaries.primaries_BT601_525 = VideoColorPrimaries(1)
VideoColorPrimaries.primaries_BT601_625 = VideoColorPrimaries(2)
VideoColorPrimaries.primaries_BT709     = VideoColorPrimaries(3)
VideoColorPrimaries.primaries_DCI_P3    = VideoColorPrimaries(5)

class VideoColorSpace(_Enum):
    '''Enumeration of the video color spaces.
    '''
    _enum_names_ = {
        1: 'space_BT601',
        2: 'space_BT709',
        3: 'space_BT2020',
    }
VideoColorSpace.space_BT2020 = VideoColorSpace(3)
VideoColorSpace.space_BT601  = VideoColorSpace(1)
VideoColorSpace.space_BT709  = VideoColorSpace(2)

class VideoTransferFunc(_Enum):
    '''Enumeration of the video transfer functions.
    '''
    _enum_names_ = {
        1: 'LINEAR',
        2: 'SRGB',
        3: 'BT470_BG',
        4: 'BT470_M',
        5: 'BT709',
        6: 'PQ',
        7: 'SMPTE_240',
        8: 'HLG',
    }
VideoTransferFunc.BT470_BG  = VideoTransferFunc(3)
VideoTransferFunc.BT470_M   = VideoTransferFunc(4)
VideoTransferFunc.BT709     = VideoTransferFunc(5)
VideoTransferFunc.HLG       = VideoTransferFunc(8)
VideoTransferFunc.LINEAR    = VideoTransferFunc(1)
VideoTransferFunc.PQ        = VideoTransferFunc(6)
VideoTransferFunc.SMPTE_240 = VideoTransferFunc(7)
VideoTransferFunc.SRGB      = VideoTransferFunc(2)

class VideoMetadataType(_Enum):
    '''Callback prototype to load opengl functions
\param[in] opaque private pointer set on the opaque parameter of @a libvlc_video_output_setup_cb()
\param fct_name name of the opengl function to load
\return a pointer to the named opengl function the null otherwise
\version libvlc 4.0.0 or later.
    '''
    _enum_names_ = {
        0: 'frame_hdr10',
    }
VideoMetadataType.frame_hdr10 = VideoMetadataType(0)

class VideoEngine(_Enum):
    '''Enumeration of the video engine to be used on output.
can be passed to @a libvlc_video_set_output_callbacks.
    '''
    _enum_names_ = {
        0: 'disable',
        1: 'opengl',
        2: 'gles2',
        3: 'd3d11',
        4: 'd3d9',
    }
VideoEngine.d3d11   = VideoEngine(3)
VideoEngine.d3d9    = VideoEngine(4)
VideoEngine.disable = VideoEngine(0)
VideoEngine.gles2   = VideoEngine(2)
VideoEngine.opengl  = VideoEngine(1)

class VideoLogoOption(_Enum):
    '''Option values for libvlc_video_{get,set}_logo_{int,string}.
    '''
    _enum_names_ = {
        0: 'logo_enable',
        1: 'logo_file',
        2: 'logo_x',
        3: 'logo_y',
        4: 'logo_delay',
        5: 'logo_repeat',
        6: 'logo_opacity',
        7: 'logo_position',
    }
VideoLogoOption.logo_delay    = VideoLogoOption(4)
VideoLogoOption.logo_enable   = VideoLogoOption(0)
VideoLogoOption.logo_file     = VideoLogoOption(1)
VideoLogoOption.logo_opacity  = VideoLogoOption(6)
VideoLogoOption.logo_position = VideoLogoOption(7)
VideoLogoOption.logo_repeat   = VideoLogoOption(5)
VideoLogoOption.logo_x        = VideoLogoOption(2)
VideoLogoOption.logo_y        = VideoLogoOption(3)

class VideoAdjustOption(_Enum):
    '''Option values for libvlc_video_{get,set}_adjust_{int,float,bool}.
    '''
    _enum_names_ = {
        0: 'Enable',
        1: 'Contrast',
        2: 'Brightness',
        3: 'Hue',
        4: 'Saturation',
        5: 'Gamma',
    }
VideoAdjustOption.Brightness = VideoAdjustOption(2)
VideoAdjustOption.Contrast   = VideoAdjustOption(1)
VideoAdjustOption.Enable     = VideoAdjustOption(0)
VideoAdjustOption.Gamma      = VideoAdjustOption(5)
VideoAdjustOption.Hue        = VideoAdjustOption(3)
VideoAdjustOption.Saturation = VideoAdjustOption(4)

class AudioOutputStereomode(_Enum):
    '''Audio stereo modes.
    '''
    _enum_names_ = {
        0: 'AudioStereoMode_Unset',
        1: 'AudioStereoMode_Stereo',
        2: 'AudioStereoMode_RStereo',
        3: 'AudioStereoMode_Left',
        4: 'AudioStereoMode_Right',
        5: 'AudioStereoMode_Dolbys',
        7: 'AudioStereoMode_Mono',
    }
AudioOutputStereomode.AudioStereoMode_Dolbys  = AudioOutputStereomode(5)
AudioOutputStereomode.AudioStereoMode_Left    = AudioOutputStereomode(3)
AudioOutputStereomode.AudioStereoMode_Mono    = AudioOutputStereomode(7)
AudioOutputStereomode.AudioStereoMode_RStereo = AudioOutputStereomode(2)
AudioOutputStereomode.AudioStereoMode_Right   = AudioOutputStereomode(4)
AudioOutputStereomode.AudioStereoMode_Stereo  = AudioOutputStereomode(1)
AudioOutputStereomode.AudioStereoMode_Unset   = AudioOutputStereomode(0)

class AudioOutputMixmode(_Enum):
    '''Audio mix modes.
    '''
    _enum_names_ = {
        0: 'AudioMixMode_Unset',
        1: 'AudioMixMode_Stereo',
        2: 'AudioMixMode_Binaural',
        3: 'AudioMixMode_4_0',
        4: 'AudioMixMode_5_1',
        5: 'AudioMixMode_7_1',
    }
AudioOutputMixmode.AudioMixMode_4_0      = AudioOutputMixmode(3)
AudioOutputMixmode.AudioMixMode_5_1      = AudioOutputMixmode(4)
AudioOutputMixmode.AudioMixMode_7_1      = AudioOutputMixmode(5)
AudioOutputMixmode.AudioMixMode_Binaural = AudioOutputMixmode(2)
AudioOutputMixmode.AudioMixMode_Stereo   = AudioOutputMixmode(1)
AudioOutputMixmode.AudioMixMode_Unset    = AudioOutputMixmode(0)

class MediaPlayerRole(_Enum):
    '''Media player roles.
\version libvlc 3.0.0 and later.
see \ref libvlc_media_player_set_role().
    '''
    _enum_names_ = {
        0: '_None',
        1: 'Music',
        2: 'Video',
        3: 'Communication',
        4: 'Game',
        5: 'Notification',
        6: 'Animation',
        7: 'Production',
        8: 'Accessibility',
        9: 'Test',
    }
MediaPlayerRole.Accessibility = MediaPlayerRole(8)
MediaPlayerRole.Animation     = MediaPlayerRole(6)
MediaPlayerRole.Communication = MediaPlayerRole(3)
MediaPlayerRole.Game          = MediaPlayerRole(4)
MediaPlayerRole.Music         = MediaPlayerRole(1)
MediaPlayerRole.Notification  = MediaPlayerRole(5)
MediaPlayerRole.Production    = MediaPlayerRole(7)
MediaPlayerRole.Test          = MediaPlayerRole(9)
MediaPlayerRole.Video         = MediaPlayerRole(2)
MediaPlayerRole._None         = MediaPlayerRole(0)

class TrackType(_Enum):
    '''\defgroup libvlc_media_track libvlc media track
\ingroup libvlc
@ref libvlc_media_track_t is an abstract representation of a media track.
@{
\file
libvlc media track.
    '''
    _enum_names_ = {
        -1: 'unknown',
        0: 'audio',
        1: 'video',
        2: 'ext',
    }
TrackType.audio   = TrackType(0)
TrackType.ext     = TrackType(2)
TrackType.unknown = TrackType(-1)
TrackType.video   = TrackType(1)

class VideoOrient(_Enum):
    '''N/A
    '''
    _enum_names_ = {
        0: 'top_left',
        1: 'top_right',
        2: 'bottom_left',
        3: 'bottom_right',
        4: 'left_top',
        5: 'left_bottom',
        6: 'right_top',
        7: 'right_bottom',
    }
VideoOrient.bottom_left  = VideoOrient(2)
VideoOrient.bottom_right = VideoOrient(3)
VideoOrient.left_bottom  = VideoOrient(5)
VideoOrient.left_top     = VideoOrient(4)
VideoOrient.right_bottom = VideoOrient(7)
VideoOrient.right_top    = VideoOrient(6)
VideoOrient.top_left     = VideoOrient(0)
VideoOrient.top_right    = VideoOrient(1)

class VideoProjection(_Enum):
    '''N/A
    '''
    _enum_names_ = {
        0: 'rectangular',
        1: 'equirectangular',
        0x100: 'cubemap_layout_standard',
    }
VideoProjection.cubemap_layout_standard = VideoProjection(0x100)
VideoProjection.equirectangular         = VideoProjection(1)
VideoProjection.rectangular             = VideoProjection(0)

class VideoMultiview(_Enum):
    '''Viewpoint
\warning allocate using libvlc_video_new_viewpoint().
    '''
    _enum_names_ = {
        0: '_2d',
        1: 'stereo_sbs',
        2: 'stereo_tb',
        3: 'stereo_row',
        4: 'stereo_col',
        5: 'stereo_frame',
        6: 'stereo_checkerboard',
    }
VideoMultiview._2d                 = VideoMultiview(0)
VideoMultiview.stereo_checkerboard = VideoMultiview(6)
VideoMultiview.stereo_col          = VideoMultiview(4)
VideoMultiview.stereo_frame        = VideoMultiview(5)
VideoMultiview.stereo_row          = VideoMultiview(3)
VideoMultiview.stereo_sbs          = VideoMultiview(1)
VideoMultiview.stereo_tb           = VideoMultiview(2)

class PictureType(_Enum):
    '''N/A
    '''
    _enum_names_ = {
        0: 'Argb',
        1: 'Png',
        2: 'Jpg',
    }
PictureType.Argb = PictureType(0)
PictureType.Jpg  = PictureType(2)
PictureType.Png  = PictureType(1)

# End of generated enum types #

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
    ]

# Generated structs #
class TrackDescription(ctypes.Structure):
    '''Description for video, audio tracks and subtitles. it contains
id, name (description string) and pointer to next record.
    '''
    pass
TrackDescription._fields_ = (
        ('i_id', ctypes.c_int),
        ('psz_name', ctypes.c_char_p),
        ('p_next', ctypes.POINTER(TrackDescription)),
    )

class ModuleDescription(ctypes.Structure):
    '''Description of a module.
    '''
    pass
ModuleDescription._fields_ = (
        ('psz_name', ctypes.c_char_p),
        ('psz_shortname', ctypes.c_char_p),
        ('psz_longname', ctypes.c_char_p),
        ('psz_help', ctypes.c_char_p),
        ('p_next', ctypes.POINTER(ModuleDescription)),
    )

class DialogCbs(ctypes.Structure):
    '''Dialog callbacks to be implemented
@attention starting with vlc 4.0.0 the error callback (pf_display_error) is
           no longer part of this struct and need to be registered separately
           using @a libvlc_dialog_set_error_callback
See libvlc_dialog_set_error_callback.
    '''
    pass
DialogCbs._fields_ = (
    )

class Event(ctypes.Structure):
    '''A libvlc event.
    '''
    pass
    _fields_ = [
        ('type',   EventType      ),
        ('object', ctypes.c_void_p),
        ('u',      EventUnion     ),
    ]



class MediaStats(ctypes.Structure):
    '''Libvlc media or media_player state.
    '''
    pass
MediaStats._fields_ = (
        ('i_read_bytes', ctypes.c_int),
        ('f_input_bitrate', ctypes.c_float),
        ('i_demux_read_bytes', ctypes.c_int),
        ('f_demux_bitrate', ctypes.c_float),
        ('i_demux_corrupted', ctypes.c_int),
        ('i_demux_discontinuity', ctypes.c_int),
        ('i_decoded_video', ctypes.c_int),
        ('i_decoded_audio', ctypes.c_int),
        ('i_displayed_pictures', ctypes.c_int),
        ('i_late_pictures', ctypes.c_int),
        ('i_lost_pictures', ctypes.c_int),
        ('i_played_abuffers', ctypes.c_int),
        ('i_lost_abuffers', ctypes.c_int),
    )

class MediaSlave(ctypes.Structure):
    '''A slave of a libvlc_media_t
See libvlc_media_slaves_get.
    '''
    pass
MediaSlave._fields_ = (
        ('psz_uri', ctypes.c_char_p),
        ('i_type', MediaSlaveType),
        ('i_priority', ctypes.c_uint),
    )

class MediaDiscovererDescription(ctypes.Structure):
    '''Media discoverer description
See libvlc_media_discoverer_list_get().
    '''
    pass
MediaDiscovererDescription._fields_ = (
        ('psz_name', ctypes.c_char_p),
        ('psz_longname', ctypes.c_char_p),
        ('i_cat', MediaDiscovererCategory),
    )

class TitleDescription(ctypes.Structure):
    '''Description for titles.
    '''
    pass
TitleDescription._fields_ = (
        ('i_duration', ctypes.c_int64),
        ('psz_name', ctypes.c_char_p),
        ('i_flags', ctypes.c_uint),
    )

class ChapterDescription(ctypes.Structure):
    '''Description for chapters.
    '''
    pass
ChapterDescription._fields_ = (
        ('i_time_offset', ctypes.c_int64),
        ('i_duration', ctypes.c_int64),
        ('psz_name', ctypes.c_char_p),
    )

class AudioOutput(ctypes.Structure):
    '''Description for audio output. it contains
name, description and pointer to next record.
    '''
    pass
AudioOutput._fields_ = (
        ('psz_name', ctypes.c_char_p),
        ('psz_description', ctypes.c_char_p),
        ('p_next', ctypes.POINTER(AudioOutput)),
    )

class AudioOutputDevice(ctypes.Structure):
    '''Description for audio output device.
    '''
    pass
AudioOutputDevice._fields_ = (
        ('p_next', ctypes.POINTER(AudioOutputDevice)),
        ('psz_device', ctypes.c_char_p),
        ('psz_description', ctypes.c_char_p),
    )

class VideoSetupDeviceCfg(ctypes.Structure):
    '''Set decoded video chroma and dimensions. this only works in combination with
libvlc_video_set_callbacks().
\param mp the media player
\param setup callback to select the video format (cannot be null)
\param cleanup callback to release any allocated resources (or null)
\version libvlc 2.0.0 or later.
    '''
    pass
VideoSetupDeviceCfg._fields_ = (
        ('hardware_decoding', ctypes.c_bool),
    )

class VideoSetupDeviceInfo(ctypes.Structure):
    '''N/A
    '''
    pass
VideoSetupDeviceInfo._fields_ = (
        ('device_context', ctypes.c_void_p),
        ('context_mutex', ctypes.c_void_p),
    )

class VideoRenderCfg(ctypes.Structure):
    '''Callback prototype called to release user data
\param[in] opaque private pointer set on the opaque parameter of @a libvlc_video_output_setup_cb()
\version libvlc 4.0.0 or later.
    '''
    pass
VideoRenderCfg._fields_ = (
        ('width', ctypes.c_uint),
        ('height', ctypes.c_uint),
        ('bitdepth', ctypes.c_uint),
        ('full_range', ctypes.c_bool),
        ('colorspace', VideoColorSpace),
        ('primaries', VideoColorPrimaries),
        ('transfer', VideoTransferFunc),
        ('device', ctypes.c_void_p),
    )

class VideoOutputCfg(ctypes.Structure):
    '''N/A
    '''
    pass
VideoOutputCfg._fields_ = (
        ('dxgi_format', ctypes.c_int),
        ('d3d9_format', ctypes.c_uint32),
        ('opengl_format', ctypes.c_int),
        ('p_surface', ctypes.c_void_p),
    )

class VideoFrameHdr10Metadata(ctypes.Structure):
    '''Callback prototype to load opengl functions
\param[in] opaque private pointer set on the opaque parameter of @a libvlc_video_output_setup_cb()
\param fct_name name of the opengl function to load
\return a pointer to the named opengl function the null otherwise
\version libvlc 4.0.0 or later.
    '''
    pass
VideoFrameHdr10Metadata._fields_ = (
        ('RedPrimary[2]', ctypes.c_uint16),
        ('GreenPrimary[2]', ctypes.c_uint16),
        ('BluePrimary[2]', ctypes.c_uint16),
        ('WhitePoint[2]', ctypes.c_uint16),
        ('MaxMasteringLuminance', ctypes.c_uint),
        ('MinMasteringLuminance', ctypes.c_uint),
        ('MaxContentLightLevel', ctypes.c_uint16),
        ('MaxFrameAverageLightLevel', ctypes.c_uint16),
    )

class PlayerProgram(ctypes.Structure):
    '''Add a slave to the current media player.
\note if the player is playing, the slave will be added directly. this call
will also update the slave list of the attached libvlc_media_t.
\version libvlc 3.0.0 and later.
See libvlc_media_slaves_add
\param p_mi the media player
\param i_type subtitle or audio
\param psz_uri uri of the slave (should contain a valid scheme).
\param b_select true if this slave should be selected when it's loaded
\return 0 on success, -1 on error.
    '''
    pass
PlayerProgram._fields_ = (
        ('i_group_id', ctypes.c_int),
        ('psz_name', ctypes.c_char_p),
        ('b_selected', ctypes.c_bool),
        ('b_scrambled', ctypes.c_bool),
    )

class MediaPlayerTimePoint(ctypes.Structure):
    '''Media player timer point
\note ts and system_date values should not be used directly by the user.
libvlc_media_player_time_point_interpolate() will read these values and
return an interpolated ts.
See libvlc_media_player_watch_time_on_update.
    '''
    pass
MediaPlayerTimePoint._fields_ = (
        ('position', ctypes.c_double),
        ('rate', ctypes.c_double),
        ('ts_us', ctypes.c_int64),
        ('length_us', ctypes.c_int64),
        ('system_date_us', ctypes.c_int64),
    )

class AudioTrack(ctypes.Structure):
    '''\defgroup libvlc_media_track libvlc media track
\ingroup libvlc
@ref libvlc_media_track_t is an abstract representation of a media track.
@{
\file
libvlc media track.
    '''
    pass
AudioTrack._fields_ = (
        ('i_channels', ctypes.c_uint),
        ('i_rate', ctypes.c_uint),
    )

class VideoViewpoint(ctypes.Structure):
    '''Viewpoint
\warning allocate using libvlc_video_new_viewpoint().
    '''
    pass
VideoViewpoint._fields_ = (
        ('f_yaw', ctypes.c_float),
        ('f_pitch', ctypes.c_float),
        ('f_roll', ctypes.c_float),
        ('f_field_of_view', ctypes.c_float),
    )

class VideoTrack(ctypes.Structure):
    '''N/A
    '''
    pass
VideoTrack._fields_ = (
        ('i_height', ctypes.c_uint),
        ('i_width', ctypes.c_uint),
        ('i_sar_num', ctypes.c_uint),
        ('i_sar_den', ctypes.c_uint),
        ('i_frame_rate_num', ctypes.c_uint),
        ('i_frame_rate_den', ctypes.c_uint),
        ('i_orientation', VideoOrient),
        ('i_projection', VideoProjection),
        ('pose', VideoViewpoint),
        ('i_multiview', VideoMultiview),
    )

class SubtitleTrack(ctypes.Structure):
    '''N/A
    '''
    pass
SubtitleTrack._fields_ = (
        ('psz_encoding', ctypes.c_char_p),
    )

class MediaTrack(ctypes.Structure):
    '''N/A
    '''
    pass
MediaTrack._fields_ = (
        ('i_codec', ctypes.c_uint32),
        ('i_original_fourcc', ctypes.c_uint32),
        ('i_id', ctypes.c_int),
        ('i_type', TrackType),
        ('i_profile', ctypes.c_int),
        ('i_level', ctypes.c_int),
        ('audio', ctypes.POINTER(AudioTrack)),
        ('video', ctypes.POINTER(VideoTrack)),
        ('subtitle', ctypes.POINTER(SubtitleTrack)),
    )

class RdDescription(ctypes.Structure):
    '''Renderer discoverer description
See libvlc_renderer_discoverer_list_get().
    '''
    pass
RdDescription._fields_ = (
        ('psz_name', ctypes.c_char_p),
        ('psz_longname', ctypes.c_char_p),
    )

# End of generated structs #

# Generated callback definitions #
class Callback(ctypes.c_void_p):
    """Callback function notification.
    @param p_event: the event triggering the callback.
    """
    pass
class LogCb(ctypes.c_void_p):
    """Callback prototype for LibVLC log message handler.
    @param data: data pointer as given to L{libvlc_log_set}().
    @param level: message level (@ref L{LogLevel}).
    @param ctx: message context (meta-information about the message).
    @param fmt: printf() format string (as defined by ISO C11).
    @param args: variable argument list for the format @note Log message handlers B{must} be thread-safe. @warning The message context pointer, the format string parameters and the variable arguments are only valid until the callback returns.
    """
    pass
class DialogErrorCbs(ctypes.c_void_p):
    """Called when an error message needs to be displayed.
    @param p_data: opaque pointer for the callback.
    @param psz_title: title of the dialog.
    @param psz_text: text of the dialog.
    """
    pass
class MediaOpenCb(ctypes.c_void_p):
    """Callback prototype to open a custom bitstream input media.
    The same media item can be opened multiple times. Each time, this callback
    is invoked. It should allocate and initialize any instance-specific
    resources, then store them in *datap. The instance resources can be freed
    in the @ref L{MediaCloseCb} callback.
    @param opaque: private pointer as passed to L{libvlc_media_new_callbacks}().
    @return: datap storage space for a private data pointer, sizep byte length of the bitstream or UINT64_MAX if unknown.
    """
    pass
class MediaReadCb(ctypes.c_void_p):
    """Callback prototype to read data from a custom bitstream input media.
    @param opaque: private pointer as set by the @ref L{MediaOpenCb} callback.
    @param buf: start address of the buffer to read data into.
    @param len: bytes length of the buffer.
    @return: strictly positive number of bytes read, 0 on end-of-stream, or -1 on non-recoverable error @note If no data is immediately available, then the callback should sleep. @warning The application is responsible for avoiding deadlock situations.
    """
    pass
class MediaSeekCb(ctypes.c_void_p):
    """Callback prototype to seek a custom bitstream input media.
    @param opaque: private pointer as set by the @ref L{MediaOpenCb} callback.
    @param offset: absolute byte offset to seek to.
    @return: 0 on success, -1 on error.
    """
    pass
class MediaCloseCb(ctypes.c_void_p):
    """Callback prototype to close a custom bitstream input media.
    @param opaque: private pointer as set by the @ref L{MediaOpenCb} callback.
    """
    pass
class VideoLockCb(ctypes.c_void_p):
    """Callback prototype to allocate and lock a picture buffer.
    Whenever a new video frame needs to be decoded, the lock callback is
    invoked. Depending on the video chroma, one or three pixel planes of
    adequate dimensions must be returned via the second parameter. Those
    planes must be aligned on 32-bytes boundaries.
    @param[in] opaque private pointer as passed to L{libvlc_video_set_callbacks}().
    @param[out] planes start address of the pixel planes (LibVLC allocates the array of void pointers, this callback must initialize the array).
    @return: a private pointer for the display and unlock callbacks to identify the picture buffers.
    """
    pass
class VideoUnlockCb(ctypes.c_void_p):
    """Callback prototype to unlock a picture buffer.
    When the video frame decoding is complete, the unlock callback is invoked.
    This callback might not be needed at all. It is only an indication that the
    application can now read the pixel values if it needs to.
    @note: A picture buffer is unlocked after the picture is decoded,
    but before the picture is displayed.
    @param[in] opaque private pointer as passed to L{libvlc_video_set_callbacks}().
    @param[in] picture private pointer returned from the @ref L{VideoLockCb} callback.
    @param[in] planes pixel planes as defined by the @ref L{VideoLockCb} callback (this parameter is only for convenience).
    """
    pass
class VideoDisplayCb(ctypes.c_void_p):
    """Callback prototype to display a picture.
    When the video frame needs to be shown, as determined by the media playback
    clock, the display callback is invoked.
    @param[in] opaque private pointer as passed to L{libvlc_video_set_callbacks}().
    @param[in] picture private pointer returned from the @ref L{VideoLockCb} callback.
    """
    pass
class VideoFormatCb(ctypes.c_void_p):
    """Callback prototype to configure picture buffers format.
    This callback gets the format of the video as output by the video decoder
    and the chain of video filters (if any). It can opt to change any parameter
    as it needs. In that case, LibVLC will attempt to convert the video format
    (rescaling and chroma conversion) but these operations can be CPU intensive.
    @param[in,out] opaque pointer to the private pointer passed to L{libvlc_video_set_callbacks}().
    @param[in,out] chroma pointer to the 4 bytes video format identifier.
    @param[in,out] width pointer to the buffer width in pixels.
    @param[in,out] height pointer to the buffer height in pixels.
    @param[out] pitches table of scanline pitches in bytes for each pixel plane (the table is allocated by LibVLC).
    @param[out] lines table of scanlines count for each plane.
    @param[in] (width+1) - pointer to display width in pixels.
    @param[in] (height+1) - pointer to display height in pixels @note For each pixels plane, the scanline pitch must be bigger than or equal to the number of bytes per pixel multiplied by the pixel width. Similarly, the number of scanlines must be bigger than of equal to the pixel height. Furthermore, we recommend that pitches and lines be multiple of 32 to not break assumptions that might be held by optimized code in the video decoders, video filters and/or video converters.
    @return: the number of picture buffers allocated, 0 indicates failure.
    @version: LibVLC 4.0.0 and later.
    """
    pass
class VideoCleanupCb(ctypes.c_void_p):
    """Callback prototype to configure picture buffers format.
    @param[in] opaque private pointer as passed to L{libvlc_video_set_format_callbacks}() (and possibly modified by @ref L{VideoFormatCb}).
    """
    pass
class VideoOutputSetupCb(ctypes.c_void_p):
    """Callback prototype called to initialize user data.
    Setup the rendering environment.
    @param[in,out] opaque private pointer passed to the @a libvlc_video_set_output_callbacks() on input. The callback can change this value on output to be passed to all the other callbacks set on @a libvlc_video_set_output_callbacks().
    @param[in] cfg requested configuration of the video device.
    @param[out] out L{VideoSetupDeviceInfo}* to fill.
    @return: true on success.
    @version: LibVLC 4.0.0 or later For \ref libvlc_video_engine_d3d9 the output must be a IDirect3D9*. A reference to this object is held until the \ref L{VideoOutputCleanupCb} is called. the device must be created with D3DPRESENT_PARAMETERS.hDeviceWindow set to 0. For \ref libvlc_video_engine_d3d11 the output must be a ID3D11DeviceContext*. A reference to this object is held until the \ref L{VideoOutputCleanupCb} is called. The ID3D11Device used to create ID3D11DeviceContext must have multithreading enabled. If the ID3D11DeviceContext is used outside of the callbacks called by libvlc, the host MUST use a mutex to protect the access to the ID3D11DeviceContext of libvlc. This mutex value is set on d3d11.context_mutex. If the ID3D11DeviceContext is not used outside of the callbacks, the mutex d3d11.context_mutex may be None.
    """
    pass
class VideoOutputCleanupCb(ctypes.c_void_p):
    """Callback prototype called to release user data.
    @param[in] opaque private pointer set on the opaque parameter of @a L{VideoOutputSetupCb}().
    @version: LibVLC 4.0.0 or later.
    """
    pass
class VideoUpdateOutputCb(ctypes.c_void_p):
    """Callback prototype called on video size changes.
    Update the rendering output setup.
    @param[in] opaque private pointer set on the opaque parameter of @a L{VideoOutputSetupCb}().
    @param[in] cfg configuration of the video that will be rendered.
    @param[out] output configuration describing with how the rendering is setup.
    @version: LibVLC 4.0.0 or later @note the configuration device for Direct3D9 is the IDirect3DDevice9 that VLC uses to render. The host must set a Render target and call Present() when it needs the drawing from VLC to be done. This object is not valid anymore after Cleanup is called. Tone mapping, range and color conversion will be done depending on the values set in the output structure.
    """
    pass
class VideoSwapCb(ctypes.c_void_p):
    """Callback prototype called after performing drawing calls.
    This callback is called outside of libvlc_video_makeCurrent_cb current/not-current
    calls.
    @param[in] opaque private pointer set on the opaque parameter of @a L{VideoOutputSetupCb}().
    @version: LibVLC 4.0.0 or later.
    """
    pass
class VideoMakecurrentCb(ctypes.c_void_p):
    """Callback prototype to set up the OpenGL context for rendering.
    Tell the host the rendering is about to start/has finished.
    @param[in] opaque private pointer set on the opaque parameter of @a L{VideoOutputSetupCb}().
    @param[in] enter true to set the context as current, false to unset it.
    @return: true on success.
    @version: LibVLC 4.0.0 or later On Direct3D11 the following may change on the provided ID3D11DeviceContext* between \p enter being true and \p enter being false: - IASetPrimitiveTopology() - IASetInputLayout() - IASetVertexBuffers() - IASetIndexBuffer() - VSSetConstantBuffers() - VSSetShader() - PSSetSamplers() - PSSetConstantBuffers() - PSSetShaderResources() - PSSetShader() - RSSetViewports() - DrawIndexed().
    """
    pass
class VideoGetprocaddressCb(ctypes.c_void_p):
    """Callback prototype to load opengl functions.
    @param[in] opaque private pointer set on the opaque parameter of @a L{VideoOutputSetupCb}().
    @param fct_name: name of the opengl function to load.
    @return: a pointer to the named OpenGL function the None otherwise.
    @version: LibVLC 4.0.0 or later.
    """
    pass
class VideoFramemetadataCb(ctypes.c_void_p):
    """Callback prototype to receive metadata before rendering.
    @param[in] opaque private pointer passed to the @a libvlc_video_set_output_callbacks().
    @param[in] type type of data passed in metadata.
    @param[in] metadata the type of metadata.
    @version: LibVLC 4.0.0 or later.
    """
    pass
class VideoOutputResizeCb(ctypes.c_void_p):
    """Callback type that can be called to request a render size changes.
    
    libvlc will provide a callback of this type when calling \ref libvlc_video_output_set_resize_cb.
    
    @param report_opaque: parameter passed to \ref libvlc_video_output_set_resize_cb. [IN].
    @param width: new rendering width requested. [IN].
    @param height: new rendering height requested. [IN].
    """
    pass
class VideoOutputSelectPlaneCb(ctypes.c_void_p):
    """Tell the host the rendering for the given plane is about to start.
    @param[in] opaque private pointer set on the opaque parameter of @a L{VideoOutputSetupCb}().
    @param plane: number of the rendering plane to select.
    @param output: handle of the rendering output for the given plane.
    @return: true on success.
    @version: LibVLC 4.0.0 or later @note This is only used with \ref libvlc_video_engine_d3d11. The output parameter receives the ID3D11RenderTargetView* to use for rendering the plane. If this callback is not used (set to None in @a libvlc_video_set_output_callbacks()) OMSetRenderTargets has to be set during the @a libvlc_video_makeCurrent_cb() entering call. The number of planes depend on the DXGI_FORMAT returned during the @a L{VideoUpdateOutputCb}() call. It's usually one plane except for semi-planar formats like DXGI_FORMAT_NV12 or DXGI_FORMAT_P010. This callback is called between libvlc_video_makeCurrent_cb current/not-current calls.
    """
    pass
class AudioPlayCb(ctypes.c_void_p):
    """Callback prototype for audio playback.
    The LibVLC media player decodes and post-processes the audio signal
    asynchronously (in an internal thread). Whenever audio samples are ready
    to be queued to the output, this callback is invoked.
    The number of samples provided per invocation may depend on the file format,
    the audio coding algorithm, the decoder plug-in, the post-processing
    filters and timing. Application must not assume a certain number of samples.
    The exact format of audio samples is determined by L{libvlc_audio_set_format}()
    or L{libvlc_audio_set_format_callbacks}() as is the channels layout.
    Note that the number of samples is per channel. For instance, if the audio
    track sampling rate is 48000 Hz, then 1200 samples represent 25 milliseconds
    of audio signal - regardless of the number of audio channels.
    @param[in] data data pointer as passed to L{libvlc_audio_set_callbacks}().
    @param[in] samples pointer to a table of audio samples to play back.
    @param count: number of audio samples to play back.
    @param pts: expected play time stamp (see libvlc_delay()).
    """
    pass
class AudioPauseCb(ctypes.c_void_p):
    """Callback prototype for audio pause.
    LibVLC invokes this callback to pause audio playback.
    @note: The pause callback is never called if the audio is already paused.
    @param[in] data data pointer as passed to L{libvlc_audio_set_callbacks}().
    @param pts: time stamp of the pause request (should be elapsed already).
    """
    pass
class AudioResumeCb(ctypes.c_void_p):
    """Callback prototype for audio resumption.
    LibVLC invokes this callback to resume audio playback after it was
    previously paused.
    @note: The resume callback is never called if the audio is not paused.
    @param[in] data data pointer as passed to L{libvlc_audio_set_callbacks}().
    @param pts: time stamp of the resumption request (should be elapsed already).
    """
    pass
class AudioFlushCb(ctypes.c_void_p):
    """Callback prototype for audio buffer flush.
    LibVLC invokes this callback if it needs to discard all pending buffers and
    stop playback as soon as possible. This typically occurs when the media is
    stopped.
    @param[in] data data pointer as passed to L{libvlc_audio_set_callbacks}().
    """
    pass
class AudioDrainCb(ctypes.c_void_p):
    """Callback prototype for audio buffer drain.
    LibVLC may invoke this callback when the decoded audio track is ending.
    There will be no further decoded samples for the track, but playback should
    nevertheless continue until all already pending buffers are rendered.
    @param[in] data data pointer as passed to L{libvlc_audio_set_callbacks}().
    """
    pass
class AudioSetVolumeCb(ctypes.c_void_p):
    """Callback prototype for audio volume change.
    @param[in] data data pointer as passed to L{libvlc_audio_set_callbacks}().
    @param volume: software volume (1. = nominal, 0. = mute).
    @param mute: muted flag.
    """
    pass
class AudioSetupCb(ctypes.c_void_p):
    """Callback prototype to setup the audio playback.
    This is called when the media player needs to create a new audio output.
    @param[in,out] opaque pointer to the data pointer passed to L{libvlc_audio_set_callbacks}().
    @param[in,out] format 4 bytes sample format.
    @param[in,out] rate sample rate.
    @param[in,out] channels channels count.
    @return: 0 on success, anything else to skip audio playback.
    """
    pass
class AudioCleanupCb(ctypes.c_void_p):
    """Callback prototype for audio playback cleanup.
    This is called when the media player no longer needs an audio output.
    @param[in] opaque data pointer as passed to L{libvlc_audio_set_callbacks}().
    """
    pass
class MediaPlayerWatchTimeOnUpdate(ctypes.c_void_p):
    """Callback prototype that notify when the player state or time changed.
    Get notified when the time is updated by the input or output source. The
    input source is the 'demux' or the 'access_demux'. The output source are
    audio and video outputs: an update is received each time a video frame is
    displayed or an audio sample is written. The delay between each updates may
    depend on the input and source type (it can be every 5ms, 30ms, 1s or
    10s...). Users of this timer may need to update the position at a higher
    frequency from their own mainloop via
    L{libvlc_media_player_time_point_interpolate}().
    @warning: It is forbidden to call any Media Player functions from here.
    @param value: always valid, the time corresponding to the state.
    @param data: opaque pointer set by L{libvlc_media_player_watch_time}().
    """
    pass
class MediaPlayerWatchTimeOnDiscontinuity(ctypes.c_void_p):
    """Callback prototype that notify when the player is paused or a discontinuity
    occurred.
    Likely caused by seek from the user or because the playback is stopped. The
    player user should stop its "interpolate" timer.
    @warning: It is forbidden to call any Media Player functions from here.
    @param system_date_us: system date, in us, of this event, only valid (> 0) when paused. It can be used to interpolate the last updated point to this date in order to get the last paused ts/position.
    @param data: opaque pointer set by L{libvlc_media_player_watch_time}().
    """
    pass
class CallbackDecorators(object):
    "Class holding various method decorators for callback functions."
    Callback = ctypes.CFUNCTYPE(None, ctypes.POINTER(Event), ctypes.c_void_p)
    Callback.__doc__ = '''Callback function notification.
        @param p_event: the event triggering the callback.
    '''
    LogCb = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_int, Log_ptr, ctypes.c_char_p, ctypes.c_void_p)
    LogCb.__doc__ = '''Callback prototype for LibVLC log message handler.
        @param data: data pointer as given to L{libvlc_log_set}().
        @param level: message level (@ref L{LogLevel}).
        @param ctx: message context (meta-information about the message).
        @param fmt: printf() format string (as defined by ISO C11).
        @param args: variable argument list for the format @note Log message handlers B{must} be thread-safe. @warning The message context pointer, the format string parameters and the variable arguments are only valid until the callback returns.
    '''
    DialogErrorCbs = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p)
    DialogErrorCbs.__doc__ = '''Called when an error message needs to be displayed.
        @param p_data: opaque pointer for the callback.
        @param psz_title: title of the dialog.
        @param psz_text: text of the dialog.
    '''
    MediaOpenCb = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(ctypes.c_uint64))
    MediaOpenCb.__doc__ = '''Callback prototype to open a custom bitstream input media.
        The same media item can be opened multiple times. Each time, this callback
        is invoked. It should allocate and initialize any instance-specific
        resources, then store them in *datap. The instance resources can be freed
        in the @ref L{MediaCloseCb} callback.
        @param opaque: private pointer as passed to L{libvlc_media_new_callbacks}().
        @return: datap storage space for a private data pointer, sizep byte length of the bitstream or UINT64_MAX if unknown.
    '''
    MediaReadCb = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(ctypes.c_char), ctypes.c_size_t)
    MediaReadCb.__doc__ = '''Callback prototype to read data from a custom bitstream input media.
        @param opaque: private pointer as set by the @ref L{MediaOpenCb} callback.
        @param buf: start address of the buffer to read data into.
        @param len: bytes length of the buffer.
        @return: strictly positive number of bytes read, 0 on end-of-stream, or -1 on non-recoverable error @note If no data is immediately available, then the callback should sleep. @warning The application is responsible for avoiding deadlock situations.
    '''
    MediaSeekCb = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_uint64)
    MediaSeekCb.__doc__ = '''Callback prototype to seek a custom bitstream input media.
        @param opaque: private pointer as set by the @ref L{MediaOpenCb} callback.
        @param offset: absolute byte offset to seek to.
        @return: 0 on success, -1 on error.
    '''
    MediaCloseCb = ctypes.CFUNCTYPE(None, ctypes.c_void_p)
    MediaCloseCb.__doc__ = '''Callback prototype to close a custom bitstream input media.
        @param opaque: private pointer as set by the @ref L{MediaOpenCb} callback.
    '''
    VideoLockCb = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p))
    VideoLockCb.__doc__ = '''Callback prototype to allocate and lock a picture buffer.
        Whenever a new video frame needs to be decoded, the lock callback is
        invoked. Depending on the video chroma, one or three pixel planes of
        adequate dimensions must be returned via the second parameter. Those
        planes must be aligned on 32-bytes boundaries.
        @param[in] opaque private pointer as passed to L{libvlc_video_set_callbacks}().
        @param[out] planes start address of the pixel planes (LibVLC allocates the array of void pointers, this callback must initialize the array).
        @return: a private pointer for the display and unlock callbacks to identify the picture buffers.
    '''
    VideoUnlockCb = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p))
    VideoUnlockCb.__doc__ = '''Callback prototype to unlock a picture buffer.
        When the video frame decoding is complete, the unlock callback is invoked.
        This callback might not be needed at all. It is only an indication that the
        application can now read the pixel values if it needs to.
        @note: A picture buffer is unlocked after the picture is decoded,
        but before the picture is displayed.
        @param[in] opaque private pointer as passed to L{libvlc_video_set_callbacks}().
        @param[in] picture private pointer returned from the @ref L{VideoLockCb} callback.
        @param[in] planes pixel planes as defined by the @ref L{VideoLockCb} callback (this parameter is only for convenience).
    '''
    VideoDisplayCb = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_void_p)
    VideoDisplayCb.__doc__ = '''Callback prototype to display a picture.
        When the video frame needs to be shown, as determined by the media playback
        clock, the display callback is invoked.
        @param[in] opaque private pointer as passed to L{libvlc_video_set_callbacks}().
        @param[in] picture private pointer returned from the @ref L{VideoLockCb} callback.
    '''
    VideoFormatCb = ctypes.CFUNCTYPE(ctypes.c_uint, ctypes.POINTER(ctypes.c_void_p), ctypes.c_char_p, ctypes.POINTER(ctypes.c_uint), ctypes.POINTER(ctypes.c_uint), ctypes.POINTER(ctypes.c_uint), ctypes.POINTER(ctypes.c_uint))
    VideoFormatCb.__doc__ = '''Callback prototype to configure picture buffers format.
        This callback gets the format of the video as output by the video decoder
        and the chain of video filters (if any). It can opt to change any parameter
        as it needs. In that case, LibVLC will attempt to convert the video format
        (rescaling and chroma conversion) but these operations can be CPU intensive.
        @param[in,out] opaque pointer to the private pointer passed to L{libvlc_video_set_callbacks}().
        @param[in,out] chroma pointer to the 4 bytes video format identifier.
        @param[in,out] width pointer to the buffer width in pixels.
        @param[in,out] height pointer to the buffer height in pixels.
        @param[out] pitches table of scanline pitches in bytes for each pixel plane (the table is allocated by LibVLC).
        @param[out] lines table of scanlines count for each plane.
        @param[in] (width+1) - pointer to display width in pixels.
        @param[in] (height+1) - pointer to display height in pixels @note For each pixels plane, the scanline pitch must be bigger than or equal to the number of bytes per pixel multiplied by the pixel width. Similarly, the number of scanlines must be bigger than of equal to the pixel height. Furthermore, we recommend that pitches and lines be multiple of 32 to not break assumptions that might be held by optimized code in the video decoders, video filters and/or video converters.
        @return: the number of picture buffers allocated, 0 indicates failure.
        @version: LibVLC 4.0.0 and later.
    '''
    VideoCleanupCb = ctypes.CFUNCTYPE(None, ctypes.c_void_p)
    VideoCleanupCb.__doc__ = '''Callback prototype to configure picture buffers format.
        @param[in] opaque private pointer as passed to L{libvlc_video_set_format_callbacks}() (and possibly modified by @ref L{VideoFormatCb}).
    '''
    VideoOutputSetupCb = ctypes.CFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(VideoSetupDeviceCfg), ctypes.POINTER(VideoSetupDeviceInfo))
    VideoOutputSetupCb.__doc__ = '''Callback prototype called to initialize user data.
        Setup the rendering environment.
        @param[in,out] opaque private pointer passed to the @a libvlc_video_set_output_callbacks() on input. The callback can change this value on output to be passed to all the other callbacks set on @a libvlc_video_set_output_callbacks().
        @param[in] cfg requested configuration of the video device.
        @param[out] out L{VideoSetupDeviceInfo}* to fill.
        @return: true on success.
        @version: LibVLC 4.0.0 or later For \ref libvlc_video_engine_d3d9 the output must be a IDirect3D9*. A reference to this object is held until the \ref L{VideoOutputCleanupCb} is called. the device must be created with D3DPRESENT_PARAMETERS.hDeviceWindow set to 0. For \ref libvlc_video_engine_d3d11 the output must be a ID3D11DeviceContext*. A reference to this object is held until the \ref L{VideoOutputCleanupCb} is called. The ID3D11Device used to create ID3D11DeviceContext must have multithreading enabled. If the ID3D11DeviceContext is used outside of the callbacks called by libvlc, the host MUST use a mutex to protect the access to the ID3D11DeviceContext of libvlc. This mutex value is set on d3d11.context_mutex. If the ID3D11DeviceContext is not used outside of the callbacks, the mutex d3d11.context_mutex may be None.
    '''
    VideoOutputCleanupCb = ctypes.CFUNCTYPE(None, ctypes.c_void_p)
    VideoOutputCleanupCb.__doc__ = '''Callback prototype called to release user data.
        @param[in] opaque private pointer set on the opaque parameter of @a L{VideoOutputSetupCb}().
        @version: LibVLC 4.0.0 or later.
    '''
    VideoUpdateOutputCb = ctypes.CFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.POINTER(VideoRenderCfg), ctypes.POINTER(VideoOutputCfg))
    VideoUpdateOutputCb.__doc__ = '''Callback prototype called on video size changes.
        Update the rendering output setup.
        @param[in] opaque private pointer set on the opaque parameter of @a L{VideoOutputSetupCb}().
        @param[in] cfg configuration of the video that will be rendered.
        @param[out] output configuration describing with how the rendering is setup.
        @version: LibVLC 4.0.0 or later @note the configuration device for Direct3D9 is the IDirect3DDevice9 that VLC uses to render. The host must set a Render target and call Present() when it needs the drawing from VLC to be done. This object is not valid anymore after Cleanup is called. Tone mapping, range and color conversion will be done depending on the values set in the output structure.
    '''
    VideoSwapCb = ctypes.CFUNCTYPE(None, ctypes.c_void_p)
    VideoSwapCb.__doc__ = '''Callback prototype called after performing drawing calls.
        This callback is called outside of libvlc_video_makeCurrent_cb current/not-current
        calls.
        @param[in] opaque private pointer set on the opaque parameter of @a L{VideoOutputSetupCb}().
        @version: LibVLC 4.0.0 or later.
    '''
    VideoMakecurrentCb = ctypes.CFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_bool)
    VideoMakecurrentCb.__doc__ = '''Callback prototype to set up the OpenGL context for rendering.
        Tell the host the rendering is about to start/has finished.
        @param[in] opaque private pointer set on the opaque parameter of @a L{VideoOutputSetupCb}().
        @param[in] enter true to set the context as current, false to unset it.
        @return: true on success.
        @version: LibVLC 4.0.0 or later On Direct3D11 the following may change on the provided ID3D11DeviceContext* between \p enter being true and \p enter being false: - IASetPrimitiveTopology() - IASetInputLayout() - IASetVertexBuffers() - IASetIndexBuffer() - VSSetConstantBuffers() - VSSetShader() - PSSetSamplers() - PSSetConstantBuffers() - PSSetShaderResources() - PSSetShader() - RSSetViewports() - DrawIndexed().
    '''
    VideoGetprocaddressCb = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.c_char_p)
    VideoGetprocaddressCb.__doc__ = '''Callback prototype to load opengl functions.
        @param[in] opaque private pointer set on the opaque parameter of @a L{VideoOutputSetupCb}().
        @param fct_name: name of the opengl function to load.
        @return: a pointer to the named OpenGL function the None otherwise.
        @version: LibVLC 4.0.0 or later.
    '''
    VideoFramemetadataCb = ctypes.CFUNCTYPE(None, ctypes.c_void_p, VideoMetadataType, ctypes.c_void_p)
    VideoFramemetadataCb.__doc__ = '''Callback prototype to receive metadata before rendering.
        @param[in] opaque private pointer passed to the @a libvlc_video_set_output_callbacks().
        @param[in] type type of data passed in metadata.
        @param[in] metadata the type of metadata.
        @version: LibVLC 4.0.0 or later.
    '''
    VideoOutputResizeCb = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_uint, ctypes.c_uint)
    VideoOutputResizeCb.__doc__ = '''Callback type that can be called to request a render size changes.
        
        libvlc will provide a callback of this type when calling \ref libvlc_video_output_set_resize_cb.
        
        @param report_opaque: parameter passed to \ref libvlc_video_output_set_resize_cb. [IN].
        @param width: new rendering width requested. [IN].
        @param height: new rendering height requested. [IN].
    '''
    VideoOutputSelectPlaneCb = ctypes.CFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p)
    VideoOutputSelectPlaneCb.__doc__ = '''Tell the host the rendering for the given plane is about to start.
        @param[in] opaque private pointer set on the opaque parameter of @a L{VideoOutputSetupCb}().
        @param plane: number of the rendering plane to select.
        @param output: handle of the rendering output for the given plane.
        @return: true on success.
        @version: LibVLC 4.0.0 or later @note This is only used with \ref libvlc_video_engine_d3d11. The output parameter receives the ID3D11RenderTargetView* to use for rendering the plane. If this callback is not used (set to None in @a libvlc_video_set_output_callbacks()) OMSetRenderTargets has to be set during the @a libvlc_video_makeCurrent_cb() entering call. The number of planes depend on the DXGI_FORMAT returned during the @a L{VideoUpdateOutputCb}() call. It's usually one plane except for semi-planar formats like DXGI_FORMAT_NV12 or DXGI_FORMAT_P010. This callback is called between libvlc_video_makeCurrent_cb current/not-current calls.
    '''
    AudioPlayCb = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint, ctypes.c_int64)
    AudioPlayCb.__doc__ = '''Callback prototype for audio playback.
        The LibVLC media player decodes and post-processes the audio signal
        asynchronously (in an internal thread). Whenever audio samples are ready
        to be queued to the output, this callback is invoked.
        The number of samples provided per invocation may depend on the file format,
        the audio coding algorithm, the decoder plug-in, the post-processing
        filters and timing. Application must not assume a certain number of samples.
        The exact format of audio samples is determined by L{libvlc_audio_set_format}()
        or L{libvlc_audio_set_format_callbacks}() as is the channels layout.
        Note that the number of samples is per channel. For instance, if the audio
        track sampling rate is 48000 Hz, then 1200 samples represent 25 milliseconds
        of audio signal - regardless of the number of audio channels.
        @param[in] data data pointer as passed to L{libvlc_audio_set_callbacks}().
        @param[in] samples pointer to a table of audio samples to play back.
        @param count: number of audio samples to play back.
        @param pts: expected play time stamp (see libvlc_delay()).
    '''
    AudioPauseCb = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_int64)
    AudioPauseCb.__doc__ = '''Callback prototype for audio pause.
        LibVLC invokes this callback to pause audio playback.
        @note: The pause callback is never called if the audio is already paused.
        @param[in] data data pointer as passed to L{libvlc_audio_set_callbacks}().
        @param pts: time stamp of the pause request (should be elapsed already).
    '''
    AudioResumeCb = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_int64)
    AudioResumeCb.__doc__ = '''Callback prototype for audio resumption.
        LibVLC invokes this callback to resume audio playback after it was
        previously paused.
        @note: The resume callback is never called if the audio is not paused.
        @param[in] data data pointer as passed to L{libvlc_audio_set_callbacks}().
        @param pts: time stamp of the resumption request (should be elapsed already).
    '''
    AudioFlushCb = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_int64)
    AudioFlushCb.__doc__ = '''Callback prototype for audio buffer flush.
        LibVLC invokes this callback if it needs to discard all pending buffers and
        stop playback as soon as possible. This typically occurs when the media is
        stopped.
        @param[in] data data pointer as passed to L{libvlc_audio_set_callbacks}().
    '''
    AudioDrainCb = ctypes.CFUNCTYPE(None, ctypes.c_void_p)
    AudioDrainCb.__doc__ = '''Callback prototype for audio buffer drain.
        LibVLC may invoke this callback when the decoded audio track is ending.
        There will be no further decoded samples for the track, but playback should
        nevertheless continue until all already pending buffers are rendered.
        @param[in] data data pointer as passed to L{libvlc_audio_set_callbacks}().
    '''
    AudioSetVolumeCb = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_float, ctypes.c_bool)
    AudioSetVolumeCb.__doc__ = '''Callback prototype for audio volume change.
        @param[in] data data pointer as passed to L{libvlc_audio_set_callbacks}().
        @param volume: software volume (1. = nominal, 0. = mute).
        @param mute: muted flag.
    '''
    AudioSetupCb = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.POINTER(ctypes.c_void_p), ctypes.c_char_p, ctypes.POINTER(ctypes.c_uint), ctypes.POINTER(ctypes.c_uint))
    AudioSetupCb.__doc__ = '''Callback prototype to setup the audio playback.
        This is called when the media player needs to create a new audio output.
        @param[in,out] opaque pointer to the data pointer passed to L{libvlc_audio_set_callbacks}().
        @param[in,out] format 4 bytes sample format.
        @param[in,out] rate sample rate.
        @param[in,out] channels channels count.
        @return: 0 on success, anything else to skip audio playback.
    '''
    AudioCleanupCb = ctypes.CFUNCTYPE(None, ctypes.c_void_p)
    AudioCleanupCb.__doc__ = '''Callback prototype for audio playback cleanup.
        This is called when the media player no longer needs an audio output.
        @param[in] opaque data pointer as passed to L{libvlc_audio_set_callbacks}().
    '''
    MediaPlayerWatchTimeOnUpdate = ctypes.CFUNCTYPE(None, ctypes.POINTER(MediaPlayerTimePoint), ctypes.c_void_p)
    MediaPlayerWatchTimeOnUpdate.__doc__ = '''Callback prototype that notify when the player state or time changed.
        Get notified when the time is updated by the input or output source. The
        input source is the 'demux' or the 'access_demux'. The output source are
        audio and video outputs: an update is received each time a video frame is
        displayed or an audio sample is written. The delay between each updates may
        depend on the input and source type (it can be every 5ms, 30ms, 1s or
        10s...). Users of this timer may need to update the position at a higher
        frequency from their own mainloop via
        L{libvlc_media_player_time_point_interpolate}().
        @warning: It is forbidden to call any Media Player functions from here.
        @param value: always valid, the time corresponding to the state.
        @param data: opaque pointer set by L{libvlc_media_player_watch_time}().
    '''
    MediaPlayerWatchTimeOnDiscontinuity = ctypes.CFUNCTYPE(None, ctypes.c_int64, ctypes.c_void_p)
    MediaPlayerWatchTimeOnDiscontinuity.__doc__ = '''Callback prototype that notify when the player is paused or a discontinuity
        occurred.
        Likely caused by seek from the user or because the playback is stopped. The
        player user should stop its "interpolate" timer.
        @warning: It is forbidden to call any Media Player functions from here.
        @param system_date_us: system date, in us, of this event, only valid (> 0) when paused. It can be used to interpolate the last updated point to this date in order to get the last paused ts/position.
        @param data: opaque pointer set by L{libvlc_media_player_watch_time}().
    '''
cb = CallbackDecorators
# End of generated enum types #

# End of header.py #
class AudioEqualizer(_Ctype):
    '''Create a new default equalizer, with all frequency values zeroed.

    The new equalizer can subsequently be applied to a media player by invoking
    L{MediaPlayer.set_equalizer}.
    The returned handle should be freed via libvlc_audio_equalizer_release() when
    it is no longer needed.
    '''

    def __new__(cls, *args):
        if len(args) == 1 and isinstance(args[0], _Ints):
            return _Constructor(cls, args[0])
        return libvlc_audio_equalizer_new()



    def release(self):
        '''Release a previously created equalizer instance.
        The equalizer was previously created by using L{new}() or
        L{new_from_preset}().
        It is safe to invoke this method with a None p_equalizer parameter for no effect.
        @version: LibVLC 2.2.0 or later.
        '''
        return libvlc_audio_equalizer_release(self)


    def set_preamp(self, f_preamp):
        '''Set a new pre-amplification value for an equalizer.
        The new equalizer settings are subsequently applied to a media player by invoking
        L{media_player_set_equalizer}().
        The supplied amplification value will be clamped to the -20.0 to +20.0 range.
        @param f_preamp: preamp value (-20.0 to 20.0 Hz).
        @return: zero on success, -1 on error.
        @version: LibVLC 2.2.0 or later.
        '''
        return libvlc_audio_equalizer_set_preamp(self, f_preamp)


    def get_preamp(self):
        '''Get the current pre-amplification value from an equalizer.
        @return: preamp value (Hz).
        @version: LibVLC 2.2.0 or later.
        '''
        return libvlc_audio_equalizer_get_preamp(self)


    def set_amp_at_index(self, f_amp, u_band):
        '''Set a new amplification value for a particular equalizer frequency band.
        The new equalizer settings are subsequently applied to a media player by invoking
        L{media_player_set_equalizer}().
        The supplied amplification value will be clamped to the -20.0 to +20.0 range.
        @param f_amp: amplification value (-20.0 to 20.0 Hz).
        @param u_band: index, counting from zero, of the frequency band to set.
        @return: zero on success, -1 on error.
        @version: LibVLC 2.2.0 or later.
        '''
        return libvlc_audio_equalizer_set_amp_at_index(self, f_amp, u_band)


    def get_amp_at_index(self, u_band):
        '''Get the amplification value for a particular equalizer frequency band.
        @param u_band: index, counting from zero, of the frequency band to get.
        @return: amplification value (Hz); NaN if there is no such frequency band.
        @version: LibVLC 2.2.0 or later.
        '''
        return libvlc_audio_equalizer_get_amp_at_index(self, u_band)

class EventManager(_Ctype):
    '''Create an event manager with callback handler.

    This class interposes the registration and handling of
    event notifications in order to (a) remove the need for
    decorating each callback functions with the decorator
    '@callbackmethod', (b) allow any number of positional
    and/or keyword arguments to the callback (in addition
    to the Event instance) and (c) to preserve the Python
    objects such that the callback and argument objects
    remain alive (i.e. are not garbage collected) until
    B{after} the notification has been unregistered.

    @note: Only a single notification can be registered
    for each event type in an EventManager instance.
    
    '''

    _callback_handler = None
    _callbacks = {}

    def __new__(cls, ptr=_internal_guard):
        if ptr == _internal_guard:
            raise VLCException("(INTERNAL) ctypes class.\nYou should get a reference to EventManager through the MediaPlayer.event_manager() method.")
        return _Constructor(cls, ptr)

    def event_attach(self, eventtype, callback, *args, **kwds):
        """Register an event notification.

        @param eventtype: the desired event type to be notified about.
        @param callback: the function to call when the event occurs.
        @param args: optional positional arguments for the callback.
        @param kwds: optional keyword arguments for the callback.
        @return: 0 on success, ENOMEM on error.

        @note: The callback function must have at least one argument,
        an Event instance.  Any other, optional positional and keyword
        arguments are in B{addition} to the first one. Warning: libvlc
        is not reentrant, i.e. you cannot call libvlc functions from
        an event handler. They must be called from the main
        application thread.
        """
        if not isinstance(eventtype, EventType):
            raise VLCException("%s required: %r" % ('EventType', eventtype))
        if not hasattr(callback, '__call__'):  # callable()
            raise VLCException("%s required: %r" % ('callable', callback))
         # check that the callback expects arguments
        if len_args(callback) < 1:  # list(...)
            raise VLCException("%s required: %r" % ('argument', callback))

        if self._callback_handler is None:
            _called_from_ctypes = ctypes.CFUNCTYPE(None, ctypes.POINTER(Event), ctypes.c_void_p)
            @_called_from_ctypes
            def _callback_handler(event, k):
                """(INTERNAL) handle callback call from ctypes.

                @note: We cannot simply make this an EventManager
                method since ctypes does not prepend self as the
                first parameter, hence this closure.
                """
                try: # retrieve Python callback and arguments
                    call, args, kwds = self._callbacks[k]
                except KeyError:  # detached?
                    pass
                else:
                    # deref event.contents to simplify callback code
                    call(event.contents, *args, **kwds)
            self._callback_handler = _callback_handler
            self._callbacks = {}

        k = eventtype.value
        r = libvlc_event_attach(self, k, self._callback_handler, k)
        if not r:
            self._callbacks[k] = (callback, args, kwds)
        return r

    def event_detach(self, eventtype):
        """Unregister an event notification.

        @param eventtype: the event type notification to be removed.
        """
        if not isinstance(eventtype, EventType):
            raise VLCException("%s required: %r" % ('EventType', eventtype))

        k = eventtype.value
        if k in self._callbacks:
            del self._callbacks[k] # remove, regardless of libvlc return value
            libvlc_event_detach(self, k, self._callback_handler, k)


class Instance(_Ctype):
    '''Create a new Instance instance.

    It may take as parameter either:
      - a string
      - a list of strings as first parameters
      - the parameters given as the constructor parameters (must be strings)
    
    '''

    def __new__(cls, *args):
        if len(args) == 1:
            # Only 1 arg. It is either a C pointer, or an arg string,
            # or a tuple.
            i = args[0]
            if isinstance(i, _Ints):
                return _Constructor(cls, i)
            elif isinstance(i, basestring):
                args = i.strip().split()
            elif isinstance(i, _Seqs):
                args = list(i)
            else:
                raise VLCException('Instance %r' % (args,))
        else:
            args = list(args)

        if not args:  # no parameters passed
            args = ['vlc']
        elif args[0] != 'vlc':
            args.insert(0, 'vlc')

        if plugin_path is not None:
            # set plugin_path if detected, win32 and MacOS,
            # if the user did not specify it itself.
            os.environ.setdefault('VLC_PLUGIN_PATH', plugin_path)

        if PYTHON3:
            args = [ str_to_bytes(a) for a in args ]
        return libvlc_new(len(args), args)

    def media_player_new(self, uri=None):
        """Create a new MediaPlayer instance.

        @param uri: an optional URI to play in the player as a str, bytes or PathLike object.
        """
        p = libvlc_media_player_new(self)
        if uri:
            p.set_media(self.media_new(uri))
        p._instance = self
        return p

    def media_list_player_new(self):
        """Create a new MediaListPlayer instance.
        """
        p = libvlc_media_list_player_new(self)
        p._instance = self
        return p

    def media_new(self, mrl, *options):
        """Create a new Media instance.

        If mrl contains a colon (:) preceded by more than 1 letter, it
        will be treated as a URL. Else, it will be considered as a
        local path. If you need more control, directly use
        media_new_location/media_new_path methods.

        Options can be specified as supplementary string parameters,
        but note that many options cannot be set at the media level,
        and rather at the Instance level. For instance, the marquee
        filter must be specified when creating the vlc.Instance or
        vlc.MediaPlayer.

        Alternatively, options can be added to the media using the
        Media.add_options method (with the same limitation).

        @param mrl: A str, bytes or PathLike object
        @param options: optional media option=value strings
        """
        mrl = try_fspath(mrl)
        if ':' in mrl and mrl.index(':') > 1:
            # Assume it is a URL
            m = libvlc_media_new_location(self, str_to_bytes(mrl))
        else:
            # Else it should be a local path.
            m = libvlc_media_new_path(self, str_to_bytes(os.path.normpath(mrl)))
        for o in options:
            libvlc_media_add_option(m, str_to_bytes(o))
        m._instance = self
        return m

    def media_new_location(self, psz_mrl):
        '''Create a media with a certain given media resource location,
        for instance a valid URL.
        @note: To refer to a local file with this function,
        the file://... URI syntax B{must} be used (see IETF RFC3986).
        We recommend using L{media_new_path}() instead when dealing with
        local files.
        See L{media_release}.
        @param psz_mrl: the media location.
        @return: the newly created media or None on error.
        '''
        return libvlc_media_new_location(self, str_to_bytes(psz_mrl))

    def media_new_path(self, path):
        """Create a media for a certain file path.
        See L{media_release}.
        @param path: A str, byte, or PathLike object representing a local filesystem path.
        @return: the newly created media or None on error.
        """
        path = try_fspath(path)
        return libvlc_media_new_path(self, str_to_bytes(path))

    def media_list_new(self, mrls=None):
        """Create a new MediaList instance.
        @param mrls: optional list of MRL strings, bytes, or PathLike objects.
        """
        # API 3 vs 4: libvlc_media_list_new does not take any
        # parameter as input anymore.
        if len_args(libvlc_media_list_new) == 1:  # API <= 3
            l = libvlc_media_list_new(self)
        else:  # API >= 4
            l = libvlc_media_list_new()
        # We should take the lock, but since we did not leak the
        # reference, nobody else can access it.
        if mrls:
            for m in mrls:
                l.add_media(m)
        l._instance = self
        return l

    def audio_output_enumerate_devices(self):
        """Enumerate the defined audio output devices.

        @return: list of dicts {name:, description:, devices:}
        """
        r = []
        head = libvlc_audio_output_list_get(self)
        if head:
            i = head
            while i:
                i = i.contents
                r.append({'name': i.name, 'description': i.description})
                i = i.next
            libvlc_audio_output_list_release(head)
        return r

    def audio_filter_list_get(self):
        """Returns a list of available audio filters.

        """
        return module_description_list(libvlc_audio_filter_list_get(self))

    def video_filter_list_get(self):
        """Returns a list of available video filters.

        """
        return module_description_list(libvlc_video_filter_list_get(self))



    def playlist_play(self):
        '''Start playing (if there is any item in the playlist).
        Additional playlist item options can be specified for addition to the
        item before it is played.
        '''
        return libvlc_playlist_play(self)


    def release(self):
        '''Decrement the reference count of a libvlc instance, and destroy it
        if it reaches zero.
        '''
        return libvlc_release(self)


    def retain(self):
        '''Increments the reference count of a libvlc instance.
        The initial reference count is 1 after L{new}() returns.
        '''
        return libvlc_retain(self)


    def add_intf(self, name):
        '''Try to start a user interface for the libvlc instance.
        @param name: interface name, or None for default.
        @return: 0 on success, -1 on error.
        '''
        return libvlc_add_intf(self, str_to_bytes(name))


    def set_user_agent(self, name, http):
        '''Sets the application name. LibVLC passes this as the user agent string
        when a protocol requires it.
        @param name: human-readable application name, e.g. "FooBar player 1.2.3".
        @param http: HTTP User Agent, e.g. "FooBar/1.2.3 Python/2.6.0".
        @version: LibVLC 1.1.1 or later.
        '''
        return libvlc_set_user_agent(self, str_to_bytes(name), str_to_bytes(http))


    def set_app_id(self, id, version, icon):
        '''Sets some meta-information about the application.
        See also L{set_user_agent}().
        @param id: Java-style application identifier, e.g. "com.acme.foobar".
        @param version: application version numbers, e.g. "1.2.3".
        @param icon: application icon name, e.g. "foobar".
        @version: LibVLC 2.1.0 or later.
        '''
        return libvlc_set_app_id(self, str_to_bytes(id), str_to_bytes(version), str_to_bytes(icon))


    def log_unset(self):
        '''Unsets the logging callback.
        This function deregisters the logging callback for a LibVLC instance.
        This is rarely needed as the callback is implicitly unset when the instance
        is destroyed.
        @note: This function will wait for any pending callbacks invocation to
        complete (causing a deadlock if called from within the callback).
        @version: LibVLC 2.1.0 or later.
        '''
        return libvlc_log_unset(self)


    def log_set(self, cb, data):
        '''Sets the logging callback for a LibVLC instance.
        This function is thread-safe: it will wait for any pending callbacks
        invocation to complete.
        @param data: opaque data pointer for the callback function @note Some log messages (especially debug) are emitted by LibVLC while is being initialized. These messages cannot be captured with this interface. @warning A deadlock may occur if this function is called from the callback.
        @param p_instance: libvlc instance.
        @version: LibVLC 2.1.0 or later.
        '''
        return libvlc_log_set(self, cb, data)


    def log_set_file(self, stream):
        '''Sets up logging to a file.
        @param stream: FILE pointer opened for writing (the FILE pointer must remain valid until L{log_unset}()).
        @version: LibVLC 2.1.0 or later.
        '''
        return libvlc_log_set_file(self, stream)


    def dialog_set_error_callback(self, p_cbs, p_data):
        '''
        '''
        return libvlc_dialog_set_error_callback(self, p_cbs, p_data)


    def media_save_meta(self, p_md):
        '''Save the meta previously set.
        @param p_md: the media descriptor.
        @return: true if the write operation was successful.
        '''
        return libvlc_media_save_meta(self, p_md)


    def media_parse_request(self, p_md, parse_flag, timeout):
        '''Parse the media asynchronously with options.
        This fetches (local or network) art, meta data and/or tracks information.
        To track when this is over you can listen to libvlc_MediaParsedChanged
        event. However if this functions returns an error, you will not receive any
        events.
        It uses a flag to specify parse options (see L{MediaParseFlag}). All
        these flags can be combined. By default, media is parsed if it's a local
        file.
        @note: Parsing can be aborted with L{media_parse_stop}().
        See libvlc_MediaParsedChanged
        See L{media_get_meta}
        See L{media_get_tracklist}
        See L{media_get_parsed_status}
        See L{MediaParseFlag}.
        @param p_md: media descriptor object.
        @param parse_flag: parse options:
        @param timeout: maximum time allowed to preparse the media. If -1, the default "preparse-timeout" option will be used as a timeout. If 0, it will wait indefinitely. If > 0, the timeout will be used (in milliseconds).
        @return: -1 in case of error, 0 otherwise.
        @version: LibVLC 4.0.0 or later.
        '''
        return libvlc_media_parse_request(self, p_md, parse_flag, timeout)


    def media_parse_stop(self, p_md):
        '''Stop the parsing of the media
        When the media parsing is stopped, the libvlc_MediaParsedChanged event will
        be sent with the libvlc_media_parsed_status_timeout status.
        See L{media_parse_request}().
        @param p_md: media descriptor object.
        @version: LibVLC 3.0.0 or later.
        '''
        return libvlc_media_parse_stop(self, p_md)


    def media_thumbnail_request_by_time(self, md, time, speed, width, height, crop, picture_type, timeout):
        '''\brief libvlc_media_request_thumbnail_by_time Start an asynchronous thumbnail generation
        If the request is successfully queued, the libvlc_MediaThumbnailGenerated
        is guaranteed to be emitted.
        The resulting thumbnail size can either be:
        - Hardcoded by providing both width & height. In which case, the image will
          be stretched to match the provided aspect ratio, or cropped if crop is true.
        - Derived from the media aspect ratio if only width or height is provided and
          the other one is set to 0.
        @param md: media descriptor object.
        @param time: The time at which the thumbnail should be generated.
        @param speed: The seeking speed \saL{ThumbnailerSeekSpeed}.
        @param width: The thumbnail width.
        @param height: the thumbnail height.
        @param crop: Should the picture be cropped to preserve source aspect ratio.
        @param picture_type: The thumbnail picture type \saL{PictureType}.
        @param timeout: A timeout value in ms, or 0 to disable timeout.
        @return: A valid opaque request object, or None in case of failure. It may be cancelled by L{media_thumbnail_request_cancel}(). It must be released by L{media_thumbnail_request_destroy}().
        @version: libvlc 4.0 or later See L{Picture} See L{PictureType}.
        '''
        return libvlc_media_thumbnail_request_by_time(self, md, time, speed, width, height, crop, picture_type, timeout)


    def media_thumbnail_request_by_pos(self, md, pos, speed, width, height, crop, picture_type, timeout):
        '''\brief libvlc_media_request_thumbnail_by_pos Start an asynchronous thumbnail generation
        If the request is successfully queued, the libvlc_MediaThumbnailGenerated
        is guaranteed to be emitted.
        The resulting thumbnail size can either be:
        - Hardcoded by providing both width & height. In which case, the image will
          be stretched to match the provided aspect ratio, or cropped if crop is true.
        - Derived from the media aspect ratio if only width or height is provided and
          the other one is set to 0.
        @param md: media descriptor object.
        @param pos: The position at which the thumbnail should be generated.
        @param speed: The seeking speed \saL{ThumbnailerSeekSpeed}.
        @param width: The thumbnail width.
        @param height: the thumbnail height.
        @param crop: Should the picture be cropped to preserve source aspect ratio.
        @param picture_type: The thumbnail picture type \saL{PictureType}.
        @param timeout: A timeout value in ms, or 0 to disable timeout.
        @return: A valid opaque request object, or None in case of failure. It may be cancelled by L{media_thumbnail_request_cancel}(). It must be released by L{media_thumbnail_request_destroy}().
        @version: libvlc 4.0 or later See L{Picture} See L{PictureType}.
        '''
        return libvlc_media_thumbnail_request_by_pos(self, md, pos, speed, width, height, crop, picture_type, timeout)


    def media_discoverer_new(self, psz_name):
        '''Create a media discoverer object by name.
        After this object is created, you should attach to media_list events in
        order to be notified of new items discovered.
        You need to call L{media_discoverer_start}() in order to start the
        discovery.
        See L{media_discoverer_media_list}
        See L{media_discoverer_start}.
        @param psz_name: service name; use L{media_discoverer_list_get}() to get a list of the discoverer names available in this libVLC instance.
        @return: media discover object or None in case of error.
        @version: LibVLC 3.0.0 or later.
        '''
        return libvlc_media_discoverer_new(self, str_to_bytes(psz_name))


    def media_discoverer_list_get(self, i_cat, ppp_services):
        '''Get media discoverer services by category.
        @param i_cat: category of services to fetch.
        @param ppp_services: address to store an allocated array of media discoverer services (must be freed with L{media_discoverer_list_release}() by the caller) [OUT].
        @return: the number of media discoverer services (0 on error).
        @version: LibVLC 3.0.0 and later.
        '''
        return libvlc_media_discoverer_list_get(self, i_cat, ppp_services)


    def media_player_new_from_media(self, p_md):
        '''Create a Media Player object from a Media.
        @param p_md: the media. Afterwards the p_md can be safely destroyed.
        @return: a new media player object, or None on error. It must be released by L{media_player_release}().
        '''
        return libvlc_media_player_new_from_media(self, p_md)


    def audio_output_list_get(self):
        '''Gets the list of available audio output modules.
        @return: list of available audio outputs. It must be freed with In case of error, None is returned.
        '''
        return libvlc_audio_output_list_get(self)


    def renderer_discoverer_new(self, psz_name):
        '''Create a renderer discoverer object by name
        After this object is created, you should attach to events in order to be
        notified of the discoverer events.
        You need to call L{renderer_discoverer_start}() in order to start the
        discovery.
        See L{renderer_discoverer_event_manager}()
        See L{renderer_discoverer_start}().
        @param psz_name: service name; use L{renderer_discoverer_list_get}() to get a list of the discoverer names available in this libVLC instance.
        @return: media discover object or None in case of error.
        @version: LibVLC 3.0.0 or later.
        '''
        return libvlc_renderer_discoverer_new(self, str_to_bytes(psz_name))


    def renderer_discoverer_list_get(self, ppp_services):
        '''Get media discoverer services
        See libvlc_renderer_list_release().
        @param ppp_services: address to store an allocated array of renderer discoverer services (must be freed with libvlc_renderer_list_release() by the caller) [OUT].
        @return: the number of media discoverer services (0 on error).
        @version: LibVLC 3.0.0 and later.
        '''
        return libvlc_renderer_discoverer_list_get(self, ppp_services)

class Media(_Ctype):
    '''Create a new Media instance.

    Usage: Media(MRL, *options)

    See vlc.Instance.media_new documentation for details.
    
    '''

    def __new__(cls, *args):
        if args:
            i = args[0]
            if isinstance(i, _Ints):
                return _Constructor(cls, i)
            if isinstance(i, Instance):
                return i.media_new(*args[1:])

        o = get_default_instance().media_new(*args)
        return o

    def get_instance(self):
        return getattr(self, '_instance', None)

    def add_options(self, *options):
        """Add a list of options to the media.

        Options must be written without the double-dash. Warning: most
        audio and video options, such as text renderer, have no
        effects on an individual media. These options must be set at
        the vlc.Instance or vlc.MediaPlayer instanciation.

        @param options: optional media option=value strings
        """
        for o in options:
            self.add_option(o)

    def tracks_get(self):
        """Get media descriptor's elementary streams description
        Note, you need to call L{parse}() or play the media at least once
        before calling this function.
        Not doing this will result in an empty array.
        The result must be freed with L{tracks_release}.
        @version: LibVLC 2.1.0 and later.
        """
        mediaTrack_pp = ctypes.POINTER(MediaTrack)()
        n = libvlc_media_tracks_get(self, ctypes.byref(mediaTrack_pp))
        info = ctypes.cast(mediaTrack_pp, ctypes.POINTER(ctypes.POINTER(MediaTrack) * n))
        try:
            contents = info.contents
        except ValueError:
            # Media not parsed, no info.
            return None
        tracks = ( contents[i].contents for i in range(len(contents)) )
        # libvlc_media_tracks_release(mediaTrack_pp, n)
        return tracks



    def add_option(self, psz_options):
        '''Add an option to the media.
        This option will be used to determine how the media_player will
        read the media. This allows to use VLC's advanced
        reading/streaming options on a per-media basis.
        @note: The options are listed in 'vlc --longhelp' from the command line,
        e.g. "--sout-all". Keep in mind that available options and their semantics
        vary across LibVLC versions and builds.
        @warning: Not all options affects L{Media} objects:
        Specifically, due to architectural issues most audio and video options,
        such as text renderer options, have no effects on an individual media.
        These options must be set through L{new}() instead.
        @param psz_options: the options (as a string).
        '''
        return libvlc_media_add_option(self, str_to_bytes(psz_options))


    def add_option_flag(self, psz_options, i_flags):
        '''Add an option to the media with configurable flags.
        This option will be used to determine how the media_player will
        read the media. This allows to use VLC's advanced
        reading/streaming options on a per-media basis.
        The options are detailed in vlc --longhelp, for instance
        "--sout-all". Note that all options are not usable on medias:
        specifically, due to architectural issues, video-related options
        such as text renderer options cannot be set on a single media. They
        must be set on the whole libvlc instance instead.
        @param psz_options: the options (as a string).
        @param i_flags: the flags for this option.
        '''
        return libvlc_media_add_option_flag(self, str_to_bytes(psz_options), i_flags)


    def retain(self):
        '''Retain a reference to a media descriptor object (L{Media}). Use
        L{release}() to decrement the reference count of a
        media descriptor object.
        '''
        return libvlc_media_retain(self)


    def release(self):
        '''Decrement the reference count of a media descriptor object. If the
        reference count is 0, then L{release}() will release the
        media descriptor object. If the media descriptor object has been released it
        should not be used again.
        '''
        return libvlc_media_release(self)


    def get_mrl(self):
        '''Get the media resource locator (mrl) from a media descriptor object.
        @return: string with mrl of media descriptor object.
        '''
        return libvlc_media_get_mrl(self)


    def duplicate(self):
        '''Duplicate a media descriptor object.
        @warning: the duplicated media won't share forthcoming updates from the
        original one.
        '''
        return libvlc_media_duplicate(self)


    def get_meta(self, e_meta):
        '''Read the meta of the media.
        Note, you need to call L{parse_request}() or play the media
        at least once before calling this function.
        If the media has not yet been parsed this will return None.
        See libvlc_MediaMetaChanged.
        @param e_meta: the meta to read.
        @return: the media's meta.
        '''
        return libvlc_media_get_meta(self, e_meta)


    def set_meta(self, e_meta, psz_value):
        '''Set the meta of the media (this function will not save the meta, call
        L{save_meta} in order to save the meta).
        @param e_meta: the meta to write.
        @param psz_value: the media's meta.
        '''
        return libvlc_media_set_meta(self, e_meta, str_to_bytes(psz_value))


    def get_stats(self, p_stats):
        '''Get the current statistics about the media.
        @param p_stats: structure that contain the statistics about the media (this structure must be allocated by the caller) \retval true statistics are available \retval false otherwise.
        '''
        return libvlc_media_get_stats(self, p_stats)


    def subitems(self):
        '''Get subitems of media descriptor object. This will increment
        the reference count of supplied media descriptor object. Use
        L{list_release}() to decrement the reference counting.
        @return: list of media descriptor subitems or None.
        '''
        return libvlc_media_subitems(self)

    @memoize_parameterless
    def event_manager(self):
        '''Get event manager from media descriptor object.
        NOTE: this function doesn't increment reference counting.
        @return: event manager object.
        '''
        return libvlc_media_event_manager(self)


    def get_duration(self):
        '''Get duration (in ms) of media descriptor object item.
        Note, you need to call L{parse_request}() or play the media
        at least once before calling this function.
        Not doing this will result in an undefined result.
        @return: duration of media item or -1 on error.
        '''
        return libvlc_media_get_duration(self)


    def get_filestat(self, type, out):
        '''Get a 'stat' value of media descriptor object item.
        @note: 'stat' values are currently only parsed by directory accesses. This
        mean that only sub medias of a directory media, parsed with
        L{parse_request}() can have valid 'stat' properties.
        @param type: a valid libvlc_media_stat_ define.
        @param out: field in which the value will be stored.
        @return: 1 on success, 0 if not found, -1 on error.
        @version: LibVLC 4.0.0 and later.
        '''
        return libvlc_media_get_filestat(self, type, out)


    def get_parsed_status(self):
        '''Get Parsed status for media descriptor object.
        See libvlc_MediaParsedChanged
        See L{MediaParsedStatus}
        See L{parse_request}().
        @return: a value of the L{MediaParsedStatus} enum.
        @version: LibVLC 3.0.0 or later.
        '''
        return libvlc_media_get_parsed_status(self)


    def set_user_data(self, p_new_user_data):
        '''Sets media descriptor's user_data. user_data is specialized data
        accessed by the host application, VLC.framework uses it as a pointer to
        an native object that references a L{Media} pointer.
        @param p_new_user_data: pointer to user data.
        '''
        return libvlc_media_set_user_data(self, p_new_user_data)


    def get_user_data(self):
        '''Get media descriptor's user_data. user_data is specialized data
        accessed by the host application, VLC.framework uses it as a pointer to
        an native object that references a L{Media} pointer
        See L{set_user_data}.
        '''
        return libvlc_media_get_user_data(self)


    def get_tracklist(self, type):
        '''Get the track list for one type.
        @param type: type of the track list to request.
        @return: a valid libvlc_media_tracklist_t or None in case of error, if there is no track for a category, the returned list will have a size of 0, delete with L{tracklist_delete}().
        @version: LibVLC 4.0.0 and later. @note You need to call L{parse_request}() or play the media at least once before calling this function.  Not doing this will result in an empty list. See L{tracklist_count} See L{tracklist_at}.
        '''
        return libvlc_media_get_tracklist(self, type)


    def get_type(self):
        '''Get the media type of the media descriptor object.
        @return: media type.
        @version: LibVLC 3.0.0 and later. See L{MediaType}.
        '''
        return libvlc_media_get_type(self)


    def slaves_add(self, i_type, i_priority, psz_uri):
        '''Add a slave to the current media.
        A slave is an external input source that may contains an additional subtitle
        track (like a .srt) or an additional audio track (like a .ac3).
        @note: This function must be called before the media is parsed (via
        L{parse_request}()) or before the media is played (via
        L{player_play}()).
        @param i_type: subtitle or audio.
        @param i_priority: from 0 (low priority) to 4 (high priority).
        @param psz_uri: Uri of the slave (should contain a valid scheme).
        @return: 0 on success, -1 on error.
        @version: LibVLC 3.0.0 and later.
        '''
        return libvlc_media_slaves_add(self, i_type, i_priority, str_to_bytes(psz_uri))


    def slaves_clear(self):
        '''Clear all slaves previously added by L{slaves_add}() or
        internally.
        @version: LibVLC 3.0.0 and later.
        '''
        return libvlc_media_slaves_clear(self)


    def slaves_get(self, ppp_slaves):
        '''Get a media descriptor's slave list
        The list will contain slaves parsed by VLC or previously added by
        L{slaves_add}(). The typical use case of this function is to save
        a list of slave in a database for a later use.
        @param ppp_slaves: address to store an allocated array of slaves (must be freed with L{slaves_release}()) [OUT].
        @return: the number of slaves (zero on error).
        @version: LibVLC 3.0.0 and later. See L{slaves_add}.
        '''
        return libvlc_media_slaves_get(self, ppp_slaves)

class MediaDiscoverer(_Ctype):
    '''N/A
    '''

    def __new__(cls, ptr=_internal_guard):
        '''(INTERNAL) ctypes wrapper constructor.
        '''
        return _Constructor(cls, ptr)

    def start(self):
        '''Start media discovery.
        To stop it, call L{stop}() or
        L{list_release}() directly.
        See L{stop}.
        @return: -1 in case of error, 0 otherwise.
        @version: LibVLC 3.0.0 or later.
        '''
        return libvlc_media_discoverer_start(self)


    def stop(self):
        '''Stop media discovery.
        See L{start}.
        @version: LibVLC 3.0.0 or later.
        '''
        return libvlc_media_discoverer_stop(self)


    def release(self):
        '''Release media discover object. If the reference count reaches 0, then
        the object will be released.
        '''
        return libvlc_media_discoverer_release(self)


    def media_list(self):
        '''Get media service discover media list.
        @return: list of media items.
        '''
        return libvlc_media_discoverer_media_list(self)


    def is_running(self):
        '''Query if media service discover object is running.
        '''
        return libvlc_media_discoverer_is_running(self)

class MediaList(_Ctype):
    '''Create a new MediaList instance.

    Usage: MediaList(list_of_MRLs)

    See vlc.Instance.media_list_new documentation for details.
    
    '''

    def __new__(cls, *args):
        if args:
            i = args[0]
            if isinstance(i, _Ints):
                return _Constructor(cls, i)
            if isinstance(i, Instance):
                return i.media_list_new(*args[1:])

        o = get_default_instance().media_list_new(*args)
        return o

    def get_instance(self):
        return getattr(self, '_instance', None)

    def add_media(self, mrl):
        """Add media instance to media list.

        The L{lock} should be held upon entering this function.
        @param mrl: a media instance or a MRL.
        @return: 0 on success, -1 if the media list is read-only.
        """
        mrl = try_fspath(mrl)
        if isinstance(mrl, basestring):
            mrl = (self.get_instance() or get_default_instance()).media_new(mrl)
        return libvlc_media_list_add_media(self, mrl)



    def release(self):
        '''Release media list created with L{new}().
        '''
        return libvlc_media_list_release(self)


    def retain(self):
        '''Retain reference to a media list.
        '''
        return libvlc_media_list_retain(self)


    def set_media(self, p_md):
        '''Associate media instance with this media list instance.
        If another media instance was present it will be released.
        The L{lock} should NOT be held upon entering this function.
        @param p_md: media instance to add.
        '''
        return libvlc_media_list_set_media(self, p_md)


    def media(self):
        '''Get media instance from this media list instance. This action will increase
        the refcount on the media instance.
        The L{lock} should NOT be held upon entering this function.
        @return: media instance.
        '''
        return libvlc_media_list_media(self)


    def insert_media(self, p_md, i_pos):
        '''Insert media instance in media list on a position
        The L{lock} should be held upon entering this function.
        @param p_md: a media instance.
        @param i_pos: position in array where to insert.
        @return: 0 on success, -1 if the media list is read-only.
        '''
        return libvlc_media_list_insert_media(self, p_md, i_pos)


    def remove_index(self, i_pos):
        '''Remove media instance from media list on a position
        The L{lock} should be held upon entering this function.
        @param i_pos: position in array where to insert.
        @return: 0 on success, -1 if the list is read-only or the item was not found.
        '''
        return libvlc_media_list_remove_index(self, i_pos)


    def count(self):
        '''Get count on media list items
        The L{lock} should be held upon entering this function.
        @return: number of items in media list.
        '''
        return libvlc_media_list_count(self)

    def __len__(self):
        return libvlc_media_list_count(self)


    def item_at_index(self, i_pos):
        '''List media instance in media list at a position
        The L{lock} should be held upon entering this function.
        @param i_pos: position in array where to insert.
        @return: media instance at position i_pos, or None if not found. In case of success, L{media_retain}() is called to increase the refcount on the media.
        '''
        return libvlc_media_list_item_at_index(self, i_pos)

    def __getitem__(self, i):
        return libvlc_media_list_item_at_index(self, i)

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]


    def index_of_item(self, p_md):
        '''Find index position of List media instance in media list.
        Warning: the function will return the first matched position.
        The L{lock} should be held upon entering this function.
        @param p_md: media instance.
        @return: position of media instance or -1 if media not found.
        '''
        return libvlc_media_list_index_of_item(self, p_md)


    def is_readonly(self):
        '''This indicates if this media list is read-only from a user point of view.
        '''
        return libvlc_media_list_is_readonly(self)


    def lock(self):
        '''Get lock on media list items.
        '''
        return libvlc_media_list_lock(self)


    def unlock(self):
        '''Release lock on media list items
        The L{lock} should be held upon entering this function.
        '''
        return libvlc_media_list_unlock(self)

    @memoize_parameterless
    def event_manager(self):
        '''Get libvlc_event_manager from this media list instance.
        The p_event_manager is immutable, so you don't have to hold the lock.
        @return: libvlc_event_manager.
        '''
        return libvlc_media_list_event_manager(self)

class MediaListPlayer(_Ctype):
    '''Create a new MediaListPlayer instance.

    It may take as parameter either:
      - a vlc.Instance
      - nothing
    
    '''

    def __new__(cls, arg=None):
        if arg is None:
            i = get_default_instance()
        elif isinstance(arg, Instance):
            i = arg
        elif isinstance(arg, _Ints):
            return _Constructor(cls, arg)
        else:
            raise TypeError('MediaListPlayer %r' % (arg,))

        return i.media_list_player_new()

    def get_instance(self):
        """Return the associated Instance.
        """
        return self._instance  #PYCHOK expected



    def release(self):
        '''Release a media_list_player after use
        Decrement the reference count of a media player object. If the
        reference count is 0, then L{release}() will
        release the media player object. If the media player object
        has been released, then it should not be used again.
        '''
        return libvlc_media_list_player_release(self)


    def retain(self):
        '''Retain a reference to a media player list object. Use
        L{release}() to decrement reference count.
        '''
        return libvlc_media_list_player_retain(self)

    @memoize_parameterless
    def event_manager(self):
        '''Return the event manager of this media_list_player.
        @return: the event manager.
        '''
        return libvlc_media_list_player_event_manager(self)


    def set_media_player(self, p_mi):
        '''Replace media player in media_list_player with this instance.
        @param p_mi: media player instance.
        '''
        return libvlc_media_list_player_set_media_player(self, p_mi)


    def get_media_player(self):
        '''Get media player of the media_list_player instance.
        @return: media player instance @note the caller is responsible for releasing the returned instance.
        '''
        return libvlc_media_list_player_get_media_player(self)


    def set_media_list(self, p_mlist):
        '''Set the media list associated with the player.
        @param p_mlist: list of media.
        '''
        return libvlc_media_list_player_set_media_list(self, p_mlist)


    def play(self):
        '''Play media list.
        '''
        return libvlc_media_list_player_play(self)


    def pause(self):
        '''Toggle pause (or resume) media list.
        '''
        return libvlc_media_list_player_pause(self)


    def set_pause(self, do_pause):
        '''Pause or resume media list.
        @param do_pause: play/resume if zero, pause if non-zero.
        @version: LibVLC 3.0.0 or later.
        '''
        return libvlc_media_list_player_set_pause(self, do_pause)


    def is_playing(self):
        '''Is media list playing?
        '''
        return libvlc_media_list_player_is_playing(self)


    def get_state(self):
        '''Get current libvlc_state of media list player.
        @return: L{State} for media list player.
        '''
        return libvlc_media_list_player_get_state(self)


    def play_item_at_index(self, i_index):
        '''Play media list item at position index.
        @param i_index: index in media list to play.
        @return: 0 upon success -1 if the item wasn't found.
        '''
        return libvlc_media_list_player_play_item_at_index(self, i_index)

    def __getitem__(self, i):
        return libvlc_media_list_player_play_item_at_index(self, i)

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]


    def play_item(self, p_md):
        '''Play the given media item.
        @param p_md: the media instance.
        @return: 0 upon success, -1 if the media is not part of the media list.
        '''
        return libvlc_media_list_player_play_item(self, p_md)


    def stop_async(self):
        '''Stop playing media list.
        '''
        return libvlc_media_list_player_stop_async(self)


    def next(self):
        '''Play next item from media list.
        @return: 0 upon success -1 if there is no next item.
        '''
        return libvlc_media_list_player_next(self)


    def previous(self):
        '''Play previous item from media list.
        @return: 0 upon success -1 if there is no previous item.
        '''
        return libvlc_media_list_player_previous(self)


    def set_playback_mode(self, e_mode):
        '''Sets the playback mode for the playlist.
        @param e_mode: playback mode specification.
        '''
        return libvlc_media_list_player_set_playback_mode(self, e_mode)

class MediaPlayer(_Ctype):
    '''Create a new MediaPlayer instance.

    It may take as parameter either:
      - a string (media URI), options... In this case, a vlc.Instance will be created.
      - a vlc.Instance, a string (media URI), options...
    
    '''

    def __new__(cls, *args):
        if len(args) == 1 and isinstance(args[0], _Ints):
            return _Constructor(cls, args[0])

        if args and isinstance(args[0], Instance):
            instance = args[0]
            args = args[1:]
        else:
            instance = get_default_instance()

        o = instance.media_player_new()
        if args:
            o.set_media(instance.media_new(*args))
        return o

    def get_instance(self):
        """Return the associated Instance.
        """
        return self._instance  #PYCHOK expected

    def set_mrl(self, mrl, *options):
        """Set the MRL to play.

        Warning: most audio and video options, such as text renderer,
        have no effects on an individual media. These options must be
        set at the vlc.Instance or vlc.MediaPlayer instanciation.

        @param mrl: The MRL
        @param options: optional media option=value strings
        @return: the Media object
        """
        m = self.get_instance().media_new(mrl, *options)
        self.set_media(m)
        return m

    def video_get_spu_description(self):
        """Get the description of available video subtitles.
        """
        return track_description_list(libvlc_video_get_spu_description(self))

    def video_get_track_description(self):
        """Get the description of available video tracks.
        """
        return track_description_list(libvlc_video_get_track_description(self))

    def audio_get_track_description(self):
        """Get the description of available audio tracks.
        """
        return track_description_list(libvlc_audio_get_track_description(self))

    def get_full_title_descriptions(self):
        '''Get the full description of available titles.
        @return: the titles list
        @version: LibVLC 3.0.0 and later.
        '''
        titleDescription_pp = ctypes.POINTER(TitleDescription)()
        n = libvlc_media_player_get_full_title_descriptions(self, ctypes.byref(titleDescription_pp))
        info = ctypes.cast(titleDescription_pp, ctypes.POINTER(ctypes.POINTER(TitleDescription) * n))
        try:
            contents = info.contents
        except ValueError:
            # Media not parsed, no info.
            return None
        descr = ( contents[i].contents for i in range(len(contents)) )
        return descr

    def get_full_chapter_descriptions(self, i_chapters_of_title):
        '''Get the full description of available chapters.
        @param i_chapters_of_title: index of the title to query for chapters (uses current title if set to -1).
        @return: the chapters list
        @version: LibVLC 3.0.0 and later.
        '''
        chapterDescription_pp = ctypes.POINTER(ChapterDescription)()
        n = libvlc_media_player_get_full_chapter_descriptions(self, i_chapters_of_title, ctypes.byref(chapterDescription_pp))
        info = ctypes.cast(chapterDescription_pp, ctypes.POINTER(ctypes.POINTER(ChapterDescription) * n))
        try:
            contents = info.contents
        except ValueError:
            # Media not parsed, no info.
            return None
        descr = ( contents[i].contents for i in range(len(contents)) )
        return descr

    def video_get_size(self, num=0):
        """Get the video size in pixels as 2-tuple (width, height).

        @param num: video number (default 0).
        """
        r = libvlc_video_get_size(self, num)
        if isinstance(r, tuple) and len(r) == 2:
            return r
        else:
            raise VLCException('invalid video number (%s)' % (num,))

    def set_hwnd(self, drawable):
        """Set a Win32/Win64 API window handle (HWND).

        Specify where the media player should render its video
        output. If LibVLC was built without Win32/Win64 API output
        support, then this has no effects.

        @param drawable: windows handle of the drawable.
        """
        if not isinstance(drawable, ctypes.c_void_p):
            drawable = ctypes.c_void_p(int(drawable))
        libvlc_media_player_set_hwnd(self, drawable)

    def video_get_width(self, num=0):
        """Get the width of a video in pixels.

        @param num: video number (default 0).
        """
        return self.video_get_size(num)[0]

    def video_get_height(self, num=0):
        """Get the height of a video in pixels.

        @param num: video number (default 0).
        """
        return self.video_get_size(num)[1]

    def video_get_cursor(self, num=0):
        """Get the mouse pointer coordinates over a video as 2-tuple (x, y).

        Coordinates are expressed in terms of the decoded video resolution,
        B{not} in terms of pixels on the screen/viewport.  To get the
        latter, you must query your windowing system directly.

        Either coordinate may be negative or larger than the corresponding
        size of the video, if the cursor is outside the rendering area.

        @warning: The coordinates may be out-of-date if the pointer is not
        located on the video rendering area.  LibVLC does not track the
        mouse pointer if the latter is outside the video widget.

        @note: LibVLC does not support multiple mouse pointers (but does
        support multiple input devices sharing the same pointer).

        @param num: video number (default 0).
        """
        r = libvlc_video_get_cursor(self, num)
        if isinstance(r, tuple) and len(r) == 2:
            return r
        raise VLCException('invalid video number (%s)' % (num,))



    def video_get_track_count(self):
        '''Get number of available video tracks.
        @return: the number of available video tracks (int).
        '''
        return libvlc_video_get_track_count(self)


    def video_get_track(self):
        '''Get current video track.
        @return: the video track ID (int) or -1 if no active input.
        '''
        return libvlc_video_get_track(self)


    def video_set_track(self, i_track):
        '''Set video track.
        @param i_track: the track ID (i_id field from track description).
        @return: 0 on success, -1 if out of range.
        '''
        return libvlc_video_set_track(self, i_track)


    def video_get_spu(self):
        '''Get current video subtitle.
        @return: the video subtitle selected, or -1 if none.
        '''
        return libvlc_video_get_spu(self)


    def video_get_spu_count(self):
        '''Get the number of available video subtitles.
        @return: the number of available video subtitles.
        '''
        return libvlc_video_get_spu_count(self)


    def video_set_spu(self, i_spu):
        '''Set new video subtitle.
        @param i_spu: video subtitle track to select (i_id from track description).
        @return: 0 on success, -1 if out of range.
        '''
        return libvlc_video_set_spu(self, i_spu)


    def audio_get_track_count(self):
        '''Get number of available audio tracks.
        @return: the number of available audio tracks (int), or -1 if unavailable.
        '''
        return libvlc_audio_get_track_count(self)


    def audio_get_track(self):
        '''Get current audio track.
        @return: the audio track ID or -1 if no active input.
        '''
        return libvlc_audio_get_track(self)


    def audio_set_track(self, i_track):
        '''Set current audio track.
        @param i_track: the track ID (i_id field from track description).
        @return: 0 on success, -1 on error.
        '''
        return libvlc_audio_set_track(self, i_track)


    def release(self):
        '''Release a media_player after use
        Decrement the reference count of a media player object. If the
        reference count is 0, then L{release}() will
        release the media player object. If the media player object
        has been released, then it should not be used again.
        '''
        return libvlc_media_player_release(self)


    def retain(self):
        '''Retain a reference to a media player object. Use
        L{release}() to decrement reference count.
        '''
        return libvlc_media_player_retain(self)


    def set_media(self, p_md):
        '''Set the media that will be used by the media_player. If any,
        previous md will be released.
        @note: The user should listen to the libvlc_MediaPlayerMediaChanged event, to
        know when the new media is actually used by the player (or to known that the
        older media is no longer used).
        @param p_md: the Media. Afterwards the p_md can be safely destroyed.
        '''
        return libvlc_media_player_set_media(self, p_md)


    def get_media(self):
        '''Get the media used by the media_player.
        @warning: Calling this function just after L{set_media}()
        will return the media that was just set, but this media might not be
        currently used internally by the player. To detect such case, the user
        should listen to the libvlc_MediaPlayerMediaChanged event.
        @return: the media associated with p_mi, or None if no media is associated.
        '''
        return libvlc_media_player_get_media(self)

    @memoize_parameterless
    def event_manager(self):
        '''Get the Event Manager from which the media player send event.
        @return: the event manager associated with p_mi.
        '''
        return libvlc_media_player_event_manager(self)


    def is_playing(self):
        '''is_playing.
        '''
        return libvlc_media_player_is_playing(self)


    def play(self):
        '''Play.
        @return: 0 if playback started (and was already started), or -1 on error.
        '''
        return libvlc_media_player_play(self)


    def set_pause(self, do_pause):
        '''Pause or resume (no effect if there is no media).
        @param do_pause: play/resume if zero, pause if non-zero.
        @version: LibVLC 1.1.1 or later.
        '''
        return libvlc_media_player_set_pause(self, do_pause)


    def pause(self):
        '''Toggle pause (no effect if there is no media).
        '''
        return libvlc_media_player_pause(self)


    def stop_async(self):
        '''Stop asynchronously
        @note: This function is asynchronous. In case of success, the user should
        wait for the libvlc_MediaPlayerStopped event to know when the stop is
        finished.
        @return: 0 if the player is being stopped, -1 otherwise (no-op).
        @version: LibVLC 4.0.0 or later.
        '''
        return libvlc_media_player_stop_async(self)


    def set_renderer(self, p_item):
        '''Set a renderer to the media player
        @note: must be called before the first call of L{play}() to
        take effect.
        See L{renderer_discoverer_new}.
        @param p_item: an item discovered by L{renderer_discoverer_start}().
        @return: 0 on success, -1 on error.
        @version: LibVLC 3.0.0 or later.
        '''
        return libvlc_media_player_set_renderer(self, p_item)


    def video_set_callbacks(self, lock, unlock, display, opaque):
        '''Set callbacks and private data to render decoded video to a custom area
        in memory.
        Use L{video_set_format}() or L{video_set_format_callbacks}()
        to configure the decoded format.
        @warning: Rendering video into custom memory buffers is considerably less
        efficient than rendering in a custom window as normal.
        For optimal perfomances, VLC media player renders into a custom window, and
        does not use this function and associated callbacks. It is B{highly
        recommended} that other LibVLC-based application do likewise.
        To embed video in a window, use L{set_xwindow}() or
        equivalent depending on the operating system.
        If window embedding does not fit the application use case, then a custom
        LibVLC video output display plugin is required to maintain optimal video
        rendering performances.
        The following limitations affect performance:
        - Hardware video decoding acceleration will either be disabled completely,
          or require (relatively slow) copy from video/DSP memory to main memory.
        - Sub-pictures (subtitles, on-screen display, etc.) must be blent into the
          main picture by the CPU instead of the GPU.
        - Depending on the video format, pixel format conversion, picture scaling,
          cropping and/or picture re-orientation, must be performed by the CPU
          instead of the GPU.
        - Memory copying is required between LibVLC reference picture buffers and
          application buffers (between lock and unlock callbacks).
        @param lock: callback to lock video memory (must not be None).
        @param unlock: callback to unlock video memory (or None if not needed).
        @param display: callback to display video (or None if not needed).
        @param opaque: private pointer for the three callbacks (as first parameter).
        @version: LibVLC 1.1.1 or later.
        '''
        return libvlc_video_set_callbacks(self, lock, unlock, display, opaque)


    def video_set_format(self, chroma, width, height, pitch):
        '''Set decoded video chroma and dimensions.
        This only works in combination with L{video_set_callbacks}(),
        and is mutually exclusive with L{video_set_format_callbacks}().
        @param chroma: a four-characters string identifying the chroma (e.g. "RV32" or "YUYV").
        @param width: pixel width.
        @param height: pixel height.
        @param pitch: line pitch (in bytes).
        @version: LibVLC 1.1.1 or later.
        @bug: All pixel planes are expected to have the same pitch. To use the YCbCr color space with chrominance subsampling, consider using L{video_set_format_callbacks}() instead.
        '''
        return libvlc_video_set_format(self, str_to_bytes(chroma), width, height, pitch)


    def video_set_format_callbacks(self, setup, cleanup):
        '''Set decoded video chroma and dimensions. This only works in combination with
        L{video_set_callbacks}().
        @param setup: callback to select the video format (cannot be None).
        @param cleanup: callback to release any allocated resources (or None).
        @version: LibVLC 2.0.0 or later.
        '''
        return libvlc_video_set_format_callbacks(self, setup, cleanup)


    def set_nsobject(self, drawable):
        '''Set the NSView handler where the media player should render its video output.
        Use the vout called "macosx".
        The drawable is an NSObject that follow the VLCVideoViewEmbedding
        protocol:
        @code.m
        @protocol VLCVideoViewEmbedding <NSObject>
        - (void)addVoutSubview:(NSView *)view;
        - (void)removeVoutSubview:(NSView *)view;
        @end
        @endcode
        Or it can be an NSView object.
        If you want to use it along with Qt see the QMacCocoaViewContainer. Then
        the following code should work:
        @code.mm
        
            NSView *video = [[NSView alloc] init];
            QMacCocoaViewContainer *container = new QMacCocoaViewContainer(video, parent);
            L{set_nsobject}(mp, video);
            [video release];
        
        @endcode
        You can find a live example in VLCVideoView in VLCKit.framework.
        @param drawable: the drawable that is either an NSView or an object following the VLCVideoViewEmbedding protocol.
        '''
        return libvlc_media_player_set_nsobject(self, drawable)


    def get_nsobject(self):
        '''Get the NSView handler previously set with L{set_nsobject}().
        @return: the NSView handler or 0 if none where set.
        '''
        return libvlc_media_player_get_nsobject(self)


    def set_xwindow(self, drawable):
        '''Set an X Window System drawable where the media player should render its
        video output. The call takes effect when the playback starts. If it is
        already started, it might need to be stopped before changes apply.
        If LibVLC was built without X11 output support, then this function has no
        effects.
        By default, LibVLC will capture input events on the video rendering area.
        Use L{video_set_mouse_input}() and L{video_set_key_input}() to
        disable that and deliver events to the parent window / to the application
        instead. By design, the X11 protocol delivers input events to only one
        recipient.
        @warning
        The application must call the XInitThreads() function from Xlib before
        L{new}(), and before any call to XOpenDisplay() directly or via any
        other library. Failure to call XInitThreads() will seriously impede LibVLC
        performance. Calling XOpenDisplay() before XInitThreads() will eventually
        crash the process. That is a limitation of Xlib.
        @param drawable: X11 window ID @note The specified identifier must correspond to an existing Input/Output class X11 window. Pixmaps are B{not} currently supported. The default X11 server is assumed, i.e. that specified in the DISPLAY environment variable. @warning LibVLC can deal with invalid X11 handle errors, however some display drivers (EGL, GLX, VA and/or VDPAU) can unfortunately not. Thus the window handle must remain valid until playback is stopped, otherwise the process may abort or crash.
        @bug No more than one window handle per media player instance can be specified. If the media has multiple simultaneously active video tracks, extra tracks will be rendered into external windows beyond the control of the application.
        '''
        return libvlc_media_player_set_xwindow(self, drawable)


    def get_xwindow(self):
        '''Get the X Window System window identifier previously set with
        L{set_xwindow}(). Note that this will return the identifier
        even if VLC is not currently using it (for instance if it is playing an
        audio-only input).
        @return: an X window ID, or 0 if none where set.
        '''
        return libvlc_media_player_get_xwindow(self)


    def get_hwnd(self):
        '''Get the Windows API window handle (HWND) previously set with
        L{set_hwnd}(). The handle will be returned even if LibVLC
        is not currently outputting any video to it.
        @return: a window handle or None if there are none.
        '''
        return libvlc_media_player_get_hwnd(self)


    def set_android_context(self, p_awindow_handler):
        '''Set the android context.
        @param p_awindow_handler: org.videolan.libvlc.AWindow jobject owned by the org.videolan.libvlc.MediaPlayer class from the libvlc-android project.
        @version: LibVLC 3.0.0 and later.
        '''
        return libvlc_media_player_set_android_context(self, p_awindow_handler)


    def audio_set_callbacks(self, play, pause, resume, flush, drain, opaque):
        '''Sets callbacks and private data for decoded audio.
        Use L{audio_set_format}() or L{audio_set_format_callbacks}()
        to configure the decoded audio format.
        @note: The audio callbacks override any other audio output mechanism.
        If the callbacks are set, LibVLC will B{not} output audio in any way.
        @param play: callback to play audio samples (must not be None).
        @param pause: callback to pause playback (or None to ignore).
        @param resume: callback to resume playback (or None to ignore).
        @param flush: callback to flush audio buffers (or None to ignore).
        @param drain: callback to drain audio buffers (or None to ignore).
        @param opaque: private pointer for the audio callbacks (as first parameter).
        @version: LibVLC 2.0.0 or later.
        '''
        return libvlc_audio_set_callbacks(self, play, pause, resume, flush, drain, opaque)


    def audio_set_volume_callback(self, set_volume):
        '''Set callbacks and private data for decoded audio. This only works in
        combination with L{audio_set_callbacks}().
        Use L{audio_set_format}() or L{audio_set_format_callbacks}()
        to configure the decoded audio format.
        @param set_volume: callback to apply audio volume, or None to apply volume in software.
        @version: LibVLC 2.0.0 or later.
        '''
        return libvlc_audio_set_volume_callback(self, set_volume)


    def audio_set_format_callbacks(self, setup, cleanup):
        '''Sets decoded audio format via callbacks.
        This only works in combination with L{audio_set_callbacks}().
        @param setup: callback to select the audio format (cannot be None).
        @param cleanup: callback to release any allocated resources (or None).
        @version: LibVLC 2.0.0 or later.
        '''
        return libvlc_audio_set_format_callbacks(self, setup, cleanup)


    def audio_set_format(self, format, rate, channels):
        '''Sets a fixed decoded audio format.
        This only works in combination with L{audio_set_callbacks}(),
        and is mutually exclusive with L{audio_set_format_callbacks}().
        The supported formats are:
        - "S16N" for signed 16-bit PCM
        - "S32N" for signed 32-bit PCM
        - "FL32" for single precision IEEE 754
        All supported formats use the native endianess.
        If there are more than one channel, samples are interleaved.
        @param format: a four-characters string identifying the sample format.
        @param rate: sample rate (expressed in Hz).
        @param channels: channels count.
        @version: LibVLC 2.0.0 or later.
        '''
        return libvlc_audio_set_format(self, str_to_bytes(format), rate, channels)


    def get_length(self):
        '''Get the current movie length (in ms).
        @return: the movie length (in ms), or -1 if there is no media.
        '''
        return libvlc_media_player_get_length(self)


    def get_time(self):
        '''Get the current movie time (in ms).
        @return: the movie time (in ms), or -1 if there is no media.
        '''
        return libvlc_media_player_get_time(self)


    def set_time(self, i_time, b_fast):
        '''Set the movie time (in ms). This has no effect if no media is being played.
        Not all formats and protocols support this.
        @param b_fast: prefer fast seeking or precise seeking.
        @param i_time: the movie time (in ms).
        @return: 0 on success, -1 on error.
        '''
        return libvlc_media_player_set_time(self, i_time, b_fast)


    def get_position(self):
        '''Get movie position as percentage between 0.0 and 1.0.
        @return: movie position, or -1. in case of error.
        '''
        return libvlc_media_player_get_position(self)


    def set_position(self, f_pos, b_fast):
        '''Set movie position as percentage between 0.0 and 1.0.
        This has no effect if playback is not enabled.
        This might not work depending on the underlying input format and protocol.
        @param b_fast: prefer fast seeking or precise seeking.
        @param f_pos: the position.
        @return: 0 on success, -1 on error.
        '''
        return libvlc_media_player_set_position(self, f_pos, b_fast)


    def set_chapter(self, i_chapter):
        '''Set movie chapter (if applicable).
        @param i_chapter: chapter number to play.
        '''
        return libvlc_media_player_set_chapter(self, i_chapter)


    def get_chapter(self):
        '''Get movie chapter.
        @return: chapter number currently playing, or -1 if there is no media.
        '''
        return libvlc_media_player_get_chapter(self)


    def get_chapter_count(self):
        '''Get movie chapter count.
        @return: number of chapters in movie, or -1.
        '''
        return libvlc_media_player_get_chapter_count(self)


    def get_chapter_count_for_title(self, i_title):
        '''Get title chapter count.
        @param i_title: title.
        @return: number of chapters in title, or -1.
        '''
        return libvlc_media_player_get_chapter_count_for_title(self, i_title)


    def set_title(self, i_title):
        '''Set movie title.
        @param i_title: title number to play.
        '''
        return libvlc_media_player_set_title(self, i_title)


    def get_title(self):
        '''Get movie title.
        @return: title number currently playing, or -1.
        '''
        return libvlc_media_player_get_title(self)


    def get_title_count(self):
        '''Get movie title count.
        @return: title number count, or -1.
        '''
        return libvlc_media_player_get_title_count(self)


    def previous_chapter(self):
        '''Set previous chapter (if applicable).
        '''
        return libvlc_media_player_previous_chapter(self)


    def next_chapter(self):
        '''Set next chapter (if applicable).
        '''
        return libvlc_media_player_next_chapter(self)


    def get_rate(self):
        '''Get the requested movie play rate.
        @warning: Depending on the underlying media, the requested rate may be
        different from the real playback rate.
        @return: movie play rate.
        '''
        return libvlc_media_player_get_rate(self)


    def set_rate(self, rate):
        '''Set movie play rate.
        @param rate: movie play rate to set.
        @return: -1 if an error was detected, 0 otherwise (but even then, it might not actually work depending on the underlying media protocol).
        '''
        return libvlc_media_player_set_rate(self, rate)


    def get_state(self):
        '''Get current movie state.
        @return: the current state of the media player (playing, paused, ...) See L{State}.
        '''
        return libvlc_media_player_get_state(self)


    def has_vout(self):
        '''How many video outputs does this media player have?
        @return: the number of video outputs.
        '''
        return libvlc_media_player_has_vout(self)


    def is_seekable(self):
        '''Is this media player seekable?
        '''
        return libvlc_media_player_is_seekable(self)


    def can_pause(self):
        '''Can this media player be paused?
        '''
        return libvlc_media_player_can_pause(self)


    def program_scrambled(self):
        '''Check if the current program is scrambled.
        @version: LibVLC 2.2.0 or later.
        '''
        return libvlc_media_player_program_scrambled(self)


    def next_frame(self):
        '''Display the next frame (if supported).
        '''
        return libvlc_media_player_next_frame(self)


    def navigate(self, navigate):
        '''Navigate through DVD Menu.
        @param navigate: the Navigation mode.
        @version: libVLC 2.0.0 or later.
        '''
        return libvlc_media_player_navigate(self, navigate)


    def set_video_title_display(self, position, timeout):
        '''Set if, and how, the video title will be shown when media is played.
        @param position: position at which to display the title, or libvlc_position_disable to prevent the title from being displayed.
        @param timeout: title display timeout in milliseconds (ignored if libvlc_position_disable).
        @version: libVLC 2.1.0 or later.
        '''
        return libvlc_media_player_set_video_title_display(self, position, timeout)


    def get_tracklist(self, type, selected):
        '''Get the track list for one type.
        @param type: type of the track list to request.
        @param selected: filter only selected tracks if true (return all tracks, even selected ones if false).
        @return: a valid libvlc_media_tracklist_t or None in case of error, if there is no track for a category, the returned list will have a size of 0, delete with L{media_tracklist_delete}().
        @version: LibVLC 4.0.0 and later. @note You need to call L{media_parse_request}() or play the media at least once before calling this function.  Not doing this will result in an empty list. @note This track list is a snapshot of the current tracks when this function is called. If a track is updated after this call, the user will need to call this function again to get the updated track. The track list can be used to get track information and to select specific tracks.
        '''
        return libvlc_media_player_get_tracklist(self, type, selected)


    def get_selected_track(self, type):
        '''Get the selected track for one type.
        @param type: type of the selected track.
        @return: a valid track or None if there is no selected tracks for this type, release it with L{media_track_release}().
        @version: LibVLC 4.0.0 and later. @warning More than one tracks can be selected for one type. In that case, L{get_tracklist}() should be used.
        '''
        return libvlc_media_player_get_selected_track(self, type)


    def get_track_from_id(self, psz_id):
        '''Get a track from a track id.
        @param psz_id: valid string representing a track id (cf. psz_id from \ref L{MediaTrack}).
        @return: a valid track or None if there is currently no tracks identified by the string id, release it with L{media_track_release}().
        @version: LibVLC 4.0.0 and later. This function can be used to get the last updated information of a track.
        '''
        return libvlc_media_player_get_track_from_id(self, str_to_bytes(psz_id))


    def select_track(self, track):
        '''Select a track
        This will unselected the current track.
        @param track: track to select, can't be None.
        @version: LibVLC 4.0.0 and later. @note Use L{select_tracks}() for multiple selection @warning Only use a \ref L{MediaTrack} retrieved with \ref L{get_tracklist}.
        '''
        return libvlc_media_player_select_track(self, track)


    def unselect_track_type(self, type):
        '''Unselect all tracks for a given type.
        @param type: type to unselect.
        @version: LibVLC 4.0.0 and later.
        '''
        return libvlc_media_player_unselect_track_type(self, type)


    def select_tracks(self, type, tracks, track_count):
        '''Select multiple tracks for one type.
        @param type: type of the selected track.
        @param tracks: pointer to the track array, or None if track_count is 0.
        @param track_count: number of tracks in the track array.
        @version: LibVLC 4.0.0 and later. @note The internal track list can change between the calls of L{get_tracklist}() and libvlc_media_player_set_tracks(). If a track selection change but the track is not present anymore, the player will just ignore it. @note selecting multiple audio tracks is currently not supported. @warning Only use a \ref L{MediaTrack} retrieved with \ref L{get_tracklist}.
        '''
        return libvlc_media_player_select_tracks(self, type, tracks, track_count)


    def select_tracks_by_ids(self, type, psz_ids):
        '''Select tracks by their string identifier.
        @param type: type to select.
        @param psz_ids: list of string identifier or None.
        @version: LibVLC 4.0.0 and later. This function can be used pre-select a list of tracks before starting the player. It has only effect for the current media. It can also be used when the player is already started. 'str_ids' can contain more than one track id, delimited with ','. "" or any invalid track id will cause the player to unselect all tracks of that category. None will disable the preference for newer tracks without unselecting any current tracks. Example: - (libvlc_track_video, "video/1,video/2") will select these 2 video tracks. If there is only one video track with the id "video/0", no tracks will be selected. - (L{TrackType}, "$slave_url_md5sum/spu/0) will select one spu added by an input slave with the corresponding url. @note The string identifier of a track can be found via psz_id from \ref L{MediaTrack} @note selecting multiple audio tracks is currently not supported. @warning Only use a \ref L{MediaTrack} id retrieved with \ref L{get_tracklist}.
        '''
        return libvlc_media_player_select_tracks_by_ids(self, type, str_to_bytes(psz_ids))


    def add_slave(self, i_type, psz_uri, b_select):
        '''Add a slave to the current media player.
        @note: If the player is playing, the slave will be added directly. This call
        will also update the slave list of the attached L{Media}.
        @param i_type: subtitle or audio.
        @param psz_uri: Uri of the slave (should contain a valid scheme).
        @param b_select: True if this slave should be selected when it's loaded.
        @return: 0 on success, -1 on error.
        @version: LibVLC 3.0.0 and later. See L{media_slaves_add}.
        '''
        return libvlc_media_player_add_slave(self, i_type, str_to_bytes(psz_uri), b_select)


    def select_program_id(self, i_group_id):
        '''Select program with a given program id.
        @note: program ids are sent via the libvlc_MediaPlayerProgramAdded event or
        can be fetch via L{get_programlist}().
        @param i_group_id: program id.
        @version: LibVLC 4.0.0 or later.
        '''
        return libvlc_media_player_select_program_id(self, i_group_id)


    def get_selected_program(self):
        '''Get the selected program.
        @return: a valid program struct or None if no programs are selected. The program need to be freed with L{player_program_delete}().
        @version: LibVLC 4.0.0 or later.
        '''
        return libvlc_media_player_get_selected_program(self)


    def get_program_from_id(self, i_group_id):
        '''Get a program struct from a program id.
        @param i_group_id: program id.
        @return: a valid program struct or None if the i_group_id is not found. The program need to be freed with L{player_program_delete}().
        @version: LibVLC 4.0.0 or later.
        '''
        return libvlc_media_player_get_program_from_id(self, i_group_id)


    def get_programlist(self):
        '''Get the program list.
        @return: a valid libvlc_media_programlist_t or None in case of error or empty list, delete with libvlc_media_programlist_delete().
        @version: LibVLC 4.0.0 and later. @note This program list is a snapshot of the current programs when this function is called. If a program is updated after this call, the user will need to call this function again to get the updated program. The program list can be used to get program information and to select specific programs.
        '''
        return libvlc_media_player_get_programlist(self)


    def toggle_fullscreen(self):
        '''Toggle fullscreen status on non-embedded video outputs.
        @warning: The same limitations applies to this function
        as to L{set_fullscreen}().
        '''
        return libvlc_toggle_fullscreen(self)


    def set_fullscreen(self, b_fullscreen):
        '''Enable or disable fullscreen.
        @warning: With most window managers, only a top-level windows can be in
        full-screen mode. Hence, this function will not operate properly if
        L{set_xwindow}() was used to embed the video in a
        non-top-level window. In that case, the embedding window must be reparented
        to the root window B{before} fullscreen mode is enabled. You will want
        to reparent it back to its normal parent when disabling fullscreen.
        @note: This setting applies to any and all current or future active video
        tracks and windows for the given media player. The choice of fullscreen
        output for each window is left to the operating system.
        @param b_fullscreen: boolean for fullscreen status.
        '''
        return libvlc_set_fullscreen(self, b_fullscreen)


    def get_fullscreen(self):
        '''Get current fullscreen status.
        @return: the fullscreen status (boolean) \retval false media player is windowed \retval true media player is in fullscreen mode.
        '''
        return libvlc_get_fullscreen(self)


    def video_set_key_input(self, on):
        '''Enable or disable key press events handling, according to the LibVLC hotkeys
        configuration. By default and for historical reasons, keyboard events are
        handled by the LibVLC video widget.
        @note: On X11, there can be only one subscriber for key press and mouse
        click events per window. If your application has subscribed to those events
        for the X window ID of the video widget, then LibVLC will not be able to
        handle key presses and mouse clicks in any case.
        @warning: This function is only implemented for X11 and Win32 at the moment.
        @param on: true to handle key press events, false to ignore them.
        '''
        return libvlc_video_set_key_input(self, on)


    def video_set_mouse_input(self, on):
        '''Enable or disable mouse click events handling. By default, those events are
        handled. This is needed for DVD menus to work, as well as a few video
        filters such as "puzzle".
        See L{video_set_key_input}().
        @warning: This function is only implemented for X11 and Win32 at the moment.
        @param on: true to handle mouse click events, false to ignore them.
        '''
        return libvlc_video_set_mouse_input(self, on)


    def video_get_scale(self):
        '''Get the current video scaling factor.
        See also L{video_set_scale}().
        @return: the currently configured zoom factor, or 0. if the video is set to fit to the output window/drawable automatically.
        '''
        return libvlc_video_get_scale(self)


    def video_set_scale(self, f_factor):
        '''Set the video scaling factor. That is the ratio of the number of pixels on
        screen to the number of pixels in the original decoded video in each
        dimension. Zero is a special value; it will adjust the video to the output
        window/drawable (in windowed mode) or the entire screen.
        Note that not all video outputs support scaling.
        @param f_factor: the scaling factor, or zero.
        '''
        return libvlc_video_set_scale(self, f_factor)


    def video_get_aspect_ratio(self):
        '''Get current video aspect ratio.
        @return: the video aspect ratio or None if unspecified (the result must be released with free() or L{free}()).
        '''
        return libvlc_video_get_aspect_ratio(self)


    def video_set_aspect_ratio(self, psz_aspect):
        '''Set new video aspect ratio.
        @param psz_aspect: new video aspect-ratio or None to reset to default @note Invalid aspect ratios are ignored.
        '''
        return libvlc_video_set_aspect_ratio(self, str_to_bytes(psz_aspect))


    def video_update_viewpoint(self, p_viewpoint, b_absolute):
        '''Update the video viewpoint information.
        @note: It is safe to call this function before the media player is started.
        @param p_viewpoint: video viewpoint allocated via L{video_new_viewpoint}().
        @param b_absolute: if true replace the old viewpoint with the new one. If false, increase/decrease it.
        @return: -1 in case of error, 0 otherwise @note the values are set asynchronously, it will be used by the next frame displayed.
        @version: LibVLC 3.0.0 and later.
        '''
        return libvlc_video_update_viewpoint(self, p_viewpoint, b_absolute)


    def video_get_spu_delay(self):
        '''Get the current subtitle delay. Positive values means subtitles are being
        displayed later, negative values earlier.
        @return: time (in microseconds) the display of subtitles is being delayed.
        @version: LibVLC 2.0.0 or later.
        '''
        return libvlc_video_get_spu_delay(self)


    def video_get_spu_text_scale(self):
        '''Get the current subtitle text scale
        The scale factor is expressed as a percentage of the default size, where
        1.0 represents 100 percent.
        @version: LibVLC 4.0.0 or later.
        '''
        return libvlc_video_get_spu_text_scale(self)


    def video_set_spu_text_scale(self, f_scale):
        '''Set the subtitle text scale.
        The scale factor is expressed as a percentage of the default size, where
        1.0 represents 100 percent.
        A value of 0.5 would result in text half the normal size, and a value of 2.0
        would result in text twice the normal size.
        The minimum acceptable value for the scale factor is 0.1.
        The maximum is 5.0 (five times normal size).
        @param f_scale: scale factor in the range [0.1;5.0] (default: 1.0).
        @version: LibVLC 4.0.0 or later.
        '''
        return libvlc_video_set_spu_text_scale(self, f_scale)


    def video_set_spu_delay(self, i_delay):
        '''Set the subtitle delay. This affects the timing of when the subtitle will
        be displayed. Positive values result in subtitles being displayed later,
        while negative values will result in subtitles being displayed earlier.
        The subtitle delay will be reset to zero each time the media changes.
        @param i_delay: time (in microseconds) the display of subtitles should be delayed.
        @return: 0 on success, -1 on error.
        @version: LibVLC 2.0.0 or later.
        '''
        return libvlc_video_set_spu_delay(self, i_delay)


    def video_set_crop_ratio(self, num, den):
        '''Set/unset the video crop ratio.
        This function forces a crop ratio on any and all video tracks rendered by
        the media player. If the display aspect ratio of a video does not match the
        crop ratio, either the top and bottom, or the left and right of the video
        will be cut out to fit the crop ratio.
        For instance, a ratio of 1:1 will force the video to a square shape.
        To disable video crop, set a crop ratio with zero as denominator.
        A call to this function overrides any previous call to any of
        L{video_set_crop_ratio}(), L{video_set_crop_border}() and/or
        L{video_set_crop_window}().
        See L{video_set_aspect_ratio}().
        @param num: crop ratio numerator (ignored if denominator is 0).
        @param den: crop ratio denominator (or 0 to unset the crop ratio).
        @version: LibVLC 4.0.0 and later.
        '''
        return libvlc_video_set_crop_ratio(self, num, den)


    def video_set_crop_window(self, x, y, width, height):
        '''Set the video crop window.
        This function selects a sub-rectangle of video to show. Any pixels outside
        the rectangle will not be shown.
        To unset the video crop window, use L{video_set_crop_ratio}() or
        L{video_set_crop_border}().
        A call to this function overrides any previous call to any of
        L{video_set_crop_ratio}(), L{video_set_crop_border}() and/or
        L{video_set_crop_window}().
        @param x: abscissa (i.e. leftmost sample column offset) of the crop window.
        @param y: ordinate (i.e. topmost sample row offset) of the crop window.
        @param width: sample width of the crop window (cannot be zero).
        @param height: sample height of the crop window (cannot be zero).
        @version: LibVLC 4.0.0 and later.
        '''
        return libvlc_video_set_crop_window(self, x, y, width, height)


    def video_set_crop_border(self, left, right, top, bottom):
        '''Set the video crop borders.
        This function selects the size of video edges to be cropped out.
        To unset the video crop borders, set all borders to zero.
        A call to this function overrides any previous call to any of
        L{video_set_crop_ratio}(), L{video_set_crop_border}() and/or
        L{video_set_crop_window}().
        @param left: number of sample columns to crop on the left.
        @param right: number of sample columns to crop on the right.
        @param top: number of sample rows to crop on the top.
        @param bottom: number of sample rows to corp on the bottom.
        @version: LibVLC 4.0.0 and later.
        '''
        return libvlc_video_set_crop_border(self, left, right, top, bottom)


    def video_get_teletext(self):
        '''Get current teletext page requested or 0 if it's disabled.
        Teletext is disabled by default, call L{video_set_teletext}() to enable
        it.
        @return: the current teletext page requested.
        '''
        return libvlc_video_get_teletext(self)


    def video_set_teletext(self, i_page):
        '''Set new teletext page to retrieve.
        This function can also be used to send a teletext key.
        @param i_page: teletex page number requested. This value can be 0 to disable teletext, a number in the range ]0;1000[ to show the requested page, or a \ref L{TeletextKey}. 100 is the default teletext page.
        '''
        return libvlc_video_set_teletext(self, i_page)


    def video_take_snapshot(self, num, psz_filepath, i_width, i_height):
        '''Take a snapshot of the current video window.
        If i_width AND i_height is 0, original size is used.
        If i_width XOR i_height is 0, original aspect-ratio is preserved.
        @param num: number of video output (typically 0 for the first/only one).
        @param psz_filepath: the path of a file or a folder to save the screenshot into.
        @param i_width: the snapshot's width.
        @param i_height: the snapshot's height.
        @return: 0 on success, -1 if the video was not found.
        '''
        return libvlc_video_take_snapshot(self, num, str_to_bytes(psz_filepath), i_width, i_height)


    def video_set_deinterlace(self, deinterlace, psz_mode):
        '''Enable or disable deinterlace filter.
        @param deinterlace: state -1: auto (default), 0: disabled, 1: enabled.
        @param psz_mode: type of deinterlace filter, None for current/default filter.
        @version: LibVLC 4.0.0 and later.
        '''
        return libvlc_video_set_deinterlace(self, deinterlace, str_to_bytes(psz_mode))


    def video_get_marquee_int(self, option):
        '''Get an integer marquee option value.
        @param option: marq option to get See L{VideoMarqueeOption}.
        '''
        return libvlc_video_get_marquee_int(self, option)


    def video_set_marquee_int(self, option, i_val):
        '''Enable, disable or set an integer marquee option
        Setting libvlc_marquee_Enable has the side effect of enabling (arg !0)
        or disabling (arg 0) the marq filter.
        @param option: marq option to set See L{VideoMarqueeOption}.
        @param i_val: marq option value.
        '''
        return libvlc_video_set_marquee_int(self, option, i_val)


    def video_set_marquee_string(self, option, psz_text):
        '''Set a marquee string option.
        @param option: marq option to set See L{VideoMarqueeOption}.
        @param psz_text: marq option value.
        '''
        return libvlc_video_set_marquee_string(self, option, str_to_bytes(psz_text))


    def video_get_logo_int(self, option):
        '''Get integer logo option.
        @param option: logo option to get, values of L{VideoLogoOption}.
        '''
        return libvlc_video_get_logo_int(self, option)


    def video_set_logo_int(self, option, value):
        '''Set logo option as integer. Options that take a different type value
        are ignored.
        Passing libvlc_logo_enable as option value has the side effect of
        starting (arg !0) or stopping (arg 0) the logo filter.
        @param option: logo option to set, values of L{VideoLogoOption}.
        @param value: logo option value.
        '''
        return libvlc_video_set_logo_int(self, option, value)


    def video_set_logo_string(self, option, psz_value):
        '''Set logo option as string. Options that take a different type value
        are ignored.
        @param option: logo option to set, values of L{VideoLogoOption}.
        @param psz_value: logo option value.
        '''
        return libvlc_video_set_logo_string(self, option, str_to_bytes(psz_value))


    def video_get_adjust_int(self, option):
        '''Get integer adjust option.
        @param option: adjust option to get, values of L{VideoAdjustOption}.
        @version: LibVLC 1.1.1 and later.
        '''
        return libvlc_video_get_adjust_int(self, option)


    def video_set_adjust_int(self, option, value):
        '''Set adjust option as integer. Options that take a different type value
        are ignored.
        Passing libvlc_adjust_enable as option value has the side effect of
        starting (arg !0) or stopping (arg 0) the adjust filter.
        @param option: adust option to set, values of L{VideoAdjustOption}.
        @param value: adjust option value.
        @version: LibVLC 1.1.1 and later.
        '''
        return libvlc_video_set_adjust_int(self, option, value)


    def video_get_adjust_float(self, option):
        '''Get float adjust option.
        @param option: adjust option to get, values of L{VideoAdjustOption}.
        @version: LibVLC 1.1.1 and later.
        '''
        return libvlc_video_get_adjust_float(self, option)


    def video_set_adjust_float(self, option, value):
        '''Set adjust option as float. Options that take a different type value
        are ignored.
        @param option: adust option to set, values of L{VideoAdjustOption}.
        @param value: adjust option value.
        @version: LibVLC 1.1.1 and later.
        '''
        return libvlc_video_set_adjust_float(self, option, value)


    def audio_output_set(self, psz_name):
        '''Selects an audio output module.
        @note: Any change will take be effect only after playback is stopped and
        restarted. Audio output cannot be changed while playing.
        @param psz_name: name of audio output, use psz_name of See L{AudioOutput}.
        @return: 0 if function succeeded, -1 on error.
        '''
        return libvlc_audio_output_set(self, str_to_bytes(psz_name))


    def audio_output_device_enum(self):
        '''Gets a list of potential audio output devices.
        See also L{audio_output_device_set}().
        @note: Not all audio outputs support enumerating devices.
        The audio output may be functional even if the list is empty (None).
        @note: The list may not be exhaustive.
        @warning: Some audio output devices in the list might not actually work in
        some circumstances. By default, it is recommended to not specify any
        explicit audio device.
        @return: A None-terminated linked list of potential audio output devices. It must be freed with L{audio_output_device_list_release}().
        @version: LibVLC 2.2.0 or later.
        '''
        return libvlc_audio_output_device_enum(self)


    def audio_output_device_set(self, device_id):
        '''Configures an explicit audio output device.
        A list of adequate potential device strings can be obtained with
        L{audio_output_device_enum}().
        @note: This function does not select the specified audio output plugin.
        L{audio_output_set}() is used for that purpose.
        @warning: The syntax for the device parameter depends on the audio output.
        Some audio output modules require further parameters (e.g. a channels map
        in the case of ALSA).
        @param device_id: device identifier string (see \ref L{AudioOutputDevice}::psz_device).
        @return: If the change of device was requested succesfully, zero is returned (the actual change is asynchronous and not guaranteed to succeed). On error, a non-zero value is returned.
        @version: This function originally expected three parameters. The middle parameter was removed from LibVLC 4.0 onward.
        '''
        return libvlc_audio_output_device_set(self, str_to_bytes(device_id))


    def audio_output_device_get(self):
        '''Get the current audio output device identifier.
        This complements L{audio_output_device_set}().
        @warning: The initial value for the current audio output device identifier
        may not be set or may be some unknown value. A LibVLC application should
        compare this value against the known device identifiers (e.g. those that
        were previously retrieved by a call to L{audio_output_device_enum}) to
        find the current audio output device.
        It is possible that the selected audio output device changes (an external
        change) without a call to L{audio_output_device_set}. That may make this
        method unsuitable to use if a LibVLC application is attempting to track
        dynamic audio device changes as they happen.
        @return: the current audio output device identifier None if no device is selected or in case of error (the result must be released with free()).
        @version: LibVLC 3.0.0 or later.
        '''
        return libvlc_audio_output_device_get(self)


    def audio_toggle_mute(self):
        '''Toggle mute status.
        '''
        return libvlc_audio_toggle_mute(self)


    def audio_get_mute(self):
        '''Get current mute status.
        @return: the mute status (boolean) if defined, -1 if undefined/unapplicable.
        '''
        return libvlc_audio_get_mute(self)


    def audio_set_mute(self, status):
        '''Set mute status.
        @param status: If status is true then mute, otherwise unmute @warning This function does not always work. If there are no active audio playback stream, the mute status might not be available. If digital pass-through (S/PDIF, HDMI...) is in use, muting may be unapplicable. Also some audio output plugins do not support muting at all. @note To force silent playback, disable all audio tracks. This is more efficient and reliable than mute.
        '''
        return libvlc_audio_set_mute(self, status)


    def audio_get_volume(self):
        '''Get current software audio volume.
        @return: the software volume in percents (0 = mute, 100 = nominal / 0dB).
        '''
        return libvlc_audio_get_volume(self)


    def audio_set_volume(self, i_volume):
        '''Set current software audio volume.
        @param i_volume: the volume in percents (0 = mute, 100 = 0dB).
        @return: 0 if the volume was set, -1 if it was out of range.
        '''
        return libvlc_audio_set_volume(self, i_volume)


    def audio_get_stereomode(self):
        '''Get current audio stereo-mode.
        @return: the audio stereo-mode, See L{AudioOutputStereomode}.
        @version: LibVLC 4.0.0 or later.
        '''
        return libvlc_audio_get_stereomode(self)


    def audio_set_stereomode(self, mode):
        '''Set current audio stereo-mode.
        @param channel: the audio stereo-mode, See L{AudioOutputStereomode}.
        @return: 0 on success, -1 on error.
        @version: LibVLC 4.0.0 or later.
        '''
        return libvlc_audio_set_stereomode(self, mode)


    def audio_get_mixmode(self):
        '''Get current audio mix-mode.
        @return: the audio mix-mode, See L{AudioOutputMixmode}.
        @version: LibVLC 4.0.0 or later.
        '''
        return libvlc_audio_get_mixmode(self)


    def audio_set_mixmode(self, mode):
        '''Set current audio mix-mode.
        By default (libvlc_AudioMixMode_Unset), the audio output will keep its
        original channel configuration (play stereo as stereo, or 5.1 as 5.1). Yet,
        the OS and Audio API might refuse a channel configuration and asks VLC to
        adapt (Stereo played as 5.1 or vice-versa).
        This function allows to force a channel configuration, it will only work if
        the OS and Audio API accept this configuration (otherwise, it won't have any
        effects). Here are some examples:
         - Play multi-channels (5.1, 7.1...) as stereo (libvlc_AudioMixMode_Stereo)
         - Play Stereo or 5.1 as 7.1 (libvlc_AudioMixMode_7_1)
         - Play multi-channels as stereo with a binaural effect
         (libvlc_AudioMixMode_Binaural). It might be selected automatically if the
         OS and Audio API can detect if a headphone is plugged.
        @param channel: the audio mix-mode, See L{AudioOutputMixmode}.
        @return: 0 on success, -1 on error.
        @version: LibVLC 4.0.0 or later.
        '''
        return libvlc_audio_set_mixmode(self, mode)


    def audio_get_delay(self):
        '''Get current audio delay.
        @return: the audio delay (microseconds).
        @version: LibVLC 1.1.1 or later.
        '''
        return libvlc_audio_get_delay(self)


    def audio_set_delay(self, i_delay):
        '''Set current audio delay. The audio delay will be reset to zero each time the media changes.
        @param i_delay: the audio delay (microseconds).
        @return: 0 on success, -1 on error.
        @version: LibVLC 1.1.1 or later.
        '''
        return libvlc_audio_set_delay(self, i_delay)


    def set_equalizer(self, p_equalizer):
        '''Apply new equalizer settings to a media player.
        The equalizer is first created by invoking L{audio_equalizer_new}() or
        L{audio_equalizer_new_from_preset}().
        It is possible to apply new equalizer settings to a media player whether the media
        player is currently playing media or not.
        Invoking this method will immediately apply the new equalizer settings to the audio
        output of the currently playing media if there is any.
        If there is no currently playing media, the new equalizer settings will be applied
        later if and when new media is played.
        Equalizer settings will automatically be applied to subsequently played media.
        To disable the equalizer for a media player invoke this method passing None for the
        p_equalizer parameter.
        The media player does not keep a reference to the supplied equalizer so it is safe
        for an application to release the equalizer reference any time after this method
        returns.
        @param p_equalizer: opaque equalizer handle, or None to disable the equalizer for this media player.
        @return: zero on success, -1 on error.
        @version: LibVLC 2.2.0 or later.
        '''
        return libvlc_media_player_set_equalizer(self, p_equalizer)


    def get_role(self):
        '''Gets the media role.
        @return: the media player role (\ref libvlc_media_player_role_t).
        @version: LibVLC 3.0.0 and later.
        '''
        return libvlc_media_player_get_role(self)


    def set_role(self, role):
        '''Sets the media role.
        @param role: the media player role (\ref libvlc_media_player_role_t).
        @return: 0 on success, -1 on error.
        '''
        return libvlc_media_player_set_role(self, role)


    def record(self, enable, dir_path):
        '''Start/stop recording
        @note: The user should listen to the libvlc_MediaPlayerRecordChanged event,
        to monitor the recording state.
        @param enable: true to start recording, false to stop.
        @param dir_path: path of the recording directory or None (use default path), has only an effect when first enabling recording.
        @version: LibVLC 4.0.0 and later.
        '''
        return libvlc_media_player_record(self, enable, str_to_bytes(dir_path))


    def watch_time(self, min_period_us, on_update, on_discontinuity, cbs_data):
        '''Watch for times updates
        @warning: Only one watcher can be registered at a time. Calling this function
        a second time (if L{unwatch_time}() was not called
        in-between) will fail.
        @param min_period_us: corresponds to the minimum period, in us, between each updates, use it to avoid flood from too many source updates, set it to 0 to receive all updates.
        @param on_update: callback to listen to update events (must not be None).
        @param on_discontinuity: callback to listen to discontinuity events (can be be None).
        @param cbs_data: opaque pointer used by the callbacks.
        @return: 0 on success, -1 on error (allocation error, or if already watching).
        @version: LibVLC 4.0.0 or later.
        '''
        return libvlc_media_player_watch_time(self, min_period_us, on_update, on_discontinuity, cbs_data)


    def unwatch_time(self):
        '''Unwatch time updates.
        @version: LibVLC 4.0.0 or later.
        '''
        return libvlc_media_player_unwatch_time(self)

class Picture(_Ctype):
    '''N/A
    '''

    def __new__(cls, ptr=_internal_guard):
        '''(INTERNAL) ctypes wrapper constructor.
        '''
        return _Constructor(cls, ptr)

    def retain(self):
        '''Increment the reference count of this picture.
        See L{release}().
        '''
        return libvlc_picture_retain(self)


    def release(self):
        '''Decrement the reference count of this picture.
        When the reference count reaches 0, the picture will be released.
        The picture must not be accessed after calling this function.
        See L{retain}.
        '''
        return libvlc_picture_release(self)


    def save(self, path):
        '''Saves this picture to a file. The image format is the same as the one
        returned by \link L{type} \endlink.
        @param path: The path to the generated file.
        @return: 0 in case of success, -1 otherwise.
        '''
        return libvlc_picture_save(self, str_to_bytes(path))


    def get_buffer(self, size):
        '''Returns the image internal buffer, including potential padding.
        The L{Picture} owns the returned buffer, which must not be modified nor
        freed.
        @param size: A pointer to a size_t that will hold the size of the buffer [required].
        @return: A pointer to the internal buffer.
        '''
        return libvlc_picture_get_buffer(self, size)


    def type(self):
        '''Returns the picture type.
        '''
        return libvlc_picture_type(self)


    def get_stride(self):
        '''Returns the image stride, ie. the number of bytes per line.
        This can only be called on images of type libvlc_picture_Argb.
        '''
        return libvlc_picture_get_stride(self)


    def get_width(self):
        '''Returns the width of the image in pixels.
        '''
        return libvlc_picture_get_width(self)


    def get_height(self):
        '''Returns the height of the image in pixels.
        '''
        return libvlc_picture_get_height(self)


    def get_time(self):
        '''Returns the time at which this picture was generated, in milliseconds.
        '''
        return libvlc_picture_get_time(self)

class Renderer(_Ctype):
    '''N/A
    '''

    def __new__(cls, ptr=_internal_guard):
        '''(INTERNAL) ctypes wrapper constructor.
        '''
        return _Constructor(cls, ptr)

    def hold(self):
        '''Hold a renderer item, i.e. creates a new reference
        This functions need to called from the libvlc_RendererDiscovererItemAdded
        callback if the libvlc user wants to use this item after. (for display or
        for passing it to the mediaplayer for example).
        @return: the current item.
        @version: LibVLC 3.0.0 or later.
        '''
        return libvlc_renderer_item_hold(self)


    def release(self):
        '''Releases a renderer item, i.e. decrements its reference counter.
        @version: LibVLC 3.0.0 or later.
        '''
        return libvlc_renderer_item_release(self)


    def name(self):
        '''Get the human readable name of a renderer item.
        @return: the name of the item (can't be None, must *not* be freed).
        @version: LibVLC 3.0.0 or later.
        '''
        return libvlc_renderer_item_name(self)


    def type(self):
        '''Get the type (not translated) of a renderer item. For now, the type can only
        be "chromecast" ("upnp", "airplay" may come later).
        @return: the type of the item (can't be None, must *not* be freed).
        @version: LibVLC 3.0.0 or later.
        '''
        return libvlc_renderer_item_type(self)


    def icon_uri(self):
        '''Get the icon uri of a renderer item.
        @return: the uri of the item's icon (can be None, must *not* be freed).
        @version: LibVLC 3.0.0 or later.
        '''
        return libvlc_renderer_item_icon_uri(self)


    def flags(self):
        '''Get the flags of a renderer item
        See LIBVLC_RENDERER_CAN_AUDIO
        See LIBVLC_RENDERER_CAN_VIDEO.
        @return: bitwise flag: capabilities of the renderer, see.
        @version: LibVLC 3.0.0 or later.
        '''
        return libvlc_renderer_item_flags(self)

class RendererDiscoverer(_Ctype):
    '''N/A
    '''

    def __new__(cls, ptr=_internal_guard):
        '''(INTERNAL) ctypes wrapper constructor.
        '''
        return _Constructor(cls, ptr)

    def release(self):
        '''Release a renderer discoverer object.
        @version: LibVLC 3.0.0 or later.
        '''
        return libvlc_renderer_discoverer_release(self)


    def start(self):
        '''Start renderer discovery
        To stop it, call L{stop}() or
        L{release}() directly.
        See L{stop}().
        @return: -1 in case of error, 0 otherwise.
        @version: LibVLC 3.0.0 or later.
        '''
        return libvlc_renderer_discoverer_start(self)


    def stop(self):
        '''Stop renderer discovery.
        See L{start}().
        @version: LibVLC 3.0.0 or later.
        '''
        return libvlc_renderer_discoverer_stop(self)

    @memoize_parameterless
    def event_manager(self):
        '''Get the event manager of the renderer discoverer
        The possible events to attach are @ref libvlc_RendererDiscovererItemAdded
        and @ref libvlc_RendererDiscovererItemDeleted.
        The @ref L{Renderer} struct passed to event callbacks is owned by
        VLC, users should take care of holding/releasing this struct for their
        internal usage.
        See L{Event}.u.renderer_discoverer_item_added.item
        See L{Event}.u.renderer_discoverer_item_removed.item.
        @return: a valid event manager (can't fail).
        @version: LibVLC 3.0.0 or later.
        '''
        return libvlc_renderer_discoverer_event_manager(self)


 # LibVLC __version__ functions #

def libvlc_track_description_list_release(p_track_description):
    '''Release (free) L{TrackDescription}.
    @param p_track_description: the structure to release.
    '''
    f = _Cfunctions.get('libvlc_track_description_list_release', None) or \
        _Cfunction('libvlc_track_description_list_release', ((1,),), None,
                    None, ctypes.POINTER(TrackDescription))
    return f(p_track_description)

def libvlc_video_get_track_count(p_mi):
    '''Get number of available video tracks.
    @param p_mi: media player.
    @return: the number of available video tracks (int).
    '''
    f = _Cfunctions.get('libvlc_video_get_track_count', None) or \
        _Cfunction('libvlc_video_get_track_count', ((1,),), None,
                    ctypes.c_int, MediaPlayer)
    return f(p_mi)

def libvlc_video_get_track_description(p_mi):
    '''Get the description of available video tracks.
    @param p_mi: media player.
    @return: list with description of available video tracks, or None on error. It must be freed with L{libvlc_track_description_list_release}().
    '''
    f = _Cfunctions.get('libvlc_video_get_track_description', None) or \
        _Cfunction('libvlc_video_get_track_description', ((1,),), None,
                    ctypes.POINTER(TrackDescription), MediaPlayer)
    return f(p_mi)

def libvlc_video_get_track(p_mi):
    '''Get current video track.
    @param p_mi: media player.
    @return: the video track ID (int) or -1 if no active input.
    '''
    f = _Cfunctions.get('libvlc_video_get_track', None) or \
        _Cfunction('libvlc_video_get_track', ((1,),), None,
                    ctypes.c_int, MediaPlayer)
    return f(p_mi)

def libvlc_video_set_track(p_mi, i_track):
    '''Set video track.
    @param p_mi: media player.
    @param i_track: the track ID (i_id field from track description).
    @return: 0 on success, -1 if out of range.
    '''
    f = _Cfunctions.get('libvlc_video_set_track', None) or \
        _Cfunction('libvlc_video_set_track', ((1,), (1,),), None,
                    ctypes.c_int, MediaPlayer, ctypes.c_int)
    return f(p_mi, i_track)

def libvlc_video_get_spu(p_mi):
    '''Get current video subtitle.
    @param p_mi: the media player.
    @return: the video subtitle selected, or -1 if none.
    '''
    f = _Cfunctions.get('libvlc_video_get_spu', None) or \
        _Cfunction('libvlc_video_get_spu', ((1,),), None,
                    ctypes.c_int, MediaPlayer)
    return f(p_mi)

def libvlc_video_get_spu_count(p_mi):
    '''Get the number of available video subtitles.
    @param p_mi: the media player.
    @return: the number of available video subtitles.
    '''
    f = _Cfunctions.get('libvlc_video_get_spu_count', None) or \
        _Cfunction('libvlc_video_get_spu_count', ((1,),), None,
                    ctypes.c_int, MediaPlayer)
    return f(p_mi)

def libvlc_video_get_spu_description(p_mi):
    '''Get the description of available video subtitles.
    @param p_mi: the media player.
    @return: list containing description of available video subtitles. It must be freed with L{libvlc_track_description_list_release}().
    '''
    f = _Cfunctions.get('libvlc_video_get_spu_description', None) or \
        _Cfunction('libvlc_video_get_spu_description', ((1,),), None,
                    ctypes.POINTER(TrackDescription), MediaPlayer)
    return f(p_mi)

def libvlc_video_set_spu(p_mi, i_spu):
    '''Set new video subtitle.
    @param p_mi: the media player.
    @param i_spu: video subtitle track to select (i_id from track description).
    @return: 0 on success, -1 if out of range.
    '''
    f = _Cfunctions.get('libvlc_video_set_spu', None) or \
        _Cfunction('libvlc_video_set_spu', ((1,), (1,),), None,
                    ctypes.c_int, MediaPlayer, ctypes.c_int)
    return f(p_mi, i_spu)

def libvlc_audio_get_track_count(p_mi):
    '''Get number of available audio tracks.
    @param p_mi: media player.
    @return: the number of available audio tracks (int), or -1 if unavailable.
    '''
    f = _Cfunctions.get('libvlc_audio_get_track_count', None) or \
        _Cfunction('libvlc_audio_get_track_count', ((1,),), None,
                    ctypes.c_int, MediaPlayer)
    return f(p_mi)

def libvlc_audio_get_track_description(p_mi):
    '''Get the description of available audio tracks.
    @param p_mi: media player.
    @return: list with description of available audio tracks, or None. It must be freed with L{libvlc_track_description_list_release}().
    '''
    f = _Cfunctions.get('libvlc_audio_get_track_description', None) or \
        _Cfunction('libvlc_audio_get_track_description', ((1,),), None,
                    ctypes.POINTER(TrackDescription), MediaPlayer)
    return f(p_mi)

def libvlc_audio_get_track(p_mi):
    '''Get current audio track.
    @param p_mi: media player.
    @return: the audio track ID or -1 if no active input.
    '''
    f = _Cfunctions.get('libvlc_audio_get_track', None) or \
        _Cfunction('libvlc_audio_get_track', ((1,),), None,
                    ctypes.c_int, MediaPlayer)
    return f(p_mi)

def libvlc_audio_set_track(p_mi, i_track):
    '''Set current audio track.
    @param p_mi: media player.
    @param i_track: the track ID (i_id field from track description).
    @return: 0 on success, -1 on error.
    '''
    f = _Cfunctions.get('libvlc_audio_set_track', None) or \
        _Cfunction('libvlc_audio_set_track', ((1,), (1,),), None,
                    ctypes.c_int, MediaPlayer, ctypes.c_int)
    return f(p_mi, i_track)

def libvlc_playlist_play(p_instance):
    '''Start playing (if there is any item in the playlist).
    Additional playlist item options can be specified for addition to the
    item before it is played.
    @param p_instance: the playlist instance.
    '''
    f = _Cfunctions.get('libvlc_playlist_play', None) or \
        _Cfunction('libvlc_playlist_play', ((1,),), None,
                    None, Instance)
    return f(p_instance)

def libvlc_errmsg():
    '''A human-readable error message for the last LibVLC error in the calling
    thread. The resulting string is valid until another error occurs (at least
    until the next LibVLC call).
    @warning
    This will be None if there was no error.
    '''
    f = _Cfunctions.get('libvlc_errmsg', None) or \
        _Cfunction('libvlc_errmsg', (), None,
                    ctypes.c_char_p)
    return f()

def libvlc_clearerr():
    '''Clears the LibVLC error status for the current thread. This is optional.
    By default, the error status is automatically overridden when a new error
    occurs, and destroyed when the thread exits.
    '''
    f = _Cfunctions.get('libvlc_clearerr', None) or \
        _Cfunction('libvlc_clearerr', (), None,
                    None)
    return f()

def libvlc_new(argc, argv):
    '''Create and initialize a libvlc instance.
    This functions accept a list of "command line" arguments similar to the
    main(). These arguments affect the LibVLC instance default configuration.
    @note
    LibVLC may create threads. Therefore, any thread-unsafe process
    initialization must be performed before calling L{libvlc_new}(). In particular
    and where applicable:
    - setlocale() and textdomain(),
    - setenv(), unsetenv() and putenv(),
    - with the X11 display system, XInitThreads()
      (see also L{libvlc_media_player_set_xwindow}()) and
    - on Microsoft Windows, SetErrorMode().
    - sigprocmask() shall never be invoked; pthread_sigmask() can be used.
    On POSIX systems, the SIGCHLD signal B{must not} be ignored, i.e. the
    signal handler must set to SIG_DFL or a function pointer, not SIG_IGN.
    Also while LibVLC is active, the wait() function shall not be called, and
    any call to waitpid() shall use a strictly positive value for the first
    parameter (i.e. the PID). Failure to follow those rules may lead to a
    deadlock or a busy loop.
    Also on POSIX systems, it is recommended that the SIGPIPE signal be blocked,
    even if it is not, in principles, necessary, e.g.:
    @code
    @endcode
    On Microsoft Windows, setting the default DLL directories to SYSTEM32
    exclusively is strongly recommended for security reasons:
    @code
    @endcode.
    @param argc: the number of arguments (should be 0).
    @param argv: list of arguments (should be None).
    @return: the libvlc instance or None in case of error.
    @version Arguments are meant to be passed from the command line to LibVLC, just like VLC media player does. The list of valid arguments depends on the LibVLC version, the operating system and platform, and set of available LibVLC plugins. Invalid or unsupported arguments will cause the function to fail (i.e. return None). Also, some arguments may alter the behaviour or otherwise interfere with other LibVLC functions. @warning There is absolutely no warranty or promise of forward, backward and cross-platform compatibility with regards to L{libvlc_new}() arguments. We recommend that you do not use them, other than when debugging.
    '''
    f = _Cfunctions.get('libvlc_new', None) or \
        _Cfunction('libvlc_new', ((1,), (1,),), class_result(Instance),
                    ctypes.c_void_p, ctypes.c_int, ListPOINTER(ctypes.c_char_p))
    return f(argc, argv)

def libvlc_release(p_instance):
    '''Decrement the reference count of a libvlc instance, and destroy it
    if it reaches zero.
    @param p_instance: the instance to destroy.
    '''
    f = _Cfunctions.get('libvlc_release', None) or \
        _Cfunction('libvlc_release', ((1,),), None,
                    None, Instance)
    return f(p_instance)

def libvlc_retain(p_instance):
    '''Increments the reference count of a libvlc instance.
    The initial reference count is 1 after L{libvlc_new}() returns.
    @param p_instance: the instance to reference.
    '''
    f = _Cfunctions.get('libvlc_retain', None) or \
        _Cfunction('libvlc_retain', ((1,),), None,
                    None, Instance)
    return f(p_instance)

def libvlc_abi_version():
    '''Get the ABI version of the libvlc library.
    This is different than the VLC version, which is the version of the whole
    VLC package. The value is the same as LIBVLC_ABI_VERSION_INT used when
    compiling.
    @return: a value with the following mask in hexadecimal 0xFF000000: major VLC version, similar to VLC major version, 0x00FF0000: major ABI version, incremented incompatible changes are added, 0x0000FF00: minor ABI version, incremented when new functions are added 0x000000FF: micro ABI version, incremented with new release/builds @note This the same value as the .so version but cross platform.
    '''
    f = _Cfunctions.get('libvlc_abi_version', None) or \
        _Cfunction('libvlc_abi_version', (), None,
                    ctypes.c_int)
    return f()

def libvlc_add_intf(p_instance, name):
    '''Try to start a user interface for the libvlc instance.
    @param p_instance: the instance.
    @param name: interface name, or None for default.
    @return: 0 on success, -1 on error.
    '''
    f = _Cfunctions.get('libvlc_add_intf', None) or \
        _Cfunction('libvlc_add_intf', ((1,), (1,),), None,
                    ctypes.c_int, Instance, ctypes.c_char_p)
    return f(p_instance, name)

def libvlc_set_user_agent(p_instance, name, http):
    '''Sets the application name. LibVLC passes this as the user agent string
    when a protocol requires it.
    @param p_instance: LibVLC instance.
    @param name: human-readable application name, e.g. "FooBar player 1.2.3".
    @param http: HTTP User Agent, e.g. "FooBar/1.2.3 Python/2.6.0".
    @version: LibVLC 1.1.1 or later.
    '''
    f = _Cfunctions.get('libvlc_set_user_agent', None) or \
        _Cfunction('libvlc_set_user_agent', ((1,), (1,), (1,),), None,
                    None, Instance, ctypes.c_char_p, ctypes.c_char_p)
    return f(p_instance, name, http)

def libvlc_set_app_id(p_instance, id, version, icon):
    '''Sets some meta-information about the application.
    See also L{libvlc_set_user_agent}().
    @param p_instance: LibVLC instance.
    @param id: Java-style application identifier, e.g. "com.acme.foobar".
    @param version: application version numbers, e.g. "1.2.3".
    @param icon: application icon name, e.g. "foobar".
    @version: LibVLC 2.1.0 or later.
    '''
    f = _Cfunctions.get('libvlc_set_app_id', None) or \
        _Cfunction('libvlc_set_app_id', ((1,), (1,), (1,), (1,),), None,
                    None, Instance, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p)
    return f(p_instance, id, version, icon)

def libvlc_get_version():
    '''Retrieve libvlc version.
    Example: "1.1.0-git The Luggage".
    @return: a string containing the libvlc version.
    '''
    f = _Cfunctions.get('libvlc_get_version', None) or \
        _Cfunction('libvlc_get_version', (), None,
                    ctypes.c_char_p)
    return f()

def libvlc_get_compiler():
    '''Retrieve libvlc compiler version.
    Example: "gcc version 4.2.3 (Ubuntu 4.2.3-2ubuntu6)".
    @return: a string containing the libvlc compiler version.
    '''
    f = _Cfunctions.get('libvlc_get_compiler', None) or \
        _Cfunction('libvlc_get_compiler', (), None,
                    ctypes.c_char_p)
    return f()

def libvlc_get_changeset():
    '''Retrieve libvlc changeset.
    Example: "aa9bce0bc4".
    @return: a string containing the libvlc changeset.
    '''
    f = _Cfunctions.get('libvlc_get_changeset', None) or \
        _Cfunction('libvlc_get_changeset', (), None,
                    ctypes.c_char_p)
    return f()

def libvlc_free(ptr):
    '''Frees an heap allocation returned by a LibVLC function.
    If you know you're using the same underlying C run-time as the LibVLC
    implementation, then you can call ANSI C free() directly instead.
    @param ptr: the pointer.
    '''
    f = _Cfunctions.get('libvlc_free', None) or \
        _Cfunction('libvlc_free', ((1,),), None,
                    None, ctypes.c_void_p)
    return f(ptr)

def libvlc_event_attach(p_event_manager, i_event_type, f_callback, user_data):
    '''Register for an event notification.
    @param p_event_manager: the event manager to which you want to attach to. Generally it is obtained by vlc_my_object_event_manager() where my_object is the object you want to listen to.
    @param i_event_type: the desired event to which we want to listen.
    @param f_callback: the function to call when i_event_type occurs.
    @param user_data: user provided data to carry with the event.
    @return: 0 on success, ENOMEM on error.
    '''
    f = _Cfunctions.get('libvlc_event_attach', None) or \
        _Cfunction('libvlc_event_attach', ((1,), (1,), (1,), (1,),), None,
                    ctypes.c_int, EventManager, ctypes.c_uint, Callback, ctypes.c_void_p)
    return f(p_event_manager, i_event_type, f_callback, user_data)

def libvlc_event_detach(p_event_manager, i_event_type, f_callback, p_user_data):
    '''Unregister an event notification.
    @param p_event_manager: the event manager.
    @param i_event_type: the desired event to which we want to unregister.
    @param f_callback: the function to call when i_event_type occurs.
    @param p_user_data: user provided data to carry with the event.
    '''
    f = _Cfunctions.get('libvlc_event_detach', None) or \
        _Cfunction('libvlc_event_detach', ((1,), (1,), (1,), (1,),), None,
                    None, EventManager, ctypes.c_uint, Callback, ctypes.c_void_p)
    return f(p_event_manager, i_event_type, f_callback, p_user_data)

def libvlc_log_get_context(ctx):
    '''Gets log message debug infos.
    This function retrieves self-debug information about a log message:
    - the name of the VLC module emitting the message,
    - the name of the source code module (i.e. file) and
    - the line number within the source code module.
    The returned module name and file name will be None if unknown.
    The returned line number will similarly be zero if unknown.
    @param ctx: message context (as passed to the @ref L{LogCb} callback).
    @return: module module name storage (or None), file source code file name storage (or None), line source code file line number storage (or None).
    @version: LibVLC 2.1.0 or later.
    '''
    f = _Cfunctions.get('libvlc_log_get_context', None) or \
        _Cfunction('libvlc_log_get_context', ((1,), (2,), (2,), (2,),), None,
                    None, Log_ptr, ctypes.POINTER(ctypes.c_char_p), ctypes.POINTER(ctypes.c_char_p), ctypes.POINTER(ctypes.c_uint))
    return f(ctx)

def libvlc_log_get_object(ctx):
    '''Gets log message info.
    This function retrieves meta-information about a log message:
    - the type name of the VLC object emitting the message,
    - the object header if any, and
    - a temporaly-unique object identifier.
    This information is mainly meant for B{manual} troubleshooting.
    The returned type name may be "generic" if unknown, but it cannot be None.
    The returned header will be None if unset; in current versions, the header
    is used to distinguish for VLM inputs.
    The returned object ID will be zero if the message is not associated with
    any VLC object.
    @param ctx: message context (as passed to the @ref L{LogCb} callback).
    @return: name object name storage (or None), header object header (or None), id temporarily-unique object identifier (or 0).
    @version: LibVLC 2.1.0 or later.
    '''
    f = _Cfunctions.get('libvlc_log_get_object', None) or \
        _Cfunction('libvlc_log_get_object', ((1,), (2,), (2,), (2,),), None,
                    None, Log_ptr, ctypes.POINTER(ctypes.c_char_p), ctypes.POINTER(ctypes.c_char_p), ctypes.POINTER(ctypes.c_uint))
    return f(ctx)

def libvlc_log_unset(p_instance):
    '''Unsets the logging callback.
    This function deregisters the logging callback for a LibVLC instance.
    This is rarely needed as the callback is implicitly unset when the instance
    is destroyed.
    @note: This function will wait for any pending callbacks invocation to
    complete (causing a deadlock if called from within the callback).
    @param p_instance: libvlc instance.
    @version: LibVLC 2.1.0 or later.
    '''
    f = _Cfunctions.get('libvlc_log_unset', None) or \
        _Cfunction('libvlc_log_unset', ((1,),), None,
                    None, Instance)
    return f(p_instance)

def libvlc_log_set(p_instance, cb, data):
    '''Sets the logging callback for a LibVLC instance.
    This function is thread-safe: it will wait for any pending callbacks
    invocation to complete.
    @param cb: callback function pointer.
    @param data: opaque data pointer for the callback function @note Some log messages (especially debug) are emitted by LibVLC while is being initialized. These messages cannot be captured with this interface. @warning A deadlock may occur if this function is called from the callback.
    @param p_instance: libvlc instance.
    @version: LibVLC 2.1.0 or later.
    '''
    f = _Cfunctions.get('libvlc_log_set', None) or \
        _Cfunction('libvlc_log_set', ((1,), (1,), (1,),), None,
                    None, Instance, LogCb, ctypes.c_void_p)
    return f(p_instance, cb, data)

def libvlc_log_set_file(p_instance, stream):
    '''Sets up logging to a file.
    @param p_instance: libvlc instance.
    @param stream: FILE pointer opened for writing (the FILE pointer must remain valid until L{libvlc_log_unset}()).
    @version: LibVLC 2.1.0 or later.
    '''
    f = _Cfunctions.get('libvlc_log_set_file', None) or \
        _Cfunction('libvlc_log_set_file', ((1,), (1,),), None,
                    None, Instance, FILE_ptr)
    return f(p_instance, stream)

def libvlc_module_description_list_release(p_list):
    '''Release a list of module descriptions.
    @param p_list: the list to be released.
    '''
    f = _Cfunctions.get('libvlc_module_description_list_release', None) or \
        _Cfunction('libvlc_module_description_list_release', ((1,),), None,
                    None, ctypes.POINTER(ModuleDescription))
    return f(p_list)

def libvlc_audio_filter_list_get(p_instance):
    '''Returns a list of audio filters that are available.
    @param p_instance: libvlc instance.
    @return: a list of module descriptions. It should be freed with L{libvlc_module_description_list_release}(). In case of an error, None is returned. See L{ModuleDescription} See L{libvlc_module_description_list_release}.
    '''
    f = _Cfunctions.get('libvlc_audio_filter_list_get', None) or \
        _Cfunction('libvlc_audio_filter_list_get', ((1,),), None,
                    ctypes.POINTER(ModuleDescription), Instance)
    return f(p_instance)

def libvlc_video_filter_list_get(p_instance):
    '''Returns a list of video filters that are available.
    @param p_instance: libvlc instance.
    @return: a list of module descriptions. It should be freed with L{libvlc_module_description_list_release}(). In case of an error, None is returned. See L{ModuleDescription} See L{libvlc_module_description_list_release}.
    '''
    f = _Cfunctions.get('libvlc_video_filter_list_get', None) or \
        _Cfunction('libvlc_video_filter_list_get', ((1,),), None,
                    ctypes.POINTER(ModuleDescription), Instance)
    return f(p_instance)

def libvlc_clock():
    '''Return the current time as defined by LibVLC. The unit is the microsecond.
    Time increases monotonically (regardless of time zone changes and RTC
    adjustments).
    The origin is arbitrary but consistent across the whole system
    (e.g. the system uptime, the time since the system was booted).
    @note: On systems that support it, the POSIX monotonic clock is used.
    '''
    f = _Cfunctions.get('libvlc_clock', None) or \
        _Cfunction('libvlc_clock', (), None,
                    ctypes.c_int64)
    return f()

def libvlc_dialog_set_error_callback(p_instance, p_cbs, p_data):
    '''
    '''
    f = _Cfunctions.get('libvlc_dialog_set_error_callback', None) or \
        _Cfunction('libvlc_dialog_set_error_callback', ((1,), (1,), (1,),), None,
                    None, Instance, DialogErrorCbs, ctypes.c_void_p)
    return f(p_instance, p_cbs, p_data)

def libvlc_dialog_set_context(p_id, p_context):
    '''Associate an opaque pointer with the dialog id.
    @version: LibVLC 3.0.0 and later.
    '''
    f = _Cfunctions.get('libvlc_dialog_set_context', None) or \
        _Cfunction('libvlc_dialog_set_context', ((1,), (1,),), None,
                    None, ctypes.c_void_p, ctypes.c_void_p)
    return f(p_id, p_context)

def libvlc_dialog_get_context(p_id):
    '''Return the opaque pointer associated with the dialog id
    See L{libvlc_dialog_set_context}.
    @version: LibVLC 3.0.0 and later.
    '''
    f = _Cfunctions.get('libvlc_dialog_get_context', None) or \
        _Cfunction('libvlc_dialog_get_context', ((1,),), None,
                    ctypes.c_void_p, ctypes.c_void_p)
    return f(p_id)

def libvlc_dialog_post_login(p_id, psz_username, psz_password, b_store):
    '''Post a login answer
    After this call, p_id won't be valid anymore
    See L{DialogCbs}.pf_display_login.
    @param p_id: id of the dialog.
    @param psz_username: valid and non empty string.
    @param psz_password: valid string (can be empty).
    @param b_store: if true, store the credentials.
    @return: 0 on success, or -1 on error.
    @version: LibVLC 3.0.0 and later.
    '''
    f = _Cfunctions.get('libvlc_dialog_post_login', None) or \
        _Cfunction('libvlc_dialog_post_login', ((1,), (1,), (1,), (1,),), None,
                    ctypes.c_int, ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_bool)
    return f(p_id, psz_username, psz_password, b_store)

def libvlc_dialog_post_action(p_id, i_action):
    '''Post a question answer
    After this call, p_id won't be valid anymore
    See L{DialogCbs}.pf_display_question.
    @param p_id: id of the dialog.
    @param i_action: 1 for action1, 2 for action2.
    @return: 0 on success, or -1 on error.
    @version: LibVLC 3.0.0 and later.
    '''
    f = _Cfunctions.get('libvlc_dialog_post_action', None) or \
        _Cfunction('libvlc_dialog_post_action', ((1,), (1,),), None,
                    ctypes.c_int, ctypes.c_void_p, ctypes.c_int)
    return f(p_id, i_action)

def libvlc_dialog_dismiss(p_id):
    '''Dismiss a dialog
    After this call, p_id won't be valid anymore
    See L{DialogCbs}.pf_cancel.
    @param p_id: id of the dialog.
    @return: 0 on success, or -1 on error.
    @version: LibVLC 3.0.0 and later.
    '''
    f = _Cfunctions.get('libvlc_dialog_dismiss', None) or \
        _Cfunction('libvlc_dialog_dismiss', ((1,),), None,
                    ctypes.c_int, ctypes.c_void_p)
    return f(p_id)

def libvlc_media_new_location(psz_mrl):
    '''Create a media with a certain given media resource location,
    for instance a valid URL.
    @note: To refer to a local file with this function,
    the file://... URI syntax B{must} be used (see IETF RFC3986).
    We recommend using L{libvlc_media_new_path}() instead when dealing with
    local files.
    See L{libvlc_media_release}.
    @param psz_mrl: the media location.
    @return: the newly created media or None on error.
    '''
    f = _Cfunctions.get('libvlc_media_new_location', None) or \
        _Cfunction('libvlc_media_new_location', ((1,),), class_result(Media),
                    ctypes.c_void_p, ctypes.c_char_p)
    return f(psz_mrl)

def libvlc_media_new_path(path):
    '''Create a media for a certain file path.
    See L{libvlc_media_release}.
    @param path: local filesystem path.
    @return: the newly created media or None on error.
    '''
    f = _Cfunctions.get('libvlc_media_new_path', None) or \
        _Cfunction('libvlc_media_new_path', ((1,),), class_result(Media),
                    ctypes.c_void_p, ctypes.c_char_p)
    return f(path)

def libvlc_media_new_fd(fd):
    '''Create a media for an already open file descriptor.
    The file descriptor shall be open for reading (or reading and writing).
    Regular file descriptors, pipe read descriptors and character device
    descriptors (including TTYs) are supported on all platforms.
    Block device descriptors are supported where available.
    Directory descriptors are supported on systems that provide fdopendir().
    Sockets are supported on all platforms where they are file descriptors,
    i.e. all except Windows.
    @note: This library will B{not} automatically close the file descriptor
    under any circumstance. Nevertheless, a file descriptor can usually only be
    rendered once in a media player. To render it a second time, the file
    descriptor should probably be rewound to the beginning with lseek().
    See L{libvlc_media_release}.
    @param fd: open file descriptor.
    @return: the newly created media or None on error.
    @version: LibVLC 1.1.5 and later.
    '''
    f = _Cfunctions.get('libvlc_media_new_fd', None) or \
        _Cfunction('libvlc_media_new_fd', ((1,),), class_result(Media),
                    ctypes.c_void_p, ctypes.c_int)
    return f(fd)

def libvlc_media_new_callbacks(open_cb, read_cb, seek_cb, close_cb, opaque):
    '''Create a media with custom callbacks to read the data from.
    @param open_cb: callback to open the custom bitstream input media.
    @param read_cb: callback to read data (must not be None).
    @param seek_cb: callback to seek, or None if seeking is not supported.
    @param close_cb: callback to close the media, or None if unnecessary.
    @param opaque: data pointer for the open callback.
    @return: the newly created media or None on error @note If open_cb is None, the opaque pointer will be passed to read_cb, seek_cb and close_cb, and the stream size will be treated as unknown. @note The callbacks may be called asynchronously (from another thread). A single stream instance need not be reentrant. However the open_cb needs to be reentrant if the media is used by multiple player instances. @warning The callbacks may be used until all or any player instances that were supplied the media item are stopped. See L{libvlc_media_release}.
    @version: LibVLC 3.0.0 and later.
    '''
    f = _Cfunctions.get('libvlc_media_new_callbacks', None) or \
        _Cfunction('libvlc_media_new_callbacks', ((1,), (1,), (1,), (1,), (1,),), class_result(Media),
                    ctypes.c_void_p, MediaOpenCb, MediaReadCb, MediaSeekCb, MediaCloseCb, ctypes.c_void_p)
    return f(open_cb, read_cb, seek_cb, close_cb, opaque)

def libvlc_media_new_as_node(psz_name):
    '''Create a media as an empty node with a given name.
    See L{libvlc_media_release}.
    @param psz_name: the name of the node.
    @return: the new empty media or None on error.
    '''
    f = _Cfunctions.get('libvlc_media_new_as_node', None) or \
        _Cfunction('libvlc_media_new_as_node', ((1,),), class_result(Media),
                    ctypes.c_void_p, ctypes.c_char_p)
    return f(psz_name)

def libvlc_media_add_option(p_md, psz_options):
    '''Add an option to the media.
    This option will be used to determine how the media_player will
    read the media. This allows to use VLC's advanced
    reading/streaming options on a per-media basis.
    @note: The options are listed in 'vlc --longhelp' from the command line,
    e.g. "--sout-all". Keep in mind that available options and their semantics
    vary across LibVLC versions and builds.
    @warning: Not all options affects L{Media} objects:
    Specifically, due to architectural issues most audio and video options,
    such as text renderer options, have no effects on an individual media.
    These options must be set through L{libvlc_new}() instead.
    @param p_md: the media descriptor.
    @param psz_options: the options (as a string).
    '''
    f = _Cfunctions.get('libvlc_media_add_option', None) or \
        _Cfunction('libvlc_media_add_option', ((1,), (1,),), None,
                    None, Media, ctypes.c_char_p)
    return f(p_md, psz_options)

def libvlc_media_add_option_flag(p_md, psz_options, i_flags):
    '''Add an option to the media with configurable flags.
    This option will be used to determine how the media_player will
    read the media. This allows to use VLC's advanced
    reading/streaming options on a per-media basis.
    The options are detailed in vlc --longhelp, for instance
    "--sout-all". Note that all options are not usable on medias:
    specifically, due to architectural issues, video-related options
    such as text renderer options cannot be set on a single media. They
    must be set on the whole libvlc instance instead.
    @param p_md: the media descriptor.
    @param psz_options: the options (as a string).
    @param i_flags: the flags for this option.
    '''
    f = _Cfunctions.get('libvlc_media_add_option_flag', None) or \
        _Cfunction('libvlc_media_add_option_flag', ((1,), (1,), (1,),), None,
                    None, Media, ctypes.c_char_p, ctypes.c_uint)
    return f(p_md, psz_options, i_flags)

def libvlc_media_retain(p_md):
    '''Retain a reference to a media descriptor object (L{Media}). Use
    L{libvlc_media_release}() to decrement the reference count of a
    media descriptor object.
    @param p_md: the media descriptor.
    '''
    f = _Cfunctions.get('libvlc_media_retain', None) or \
        _Cfunction('libvlc_media_retain', ((1,),), None,
                    None, Media)
    return f(p_md)

def libvlc_media_release(p_md):
    '''Decrement the reference count of a media descriptor object. If the
    reference count is 0, then L{libvlc_media_release}() will release the
    media descriptor object. If the media descriptor object has been released it
    should not be used again.
    @param p_md: the media descriptor.
    '''
    f = _Cfunctions.get('libvlc_media_release', None) or \
        _Cfunction('libvlc_media_release', ((1,),), None,
                    None, Media)
    return f(p_md)

def libvlc_media_get_mrl(p_md):
    '''Get the media resource locator (mrl) from a media descriptor object.
    @param p_md: a media descriptor object.
    @return: string with mrl of media descriptor object.
    '''
    f = _Cfunctions.get('libvlc_media_get_mrl', None) or \
        _Cfunction('libvlc_media_get_mrl', ((1,),), string_result,
                    ctypes.c_void_p, Media)
    return f(p_md)

def libvlc_media_duplicate(p_md):
    '''Duplicate a media descriptor object.
    @warning: the duplicated media won't share forthcoming updates from the
    original one.
    @param p_md: a media descriptor object.
    '''
    f = _Cfunctions.get('libvlc_media_duplicate', None) or \
        _Cfunction('libvlc_media_duplicate', ((1,),), class_result(Media),
                    ctypes.c_void_p, Media)
    return f(p_md)

def libvlc_media_get_meta(p_md, e_meta):
    '''Read the meta of the media.
    Note, you need to call L{libvlc_media_parse_request}() or play the media
    at least once before calling this function.
    If the media has not yet been parsed this will return None.
    See libvlc_MediaMetaChanged.
    @param p_md: the media descriptor.
    @param e_meta: the meta to read.
    @return: the media's meta.
    '''
    f = _Cfunctions.get('libvlc_media_get_meta', None) or \
        _Cfunction('libvlc_media_get_meta', ((1,), (1,),), string_result,
                    ctypes.c_void_p, Media, Meta)
    return f(p_md, e_meta)

def libvlc_media_set_meta(p_md, e_meta, psz_value):
    '''Set the meta of the media (this function will not save the meta, call
    L{libvlc_media_save_meta} in order to save the meta).
    @param p_md: the media descriptor.
    @param e_meta: the meta to write.
    @param psz_value: the media's meta.
    '''
    f = _Cfunctions.get('libvlc_media_set_meta', None) or \
        _Cfunction('libvlc_media_set_meta', ((1,), (1,), (1,),), None,
                    None, Media, Meta, ctypes.c_char_p)
    return f(p_md, e_meta, psz_value)

def libvlc_media_save_meta(inst, p_md):
    '''Save the meta previously set.
    @param inst: LibVLC instance.
    @param p_md: the media descriptor.
    @return: true if the write operation was successful.
    '''
    f = _Cfunctions.get('libvlc_media_save_meta', None) or \
        _Cfunction('libvlc_media_save_meta', ((1,), (1,),), None,
                    ctypes.c_int, Instance, Media)
    return f(inst, p_md)

def libvlc_media_get_stats(p_md, p_stats):
    '''Get the current statistics about the media.
    @param p_md: media descriptor object.
    @param p_stats: structure that contain the statistics about the media (this structure must be allocated by the caller) \retval true statistics are available \retval false otherwise.
    '''
    f = _Cfunctions.get('libvlc_media_get_stats', None) or \
        _Cfunction('libvlc_media_get_stats', ((1,), (1,),), None,
                    ctypes.c_bool, Media, ctypes.POINTER(MediaStats))
    return f(p_md, p_stats)

def libvlc_media_subitems(p_md):
    '''Get subitems of media descriptor object. This will increment
    the reference count of supplied media descriptor object. Use
    L{libvlc_media_list_release}() to decrement the reference counting.
    @param p_md: media descriptor object.
    @return: list of media descriptor subitems or None.
    '''
    f = _Cfunctions.get('libvlc_media_subitems', None) or \
        _Cfunction('libvlc_media_subitems', ((1,),), class_result(MediaList),
                    ctypes.c_void_p, Media)
    return f(p_md)

def libvlc_media_event_manager(p_md):
    '''Get event manager from media descriptor object.
    NOTE: this function doesn't increment reference counting.
    @param p_md: a media descriptor object.
    @return: event manager object.
    '''
    f = _Cfunctions.get('libvlc_media_event_manager', None) or \
        _Cfunction('libvlc_media_event_manager', ((1,),), class_result(EventManager),
                    ctypes.c_void_p, Media)
    return f(p_md)

def libvlc_media_get_duration(p_md):
    '''Get duration (in ms) of media descriptor object item.
    Note, you need to call L{libvlc_media_parse_request}() or play the media
    at least once before calling this function.
    Not doing this will result in an undefined result.
    @param p_md: media descriptor object.
    @return: duration of media item or -1 on error.
    '''
    f = _Cfunctions.get('libvlc_media_get_duration', None) or \
        _Cfunction('libvlc_media_get_duration', ((1,),), None,
                    ctypes.c_longlong, Media)
    return f(p_md)

def libvlc_media_get_filestat(p_md, type, out):
    '''Get a 'stat' value of media descriptor object item.
    @note: 'stat' values are currently only parsed by directory accesses. This
    mean that only sub medias of a directory media, parsed with
    L{libvlc_media_parse_request}() can have valid 'stat' properties.
    @param p_md: media descriptor object.
    @param type: a valid libvlc_media_stat_ define.
    @param out: field in which the value will be stored.
    @return: 1 on success, 0 if not found, -1 on error.
    @version: LibVLC 4.0.0 and later.
    '''
    f = _Cfunctions.get('libvlc_media_get_filestat', None) or \
        _Cfunction('libvlc_media_get_filestat', ((1,), (1,), (1,),), None,
                    ctypes.c_int, Media, ctypes.c_uint, ctypes.POINTER(ctypes.c_uint64))
    return f(p_md, type, out)

def libvlc_media_parse_request(inst, p_md, parse_flag, timeout):
    '''Parse the media asynchronously with options.
    This fetches (local or network) art, meta data and/or tracks information.
    To track when this is over you can listen to libvlc_MediaParsedChanged
    event. However if this functions returns an error, you will not receive any
    events.
    It uses a flag to specify parse options (see L{MediaParseFlag}). All
    these flags can be combined. By default, media is parsed if it's a local
    file.
    @note: Parsing can be aborted with L{libvlc_media_parse_stop}().
    See libvlc_MediaParsedChanged
    See L{libvlc_media_get_meta}
    See L{libvlc_media_get_tracklist}
    See L{libvlc_media_get_parsed_status}
    See L{MediaParseFlag}.
    @param inst: LibVLC instance that is to parse the media.
    @param p_md: media descriptor object.
    @param parse_flag: parse options:
    @param timeout: maximum time allowed to preparse the media. If -1, the default "preparse-timeout" option will be used as a timeout. If 0, it will wait indefinitely. If > 0, the timeout will be used (in milliseconds).
    @return: -1 in case of error, 0 otherwise.
    @version: LibVLC 4.0.0 or later.
    '''
    f = _Cfunctions.get('libvlc_media_parse_request', None) or \
        _Cfunction('libvlc_media_parse_request', ((1,), (1,), (1,), (1,),), None,
                    ctypes.c_int, Instance, Media, MediaParseFlag, ctypes.c_int)
    return f(inst, p_md, parse_flag, timeout)

def libvlc_media_parse_stop(inst, p_md):
    '''Stop the parsing of the media
    When the media parsing is stopped, the libvlc_MediaParsedChanged event will
    be sent with the libvlc_media_parsed_status_timeout status.
    See L{libvlc_media_parse_request}().
    @param inst: LibVLC instance that is to cease or give up parsing the media.
    @param p_md: media descriptor object.
    @version: LibVLC 3.0.0 or later.
    '''
    f = _Cfunctions.get('libvlc_media_parse_stop', None) or \
        _Cfunction('libvlc_media_parse_stop', ((1,), (1,),), None,
                    None, Instance, Media)
    return f(inst, p_md)

def libvlc_media_get_parsed_status(p_md):
    '''Get Parsed status for media descriptor object.
    See libvlc_MediaParsedChanged
    See L{MediaParsedStatus}
    See L{libvlc_media_parse_request}().
    @param p_md: media descriptor object.
    @return: a value of the L{MediaParsedStatus} enum.
    @version: LibVLC 3.0.0 or later.
    '''
    f = _Cfunctions.get('libvlc_media_get_parsed_status', None) or \
        _Cfunction('libvlc_media_get_parsed_status', ((1,),), None,
                    MediaParsedStatus, Media)
    return f(p_md)

def libvlc_media_set_user_data(p_md, p_new_user_data):
    '''Sets media descriptor's user_data. user_data is specialized data
    accessed by the host application, VLC.framework uses it as a pointer to
    an native object that references a L{Media} pointer.
    @param p_md: media descriptor object.
    @param p_new_user_data: pointer to user data.
    '''
    f = _Cfunctions.get('libvlc_media_set_user_data', None) or \
        _Cfunction('libvlc_media_set_user_data', ((1,), (1,),), None,
                    None, Media, ctypes.c_void_p)
    return f(p_md, p_new_user_data)

def libvlc_media_get_user_data(p_md):
    '''Get media descriptor's user_data. user_data is specialized data
    accessed by the host application, VLC.framework uses it as a pointer to
    an native object that references a L{Media} pointer
    See L{libvlc_media_set_user_data}.
    @param p_md: media descriptor object.
    '''
    f = _Cfunctions.get('libvlc_media_get_user_data', None) or \
        _Cfunction('libvlc_media_get_user_data', ((1,),), None,
                    ctypes.c_void_p, Media)
    return f(p_md)

def libvlc_media_get_tracklist(p_md, type):
    '''Get the track list for one type.
    @param p_md: media descriptor object.
    @param type: type of the track list to request.
    @return: a valid libvlc_media_tracklist_t or None in case of error, if there is no track for a category, the returned list will have a size of 0, delete with L{libvlc_media_tracklist_delete}().
    @version: LibVLC 4.0.0 and later. @note You need to call L{libvlc_media_parse_request}() or play the media at least once before calling this function.  Not doing this will result in an empty list. See L{libvlc_media_tracklist_count} See L{libvlc_media_tracklist_at}.
    '''
    f = _Cfunctions.get('libvlc_media_get_tracklist', None) or \
        _Cfunction('libvlc_media_get_tracklist', ((1,), (1,),), None,
                    ctypes.c_void_p, Media, TrackType)
    return f(p_md, type)

def libvlc_media_get_codec_description(i_type, i_codec):
    '''Get codec description from media elementary stream
    Note, you need to call L{libvlc_media_parse_request}() or play the media
    at least once before calling this function.
    @param i_type: i_type from L{MediaTrack}.
    @param i_codec: i_codec or i_original_fourcc from L{MediaTrack}.
    @return: codec description.
    @version: LibVLC 3.0.0 and later. See L{MediaTrack}.
    '''
    f = _Cfunctions.get('libvlc_media_get_codec_description', None) or \
        _Cfunction('libvlc_media_get_codec_description', ((1,), (1,),), None,
                    ctypes.c_char_p, TrackType, ctypes.c_uint32)
    return f(i_type, i_codec)

def libvlc_media_get_type(p_md):
    '''Get the media type of the media descriptor object.
    @param p_md: media descriptor object.
    @return: media type.
    @version: LibVLC 3.0.0 and later. See L{MediaType}.
    '''
    f = _Cfunctions.get('libvlc_media_get_type', None) or \
        _Cfunction('libvlc_media_get_type', ((1,),), None,
                    MediaType, Media)
    return f(p_md)

def libvlc_media_thumbnail_request_by_time(inst, md, time, speed, width, height, crop, picture_type, timeout):
    '''\brief libvlc_media_request_thumbnail_by_time Start an asynchronous thumbnail generation
    If the request is successfully queued, the libvlc_MediaThumbnailGenerated
    is guaranteed to be emitted.
    The resulting thumbnail size can either be:
    - Hardcoded by providing both width & height. In which case, the image will
      be stretched to match the provided aspect ratio, or cropped if crop is true.
    - Derived from the media aspect ratio if only width or height is provided and
      the other one is set to 0.
    @param inst: LibVLC instance to generate the thumbnail with.
    @param md: media descriptor object.
    @param time: The time at which the thumbnail should be generated.
    @param speed: The seeking speed \saL{ThumbnailerSeekSpeed}.
    @param width: The thumbnail width.
    @param height: the thumbnail height.
    @param crop: Should the picture be cropped to preserve source aspect ratio.
    @param picture_type: The thumbnail picture type \saL{PictureType}.
    @param timeout: A timeout value in ms, or 0 to disable timeout.
    @return: A valid opaque request object, or None in case of failure. It may be cancelled by L{libvlc_media_thumbnail_request_cancel}(). It must be released by L{libvlc_media_thumbnail_request_destroy}().
    @version: libvlc 4.0 or later See L{Picture} See L{PictureType}.
    '''
    f = _Cfunctions.get('libvlc_media_thumbnail_request_by_time', None) or \
        _Cfunction('libvlc_media_thumbnail_request_by_time', ((1,), (1,), (1,), (1,), (1,), (1,), (1,), (1,), (1,),), None,
                    MediaThumbnailRequest, Instance, Media, ctypes.c_longlong, ThumbnailerSeekSpeed, ctypes.c_uint, ctypes.c_uint, ctypes.c_bool, PictureType, ctypes.c_longlong)
    return f(inst, md, time, speed, width, height, crop, picture_type, timeout)

def libvlc_media_thumbnail_request_by_pos(inst, md, pos, speed, width, height, crop, picture_type, timeout):
    '''\brief libvlc_media_request_thumbnail_by_pos Start an asynchronous thumbnail generation
    If the request is successfully queued, the libvlc_MediaThumbnailGenerated
    is guaranteed to be emitted.
    The resulting thumbnail size can either be:
    - Hardcoded by providing both width & height. In which case, the image will
      be stretched to match the provided aspect ratio, or cropped if crop is true.
    - Derived from the media aspect ratio if only width or height is provided and
      the other one is set to 0.
    @param inst: LibVLC instance to generate the thumbnail with.
    @param md: media descriptor object.
    @param pos: The position at which the thumbnail should be generated.
    @param speed: The seeking speed \saL{ThumbnailerSeekSpeed}.
    @param width: The thumbnail width.
    @param height: the thumbnail height.
    @param crop: Should the picture be cropped to preserve source aspect ratio.
    @param picture_type: The thumbnail picture type \saL{PictureType}.
    @param timeout: A timeout value in ms, or 0 to disable timeout.
    @return: A valid opaque request object, or None in case of failure. It may be cancelled by L{libvlc_media_thumbnail_request_cancel}(). It must be released by L{libvlc_media_thumbnail_request_destroy}().
    @version: libvlc 4.0 or later See L{Picture} See L{PictureType}.
    '''
    f = _Cfunctions.get('libvlc_media_thumbnail_request_by_pos', None) or \
        _Cfunction('libvlc_media_thumbnail_request_by_pos', ((1,), (1,), (1,), (1,), (1,), (1,), (1,), (1,), (1,),), None,
                    MediaThumbnailRequest, Instance, Media, ctypes.c_double, ThumbnailerSeekSpeed, ctypes.c_uint, ctypes.c_uint, ctypes.c_bool, PictureType, ctypes.c_longlong)
    return f(inst, md, pos, speed, width, height, crop, picture_type, timeout)

def libvlc_media_thumbnail_request_cancel(p_req):
    '''@brief libvlc_media_thumbnail_cancel cancels a thumbnailing request.
    @param p_req: An opaque thumbnail request object. Cancelling the request will still cause libvlc_MediaThumbnailGenerated event to be emitted, with a None L{Picture} If the request is cancelled after its completion, the behavior is undefined.
    '''
    f = _Cfunctions.get('libvlc_media_thumbnail_request_cancel', None) or \
        _Cfunction('libvlc_media_thumbnail_request_cancel', ((1,),), None,
                    None, MediaThumbnailRequest)
    return f(p_req)

def libvlc_media_thumbnail_request_destroy(p_req):
    '''@brief libvlc_media_thumbnail_destroy destroys a thumbnail request.
    @param p_req: An opaque thumbnail request object. If the request has not completed or hasn't been cancelled yet, the behavior is undefined.
    '''
    f = _Cfunctions.get('libvlc_media_thumbnail_request_destroy', None) or \
        _Cfunction('libvlc_media_thumbnail_request_destroy', ((1,),), None,
                    None, MediaThumbnailRequest)
    return f(p_req)

def libvlc_media_slaves_add(p_md, i_type, i_priority, psz_uri):
    '''Add a slave to the current media.
    A slave is an external input source that may contains an additional subtitle
    track (like a .srt) or an additional audio track (like a .ac3).
    @note: This function must be called before the media is parsed (via
    L{libvlc_media_parse_request}()) or before the media is played (via
    L{libvlc_media_player_play}()).
    @param p_md: media descriptor object.
    @param i_type: subtitle or audio.
    @param i_priority: from 0 (low priority) to 4 (high priority).
    @param psz_uri: Uri of the slave (should contain a valid scheme).
    @return: 0 on success, -1 on error.
    @version: LibVLC 3.0.0 and later.
    '''
    f = _Cfunctions.get('libvlc_media_slaves_add', None) or \
        _Cfunction('libvlc_media_slaves_add', ((1,), (1,), (1,), (1,),), None,
                    ctypes.c_int, Media, MediaSlaveType, ctypes.c_uint, ctypes.c_char_p)
    return f(p_md, i_type, i_priority, psz_uri)

def libvlc_media_slaves_clear(p_md):
    '''Clear all slaves previously added by L{libvlc_media_slaves_add}() or
    internally.
    @param p_md: media descriptor object.
    @version: LibVLC 3.0.0 and later.
    '''
    f = _Cfunctions.get('libvlc_media_slaves_clear', None) or \
        _Cfunction('libvlc_media_slaves_clear', ((1,),), None,
                    None, Media)
    return f(p_md)

def libvlc_media_slaves_get(p_md, ppp_slaves):
    '''Get a media descriptor's slave list
    The list will contain slaves parsed by VLC or previously added by
    L{libvlc_media_slaves_add}(). The typical use case of this function is to save
    a list of slave in a database for a later use.
    @param p_md: media descriptor object.
    @param ppp_slaves: address to store an allocated array of slaves (must be freed with L{libvlc_media_slaves_release}()) [OUT].
    @return: the number of slaves (zero on error).
    @version: LibVLC 3.0.0 and later. See L{libvlc_media_slaves_add}.
    '''
    f = _Cfunctions.get('libvlc_media_slaves_get', None) or \
        _Cfunction('libvlc_media_slaves_get', ((1,), (1,),), None,
                    ctypes.c_uint, Media, ctypes.POINTER(ctypes.POINTER(MediaSlave)))
    return f(p_md, ppp_slaves)

def libvlc_media_slaves_release(pp_slaves, i_count):
    '''Release a media descriptor's slave list.
    @param pp_slaves: slave array to release.
    @param i_count: number of elements in the array.
    @version: LibVLC 3.0.0 and later.
    '''
    f = _Cfunctions.get('libvlc_media_slaves_release', None) or \
        _Cfunction('libvlc_media_slaves_release', ((1,), (1,),), None,
                    None, ctypes.POINTER(ctypes.POINTER(MediaSlave)), ctypes.c_uint)
    return f(pp_slaves, i_count)

def libvlc_media_discoverer_new(p_inst, psz_name):
    '''Create a media discoverer object by name.
    After this object is created, you should attach to media_list events in
    order to be notified of new items discovered.
    You need to call L{libvlc_media_discoverer_start}() in order to start the
    discovery.
    See L{libvlc_media_discoverer_media_list}
    See L{libvlc_media_discoverer_start}.
    @param p_inst: libvlc instance.
    @param psz_name: service name; use L{libvlc_media_discoverer_list_get}() to get a list of the discoverer names available in this libVLC instance.
    @return: media discover object or None in case of error.
    @version: LibVLC 3.0.0 or later.
    '''
    f = _Cfunctions.get('libvlc_media_discoverer_new', None) or \
        _Cfunction('libvlc_media_discoverer_new', ((1,), (1,),), class_result(MediaDiscoverer),
                    ctypes.c_void_p, Instance, ctypes.c_char_p)
    return f(p_inst, psz_name)

def libvlc_media_discoverer_start(p_mdis):
    '''Start media discovery.
    To stop it, call L{libvlc_media_discoverer_stop}() or
    L{libvlc_media_discoverer_list_release}() directly.
    See L{libvlc_media_discoverer_stop}.
    @param p_mdis: media discover object.
    @return: -1 in case of error, 0 otherwise.
    @version: LibVLC 3.0.0 or later.
    '''
    f = _Cfunctions.get('libvlc_media_discoverer_start', None) or \
        _Cfunction('libvlc_media_discoverer_start', ((1,),), None,
                    ctypes.c_int, MediaDiscoverer)
    return f(p_mdis)

def libvlc_media_discoverer_stop(p_mdis):
    '''Stop media discovery.
    See L{libvlc_media_discoverer_start}.
    @param p_mdis: media discover object.
    @version: LibVLC 3.0.0 or later.
    '''
    f = _Cfunctions.get('libvlc_media_discoverer_stop', None) or \
        _Cfunction('libvlc_media_discoverer_stop', ((1,),), None,
                    None, MediaDiscoverer)
    return f(p_mdis)

def libvlc_media_discoverer_release(p_mdis):
    '''Release media discover object. If the reference count reaches 0, then
    the object will be released.
    @param p_mdis: media service discover object.
    '''
    f = _Cfunctions.get('libvlc_media_discoverer_release', None) or \
        _Cfunction('libvlc_media_discoverer_release', ((1,),), None,
                    None, MediaDiscoverer)
    return f(p_mdis)

def libvlc_media_discoverer_media_list(p_mdis):
    '''Get media service discover media list.
    @param p_mdis: media service discover object.
    @return: list of media items.
    '''
    f = _Cfunctions.get('libvlc_media_discoverer_media_list', None) or \
        _Cfunction('libvlc_media_discoverer_media_list', ((1,),), class_result(MediaList),
                    ctypes.c_void_p, MediaDiscoverer)
    return f(p_mdis)

def libvlc_media_discoverer_is_running(p_mdis):
    '''Query if media service discover object is running.
    @param p_mdis: media service discover object \retval true running \retval false not running.
    '''
    f = _Cfunctions.get('libvlc_media_discoverer_is_running', None) or \
        _Cfunction('libvlc_media_discoverer_is_running', ((1,),), None,
                    ctypes.c_bool, MediaDiscoverer)
    return f(p_mdis)

def libvlc_media_discoverer_list_get(p_inst, i_cat, ppp_services):
    '''Get media discoverer services by category.
    @param p_inst: libvlc instance.
    @param i_cat: category of services to fetch.
    @param ppp_services: address to store an allocated array of media discoverer services (must be freed with L{libvlc_media_discoverer_list_release}() by the caller) [OUT].
    @return: the number of media discoverer services (0 on error).
    @version: LibVLC 3.0.0 and later.
    '''
    f = _Cfunctions.get('libvlc_media_discoverer_list_get', None) or \
        _Cfunction('libvlc_media_discoverer_list_get', ((1,), (1,), (1,),), None,
                    ctypes.c_size_t, Instance, MediaDiscovererCategory, ctypes.POINTER(ctypes.POINTER(ctypes.POINTER(MediaDiscovererDescription))))
    return f(p_inst, i_cat, ppp_services)

def libvlc_media_discoverer_list_release(pp_services, i_count):
    '''Release an array of media discoverer services.
    @param pp_services: array to release.
    @param i_count: number of elements in the array.
    @version: LibVLC 3.0.0 and later. See L{libvlc_media_discoverer_list_get}().
    '''
    f = _Cfunctions.get('libvlc_media_discoverer_list_release', None) or \
        _Cfunction('libvlc_media_discoverer_list_release', ((1,), (1,),), None,
                    None, ctypes.POINTER(ctypes.POINTER(MediaDiscovererDescription)), ctypes.c_size_t)
    return f(pp_services, i_count)

def libvlc_media_list_new():
    '''Create an empty media list.
    @return: empty media list, or None on error.
    '''
    f = _Cfunctions.get('libvlc_media_list_new', None) or \
        _Cfunction('libvlc_media_list_new', (), class_result(MediaList),
                    ctypes.c_void_p)
    return f()

def libvlc_media_list_release(p_ml):
    '''Release media list created with L{libvlc_media_list_new}().
    @param p_ml: a media list created with L{libvlc_media_list_new}().
    '''
    f = _Cfunctions.get('libvlc_media_list_release', None) or \
        _Cfunction('libvlc_media_list_release', ((1,),), None,
                    None, MediaList)
    return f(p_ml)

def libvlc_media_list_retain(p_ml):
    '''Retain reference to a media list.
    @param p_ml: a media list created with L{libvlc_media_list_new}().
    '''
    f = _Cfunctions.get('libvlc_media_list_retain', None) or \
        _Cfunction('libvlc_media_list_retain', ((1,),), None,
                    None, MediaList)
    return f(p_ml)

def libvlc_media_list_set_media(p_ml, p_md):
    '''Associate media instance with this media list instance.
    If another media instance was present it will be released.
    The L{libvlc_media_list_lock} should NOT be held upon entering this function.
    @param p_ml: a media list instance.
    @param p_md: media instance to add.
    '''
    f = _Cfunctions.get('libvlc_media_list_set_media', None) or \
        _Cfunction('libvlc_media_list_set_media', ((1,), (1,),), None,
                    None, MediaList, Media)
    return f(p_ml, p_md)

def libvlc_media_list_media(p_ml):
    '''Get media instance from this media list instance. This action will increase
    the refcount on the media instance.
    The L{libvlc_media_list_lock} should NOT be held upon entering this function.
    @param p_ml: a media list instance.
    @return: media instance.
    '''
    f = _Cfunctions.get('libvlc_media_list_media', None) or \
        _Cfunction('libvlc_media_list_media', ((1,),), class_result(Media),
                    ctypes.c_void_p, MediaList)
    return f(p_ml)

def libvlc_media_list_add_media(p_ml, p_md):
    '''Add media instance to media list
    The L{libvlc_media_list_lock} should be held upon entering this function.
    @param p_ml: a media list instance.
    @param p_md: a media instance.
    @return: 0 on success, -1 if the media list is read-only.
    '''
    f = _Cfunctions.get('libvlc_media_list_add_media', None) or \
        _Cfunction('libvlc_media_list_add_media', ((1,), (1,),), None,
                    ctypes.c_int, MediaList, Media)
    return f(p_ml, p_md)

def libvlc_media_list_insert_media(p_ml, p_md, i_pos):
    '''Insert media instance in media list on a position
    The L{libvlc_media_list_lock} should be held upon entering this function.
    @param p_ml: a media list instance.
    @param p_md: a media instance.
    @param i_pos: position in array where to insert.
    @return: 0 on success, -1 if the media list is read-only.
    '''
    f = _Cfunctions.get('libvlc_media_list_insert_media', None) or \
        _Cfunction('libvlc_media_list_insert_media', ((1,), (1,), (1,),), None,
                    ctypes.c_int, MediaList, Media, ctypes.c_int)
    return f(p_ml, p_md, i_pos)

def libvlc_media_list_remove_index(p_ml, i_pos):
    '''Remove media instance from media list on a position
    The L{libvlc_media_list_lock} should be held upon entering this function.
    @param p_ml: a media list instance.
    @param i_pos: position in array where to insert.
    @return: 0 on success, -1 if the list is read-only or the item was not found.
    '''
    f = _Cfunctions.get('libvlc_media_list_remove_index', None) or \
        _Cfunction('libvlc_media_list_remove_index', ((1,), (1,),), None,
                    ctypes.c_int, MediaList, ctypes.c_int)
    return f(p_ml, i_pos)

def libvlc_media_list_count(p_ml):
    '''Get count on media list items
    The L{libvlc_media_list_lock} should be held upon entering this function.
    @param p_ml: a media list instance.
    @return: number of items in media list.
    '''
    f = _Cfunctions.get('libvlc_media_list_count', None) or \
        _Cfunction('libvlc_media_list_count', ((1,),), None,
                    ctypes.c_int, MediaList)
    return f(p_ml)

def libvlc_media_list_item_at_index(p_ml, i_pos):
    '''List media instance in media list at a position
    The L{libvlc_media_list_lock} should be held upon entering this function.
    @param p_ml: a media list instance.
    @param i_pos: position in array where to insert.
    @return: media instance at position i_pos, or None if not found. In case of success, L{libvlc_media_retain}() is called to increase the refcount on the media.
    '''
    f = _Cfunctions.get('libvlc_media_list_item_at_index', None) or \
        _Cfunction('libvlc_media_list_item_at_index', ((1,), (1,),), class_result(Media),
                    ctypes.c_void_p, MediaList, ctypes.c_int)
    return f(p_ml, i_pos)

def libvlc_media_list_index_of_item(p_ml, p_md):
    '''Find index position of List media instance in media list.
    Warning: the function will return the first matched position.
    The L{libvlc_media_list_lock} should be held upon entering this function.
    @param p_ml: a media list instance.
    @param p_md: media instance.
    @return: position of media instance or -1 if media not found.
    '''
    f = _Cfunctions.get('libvlc_media_list_index_of_item', None) or \
        _Cfunction('libvlc_media_list_index_of_item', ((1,), (1,),), None,
                    ctypes.c_int, MediaList, Media)
    return f(p_ml, p_md)

def libvlc_media_list_is_readonly(p_ml):
    '''This indicates if this media list is read-only from a user point of view.
    @param p_ml: media list instance \retval true read-only \retval false read/write.
    '''
    f = _Cfunctions.get('libvlc_media_list_is_readonly', None) or \
        _Cfunction('libvlc_media_list_is_readonly', ((1,),), None,
                    ctypes.c_bool, MediaList)
    return f(p_ml)

def libvlc_media_list_lock(p_ml):
    '''Get lock on media list items.
    @param p_ml: a media list instance.
    '''
    f = _Cfunctions.get('libvlc_media_list_lock', None) or \
        _Cfunction('libvlc_media_list_lock', ((1,),), None,
                    None, MediaList)
    return f(p_ml)

def libvlc_media_list_unlock(p_ml):
    '''Release lock on media list items
    The L{libvlc_media_list_lock} should be held upon entering this function.
    @param p_ml: a media list instance.
    '''
    f = _Cfunctions.get('libvlc_media_list_unlock', None) or \
        _Cfunction('libvlc_media_list_unlock', ((1,),), None,
                    None, MediaList)
    return f(p_ml)

def libvlc_media_list_event_manager(p_ml):
    '''Get libvlc_event_manager from this media list instance.
    The p_event_manager is immutable, so you don't have to hold the lock.
    @param p_ml: a media list instance.
    @return: libvlc_event_manager.
    '''
    f = _Cfunctions.get('libvlc_media_list_event_manager', None) or \
        _Cfunction('libvlc_media_list_event_manager', ((1,),), class_result(EventManager),
                    ctypes.c_void_p, MediaList)
    return f(p_ml)

def libvlc_media_list_player_new(p_instance):
    '''Create new media_list_player.
    @param p_instance: libvlc instance.
    @return: media list player instance or None on error (it must be released by L{libvlc_media_list_player_release}()).
    '''
    f = _Cfunctions.get('libvlc_media_list_player_new', None) or \
        _Cfunction('libvlc_media_list_player_new', ((1,),), class_result(MediaListPlayer),
                    ctypes.c_void_p, Instance)
    return f(p_instance)

def libvlc_media_list_player_release(p_mlp):
    '''Release a media_list_player after use
    Decrement the reference count of a media player object. If the
    reference count is 0, then L{libvlc_media_list_player_release}() will
    release the media player object. If the media player object
    has been released, then it should not be used again.
    @param p_mlp: media list player instance.
    '''
    f = _Cfunctions.get('libvlc_media_list_player_release', None) or \
        _Cfunction('libvlc_media_list_player_release', ((1,),), None,
                    None, MediaListPlayer)
    return f(p_mlp)

def libvlc_media_list_player_retain(p_mlp):
    '''Retain a reference to a media player list object. Use
    L{libvlc_media_list_player_release}() to decrement reference count.
    @param p_mlp: media player list object.
    '''
    f = _Cfunctions.get('libvlc_media_list_player_retain', None) or \
        _Cfunction('libvlc_media_list_player_retain', ((1,),), None,
                    None, MediaListPlayer)
    return f(p_mlp)

def libvlc_media_list_player_event_manager(p_mlp):
    '''Return the event manager of this media_list_player.
    @param p_mlp: media list player instance.
    @return: the event manager.
    '''
    f = _Cfunctions.get('libvlc_media_list_player_event_manager', None) or \
        _Cfunction('libvlc_media_list_player_event_manager', ((1,),), class_result(EventManager),
                    ctypes.c_void_p, MediaListPlayer)
    return f(p_mlp)

def libvlc_media_list_player_set_media_player(p_mlp, p_mi):
    '''Replace media player in media_list_player with this instance.
    @param p_mlp: media list player instance.
    @param p_mi: media player instance.
    '''
    f = _Cfunctions.get('libvlc_media_list_player_set_media_player', None) or \
        _Cfunction('libvlc_media_list_player_set_media_player', ((1,), (1,),), None,
                    None, MediaListPlayer, MediaPlayer)
    return f(p_mlp, p_mi)

def libvlc_media_list_player_get_media_player(p_mlp):
    '''Get media player of the media_list_player instance.
    @param p_mlp: media list player instance.
    @return: media player instance @note the caller is responsible for releasing the returned instance.
    '''
    f = _Cfunctions.get('libvlc_media_list_player_get_media_player', None) or \
        _Cfunction('libvlc_media_list_player_get_media_player', ((1,),), class_result(MediaPlayer),
                    ctypes.c_void_p, MediaListPlayer)
    return f(p_mlp)

def libvlc_media_list_player_set_media_list(p_mlp, p_mlist):
    '''Set the media list associated with the player.
    @param p_mlp: media list player instance.
    @param p_mlist: list of media.
    '''
    f = _Cfunctions.get('libvlc_media_list_player_set_media_list', None) or \
        _Cfunction('libvlc_media_list_player_set_media_list', ((1,), (1,),), None,
                    None, MediaListPlayer, MediaList)
    return f(p_mlp, p_mlist)

def libvlc_media_list_player_play(p_mlp):
    '''Play media list.
    @param p_mlp: media list player instance.
    '''
    f = _Cfunctions.get('libvlc_media_list_player_play', None) or \
        _Cfunction('libvlc_media_list_player_play', ((1,),), None,
                    None, MediaListPlayer)
    return f(p_mlp)

def libvlc_media_list_player_pause(p_mlp):
    '''Toggle pause (or resume) media list.
    @param p_mlp: media list player instance.
    '''
    f = _Cfunctions.get('libvlc_media_list_player_pause', None) or \
        _Cfunction('libvlc_media_list_player_pause', ((1,),), None,
                    None, MediaListPlayer)
    return f(p_mlp)

def libvlc_media_list_player_set_pause(p_mlp, do_pause):
    '''Pause or resume media list.
    @param p_mlp: media list player instance.
    @param do_pause: play/resume if zero, pause if non-zero.
    @version: LibVLC 3.0.0 or later.
    '''
    f = _Cfunctions.get('libvlc_media_list_player_set_pause', None) or \
        _Cfunction('libvlc_media_list_player_set_pause', ((1,), (1,),), None,
                    None, MediaListPlayer, ctypes.c_int)
    return f(p_mlp, do_pause)

def libvlc_media_list_player_is_playing(p_mlp):
    '''Is media list playing?
    @param p_mlp: media list player instance \retval true playing \retval false not playing.
    '''
    f = _Cfunctions.get('libvlc_media_list_player_is_playing', None) or \
        _Cfunction('libvlc_media_list_player_is_playing', ((1,),), None,
                    ctypes.c_bool, MediaListPlayer)
    return f(p_mlp)

def libvlc_media_list_player_get_state(p_mlp):
    '''Get current libvlc_state of media list player.
    @param p_mlp: media list player instance.
    @return: L{State} for media list player.
    '''
    f = _Cfunctions.get('libvlc_media_list_player_get_state', None) or \
        _Cfunction('libvlc_media_list_player_get_state', ((1,),), None,
                    State, MediaListPlayer)
    return f(p_mlp)

def libvlc_media_list_player_play_item_at_index(p_mlp, i_index):
    '''Play media list item at position index.
    @param p_mlp: media list player instance.
    @param i_index: index in media list to play.
    @return: 0 upon success -1 if the item wasn't found.
    '''
    f = _Cfunctions.get('libvlc_media_list_player_play_item_at_index', None) or \
        _Cfunction('libvlc_media_list_player_play_item_at_index', ((1,), (1,),), None,
                    ctypes.c_int, MediaListPlayer, ctypes.c_int)
    return f(p_mlp, i_index)

def libvlc_media_list_player_play_item(p_mlp, p_md):
    '''Play the given media item.
    @param p_mlp: media list player instance.
    @param p_md: the media instance.
    @return: 0 upon success, -1 if the media is not part of the media list.
    '''
    f = _Cfunctions.get('libvlc_media_list_player_play_item', None) or \
        _Cfunction('libvlc_media_list_player_play_item', ((1,), (1,),), None,
                    ctypes.c_int, MediaListPlayer, Media)
    return f(p_mlp, p_md)

def libvlc_media_list_player_stop_async(p_mlp):
    '''Stop playing media list.
    @param p_mlp: media list player instance.
    '''
    f = _Cfunctions.get('libvlc_media_list_player_stop_async', None) or \
        _Cfunction('libvlc_media_list_player_stop_async', ((1,),), None,
                    None, MediaListPlayer)
    return f(p_mlp)

def libvlc_media_list_player_next(p_mlp):
    '''Play next item from media list.
    @param p_mlp: media list player instance.
    @return: 0 upon success -1 if there is no next item.
    '''
    f = _Cfunctions.get('libvlc_media_list_player_next', None) or \
        _Cfunction('libvlc_media_list_player_next', ((1,),), None,
                    ctypes.c_int, MediaListPlayer)
    return f(p_mlp)

def libvlc_media_list_player_previous(p_mlp):
    '''Play previous item from media list.
    @param p_mlp: media list player instance.
    @return: 0 upon success -1 if there is no previous item.
    '''
    f = _Cfunctions.get('libvlc_media_list_player_previous', None) or \
        _Cfunction('libvlc_media_list_player_previous', ((1,),), None,
                    ctypes.c_int, MediaListPlayer)
    return f(p_mlp)

def libvlc_media_list_player_set_playback_mode(p_mlp, e_mode):
    '''Sets the playback mode for the playlist.
    @param p_mlp: media list player instance.
    @param e_mode: playback mode specification.
    '''
    f = _Cfunctions.get('libvlc_media_list_player_set_playback_mode', None) or \
        _Cfunction('libvlc_media_list_player_set_playback_mode', ((1,), (1,),), None,
                    None, MediaListPlayer, PlaybackMode)
    return f(p_mlp, e_mode)

def libvlc_media_player_new(p_libvlc_instance):
    '''Create an empty Media Player object.
    @param p_libvlc_instance: the libvlc instance in which the Media Player should be created.
    @return: a new media player object, or None on error. It must be released by L{libvlc_media_player_release}().
    '''
    f = _Cfunctions.get('libvlc_media_player_new', None) or \
        _Cfunction('libvlc_media_player_new', ((1,),), class_result(MediaPlayer),
                    ctypes.c_void_p, Instance)
    return f(p_libvlc_instance)

def libvlc_media_player_new_from_media(inst, p_md):
    '''Create a Media Player object from a Media.
    @param inst: LibVLC instance to create a media player with.
    @param p_md: the media. Afterwards the p_md can be safely destroyed.
    @return: a new media player object, or None on error. It must be released by L{libvlc_media_player_release}().
    '''
    f = _Cfunctions.get('libvlc_media_player_new_from_media', None) or \
        _Cfunction('libvlc_media_player_new_from_media', ((1,), (1,),), class_result(MediaPlayer),
                    ctypes.c_void_p, Instance, Media)
    return f(inst, p_md)

def libvlc_media_player_release(p_mi):
    '''Release a media_player after use
    Decrement the reference count of a media player object. If the
    reference count is 0, then L{libvlc_media_player_release}() will
    release the media player object. If the media player object
    has been released, then it should not be used again.
    @param p_mi: the Media Player to free.
    '''
    f = _Cfunctions.get('libvlc_media_player_release', None) or \
        _Cfunction('libvlc_media_player_release', ((1,),), None,
                    None, MediaPlayer)
    return f(p_mi)

def libvlc_media_player_retain(p_mi):
    '''Retain a reference to a media player object. Use
    L{libvlc_media_player_release}() to decrement reference count.
    @param p_mi: media player object.
    '''
    f = _Cfunctions.get('libvlc_media_player_retain', None) or \
        _Cfunction('libvlc_media_player_retain', ((1,),), None,
                    None, MediaPlayer)
    return f(p_mi)

def libvlc_media_player_set_media(p_mi, p_md):
    '''Set the media that will be used by the media_player. If any,
    previous md will be released.
    @note: The user should listen to the libvlc_MediaPlayerMediaChanged event, to
    know when the new media is actually used by the player (or to known that the
    older media is no longer used).
    @param p_mi: the Media Player.
    @param p_md: the Media. Afterwards the p_md can be safely destroyed.
    '''
    f = _Cfunctions.get('libvlc_media_player_set_media', None) or \
        _Cfunction('libvlc_media_player_set_media', ((1,), (1,),), None,
                    None, MediaPlayer, Media)
    return f(p_mi, p_md)

def libvlc_media_player_get_media(p_mi):
    '''Get the media used by the media_player.
    @warning: Calling this function just after L{libvlc_media_player_set_media}()
    will return the media that was just set, but this media might not be
    currently used internally by the player. To detect such case, the user
    should listen to the libvlc_MediaPlayerMediaChanged event.
    @param p_mi: the Media Player.
    @return: the media associated with p_mi, or None if no media is associated.
    '''
    f = _Cfunctions.get('libvlc_media_player_get_media', None) or \
        _Cfunction('libvlc_media_player_get_media', ((1,),), class_result(Media),
                    ctypes.c_void_p, MediaPlayer)
    return f(p_mi)

def libvlc_media_player_event_manager(p_mi):
    '''Get the Event Manager from which the media player send event.
    @param p_mi: the Media Player.
    @return: the event manager associated with p_mi.
    '''
    f = _Cfunctions.get('libvlc_media_player_event_manager', None) or \
        _Cfunction('libvlc_media_player_event_manager', ((1,),), class_result(EventManager),
                    ctypes.c_void_p, MediaPlayer)
    return f(p_mi)

def libvlc_media_player_is_playing(p_mi):
    '''is_playing.
    @param p_mi: the Media Player \retval true media player is playing \retval false media player is not playing.
    '''
    f = _Cfunctions.get('libvlc_media_player_is_playing', None) or \
        _Cfunction('libvlc_media_player_is_playing', ((1,),), None,
                    ctypes.c_bool, MediaPlayer)
    return f(p_mi)

def libvlc_media_player_play(p_mi):
    '''Play.
    @param p_mi: the Media Player.
    @return: 0 if playback started (and was already started), or -1 on error.
    '''
    f = _Cfunctions.get('libvlc_media_player_play', None) or \
        _Cfunction('libvlc_media_player_play', ((1,),), None,
                    ctypes.c_int, MediaPlayer)
    return f(p_mi)

def libvlc_media_player_set_pause(mp, do_pause):
    '''Pause or resume (no effect if there is no media).
    @param mp: the Media Player.
    @param do_pause: play/resume if zero, pause if non-zero.
    @version: LibVLC 1.1.1 or later.
    '''
    f = _Cfunctions.get('libvlc_media_player_set_pause', None) or \
        _Cfunction('libvlc_media_player_set_pause', ((1,), (1,),), None,
                    None, MediaPlayer, ctypes.c_int)
    return f(mp, do_pause)

def libvlc_media_player_pause(p_mi):
    '''Toggle pause (no effect if there is no media).
    @param p_mi: the Media Player.
    '''
    f = _Cfunctions.get('libvlc_media_player_pause', None) or \
        _Cfunction('libvlc_media_player_pause', ((1,),), None,
                    None, MediaPlayer)
    return f(p_mi)

def libvlc_media_player_stop_async(p_mi):
    '''Stop asynchronously
    @note: This function is asynchronous. In case of success, the user should
    wait for the libvlc_MediaPlayerStopped event to know when the stop is
    finished.
    @param p_mi: the Media Player.
    @return: 0 if the player is being stopped, -1 otherwise (no-op).
    @version: LibVLC 4.0.0 or later.
    '''
    f = _Cfunctions.get('libvlc_media_player_stop_async', None) or \
        _Cfunction('libvlc_media_player_stop_async', ((1,),), None,
                    ctypes.c_int, MediaPlayer)
    return f(p_mi)

def libvlc_media_player_set_renderer(p_mi, p_item):
    '''Set a renderer to the media player
    @note: must be called before the first call of L{libvlc_media_player_play}() to
    take effect.
    See L{libvlc_renderer_discoverer_new}.
    @param p_mi: the Media Player.
    @param p_item: an item discovered by L{libvlc_renderer_discoverer_start}().
    @return: 0 on success, -1 on error.
    @version: LibVLC 3.0.0 or later.
    '''
    f = _Cfunctions.get('libvlc_media_player_set_renderer', None) or \
        _Cfunction('libvlc_media_player_set_renderer', ((1,), (1,),), None,
                    ctypes.c_int, MediaPlayer, Renderer)
    return f(p_mi, p_item)

def libvlc_video_set_callbacks(mp, lock, unlock, display, opaque):
    '''Set callbacks and private data to render decoded video to a custom area
    in memory.
    Use L{libvlc_video_set_format}() or L{libvlc_video_set_format_callbacks}()
    to configure the decoded format.
    @warning: Rendering video into custom memory buffers is considerably less
    efficient than rendering in a custom window as normal.
    For optimal perfomances, VLC media player renders into a custom window, and
    does not use this function and associated callbacks. It is B{highly
    recommended} that other LibVLC-based application do likewise.
    To embed video in a window, use L{libvlc_media_player_set_xwindow}() or
    equivalent depending on the operating system.
    If window embedding does not fit the application use case, then a custom
    LibVLC video output display plugin is required to maintain optimal video
    rendering performances.
    The following limitations affect performance:
    - Hardware video decoding acceleration will either be disabled completely,
      or require (relatively slow) copy from video/DSP memory to main memory.
    - Sub-pictures (subtitles, on-screen display, etc.) must be blent into the
      main picture by the CPU instead of the GPU.
    - Depending on the video format, pixel format conversion, picture scaling,
      cropping and/or picture re-orientation, must be performed by the CPU
      instead of the GPU.
    - Memory copying is required between LibVLC reference picture buffers and
      application buffers (between lock and unlock callbacks).
    @param mp: the media player.
    @param lock: callback to lock video memory (must not be None).
    @param unlock: callback to unlock video memory (or None if not needed).
    @param display: callback to display video (or None if not needed).
    @param opaque: private pointer for the three callbacks (as first parameter).
    @version: LibVLC 1.1.1 or later.
    '''
    f = _Cfunctions.get('libvlc_video_set_callbacks', None) or \
        _Cfunction('libvlc_video_set_callbacks', ((1,), (1,), (1,), (1,), (1,),), None,
                    None, MediaPlayer, VideoLockCb, VideoUnlockCb, VideoDisplayCb, ctypes.c_void_p)
    return f(mp, lock, unlock, display, opaque)

def libvlc_video_set_format(mp, chroma, width, height, pitch):
    '''Set decoded video chroma and dimensions.
    This only works in combination with L{libvlc_video_set_callbacks}(),
    and is mutually exclusive with L{libvlc_video_set_format_callbacks}().
    @param mp: the media player.
    @param chroma: a four-characters string identifying the chroma (e.g. "RV32" or "YUYV").
    @param width: pixel width.
    @param height: pixel height.
    @param pitch: line pitch (in bytes).
    @version: LibVLC 1.1.1 or later.
    @bug: All pixel planes are expected to have the same pitch. To use the YCbCr color space with chrominance subsampling, consider using L{libvlc_video_set_format_callbacks}() instead.
    '''
    f = _Cfunctions.get('libvlc_video_set_format', None) or \
        _Cfunction('libvlc_video_set_format', ((1,), (1,), (1,), (1,), (1,),), None,
                    None, MediaPlayer, ctypes.c_char_p, ctypes.c_uint, ctypes.c_uint, ctypes.c_uint)
    return f(mp, chroma, width, height, pitch)

def libvlc_video_set_format_callbacks(mp, setup, cleanup):
    '''Set decoded video chroma and dimensions. This only works in combination with
    L{libvlc_video_set_callbacks}().
    @param mp: the media player.
    @param setup: callback to select the video format (cannot be None).
    @param cleanup: callback to release any allocated resources (or None).
    @version: LibVLC 2.0.0 or later.
    '''
    f = _Cfunctions.get('libvlc_video_set_format_callbacks', None) or \
        _Cfunction('libvlc_video_set_format_callbacks', ((1,), (1,), (1,),), None,
                    None, MediaPlayer, VideoFormatCb, VideoCleanupCb)
    return f(mp, setup, cleanup)

def libvlc_media_player_set_nsobject(p_mi, drawable):
    '''Set the NSView handler where the media player should render its video output.
    Use the vout called "macosx".
    The drawable is an NSObject that follow the VLCVideoViewEmbedding
    protocol:
    @code.m
    @protocol VLCVideoViewEmbedding <NSObject>
    - (void)addVoutSubview:(NSView *)view;
    - (void)removeVoutSubview:(NSView *)view;
    @end
    @endcode
    Or it can be an NSView object.
    If you want to use it along with Qt see the QMacCocoaViewContainer. Then
    the following code should work:
    @code.mm
    
        NSView *video = [[NSView alloc] init];
        QMacCocoaViewContainer *container = new QMacCocoaViewContainer(video, parent);
        L{libvlc_media_player_set_nsobject}(mp, video);
        [video release];
    
    @endcode
    You can find a live example in VLCVideoView in VLCKit.framework.
    @param p_mi: the Media Player.
    @param drawable: the drawable that is either an NSView or an object following the VLCVideoViewEmbedding protocol.
    '''
    f = _Cfunctions.get('libvlc_media_player_set_nsobject', None) or \
        _Cfunction('libvlc_media_player_set_nsobject', ((1,), (1,),), None,
                    None, MediaPlayer, ctypes.c_void_p)
    return f(p_mi, drawable)

def libvlc_media_player_get_nsobject(p_mi):
    '''Get the NSView handler previously set with L{libvlc_media_player_set_nsobject}().
    @param p_mi: the Media Player.
    @return: the NSView handler or 0 if none where set.
    '''
    f = _Cfunctions.get('libvlc_media_player_get_nsobject', None) or \
        _Cfunction('libvlc_media_player_get_nsobject', ((1,),), None,
                    ctypes.c_void_p, MediaPlayer)
    return f(p_mi)

def libvlc_media_player_set_xwindow(p_mi, drawable):
    '''Set an X Window System drawable where the media player should render its
    video output. The call takes effect when the playback starts. If it is
    already started, it might need to be stopped before changes apply.
    If LibVLC was built without X11 output support, then this function has no
    effects.
    By default, LibVLC will capture input events on the video rendering area.
    Use L{libvlc_video_set_mouse_input}() and L{libvlc_video_set_key_input}() to
    disable that and deliver events to the parent window / to the application
    instead. By design, the X11 protocol delivers input events to only one
    recipient.
    @warning
    The application must call the XInitThreads() function from Xlib before
    L{libvlc_new}(), and before any call to XOpenDisplay() directly or via any
    other library. Failure to call XInitThreads() will seriously impede LibVLC
    performance. Calling XOpenDisplay() before XInitThreads() will eventually
    crash the process. That is a limitation of Xlib.
    @param p_mi: media player.
    @param drawable: X11 window ID @note The specified identifier must correspond to an existing Input/Output class X11 window. Pixmaps are B{not} currently supported. The default X11 server is assumed, i.e. that specified in the DISPLAY environment variable. @warning LibVLC can deal with invalid X11 handle errors, however some display drivers (EGL, GLX, VA and/or VDPAU) can unfortunately not. Thus the window handle must remain valid until playback is stopped, otherwise the process may abort or crash.
    @bug No more than one window handle per media player instance can be specified. If the media has multiple simultaneously active video tracks, extra tracks will be rendered into external windows beyond the control of the application.
    '''
    f = _Cfunctions.get('libvlc_media_player_set_xwindow', None) or \
        _Cfunction('libvlc_media_player_set_xwindow', ((1,), (1,),), None,
                    None, MediaPlayer, ctypes.c_uint32)
    return f(p_mi, drawable)

def libvlc_media_player_get_xwindow(p_mi):
    '''Get the X Window System window identifier previously set with
    L{libvlc_media_player_set_xwindow}(). Note that this will return the identifier
    even if VLC is not currently using it (for instance if it is playing an
    audio-only input).
    @param p_mi: the Media Player.
    @return: an X window ID, or 0 if none where set.
    '''
    f = _Cfunctions.get('libvlc_media_player_get_xwindow', None) or \
        _Cfunction('libvlc_media_player_get_xwindow', ((1,),), None,
                    ctypes.c_uint32, MediaPlayer)
    return f(p_mi)

def libvlc_media_player_set_hwnd(p_mi, drawable):
    '''Set a Win32/Win64 API window handle (HWND) where the media player should
    render its video output. If LibVLC was built without Win32/Win64 API output
    support, then this has no effects.
    @param p_mi: the Media Player.
    @param drawable: windows handle of the drawable.
    '''
    f = _Cfunctions.get('libvlc_media_player_set_hwnd', None) or \
        _Cfunction('libvlc_media_player_set_hwnd', ((1,), (1,),), None,
                    None, MediaPlayer, ctypes.c_void_p)
    return f(p_mi, drawable)

def libvlc_media_player_get_hwnd(p_mi):
    '''Get the Windows API window handle (HWND) previously set with
    L{libvlc_media_player_set_hwnd}(). The handle will be returned even if LibVLC
    is not currently outputting any video to it.
    @param p_mi: the Media Player.
    @return: a window handle or None if there are none.
    '''
    f = _Cfunctions.get('libvlc_media_player_get_hwnd', None) or \
        _Cfunction('libvlc_media_player_get_hwnd', ((1,),), None,
                    ctypes.c_void_p, MediaPlayer)
    return f(p_mi)

def libvlc_media_player_set_android_context(p_mi, p_awindow_handler):
    '''Set the android context.
    @param p_mi: the media player.
    @param p_awindow_handler: org.videolan.libvlc.AWindow jobject owned by the org.videolan.libvlc.MediaPlayer class from the libvlc-android project.
    @version: LibVLC 3.0.0 and later.
    '''
    f = _Cfunctions.get('libvlc_media_player_set_android_context', None) or \
        _Cfunction('libvlc_media_player_set_android_context', ((1,), (1,),), None,
                    None, MediaPlayer, ctypes.c_void_p)
    return f(p_mi, p_awindow_handler)

def libvlc_audio_set_callbacks(mp, play, pause, resume, flush, drain, opaque):
    '''Sets callbacks and private data for decoded audio.
    Use L{libvlc_audio_set_format}() or L{libvlc_audio_set_format_callbacks}()
    to configure the decoded audio format.
    @note: The audio callbacks override any other audio output mechanism.
    If the callbacks are set, LibVLC will B{not} output audio in any way.
    @param mp: the media player.
    @param play: callback to play audio samples (must not be None).
    @param pause: callback to pause playback (or None to ignore).
    @param resume: callback to resume playback (or None to ignore).
    @param flush: callback to flush audio buffers (or None to ignore).
    @param drain: callback to drain audio buffers (or None to ignore).
    @param opaque: private pointer for the audio callbacks (as first parameter).
    @version: LibVLC 2.0.0 or later.
    '''
    f = _Cfunctions.get('libvlc_audio_set_callbacks', None) or \
        _Cfunction('libvlc_audio_set_callbacks', ((1,), (1,), (1,), (1,), (1,), (1,), (1,),), None,
                    None, MediaPlayer, AudioPlayCb, AudioPauseCb, AudioResumeCb, AudioFlushCb, AudioDrainCb, ctypes.c_void_p)
    return f(mp, play, pause, resume, flush, drain, opaque)

def libvlc_audio_set_volume_callback(mp, set_volume):
    '''Set callbacks and private data for decoded audio. This only works in
    combination with L{libvlc_audio_set_callbacks}().
    Use L{libvlc_audio_set_format}() or L{libvlc_audio_set_format_callbacks}()
    to configure the decoded audio format.
    @param mp: the media player.
    @param set_volume: callback to apply audio volume, or None to apply volume in software.
    @version: LibVLC 2.0.0 or later.
    '''
    f = _Cfunctions.get('libvlc_audio_set_volume_callback', None) or \
        _Cfunction('libvlc_audio_set_volume_callback', ((1,), (1,),), None,
                    None, MediaPlayer, AudioSetVolumeCb)
    return f(mp, set_volume)

def libvlc_audio_set_format_callbacks(mp, setup, cleanup):
    '''Sets decoded audio format via callbacks.
    This only works in combination with L{libvlc_audio_set_callbacks}().
    @param mp: the media player.
    @param setup: callback to select the audio format (cannot be None).
    @param cleanup: callback to release any allocated resources (or None).
    @version: LibVLC 2.0.0 or later.
    '''
    f = _Cfunctions.get('libvlc_audio_set_format_callbacks', None) or \
        _Cfunction('libvlc_audio_set_format_callbacks', ((1,), (1,), (1,),), None,
                    None, MediaPlayer, AudioSetupCb, AudioCleanupCb)
    return f(mp, setup, cleanup)

def libvlc_audio_set_format(mp, format, rate, channels):
    '''Sets a fixed decoded audio format.
    This only works in combination with L{libvlc_audio_set_callbacks}(),
    and is mutually exclusive with L{libvlc_audio_set_format_callbacks}().
    The supported formats are:
    - "S16N" for signed 16-bit PCM
    - "S32N" for signed 32-bit PCM
    - "FL32" for single precision IEEE 754
    All supported formats use the native endianess.
    If there are more than one channel, samples are interleaved.
    @param mp: the media player.
    @param format: a four-characters string identifying the sample format.
    @param rate: sample rate (expressed in Hz).
    @param channels: channels count.
    @version: LibVLC 2.0.0 or later.
    '''
    f = _Cfunctions.get('libvlc_audio_set_format', None) or \
        _Cfunction('libvlc_audio_set_format', ((1,), (1,), (1,), (1,),), None,
                    None, MediaPlayer, ctypes.c_char_p, ctypes.c_uint, ctypes.c_uint)
    return f(mp, format, rate, channels)

def libvlc_media_player_get_length(p_mi):
    '''Get the current movie length (in ms).
    @param p_mi: the Media Player.
    @return: the movie length (in ms), or -1 if there is no media.
    '''
    f = _Cfunctions.get('libvlc_media_player_get_length', None) or \
        _Cfunction('libvlc_media_player_get_length', ((1,),), None,
                    ctypes.c_longlong, MediaPlayer)
    return f(p_mi)

def libvlc_media_player_get_time(p_mi):
    '''Get the current movie time (in ms).
    @param p_mi: the Media Player.
    @return: the movie time (in ms), or -1 if there is no media.
    '''
    f = _Cfunctions.get('libvlc_media_player_get_time', None) or \
        _Cfunction('libvlc_media_player_get_time', ((1,),), None,
                    ctypes.c_longlong, MediaPlayer)
    return f(p_mi)

def libvlc_media_player_set_time(p_mi, i_time, b_fast):
    '''Set the movie time (in ms). This has no effect if no media is being played.
    Not all formats and protocols support this.
    @param p_mi: the Media Player.
    @param b_fast: prefer fast seeking or precise seeking.
    @param i_time: the movie time (in ms).
    @return: 0 on success, -1 on error.
    '''
    f = _Cfunctions.get('libvlc_media_player_set_time', None) or \
        _Cfunction('libvlc_media_player_set_time', ((1,), (1,), (1,),), None,
                    ctypes.c_int, MediaPlayer, ctypes.c_longlong, ctypes.c_bool)
    return f(p_mi, i_time, b_fast)

def libvlc_media_player_get_position(p_mi):
    '''Get movie position as percentage between 0.0 and 1.0.
    @param p_mi: the Media Player.
    @return: movie position, or -1. in case of error.
    '''
    f = _Cfunctions.get('libvlc_media_player_get_position', None) or \
        _Cfunction('libvlc_media_player_get_position', ((1,),), None,
                    ctypes.c_double, MediaPlayer)
    return f(p_mi)

def libvlc_media_player_set_position(p_mi, f_pos, b_fast):
    '''Set movie position as percentage between 0.0 and 1.0.
    This has no effect if playback is not enabled.
    This might not work depending on the underlying input format and protocol.
    @param p_mi: the Media Player.
    @param b_fast: prefer fast seeking or precise seeking.
    @param f_pos: the position.
    @return: 0 on success, -1 on error.
    '''
    f = _Cfunctions.get('libvlc_media_player_set_position', None) or \
        _Cfunction('libvlc_media_player_set_position', ((1,), (1,), (1,),), None,
                    ctypes.c_int, MediaPlayer, ctypes.c_double, ctypes.c_bool)
    return f(p_mi, f_pos, b_fast)

def libvlc_media_player_set_chapter(p_mi, i_chapter):
    '''Set movie chapter (if applicable).
    @param p_mi: the Media Player.
    @param i_chapter: chapter number to play.
    '''
    f = _Cfunctions.get('libvlc_media_player_set_chapter', None) or \
        _Cfunction('libvlc_media_player_set_chapter', ((1,), (1,),), None,
                    None, MediaPlayer, ctypes.c_int)
    return f(p_mi, i_chapter)

def libvlc_media_player_get_chapter(p_mi):
    '''Get movie chapter.
    @param p_mi: the Media Player.
    @return: chapter number currently playing, or -1 if there is no media.
    '''
    f = _Cfunctions.get('libvlc_media_player_get_chapter', None) or \
        _Cfunction('libvlc_media_player_get_chapter', ((1,),), None,
                    ctypes.c_int, MediaPlayer)
    return f(p_mi)

def libvlc_media_player_get_chapter_count(p_mi):
    '''Get movie chapter count.
    @param p_mi: the Media Player.
    @return: number of chapters in movie, or -1.
    '''
    f = _Cfunctions.get('libvlc_media_player_get_chapter_count', None) or \
        _Cfunction('libvlc_media_player_get_chapter_count', ((1,),), None,
                    ctypes.c_int, MediaPlayer)
    return f(p_mi)

def libvlc_media_player_get_chapter_count_for_title(p_mi, i_title):
    '''Get title chapter count.
    @param p_mi: the Media Player.
    @param i_title: title.
    @return: number of chapters in title, or -1.
    '''
    f = _Cfunctions.get('libvlc_media_player_get_chapter_count_for_title', None) or \
        _Cfunction('libvlc_media_player_get_chapter_count_for_title', ((1,), (1,),), None,
                    ctypes.c_int, MediaPlayer, ctypes.c_int)
    return f(p_mi, i_title)

def libvlc_media_player_set_title(p_mi, i_title):
    '''Set movie title.
    @param p_mi: the Media Player.
    @param i_title: title number to play.
    '''
    f = _Cfunctions.get('libvlc_media_player_set_title', None) or \
        _Cfunction('libvlc_media_player_set_title', ((1,), (1,),), None,
                    None, MediaPlayer, ctypes.c_int)
    return f(p_mi, i_title)

def libvlc_media_player_get_title(p_mi):
    '''Get movie title.
    @param p_mi: the Media Player.
    @return: title number currently playing, or -1.
    '''
    f = _Cfunctions.get('libvlc_media_player_get_title', None) or \
        _Cfunction('libvlc_media_player_get_title', ((1,),), None,
                    ctypes.c_int, MediaPlayer)
    return f(p_mi)

def libvlc_media_player_get_title_count(p_mi):
    '''Get movie title count.
    @param p_mi: the Media Player.
    @return: title number count, or -1.
    '''
    f = _Cfunctions.get('libvlc_media_player_get_title_count', None) or \
        _Cfunction('libvlc_media_player_get_title_count', ((1,),), None,
                    ctypes.c_int, MediaPlayer)
    return f(p_mi)

def libvlc_media_player_previous_chapter(p_mi):
    '''Set previous chapter (if applicable).
    @param p_mi: the Media Player.
    '''
    f = _Cfunctions.get('libvlc_media_player_previous_chapter', None) or \
        _Cfunction('libvlc_media_player_previous_chapter', ((1,),), None,
                    None, MediaPlayer)
    return f(p_mi)

def libvlc_media_player_next_chapter(p_mi):
    '''Set next chapter (if applicable).
    @param p_mi: the Media Player.
    '''
    f = _Cfunctions.get('libvlc_media_player_next_chapter', None) or \
        _Cfunction('libvlc_media_player_next_chapter', ((1,),), None,
                    None, MediaPlayer)
    return f(p_mi)

def libvlc_media_player_get_rate(p_mi):
    '''Get the requested movie play rate.
    @warning: Depending on the underlying media, the requested rate may be
    different from the real playback rate.
    @param p_mi: the Media Player.
    @return: movie play rate.
    '''
    f = _Cfunctions.get('libvlc_media_player_get_rate', None) or \
        _Cfunction('libvlc_media_player_get_rate', ((1,),), None,
                    ctypes.c_float, MediaPlayer)
    return f(p_mi)

def libvlc_media_player_set_rate(p_mi, rate):
    '''Set movie play rate.
    @param p_mi: the Media Player.
    @param rate: movie play rate to set.
    @return: -1 if an error was detected, 0 otherwise (but even then, it might not actually work depending on the underlying media protocol).
    '''
    f = _Cfunctions.get('libvlc_media_player_set_rate', None) or \
        _Cfunction('libvlc_media_player_set_rate', ((1,), (1,),), None,
                    ctypes.c_int, MediaPlayer, ctypes.c_float)
    return f(p_mi, rate)

def libvlc_media_player_get_state(p_mi):
    '''Get current movie state.
    @param p_mi: the Media Player.
    @return: the current state of the media player (playing, paused, ...) See L{State}.
    '''
    f = _Cfunctions.get('libvlc_media_player_get_state', None) or \
        _Cfunction('libvlc_media_player_get_state', ((1,),), None,
                    State, MediaPlayer)
    return f(p_mi)

def libvlc_media_player_has_vout(p_mi):
    '''How many video outputs does this media player have?
    @param p_mi: the media player.
    @return: the number of video outputs.
    '''
    f = _Cfunctions.get('libvlc_media_player_has_vout', None) or \
        _Cfunction('libvlc_media_player_has_vout', ((1,),), None,
                    ctypes.c_uint, MediaPlayer)
    return f(p_mi)

def libvlc_media_player_is_seekable(p_mi):
    '''Is this media player seekable?
    @param p_mi: the media player \retval true media player can seek \retval false media player cannot seek.
    '''
    f = _Cfunctions.get('libvlc_media_player_is_seekable', None) or \
        _Cfunction('libvlc_media_player_is_seekable', ((1,),), None,
                    ctypes.c_bool, MediaPlayer)
    return f(p_mi)

def libvlc_media_player_can_pause(p_mi):
    '''Can this media player be paused?
    @param p_mi: the media player \retval true media player can be paused \retval false media player cannot be paused.
    '''
    f = _Cfunctions.get('libvlc_media_player_can_pause', None) or \
        _Cfunction('libvlc_media_player_can_pause', ((1,),), None,
                    ctypes.c_bool, MediaPlayer)
    return f(p_mi)

def libvlc_media_player_program_scrambled(p_mi):
    '''Check if the current program is scrambled.
    @param p_mi: the media player \retval true current program is scrambled \retval false current program is not scrambled.
    @version: LibVLC 2.2.0 or later.
    '''
    f = _Cfunctions.get('libvlc_media_player_program_scrambled', None) or \
        _Cfunction('libvlc_media_player_program_scrambled', ((1,),), None,
                    ctypes.c_bool, MediaPlayer)
    return f(p_mi)

def libvlc_media_player_next_frame(p_mi):
    '''Display the next frame (if supported).
    @param p_mi: the media player.
    '''
    f = _Cfunctions.get('libvlc_media_player_next_frame', None) or \
        _Cfunction('libvlc_media_player_next_frame', ((1,),), None,
                    None, MediaPlayer)
    return f(p_mi)

def libvlc_media_player_navigate(p_mi, navigate):
    '''Navigate through DVD Menu.
    @param p_mi: the Media Player.
    @param navigate: the Navigation mode.
    @version: libVLC 2.0.0 or later.
    '''
    f = _Cfunctions.get('libvlc_media_player_navigate', None) or \
        _Cfunction('libvlc_media_player_navigate', ((1,), (1,),), None,
                    None, MediaPlayer, ctypes.c_uint)
    return f(p_mi, navigate)

def libvlc_media_player_set_video_title_display(p_mi, position, timeout):
    '''Set if, and how, the video title will be shown when media is played.
    @param p_mi: the media player.
    @param position: position at which to display the title, or libvlc_position_disable to prevent the title from being displayed.
    @param timeout: title display timeout in milliseconds (ignored if libvlc_position_disable).
    @version: libVLC 2.1.0 or later.
    '''
    f = _Cfunctions.get('libvlc_media_player_set_video_title_display', None) or \
        _Cfunction('libvlc_media_player_set_video_title_display', ((1,), (1,), (1,),), None,
                    None, MediaPlayer, Position, ctypes.c_uint)
    return f(p_mi, position, timeout)

def libvlc_media_player_get_tracklist(p_mi, type, selected):
    '''Get the track list for one type.
    @param p_mi: the media player.
    @param type: type of the track list to request.
    @param selected: filter only selected tracks if true (return all tracks, even selected ones if false).
    @return: a valid libvlc_media_tracklist_t or None in case of error, if there is no track for a category, the returned list will have a size of 0, delete with L{libvlc_media_tracklist_delete}().
    @version: LibVLC 4.0.0 and later. @note You need to call L{libvlc_media_parse_request}() or play the media at least once before calling this function.  Not doing this will result in an empty list. @note This track list is a snapshot of the current tracks when this function is called. If a track is updated after this call, the user will need to call this function again to get the updated track. The track list can be used to get track information and to select specific tracks.
    '''
    f = _Cfunctions.get('libvlc_media_player_get_tracklist', None) or \
        _Cfunction('libvlc_media_player_get_tracklist', ((1,), (1,), (1,),), None,
                    ctypes.c_void_p, MediaPlayer, TrackType, ctypes.c_bool)
    return f(p_mi, type, selected)

def libvlc_media_player_get_selected_track(p_mi, type):
    '''Get the selected track for one type.
    @param p_mi: the media player.
    @param type: type of the selected track.
    @return: a valid track or None if there is no selected tracks for this type, release it with L{libvlc_media_track_release}().
    @version: LibVLC 4.0.0 and later. @warning More than one tracks can be selected for one type. In that case, L{libvlc_media_player_get_tracklist}() should be used.
    '''
    f = _Cfunctions.get('libvlc_media_player_get_selected_track', None) or \
        _Cfunction('libvlc_media_player_get_selected_track', ((1,), (1,),), None,
                    ctypes.POINTER(MediaTrack), MediaPlayer, TrackType)
    return f(p_mi, type)

def libvlc_media_player_get_track_from_id(p_mi, psz_id):
    '''Get a track from a track id.
    @param p_mi: the media player.
    @param psz_id: valid string representing a track id (cf. psz_id from \ref L{MediaTrack}).
    @return: a valid track or None if there is currently no tracks identified by the string id, release it with L{libvlc_media_track_release}().
    @version: LibVLC 4.0.0 and later. This function can be used to get the last updated information of a track.
    '''
    f = _Cfunctions.get('libvlc_media_player_get_track_from_id', None) or \
        _Cfunction('libvlc_media_player_get_track_from_id', ((1,), (1,),), None,
                    ctypes.POINTER(MediaTrack), MediaPlayer, ctypes.c_char_p)
    return f(p_mi, psz_id)

def libvlc_media_player_select_track(p_mi, track):
    '''Select a track
    This will unselected the current track.
    @param p_mi: the media player.
    @param track: track to select, can't be None.
    @version: LibVLC 4.0.0 and later. @note Use L{libvlc_media_player_select_tracks}() for multiple selection @warning Only use a \ref L{MediaTrack} retrieved with \ref L{libvlc_media_player_get_tracklist}.
    '''
    f = _Cfunctions.get('libvlc_media_player_select_track', None) or \
        _Cfunction('libvlc_media_player_select_track', ((1,), (1,),), None,
                    None, MediaPlayer, ctypes.POINTER(MediaTrack))
    return f(p_mi, track)

def libvlc_media_player_unselect_track_type(p_mi, type):
    '''Unselect all tracks for a given type.
    @param p_mi: the media player.
    @param type: type to unselect.
    @version: LibVLC 4.0.0 and later.
    '''
    f = _Cfunctions.get('libvlc_media_player_unselect_track_type', None) or \
        _Cfunction('libvlc_media_player_unselect_track_type', ((1,), (1,),), None,
                    None, MediaPlayer, TrackType)
    return f(p_mi, type)

def libvlc_media_player_select_tracks(p_mi, type, tracks, track_count):
    '''Select multiple tracks for one type.
    @param p_mi: the media player.
    @param type: type of the selected track.
    @param tracks: pointer to the track array, or None if track_count is 0.
    @param track_count: number of tracks in the track array.
    @version: LibVLC 4.0.0 and later. @note The internal track list can change between the calls of L{libvlc_media_player_get_tracklist}() and libvlc_media_player_set_tracks(). If a track selection change but the track is not present anymore, the player will just ignore it. @note selecting multiple audio tracks is currently not supported. @warning Only use a \ref L{MediaTrack} retrieved with \ref L{libvlc_media_player_get_tracklist}.
    '''
    f = _Cfunctions.get('libvlc_media_player_select_tracks', None) or \
        _Cfunction('libvlc_media_player_select_tracks', ((1,), (1,), (1,), (1,),), None,
                    None, MediaPlayer, TrackType, ctypes.POINTER(ctypes.POINTER(MediaTrack)), ctypes.c_size_t)
    return f(p_mi, type, tracks, track_count)

def libvlc_media_player_select_tracks_by_ids(p_mi, type, psz_ids):
    '''Select tracks by their string identifier.
    @param p_mi: the media player.
    @param type: type to select.
    @param psz_ids: list of string identifier or None.
    @version: LibVLC 4.0.0 and later. This function can be used pre-select a list of tracks before starting the player. It has only effect for the current media. It can also be used when the player is already started. 'str_ids' can contain more than one track id, delimited with ','. "" or any invalid track id will cause the player to unselect all tracks of that category. None will disable the preference for newer tracks without unselecting any current tracks. Example: - (libvlc_track_video, "video/1,video/2") will select these 2 video tracks. If there is only one video track with the id "video/0", no tracks will be selected. - (L{TrackType}, "$slave_url_md5sum/spu/0) will select one spu added by an input slave with the corresponding url. @note The string identifier of a track can be found via psz_id from \ref L{MediaTrack} @note selecting multiple audio tracks is currently not supported. @warning Only use a \ref L{MediaTrack} id retrieved with \ref L{libvlc_media_player_get_tracklist}.
    '''
    f = _Cfunctions.get('libvlc_media_player_select_tracks_by_ids', None) or \
        _Cfunction('libvlc_media_player_select_tracks_by_ids', ((1,), (1,), (1,),), None,
                    None, MediaPlayer, TrackType, ctypes.c_char_p)
    return f(p_mi, type, psz_ids)

def libvlc_media_player_add_slave(p_mi, i_type, psz_uri, b_select):
    '''Add a slave to the current media player.
    @note: If the player is playing, the slave will be added directly. This call
    will also update the slave list of the attached L{Media}.
    @param p_mi: the media player.
    @param i_type: subtitle or audio.
    @param psz_uri: Uri of the slave (should contain a valid scheme).
    @param b_select: True if this slave should be selected when it's loaded.
    @return: 0 on success, -1 on error.
    @version: LibVLC 3.0.0 and later. See L{libvlc_media_slaves_add}.
    '''
    f = _Cfunctions.get('libvlc_media_player_add_slave', None) or \
        _Cfunction('libvlc_media_player_add_slave', ((1,), (1,), (1,), (1,),), None,
                    ctypes.c_int, MediaPlayer, MediaSlaveType, ctypes.c_char_p, ctypes.c_bool)
    return f(p_mi, i_type, psz_uri, b_select)

def libvlc_player_program_delete(program):
    '''Delete a program struct.
    @param program: returned by L{libvlc_media_player_get_selected_program}() or L{libvlc_media_player_get_program_from_id}().
    @version: LibVLC 4.0.0 and later.
    '''
    f = _Cfunctions.get('libvlc_player_program_delete', None) or \
        _Cfunction('libvlc_player_program_delete', ((1,),), None,
                    None, ctypes.POINTER(PlayerProgram))
    return f(program)

def libvlc_player_programlist_count(list):
    '''Get the number of programs in a programlist.
    @param list: valid programlist.
    @return: number of programs, or 0 if the list is empty.
    @version: LibVLC 4.0.0 and later.
    '''
    f = _Cfunctions.get('libvlc_player_programlist_count', None) or \
        _Cfunction('libvlc_player_programlist_count', ((1,),), None,
                    ctypes.c_size_t, ctypes.c_void_p)
    return f(list)

def libvlc_player_programlist_at(list, index):
    '''Get a program at a specific index
    @warning: The behaviour is undefined if the index is not valid.
    @param list: valid programlist.
    @param index: valid index in the range [0; count[.
    @return: a valid program (can't be None if L{libvlc_player_programlist_count}() returned a valid count).
    @version: LibVLC 4.0.0 and later.
    '''
    f = _Cfunctions.get('libvlc_player_programlist_at', None) or \
        _Cfunction('libvlc_player_programlist_at', ((1,), (1,),), None,
                    ctypes.POINTER(PlayerProgram), ctypes.c_void_p, ctypes.c_size_t)
    return f(list, index)

def libvlc_player_programlist_delete(list):
    '''Release a programlist
    @note: program structs from the list are also deleted.
    @param list: valid programlist.
    @version: LibVLC 4.0.0 and later. See L{libvlc_media_player_get_programlist}.
    '''
    f = _Cfunctions.get('libvlc_player_programlist_delete', None) or \
        _Cfunction('libvlc_player_programlist_delete', ((1,),), None,
                    None, ctypes.c_void_p)
    return f(list)

def libvlc_media_player_select_program_id(p_mi, i_group_id):
    '''Select program with a given program id.
    @note: program ids are sent via the libvlc_MediaPlayerProgramAdded event or
    can be fetch via L{libvlc_media_player_get_programlist}().
    @param p_mi: opaque media player handle.
    @param i_group_id: program id.
    @version: LibVLC 4.0.0 or later.
    '''
    f = _Cfunctions.get('libvlc_media_player_select_program_id', None) or \
        _Cfunction('libvlc_media_player_select_program_id', ((1,), (1,),), None,
                    None, MediaPlayer, ctypes.c_int)
    return f(p_mi, i_group_id)

def libvlc_media_player_get_selected_program(p_mi):
    '''Get the selected program.
    @param p_mi: opaque media player handle.
    @return: a valid program struct or None if no programs are selected. The program need to be freed with L{libvlc_player_program_delete}().
    @version: LibVLC 4.0.0 or later.
    '''
    f = _Cfunctions.get('libvlc_media_player_get_selected_program', None) or \
        _Cfunction('libvlc_media_player_get_selected_program', ((1,),), None,
                    ctypes.POINTER(PlayerProgram), MediaPlayer)
    return f(p_mi)

def libvlc_media_player_get_program_from_id(p_mi, i_group_id):
    '''Get a program struct from a program id.
    @param p_mi: opaque media player handle.
    @param i_group_id: program id.
    @return: a valid program struct or None if the i_group_id is not found. The program need to be freed with L{libvlc_player_program_delete}().
    @version: LibVLC 4.0.0 or later.
    '''
    f = _Cfunctions.get('libvlc_media_player_get_program_from_id', None) or \
        _Cfunction('libvlc_media_player_get_program_from_id', ((1,), (1,),), None,
                    ctypes.POINTER(PlayerProgram), MediaPlayer, ctypes.c_int)
    return f(p_mi, i_group_id)

def libvlc_media_player_get_programlist(p_mi):
    '''Get the program list.
    @param p_mi: the media player.
    @return: a valid libvlc_media_programlist_t or None in case of error or empty list, delete with libvlc_media_programlist_delete().
    @version: LibVLC 4.0.0 and later. @note This program list is a snapshot of the current programs when this function is called. If a program is updated after this call, the user will need to call this function again to get the updated program. The program list can be used to get program information and to select specific programs.
    '''
    f = _Cfunctions.get('libvlc_media_player_get_programlist', None) or \
        _Cfunction('libvlc_media_player_get_programlist', ((1,),), None,
                    ctypes.c_void_p, MediaPlayer)
    return f(p_mi)

def libvlc_toggle_fullscreen(p_mi):
    '''Toggle fullscreen status on non-embedded video outputs.
    @warning: The same limitations applies to this function
    as to L{libvlc_set_fullscreen}().
    @param p_mi: the media player.
    '''
    f = _Cfunctions.get('libvlc_toggle_fullscreen', None) or \
        _Cfunction('libvlc_toggle_fullscreen', ((1,),), None,
                    None, MediaPlayer)
    return f(p_mi)

def libvlc_set_fullscreen(p_mi, b_fullscreen):
    '''Enable or disable fullscreen.
    @warning: With most window managers, only a top-level windows can be in
    full-screen mode. Hence, this function will not operate properly if
    L{libvlc_media_player_set_xwindow}() was used to embed the video in a
    non-top-level window. In that case, the embedding window must be reparented
    to the root window B{before} fullscreen mode is enabled. You will want
    to reparent it back to its normal parent when disabling fullscreen.
    @note: This setting applies to any and all current or future active video
    tracks and windows for the given media player. The choice of fullscreen
    output for each window is left to the operating system.
    @param p_mi: the media player.
    @param b_fullscreen: boolean for fullscreen status.
    '''
    f = _Cfunctions.get('libvlc_set_fullscreen', None) or \
        _Cfunction('libvlc_set_fullscreen', ((1,), (1,),), None,
                    None, MediaPlayer, ctypes.c_bool)
    return f(p_mi, b_fullscreen)

def libvlc_get_fullscreen(p_mi):
    '''Get current fullscreen status.
    @param p_mi: the media player.
    @return: the fullscreen status (boolean) \retval false media player is windowed \retval true media player is in fullscreen mode.
    '''
    f = _Cfunctions.get('libvlc_get_fullscreen', None) or \
        _Cfunction('libvlc_get_fullscreen', ((1,),), None,
                    ctypes.c_bool, MediaPlayer)
    return f(p_mi)

def libvlc_video_set_key_input(p_mi, on):
    '''Enable or disable key press events handling, according to the LibVLC hotkeys
    configuration. By default and for historical reasons, keyboard events are
    handled by the LibVLC video widget.
    @note: On X11, there can be only one subscriber for key press and mouse
    click events per window. If your application has subscribed to those events
    for the X window ID of the video widget, then LibVLC will not be able to
    handle key presses and mouse clicks in any case.
    @warning: This function is only implemented for X11 and Win32 at the moment.
    @param p_mi: the media player.
    @param on: true to handle key press events, false to ignore them.
    '''
    f = _Cfunctions.get('libvlc_video_set_key_input', None) or \
        _Cfunction('libvlc_video_set_key_input', ((1,), (1,),), None,
                    None, MediaPlayer, ctypes.c_uint)
    return f(p_mi, on)

def libvlc_video_set_mouse_input(p_mi, on):
    '''Enable or disable mouse click events handling. By default, those events are
    handled. This is needed for DVD menus to work, as well as a few video
    filters such as "puzzle".
    See L{libvlc_video_set_key_input}().
    @warning: This function is only implemented for X11 and Win32 at the moment.
    @param p_mi: the media player.
    @param on: true to handle mouse click events, false to ignore them.
    '''
    f = _Cfunctions.get('libvlc_video_set_mouse_input', None) or \
        _Cfunction('libvlc_video_set_mouse_input', ((1,), (1,),), None,
                    None, MediaPlayer, ctypes.c_uint)
    return f(p_mi, on)

def libvlc_video_get_size(p_mi, num):
    '''Get the pixel dimensions of a video.
    @param p_mi: media player.
    @param num: number of the video (starting from, and most commonly 0).
    @param[out] px pointer to get the pixel width.
    @param[out] py pointer to get the pixel height.
    @return: 0 on success, -1 if the specified video does not exist.
    '''
    f = _Cfunctions.get('libvlc_video_get_size', None) or \
        _Cfunction('libvlc_video_get_size', ((1,), (1,), (2,), (2,),), None,
                    ctypes.c_int, MediaPlayer, ctypes.c_uint, ctypes.POINTER(ctypes.c_uint), ctypes.POINTER(ctypes.c_uint))
    return f(p_mi, num)

def libvlc_video_get_cursor(p_mi, num):
    '''Get the mouse pointer coordinates over a video.
    Coordinates are expressed in terms of the decoded video resolution,
    B{not} in terms of pixels on the screen/viewport (to get the latter,
    you can query your windowing system directly).
    Either of the coordinates may be negative or larger than the corresponding
    dimension of the video, if the cursor is outside the rendering area.
    @warning: The coordinates may be out-of-date if the pointer is not located
    on the video rendering area. LibVLC does not track the pointer if it is
    outside of the video widget.
    @note: LibVLC does not support multiple pointers (it does of course support
    multiple input devices sharing the same pointer) at the moment.
    @param p_mi: media player.
    @param num: number of the video (starting from, and most commonly 0).
    @param[out] px pointer to get the abscissa.
    @param[out] py pointer to get the ordinate.
    @return: 0 on success, -1 if the specified video does not exist.
    '''
    f = _Cfunctions.get('libvlc_video_get_cursor', None) or \
        _Cfunction('libvlc_video_get_cursor', ((1,), (1,), (2,), (2,),), None,
                    ctypes.c_int, MediaPlayer, ctypes.c_uint, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
    return f(p_mi, num)

def libvlc_video_get_scale(p_mi):
    '''Get the current video scaling factor.
    See also L{libvlc_video_set_scale}().
    @param p_mi: the media player.
    @return: the currently configured zoom factor, or 0. if the video is set to fit to the output window/drawable automatically.
    '''
    f = _Cfunctions.get('libvlc_video_get_scale', None) or \
        _Cfunction('libvlc_video_get_scale', ((1,),), None,
                    ctypes.c_float, MediaPlayer)
    return f(p_mi)

def libvlc_video_set_scale(p_mi, f_factor):
    '''Set the video scaling factor. That is the ratio of the number of pixels on
    screen to the number of pixels in the original decoded video in each
    dimension. Zero is a special value; it will adjust the video to the output
    window/drawable (in windowed mode) or the entire screen.
    Note that not all video outputs support scaling.
    @param p_mi: the media player.
    @param f_factor: the scaling factor, or zero.
    '''
    f = _Cfunctions.get('libvlc_video_set_scale', None) or \
        _Cfunction('libvlc_video_set_scale', ((1,), (1,),), None,
                    None, MediaPlayer, ctypes.c_float)
    return f(p_mi, f_factor)

def libvlc_video_get_aspect_ratio(p_mi):
    '''Get current video aspect ratio.
    @param p_mi: the media player.
    @return: the video aspect ratio or None if unspecified (the result must be released with free() or L{libvlc_free}()).
    '''
    f = _Cfunctions.get('libvlc_video_get_aspect_ratio', None) or \
        _Cfunction('libvlc_video_get_aspect_ratio', ((1,),), string_result,
                    ctypes.c_void_p, MediaPlayer)
    return f(p_mi)

def libvlc_video_set_aspect_ratio(p_mi, psz_aspect):
    '''Set new video aspect ratio.
    @param p_mi: the media player.
    @param psz_aspect: new video aspect-ratio or None to reset to default @note Invalid aspect ratios are ignored.
    '''
    f = _Cfunctions.get('libvlc_video_set_aspect_ratio', None) or \
        _Cfunction('libvlc_video_set_aspect_ratio', ((1,), (1,),), None,
                    None, MediaPlayer, ctypes.c_char_p)
    return f(p_mi, psz_aspect)

def libvlc_video_new_viewpoint():
    '''Create a video viewpoint structure.
    @return: video viewpoint or None (the result must be released with free()).
    @version: LibVLC 3.0.0 and later.
    '''
    f = _Cfunctions.get('libvlc_video_new_viewpoint', None) or \
        _Cfunction('libvlc_video_new_viewpoint', (), None,
                    ctypes.POINTER(VideoViewpoint))
    return f()

def libvlc_video_update_viewpoint(p_mi, p_viewpoint, b_absolute):
    '''Update the video viewpoint information.
    @note: It is safe to call this function before the media player is started.
    @param p_mi: the media player.
    @param p_viewpoint: video viewpoint allocated via L{libvlc_video_new_viewpoint}().
    @param b_absolute: if true replace the old viewpoint with the new one. If false, increase/decrease it.
    @return: -1 in case of error, 0 otherwise @note the values are set asynchronously, it will be used by the next frame displayed.
    @version: LibVLC 3.0.0 and later.
    '''
    f = _Cfunctions.get('libvlc_video_update_viewpoint', None) or \
        _Cfunction('libvlc_video_update_viewpoint', ((1,), (1,), (1,),), None,
                    ctypes.c_int, MediaPlayer, ctypes.POINTER(VideoViewpoint), ctypes.c_bool)
    return f(p_mi, p_viewpoint, b_absolute)

def libvlc_video_get_spu_delay(p_mi):
    '''Get the current subtitle delay. Positive values means subtitles are being
    displayed later, negative values earlier.
    @param p_mi: media player.
    @return: time (in microseconds) the display of subtitles is being delayed.
    @version: LibVLC 2.0.0 or later.
    '''
    f = _Cfunctions.get('libvlc_video_get_spu_delay', None) or \
        _Cfunction('libvlc_video_get_spu_delay', ((1,),), None,
                    ctypes.c_int64, MediaPlayer)
    return f(p_mi)

def libvlc_video_get_spu_text_scale(p_mi):
    '''Get the current subtitle text scale
    The scale factor is expressed as a percentage of the default size, where
    1.0 represents 100 percent.
    @param p_mi: media player.
    @version: LibVLC 4.0.0 or later.
    '''
    f = _Cfunctions.get('libvlc_video_get_spu_text_scale', None) or \
        _Cfunction('libvlc_video_get_spu_text_scale', ((1,),), None,
                    ctypes.c_float, MediaPlayer)
    return f(p_mi)

def libvlc_video_set_spu_text_scale(p_mi, f_scale):
    '''Set the subtitle text scale.
    The scale factor is expressed as a percentage of the default size, where
    1.0 represents 100 percent.
    A value of 0.5 would result in text half the normal size, and a value of 2.0
    would result in text twice the normal size.
    The minimum acceptable value for the scale factor is 0.1.
    The maximum is 5.0 (five times normal size).
    @param p_mi: media player.
    @param f_scale: scale factor in the range [0.1;5.0] (default: 1.0).
    @version: LibVLC 4.0.0 or later.
    '''
    f = _Cfunctions.get('libvlc_video_set_spu_text_scale', None) or \
        _Cfunction('libvlc_video_set_spu_text_scale', ((1,), (1,),), None,
                    None, MediaPlayer, ctypes.c_float)
    return f(p_mi, f_scale)

def libvlc_video_set_spu_delay(p_mi, i_delay):
    '''Set the subtitle delay. This affects the timing of when the subtitle will
    be displayed. Positive values result in subtitles being displayed later,
    while negative values will result in subtitles being displayed earlier.
    The subtitle delay will be reset to zero each time the media changes.
    @param p_mi: media player.
    @param i_delay: time (in microseconds) the display of subtitles should be delayed.
    @return: 0 on success, -1 on error.
    @version: LibVLC 2.0.0 or later.
    '''
    f = _Cfunctions.get('libvlc_video_set_spu_delay', None) or \
        _Cfunction('libvlc_video_set_spu_delay', ((1,), (1,),), None,
                    ctypes.c_int, MediaPlayer, ctypes.c_int64)
    return f(p_mi, i_delay)

def libvlc_media_player_get_full_title_descriptions(p_mi, titles):
    '''Get the full description of available titles.
    @param p_mi: the media player.
    @param[out] titles address to store an allocated array of title descriptions descriptions (must be freed with L{libvlc_title_descriptions_release}() by the caller).
    @return: the number of titles (-1 on error).
    @version: LibVLC 3.0.0 and later.
    '''
    f = _Cfunctions.get('libvlc_media_player_get_full_title_descriptions', None) or \
        _Cfunction('libvlc_media_player_get_full_title_descriptions', ((1,), (1,),), None,
                    ctypes.c_int, MediaPlayer, ctypes.POINTER(ctypes.POINTER(TitleDescription)))
    return f(p_mi, titles)

def libvlc_title_descriptions_release(p_titles, i_count):
    '''Release a title description.
    @param p_titles: title description array to release.
    @param i_count: number of title descriptions to release.
    @version: LibVLC 3.0.0 and later.
    '''
    f = _Cfunctions.get('libvlc_title_descriptions_release', None) or \
        _Cfunction('libvlc_title_descriptions_release', ((1,), (1,),), None,
                    None, ctypes.POINTER(ctypes.POINTER(TitleDescription)), ctypes.c_uint)
    return f(p_titles, i_count)

def libvlc_media_player_get_full_chapter_descriptions(p_mi, i_chapters_of_title, pp_chapters):
    '''Get the full description of available chapters.
    @param p_mi: the media player.
    @param i_chapters_of_title: index of the title to query for chapters (uses current title if set to -1).
    @param[out] pp_chapters address to store an allocated array of chapter descriptions descriptions (must be freed with L{libvlc_chapter_descriptions_release}() by the caller).
    @return: the number of chapters (-1 on error).
    @version: LibVLC 3.0.0 and later.
    '''
    f = _Cfunctions.get('libvlc_media_player_get_full_chapter_descriptions', None) or \
        _Cfunction('libvlc_media_player_get_full_chapter_descriptions', ((1,), (1,), (1,),), None,
                    ctypes.c_int, MediaPlayer, ctypes.c_int, ctypes.POINTER(ctypes.POINTER(ChapterDescription)))
    return f(p_mi, i_chapters_of_title, pp_chapters)

def libvlc_chapter_descriptions_release(p_chapters, i_count):
    '''Release a chapter description.
    @param p_chapters: chapter description array to release.
    @param i_count: number of chapter descriptions to release.
    @version: LibVLC 3.0.0 and later.
    '''
    f = _Cfunctions.get('libvlc_chapter_descriptions_release', None) or \
        _Cfunction('libvlc_chapter_descriptions_release', ((1,), (1,),), None,
                    None, ctypes.POINTER(ctypes.POINTER(ChapterDescription)), ctypes.c_uint)
    return f(p_chapters, i_count)

def libvlc_video_set_crop_ratio(mp, num, den):
    '''Set/unset the video crop ratio.
    This function forces a crop ratio on any and all video tracks rendered by
    the media player. If the display aspect ratio of a video does not match the
    crop ratio, either the top and bottom, or the left and right of the video
    will be cut out to fit the crop ratio.
    For instance, a ratio of 1:1 will force the video to a square shape.
    To disable video crop, set a crop ratio with zero as denominator.
    A call to this function overrides any previous call to any of
    L{libvlc_video_set_crop_ratio}(), L{libvlc_video_set_crop_border}() and/or
    L{libvlc_video_set_crop_window}().
    See L{libvlc_video_set_aspect_ratio}().
    @param mp: the media player.
    @param num: crop ratio numerator (ignored if denominator is 0).
    @param den: crop ratio denominator (or 0 to unset the crop ratio).
    @version: LibVLC 4.0.0 and later.
    '''
    f = _Cfunctions.get('libvlc_video_set_crop_ratio', None) or \
        _Cfunction('libvlc_video_set_crop_ratio', ((1,), (1,), (1,),), None,
                    None, MediaPlayer, ctypes.c_uint, ctypes.c_uint)
    return f(mp, num, den)

def libvlc_video_set_crop_window(mp, x, y, width, height):
    '''Set the video crop window.
    This function selects a sub-rectangle of video to show. Any pixels outside
    the rectangle will not be shown.
    To unset the video crop window, use L{libvlc_video_set_crop_ratio}() or
    L{libvlc_video_set_crop_border}().
    A call to this function overrides any previous call to any of
    L{libvlc_video_set_crop_ratio}(), L{libvlc_video_set_crop_border}() and/or
    L{libvlc_video_set_crop_window}().
    @param mp: the media player.
    @param x: abscissa (i.e. leftmost sample column offset) of the crop window.
    @param y: ordinate (i.e. topmost sample row offset) of the crop window.
    @param width: sample width of the crop window (cannot be zero).
    @param height: sample height of the crop window (cannot be zero).
    @version: LibVLC 4.0.0 and later.
    '''
    f = _Cfunctions.get('libvlc_video_set_crop_window', None) or \
        _Cfunction('libvlc_video_set_crop_window', ((1,), (1,), (1,), (1,), (1,),), None,
                    None, MediaPlayer, ctypes.c_uint, ctypes.c_uint, ctypes.c_uint, ctypes.c_uint)
    return f(mp, x, y, width, height)

def libvlc_video_set_crop_border(mp, left, right, top, bottom):
    '''Set the video crop borders.
    This function selects the size of video edges to be cropped out.
    To unset the video crop borders, set all borders to zero.
    A call to this function overrides any previous call to any of
    L{libvlc_video_set_crop_ratio}(), L{libvlc_video_set_crop_border}() and/or
    L{libvlc_video_set_crop_window}().
    @param mp: the media player.
    @param left: number of sample columns to crop on the left.
    @param right: number of sample columns to crop on the right.
    @param top: number of sample rows to crop on the top.
    @param bottom: number of sample rows to corp on the bottom.
    @version: LibVLC 4.0.0 and later.
    '''
    f = _Cfunctions.get('libvlc_video_set_crop_border', None) or \
        _Cfunction('libvlc_video_set_crop_border', ((1,), (1,), (1,), (1,), (1,),), None,
                    None, MediaPlayer, ctypes.c_uint, ctypes.c_uint, ctypes.c_uint, ctypes.c_uint)
    return f(mp, left, right, top, bottom)

def libvlc_video_get_teletext(p_mi):
    '''Get current teletext page requested or 0 if it's disabled.
    Teletext is disabled by default, call L{libvlc_video_set_teletext}() to enable
    it.
    @param p_mi: the media player.
    @return: the current teletext page requested.
    '''
    f = _Cfunctions.get('libvlc_video_get_teletext', None) or \
        _Cfunction('libvlc_video_get_teletext', ((1,),), None,
                    ctypes.c_int, MediaPlayer)
    return f(p_mi)

def libvlc_video_set_teletext(p_mi, i_page):
    '''Set new teletext page to retrieve.
    This function can also be used to send a teletext key.
    @param p_mi: the media player.
    @param i_page: teletex page number requested. This value can be 0 to disable teletext, a number in the range ]0;1000[ to show the requested page, or a \ref L{TeletextKey}. 100 is the default teletext page.
    '''
    f = _Cfunctions.get('libvlc_video_set_teletext', None) or \
        _Cfunction('libvlc_video_set_teletext', ((1,), (1,),), None,
                    None, MediaPlayer, ctypes.c_int)
    return f(p_mi, i_page)

def libvlc_video_take_snapshot(p_mi, num, psz_filepath, i_width, i_height):
    '''Take a snapshot of the current video window.
    If i_width AND i_height is 0, original size is used.
    If i_width XOR i_height is 0, original aspect-ratio is preserved.
    @param p_mi: media player instance.
    @param num: number of video output (typically 0 for the first/only one).
    @param psz_filepath: the path of a file or a folder to save the screenshot into.
    @param i_width: the snapshot's width.
    @param i_height: the snapshot's height.
    @return: 0 on success, -1 if the video was not found.
    '''
    f = _Cfunctions.get('libvlc_video_take_snapshot', None) or \
        _Cfunction('libvlc_video_take_snapshot', ((1,), (1,), (1,), (1,), (1,),), None,
                    ctypes.c_int, MediaPlayer, ctypes.c_uint, ctypes.c_char_p, ctypes.c_uint, ctypes.c_uint)
    return f(p_mi, num, psz_filepath, i_width, i_height)

def libvlc_video_set_deinterlace(p_mi, deinterlace, psz_mode):
    '''Enable or disable deinterlace filter.
    @param p_mi: libvlc media player.
    @param deinterlace: state -1: auto (default), 0: disabled, 1: enabled.
    @param psz_mode: type of deinterlace filter, None for current/default filter.
    @version: LibVLC 4.0.0 and later.
    '''
    f = _Cfunctions.get('libvlc_video_set_deinterlace', None) or \
        _Cfunction('libvlc_video_set_deinterlace', ((1,), (1,), (1,),), None,
                    None, MediaPlayer, ctypes.c_int, ctypes.c_char_p)
    return f(p_mi, deinterlace, psz_mode)

def libvlc_video_get_marquee_int(p_mi, option):
    '''Get an integer marquee option value.
    @param p_mi: libvlc media player.
    @param option: marq option to get See L{VideoMarqueeOption}.
    '''
    f = _Cfunctions.get('libvlc_video_get_marquee_int', None) or \
        _Cfunction('libvlc_video_get_marquee_int', ((1,), (1,),), None,
                    ctypes.c_int, MediaPlayer, ctypes.c_uint)
    return f(p_mi, option)

def libvlc_video_set_marquee_int(p_mi, option, i_val):
    '''Enable, disable or set an integer marquee option
    Setting libvlc_marquee_Enable has the side effect of enabling (arg !0)
    or disabling (arg 0) the marq filter.
    @param p_mi: libvlc media player.
    @param option: marq option to set See L{VideoMarqueeOption}.
    @param i_val: marq option value.
    '''
    f = _Cfunctions.get('libvlc_video_set_marquee_int', None) or \
        _Cfunction('libvlc_video_set_marquee_int', ((1,), (1,), (1,),), None,
                    None, MediaPlayer, ctypes.c_uint, ctypes.c_int)
    return f(p_mi, option, i_val)

def libvlc_video_set_marquee_string(p_mi, option, psz_text):
    '''Set a marquee string option.
    @param p_mi: libvlc media player.
    @param option: marq option to set See L{VideoMarqueeOption}.
    @param psz_text: marq option value.
    '''
    f = _Cfunctions.get('libvlc_video_set_marquee_string', None) or \
        _Cfunction('libvlc_video_set_marquee_string', ((1,), (1,), (1,),), None,
                    None, MediaPlayer, ctypes.c_uint, ctypes.c_char_p)
    return f(p_mi, option, psz_text)

def libvlc_video_get_logo_int(p_mi, option):
    '''Get integer logo option.
    @param p_mi: libvlc media player instance.
    @param option: logo option to get, values of L{VideoLogoOption}.
    '''
    f = _Cfunctions.get('libvlc_video_get_logo_int', None) or \
        _Cfunction('libvlc_video_get_logo_int', ((1,), (1,),), None,
                    ctypes.c_int, MediaPlayer, ctypes.c_uint)
    return f(p_mi, option)

def libvlc_video_set_logo_int(p_mi, option, value):
    '''Set logo option as integer. Options that take a different type value
    are ignored.
    Passing libvlc_logo_enable as option value has the side effect of
    starting (arg !0) or stopping (arg 0) the logo filter.
    @param p_mi: libvlc media player instance.
    @param option: logo option to set, values of L{VideoLogoOption}.
    @param value: logo option value.
    '''
    f = _Cfunctions.get('libvlc_video_set_logo_int', None) or \
        _Cfunction('libvlc_video_set_logo_int', ((1,), (1,), (1,),), None,
                    None, MediaPlayer, ctypes.c_uint, ctypes.c_int)
    return f(p_mi, option, value)

def libvlc_video_set_logo_string(p_mi, option, psz_value):
    '''Set logo option as string. Options that take a different type value
    are ignored.
    @param p_mi: libvlc media player instance.
    @param option: logo option to set, values of L{VideoLogoOption}.
    @param psz_value: logo option value.
    '''
    f = _Cfunctions.get('libvlc_video_set_logo_string', None) or \
        _Cfunction('libvlc_video_set_logo_string', ((1,), (1,), (1,),), None,
                    None, MediaPlayer, ctypes.c_uint, ctypes.c_char_p)
    return f(p_mi, option, psz_value)

def libvlc_video_get_adjust_int(p_mi, option):
    '''Get integer adjust option.
    @param p_mi: libvlc media player instance.
    @param option: adjust option to get, values of L{VideoAdjustOption}.
    @version: LibVLC 1.1.1 and later.
    '''
    f = _Cfunctions.get('libvlc_video_get_adjust_int', None) or \
        _Cfunction('libvlc_video_get_adjust_int', ((1,), (1,),), None,
                    ctypes.c_int, MediaPlayer, ctypes.c_uint)
    return f(p_mi, option)

def libvlc_video_set_adjust_int(p_mi, option, value):
    '''Set adjust option as integer. Options that take a different type value
    are ignored.
    Passing libvlc_adjust_enable as option value has the side effect of
    starting (arg !0) or stopping (arg 0) the adjust filter.
    @param p_mi: libvlc media player instance.
    @param option: adust option to set, values of L{VideoAdjustOption}.
    @param value: adjust option value.
    @version: LibVLC 1.1.1 and later.
    '''
    f = _Cfunctions.get('libvlc_video_set_adjust_int', None) or \
        _Cfunction('libvlc_video_set_adjust_int', ((1,), (1,), (1,),), None,
                    None, MediaPlayer, ctypes.c_uint, ctypes.c_int)
    return f(p_mi, option, value)

def libvlc_video_get_adjust_float(p_mi, option):
    '''Get float adjust option.
    @param p_mi: libvlc media player instance.
    @param option: adjust option to get, values of L{VideoAdjustOption}.
    @version: LibVLC 1.1.1 and later.
    '''
    f = _Cfunctions.get('libvlc_video_get_adjust_float', None) or \
        _Cfunction('libvlc_video_get_adjust_float', ((1,), (1,),), None,
                    ctypes.c_float, MediaPlayer, ctypes.c_uint)
    return f(p_mi, option)

def libvlc_video_set_adjust_float(p_mi, option, value):
    '''Set adjust option as float. Options that take a different type value
    are ignored.
    @param p_mi: libvlc media player instance.
    @param option: adust option to set, values of L{VideoAdjustOption}.
    @param value: adjust option value.
    @version: LibVLC 1.1.1 and later.
    '''
    f = _Cfunctions.get('libvlc_video_set_adjust_float', None) or \
        _Cfunction('libvlc_video_set_adjust_float', ((1,), (1,), (1,),), None,
                    None, MediaPlayer, ctypes.c_uint, ctypes.c_float)
    return f(p_mi, option, value)

def libvlc_audio_output_list_get(p_instance):
    '''Gets the list of available audio output modules.
    @param p_instance: libvlc instance.
    @return: list of available audio outputs. It must be freed with In case of error, None is returned.
    '''
    f = _Cfunctions.get('libvlc_audio_output_list_get', None) or \
        _Cfunction('libvlc_audio_output_list_get', ((1,),), None,
                    ctypes.POINTER(AudioOutput), Instance)
    return f(p_instance)

def libvlc_audio_output_list_release(p_list):
    '''Frees the list of available audio output modules.
    @param p_list: list with audio outputs for release.
    '''
    f = _Cfunctions.get('libvlc_audio_output_list_release', None) or \
        _Cfunction('libvlc_audio_output_list_release', ((1,),), None,
                    None, ctypes.POINTER(AudioOutput))
    return f(p_list)

def libvlc_audio_output_set(p_mi, psz_name):
    '''Selects an audio output module.
    @note: Any change will take be effect only after playback is stopped and
    restarted. Audio output cannot be changed while playing.
    @param p_mi: media player.
    @param psz_name: name of audio output, use psz_name of See L{AudioOutput}.
    @return: 0 if function succeeded, -1 on error.
    '''
    f = _Cfunctions.get('libvlc_audio_output_set', None) or \
        _Cfunction('libvlc_audio_output_set', ((1,), (1,),), None,
                    ctypes.c_int, MediaPlayer, ctypes.c_char_p)
    return f(p_mi, psz_name)

def libvlc_audio_output_device_enum(mp):
    '''Gets a list of potential audio output devices.
    See also L{libvlc_audio_output_device_set}().
    @note: Not all audio outputs support enumerating devices.
    The audio output may be functional even if the list is empty (None).
    @note: The list may not be exhaustive.
    @warning: Some audio output devices in the list might not actually work in
    some circumstances. By default, it is recommended to not specify any
    explicit audio device.
    @param mp: media player.
    @return: A None-terminated linked list of potential audio output devices. It must be freed with L{libvlc_audio_output_device_list_release}().
    @version: LibVLC 2.2.0 or later.
    '''
    f = _Cfunctions.get('libvlc_audio_output_device_enum', None) or \
        _Cfunction('libvlc_audio_output_device_enum', ((1,),), None,
                    ctypes.POINTER(AudioOutputDevice), MediaPlayer)
    return f(mp)

def libvlc_audio_output_device_list_release(p_list):
    '''Frees a list of available audio output devices.
    @param p_list: list with audio outputs for release.
    @version: LibVLC 2.1.0 or later.
    '''
    f = _Cfunctions.get('libvlc_audio_output_device_list_release', None) or \
        _Cfunction('libvlc_audio_output_device_list_release', ((1,),), None,
                    None, ctypes.POINTER(AudioOutputDevice))
    return f(p_list)

def libvlc_audio_output_device_set(mp, device_id):
    '''Configures an explicit audio output device.
    A list of adequate potential device strings can be obtained with
    L{libvlc_audio_output_device_enum}().
    @note: This function does not select the specified audio output plugin.
    L{libvlc_audio_output_set}() is used for that purpose.
    @warning: The syntax for the device parameter depends on the audio output.
    Some audio output modules require further parameters (e.g. a channels map
    in the case of ALSA).
    @param mp: media player.
    @param device_id: device identifier string (see \ref L{AudioOutputDevice}::psz_device).
    @return: If the change of device was requested succesfully, zero is returned (the actual change is asynchronous and not guaranteed to succeed). On error, a non-zero value is returned.
    @version: This function originally expected three parameters. The middle parameter was removed from LibVLC 4.0 onward.
    '''
    f = _Cfunctions.get('libvlc_audio_output_device_set', None) or \
        _Cfunction('libvlc_audio_output_device_set', ((1,), (1,),), None,
                    ctypes.c_int, MediaPlayer, ctypes.c_char_p)
    return f(mp, device_id)

def libvlc_audio_output_device_get(mp):
    '''Get the current audio output device identifier.
    This complements L{libvlc_audio_output_device_set}().
    @warning: The initial value for the current audio output device identifier
    may not be set or may be some unknown value. A LibVLC application should
    compare this value against the known device identifiers (e.g. those that
    were previously retrieved by a call to L{libvlc_audio_output_device_enum}) to
    find the current audio output device.
    It is possible that the selected audio output device changes (an external
    change) without a call to L{libvlc_audio_output_device_set}. That may make this
    method unsuitable to use if a LibVLC application is attempting to track
    dynamic audio device changes as they happen.
    @param mp: media player.
    @return: the current audio output device identifier None if no device is selected or in case of error (the result must be released with free()).
    @version: LibVLC 3.0.0 or later.
    '''
    f = _Cfunctions.get('libvlc_audio_output_device_get', None) or \
        _Cfunction('libvlc_audio_output_device_get', ((1,),), string_result,
                    ctypes.c_void_p, MediaPlayer)
    return f(mp)

def libvlc_audio_toggle_mute(p_mi):
    '''Toggle mute status.
    @param p_mi: media player @warning Toggling mute atomically is not always possible: On some platforms, other processes can mute the VLC audio playback stream asynchronously. Thus, there is a small race condition where toggling will not work. See also the limitations of L{libvlc_audio_set_mute}().
    '''
    f = _Cfunctions.get('libvlc_audio_toggle_mute', None) or \
        _Cfunction('libvlc_audio_toggle_mute', ((1,),), None,
                    None, MediaPlayer)
    return f(p_mi)

def libvlc_audio_get_mute(p_mi):
    '''Get current mute status.
    @param p_mi: media player.
    @return: the mute status (boolean) if defined, -1 if undefined/unapplicable.
    '''
    f = _Cfunctions.get('libvlc_audio_get_mute', None) or \
        _Cfunction('libvlc_audio_get_mute', ((1,),), None,
                    ctypes.c_int, MediaPlayer)
    return f(p_mi)

def libvlc_audio_set_mute(p_mi, status):
    '''Set mute status.
    @param p_mi: media player.
    @param status: If status is true then mute, otherwise unmute @warning This function does not always work. If there are no active audio playback stream, the mute status might not be available. If digital pass-through (S/PDIF, HDMI...) is in use, muting may be unapplicable. Also some audio output plugins do not support muting at all. @note To force silent playback, disable all audio tracks. This is more efficient and reliable than mute.
    '''
    f = _Cfunctions.get('libvlc_audio_set_mute', None) or \
        _Cfunction('libvlc_audio_set_mute', ((1,), (1,),), None,
                    None, MediaPlayer, ctypes.c_int)
    return f(p_mi, status)

def libvlc_audio_get_volume(p_mi):
    '''Get current software audio volume.
    @param p_mi: media player.
    @return: the software volume in percents (0 = mute, 100 = nominal / 0dB).
    '''
    f = _Cfunctions.get('libvlc_audio_get_volume', None) or \
        _Cfunction('libvlc_audio_get_volume', ((1,),), None,
                    ctypes.c_int, MediaPlayer)
    return f(p_mi)

def libvlc_audio_set_volume(p_mi, i_volume):
    '''Set current software audio volume.
    @param p_mi: media player.
    @param i_volume: the volume in percents (0 = mute, 100 = 0dB).
    @return: 0 if the volume was set, -1 if it was out of range.
    '''
    f = _Cfunctions.get('libvlc_audio_set_volume', None) or \
        _Cfunction('libvlc_audio_set_volume', ((1,), (1,),), None,
                    ctypes.c_int, MediaPlayer, ctypes.c_int)
    return f(p_mi, i_volume)

def libvlc_audio_get_stereomode(p_mi):
    '''Get current audio stereo-mode.
    @param p_mi: media player.
    @return: the audio stereo-mode, See L{AudioOutputStereomode}.
    @version: LibVLC 4.0.0 or later.
    '''
    f = _Cfunctions.get('libvlc_audio_get_stereomode', None) or \
        _Cfunction('libvlc_audio_get_stereomode', ((1,),), None,
                    AudioOutputStereomode, MediaPlayer)
    return f(p_mi)

def libvlc_audio_set_stereomode(p_mi, mode):
    '''Set current audio stereo-mode.
    @param p_mi: media player.
    @param channel: the audio stereo-mode, See L{AudioOutputStereomode}.
    @return: 0 on success, -1 on error.
    @version: LibVLC 4.0.0 or later.
    '''
    f = _Cfunctions.get('libvlc_audio_set_stereomode', None) or \
        _Cfunction('libvlc_audio_set_stereomode', ((1,), (1,),), None,
                    ctypes.c_int, MediaPlayer, AudioOutputStereomode)
    return f(p_mi, mode)

def libvlc_audio_get_mixmode(p_mi):
    '''Get current audio mix-mode.
    @param p_mi: media player.
    @return: the audio mix-mode, See L{AudioOutputMixmode}.
    @version: LibVLC 4.0.0 or later.
    '''
    f = _Cfunctions.get('libvlc_audio_get_mixmode', None) or \
        _Cfunction('libvlc_audio_get_mixmode', ((1,),), None,
                    AudioOutputMixmode, MediaPlayer)
    return f(p_mi)

def libvlc_audio_set_mixmode(p_mi, mode):
    '''Set current audio mix-mode.
    By default (libvlc_AudioMixMode_Unset), the audio output will keep its
    original channel configuration (play stereo as stereo, or 5.1 as 5.1). Yet,
    the OS and Audio API might refuse a channel configuration and asks VLC to
    adapt (Stereo played as 5.1 or vice-versa).
    This function allows to force a channel configuration, it will only work if
    the OS and Audio API accept this configuration (otherwise, it won't have any
    effects). Here are some examples:
     - Play multi-channels (5.1, 7.1...) as stereo (libvlc_AudioMixMode_Stereo)
     - Play Stereo or 5.1 as 7.1 (libvlc_AudioMixMode_7_1)
     - Play multi-channels as stereo with a binaural effect
     (libvlc_AudioMixMode_Binaural). It might be selected automatically if the
     OS and Audio API can detect if a headphone is plugged.
    @param p_mi: media player.
    @param channel: the audio mix-mode, See L{AudioOutputMixmode}.
    @return: 0 on success, -1 on error.
    @version: LibVLC 4.0.0 or later.
    '''
    f = _Cfunctions.get('libvlc_audio_set_mixmode', None) or \
        _Cfunction('libvlc_audio_set_mixmode', ((1,), (1,),), None,
                    ctypes.c_int, MediaPlayer, AudioOutputMixmode)
    return f(p_mi, mode)

def libvlc_audio_get_delay(p_mi):
    '''Get current audio delay.
    @param p_mi: media player.
    @return: the audio delay (microseconds).
    @version: LibVLC 1.1.1 or later.
    '''
    f = _Cfunctions.get('libvlc_audio_get_delay', None) or \
        _Cfunction('libvlc_audio_get_delay', ((1,),), None,
                    ctypes.c_int64, MediaPlayer)
    return f(p_mi)

def libvlc_audio_set_delay(p_mi, i_delay):
    '''Set current audio delay. The audio delay will be reset to zero each time the media changes.
    @param p_mi: media player.
    @param i_delay: the audio delay (microseconds).
    @return: 0 on success, -1 on error.
    @version: LibVLC 1.1.1 or later.
    '''
    f = _Cfunctions.get('libvlc_audio_set_delay', None) or \
        _Cfunction('libvlc_audio_set_delay', ((1,), (1,),), None,
                    ctypes.c_int, MediaPlayer, ctypes.c_int64)
    return f(p_mi, i_delay)

def libvlc_audio_equalizer_get_preset_count():
    '''Get the number of equalizer presets.
    @return: number of presets.
    @version: LibVLC 2.2.0 or later.
    '''
    f = _Cfunctions.get('libvlc_audio_equalizer_get_preset_count', None) or \
        _Cfunction('libvlc_audio_equalizer_get_preset_count', (), None,
                    ctypes.c_uint)
    return f()

def libvlc_audio_equalizer_get_preset_name(u_index):
    '''Get the name of a particular equalizer preset.
    This name can be used, for example, to prepare a preset label or menu in a user
    interface.
    @param u_index: index of the preset, counting from zero.
    @return: preset name, or None if there is no such preset.
    @version: LibVLC 2.2.0 or later.
    '''
    f = _Cfunctions.get('libvlc_audio_equalizer_get_preset_name', None) or \
        _Cfunction('libvlc_audio_equalizer_get_preset_name', ((1,),), None,
                    ctypes.c_char_p, ctypes.c_uint)
    return f(u_index)

def libvlc_audio_equalizer_get_band_count():
    '''Get the number of distinct frequency bands for an equalizer.
    @return: number of frequency bands.
    @version: LibVLC 2.2.0 or later.
    '''
    f = _Cfunctions.get('libvlc_audio_equalizer_get_band_count', None) or \
        _Cfunction('libvlc_audio_equalizer_get_band_count', (), None,
                    ctypes.c_uint)
    return f()

def libvlc_audio_equalizer_get_band_frequency(u_index):
    '''Get a particular equalizer band frequency.
    This value can be used, for example, to create a label for an equalizer band control
    in a user interface.
    @param u_index: index of the band, counting from zero.
    @return: equalizer band frequency (Hz), or -1 if there is no such band.
    @version: LibVLC 2.2.0 or later.
    '''
    f = _Cfunctions.get('libvlc_audio_equalizer_get_band_frequency', None) or \
        _Cfunction('libvlc_audio_equalizer_get_band_frequency', ((1,),), None,
                    ctypes.c_float, ctypes.c_uint)
    return f(u_index)

def libvlc_audio_equalizer_new():
    '''Create a new default equalizer, with all frequency values zeroed.
    The new equalizer can subsequently be applied to a media player by invoking
    L{libvlc_media_player_set_equalizer}().
    The returned handle should be freed via L{libvlc_audio_equalizer_release}() when
    it is no longer needed.
    @return: opaque equalizer handle, or None on error.
    @version: LibVLC 2.2.0 or later.
    '''
    f = _Cfunctions.get('libvlc_audio_equalizer_new', None) or \
        _Cfunction('libvlc_audio_equalizer_new', (), class_result(AudioEqualizer),
                    ctypes.c_void_p)
    return f()

def libvlc_audio_equalizer_new_from_preset(u_index):
    '''Create a new equalizer, with initial frequency values copied from an existing
    preset.
    The new equalizer can subsequently be applied to a media player by invoking
    L{libvlc_media_player_set_equalizer}().
    The returned handle should be freed via L{libvlc_audio_equalizer_release}() when
    it is no longer needed.
    @param u_index: index of the preset, counting from zero.
    @return: opaque equalizer handle, or None on error (it must be released with L{libvlc_audio_equalizer_release}()).
    @version: LibVLC 2.2.0 or later.
    '''
    f = _Cfunctions.get('libvlc_audio_equalizer_new_from_preset', None) or \
        _Cfunction('libvlc_audio_equalizer_new_from_preset', ((1,),), class_result(AudioEqualizer),
                    ctypes.c_void_p, ctypes.c_uint)
    return f(u_index)

def libvlc_audio_equalizer_release(p_equalizer):
    '''Release a previously created equalizer instance.
    The equalizer was previously created by using L{libvlc_audio_equalizer_new}() or
    L{libvlc_audio_equalizer_new_from_preset}().
    It is safe to invoke this method with a None p_equalizer parameter for no effect.
    @param p_equalizer: opaque equalizer handle, or None.
    @version: LibVLC 2.2.0 or later.
    '''
    f = _Cfunctions.get('libvlc_audio_equalizer_release', None) or \
        _Cfunction('libvlc_audio_equalizer_release', ((1,),), None,
                    None, AudioEqualizer)
    return f(p_equalizer)

def libvlc_audio_equalizer_set_preamp(p_equalizer, f_preamp):
    '''Set a new pre-amplification value for an equalizer.
    The new equalizer settings are subsequently applied to a media player by invoking
    L{libvlc_media_player_set_equalizer}().
    The supplied amplification value will be clamped to the -20.0 to +20.0 range.
    @param p_equalizer: valid equalizer handle, must not be None.
    @param f_preamp: preamp value (-20.0 to 20.0 Hz).
    @return: zero on success, -1 on error.
    @version: LibVLC 2.2.0 or later.
    '''
    f = _Cfunctions.get('libvlc_audio_equalizer_set_preamp', None) or \
        _Cfunction('libvlc_audio_equalizer_set_preamp', ((1,), (1,),), None,
                    ctypes.c_int, AudioEqualizer, ctypes.c_float)
    return f(p_equalizer, f_preamp)

def libvlc_audio_equalizer_get_preamp(p_equalizer):
    '''Get the current pre-amplification value from an equalizer.
    @param p_equalizer: valid equalizer handle, must not be None.
    @return: preamp value (Hz).
    @version: LibVLC 2.2.0 or later.
    '''
    f = _Cfunctions.get('libvlc_audio_equalizer_get_preamp', None) or \
        _Cfunction('libvlc_audio_equalizer_get_preamp', ((1,),), None,
                    ctypes.c_float, AudioEqualizer)
    return f(p_equalizer)

def libvlc_audio_equalizer_set_amp_at_index(p_equalizer, f_amp, u_band):
    '''Set a new amplification value for a particular equalizer frequency band.
    The new equalizer settings are subsequently applied to a media player by invoking
    L{libvlc_media_player_set_equalizer}().
    The supplied amplification value will be clamped to the -20.0 to +20.0 range.
    @param p_equalizer: valid equalizer handle, must not be None.
    @param f_amp: amplification value (-20.0 to 20.0 Hz).
    @param u_band: index, counting from zero, of the frequency band to set.
    @return: zero on success, -1 on error.
    @version: LibVLC 2.2.0 or later.
    '''
    f = _Cfunctions.get('libvlc_audio_equalizer_set_amp_at_index', None) or \
        _Cfunction('libvlc_audio_equalizer_set_amp_at_index', ((1,), (1,), (1,),), None,
                    ctypes.c_int, AudioEqualizer, ctypes.c_float, ctypes.c_uint)
    return f(p_equalizer, f_amp, u_band)

def libvlc_audio_equalizer_get_amp_at_index(p_equalizer, u_band):
    '''Get the amplification value for a particular equalizer frequency band.
    @param p_equalizer: valid equalizer handle, must not be None.
    @param u_band: index, counting from zero, of the frequency band to get.
    @return: amplification value (Hz); NaN if there is no such frequency band.
    @version: LibVLC 2.2.0 or later.
    '''
    f = _Cfunctions.get('libvlc_audio_equalizer_get_amp_at_index', None) or \
        _Cfunction('libvlc_audio_equalizer_get_amp_at_index', ((1,), (1,),), None,
                    ctypes.c_float, AudioEqualizer, ctypes.c_uint)
    return f(p_equalizer, u_band)

def libvlc_media_player_set_equalizer(p_mi, p_equalizer):
    '''Apply new equalizer settings to a media player.
    The equalizer is first created by invoking L{libvlc_audio_equalizer_new}() or
    L{libvlc_audio_equalizer_new_from_preset}().
    It is possible to apply new equalizer settings to a media player whether the media
    player is currently playing media or not.
    Invoking this method will immediately apply the new equalizer settings to the audio
    output of the currently playing media if there is any.
    If there is no currently playing media, the new equalizer settings will be applied
    later if and when new media is played.
    Equalizer settings will automatically be applied to subsequently played media.
    To disable the equalizer for a media player invoke this method passing None for the
    p_equalizer parameter.
    The media player does not keep a reference to the supplied equalizer so it is safe
    for an application to release the equalizer reference any time after this method
    returns.
    @param p_mi: opaque media player handle.
    @param p_equalizer: opaque equalizer handle, or None to disable the equalizer for this media player.
    @return: zero on success, -1 on error.
    @version: LibVLC 2.2.0 or later.
    '''
    f = _Cfunctions.get('libvlc_media_player_set_equalizer', None) or \
        _Cfunction('libvlc_media_player_set_equalizer', ((1,), (1,),), None,
                    ctypes.c_int, MediaPlayer, AudioEqualizer)
    return f(p_mi, p_equalizer)

def libvlc_media_player_get_role(p_mi):
    '''Gets the media role.
    @param p_mi: media player.
    @return: the media player role (\ref libvlc_media_player_role_t).
    @version: LibVLC 3.0.0 and later.
    '''
    f = _Cfunctions.get('libvlc_media_player_get_role', None) or \
        _Cfunction('libvlc_media_player_get_role', ((1,),), None,
                    ctypes.c_int, MediaPlayer)
    return f(p_mi)

def libvlc_media_player_set_role(p_mi, role):
    '''Sets the media role.
    @param p_mi: media player.
    @param role: the media player role (\ref libvlc_media_player_role_t).
    @return: 0 on success, -1 on error.
    '''
    f = _Cfunctions.get('libvlc_media_player_set_role', None) or \
        _Cfunction('libvlc_media_player_set_role', ((1,), (1,),), None,
                    ctypes.c_int, MediaPlayer, ctypes.c_uint)
    return f(p_mi, role)

def libvlc_media_player_record(p_mi, enable, dir_path):
    '''Start/stop recording
    @note: The user should listen to the libvlc_MediaPlayerRecordChanged event,
    to monitor the recording state.
    @param p_mi: media player.
    @param enable: true to start recording, false to stop.
    @param dir_path: path of the recording directory or None (use default path), has only an effect when first enabling recording.
    @version: LibVLC 4.0.0 and later.
    '''
    f = _Cfunctions.get('libvlc_media_player_record', None) or \
        _Cfunction('libvlc_media_player_record', ((1,), (1,), (1,),), None,
                    None, MediaPlayer, ctypes.c_bool, ctypes.c_char_p)
    return f(p_mi, enable, dir_path)

def libvlc_media_player_watch_time(p_mi, min_period_us, on_update, on_discontinuity, cbs_data):
    '''Watch for times updates
    @warning: Only one watcher can be registered at a time. Calling this function
    a second time (if L{libvlc_media_player_unwatch_time}() was not called
    in-between) will fail.
    @param p_mi: the media player.
    @param min_period_us: corresponds to the minimum period, in us, between each updates, use it to avoid flood from too many source updates, set it to 0 to receive all updates.
    @param on_update: callback to listen to update events (must not be None).
    @param on_discontinuity: callback to listen to discontinuity events (can be be None).
    @param cbs_data: opaque pointer used by the callbacks.
    @return: 0 on success, -1 on error (allocation error, or if already watching).
    @version: LibVLC 4.0.0 or later.
    '''
    f = _Cfunctions.get('libvlc_media_player_watch_time', None) or \
        _Cfunction('libvlc_media_player_watch_time', ((1,), (1,), (1,), (1,), (1,),), None,
                    ctypes.c_int, MediaPlayer, ctypes.c_int64, MediaPlayerWatchTimeOnUpdate, MediaPlayerWatchTimeOnDiscontinuity, ctypes.c_void_p)
    return f(p_mi, min_period_us, on_update, on_discontinuity, cbs_data)

def libvlc_media_player_unwatch_time(p_mi):
    '''Unwatch time updates.
    @param p_mi: the media player.
    @version: LibVLC 4.0.0 or later.
    '''
    f = _Cfunctions.get('libvlc_media_player_unwatch_time', None) or \
        _Cfunction('libvlc_media_player_unwatch_time', ((1,),), None,
                    None, MediaPlayer)
    return f(p_mi)

def libvlc_media_player_time_point_interpolate(point, system_now_us, out_ts_us, out_pos):
    '''Interpolate a timer value to now.
    @param point: time update obtained via the L{MediaPlayerWatchTimeOnUpdate}() callback.
    @param system_now_us: current system date, in us, returned by L{libvlc_clock}().
    @param out_ts_us: pointer where to set the interpolated ts, in us.
    @param out_pos: pointer where to set the interpolated position.
    @return: 0 in case of success, -1 if the interpolated ts is negative (could happen during the buffering step).
    @version: LibVLC 4.0.0 or later.
    '''
    f = _Cfunctions.get('libvlc_media_player_time_point_interpolate', None) or \
        _Cfunction('libvlc_media_player_time_point_interpolate', ((1,), (1,), (1,), (1,),), None,
                    ctypes.c_int, ctypes.POINTER(MediaPlayerTimePoint), ctypes.c_int64, ctypes.POINTER(ctypes.c_int64), ctypes.POINTER(ctypes.c_double))
    return f(point, system_now_us, out_ts_us, out_pos)

def libvlc_media_player_time_point_get_next_date(point, system_now_us, interpolated_ts_us, next_interval_us):
    '''Get the date of the next interval
    Can be used to setup an UI timer in order to update some widgets at specific
    interval. A next_interval of VLC_TICK_FROM_SEC(1) can be used to update a
    time widget when the media reaches a new second.
    @note: The media time doesn't necessarily correspond to the system time, that
    is why this function is needed and uses the rate of the current point.
    @param point: time update obtained via the L{MediaPlayerWatchTimeOnUpdate}().
    @param system_now_us: same system date used by L{libvlc_media_player_time_point_interpolate}().
    @param interpolated_ts_us: ts returned by L{libvlc_media_player_time_point_interpolate}().
    @param next_interval_us: next interval, in us.
    @return: the absolute system date, in us,  of the next interval, use libvlc_delay() to get a relative delay.
    @version: LibVLC 4.0.0 or later.
    '''
    f = _Cfunctions.get('libvlc_media_player_time_point_get_next_date', None) or \
        _Cfunction('libvlc_media_player_time_point_get_next_date', ((1,), (1,), (1,), (1,),), None,
                    ctypes.c_int64, ctypes.POINTER(MediaPlayerTimePoint), ctypes.c_int64, ctypes.c_int64, ctypes.c_int64)
    return f(point, system_now_us, interpolated_ts_us, next_interval_us)

def libvlc_media_tracklist_count(list):
    '''Get the number of tracks in a tracklist.
    @param list: valid tracklist.
    @return: number of tracks, or 0 if the list is empty.
    @version: LibVLC 4.0.0 and later.
    '''
    f = _Cfunctions.get('libvlc_media_tracklist_count', None) or \
        _Cfunction('libvlc_media_tracklist_count', ((1,),), None,
                    ctypes.c_size_t, ctypes.c_void_p)
    return f(list)

def libvlc_media_tracklist_at(list, index):
    '''Get a track at a specific index
    @warning: The behaviour is undefined if the index is not valid.
    @param list: valid tracklist.
    @param index: valid index in the range [0; count[.
    @return: a valid track (can't be None if L{libvlc_media_tracklist_count}() returned a valid count).
    @version: LibVLC 4.0.0 and later.
    '''
    f = _Cfunctions.get('libvlc_media_tracklist_at', None) or \
        _Cfunction('libvlc_media_tracklist_at', ((1,), (1,),), None,
                    ctypes.POINTER(MediaTrack), ctypes.c_void_p, ctypes.c_size_t)
    return f(list, index)

def libvlc_media_tracklist_delete(list):
    '''Release a tracklist.
    @param list: valid tracklist.
    @version: LibVLC 4.0.0 and later. See L{libvlc_media_get_tracklist} See L{libvlc_media_player_get_tracklist}.
    '''
    f = _Cfunctions.get('libvlc_media_tracklist_delete', None) or \
        _Cfunction('libvlc_media_tracklist_delete', ((1,),), None,
                    None, ctypes.c_void_p)
    return f(list)

def libvlc_media_track_hold(track):
    '''Hold a single track reference.
    @param track: valid track.
    @return: the same track, need to be released with L{libvlc_media_track_release}().
    @version: LibVLC 4.0.0 and later. This function can be used to hold a track from a tracklist. In that case, the track can outlive its tracklist.
    '''
    f = _Cfunctions.get('libvlc_media_track_hold', None) or \
        _Cfunction('libvlc_media_track_hold', ((1,),), None,
                    ctypes.POINTER(MediaTrack), ctypes.POINTER(MediaTrack))
    return f(track)

def libvlc_media_track_release(track):
    '''Release a single track.
    @param track: valid track.
    @version: LibVLC 4.0.0 and later. @warning Tracks from a tracklist are released alongside the list with L{libvlc_media_tracklist_delete}(). @note You only need to release tracks previously held with L{libvlc_media_track_hold}() or returned by L{libvlc_media_player_get_selected_track}() and L{libvlc_media_player_get_track_from_id}().
    '''
    f = _Cfunctions.get('libvlc_media_track_release', None) or \
        _Cfunction('libvlc_media_track_release', ((1,),), None,
                    None, ctypes.POINTER(MediaTrack))
    return f(track)

def libvlc_picture_retain(pic):
    '''Increment the reference count of this picture.
    See L{libvlc_picture_release}().
    @param pic: A picture object.
    '''
    f = _Cfunctions.get('libvlc_picture_retain', None) or \
        _Cfunction('libvlc_picture_retain', ((1,),), None,
                    None, Picture)
    return f(pic)

def libvlc_picture_release(pic):
    '''Decrement the reference count of this picture.
    When the reference count reaches 0, the picture will be released.
    The picture must not be accessed after calling this function.
    See L{libvlc_picture_retain}.
    @param pic: A picture object.
    '''
    f = _Cfunctions.get('libvlc_picture_release', None) or \
        _Cfunction('libvlc_picture_release', ((1,),), None,
                    None, Picture)
    return f(pic)

def libvlc_picture_save(pic, path):
    '''Saves this picture to a file. The image format is the same as the one
    returned by \link L{libvlc_picture_type} \endlink.
    @param pic: A picture object.
    @param path: The path to the generated file.
    @return: 0 in case of success, -1 otherwise.
    '''
    f = _Cfunctions.get('libvlc_picture_save', None) or \
        _Cfunction('libvlc_picture_save', ((1,), (1,),), None,
                    ctypes.c_int, Picture, ctypes.c_char_p)
    return f(pic, path)

def libvlc_picture_get_buffer(pic, size):
    '''Returns the image internal buffer, including potential padding.
    The L{Picture} owns the returned buffer, which must not be modified nor
    freed.
    @param pic: A picture object.
    @param size: A pointer to a size_t that will hold the size of the buffer [required].
    @return: A pointer to the internal buffer.
    '''
    f = _Cfunctions.get('libvlc_picture_get_buffer', None) or \
        _Cfunction('libvlc_picture_get_buffer', ((1,), (1,),), None,
                    ctypes.c_char_p, Picture, ctypes.POINTER(ctypes.c_size_t))
    return f(pic, size)

def libvlc_picture_type(pic):
    '''Returns the picture type.
    @param pic: A picture object See L{PictureType}.
    '''
    f = _Cfunctions.get('libvlc_picture_type', None) or \
        _Cfunction('libvlc_picture_type', ((1,),), None,
                    PictureType, Picture)
    return f(pic)

def libvlc_picture_get_stride(pic):
    '''Returns the image stride, ie. the number of bytes per line.
    This can only be called on images of type libvlc_picture_Argb.
    @param pic: A picture object.
    '''
    f = _Cfunctions.get('libvlc_picture_get_stride', None) or \
        _Cfunction('libvlc_picture_get_stride', ((1,),), None,
                    ctypes.c_uint, Picture)
    return f(pic)

def libvlc_picture_get_width(pic):
    '''Returns the width of the image in pixels.
    @param pic: A picture object.
    '''
    f = _Cfunctions.get('libvlc_picture_get_width', None) or \
        _Cfunction('libvlc_picture_get_width', ((1,),), None,
                    ctypes.c_uint, Picture)
    return f(pic)

def libvlc_picture_get_height(pic):
    '''Returns the height of the image in pixels.
    @param pic: A picture object.
    '''
    f = _Cfunctions.get('libvlc_picture_get_height', None) or \
        _Cfunction('libvlc_picture_get_height', ((1,),), None,
                    ctypes.c_uint, Picture)
    return f(pic)

def libvlc_picture_get_time(pic):
    '''Returns the time at which this picture was generated, in milliseconds.
    @param pic: A picture object.
    '''
    f = _Cfunctions.get('libvlc_picture_get_time', None) or \
        _Cfunction('libvlc_picture_get_time', ((1,),), None,
                    ctypes.c_longlong, Picture)
    return f(pic)

def libvlc_picture_list_count(list):
    '''Returns the number of pictures in the list.
    '''
    f = _Cfunctions.get('libvlc_picture_list_count', None) or \
        _Cfunction('libvlc_picture_list_count', ((1,),), None,
                    ctypes.c_size_t, ctypes.c_void_p)
    return f(list)

def libvlc_picture_list_at(list, index):
    '''Returns the picture at the provided index.
    If the index is out of bound, the result is undefined.
    '''
    f = _Cfunctions.get('libvlc_picture_list_at', None) or \
        _Cfunction('libvlc_picture_list_at', ((1,), (1,),), class_result(Picture),
                    ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t)
    return f(list, index)

def libvlc_picture_list_destroy(list):
    '''Destroys a picture list and releases the pictures it contains.
    @param list: The list to destroy Calling this function with a None list is safe and will return immediately.
    '''
    f = _Cfunctions.get('libvlc_picture_list_destroy', None) or \
        _Cfunction('libvlc_picture_list_destroy', ((1,),), None,
                    None, ctypes.c_void_p)
    return f(list)

def libvlc_renderer_item_hold(p_item):
    '''Hold a renderer item, i.e. creates a new reference
    This functions need to called from the libvlc_RendererDiscovererItemAdded
    callback if the libvlc user wants to use this item after. (for display or
    for passing it to the mediaplayer for example).
    @return: the current item.
    @version: LibVLC 3.0.0 or later.
    '''
    f = _Cfunctions.get('libvlc_renderer_item_hold', None) or \
        _Cfunction('libvlc_renderer_item_hold', ((1,),), class_result(Renderer),
                    ctypes.c_void_p, Renderer)
    return f(p_item)

def libvlc_renderer_item_release(p_item):
    '''Releases a renderer item, i.e. decrements its reference counter.
    @version: LibVLC 3.0.0 or later.
    '''
    f = _Cfunctions.get('libvlc_renderer_item_release', None) or \
        _Cfunction('libvlc_renderer_item_release', ((1,),), None,
                    None, Renderer)
    return f(p_item)

def libvlc_renderer_item_name(p_item):
    '''Get the human readable name of a renderer item.
    @return: the name of the item (can't be None, must *not* be freed).
    @version: LibVLC 3.0.0 or later.
    '''
    f = _Cfunctions.get('libvlc_renderer_item_name', None) or \
        _Cfunction('libvlc_renderer_item_name', ((1,),), None,
                    ctypes.c_char_p, Renderer)
    return f(p_item)

def libvlc_renderer_item_type(p_item):
    '''Get the type (not translated) of a renderer item. For now, the type can only
    be "chromecast" ("upnp", "airplay" may come later).
    @return: the type of the item (can't be None, must *not* be freed).
    @version: LibVLC 3.0.0 or later.
    '''
    f = _Cfunctions.get('libvlc_renderer_item_type', None) or \
        _Cfunction('libvlc_renderer_item_type', ((1,),), None,
                    ctypes.c_char_p, Renderer)
    return f(p_item)

def libvlc_renderer_item_icon_uri(p_item):
    '''Get the icon uri of a renderer item.
    @return: the uri of the item's icon (can be None, must *not* be freed).
    @version: LibVLC 3.0.0 or later.
    '''
    f = _Cfunctions.get('libvlc_renderer_item_icon_uri', None) or \
        _Cfunction('libvlc_renderer_item_icon_uri', ((1,),), None,
                    ctypes.c_char_p, Renderer)
    return f(p_item)

def libvlc_renderer_item_flags(p_item):
    '''Get the flags of a renderer item
    See LIBVLC_RENDERER_CAN_AUDIO
    See LIBVLC_RENDERER_CAN_VIDEO.
    @return: bitwise flag: capabilities of the renderer, see.
    @version: LibVLC 3.0.0 or later.
    '''
    f = _Cfunctions.get('libvlc_renderer_item_flags', None) or \
        _Cfunction('libvlc_renderer_item_flags', ((1,),), None,
                    ctypes.c_int, Renderer)
    return f(p_item)

def libvlc_renderer_discoverer_new(p_inst, psz_name):
    '''Create a renderer discoverer object by name
    After this object is created, you should attach to events in order to be
    notified of the discoverer events.
    You need to call L{libvlc_renderer_discoverer_start}() in order to start the
    discovery.
    See L{libvlc_renderer_discoverer_event_manager}()
    See L{libvlc_renderer_discoverer_start}().
    @param p_inst: libvlc instance.
    @param psz_name: service name; use L{libvlc_renderer_discoverer_list_get}() to get a list of the discoverer names available in this libVLC instance.
    @return: media discover object or None in case of error.
    @version: LibVLC 3.0.0 or later.
    '''
    f = _Cfunctions.get('libvlc_renderer_discoverer_new', None) or \
        _Cfunction('libvlc_renderer_discoverer_new', ((1,), (1,),), class_result(RendererDiscoverer),
                    ctypes.c_void_p, Instance, ctypes.c_char_p)
    return f(p_inst, psz_name)

def libvlc_renderer_discoverer_release(p_rd):
    '''Release a renderer discoverer object.
    @param p_rd: renderer discoverer object.
    @version: LibVLC 3.0.0 or later.
    '''
    f = _Cfunctions.get('libvlc_renderer_discoverer_release', None) or \
        _Cfunction('libvlc_renderer_discoverer_release', ((1,),), None,
                    None, RendererDiscoverer)
    return f(p_rd)

def libvlc_renderer_discoverer_start(p_rd):
    '''Start renderer discovery
    To stop it, call L{libvlc_renderer_discoverer_stop}() or
    L{libvlc_renderer_discoverer_release}() directly.
    See L{libvlc_renderer_discoverer_stop}().
    @param p_rd: renderer discoverer object.
    @return: -1 in case of error, 0 otherwise.
    @version: LibVLC 3.0.0 or later.
    '''
    f = _Cfunctions.get('libvlc_renderer_discoverer_start', None) or \
        _Cfunction('libvlc_renderer_discoverer_start', ((1,),), None,
                    ctypes.c_int, RendererDiscoverer)
    return f(p_rd)

def libvlc_renderer_discoverer_stop(p_rd):
    '''Stop renderer discovery.
    See L{libvlc_renderer_discoverer_start}().
    @param p_rd: renderer discoverer object.
    @version: LibVLC 3.0.0 or later.
    '''
    f = _Cfunctions.get('libvlc_renderer_discoverer_stop', None) or \
        _Cfunction('libvlc_renderer_discoverer_stop', ((1,),), None,
                    None, RendererDiscoverer)
    return f(p_rd)

def libvlc_renderer_discoverer_event_manager(p_rd):
    '''Get the event manager of the renderer discoverer
    The possible events to attach are @ref libvlc_RendererDiscovererItemAdded
    and @ref libvlc_RendererDiscovererItemDeleted.
    The @ref L{Renderer} struct passed to event callbacks is owned by
    VLC, users should take care of holding/releasing this struct for their
    internal usage.
    See L{Event}.u.renderer_discoverer_item_added.item
    See L{Event}.u.renderer_discoverer_item_removed.item.
    @return: a valid event manager (can't fail).
    @version: LibVLC 3.0.0 or later.
    '''
    f = _Cfunctions.get('libvlc_renderer_discoverer_event_manager', None) or \
        _Cfunction('libvlc_renderer_discoverer_event_manager', ((1,),), class_result(EventManager),
                    ctypes.c_void_p, RendererDiscoverer)
    return f(p_rd)

def libvlc_renderer_discoverer_list_get(p_inst, ppp_services):
    '''Get media discoverer services
    See libvlc_renderer_list_release().
    @param p_inst: libvlc instance.
    @param ppp_services: address to store an allocated array of renderer discoverer services (must be freed with libvlc_renderer_list_release() by the caller) [OUT].
    @return: the number of media discoverer services (0 on error).
    @version: LibVLC 3.0.0 and later.
    '''
    f = _Cfunctions.get('libvlc_renderer_discoverer_list_get', None) or \
        _Cfunction('libvlc_renderer_discoverer_list_get', ((1,), (1,),), None,
                    ctypes.c_size_t, Instance, ctypes.POINTER(ctypes.POINTER(ctypes.POINTER(RdDescription))))
    return f(p_inst, ppp_services)

def libvlc_renderer_discoverer_list_release(pp_services, i_count):
    '''Release an array of media discoverer services
    See L{libvlc_renderer_discoverer_list_get}().
    @param pp_services: array to release.
    @param i_count: number of elements in the array.
    @version: LibVLC 3.0.0 and later.
    '''
    f = _Cfunctions.get('libvlc_renderer_discoverer_list_release', None) or \
        _Cfunction('libvlc_renderer_discoverer_list_release', ((1,), (1,),), None,
                    None, ctypes.POINTER(ctypes.POINTER(RdDescription)), ctypes.c_size_t)
    return f(pp_services, i_count)


# 4 function(s) blacklisted:
#  libvlc_dialog_set_callbacks
#  libvlc_set_exit_handler
#  libvlc_video_output_set_resize_cb
#  libvlc_video_set_output_callbacks

# 55 function(s) not wrapped as methods:
#  libvlc_abi_version
#  libvlc_audio_equalizer_get_band_count
#  libvlc_audio_equalizer_get_band_frequency
#  libvlc_audio_equalizer_get_preset_count
#  libvlc_audio_equalizer_get_preset_name
#  libvlc_audio_equalizer_new
#  libvlc_audio_equalizer_new_from_preset
#  libvlc_audio_output_device_list_release
#  libvlc_audio_output_list_release
#  libvlc_chapter_descriptions_release
#  libvlc_clearerr
#  libvlc_clock
#  libvlc_dialog_dismiss
#  libvlc_dialog_get_context
#  libvlc_dialog_post_action
#  libvlc_dialog_post_login
#  libvlc_dialog_set_context
#  libvlc_errmsg
#  libvlc_free
#  libvlc_get_changeset
#  libvlc_get_compiler
#  libvlc_get_version
#  libvlc_log_get_context
#  libvlc_log_get_object
#  libvlc_media_discoverer_list_release
#  libvlc_media_get_codec_description
#  libvlc_media_list_new
#  libvlc_media_new_as_node
#  libvlc_media_new_callbacks
#  libvlc_media_new_fd
#  libvlc_media_new_location
#  libvlc_media_new_path
#  libvlc_media_player_time_point_get_next_date
#  libvlc_media_player_time_point_interpolate
#  libvlc_media_slaves_release
#  libvlc_media_thumbnail_request_cancel
#  libvlc_media_thumbnail_request_destroy
#  libvlc_media_track_hold
#  libvlc_media_track_release
#  libvlc_media_tracklist_at
#  libvlc_media_tracklist_count
#  libvlc_media_tracklist_delete
#  libvlc_module_description_list_release
#  libvlc_new
#  libvlc_picture_list_at
#  libvlc_picture_list_count
#  libvlc_picture_list_destroy
#  libvlc_player_program_delete
#  libvlc_player_programlist_at
#  libvlc_player_programlist_count
#  libvlc_player_programlist_delete
#  libvlc_renderer_discoverer_list_release
#  libvlc_title_descriptions_release
#  libvlc_track_description_list_release
#  libvlc_video_new_viewpoint

# Start of footer.py #

# Backward compatibility
def callbackmethod(callback):
    """Now obsolete @callbackmethod decorator."""
    return callback

# libvlc_free is not present in some versions of libvlc. If it is not
# in the library, then emulate it by calling libc.free
if not hasattr(dll, 'libvlc_free'):
    # need to find the free function in the C runtime. This is
    # platform specific.
    # For Linux and MacOSX
    libc_path = find_library('c')
    if libc_path:
        libc = ctypes.CDLL(libc_path)
        libvlc_free = libc.free
    else:
        # On win32, it is impossible to guess the proper lib to call
        # (msvcrt, mingw...). Just ignore the call: it will memleak,
        # but not prevent to run the application.
        def libvlc_free(p):
            pass

    # ensure argtypes is right, because default type of int won't
    # work on 64-bit systems
    libvlc_free.argtypes = [ ctypes.c_void_p ]

# Version functions
def _dot2int(v):
    '''(INTERNAL) Convert 'i.i.i[.i]' str to int.
    '''
    t = [int(i) for i in v.split('.')]
    if len(t) == 3:
        if t[2] < 100:
            t.append(0)
        else:  # 100 is arbitrary
            t[2:4] = divmod(t[2], 100)
    elif len(t) != 4:
        raise ValueError('"i.i.i[.i]": %r' % (v,))
    if min(t) < 0 or max(t) > 255:
        raise ValueError('[0..255]: %r' % (v,))
    i = t.pop(0)
    while t:
        i = (i << 8) + t.pop(0)
    return i

def hex_version():
    """Return the version of these bindings in hex or 0 if unavailable.
    """
    try:
        return _dot2int(__version__)
    except (NameError, ValueError):
        return 0

def libvlc_hex_version():
    """Return the libvlc version in hex or 0 if unavailable.
    """
    try:
        return _dot2int(bytes_to_str(libvlc_get_version()).split()[0])
    except ValueError:
        return 0

def debug_callback(event, *args, **kwds):
    '''Example callback, useful for debugging.
    '''
    l = ['event %s' % (event.type,)]
    if args:
        l.extend(map(str, args))
    if kwds:
        l.extend(sorted('%s=%s' % t for t in kwds.items()))
    print('Debug callback (%s)' % ', '.join(l))

def print_python():
    from platform import architecture, machine, mac_ver, uname, win32_ver
    if 'intelpython' in sys.executable:
        t = 'Intel-'
    # elif 'PyPy ' in sys.version:
    #     t = 'PyPy-'
    else:
        t = ''
    t = '%sPython: %s (%s)' % (t, sys.version.split()[0], architecture()[0])
    if win32_ver()[0]:
        t = t, 'Windows', win32_ver()[0]
    elif mac_ver()[0]:
        t = t, ('iOS' if sys.platform == 'ios' else 'macOS'), mac_ver()[0], machine()
    else:
        try:
            import distro  # <http://GitHub.com/nir0s/distro>
            t = t, bytes_to_str(distro.name()), bytes_to_str(distro.version())
        except ImportError:
            t = (t,) + uname()[0:3:2]
    print(' '.join(t))

def print_version():
    """Print version of this vlc.py and of the libvlc"""
    try:
        print('%s: %s (%s)' % (os.path.basename(__file__), __version__, build_date))
        print('libVLC: %s (%#x)' % (bytes_to_str(libvlc_get_version()), libvlc_hex_version()))
        # print('libVLC %s' % bytes_to_str(libvlc_get_compiler()))
        if plugin_path:
            print('plugins: %s' % plugin_path)
    except Exception:
        print('Error: %s' % sys.exc_info()[1])


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    try:
        from msvcrt import getch
    except ImportError:
        import termios
        import tty

        def getch():  # getchar(), getc(stdin)  #PYCHOK flake
            fd = sys.stdin.fileno()
            old = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                ch = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old)
            return ch

    def end_callback(event):
        print('End of media stream (event %s)' % event.type)
        sys.exit(0)

    echo_position = False
    def pos_callback(event, player):
        if echo_position:
            sys.stdout.write('\r%s to %.2f%% (%.2f%%)' % (event.type,
                                                          event.u.new_position * 100,
                                                          player.get_position() * 100))
            sys.stdout.flush()

    if '-h' in sys.argv[:2] or '--help' in sys.argv[:2]:
        print('Usage: %s [options] <movie_filename>' % sys.argv[0])
        print('Once launched, type ? for help.')
        print('')

    elif '-v' in sys.argv[:2] or '--version' in sys.argv[:2]:
        print_version()
        print_python()
        print('')

    else:
        movie = os.path.expanduser(sys.argv.pop())
        if not os.access(movie, os.R_OK):
            print('Error: %s file not readable' % movie)
            sys.exit(1)

        # Need --sub-source=marq in order to use marquee below
        instance = Instance(["--sub-source=marq"] + sys.argv[1:])
        try:
            media = instance.media_new(movie)
        except (AttributeError, NameError) as e:
            print('%s: %s (%s %s vs LibVLC %s)' % (e.__class__.__name__, e,
                                                   sys.argv[0], __version__,
                                                   libvlc_get_version()))
            sys.exit(1)
        player = instance.media_player_new()
        player.set_media(media)
        player.play()

        # Some marquee examples.  Marquee requires '--sub-source marq' in the
        # Instance() call above, see <http://www.videolan.org/doc/play-howto/en/ch04.html>
        player.video_set_marquee_int(VideoMarqueeOption.Enable, 1)
        player.video_set_marquee_int(VideoMarqueeOption.Size, 24)  # pixels
        # FIXME: This crashes the module - it should be investigated
        # player.video_set_marquee_int(VideoMarqueeOption.Position, Position.bottom)
        if False:  # only one marquee can be specified
            player.video_set_marquee_int(VideoMarqueeOption.Timeout, 5000)  # millisec, 0==forever
            t = media.get_mrl()  # movie
        else:  # update marquee text periodically
            player.video_set_marquee_int(VideoMarqueeOption.Timeout, 0)  # millisec, 0==forever
            player.video_set_marquee_int(VideoMarqueeOption.Refresh, 1000)  # millisec (or sec?)
            ##t = '$L / $D or $P at $T'
            t = '%Y-%m-%d  %H:%M:%S'
        player.video_set_marquee_string(VideoMarqueeOption.Text, str_to_bytes(t))

        # Some event manager examples.  Note, the callback can be any Python
        # callable and does not need to be decorated.  Optionally, specify
        # any number of positional and/or keyword arguments to be passed
        # to the callback (in addition to the first one, an Event instance).
        event_manager = player.event_manager()
        event_manager.event_attach(EventType.MediaPlayerEndReached,      end_callback)
        event_manager.event_attach(EventType.MediaPlayerPositionChanged, pos_callback, player)

        def mspf():
            """Milliseconds per frame"""
            return int(1000 // (player.get_fps() or 25))

        def print_info():
            """Print information about the media"""
            try:
                print_version()
                media = player.get_media()
                print('State: %s' % player.get_state())
                print('Media: %s' % bytes_to_str(media.get_mrl()))
                print('Track: %s/%s' % (player.video_get_track(), player.video_get_track_count()))
                print('Current time: %s/%s' % (player.get_time(), media.get_duration()))
                print('Position: %s' % player.get_position())
                print('FPS: %s (%d ms)' % (player.get_fps(), mspf()))
                print('Rate: %s' % player.get_rate())
                print('Video size: %s' % str(player.video_get_size(0)))  # num=0
                print('Scale: %s' % player.video_get_scale())
                print('Aspect ratio: %s' % player.video_get_aspect_ratio())
               #print('Window:' % player.get_hwnd()
            except Exception:
                print('Error: %s' % sys.exc_info()[1])

        def sec_forward():
            """Go forward one sec"""
            player.set_time(player.get_time() + 1000)

        def sec_backward():
            """Go backward one sec"""
            player.set_time(player.get_time() - 1000)

        def frame_forward():
            """Go forward one frame"""
            player.set_time(player.get_time() + mspf())

        def frame_backward():
            """Go backward one frame"""
            player.set_time(player.get_time() - mspf())

        def print_help():
            """Print help"""
            print('Single-character commands:')
            for k, m in sorted(keybindings.items()):
                m = (m.__doc__ or m.__name__).splitlines()[0]
                print('  %s: %s.' % (k, m.rstrip('.')))
            print('0-9: go to that fraction of the movie')

        def quit_app():
            """Stop and exit"""
            sys.exit(0)

        def toggle_echo_position():
            """Toggle echoing of media position"""
            global echo_position
            echo_position = not echo_position

        keybindings = {
            ' ': player.pause,
            '+': sec_forward,
            '-': sec_backward,
            '.': frame_forward,
            ',': frame_backward,
            'f': player.toggle_fullscreen,
            'i': print_info,
            'p': toggle_echo_position,
            'q': quit_app,
            '?': print_help,
            }

        print('Press q to quit, ? to get help.%s' % os.linesep)
        while True:
            k = getch()
            print('> %s' % k)
            if k in keybindings:
                keybindings[k]()
            elif k.isdigit():
                 # jump to fraction of the movie.
                player.set_position(float('0.'+k))
