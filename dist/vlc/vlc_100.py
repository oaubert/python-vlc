#! /usr/bin/python

#
# Python ctypes bindings for VLC
# Copyright (C) 2009 the VideoLAN team
# $Id: $
#
# Authors: Olivier Aubert <olivier.aubert at liris.cnrs.fr>
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
#

"""This module provides bindings for the
U{libvlc<http://wiki.videolan.org/ExternalAPI>} and
U{MediaControl<http://wiki.videolan.org/MediaControlAPI>} APIs.

You can find documentation at U{http://www.advene.org/download/python-ctypes/}.

Basically, the most important class is L{Instance}, which is used to
create a libvlc Instance. From this instance, you can then create
L{MediaPlayer} and L{MediaListPlayer} instances.
"""

import logging
import ctypes
import sys

build_date="Thu Jan 28 12:00:04 2010"

# Used for win32 and MacOS X
detected_plugin_path=None

if sys.platform == 'linux2':
    dll=ctypes.CDLL('libvlc.so')
elif sys.platform == 'win32':
    import ctypes.util
    import os
    detected_plugin_path=None
    path=ctypes.util.find_library('libvlc.dll')
    if path is None:
        # Try to use registry settings
        import _winreg
        detected_plugin_path_found = None
        subkey, name = 'Software\\VideoLAN\\VLC','InstallDir'
        for hkey in _winreg.HKEY_LOCAL_MACHINE, _winreg.HKEY_CURRENT_USER:
            try:
                reg = _winreg.OpenKey(hkey, subkey)
                detected_plugin_path_found, type_id = _winreg.QueryValueEx(reg, name)
                _winreg.CloseKey(reg)
                break
            except _winreg.error:
                pass
        if detected_plugin_path_found:
            detected_plugin_path = detected_plugin_path_found
        else:
            # Try a standard location.
            p='c:\\Program Files\\VideoLAN\\VLC\\libvlc.dll'
            if os.path.exists(p):
                detected_plugin_path=os.path.dirname(p)
        if detected_plugin_path is not None:
            os.chdir(detected_plugin_path)
        # If chdir failed, this will not work and raise an exception
        path='libvlc.dll'
    else:
        detected_plugin_path=os.path.dirname(path)
    dll=ctypes.CDLL(path)
elif sys.platform == 'darwin':
    # FIXME: should find a means to configure path
    d='/Applications/VLC.app'
    import os
    if os.path.exists(d):
        dll=ctypes.CDLL(d+'/Contents/MacOS/lib/libvlc.2.dylib')
        detected_plugin_path=d+'/Contents/MacOS/modules'
    else:
        # Hope some default path is set...
        dll=ctypes.CDLL('libvlc.2.dylib')

#
# Generated enum types.
#

class EventType(ctypes.c_ulong):
    """ libvlc_core
LibVLC Available Events


    """
    _names={
        1: 'MediaSubItemAdded',
        2: 'MediaDurationChanged',
        3: 'MediaPreparsedChanged',
        4: 'MediaFreed',
        5: 'MediaStateChanged',
        6: 'MediaPlayerNothingSpecial',
        7: 'MediaPlayerOpening',
        8: 'MediaPlayerBuffering',
        9: 'MediaPlayerPlaying',
        10: 'MediaPlayerPaused',
        11: 'MediaPlayerStopped',
        12: 'MediaPlayerForward',
        13: 'MediaPlayerBackward',
        14: 'MediaPlayerEndReached',
        15: 'MediaPlayerEncounteredError',
        16: 'MediaPlayerTimeChanged',
        17: 'MediaPlayerPositionChanged',
        18: 'MediaPlayerSeekableChanged',
        19: 'MediaPlayerPausableChanged',
        20: 'MediaListItemAdded',
        21: 'MediaListWillAddItem',
        22: 'MediaListItemDeleted',
        23: 'MediaListWillDeleteItem',
        24: 'MediaListViewItemAdded',
        25: 'MediaListViewWillAddItem',
        26: 'MediaListViewItemDeleted',
        27: 'MediaListViewWillDeleteItem',
        28: 'MediaListPlayerPlayed',
        29: 'MediaListPlayerNextItemSet',
        30: 'MediaListPlayerStopped',
        31: 'MediaDiscovererStarted',
        32: 'MediaDiscovererEnded',
        33: 'MediaPlayerTitleChanged',
        34: 'MediaPlayerSnapshotTaken',
    }

    def __repr__(self):
        return ".".join((self.__class__.__module__, self.__class__.__name__, self._names[self.value]))

    def __eq__(self, other):
        return ( (isinstance(other, ctypes.c_ulong) and self.value == other.value)
                 or (isinstance(other, (int, long)) and self.value == other ) )

    def __ne__(self, other):
        return not self.__eq__(other)
    
EventType.MediaSubItemAdded=EventType(1)
EventType.MediaDurationChanged=EventType(2)
EventType.MediaPreparsedChanged=EventType(3)
EventType.MediaFreed=EventType(4)
EventType.MediaStateChanged=EventType(5)
EventType.MediaPlayerNothingSpecial=EventType(6)
EventType.MediaPlayerOpening=EventType(7)
EventType.MediaPlayerBuffering=EventType(8)
EventType.MediaPlayerPlaying=EventType(9)
EventType.MediaPlayerPaused=EventType(10)
EventType.MediaPlayerStopped=EventType(11)
EventType.MediaPlayerForward=EventType(12)
EventType.MediaPlayerBackward=EventType(13)
EventType.MediaPlayerEndReached=EventType(14)
EventType.MediaPlayerEncounteredError=EventType(15)
EventType.MediaPlayerTimeChanged=EventType(16)
EventType.MediaPlayerPositionChanged=EventType(17)
EventType.MediaPlayerSeekableChanged=EventType(18)
EventType.MediaPlayerPausableChanged=EventType(19)
EventType.MediaListItemAdded=EventType(20)
EventType.MediaListWillAddItem=EventType(21)
EventType.MediaListItemDeleted=EventType(22)
EventType.MediaListWillDeleteItem=EventType(23)
EventType.MediaListViewItemAdded=EventType(24)
EventType.MediaListViewWillAddItem=EventType(25)
EventType.MediaListViewItemDeleted=EventType(26)
EventType.MediaListViewWillDeleteItem=EventType(27)
EventType.MediaListPlayerPlayed=EventType(28)
EventType.MediaListPlayerNextItemSet=EventType(29)
EventType.MediaListPlayerStopped=EventType(30)
EventType.MediaDiscovererStarted=EventType(31)
EventType.MediaDiscovererEnded=EventType(32)
EventType.MediaPlayerTitleChanged=EventType(33)
EventType.MediaPlayerSnapshotTaken=EventType(34)

class Meta(ctypes.c_ulong):
    """ libvlc_media
LibVLC Media Meta


    """
    _names={
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
    }

    def __repr__(self):
        return ".".join((self.__class__.__module__, self.__class__.__name__, self._names[self.value]))

    def __eq__(self, other):
        return ( (isinstance(other, ctypes.c_ulong) and self.value == other.value)
                 or (isinstance(other, (int, long)) and self.value == other ) )

    def __ne__(self, other):
        return not self.__eq__(other)
    
Meta.Title=Meta(0)
Meta.Artist=Meta(1)
Meta.Genre=Meta(2)
Meta.Copyright=Meta(3)
Meta.Album=Meta(4)
Meta.TrackNumber=Meta(5)
Meta.Description=Meta(6)
Meta.Rating=Meta(7)
Meta.Date=Meta(8)
Meta.Setting=Meta(9)
Meta.URL=Meta(10)
Meta.Language=Meta(11)
Meta.NowPlaying=Meta(12)
Meta.Publisher=Meta(13)
Meta.EncodedBy=Meta(14)
Meta.ArtworkURL=Meta(15)
Meta.TrackID=Meta(16)

class State(ctypes.c_ulong):
    """Note the order of libvlc_state_t enum must match exactly the order of
See mediacontrol_PlayerStatus, See input_state_e enums,
and VideoLAN.LibVLC.State (at bindings/cil/src/media.cs).
Expected states by web plugins are:
IDLE/CLOSE=0, OPENING=1, BUFFERING=2, PLAYING=3, PAUSED=4,
STOPPING=5, ENDED=6, ERROR=7

    """
    _names={
        0: 'NothingSpecial',
        1: 'Opening',
        2: 'Buffering',
        3: 'Playing',
        4: 'Paused',
        5: 'Stopped',
        6: 'Ended',
        7: 'Error',
    }

    def __repr__(self):
        return ".".join((self.__class__.__module__, self.__class__.__name__, self._names[self.value]))

    def __eq__(self, other):
        return ( (isinstance(other, ctypes.c_ulong) and self.value == other.value)
                 or (isinstance(other, (int, long)) and self.value == other ) )

    def __ne__(self, other):
        return not self.__eq__(other)
    
State.NothingSpecial=State(0)
State.Opening=State(1)
State.Buffering=State(2)
State.Playing=State(3)
State.Paused=State(4)
State.Stopped=State(5)
State.Ended=State(6)
State.Error=State(7)

class AudioOutputDeviceTypes(ctypes.c_ulong):
    """Audio device types

    """
    _names={
        -1: 'Error',
        1: 'Mono',
        2: 'Stereo',
        4: '_2F2R',
        5: '_3F2R',
        6: '_5_1',
        7: '_6_1',
        8: '_7_1',
        10: 'SPDIF',
    }

    def __repr__(self):
        return ".".join((self.__class__.__module__, self.__class__.__name__, self._names[self.value]))

    def __eq__(self, other):
        return ( (isinstance(other, ctypes.c_ulong) and self.value == other.value)
                 or (isinstance(other, (int, long)) and self.value == other ) )

    def __ne__(self, other):
        return not self.__eq__(other)
    
AudioOutputDeviceTypes.Error=AudioOutputDeviceTypes(-1)
AudioOutputDeviceTypes.Mono=AudioOutputDeviceTypes(1)
AudioOutputDeviceTypes.Stereo=AudioOutputDeviceTypes(2)
AudioOutputDeviceTypes._2F2R=AudioOutputDeviceTypes(4)
AudioOutputDeviceTypes._3F2R=AudioOutputDeviceTypes(5)
AudioOutputDeviceTypes._5_1=AudioOutputDeviceTypes(6)
AudioOutputDeviceTypes._6_1=AudioOutputDeviceTypes(7)
AudioOutputDeviceTypes._7_1=AudioOutputDeviceTypes(8)
AudioOutputDeviceTypes.SPDIF=AudioOutputDeviceTypes(10)

class AudioOutputChannel(ctypes.c_ulong):
    """Audio channels

    """
    _names={
        -1: 'Error',
        1: 'Stereo',
        2: 'RStereo',
        3: 'Left',
        4: 'Right',
        5: 'Dolbys',
    }

    def __repr__(self):
        return ".".join((self.__class__.__module__, self.__class__.__name__, self._names[self.value]))

    def __eq__(self, other):
        return ( (isinstance(other, ctypes.c_ulong) and self.value == other.value)
                 or (isinstance(other, (int, long)) and self.value == other ) )

    def __ne__(self, other):
        return not self.__eq__(other)
    
AudioOutputChannel.Error=AudioOutputChannel(-1)
AudioOutputChannel.Stereo=AudioOutputChannel(1)
AudioOutputChannel.RStereo=AudioOutputChannel(2)
AudioOutputChannel.Left=AudioOutputChannel(3)
AudioOutputChannel.Right=AudioOutputChannel(4)
AudioOutputChannel.Dolbys=AudioOutputChannel(5)

class PositionOrigin(ctypes.c_ulong):
    """A position may have different origins:
 - absolute counts from the movie start
 - relative counts from the current position
 - modulo counts from the current position and wraps at the end of the movie

    """
    _names={
        0: 'AbsolutePosition',
        1: 'RelativePosition',
        2: 'ModuloPosition',
    }

    def __repr__(self):
        return ".".join((self.__class__.__module__, self.__class__.__name__, self._names[self.value]))

    def __eq__(self, other):
        return ( (isinstance(other, ctypes.c_ulong) and self.value == other.value)
                 or (isinstance(other, (int, long)) and self.value == other ) )

    def __ne__(self, other):
        return not self.__eq__(other)
    
PositionOrigin.AbsolutePosition=PositionOrigin(0)
PositionOrigin.RelativePosition=PositionOrigin(1)
PositionOrigin.ModuloPosition=PositionOrigin(2)

class PositionKey(ctypes.c_ulong):
    """Units available in mediacontrol Positions
 - ByteCount number of bytes
 - SampleCount number of frames
 - MediaTime time in milliseconds

    """
    _names={
        0: 'ByteCount',
        1: 'SampleCount',
        2: 'MediaTime',
    }

    def __repr__(self):
        return ".".join((self.__class__.__module__, self.__class__.__name__, self._names[self.value]))

    def __eq__(self, other):
        return ( (isinstance(other, ctypes.c_ulong) and self.value == other.value)
                 or (isinstance(other, (int, long)) and self.value == other ) )

    def __ne__(self, other):
        return not self.__eq__(other)
    
PositionKey.ByteCount=PositionKey(0)
PositionKey.SampleCount=PositionKey(1)
PositionKey.MediaTime=PositionKey(2)

class PlayerStatus(ctypes.c_ulong):
    """Possible player status
Note the order of these enums must match exactly the order of
libvlc_state_t and input_state_e enums.

    """
    _names={
        0: 'UndefinedStatus',
        1: 'InitStatus',
        2: 'BufferingStatus',
        3: 'PlayingStatus',
        4: 'PauseStatus',
        5: 'StopStatus',
        6: 'EndStatus',
        7: 'ErrorStatus',
    }

    def __repr__(self):
        return ".".join((self.__class__.__module__, self.__class__.__name__, self._names[self.value]))

    def __eq__(self, other):
        return ( (isinstance(other, ctypes.c_ulong) and self.value == other.value)
                 or (isinstance(other, (int, long)) and self.value == other ) )

    def __ne__(self, other):
        return not self.__eq__(other)
    
PlayerStatus.UndefinedStatus=PlayerStatus(0)
PlayerStatus.InitStatus=PlayerStatus(1)
PlayerStatus.BufferingStatus=PlayerStatus(2)
PlayerStatus.PlayingStatus=PlayerStatus(3)
PlayerStatus.PauseStatus=PlayerStatus(4)
PlayerStatus.StopStatus=PlayerStatus(5)
PlayerStatus.EndStatus=PlayerStatus(6)
PlayerStatus.ErrorStatus=PlayerStatus(7)


#
# End of generated enum types.
#

class ListPOINTER(object):
    '''Just like a POINTER but accept a list of ctype as an argument.
    '''
    def __init__(self, etype):
        self.etype = etype

    def from_param(self, param):
        if isinstance(param, (list, tuple)):
            return (self.etype * len(param))(*param)

class LibVLCException(Exception):
    """Python exception raised by libvlc methods.
    """
    pass

# From libvlc_structures.h

# This is version-dependent, depending on the presence of libvlc_errmsg

if hasattr(dll, 'libvlc_errmsg'):
    # New-style message passing
    class VLCException(ctypes.Structure):
        """libvlc exception.
        """
        _fields_= [
                    ('raised', ctypes.c_int),
                    ]

        @property
        def message(self):
            return dll.libvlc_errmsg()

        def init(self):
            libvlc_exception_init(self)

        def clear(self):
            libvlc_exception_clear(self)
else:
    # Old-style exceptions
    class VLCException(ctypes.Structure):
        """libvlc exception.
        """
        _fields_= [
                    ('raised', ctypes.c_int),
                    ('code', ctypes.c_int),
                    ('message', ctypes.c_char_p),
                    ]
        def init(self):
            libvlc_exception_init(self)

        def clear(self):
            libvlc_exception_clear(self)

class MediaStats(ctypes.Structure):
    _fields_= [
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

    def __str__(self):
        return "MediaStats\n%s" % "\n".join( "%s:\t%s" % (n, getattr(self, n)) for n in self._fields_ )

if 'EsType' in dir():
    class MediaES(ctypes.Structure):
        _fields_= [
            ('codec'   , ctypes.c_uint32),
            ('id'      , ctypes.c_int),
            ('type'    , EsType),
            ('profile' , ctypes.c_int),
            ('level'   , ctypes.c_int),
            ('channels',  ctypes.c_uint),
            ('rate'    , ctypes.c_uint),
            ('height'  , ctypes.c_uint),
            ('width'   , ctypes.c_uint),
            ]

        def __str__(self):
            return "MediaES \n%s" % "\n".join( "%s:\t%s" % (n, getattr(self, n)) for n in self._fields_ )

class PlaylistItem(ctypes.Structure):
    _fields_= [
                ('id', ctypes.c_int),
                ('uri', ctypes.c_char_p),
                ('name', ctypes.c_char_p),
                ]

    def __str__(self):
        return "PlaylistItem #%d %s (%uri)" % (self.id, self.name, self.uri)

class LogMessage(ctypes.Structure):
    _fields_= [
                ('size', ctypes.c_uint),
                ('severity', ctypes.c_int),
                ('type', ctypes.c_char_p),
                ('name', ctypes.c_char_p),
                ('header', ctypes.c_char_p),
                ('message', ctypes.c_char_p),
                ]

    def __init__(self):
        super(LogMessage, self).__init__()
        self.size=ctypes.sizeof(self)

    def __str__(self):
        return "vlc.LogMessage(%d:%s): %s" % (self.severity, self.type, self.message)

class MediaControlPosition(ctypes.Structure):
    _fields_= [
                ('origin', PositionOrigin),
                ('key', PositionKey),
                ('value', ctypes.c_longlong),
                ]

    def __init__(self, value=0, origin=None, key=None):
        # We override the __init__ method so that instanciating the
        # class with an int as parameter will create the appropriate
        # default position (absolute position, media time, with the
        # int as value).
        super(MediaControlPosition, self).__init__()
        self.value=value
        if origin is None:
            origin=PositionOrigin.AbsolutePosition
        if key is None:
            key=PositionKey.MediaTime
        self.origin=origin
        self.key=key

    def __str__(self):
        return "MediaControlPosition %ld (%s, %s)" % (
            self.value,
            str(self.origin),
            str(self.key)
            )

    @staticmethod
    def from_param(arg):
        if isinstance(arg, (int, long)):
            return MediaControlPosition(arg)
        else:
            return arg

class MediaControlException(ctypes.Structure):
    _fields_= [
                ('code', ctypes.c_int),
                ('message', ctypes.c_char_p),
                ]
    def init(self):
        mediacontrol_exception_init(self)

    def clear(self):
        mediacontrol_exception_free(self)

class MediaControlStreamInformation(ctypes.Structure):
    _fields_= [
                ('status', PlayerStatus),
                ('url', ctypes.c_char_p),
                ('position', ctypes.c_longlong),
                ('length', ctypes.c_longlong),
                ]

    def __str__(self):
        return "%s (%s) : %ld / %ld" % (self.url or "<No defined URL>",
                                        str(self.status),
                                        self.position,
                                        self.length)

class RGBPicture(ctypes.Structure):
    _fields_= [
                ('width', ctypes.c_int),
                ('height', ctypes.c_int),
                ('type', ctypes.c_uint32),
                ('date', ctypes.c_ulonglong),
                ('size', ctypes.c_int),
                ('data_pointer', ctypes.c_void_p),
                ]

    @property
    def data(self):
        return ctypes.string_at(self.data_pointer, self.size)

    def __str__(self):
        return "RGBPicture (%d, %d) - %ld ms - %d bytes" % (self.width, self.height, self.date, self.size)

    def free(self):
        mediacontrol_RGBPicture__free(self)

def check_vlc_exception(result, func, args):
    """Error checking method for functions using an exception in/out parameter.
    """
    ex=args[-1]
    if not isinstance(ex, (VLCException, MediaControlException)):
        logging.warn("python-vlc: error when processing function %s. Please report this as a bug to vlc-devel@videolan.org" % str(func))
        return result
    # Take into account both VLCException and MediacontrolException:
    c=getattr(ex, 'raised', getattr(ex, 'code', 0))
    if c:
        raise LibVLCException(ex.message)
    return result

### End of header.py ###
class AudioOutput(object):

    def __new__(cls, pointer=None):
        '''Internal method used for instanciating wrappers from ctypes.
        '''
        if pointer is None:
            raise Exception("Internal method. Surely this class cannot be instanciated by itself.")
        if pointer == 0:
            return None
        else:
            o=object.__new__(cls)
            o._as_parameter_=ctypes.c_void_p(pointer)
            return o


    @staticmethod
    def from_param(arg):
        '''(INTERNAL) ctypes parameter conversion method.
        '''
        return arg._as_parameter_

    if hasattr(dll, 'libvlc_audio_output_list_release'):
        def list_release(self):
            """Free the list of available audio outputs
        """
            return libvlc_audio_output_list_release(self)

class EventManager(object):

    def __new__(cls, pointer=None):
        '''Internal method used for instanciating wrappers from ctypes.
        '''
        if pointer is None:
            raise Exception("Internal method. Surely this class cannot be instanciated by itself.")
        if pointer == 0:
            return None
        else:
            o=object.__new__(cls)
            o._as_parameter_=ctypes.c_void_p(pointer)
            return o


    @staticmethod
    def from_param(arg):
        '''(INTERNAL) ctypes parameter conversion method.
        '''
        return arg._as_parameter_

    if hasattr(dll, 'libvlc_event_attach'):
        def event_attach(self, i_event_type, f_callback, user_data):
            """Register for an event notification.
@param i_event_type: the desired event to which we want to listen
@param f_callback: the function to call when i_event_type occurs
@param user_data: user provided data to carry with the event
        """
            e=VLCException()
            return libvlc_event_attach(self, i_event_type, f_callback, user_data, e)

    if hasattr(dll, 'libvlc_event_detach'):
        def event_detach(self, i_event_type, f_callback, p_user_data):
            """Unregister an event notification.
@param i_event_type: the desired event to which we want to unregister
@param f_callback: the function to call when i_event_type occurs
@param p_user_data: user provided data to carry with the event
        """
            e=VLCException()
            return libvlc_event_detach(self, i_event_type, f_callback, p_user_data, e)

class Instance(object):
    """Create a new Instance instance.

    It may take as parameter either:
      - a string
      - a list of strings as first parameters
      - the parameters given as the constructor parameters (must be strings)
      - a MediaControl instance
    
    """

    @staticmethod
    def from_param(arg):
        '''(INTERNAL) ctypes parameter conversion method.
        '''
        return arg._as_parameter_


    def __new__(cls, *p):
        if p and p[0] == 0:
            return None
        elif p and isinstance(p[0], (int, long)):
            # instance creation from ctypes
            o=object.__new__(cls)
            o._as_parameter_=ctypes.c_void_p(p[0])
            return o
        elif len(p) == 1 and isinstance(p[0], basestring):
            # Only 1 string parameter: should be a parameter line
            p=p[0].split(' ')
        elif len(p) == 1 and isinstance(p[0], (tuple, list)):
            p=p[0]

        if p and isinstance(p[0], MediaControl):
            return p[0].get_instance()
        else:
            if not p and detected_plugin_path is not None:
                # No parameters passed. Under win32 and MacOS, specify
                # the detected_plugin_path if present.
                p=[ 'vlc', '--plugin-path='+ detected_plugin_path ]
            e=VLCException()
            return libvlc_new(len(p), p, e)

    def media_player_new(self, uri=None):
        """Create a new Media Player object.

        @param uri: an optional URI to play in the player.
        """
        e=VLCException()
        p=libvlc_media_player_new(self, e)
        if uri:
            p.set_media(self.media_new(uri))
        p._instance=self
        return p

    def media_list_player_new(self):
        """Create an empty Media Player object
        """
        e=VLCException()
        p=libvlc_media_list_player_new(self, e)
        p._instance=self
        return p

    def media_new(self, mrl, *options):
        """Create an empty Media Player object

        Options can be specified as supplementary string parameters, e.g.
        m=i.media_new('foo.avi', 'sub-filter=marq{marquee=Hello}', 'vout-filter=invert')
        """
        e=VLCException()
        m=libvlc_media_new(self, mrl, e)
        for o in options:
            libvlc_media_add_option(m, o, e)
        return m


    if hasattr(dll, 'libvlc_get_vlc_id'):
        def get_vlc_id(self):
            """Return a libvlc instance identifier for legacy APIs. Use of this
function is discouraged, you should convert your program to use the
new API.
@return: the instance identifier
        """
            return libvlc_get_vlc_id(self)

    if hasattr(dll, 'libvlc_release'):
        def release(self):
            """Decrement the reference count of a libvlc instance, and destroy it
if it reaches zero.
        """
            return libvlc_release(self)

    if hasattr(dll, 'libvlc_retain'):
        def retain(self):
            """Increments the reference count of a libvlc instance.
The initial reference count is 1 after libvlc_new() returns.
        """
            return libvlc_retain(self)

    if hasattr(dll, 'libvlc_add_intf'):
        def add_intf(self, name):
            """Try to start a user interface for the libvlc instance.
@param name: interface name, or NULL for default
        """
            e=VLCException()
            return libvlc_add_intf(self, name, e)

    if hasattr(dll, 'libvlc_wait'):
        def wait(self):
            """Waits until an interface causes the instance to exit.
You should start at least one interface first, using libvlc_add_intf().
        """
            return libvlc_wait(self)

    if hasattr(dll, 'libvlc_get_log_verbosity'):
        def get_log_verbosity(self):
            """Return the VLC messaging verbosity level.
@return: verbosity level for messages
        """
            e=VLCException()
            return libvlc_get_log_verbosity(self, e)

    if hasattr(dll, 'libvlc_set_log_verbosity'):
        def set_log_verbosity(self, level):
            """Set the VLC messaging verbosity level.
@param level: log level
        """
            e=VLCException()
            return libvlc_set_log_verbosity(self, level, e)

    if hasattr(dll, 'libvlc_log_open'):
        def log_open(self):
            """Open a VLC message log instance.
@return: log message instance
        """
            e=VLCException()
            return libvlc_log_open(self, e)

    if hasattr(dll, 'libvlc_media_new_as_node'):
        def media_new_as_node(self, psz_name):
            """Create a media as an empty node with the passed name.
@param psz_name: the name of the node
@return: the new empty media
        """
            e=VLCException()
            return libvlc_media_new_as_node(self, psz_name, e)

    if hasattr(dll, 'libvlc_media_discoverer_new_from_name'):
        def media_discoverer_new_from_name(self, psz_name):
            """Discover media service by name.
@param psz_name: service name
@return: media discover object
        """
            e=VLCException()
            return libvlc_media_discoverer_new_from_name(self, psz_name, e)

    if hasattr(dll, 'libvlc_media_library_new'):
        def media_library_new(self):
            """\ingroup libvlc
LibVLC Media Library

        """
            e=VLCException()
            return libvlc_media_library_new(self, e)

    if hasattr(dll, 'libvlc_media_list_new'):
        def media_list_new(self):
            """Create an empty media list.
@return: empty media list
        """
            e=VLCException()
            return libvlc_media_list_new(self, e)

    if hasattr(dll, 'libvlc_audio_output_list_get'):
        def audio_output_list_get(self):
            """Get the list of available audio outputs
@return: list of available audio outputs, at the end free it with
        """
            e=VLCException()
            return libvlc_audio_output_list_get(self, e)

    if hasattr(dll, 'libvlc_audio_output_set'):
        def audio_output_set(self, psz_name):
            """Set the audio output.
Change will be applied after stop and play.
@return: true if function succeded
        """
            return libvlc_audio_output_set(self, psz_name)

    if hasattr(dll, 'libvlc_audio_output_device_count'):
        def audio_output_device_count(self, psz_audio_output):
            """Get count of devices for audio output, these devices are hardware oriented
like analor or digital output of sound card
@return: number of devices
        """
            return libvlc_audio_output_device_count(self, psz_audio_output)

    if hasattr(dll, 'libvlc_audio_output_device_longname'):
        def audio_output_device_longname(self, psz_audio_output, i_device):
            """Get long name of device, if not available short name given
@param psz_audio_output: - name of audio output, \see libvlc_audio_output_t
@return: long name of device
        """
            return libvlc_audio_output_device_longname(self, psz_audio_output, i_device)

    if hasattr(dll, 'libvlc_audio_output_device_id'):
        def audio_output_device_id(self, psz_audio_output, i_device):
            """Get id name of device
@param psz_audio_output: - name of audio output, \see libvlc_audio_output_t
@return: id name of device, use for setting device, need to be free after use
        """
            return libvlc_audio_output_device_id(self, psz_audio_output, i_device)

    if hasattr(dll, 'libvlc_audio_output_device_set'):
        def audio_output_device_set(self, psz_audio_output, psz_device_id):
            """Set device for using
@param psz_audio_output: - name of audio output, \see libvlc_audio_output_t
        """
            return libvlc_audio_output_device_set(self, psz_audio_output, psz_device_id)

    if hasattr(dll, 'libvlc_audio_output_get_device_type'):
        def audio_output_get_device_type(self):
            """Get current audio device type. Device type describes something like
character of output sound - stereo sound, 2.1, 5.1 etc
@return: the audio devices type \see libvlc_audio_output_device_types_t
        """
            e=VLCException()
            return libvlc_audio_output_get_device_type(self, e)

    if hasattr(dll, 'libvlc_audio_output_set_device_type'):
        def audio_output_set_device_type(self, device_type):
            """Set current audio device type.
@param device_type: the audio device type,
        """
            e=VLCException()
            return libvlc_audio_output_set_device_type(self, device_type, e)

    if hasattr(dll, 'libvlc_audio_toggle_mute'):
        def audio_toggle_mute(self):
            """Toggle mute status.
        """
            e=VLCException()
            return libvlc_audio_toggle_mute(self, e)

    if hasattr(dll, 'libvlc_audio_get_mute'):
        def audio_get_mute(self):
            """Get current mute status.
@return: the mute status (boolean)
        """
            e=VLCException()
            return libvlc_audio_get_mute(self, e)

    if hasattr(dll, 'libvlc_audio_set_mute'):
        def audio_set_mute(self, status):
            """Set mute status.
@param status: If status is true then mute, otherwise unmute
        """
            e=VLCException()
            return libvlc_audio_set_mute(self, status, e)

    if hasattr(dll, 'libvlc_audio_get_volume'):
        def audio_get_volume(self):
            """Get current audio level.
@return: the audio level (int)
        """
            e=VLCException()
            return libvlc_audio_get_volume(self, e)

    if hasattr(dll, 'libvlc_audio_set_volume'):
        def audio_set_volume(self, i_volume):
            """Set current audio level.
@param i_volume: the volume (int)
        """
            e=VLCException()
            return libvlc_audio_set_volume(self, i_volume, e)

    if hasattr(dll, 'libvlc_audio_get_channel'):
        def audio_get_channel(self):
            """Get current audio channel.
@return: the audio channel \see libvlc_audio_output_channel_t
        """
            e=VLCException()
            return libvlc_audio_get_channel(self, e)

    if hasattr(dll, 'libvlc_audio_set_channel'):
        def audio_set_channel(self, channel):
            """Set current audio channel.
@param channel: the audio channel, \see libvlc_audio_output_channel_t
        """
            e=VLCException()
            return libvlc_audio_set_channel(self, channel, e)

    if hasattr(dll, 'libvlc_vlm_release'):
        def vlm_release(self):
            """Release the vlm instance related to the given libvlc_instance_t
        """
            e=VLCException()
            return libvlc_vlm_release(self, e)

    if hasattr(dll, 'libvlc_vlm_add_broadcast'):
        def vlm_add_broadcast(self, psz_name, psz_input, psz_output, i_options, ppsz_options, b_enabled, b_loop):
            """Add a broadcast, with one input.
@param psz_name: the name of the new broadcast
@param psz_input: the input MRL
@param psz_output: the output MRL (the parameter to the "sout" variable)
@param i_options: number of additional options
@param ppsz_options: additional options
@param b_enabled: boolean for enabling the new broadcast
@param b_loop: Should this broadcast be played in loop ?
        """
            e=VLCException()
            return libvlc_vlm_add_broadcast(self, psz_name, psz_input, psz_output, i_options, ppsz_options, b_enabled, b_loop, e)

    if hasattr(dll, 'libvlc_vlm_add_vod'):
        def vlm_add_vod(self, psz_name, psz_input, i_options, ppsz_options, b_enabled, psz_mux):
            """Add a vod, with one input.
@param psz_name: the name of the new vod media
@param psz_input: the input MRL
@param i_options: number of additional options
@param ppsz_options: additional options
@param b_enabled: boolean for enabling the new vod
@param psz_mux: the muxer of the vod media
        """
            e=VLCException()
            return libvlc_vlm_add_vod(self, psz_name, psz_input, i_options, ppsz_options, b_enabled, psz_mux, e)

    if hasattr(dll, 'libvlc_vlm_del_media'):
        def vlm_del_media(self, psz_name):
            """Delete a media (VOD or broadcast).
@param psz_name: the media to delete
        """
            e=VLCException()
            return libvlc_vlm_del_media(self, psz_name, e)

    if hasattr(dll, 'libvlc_vlm_set_enabled'):
        def vlm_set_enabled(self, psz_name, b_enabled):
            """Enable or disable a media (VOD or broadcast).
@param psz_name: the media to work on
@param b_enabled: the new status
        """
            e=VLCException()
            return libvlc_vlm_set_enabled(self, psz_name, b_enabled, e)

    if hasattr(dll, 'libvlc_vlm_set_output'):
        def vlm_set_output(self, psz_name, psz_output):
            """Set the output for a media.
@param psz_name: the media to work on
@param psz_output: the output MRL (the parameter to the "sout" variable)
        """
            e=VLCException()
            return libvlc_vlm_set_output(self, psz_name, psz_output, e)

    if hasattr(dll, 'libvlc_vlm_set_input'):
        def vlm_set_input(self, psz_name, psz_input):
            """Set a media's input MRL. This will delete all existing inputs and
add the specified one.
@param psz_name: the media to work on
@param psz_input: the input MRL
        """
            e=VLCException()
            return libvlc_vlm_set_input(self, psz_name, psz_input, e)

    if hasattr(dll, 'libvlc_vlm_add_input'):
        def vlm_add_input(self, psz_name, psz_input):
            """Add a media's input MRL. This will add the specified one.
@param psz_name: the media to work on
@param psz_input: the input MRL
        """
            e=VLCException()
            return libvlc_vlm_add_input(self, psz_name, psz_input, e)

    if hasattr(dll, 'libvlc_vlm_set_loop'):
        def vlm_set_loop(self, psz_name, b_loop):
            """Set a media's loop status.
@param psz_name: the media to work on
@param b_loop: the new status
        """
            e=VLCException()
            return libvlc_vlm_set_loop(self, psz_name, b_loop, e)

    if hasattr(dll, 'libvlc_vlm_set_mux'):
        def vlm_set_mux(self, psz_name, psz_mux):
            """Set a media's vod muxer.
@param psz_name: the media to work on
@param psz_mux: the new muxer
        """
            e=VLCException()
            return libvlc_vlm_set_mux(self, psz_name, psz_mux, e)

    if hasattr(dll, 'libvlc_vlm_change_media'):
        def vlm_change_media(self, psz_name, psz_input, psz_output, i_options, ppsz_options, b_enabled, b_loop):
            """Edit the parameters of a media. This will delete all existing inputs and
add the specified one.
@param psz_name: the name of the new broadcast
@param psz_input: the input MRL
@param psz_output: the output MRL (the parameter to the "sout" variable)
@param i_options: number of additional options
@param ppsz_options: additional options
@param b_enabled: boolean for enabling the new broadcast
@param b_loop: Should this broadcast be played in loop ?
        """
            e=VLCException()
            return libvlc_vlm_change_media(self, psz_name, psz_input, psz_output, i_options, ppsz_options, b_enabled, b_loop, e)

    if hasattr(dll, 'libvlc_vlm_play_media'):
        def vlm_play_media(self, psz_name):
            """Play the named broadcast.
@param psz_name: the name of the broadcast
        """
            e=VLCException()
            return libvlc_vlm_play_media(self, psz_name, e)

    if hasattr(dll, 'libvlc_vlm_stop_media'):
        def vlm_stop_media(self, psz_name):
            """Stop the named broadcast.
@param psz_name: the name of the broadcast
        """
            e=VLCException()
            return libvlc_vlm_stop_media(self, psz_name, e)

    if hasattr(dll, 'libvlc_vlm_pause_media'):
        def vlm_pause_media(self, psz_name):
            """Pause the named broadcast.
@param psz_name: the name of the broadcast
        """
            e=VLCException()
            return libvlc_vlm_pause_media(self, psz_name, e)

    if hasattr(dll, 'libvlc_vlm_seek_media'):
        def vlm_seek_media(self, psz_name, f_percentage):
            """Seek in the named broadcast.
@param psz_name: the name of the broadcast
@param f_percentage: the percentage to seek to
        """
            e=VLCException()
            return libvlc_vlm_seek_media(self, psz_name, f_percentage, e)

    if hasattr(dll, 'libvlc_vlm_show_media'):
        def vlm_show_media(self, psz_name):
            """Return information about the named broadcast.
\bug will always return NULL
@param psz_name: the name of the broadcast
@return: string with information about named media
        """
            e=VLCException()
            return libvlc_vlm_show_media(self, psz_name, e)

    if hasattr(dll, 'libvlc_vlm_get_media_instance_position'):
        def vlm_get_media_instance_position(self, psz_name, i_instance):
            """Get vlm_media instance position by name or instance id
@param psz_name: name of vlm media instance
@param i_instance: instance id
@return: position as float
        """
            e=VLCException()
            return libvlc_vlm_get_media_instance_position(self, psz_name, i_instance, e)

    if hasattr(dll, 'libvlc_vlm_get_media_instance_time'):
        def vlm_get_media_instance_time(self, psz_name, i_instance):
            """Get vlm_media instance time by name or instance id
@param psz_name: name of vlm media instance
@param i_instance: instance id
@return: time as integer
        """
            e=VLCException()
            return libvlc_vlm_get_media_instance_time(self, psz_name, i_instance, e)

    if hasattr(dll, 'libvlc_vlm_get_media_instance_length'):
        def vlm_get_media_instance_length(self, psz_name, i_instance):
            """Get vlm_media instance length by name or instance id
@param psz_name: name of vlm media instance
@param i_instance: instance id
@return: length of media item
        """
            e=VLCException()
            return libvlc_vlm_get_media_instance_length(self, psz_name, i_instance, e)

    if hasattr(dll, 'libvlc_vlm_get_media_instance_rate'):
        def vlm_get_media_instance_rate(self, psz_name, i_instance):
            """Get vlm_media instance playback rate by name or instance id
@param psz_name: name of vlm media instance
@param i_instance: instance id
@return: playback rate
        """
            e=VLCException()
            return libvlc_vlm_get_media_instance_rate(self, psz_name, i_instance, e)

    if hasattr(dll, 'libvlc_vlm_get_media_instance_title'):
        def vlm_get_media_instance_title(self, psz_name, i_instance):
            """Get vlm_media instance title number by name or instance id
\bug will always return 0
@param psz_name: name of vlm media instance
@param i_instance: instance id
@return: title as number
        """
            e=VLCException()
            return libvlc_vlm_get_media_instance_title(self, psz_name, i_instance, e)

    if hasattr(dll, 'libvlc_vlm_get_media_instance_chapter'):
        def vlm_get_media_instance_chapter(self, psz_name, i_instance):
            """Get vlm_media instance chapter number by name or instance id
\bug will always return 0
@param psz_name: name of vlm media instance
@param i_instance: instance id
@return: chapter as number
        """
            e=VLCException()
            return libvlc_vlm_get_media_instance_chapter(self, psz_name, i_instance, e)

    if hasattr(dll, 'libvlc_vlm_get_media_instance_seekable'):
        def vlm_get_media_instance_seekable(self, psz_name, i_instance):
            """Is libvlc instance seekable ?
\bug will always return 0
@param psz_name: name of vlm media instance
@param i_instance: instance id
@return: 1 if seekable, 0 if not
        """
            e=VLCException()
            return libvlc_vlm_get_media_instance_seekable(self, psz_name, i_instance, e)

    if hasattr(dll, 'mediacontrol_new_from_instance'):
        def mediacontrol_new_from_instance(self):
            """Create a MediaControl instance from an existing libvlc instance
@return: a mediacontrol_Instance
        """
            e=MediaControlException()
            return mediacontrol_new_from_instance(self, e)

class Log(object):

    def __new__(cls, pointer=None):
        '''Internal method used for instanciating wrappers from ctypes.
        '''
        if pointer is None:
            raise Exception("Internal method. Surely this class cannot be instanciated by itself.")
        if pointer == 0:
            return None
        else:
            o=object.__new__(cls)
            o._as_parameter_=ctypes.c_void_p(pointer)
            return o


    @staticmethod
    def from_param(arg):
        '''(INTERNAL) ctypes parameter conversion method.
        '''
        return arg._as_parameter_

    def __iter__(self):
        return self.get_iterator()

    def dump(self):
        return [ str(m) for m in self ]

    if hasattr(dll, 'libvlc_log_close'):
        def close(self):
            """Close a VLC message log instance.
        """
            e=VLCException()
            return libvlc_log_close(self, e)

    if hasattr(dll, 'libvlc_log_count'):
        def count(self):
            """Returns the number of messages in a log instance.
@return: number of log messages
        """
            e=VLCException()
            return libvlc_log_count(self, e)

    def __len__(self):
        e=VLCException()
        return libvlc_log_count(self, e)

    if hasattr(dll, 'libvlc_log_clear'):
        def clear(self):
            """Clear a log instance.
All messages in the log are removed. The log should be cleared on a
regular basis to avoid clogging.
        """
            e=VLCException()
            return libvlc_log_clear(self, e)

    if hasattr(dll, 'libvlc_log_get_iterator'):
        def get_iterator(self):
            """Allocate and returns a new iterator to messages in log.
@return: log iterator object
        """
            e=VLCException()
            return libvlc_log_get_iterator(self, e)

class LogIterator(object):

    def __new__(cls, pointer=None):
        '''Internal method used for instanciating wrappers from ctypes.
        '''
        if pointer is None:
            raise Exception("Internal method. Surely this class cannot be instanciated by itself.")
        if pointer == 0:
            return None
        else:
            o=object.__new__(cls)
            o._as_parameter_=ctypes.c_void_p(pointer)
            return o


    @staticmethod
    def from_param(arg):
        '''(INTERNAL) ctypes parameter conversion method.
        '''
        return arg._as_parameter_

    def __iter__(self):
        return self

    def next(self):
        if not self.has_next():
            raise StopIteration
        buf=LogMessage()
        e=VLCException()
        ret=libvlc_log_iterator_next(self, buf, e)
        return ret.contents


    if hasattr(dll, 'libvlc_log_iterator_free'):
        def free(self):
            """Release a previoulsy allocated iterator.
        """
            e=VLCException()
            return libvlc_log_iterator_free(self, e)

    if hasattr(dll, 'libvlc_log_iterator_has_next'):
        def has_next(self):
            """Return whether log iterator has more messages.
@return: true if iterator has more message objects, else false
        """
            e=VLCException()
            return libvlc_log_iterator_has_next(self, e)

class Media(object):

    def __new__(cls, pointer=None):
        '''Internal method used for instanciating wrappers from ctypes.
        '''
        if pointer is None:
            raise Exception("Internal method. Surely this class cannot be instanciated by itself.")
        if pointer == 0:
            return None
        else:
            o=object.__new__(cls)
            o._as_parameter_=ctypes.c_void_p(pointer)
            return o


    @staticmethod
    def from_param(arg):
        '''(INTERNAL) ctypes parameter conversion method.
        '''
        return arg._as_parameter_

    def add_options(self, *list_of_options):
        """Add a list of options to the media.

        Options must be written without the double-dash, e.g.:
        m.add_options('sub-filter=marq@test{marquee=Hello}', 'video-filter=invert')

        Note that you also can directly pass these options in the Instance.media_new method:
        m=instance.media_new( 'foo.avi', 'sub-filter=marq@test{marquee=Hello}', 'video-filter=invert')
        """
        for o in list_of_options:
            self.add_option(o)


    if hasattr(dll, 'libvlc_media_add_option'):
        def add_option(self, ppsz_options):
            """Add an option to the media.
This option will be used to determine how the media_player will
read the media. This allows to use VLC's advanced
reading/streaming options on a per-media basis.
The options are detailed in vlc --long-help, for instance "--sout-all"
@param ppsz_options: the options (as a string)
        """
            e=VLCException()
            return libvlc_media_add_option(self, ppsz_options, e)

    if hasattr(dll, 'libvlc_media_add_option_untrusted'):
        def add_option_untrusted(self, ppsz_options):
            """Add an option to the media from an untrusted source.
This option will be used to determine how the media_player will
read the media. This allows to use VLC's advanced
reading/streaming options on a per-media basis.
The options are detailed in vlc --long-help, for instance "--sout-all"
@param ppsz_options: the options (as a string)
        """
            e=VLCException()
            return libvlc_media_add_option_untrusted(self, ppsz_options, e)

    if hasattr(dll, 'libvlc_media_retain'):
        def retain(self):
            """Retain a reference to a media descriptor object (libvlc_media_t). Use
libvlc_media_release() to decrement the reference count of a
media descriptor object.
        """
            return libvlc_media_retain(self)

    if hasattr(dll, 'libvlc_media_release'):
        def release(self):
            """Decrement the reference count of a media descriptor object. If the
reference count is 0, then libvlc_media_release() will release the
media descriptor object. It will send out an libvlc_MediaFreed event
to all listeners. If the media descriptor object has been released it
should not be used again.
        """
            return libvlc_media_release(self)

    if hasattr(dll, 'libvlc_media_get_mrl'):
        def get_mrl(self):
            """Get the media resource locator (mrl) from a media descriptor object
@return: string with mrl of media descriptor object
        """
            e=VLCException()
            return libvlc_media_get_mrl(self, e)

    if hasattr(dll, 'libvlc_media_duplicate'):
        def duplicate(self):
            """Duplicate a media descriptor object.
        """
            return libvlc_media_duplicate(self)

    if hasattr(dll, 'libvlc_media_get_meta'):
        def get_meta(self, e_meta):
            """Read the meta of the media.
@param e_meta: the meta to read
@return: the media's meta
        """
            e=VLCException()
            return libvlc_media_get_meta(self, e_meta, e)

    if hasattr(dll, 'libvlc_media_get_state'):
        def get_state(self):
            """Get current state of media descriptor object. Possible media states
are defined in libvlc_structures.c ( libvlc_NothingSpecial=0,
libvlc_Opening, libvlc_Buffering, libvlc_Playing, libvlc_Paused,
libvlc_Stopped, libvlc_Ended,
libvlc_Error).
See libvlc_state_t
@return: state of media descriptor object
        """
            e=VLCException()
            return libvlc_media_get_state(self, e)

    if hasattr(dll, 'libvlc_media_subitems'):
        def subitems(self):
            """Get subitems of media descriptor object. This will increment
the reference count of supplied media descriptor object. Use
libvlc_media_list_release() to decrement the reference counting.
@return: list of media descriptor subitems or NULL
        """
            e=VLCException()
            return libvlc_media_subitems(self, e)

    if hasattr(dll, 'libvlc_media_event_manager'):
        def event_manager(self):
            """Get event manager from media descriptor object.
NOTE: this function doesn't increment reference counting.
@return: event manager object
        """
            e=VLCException()
            return libvlc_media_event_manager(self, e)

    if hasattr(dll, 'libvlc_media_get_duration'):
        def get_duration(self):
            """Get duration of media descriptor object item.
@return: duration of media item
        """
            e=VLCException()
            return libvlc_media_get_duration(self, e)

    if hasattr(dll, 'libvlc_media_is_preparsed'):
        def is_preparsed(self):
            """Get preparsed status for media descriptor object.
@return: true if media object has been preparsed otherwise it returns false
        """
            e=VLCException()
            return libvlc_media_is_preparsed(self, e)

    if hasattr(dll, 'libvlc_media_set_user_data'):
        def set_user_data(self, p_new_user_data):
            """Sets media descriptor's user_data. user_data is specialized data
accessed by the host application, VLC.framework uses it as a pointer to
an native object that references a libvlc_media_t pointer
@param p_new_user_data: pointer to user data
        """
            e=VLCException()
            return libvlc_media_set_user_data(self, p_new_user_data, e)

    if hasattr(dll, 'libvlc_media_get_user_data'):
        def get_user_data(self):
            """Get media descriptor's user_data. user_data is specialized data
accessed by the host application, VLC.framework uses it as a pointer to
an native object that references a libvlc_media_t pointer
        """
            e=VLCException()
            return libvlc_media_get_user_data(self, e)

    if hasattr(dll, 'libvlc_media_player_new_from_media'):
        def player_new_from_media(self):
            """Create a Media Player object from a Media
        """
            e=VLCException()
            return libvlc_media_player_new_from_media(self, e)

class MediaControl(object):
    """Create a new MediaControl instance

    It may take as parameter either:
      - a string
      - a list of strings as first parameters
      - the parameters given as the constructor parameters (must be strings)
      - a vlc.Instance
    
    """

    @staticmethod
    def from_param(arg):
        '''(INTERNAL) ctypes parameter conversion method.
        '''
        return arg._as_parameter_


    def __new__(cls, *p):
        if p and p[0] == 0:
            return None
        elif p and isinstance(p[0], (int, long)):
            # instance creation from ctypes
            o=object.__new__(cls)
            o._as_parameter_=ctypes.c_void_p(p[0])
            return o
        elif len(p) == 1 and isinstance(p[0], basestring):
            # Only 1 string parameter: should be a parameter line
            p=p[0].split(' ')
        elif len(p) == 1 and isinstance(p[0], (tuple, list)):
            p=p[0]

        if p and isinstance(p[0], Instance):
            e=MediaControlException()
            return mediacontrol_new_from_instance(p[0], e)
        else:
            if not p and detected_plugin_path is not None:
                # No parameters passed. Under win32 and MacOS, specify
                # the detected_plugin_path if present.
                p=[ 'vlc', '--plugin-path='+ detected_plugin_path ]
            e=MediaControlException()
            return mediacontrol_new(len(p), p, e)

    def get_media_position(self, origin=PositionOrigin.AbsolutePosition, key=PositionKey.MediaTime):
        e=MediaControlException()
        p=mediacontrol_get_media_position(self, origin, key, e)
        if p:
            return p.contents
        else:
            return None

    def set_media_position(self, pos):
        """Set the media position.

        @param pos: a MediaControlPosition or an integer (in ms)
        """
        if not isinstance(pos, MediaControlPosition):
            pos=MediaControlPosition(long(pos))
        e=MediaControlException()
        mediacontrol_set_media_position(self, pos, e)

    def start(self, pos=0):
        """Start the player at the given position.

        @param pos: a MediaControlPosition or an integer (in ms)
        """
        if not isinstance(pos, MediaControlPosition):
            pos=MediaControlPosition(long(pos))
        e=MediaControlException()
        mediacontrol_start(self, pos, e)

    def snapshot(self, pos=0):
        """Take a snapshot.

        Note: the position parameter is not properly implemented. For
        the moment, the only valid position is the 0-relative position
        (i.e. the current position).

        @param pos: a MediaControlPosition or an integer (in ms)
        """
        if not isinstance(pos, MediaControlPosition):
            pos=MediaControlPosition(long(pos))
        e=MediaControlException()
        p=mediacontrol_snapshot(self, pos, e)
        if p:
            snap=p.contents
            # FIXME: there is a bug in the current mediacontrol_snapshot
            # implementation, which sets an incorrect date.
            # Workaround here:
            snap.date=self.get_media_position().value
            return snap
        else:
            return None

    def display_text(self, message='', begin=0, end=1000):
        """Display a caption between begin and end positions.

        @param message: the caption to display
        @param begin: the begin position
        @param end: the end position
        """
        if not isinstance(begin, MediaControlPosition):
            begin=self.value2position(begin)
        if not isinstance(end, MediaControlPosition):
            end=self.value2position(end)
        e=MediaControlException()
        mediacontrol_display_text(self, message, begin, end, e)

    def get_stream_information(self, key=PositionKey.MediaTime):
        """Return information about the stream.
        """
        e=MediaControlException()
        return mediacontrol_get_stream_information(self, key, e).contents


    if hasattr(dll, 'mediacontrol_get_libvlc_instance'):
        def get_instance(self):
            """Get the associated libvlc instance
@return: a libvlc instance
        """
            return mediacontrol_get_libvlc_instance(self)

    if hasattr(dll, 'mediacontrol_get_media_player'):
        def get_media_player(self):
            """Get the associated libvlc_media_player
@return: a libvlc_media_player_t instance
        """
            return mediacontrol_get_media_player(self)

    if hasattr(dll, 'mediacontrol_pause'):
        def pause(self):
            """Pause the movie at a given position
        """
            e=MediaControlException()
            return mediacontrol_pause(self, e)

    if hasattr(dll, 'mediacontrol_resume'):
        def resume(self):
            """Resume the movie at a given position
        """
            e=MediaControlException()
            return mediacontrol_resume(self, e)

    if hasattr(dll, 'mediacontrol_stop'):
        def stop(self):
            """Stop the movie at a given position
        """
            e=MediaControlException()
            return mediacontrol_stop(self, e)

    if hasattr(dll, 'mediacontrol_exit'):
        def exit(self):
            """Exit the player
        """
            return mediacontrol_exit(self)

    if hasattr(dll, 'mediacontrol_set_mrl'):
        def set_mrl(self, psz_file):
            """Set the MRL to be played.
@param psz_file: the MRL
        """
            e=MediaControlException()
            return mediacontrol_set_mrl(self, psz_file, e)

    if hasattr(dll, 'mediacontrol_get_mrl'):
        def get_mrl(self):
            """Get the MRL to be played.
        """
            e=MediaControlException()
            return mediacontrol_get_mrl(self, e)

    if hasattr(dll, 'mediacontrol_sound_get_volume'):
        def sound_get_volume(self):
            """Get the current audio level, normalized in [0..100]
@return: the volume
        """
            e=MediaControlException()
            return mediacontrol_sound_get_volume(self, e)

    if hasattr(dll, 'mediacontrol_sound_set_volume'):
        def sound_set_volume(self, volume):
            """Set the audio level
@param volume: the volume (normalized in [0..100])
        """
            e=MediaControlException()
            return mediacontrol_sound_set_volume(self, volume, e)

    if hasattr(dll, 'mediacontrol_set_visual'):
        def set_visual(self, visual_id):
            """Set the video output window
@param visual_id: the Xid or HWND, depending on the platform
        """
            e=MediaControlException()
            return mediacontrol_set_visual(self, visual_id, e)

    if hasattr(dll, 'mediacontrol_get_rate'):
        def get_rate(self):
            """Get the current playing rate, in percent
@return: the rate
        """
            e=MediaControlException()
            return mediacontrol_get_rate(self, e)

    if hasattr(dll, 'mediacontrol_set_rate'):
        def set_rate(self, rate):
            """Set the playing rate, in percent
@param rate: the desired rate
        """
            e=MediaControlException()
            return mediacontrol_set_rate(self, rate, e)

    if hasattr(dll, 'mediacontrol_get_fullscreen'):
        def get_fullscreen(self):
            """Get current fullscreen status
@return: the fullscreen status
        """
            e=MediaControlException()
            return mediacontrol_get_fullscreen(self, e)

    if hasattr(dll, 'mediacontrol_set_fullscreen'):
        def set_fullscreen(self, b_fullscreen):
            """Set fullscreen status
@param b_fullscreen: the desired status
        """
            e=MediaControlException()
            return mediacontrol_set_fullscreen(self, b_fullscreen, e)

class MediaDiscoverer(object):

    def __new__(cls, pointer=None):
        '''Internal method used for instanciating wrappers from ctypes.
        '''
        if pointer is None:
            raise Exception("Internal method. Surely this class cannot be instanciated by itself.")
        if pointer == 0:
            return None
        else:
            o=object.__new__(cls)
            o._as_parameter_=ctypes.c_void_p(pointer)
            return o


    @staticmethod
    def from_param(arg):
        '''(INTERNAL) ctypes parameter conversion method.
        '''
        return arg._as_parameter_

    if hasattr(dll, 'libvlc_media_discoverer_release'):
        def release(self):
            """Release media discover object. If the reference count reaches 0, then
the object will be released.
        """
            return libvlc_media_discoverer_release(self)

    if hasattr(dll, 'libvlc_media_discoverer_localized_name'):
        def localized_name(self):
            """Get media service discover object its localized name.
@return: localized name
        """
            return libvlc_media_discoverer_localized_name(self)

    if hasattr(dll, 'libvlc_media_discoverer_media_list'):
        def media_list(self):
            """Get media service discover media list.
@return: list of media items
        """
            return libvlc_media_discoverer_media_list(self)

    if hasattr(dll, 'libvlc_media_discoverer_event_manager'):
        def event_manager(self):
            """Get event manager from media service discover object.
@return: event manager object.
        """
            return libvlc_media_discoverer_event_manager(self)

    if hasattr(dll, 'libvlc_media_discoverer_is_running'):
        def is_running(self):
            """Query if media service discover object is running.
@return: true if running, false if not
        """
            return libvlc_media_discoverer_is_running(self)

class MediaLibrary(object):

    def __new__(cls, pointer=None):
        '''Internal method used for instanciating wrappers from ctypes.
        '''
        if pointer is None:
            raise Exception("Internal method. Surely this class cannot be instanciated by itself.")
        if pointer == 0:
            return None
        else:
            o=object.__new__(cls)
            o._as_parameter_=ctypes.c_void_p(pointer)
            return o


    @staticmethod
    def from_param(arg):
        '''(INTERNAL) ctypes parameter conversion method.
        '''
        return arg._as_parameter_

    if hasattr(dll, 'libvlc_media_library_release'):
        def release(self):
            """Release media library object. This functions decrements the
reference count of the media library object. If it reaches 0,
then the object will be released.
        """
            return libvlc_media_library_release(self)

    if hasattr(dll, 'libvlc_media_library_retain'):
        def retain(self):
            """Retain a reference to a media library object. This function will
increment the reference counting for this object. Use
libvlc_media_library_release() to decrement the reference count.
        """
            return libvlc_media_library_retain(self)

    if hasattr(dll, 'libvlc_media_library_load'):
        def load(self):
            """Load media library.
        """
            e=VLCException()
            return libvlc_media_library_load(self, e)

    if hasattr(dll, 'libvlc_media_library_save'):
        def save(self):
            """Save media library.
        """
            e=VLCException()
            return libvlc_media_library_save(self, e)

    if hasattr(dll, 'libvlc_media_library_media_list'):
        def media_list(self):
            """Get media library subitems.
@return: media list subitems
        """
            e=VLCException()
            return libvlc_media_library_media_list(self, e)

class MediaList(object):

    def __new__(cls, pointer=None):
        '''Internal method used for instanciating wrappers from ctypes.
        '''
        if pointer is None:
            raise Exception("Internal method. Surely this class cannot be instanciated by itself.")
        if pointer == 0:
            return None
        else:
            o=object.__new__(cls)
            o._as_parameter_=ctypes.c_void_p(pointer)
            return o


    @staticmethod
    def from_param(arg):
        '''(INTERNAL) ctypes parameter conversion method.
        '''
        return arg._as_parameter_

    if hasattr(dll, 'libvlc_media_list_release'):
        def release(self):
            """Release media list created with libvlc_media_list_new().
        """
            return libvlc_media_list_release(self)

    if hasattr(dll, 'libvlc_media_list_retain'):
        def retain(self):
            """Retain reference to a media list
        """
            return libvlc_media_list_retain(self)

    if hasattr(dll, 'libvlc_media_list_set_media'):
        def set_media(self, p_mi):
            """Associate media instance with this media list instance.
If another media instance was present it will be released.
The libvlc_media_list_lock should NOT be held upon entering this function.
@param p_mi: media instance to add
        """
            e=VLCException()
            return libvlc_media_list_set_media(self, p_mi, e)

    if hasattr(dll, 'libvlc_media_list_media'):
        def media(self):
            """Get media instance from this media list instance. This action will increase
the refcount on the media instance.
The libvlc_media_list_lock should NOT be held upon entering this function.
@return: media instance
        """
            e=VLCException()
            return libvlc_media_list_media(self, e)

    if hasattr(dll, 'libvlc_media_list_add_media'):
        def add_media(self, p_mi):
            """Add media instance to media list
The libvlc_media_list_lock should be held upon entering this function.
@param p_mi: a media instance
        """
            e=VLCException()
            return libvlc_media_list_add_media(self, p_mi, e)

    if hasattr(dll, 'libvlc_media_list_insert_media'):
        def insert_media(self, p_mi, i_pos):
            """Insert media instance in media list on a position
The libvlc_media_list_lock should be held upon entering this function.
@param p_mi: a media instance
@param i_pos: position in array where to insert
        """
            e=VLCException()
            return libvlc_media_list_insert_media(self, p_mi, i_pos, e)

    if hasattr(dll, 'libvlc_media_list_remove_index'):
        def remove_index(self, i_pos):
            """Remove media instance from media list on a position
The libvlc_media_list_lock should be held upon entering this function.
@param i_pos: position in array where to insert
        """
            e=VLCException()
            return libvlc_media_list_remove_index(self, i_pos, e)

    if hasattr(dll, 'libvlc_media_list_count'):
        def count(self):
            """Get count on media list items
The libvlc_media_list_lock should be held upon entering this function.
@return: number of items in media list
        """
            e=VLCException()
            return libvlc_media_list_count(self, e)

    def __len__(self):
        e=VLCException()
        return libvlc_media_list_count(self, e)

    if hasattr(dll, 'libvlc_media_list_item_at_index'):
        def item_at_index(self, i_pos):
            """List media instance in media list at a position
The libvlc_media_list_lock should be held upon entering this function.
@param i_pos: position in array where to insert
@return: media instance at position i_pos and libvlc_media_retain() has been called to increase the refcount on this object.
        """
            e=VLCException()
            return libvlc_media_list_item_at_index(self, i_pos, e)

    def __getitem__(self, i):
        e=VLCException()
        return libvlc_media_list_item_at_index(self, i, e)

    def __iter__(self):
        e=VLCException()
        for i in xrange(len(self)):
            yield self[i]

    if hasattr(dll, 'libvlc_media_list_index_of_item'):
        def index_of_item(self, p_mi):
            """Find index position of List media instance in media list.
Warning: the function will return the first matched position.
The libvlc_media_list_lock should be held upon entering this function.
@param p_mi: media list instance
@return: position of media instance
        """
            e=VLCException()
            return libvlc_media_list_index_of_item(self, p_mi, e)

    if hasattr(dll, 'libvlc_media_list_is_readonly'):
        def is_readonly(self):
            """This indicates if this media list is read-only from a user point of view
@return: 0 on readonly, 1 on readwrite
        """
            return libvlc_media_list_is_readonly(self)

    if hasattr(dll, 'libvlc_media_list_lock'):
        def lock(self):
            """Get lock on media list items
        """
            return libvlc_media_list_lock(self)

    if hasattr(dll, 'libvlc_media_list_unlock'):
        def unlock(self):
            """Release lock on media list items
The libvlc_media_list_lock should be held upon entering this function.
        """
            return libvlc_media_list_unlock(self)

    if hasattr(dll, 'libvlc_media_list_flat_view'):
        def flat_view(self):
            """Get a flat media list view of media list items
@return: flat media list view instance
        """
            e=VLCException()
            return libvlc_media_list_flat_view(self, e)

    if hasattr(dll, 'libvlc_media_list_hierarchical_view'):
        def hierarchical_view(self):
            """Get a hierarchical media list view of media list items
@return: hierarchical media list view instance
        """
            e=VLCException()
            return libvlc_media_list_hierarchical_view(self, e)

    if hasattr(dll, 'libvlc_media_list_hierarchical_node_view'):
        def hierarchical_node_view(self):
            """
        """
            e=VLCException()
            return libvlc_media_list_hierarchical_node_view(self, e)

    if hasattr(dll, 'libvlc_media_list_event_manager'):
        def event_manager(self):
            """Get libvlc_event_manager from this media list instance.
The p_event_manager is immutable, so you don't have to hold the lock
@return: libvlc_event_manager
        """
            e=VLCException()
            return libvlc_media_list_event_manager(self, e)

class MediaListPlayer(object):
    """Create a new MediaPlayer instance.

    It may take as parameter either:
      - a vlc.Instance
      - nothing
    
    """

    @staticmethod
    def from_param(arg):
        '''(INTERNAL) ctypes parameter conversion method.
        '''
        return arg._as_parameter_


    def __new__(cls, *p):
        if p and p[0] == 0:
            return None
        elif p and isinstance(p[0], (int, long)):
            # instance creation from ctypes
            o=object.__new__(cls)
            o._as_parameter_=ctypes.c_void_p(p[0])
            return o
        elif len(p) == 1 and isinstance(p[0], (tuple, list)):
            p=p[0]

        if p and isinstance(p[0], Instance):
            return p[0].media_list_player_new()
        else:
            i=Instance()
            o=i.media_list_player_new()
            return o

    def get_instance(self):
        """Return the associated vlc.Instance.
        """
        return self._instance


    if hasattr(dll, 'libvlc_media_list_player_release'):
        def release(self):
            """Release media_list_player.
        """
            return libvlc_media_list_player_release(self)

    if hasattr(dll, 'libvlc_media_list_player_set_media_player'):
        def set_media_player(self, p_mi):
            """Replace media player in media_list_player with this instance.
@param p_mi: media player instance
        """
            e=VLCException()
            return libvlc_media_list_player_set_media_player(self, p_mi, e)

    if hasattr(dll, 'libvlc_media_list_player_set_media_list'):
        def set_media_list(self, p_mlist):
            """
        """
            e=VLCException()
            return libvlc_media_list_player_set_media_list(self, p_mlist, e)

    if hasattr(dll, 'libvlc_media_list_player_play'):
        def play(self):
            """Play media list
        """
            e=VLCException()
            return libvlc_media_list_player_play(self, e)

    if hasattr(dll, 'libvlc_media_list_player_pause'):
        def pause(self):
            """Pause media list
        """
            e=VLCException()
            return libvlc_media_list_player_pause(self, e)

    if hasattr(dll, 'libvlc_media_list_player_is_playing'):
        def is_playing(self):
            """Is media list playing?
@return: true for playing and false for not playing
        """
            e=VLCException()
            return libvlc_media_list_player_is_playing(self, e)

    if hasattr(dll, 'libvlc_media_list_player_get_state'):
        def get_state(self):
            """Get current libvlc_state of media list player
@return: libvlc_state_t for media list player
        """
            e=VLCException()
            return libvlc_media_list_player_get_state(self, e)

    if hasattr(dll, 'libvlc_media_list_player_play_item_at_index'):
        def play_item_at_index(self, i_index):
            """Play media list item at position index
@param i_index: index in media list to play
        """
            e=VLCException()
            return libvlc_media_list_player_play_item_at_index(self, i_index, e)

    def __getitem__(self, i):
        e=VLCException()
        return libvlc_media_list_player_play_item_at_index(self, i, e)

    def __iter__(self):
        e=VLCException()
        for i in xrange(len(self)):
            yield self[i]

    if hasattr(dll, 'libvlc_media_list_player_play_item'):
        def play_item(self, p_md):
            """
        """
            e=VLCException()
            return libvlc_media_list_player_play_item(self, p_md, e)

    if hasattr(dll, 'libvlc_media_list_player_stop'):
        def stop(self):
            """Stop playing media list
        """
            e=VLCException()
            return libvlc_media_list_player_stop(self, e)

    if hasattr(dll, 'libvlc_media_list_player_next'):
        def next(self):
            """Play next item from media list
        """
            e=VLCException()
            return libvlc_media_list_player_next(self, e)

class MediaListView(object):

    def __new__(cls, pointer=None):
        '''Internal method used for instanciating wrappers from ctypes.
        '''
        if pointer is None:
            raise Exception("Internal method. Surely this class cannot be instanciated by itself.")
        if pointer == 0:
            return None
        else:
            o=object.__new__(cls)
            o._as_parameter_=ctypes.c_void_p(pointer)
            return o


    @staticmethod
    def from_param(arg):
        '''(INTERNAL) ctypes parameter conversion method.
        '''
        return arg._as_parameter_

    if hasattr(dll, 'libvlc_media_list_view_retain'):
        def retain(self):
            """Retain reference to a media list view
        """
            return libvlc_media_list_view_retain(self)

    if hasattr(dll, 'libvlc_media_list_view_release'):
        def release(self):
            """Release reference to a media list view. If the refcount reaches 0, then
the object will be released.
        """
            return libvlc_media_list_view_release(self)

    if hasattr(dll, 'libvlc_media_list_view_event_manager'):
        def event_manager(self):
            """Get libvlc_event_manager from this media list view instance.
The p_event_manager is immutable, so you don't have to hold the lock
@return: libvlc_event_manager
        """
            return libvlc_media_list_view_event_manager(self)

    if hasattr(dll, 'libvlc_media_list_view_count'):
        def count(self):
            """Get count on media list view items
@return: number of items in media list view
        """
            e=VLCException()
            return libvlc_media_list_view_count(self, e)

    def __len__(self):
        e=VLCException()
        return libvlc_media_list_view_count(self, e)

    if hasattr(dll, 'libvlc_media_list_view_item_at_index'):
        def item_at_index(self, i_index):
            """List media instance in media list view at an index position
@param i_index: index position in array where to insert
@return: media instance at position i_pos and libvlc_media_retain() has been called to increase the refcount on this object.
        """
            e=VLCException()
            return libvlc_media_list_view_item_at_index(self, i_index, e)

    def __getitem__(self, i):
        e=VLCException()
        return libvlc_media_list_view_item_at_index(self, i, e)

    def __iter__(self):
        e=VLCException()
        for i in xrange(len(self)):
            yield self[i]

    if hasattr(dll, 'libvlc_media_list_view_children_at_index'):
        def children_at_index(self, index):
            """
        """
            e=VLCException()
            return libvlc_media_list_view_children_at_index(self, index, e)

    if hasattr(dll, 'libvlc_media_list_view_children_for_item'):
        def children_for_item(self, p_md):
            """
        """
            e=VLCException()
            return libvlc_media_list_view_children_for_item(self, p_md, e)

    if hasattr(dll, 'libvlc_media_list_view_parent_media_list'):
        def parent_media_list(self):
            """
        """
            e=VLCException()
            return libvlc_media_list_view_parent_media_list(self, e)

class MediaPlayer(object):
    """Create a new MediaPlayer instance.

    It may take as parameter either:
      - a string (media URI). In this case, a vlc.Instance will be created.
      - a vlc.Instance
    
    """

    @staticmethod
    def from_param(arg):
        '''(INTERNAL) ctypes parameter conversion method.
        '''
        return arg._as_parameter_


    def __new__(cls, *p):
        if p and p[0] == 0:
            return None
        elif p and isinstance(p[0], (int, long)):
            # instance creation from ctypes
            o=object.__new__(cls)
            o._as_parameter_=ctypes.c_void_p(p[0])
            return o

        if p and isinstance(p[0], Instance):
            return p[0].media_player_new()
        else:
            i=Instance()
            o=i.media_player_new()
            if p:
                o.set_media(i.media_new(p[0]))
            return o

    def get_instance(self):
        """Return the associated vlc.Instance.
        """
        return self._instance


    if hasattr(dll, 'libvlc_media_player_release'):
        def release(self):
            """Release a media_player after use
Decrement the reference count of a media player object. If the
reference count is 0, then libvlc_media_player_release() will
release the media player object. If the media player object
has been released, then it should not be used again.
        """
            return libvlc_media_player_release(self)

    if hasattr(dll, 'libvlc_media_player_retain'):
        def retain(self):
            """Retain a reference to a media player object. Use
libvlc_media_player_release() to decrement reference count.
        """
            return libvlc_media_player_retain(self)

    if hasattr(dll, 'libvlc_media_player_set_media'):
        def set_media(self, p_md):
            """Set the media that will be used by the media_player. If any,
previous md will be released.
@param p_md: the Media. Afterwards the p_md can be safely
        """
            e=VLCException()
            return libvlc_media_player_set_media(self, p_md, e)

    if hasattr(dll, 'libvlc_media_player_get_media'):
        def get_media(self):
            """Get the media used by the media_player.
@return: the media associated with p_mi, or NULL if no
        """
            e=VLCException()
            return libvlc_media_player_get_media(self, e)

    if hasattr(dll, 'libvlc_media_player_event_manager'):
        def event_manager(self):
            """Get the Event Manager from which the media player send event.
@return: the event manager associated with p_mi
        """
            e=VLCException()
            return libvlc_media_player_event_manager(self, e)

    if hasattr(dll, 'libvlc_media_player_is_playing'):
        def is_playing(self):
            """is_playing
@return: 1 if the media player is playing, 0 otherwise
        """
            e=VLCException()
            return libvlc_media_player_is_playing(self, e)

    if hasattr(dll, 'libvlc_media_player_play'):
        def play(self):
            """Play
        """
            e=VLCException()
            return libvlc_media_player_play(self, e)

    if hasattr(dll, 'libvlc_media_player_pause'):
        def pause(self):
            """Pause
        """
            e=VLCException()
            return libvlc_media_player_pause(self, e)

    if hasattr(dll, 'libvlc_media_player_stop'):
        def stop(self):
            """Stop
        """
            e=VLCException()
            return libvlc_media_player_stop(self, e)

    if hasattr(dll, 'libvlc_media_player_set_nsobject'):
        def set_nsobject(self, drawable):
            """Set the agl handler where the media player should render its video output.
@param drawable: the agl handler
        """
            e=VLCException()
            return libvlc_media_player_set_nsobject(self, drawable, e)

    if hasattr(dll, 'libvlc_media_player_get_nsobject'):
        def get_nsobject(self):
            """Get the agl handler previously set with libvlc_media_player_set_agl().
@return: the agl handler or 0 if none where set
        """
            return libvlc_media_player_get_nsobject(self)

    if hasattr(dll, 'libvlc_media_player_set_agl'):
        def set_agl(self, drawable):
            """Set the agl handler where the media player should render its video output.
@param drawable: the agl handler
        """
            e=VLCException()
            return libvlc_media_player_set_agl(self, drawable, e)

    if hasattr(dll, 'libvlc_media_player_get_agl'):
        def get_agl(self):
            """Get the agl handler previously set with libvlc_media_player_set_agl().
@return: the agl handler or 0 if none where set
        """
            return libvlc_media_player_get_agl(self)

    if hasattr(dll, 'libvlc_media_player_set_xwindow'):
        def set_xwindow(self, drawable):
            """Set an X Window System drawable where the media player should render its
video output. If LibVLC was built without X11 output support, then this has
no effects.
The specified identifier must correspond to an existing Input/Output class
X11 window. Pixmaps are <b>not</b> supported. The caller shall ensure that
the X11 server is the same as the one the VLC instance has been configured
with.
If XVideo is <b>not</b> used, it is assumed that the drawable has the
following properties in common with the default X11 screen: depth, scan line
pad, black pixel. This is a bug.
@param drawable: the ID of the X window
        """
            e=VLCException()
            return libvlc_media_player_set_xwindow(self, drawable, e)

    if hasattr(dll, 'libvlc_media_player_get_xwindow'):
        def get_xwindow(self):
            """Get the X Window System window identifier previously set with
libvlc_media_player_set_xwindow(). Note that this will return the identifier
even if VLC is not currently using it (for instance if it is playing an
audio-only input).
@return: an X window ID, or 0 if none where set.
        """
            return libvlc_media_player_get_xwindow(self)

    if hasattr(dll, 'libvlc_media_player_set_hwnd'):
        def set_hwnd(self, drawable):
            """Set a Win32/Win64 API window handle (HWND) where the media player should
render its video output. If LibVLC was built without Win32/Win64 API output
support, then this has no effects.
@param drawable: windows handle of the drawable
        """
            e=VLCException()
            return libvlc_media_player_set_hwnd(self, drawable, e)

    if hasattr(dll, 'libvlc_media_player_get_hwnd'):
        def get_hwnd(self):
            """Get the Windows API window handle (HWND) previously set with
libvlc_media_player_set_hwnd(). The handle will be returned even if LibVLC
is not currently outputting any video to it.
@return: a window handle or NULL if there are none.
        """
            return libvlc_media_player_get_hwnd(self)

    if hasattr(dll, 'libvlc_media_player_get_length'):
        def get_length(self):
            """Get the current movie length (in ms).
@return: the movie length (in ms).
        """
            e=VLCException()
            return libvlc_media_player_get_length(self, e)

    if hasattr(dll, 'libvlc_media_player_get_time'):
        def get_time(self):
            """Get the current movie time (in ms).
@return: the movie time (in ms).
        """
            e=VLCException()
            return libvlc_media_player_get_time(self, e)

    if hasattr(dll, 'libvlc_media_player_set_time'):
        def set_time(self, the):
            """Set the movie time (in ms).
@param the: movie time (in ms).
        """
            e=VLCException()
            return libvlc_media_player_set_time(self, the, e)

    if hasattr(dll, 'libvlc_media_player_get_position'):
        def get_position(self):
            """Get movie position.
@return: movie position
        """
            e=VLCException()
            return libvlc_media_player_get_position(self, e)

    if hasattr(dll, 'libvlc_media_player_set_position'):
        def set_position(self, f_pos):
            """Set movie position.
@param f_pos: the position
        """
            e=VLCException()
            return libvlc_media_player_set_position(self, f_pos, e)

    if hasattr(dll, 'libvlc_media_player_set_chapter'):
        def set_chapter(self, i_chapter):
            """Set movie chapter
@param i_chapter: chapter number to play
        """
            e=VLCException()
            return libvlc_media_player_set_chapter(self, i_chapter, e)

    if hasattr(dll, 'libvlc_media_player_get_chapter'):
        def get_chapter(self):
            """Get movie chapter
@return: chapter number currently playing
        """
            e=VLCException()
            return libvlc_media_player_get_chapter(self, e)

    if hasattr(dll, 'libvlc_media_player_get_chapter_count'):
        def get_chapter_count(self):
            """Get movie chapter count
@return: number of chapters in movie
        """
            e=VLCException()
            return libvlc_media_player_get_chapter_count(self, e)

    if hasattr(dll, 'libvlc_media_player_will_play'):
        def will_play(self):
            """Will the player play
@return: boolean
        """
            e=VLCException()
            return libvlc_media_player_will_play(self, e)

    if hasattr(dll, 'libvlc_media_player_get_chapter_count_for_title'):
        def get_chapter_count_for_title(self, i_title):
            """Get title chapter count
@param i_title: title
@return: number of chapters in title
        """
            e=VLCException()
            return libvlc_media_player_get_chapter_count_for_title(self, i_title, e)

    if hasattr(dll, 'libvlc_media_player_set_title'):
        def set_title(self, i_title):
            """Set movie title
@param i_title: title number to play
        """
            e=VLCException()
            return libvlc_media_player_set_title(self, i_title, e)

    if hasattr(dll, 'libvlc_media_player_get_title'):
        def get_title(self):
            """Get movie title
@return: title number currently playing
        """
            e=VLCException()
            return libvlc_media_player_get_title(self, e)

    if hasattr(dll, 'libvlc_media_player_get_title_count'):
        def get_title_count(self):
            """Get movie title count
@return: title number count
        """
            e=VLCException()
            return libvlc_media_player_get_title_count(self, e)

    if hasattr(dll, 'libvlc_media_player_previous_chapter'):
        def previous_chapter(self):
            """Set previous chapter
        """
            e=VLCException()
            return libvlc_media_player_previous_chapter(self, e)

    if hasattr(dll, 'libvlc_media_player_next_chapter'):
        def next_chapter(self):
            """Set next chapter
        """
            e=VLCException()
            return libvlc_media_player_next_chapter(self, e)

    if hasattr(dll, 'libvlc_media_player_get_rate'):
        def get_rate(self):
            """Get movie play rate
@return: movie play rate
        """
            e=VLCException()
            return libvlc_media_player_get_rate(self, e)

    if hasattr(dll, 'libvlc_media_player_set_rate'):
        def set_rate(self, movie):
            """Set movie play rate
@param movie: play rate to set
        """
            e=VLCException()
            return libvlc_media_player_set_rate(self, movie, e)

    if hasattr(dll, 'libvlc_media_player_get_state'):
        def get_state(self):
            """Get current movie state
@return: current movie state as libvlc_state_t
        """
            e=VLCException()
            return libvlc_media_player_get_state(self, e)

    if hasattr(dll, 'libvlc_media_player_get_fps'):
        def get_fps(self):
            """Get movie fps rate
@return: frames per second (fps) for this playing movie
        """
            e=VLCException()
            return libvlc_media_player_get_fps(self, e)

    if hasattr(dll, 'libvlc_media_player_has_vout'):
        def has_vout(self):
            """Does this media player have a video output?
        """
            e=VLCException()
            return libvlc_media_player_has_vout(self, e)

    if hasattr(dll, 'libvlc_media_player_is_seekable'):
        def is_seekable(self):
            """Is this media player seekable?
        """
            e=VLCException()
            return libvlc_media_player_is_seekable(self, e)

    if hasattr(dll, 'libvlc_media_player_can_pause'):
        def can_pause(self):
            """Can this media player be paused?
        """
            e=VLCException()
            return libvlc_media_player_can_pause(self, e)

    if hasattr(dll, 'libvlc_toggle_fullscreen'):
        def toggle_fullscreen(self):
            """Toggle fullscreen status on video output.
        """
            e=VLCException()
            return libvlc_toggle_fullscreen(self, e)

    if hasattr(dll, 'libvlc_set_fullscreen'):
        def set_fullscreen(self, b_fullscreen):
            """Enable or disable fullscreen on a video output.
@param b_fullscreen: boolean for fullscreen status
        """
            e=VLCException()
            return libvlc_set_fullscreen(self, b_fullscreen, e)

    if hasattr(dll, 'libvlc_get_fullscreen'):
        def get_fullscreen(self):
            """Get current fullscreen status.
@return: the fullscreen status (boolean)
        """
            e=VLCException()
            return libvlc_get_fullscreen(self, e)

    if hasattr(dll, 'libvlc_video_get_height'):
        def video_get_height(self):
            """Get current video height.
@return: the video height
        """
            e=VLCException()
            return libvlc_video_get_height(self, e)

    if hasattr(dll, 'libvlc_video_get_width'):
        def video_get_width(self):
            """Get current video width.
@return: the video width
        """
            e=VLCException()
            return libvlc_video_get_width(self, e)

    if hasattr(dll, 'libvlc_video_get_scale'):
        def video_get_scale(self):
            """Get the current video scaling factor.
See also libvlc_video_set_scale().
@return: the currently configured zoom factor, or 0. if the video is set
        """
            e=VLCException()
            return libvlc_video_get_scale(self, e)

    if hasattr(dll, 'libvlc_video_set_scale'):
        def video_set_scale(self, i_factor):
            """Set the video scaling factor. That is the ratio of the number of pixels on
screen to the number of pixels in the original decoded video in each
dimension. Zero is a special value; it will adjust the video to the output
window/drawable (in windowed mode) or the entire screen.
Note that not all video outputs support scaling.
@param i_factor: the scaling factor, or zero
        """
            e=VLCException()
            return libvlc_video_set_scale(self, i_factor, e)

    if hasattr(dll, 'libvlc_video_get_aspect_ratio'):
        def video_get_aspect_ratio(self):
            """Get current video aspect ratio.
@return: the video aspect ratio
        """
            e=VLCException()
            return libvlc_video_get_aspect_ratio(self, e)

    if hasattr(dll, 'libvlc_video_set_aspect_ratio'):
        def video_set_aspect_ratio(self, psz_aspect):
            """Set new video aspect ratio.
@param psz_aspect: new video aspect-ratio
        """
            e=VLCException()
            return libvlc_video_set_aspect_ratio(self, psz_aspect, e)

    if hasattr(dll, 'libvlc_video_get_spu'):
        def video_get_spu(self):
            """Get current video subtitle.
@return: the video subtitle selected
        """
            e=VLCException()
            return libvlc_video_get_spu(self, e)

    if hasattr(dll, 'libvlc_video_get_spu_count'):
        def video_get_spu_count(self):
            """Get the number of available video subtitles.
@return: the number of available video subtitles
        """
            e=VLCException()
            return libvlc_video_get_spu_count(self, e)

    if hasattr(dll, 'libvlc_video_get_spu_description'):
        def video_get_spu_description(self):
            """Get the description of available video subtitles.
@return: list containing description of available video subtitles
        """
            e=VLCException()
            return libvlc_video_get_spu_description(self, e)

    if hasattr(dll, 'libvlc_video_set_spu'):
        def video_set_spu(self, i_spu):
            """Set new video subtitle.
@param i_spu: new video subtitle to select
        """
            e=VLCException()
            return libvlc_video_set_spu(self, i_spu, e)

    if hasattr(dll, 'libvlc_video_set_subtitle_file'):
        def video_set_subtitle_file(self, psz_subtitle):
            """Set new video subtitle file.
@param psz_subtitle: new video subtitle file
@return: the success status (boolean)
        """
            e=VLCException()
            return libvlc_video_set_subtitle_file(self, psz_subtitle, e)

    if hasattr(dll, 'libvlc_video_get_title_description'):
        def video_get_title_description(self):
            """Get the description of available titles.
@return: list containing description of available titles
        """
            e=VLCException()
            return libvlc_video_get_title_description(self, e)

    if hasattr(dll, 'libvlc_video_get_chapter_description'):
        def video_get_chapter_description(self, i_title):
            """Get the description of available chapters for specific title.
@param i_title: selected title
@return: list containing description of available chapter for title i_title
        """
            e=VLCException()
            return libvlc_video_get_chapter_description(self, i_title, e)

    if hasattr(dll, 'libvlc_video_get_crop_geometry'):
        def video_get_crop_geometry(self):
            """Get current crop filter geometry.
@return: the crop filter geometry
        """
            e=VLCException()
            return libvlc_video_get_crop_geometry(self, e)

    if hasattr(dll, 'libvlc_video_set_crop_geometry'):
        def video_set_crop_geometry(self, psz_geometry):
            """Set new crop filter geometry.
@param psz_geometry: new crop filter geometry
        """
            e=VLCException()
            return libvlc_video_set_crop_geometry(self, psz_geometry, e)

    if hasattr(dll, 'libvlc_toggle_teletext'):
        def toggle_teletext(self):
            """Toggle teletext transparent status on video output.
        """
            e=VLCException()
            return libvlc_toggle_teletext(self, e)

    if hasattr(dll, 'libvlc_video_get_teletext'):
        def video_get_teletext(self):
            """Get current teletext page requested.
@return: the current teletext page requested.
        """
            e=VLCException()
            return libvlc_video_get_teletext(self, e)

    if hasattr(dll, 'libvlc_video_set_teletext'):
        def video_set_teletext(self, i_page):
            """Set new teletext page to retrieve.
@param i_page: teletex page number requested
        """
            e=VLCException()
            return libvlc_video_set_teletext(self, i_page, e)

    if hasattr(dll, 'libvlc_video_get_track_count'):
        def video_get_track_count(self):
            """Get number of available video tracks.
@return: the number of available video tracks (int)
        """
            e=VLCException()
            return libvlc_video_get_track_count(self, e)

    if hasattr(dll, 'libvlc_video_get_track_description'):
        def video_get_track_description(self):
            """Get the description of available video tracks.
@return: list with description of available video tracks
        """
            e=VLCException()
            return libvlc_video_get_track_description(self, e)

    if hasattr(dll, 'libvlc_video_get_track'):
        def video_get_track(self):
            """Get current video track.
@return: the video track (int)
        """
            e=VLCException()
            return libvlc_video_get_track(self, e)

    if hasattr(dll, 'libvlc_video_set_track'):
        def video_set_track(self, i_track):
            """Set video track.
@param i_track: the track (int)
        """
            e=VLCException()
            return libvlc_video_set_track(self, i_track, e)

    if hasattr(dll, 'libvlc_video_take_snapshot'):
        def video_take_snapshot(self, psz_filepath, i_width, i_height):
            """Take a snapshot of the current video window.
If i_width AND i_height is 0, original size is used.
If i_width XOR i_height is 0, original aspect-ratio is preserved.
@param psz_filepath: the path where to save the screenshot to
@param i_width: the snapshot's width
@param i_height: the snapshot's height
        """
            e=VLCException()
            return libvlc_video_take_snapshot(self, psz_filepath, i_width, i_height, e)

    if hasattr(dll, 'libvlc_audio_get_track_count'):
        def audio_get_track_count(self):
            """Get number of available audio tracks.
@return: the number of available audio tracks (int)
        """
            e=VLCException()
            return libvlc_audio_get_track_count(self, e)

    if hasattr(dll, 'libvlc_audio_get_track_description'):
        def audio_get_track_description(self):
            """Get the description of available audio tracks.
@return: list with description of available audio tracks
        """
            e=VLCException()
            return libvlc_audio_get_track_description(self, e)

    if hasattr(dll, 'libvlc_audio_get_track'):
        def audio_get_track(self):
            """Get current audio track.
@return: the audio track (int)
        """
            e=VLCException()
            return libvlc_audio_get_track(self, e)

    if hasattr(dll, 'libvlc_audio_set_track'):
        def audio_set_track(self, i_track):
            """Set current audio track.
@param i_track: the track (int)
        """
            e=VLCException()
            return libvlc_audio_set_track(self, i_track, e)

class TrackDescription(object):

    def __new__(cls, pointer=None):
        '''Internal method used for instanciating wrappers from ctypes.
        '''
        if pointer is None:
            raise Exception("Internal method. Surely this class cannot be instanciated by itself.")
        if pointer == 0:
            return None
        else:
            o=object.__new__(cls)
            o._as_parameter_=ctypes.c_void_p(pointer)
            return o


    @staticmethod
    def from_param(arg):
        '''(INTERNAL) ctypes parameter conversion method.
        '''
        return arg._as_parameter_

    if hasattr(dll, 'libvlc_track_description_release'):
        def release(self):
            """Release (free) libvlc_track_description_t
        """
            return libvlc_track_description_release(self)

if hasattr(dll, 'libvlc_exception_init'):
    prototype=ctypes.CFUNCTYPE(None, ctypes.POINTER(VLCException))
    paramflags=( (3, ), )
    libvlc_exception_init = prototype( ("libvlc_exception_init", dll), paramflags )
    libvlc_exception_init.errcheck = check_vlc_exception
    libvlc_exception_init.__doc__ = """Initialize an exception structure. This can be called several times to
reuse an exception structure.
@param p_exception the exception to initialize
"""

if hasattr(dll, 'libvlc_exception_clear'):
    prototype=ctypes.CFUNCTYPE(None, ctypes.POINTER(VLCException))
    paramflags=( (3, ), )
    libvlc_exception_clear = prototype( ("libvlc_exception_clear", dll), paramflags )
    libvlc_exception_clear.errcheck = check_vlc_exception
    libvlc_exception_clear.__doc__ = """Clear an exception object so it can be reused.
The exception object must have be initialized.
@param p_exception the exception to clear
"""

if hasattr(dll, 'libvlc_new'):
    prototype=ctypes.CFUNCTYPE(Instance, ctypes.c_int, ListPOINTER(ctypes.c_char_p), ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (3,)
    libvlc_new = prototype( ("libvlc_new", dll), paramflags )
    libvlc_new.errcheck = check_vlc_exception
    libvlc_new.__doc__ = """Create and initialize a libvlc instance.
@param argc the number of arguments
@param argv command-line-type arguments. argv[0] must be the path of the
       calling program.
@param p_e an initialized exception pointer
@return the libvlc instance
"""

if hasattr(dll, 'libvlc_get_vlc_id'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, Instance)
    paramflags=( (1, ), )
    libvlc_get_vlc_id = prototype( ("libvlc_get_vlc_id", dll), paramflags )
    libvlc_get_vlc_id.__doc__ = """Return a libvlc instance identifier for legacy APIs. Use of this
function is discouraged, you should convert your program to use the
new API.
@param p_instance the instance
@return the instance identifier
"""

if hasattr(dll, 'libvlc_release'):
    prototype=ctypes.CFUNCTYPE(None, Instance)
    paramflags=( (1, ), )
    libvlc_release = prototype( ("libvlc_release", dll), paramflags )
    libvlc_release.__doc__ = """Decrement the reference count of a libvlc instance, and destroy it
if it reaches zero.
@param p_instance the instance to destroy
"""

if hasattr(dll, 'libvlc_retain'):
    prototype=ctypes.CFUNCTYPE(None, Instance)
    paramflags=( (1, ), )
    libvlc_retain = prototype( ("libvlc_retain", dll), paramflags )
    libvlc_retain.__doc__ = """Increments the reference count of a libvlc instance.
The initial reference count is 1 after libvlc_new() returns.
@param p_instance the instance to reference
"""

if hasattr(dll, 'libvlc_add_intf'):
    prototype=ctypes.CFUNCTYPE(None, Instance, ctypes.c_char_p, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (3,)
    libvlc_add_intf = prototype( ("libvlc_add_intf", dll), paramflags )
    libvlc_add_intf.errcheck = check_vlc_exception
    libvlc_add_intf.__doc__ = """Try to start a user interface for the libvlc instance.
@param p_instance the instance
@param name interface name, or NULL for default
@param p_exception an initialized exception pointer
"""

if hasattr(dll, 'libvlc_wait'):
    prototype=ctypes.CFUNCTYPE(None, Instance)
    paramflags=( (1, ), )
    libvlc_wait = prototype( ("libvlc_wait", dll), paramflags )
    libvlc_wait.__doc__ = """Waits until an interface causes the instance to exit.
You should start at least one interface first, using libvlc_add_intf().
@param p_instance the instance
"""

if hasattr(dll, 'libvlc_get_version'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_char_p)
    paramflags= tuple()
    libvlc_get_version = prototype( ("libvlc_get_version", dll), paramflags )
    libvlc_get_version.__doc__ = """Retrieve libvlc version.
Example: "0.9.0-git Grishenko"
@return a string containing the libvlc version
"""

if hasattr(dll, 'libvlc_get_compiler'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_char_p)
    paramflags= tuple()
    libvlc_get_compiler = prototype( ("libvlc_get_compiler", dll), paramflags )
    libvlc_get_compiler.__doc__ = """Retrieve libvlc compiler version.
Example: "gcc version 4.2.3 (Ubuntu 4.2.3-2ubuntu6)"
@return a string containing the libvlc compiler version
"""

if hasattr(dll, 'libvlc_get_changeset'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_char_p)
    paramflags= tuple()
    libvlc_get_changeset = prototype( ("libvlc_get_changeset", dll), paramflags )
    libvlc_get_changeset.__doc__ = """Retrieve libvlc changeset.
Example: "aa9bce0bc4"
@return a string containing the libvlc changeset
"""

if hasattr(dll, 'libvlc_free'):
    prototype=ctypes.CFUNCTYPE(None, ctypes.c_void_p)
    paramflags=( (1, ), )
    libvlc_free = prototype( ("libvlc_free", dll), paramflags )
    libvlc_free.__doc__ = """Frees an heap allocation (char *) returned by a LibVLC API.
If you know you're using the same underlying C run-time as the LibVLC
implementation, then you can call ANSI C free() directly instead.
"""

if hasattr(dll, 'libvlc_event_attach'):
    prototype=ctypes.CFUNCTYPE(None, EventManager, EventType, ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (1,), (1,), (3,)
    libvlc_event_attach = prototype( ("libvlc_event_attach", dll), paramflags )
    libvlc_event_attach.errcheck = check_vlc_exception
    libvlc_event_attach.__doc__ = """Register for an event notification.
@param p_event_manager the event manager to which you want to attach to.
       Generally it is obtained by vlc_my_object_event_manager() where
       my_object is the object you want to listen to.
@param i_event_type the desired event to which we want to listen
@param f_callback the function to call when i_event_type occurs
@param user_data user provided data to carry with the event
@param p_e an initialized exception pointer
"""

if hasattr(dll, 'libvlc_event_detach'):
    prototype=ctypes.CFUNCTYPE(None, EventManager, EventType, ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (1,), (1,), (3,)
    libvlc_event_detach = prototype( ("libvlc_event_detach", dll), paramflags )
    libvlc_event_detach.errcheck = check_vlc_exception
    libvlc_event_detach.__doc__ = """Unregister an event notification.
@param p_event_manager the event manager
@param i_event_type the desired event to which we want to unregister
@param f_callback the function to call when i_event_type occurs
@param p_user_data user provided data to carry with the event
@param p_e an initialized exception pointer
"""

if hasattr(dll, 'libvlc_event_type_name'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_char_p, EventType)
    paramflags=( (1, ), )
    libvlc_event_type_name = prototype( ("libvlc_event_type_name", dll), paramflags )
    libvlc_event_type_name.__doc__ = """Get an event's type name.
@param i_event_type the desired event
"""

if hasattr(dll, 'libvlc_get_log_verbosity'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_uint, Instance, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_get_log_verbosity = prototype( ("libvlc_get_log_verbosity", dll), paramflags )
    libvlc_get_log_verbosity.errcheck = check_vlc_exception
    libvlc_get_log_verbosity.__doc__ = """Return the VLC messaging verbosity level.
@param p_instance libvlc instance
@param p_e an initialized exception pointer
@return verbosity level for messages
"""

if hasattr(dll, 'libvlc_set_log_verbosity'):
    prototype=ctypes.CFUNCTYPE(None, Instance, ctypes.c_uint, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (3,)
    libvlc_set_log_verbosity = prototype( ("libvlc_set_log_verbosity", dll), paramflags )
    libvlc_set_log_verbosity.errcheck = check_vlc_exception
    libvlc_set_log_verbosity.__doc__ = """Set the VLC messaging verbosity level.
@param p_instance libvlc log instance
@param level log level
@param p_e an initialized exception pointer
"""

if hasattr(dll, 'libvlc_log_open'):
    prototype=ctypes.CFUNCTYPE(Log, Instance, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_log_open = prototype( ("libvlc_log_open", dll), paramflags )
    libvlc_log_open.errcheck = check_vlc_exception
    libvlc_log_open.__doc__ = """Open a VLC message log instance.
@param p_instance libvlc instance
@param p_e an initialized exception pointer
@return log message instance
"""

if hasattr(dll, 'libvlc_log_close'):
    prototype=ctypes.CFUNCTYPE(None, Log, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_log_close = prototype( ("libvlc_log_close", dll), paramflags )
    libvlc_log_close.errcheck = check_vlc_exception
    libvlc_log_close.__doc__ = """Close a VLC message log instance.
@param p_log libvlc log instance
@param p_e an initialized exception pointer
"""

if hasattr(dll, 'libvlc_log_count'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_uint, Log, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_log_count = prototype( ("libvlc_log_count", dll), paramflags )
    libvlc_log_count.errcheck = check_vlc_exception
    libvlc_log_count.__doc__ = """Returns the number of messages in a log instance.
@param p_log libvlc log instance
@param p_e an initialized exception pointer
@return number of log messages
"""

if hasattr(dll, 'libvlc_log_clear'):
    prototype=ctypes.CFUNCTYPE(None, Log, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_log_clear = prototype( ("libvlc_log_clear", dll), paramflags )
    libvlc_log_clear.errcheck = check_vlc_exception
    libvlc_log_clear.__doc__ = """Clear a log instance.
All messages in the log are removed. The log should be cleared on a
regular basis to avoid clogging.
@param p_log libvlc log instance
@param p_e an initialized exception pointer
"""

if hasattr(dll, 'libvlc_log_get_iterator'):
    prototype=ctypes.CFUNCTYPE(LogIterator, Log, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_log_get_iterator = prototype( ("libvlc_log_get_iterator", dll), paramflags )
    libvlc_log_get_iterator.errcheck = check_vlc_exception
    libvlc_log_get_iterator.__doc__ = """Allocate and returns a new iterator to messages in log.
@param p_log libvlc log instance
@param p_e an initialized exception pointer
@return log iterator object
"""

if hasattr(dll, 'libvlc_log_iterator_free'):
    prototype=ctypes.CFUNCTYPE(None, LogIterator, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_log_iterator_free = prototype( ("libvlc_log_iterator_free", dll), paramflags )
    libvlc_log_iterator_free.errcheck = check_vlc_exception
    libvlc_log_iterator_free.__doc__ = """Release a previoulsy allocated iterator.
@param p_iter libvlc log iterator
@param p_e an initialized exception pointer
"""

if hasattr(dll, 'libvlc_log_iterator_has_next'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, LogIterator, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_log_iterator_has_next = prototype( ("libvlc_log_iterator_has_next", dll), paramflags )
    libvlc_log_iterator_has_next.errcheck = check_vlc_exception
    libvlc_log_iterator_has_next.__doc__ = """Return whether log iterator has more messages.
@param p_iter libvlc log iterator
@param p_e an initialized exception pointer
@return true if iterator has more message objects, else false
"""

if hasattr(dll, 'libvlc_log_iterator_next'):
    prototype=ctypes.CFUNCTYPE(ctypes.POINTER(LogMessage), LogIterator, ctypes.POINTER(LogMessage), ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (3,)
    libvlc_log_iterator_next = prototype( ("libvlc_log_iterator_next", dll), paramflags )
    libvlc_log_iterator_next.errcheck = check_vlc_exception
    libvlc_log_iterator_next.__doc__ = """Return the next log message.
The message contents must not be freed
@param p_iter libvlc log iterator
@param p_buffer log buffer
@param p_e an initialized exception pointer
@return log message object
"""

if hasattr(dll, 'libvlc_media_new'):
    prototype=ctypes.CFUNCTYPE(Media, Instance, ctypes.c_char_p, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (3,)
    libvlc_media_new = prototype( ("libvlc_media_new", dll), paramflags )
    libvlc_media_new.errcheck = check_vlc_exception
    libvlc_media_new.__doc__ = """Create a media with the given MRL.
@param p_instance the instance
@param psz_mrl the MRL to read
@param p_e an initialized exception pointer
@return the newly created media
"""

if hasattr(dll, 'libvlc_media_new_as_node'):
    prototype=ctypes.CFUNCTYPE(Media, Instance, ctypes.c_char_p, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (3,)
    libvlc_media_new_as_node = prototype( ("libvlc_media_new_as_node", dll), paramflags )
    libvlc_media_new_as_node.errcheck = check_vlc_exception
    libvlc_media_new_as_node.__doc__ = """Create a media as an empty node with the passed name.
@param p_instance the instance
@param psz_name the name of the node
@param p_e an initialized exception pointer
@return the new empty media
"""

if hasattr(dll, 'libvlc_media_add_option'):
    prototype=ctypes.CFUNCTYPE(None, Media, ctypes.c_char_p, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (3,)
    libvlc_media_add_option = prototype( ("libvlc_media_add_option", dll), paramflags )
    libvlc_media_add_option.errcheck = check_vlc_exception
    libvlc_media_add_option.__doc__ = """Add an option to the media.
This option will be used to determine how the media_player will
read the media. This allows to use VLC's advanced
reading/streaming options on a per-media basis.
The options are detailed in vlc --long-help, for instance "--sout-all"
@param p_instance the instance
@param ppsz_options the options (as a string)
@param p_e an initialized exception pointer
"""

if hasattr(dll, 'libvlc_media_add_option_untrusted'):
    prototype=ctypes.CFUNCTYPE(None, Media, ctypes.c_char_p, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (3,)
    libvlc_media_add_option_untrusted = prototype( ("libvlc_media_add_option_untrusted", dll), paramflags )
    libvlc_media_add_option_untrusted.errcheck = check_vlc_exception
    libvlc_media_add_option_untrusted.__doc__ = """Add an option to the media from an untrusted source.
This option will be used to determine how the media_player will
read the media. This allows to use VLC's advanced
reading/streaming options on a per-media basis.
The options are detailed in vlc --long-help, for instance "--sout-all"
@param p_instance the instance
@param ppsz_options the options (as a string)
@param p_e an initialized exception pointer
"""

if hasattr(dll, 'libvlc_media_retain'):
    prototype=ctypes.CFUNCTYPE(None, Media)
    paramflags=( (1, ), )
    libvlc_media_retain = prototype( ("libvlc_media_retain", dll), paramflags )
    libvlc_media_retain.__doc__ = """Retain a reference to a media descriptor object (libvlc_media_t). Use
libvlc_media_release() to decrement the reference count of a
media descriptor object.
@param p_meta_desc a media descriptor object.
"""

if hasattr(dll, 'libvlc_media_release'):
    prototype=ctypes.CFUNCTYPE(None, Media)
    paramflags=( (1, ), )
    libvlc_media_release = prototype( ("libvlc_media_release", dll), paramflags )
    libvlc_media_release.__doc__ = """Decrement the reference count of a media descriptor object. If the
reference count is 0, then libvlc_media_release() will release the
media descriptor object. It will send out an libvlc_MediaFreed event
to all listeners. If the media descriptor object has been released it
should not be used again.
@param p_meta_desc a media descriptor object.
"""

if hasattr(dll, 'libvlc_media_get_mrl'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_char_p, Media, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_media_get_mrl = prototype( ("libvlc_media_get_mrl", dll), paramflags )
    libvlc_media_get_mrl.errcheck = check_vlc_exception
    libvlc_media_get_mrl.__doc__ = """Get the media resource locator (mrl) from a media descriptor object
@param p_md a media descriptor object
@param p_e an initialized exception object
@return string with mrl of media descriptor object
"""

if hasattr(dll, 'libvlc_media_duplicate'):
    prototype=ctypes.CFUNCTYPE(Media, Media)
    paramflags=( (1, ), )
    libvlc_media_duplicate = prototype( ("libvlc_media_duplicate", dll), paramflags )
    libvlc_media_duplicate.__doc__ = """Duplicate a media descriptor object.
@param p_meta_desc a media descriptor object.
"""

if hasattr(dll, 'libvlc_media_get_meta'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_char_p, Media, Meta, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (3,)
    libvlc_media_get_meta = prototype( ("libvlc_media_get_meta", dll), paramflags )
    libvlc_media_get_meta.errcheck = check_vlc_exception
    libvlc_media_get_meta.__doc__ = """Read the meta of the media.
@param p_meta_desc the media to read
@param e_meta the meta to read
@param p_e an initialized exception pointer
@return the media's meta
"""

if hasattr(dll, 'libvlc_media_get_state'):
    prototype=ctypes.CFUNCTYPE(State, Media, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_media_get_state = prototype( ("libvlc_media_get_state", dll), paramflags )
    libvlc_media_get_state.errcheck = check_vlc_exception
    libvlc_media_get_state.__doc__ = """Get current state of media descriptor object. Possible media states
are defined in libvlc_structures.c ( libvlc_NothingSpecial=0,
libvlc_Opening, libvlc_Buffering, libvlc_Playing, libvlc_Paused,
libvlc_Stopped, libvlc_Ended,
libvlc_Error).
@see libvlc_state_t
@param p_meta_desc a media descriptor object
@param p_e an initialized exception object
@return state of media descriptor object
"""

if hasattr(dll, 'libvlc_media_subitems'):
    prototype=ctypes.CFUNCTYPE(MediaList, Media, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_media_subitems = prototype( ("libvlc_media_subitems", dll), paramflags )
    libvlc_media_subitems.errcheck = check_vlc_exception
    libvlc_media_subitems.__doc__ = """Get subitems of media descriptor object. This will increment
the reference count of supplied media descriptor object. Use
libvlc_media_list_release() to decrement the reference counting.
@param p_md media descriptor object
@param p_e initalized exception object
@return list of media descriptor subitems or NULL
and this is here for convenience */
"""

if hasattr(dll, 'libvlc_media_event_manager'):
    prototype=ctypes.CFUNCTYPE(EventManager, Media, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_media_event_manager = prototype( ("libvlc_media_event_manager", dll), paramflags )
    libvlc_media_event_manager.errcheck = check_vlc_exception
    libvlc_media_event_manager.__doc__ = """Get event manager from media descriptor object.
NOTE: this function doesn't increment reference counting.
@param p_md a media descriptor object
@param p_e an initialized exception object
@return event manager object
"""

if hasattr(dll, 'libvlc_media_get_duration'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_longlong, Media, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_media_get_duration = prototype( ("libvlc_media_get_duration", dll), paramflags )
    libvlc_media_get_duration.errcheck = check_vlc_exception
    libvlc_media_get_duration.__doc__ = """Get duration of media descriptor object item.
@param p_md media descriptor object
@param p_e an initialized exception object
@return duration of media item
"""

if hasattr(dll, 'libvlc_media_is_preparsed'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, Media, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_media_is_preparsed = prototype( ("libvlc_media_is_preparsed", dll), paramflags )
    libvlc_media_is_preparsed.errcheck = check_vlc_exception
    libvlc_media_is_preparsed.__doc__ = """Get preparsed status for media descriptor object.
@param p_md media descriptor object
@param p_e an initialized exception object
@return true if media object has been preparsed otherwise it returns false
"""

if hasattr(dll, 'libvlc_media_set_user_data'):
    prototype=ctypes.CFUNCTYPE(None, Media, ctypes.c_void_p, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (3,)
    libvlc_media_set_user_data = prototype( ("libvlc_media_set_user_data", dll), paramflags )
    libvlc_media_set_user_data.errcheck = check_vlc_exception
    libvlc_media_set_user_data.__doc__ = """Sets media descriptor's user_data. user_data is specialized data
accessed by the host application, VLC.framework uses it as a pointer to
an native object that references a libvlc_media_t pointer
@param p_md media descriptor object
@param p_new_user_data pointer to user data
@param p_e an initialized exception object
"""

if hasattr(dll, 'libvlc_media_get_user_data'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_void_p, Media, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_media_get_user_data = prototype( ("libvlc_media_get_user_data", dll), paramflags )
    libvlc_media_get_user_data.errcheck = check_vlc_exception
    libvlc_media_get_user_data.__doc__ = """Get media descriptor's user_data. user_data is specialized data
accessed by the host application, VLC.framework uses it as a pointer to
an native object that references a libvlc_media_t pointer
@param p_md media descriptor object
@param p_e an initialized exception object
"""

if hasattr(dll, 'libvlc_media_discoverer_new_from_name'):
    prototype=ctypes.CFUNCTYPE(MediaDiscoverer, Instance, ctypes.c_char_p, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (3,)
    libvlc_media_discoverer_new_from_name = prototype( ("libvlc_media_discoverer_new_from_name", dll), paramflags )
    libvlc_media_discoverer_new_from_name.errcheck = check_vlc_exception
    libvlc_media_discoverer_new_from_name.__doc__ = """Discover media service by name.
@param p_inst libvlc instance
@param psz_name service name
@param p_e an initialized exception object
@return media discover object
"""

if hasattr(dll, 'libvlc_media_discoverer_release'):
    prototype=ctypes.CFUNCTYPE(None, MediaDiscoverer)
    paramflags=( (1, ), )
    libvlc_media_discoverer_release = prototype( ("libvlc_media_discoverer_release", dll), paramflags )
    libvlc_media_discoverer_release.__doc__ = """Release media discover object. If the reference count reaches 0, then
the object will be released.
@param p_mdis media service discover object
"""

if hasattr(dll, 'libvlc_media_discoverer_localized_name'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_char_p, MediaDiscoverer)
    paramflags=( (1, ), )
    libvlc_media_discoverer_localized_name = prototype( ("libvlc_media_discoverer_localized_name", dll), paramflags )
    libvlc_media_discoverer_localized_name.__doc__ = """Get media service discover object its localized name.
@param media discover object
@return localized name
"""

if hasattr(dll, 'libvlc_media_discoverer_media_list'):
    prototype=ctypes.CFUNCTYPE(MediaList, MediaDiscoverer)
    paramflags=( (1, ), )
    libvlc_media_discoverer_media_list = prototype( ("libvlc_media_discoverer_media_list", dll), paramflags )
    libvlc_media_discoverer_media_list.__doc__ = """Get media service discover media list.
@param p_mdis media service discover object
@return list of media items
"""

if hasattr(dll, 'libvlc_media_discoverer_event_manager'):
    prototype=ctypes.CFUNCTYPE(EventManager, MediaDiscoverer)
    paramflags=( (1, ), )
    libvlc_media_discoverer_event_manager = prototype( ("libvlc_media_discoverer_event_manager", dll), paramflags )
    libvlc_media_discoverer_event_manager.__doc__ = """Get event manager from media service discover object.
@param p_mdis media service discover object
@return event manager object.
"""

if hasattr(dll, 'libvlc_media_discoverer_is_running'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaDiscoverer)
    paramflags=( (1, ), )
    libvlc_media_discoverer_is_running = prototype( ("libvlc_media_discoverer_is_running", dll), paramflags )
    libvlc_media_discoverer_is_running.__doc__ = """Query if media service discover object is running.
@param p_mdis media service discover object
@return true if running, false if not
"""

if hasattr(dll, 'libvlc_media_library_new'):
    prototype=ctypes.CFUNCTYPE(MediaLibrary, Instance, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_media_library_new = prototype( ("libvlc_media_library_new", dll), paramflags )
    libvlc_media_library_new.errcheck = check_vlc_exception
    libvlc_media_library_new.__doc__ = """\ingroup libvlc
LibVLC Media Library
@{
"""

if hasattr(dll, 'libvlc_media_library_release'):
    prototype=ctypes.CFUNCTYPE(None, MediaLibrary)
    paramflags=( (1, ), )
    libvlc_media_library_release = prototype( ("libvlc_media_library_release", dll), paramflags )
    libvlc_media_library_release.__doc__ = """Release media library object. This functions decrements the
reference count of the media library object. If it reaches 0,
then the object will be released.
@param p_mlib media library object
"""

if hasattr(dll, 'libvlc_media_library_retain'):
    prototype=ctypes.CFUNCTYPE(None, MediaLibrary)
    paramflags=( (1, ), )
    libvlc_media_library_retain = prototype( ("libvlc_media_library_retain", dll), paramflags )
    libvlc_media_library_retain.__doc__ = """Retain a reference to a media library object. This function will
increment the reference counting for this object. Use
libvlc_media_library_release() to decrement the reference count.
@param p_mlib media library object
"""

if hasattr(dll, 'libvlc_media_library_load'):
    prototype=ctypes.CFUNCTYPE(None, MediaLibrary, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_media_library_load = prototype( ("libvlc_media_library_load", dll), paramflags )
    libvlc_media_library_load.errcheck = check_vlc_exception
    libvlc_media_library_load.__doc__ = """Load media library.
@param p_mlib media library object
@param p_e an initialized exception object.
"""

if hasattr(dll, 'libvlc_media_library_save'):
    prototype=ctypes.CFUNCTYPE(None, MediaLibrary, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_media_library_save = prototype( ("libvlc_media_library_save", dll), paramflags )
    libvlc_media_library_save.errcheck = check_vlc_exception
    libvlc_media_library_save.__doc__ = """Save media library.
@param p_mlib media library object
@param p_e an initialized exception object.
"""

if hasattr(dll, 'libvlc_media_library_media_list'):
    prototype=ctypes.CFUNCTYPE(MediaList, MediaLibrary, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_media_library_media_list = prototype( ("libvlc_media_library_media_list", dll), paramflags )
    libvlc_media_library_media_list.errcheck = check_vlc_exception
    libvlc_media_library_media_list.__doc__ = """Get media library subitems.
@param p_mlib media library object
@param p_e an initialized exception object.
@return media list subitems
"""

if hasattr(dll, 'libvlc_media_list_new'):
    prototype=ctypes.CFUNCTYPE(MediaList, Instance, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_media_list_new = prototype( ("libvlc_media_list_new", dll), paramflags )
    libvlc_media_list_new.errcheck = check_vlc_exception
    libvlc_media_list_new.__doc__ = """Create an empty media list.
@param p_libvlc libvlc instance
@param p_e an initialized exception pointer
@return empty media list
"""

if hasattr(dll, 'libvlc_media_list_release'):
    prototype=ctypes.CFUNCTYPE(None, MediaList)
    paramflags=( (1, ), )
    libvlc_media_list_release = prototype( ("libvlc_media_list_release", dll), paramflags )
    libvlc_media_list_release.__doc__ = """Release media list created with libvlc_media_list_new().
@param p_ml a media list created with libvlc_media_list_new()
"""

if hasattr(dll, 'libvlc_media_list_retain'):
    prototype=ctypes.CFUNCTYPE(None, MediaList)
    paramflags=( (1, ), )
    libvlc_media_list_retain = prototype( ("libvlc_media_list_retain", dll), paramflags )
    libvlc_media_list_retain.__doc__ = """Retain reference to a media list
@param p_ml a media list created with libvlc_media_list_new()
"""

if hasattr(dll, 'libvlc_media_list_set_media'):
    prototype=ctypes.CFUNCTYPE(None, MediaList, Media, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (3,)
    libvlc_media_list_set_media = prototype( ("libvlc_media_list_set_media", dll), paramflags )
    libvlc_media_list_set_media.errcheck = check_vlc_exception
    libvlc_media_list_set_media.__doc__ = """Associate media instance with this media list instance.
If another media instance was present it will be released.
The libvlc_media_list_lock should NOT be held upon entering this function.
@param p_ml a media list instance
@param p_mi media instance to add
@param p_e initialized exception object
"""

if hasattr(dll, 'libvlc_media_list_media'):
    prototype=ctypes.CFUNCTYPE(Media, MediaList, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_media_list_media = prototype( ("libvlc_media_list_media", dll), paramflags )
    libvlc_media_list_media.errcheck = check_vlc_exception
    libvlc_media_list_media.__doc__ = """Get media instance from this media list instance. This action will increase
the refcount on the media instance.
The libvlc_media_list_lock should NOT be held upon entering this function.
@param p_ml a media list instance
@param p_e initialized exception object
@return media instance
"""

if hasattr(dll, 'libvlc_media_list_add_media'):
    prototype=ctypes.CFUNCTYPE(None, MediaList, Media, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (3,)
    libvlc_media_list_add_media = prototype( ("libvlc_media_list_add_media", dll), paramflags )
    libvlc_media_list_add_media.errcheck = check_vlc_exception
    libvlc_media_list_add_media.__doc__ = """Add media instance to media list
The libvlc_media_list_lock should be held upon entering this function.
@param p_ml a media list instance
@param p_mi a media instance
@param p_e initialized exception object
"""

if hasattr(dll, 'libvlc_media_list_insert_media'):
    prototype=ctypes.CFUNCTYPE(None, MediaList, Media, ctypes.c_int, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (1,), (3,)
    libvlc_media_list_insert_media = prototype( ("libvlc_media_list_insert_media", dll), paramflags )
    libvlc_media_list_insert_media.errcheck = check_vlc_exception
    libvlc_media_list_insert_media.__doc__ = """Insert media instance in media list on a position
The libvlc_media_list_lock should be held upon entering this function.
@param p_ml a media list instance
@param p_mi a media instance
@param i_pos position in array where to insert
@param p_e initialized exception object
"""

if hasattr(dll, 'libvlc_media_list_remove_index'):
    prototype=ctypes.CFUNCTYPE(None, MediaList, ctypes.c_int, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (3,)
    libvlc_media_list_remove_index = prototype( ("libvlc_media_list_remove_index", dll), paramflags )
    libvlc_media_list_remove_index.errcheck = check_vlc_exception
    libvlc_media_list_remove_index.__doc__ = """Remove media instance from media list on a position
The libvlc_media_list_lock should be held upon entering this function.
@param p_ml a media list instance
@param i_pos position in array where to insert
@param p_e initialized exception object
"""

if hasattr(dll, 'libvlc_media_list_count'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaList, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_media_list_count = prototype( ("libvlc_media_list_count", dll), paramflags )
    libvlc_media_list_count.errcheck = check_vlc_exception
    libvlc_media_list_count.__doc__ = """Get count on media list items
The libvlc_media_list_lock should be held upon entering this function.
@param p_ml a media list instance
@param p_e initialized exception object
@return number of items in media list
"""

if hasattr(dll, 'libvlc_media_list_item_at_index'):
    prototype=ctypes.CFUNCTYPE(Media, MediaList, ctypes.c_int, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (3,)
    libvlc_media_list_item_at_index = prototype( ("libvlc_media_list_item_at_index", dll), paramflags )
    libvlc_media_list_item_at_index.errcheck = check_vlc_exception
    libvlc_media_list_item_at_index.__doc__ = """List media instance in media list at a position
The libvlc_media_list_lock should be held upon entering this function.
@param p_ml a media list instance
@param i_pos position in array where to insert
@param p_e initialized exception object
@return media instance at position i_pos and libvlc_media_retain() has been called to increase the refcount on this object.
"""

if hasattr(dll, 'libvlc_media_list_index_of_item'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaList, Media, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (3,)
    libvlc_media_list_index_of_item = prototype( ("libvlc_media_list_index_of_item", dll), paramflags )
    libvlc_media_list_index_of_item.errcheck = check_vlc_exception
    libvlc_media_list_index_of_item.__doc__ = """Find index position of List media instance in media list.
Warning: the function will return the first matched position.
The libvlc_media_list_lock should be held upon entering this function.
@param p_ml a media list instance
@param p_mi media list instance
@param p_e initialized exception object
@return position of media instance
"""

if hasattr(dll, 'libvlc_media_list_is_readonly'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaList)
    paramflags=( (1, ), )
    libvlc_media_list_is_readonly = prototype( ("libvlc_media_list_is_readonly", dll), paramflags )
    libvlc_media_list_is_readonly.__doc__ = """This indicates if this media list is read-only from a user point of view
@param p_ml media list instance
@return 0 on readonly, 1 on readwrite
"""

if hasattr(dll, 'libvlc_media_list_lock'):
    prototype=ctypes.CFUNCTYPE(None, MediaList)
    paramflags=( (1, ), )
    libvlc_media_list_lock = prototype( ("libvlc_media_list_lock", dll), paramflags )
    libvlc_media_list_lock.__doc__ = """Get lock on media list items
@param p_ml a media list instance
"""

if hasattr(dll, 'libvlc_media_list_unlock'):
    prototype=ctypes.CFUNCTYPE(None, MediaList)
    paramflags=( (1, ), )
    libvlc_media_list_unlock = prototype( ("libvlc_media_list_unlock", dll), paramflags )
    libvlc_media_list_unlock.__doc__ = """Release lock on media list items
The libvlc_media_list_lock should be held upon entering this function.
@param p_ml a media list instance
"""

if hasattr(dll, 'libvlc_media_list_flat_view'):
    prototype=ctypes.CFUNCTYPE(MediaListView, MediaList, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_media_list_flat_view = prototype( ("libvlc_media_list_flat_view", dll), paramflags )
    libvlc_media_list_flat_view.errcheck = check_vlc_exception
    libvlc_media_list_flat_view.__doc__ = """Get a flat media list view of media list items
@param p_ml a media list instance
@param p_ex an excpetion instance
@return flat media list view instance
"""

if hasattr(dll, 'libvlc_media_list_hierarchical_view'):
    prototype=ctypes.CFUNCTYPE(MediaListView, MediaList, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_media_list_hierarchical_view = prototype( ("libvlc_media_list_hierarchical_view", dll), paramflags )
    libvlc_media_list_hierarchical_view.errcheck = check_vlc_exception
    libvlc_media_list_hierarchical_view.__doc__ = """Get a hierarchical media list view of media list items
@param p_ml a media list instance
@param p_ex an excpetion instance
@return hierarchical media list view instance
"""

if hasattr(dll, 'libvlc_media_list_hierarchical_node_view'):
    prototype=ctypes.CFUNCTYPE(MediaListView, MediaList, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_media_list_hierarchical_node_view = prototype( ("libvlc_media_list_hierarchical_node_view", dll), paramflags )
    libvlc_media_list_hierarchical_node_view.errcheck = check_vlc_exception
    libvlc_media_list_hierarchical_node_view.__doc__ = """"""

if hasattr(dll, 'libvlc_media_list_event_manager'):
    prototype=ctypes.CFUNCTYPE(EventManager, MediaList, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_media_list_event_manager = prototype( ("libvlc_media_list_event_manager", dll), paramflags )
    libvlc_media_list_event_manager.errcheck = check_vlc_exception
    libvlc_media_list_event_manager.__doc__ = """Get libvlc_event_manager from this media list instance.
The p_event_manager is immutable, so you don't have to hold the lock
@param p_ml a media list instance
@param p_ex an excpetion instance
@return libvlc_event_manager
"""

if hasattr(dll, 'libvlc_media_list_player_new'):
    prototype=ctypes.CFUNCTYPE(MediaListPlayer, Instance, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_media_list_player_new = prototype( ("libvlc_media_list_player_new", dll), paramflags )
    libvlc_media_list_player_new.errcheck = check_vlc_exception
    libvlc_media_list_player_new.__doc__ = """Create new media_list_player.
@param p_instance libvlc instance
@param p_e initialized exception instance
@return media list player instance
"""

if hasattr(dll, 'libvlc_media_list_player_release'):
    prototype=ctypes.CFUNCTYPE(None, MediaListPlayer)
    paramflags=( (1, ), )
    libvlc_media_list_player_release = prototype( ("libvlc_media_list_player_release", dll), paramflags )
    libvlc_media_list_player_release.__doc__ = """Release media_list_player.
@param p_mlp media list player instance
"""

if hasattr(dll, 'libvlc_media_list_player_set_media_player'):
    prototype=ctypes.CFUNCTYPE(None, MediaListPlayer, MediaPlayer, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (3,)
    libvlc_media_list_player_set_media_player = prototype( ("libvlc_media_list_player_set_media_player", dll), paramflags )
    libvlc_media_list_player_set_media_player.errcheck = check_vlc_exception
    libvlc_media_list_player_set_media_player.__doc__ = """Replace media player in media_list_player with this instance.
@param p_mlp media list player instance
@param p_mi media player instance
@param p_e initialized exception instance
"""

if hasattr(dll, 'libvlc_media_list_player_set_media_list'):
    prototype=ctypes.CFUNCTYPE(None, MediaListPlayer, MediaList, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (3,)
    libvlc_media_list_player_set_media_list = prototype( ("libvlc_media_list_player_set_media_list", dll), paramflags )
    libvlc_media_list_player_set_media_list.errcheck = check_vlc_exception
    libvlc_media_list_player_set_media_list.__doc__ = """"""

if hasattr(dll, 'libvlc_media_list_player_play'):
    prototype=ctypes.CFUNCTYPE(None, MediaListPlayer, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_media_list_player_play = prototype( ("libvlc_media_list_player_play", dll), paramflags )
    libvlc_media_list_player_play.errcheck = check_vlc_exception
    libvlc_media_list_player_play.__doc__ = """Play media list
@param p_mlp media list player instance
@param p_e initialized exception instance
"""

if hasattr(dll, 'libvlc_media_list_player_pause'):
    prototype=ctypes.CFUNCTYPE(None, MediaListPlayer, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_media_list_player_pause = prototype( ("libvlc_media_list_player_pause", dll), paramflags )
    libvlc_media_list_player_pause.errcheck = check_vlc_exception
    libvlc_media_list_player_pause.__doc__ = """Pause media list
@param p_mlp media list player instance
@param p_e initialized exception instance
"""

if hasattr(dll, 'libvlc_media_list_player_is_playing'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaListPlayer, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_media_list_player_is_playing = prototype( ("libvlc_media_list_player_is_playing", dll), paramflags )
    libvlc_media_list_player_is_playing.errcheck = check_vlc_exception
    libvlc_media_list_player_is_playing.__doc__ = """Is media list playing?
@param p_mlp media list player instance
@param p_e initialized exception instance
@return true for playing and false for not playing
"""

if hasattr(dll, 'libvlc_media_list_player_get_state'):
    prototype=ctypes.CFUNCTYPE(State, MediaListPlayer, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_media_list_player_get_state = prototype( ("libvlc_media_list_player_get_state", dll), paramflags )
    libvlc_media_list_player_get_state.errcheck = check_vlc_exception
    libvlc_media_list_player_get_state.__doc__ = """Get current libvlc_state of media list player
@param p_mlp media list player instance
@param p_e initialized exception instance
@return libvlc_state_t for media list player
"""

if hasattr(dll, 'libvlc_media_list_player_play_item_at_index'):
    prototype=ctypes.CFUNCTYPE(None, MediaListPlayer, ctypes.c_int, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (3,)
    libvlc_media_list_player_play_item_at_index = prototype( ("libvlc_media_list_player_play_item_at_index", dll), paramflags )
    libvlc_media_list_player_play_item_at_index.errcheck = check_vlc_exception
    libvlc_media_list_player_play_item_at_index.__doc__ = """Play media list item at position index
@param p_mlp media list player instance
@param i_index index in media list to play
@param p_e initialized exception instance
"""

if hasattr(dll, 'libvlc_media_list_player_play_item'):
    prototype=ctypes.CFUNCTYPE(None, MediaListPlayer, Media, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (3,)
    libvlc_media_list_player_play_item = prototype( ("libvlc_media_list_player_play_item", dll), paramflags )
    libvlc_media_list_player_play_item.errcheck = check_vlc_exception
    libvlc_media_list_player_play_item.__doc__ = """"""

if hasattr(dll, 'libvlc_media_list_player_stop'):
    prototype=ctypes.CFUNCTYPE(None, MediaListPlayer, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_media_list_player_stop = prototype( ("libvlc_media_list_player_stop", dll), paramflags )
    libvlc_media_list_player_stop.errcheck = check_vlc_exception
    libvlc_media_list_player_stop.__doc__ = """Stop playing media list
@param p_mlp media list player instance
@param p_e initialized exception instance
"""

if hasattr(dll, 'libvlc_media_list_player_next'):
    prototype=ctypes.CFUNCTYPE(None, MediaListPlayer, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_media_list_player_next = prototype( ("libvlc_media_list_player_next", dll), paramflags )
    libvlc_media_list_player_next.errcheck = check_vlc_exception
    libvlc_media_list_player_next.__doc__ = """Play next item from media list
@param p_mlp media list player instance
@param p_e initialized exception instance
"""

if hasattr(dll, 'libvlc_media_list_view_retain'):
    prototype=ctypes.CFUNCTYPE(None, MediaListView)
    paramflags=( (1, ), )
    libvlc_media_list_view_retain = prototype( ("libvlc_media_list_view_retain", dll), paramflags )
    libvlc_media_list_view_retain.__doc__ = """Retain reference to a media list view
@param p_mlv a media list view created with libvlc_media_list_view_new()
"""

if hasattr(dll, 'libvlc_media_list_view_release'):
    prototype=ctypes.CFUNCTYPE(None, MediaListView)
    paramflags=( (1, ), )
    libvlc_media_list_view_release = prototype( ("libvlc_media_list_view_release", dll), paramflags )
    libvlc_media_list_view_release.__doc__ = """Release reference to a media list view. If the refcount reaches 0, then
the object will be released.
@param p_mlv a media list view created with libvlc_media_list_view_new()
"""

if hasattr(dll, 'libvlc_media_list_view_event_manager'):
    prototype=ctypes.CFUNCTYPE(EventManager, MediaListView)
    paramflags=( (1, ), )
    libvlc_media_list_view_event_manager = prototype( ("libvlc_media_list_view_event_manager", dll), paramflags )
    libvlc_media_list_view_event_manager.__doc__ = """Get libvlc_event_manager from this media list view instance.
The p_event_manager is immutable, so you don't have to hold the lock
@param p_mlv a media list view instance
@return libvlc_event_manager
"""

if hasattr(dll, 'libvlc_media_list_view_count'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaListView, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_media_list_view_count = prototype( ("libvlc_media_list_view_count", dll), paramflags )
    libvlc_media_list_view_count.errcheck = check_vlc_exception
    libvlc_media_list_view_count.__doc__ = """Get count on media list view items
@param p_mlv a media list view instance
@param p_e initialized exception object
@return number of items in media list view
"""

if hasattr(dll, 'libvlc_media_list_view_item_at_index'):
    prototype=ctypes.CFUNCTYPE(Media, MediaListView, ctypes.c_int, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (3,)
    libvlc_media_list_view_item_at_index = prototype( ("libvlc_media_list_view_item_at_index", dll), paramflags )
    libvlc_media_list_view_item_at_index.errcheck = check_vlc_exception
    libvlc_media_list_view_item_at_index.__doc__ = """List media instance in media list view at an index position
@param p_mlv a media list view instance
@param i_index index position in array where to insert
@param p_e initialized exception object
@return media instance at position i_pos and libvlc_media_retain() has been called to increase the refcount on this object.
"""

if hasattr(dll, 'libvlc_media_list_view_children_at_index'):
    prototype=ctypes.CFUNCTYPE(MediaListView, MediaListView, ctypes.c_int, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (3,)
    libvlc_media_list_view_children_at_index = prototype( ("libvlc_media_list_view_children_at_index", dll), paramflags )
    libvlc_media_list_view_children_at_index.errcheck = check_vlc_exception
    libvlc_media_list_view_children_at_index.__doc__ = """"""

if hasattr(dll, 'libvlc_media_list_view_children_for_item'):
    prototype=ctypes.CFUNCTYPE(MediaListView, MediaListView, Media, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (3,)
    libvlc_media_list_view_children_for_item = prototype( ("libvlc_media_list_view_children_for_item", dll), paramflags )
    libvlc_media_list_view_children_for_item.errcheck = check_vlc_exception
    libvlc_media_list_view_children_for_item.__doc__ = """"""

if hasattr(dll, 'libvlc_media_list_view_parent_media_list'):
    prototype=ctypes.CFUNCTYPE(MediaList, MediaListView, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_media_list_view_parent_media_list = prototype( ("libvlc_media_list_view_parent_media_list", dll), paramflags )
    libvlc_media_list_view_parent_media_list.errcheck = check_vlc_exception
    libvlc_media_list_view_parent_media_list.__doc__ = """"""

if hasattr(dll, 'libvlc_media_player_new'):
    prototype=ctypes.CFUNCTYPE(MediaPlayer, Instance, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_media_player_new = prototype( ("libvlc_media_player_new", dll), paramflags )
    libvlc_media_player_new.errcheck = check_vlc_exception
    libvlc_media_player_new.__doc__ = """Create an empty Media Player object
@param p_libvlc_instance the libvlc instance in which the Media Player
       should be created.
@param p_e an initialized exception pointer
"""

if hasattr(dll, 'libvlc_media_player_new_from_media'):
    prototype=ctypes.CFUNCTYPE(MediaPlayer, Media, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_media_player_new_from_media = prototype( ("libvlc_media_player_new_from_media", dll), paramflags )
    libvlc_media_player_new_from_media.errcheck = check_vlc_exception
    libvlc_media_player_new_from_media.__doc__ = """Create a Media Player object from a Media
@param p_md the media. Afterwards the p_md can be safely
       destroyed.
@param p_e an initialized exception pointer
"""

if hasattr(dll, 'libvlc_media_player_release'):
    prototype=ctypes.CFUNCTYPE(None, MediaPlayer)
    paramflags=( (1, ), )
    libvlc_media_player_release = prototype( ("libvlc_media_player_release", dll), paramflags )
    libvlc_media_player_release.__doc__ = """Release a media_player after use
Decrement the reference count of a media player object. If the
reference count is 0, then libvlc_media_player_release() will
release the media player object. If the media player object
has been released, then it should not be used again.
@param p_mi the Media Player to free
"""

if hasattr(dll, 'libvlc_media_player_retain'):
    prototype=ctypes.CFUNCTYPE(None, MediaPlayer)
    paramflags=( (1, ), )
    libvlc_media_player_retain = prototype( ("libvlc_media_player_retain", dll), paramflags )
    libvlc_media_player_retain.__doc__ = """Retain a reference to a media player object. Use
libvlc_media_player_release() to decrement reference count.
@param p_mi media player object
"""

if hasattr(dll, 'libvlc_media_player_set_media'):
    prototype=ctypes.CFUNCTYPE(None, MediaPlayer, Media, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (3,)
    libvlc_media_player_set_media = prototype( ("libvlc_media_player_set_media", dll), paramflags )
    libvlc_media_player_set_media.errcheck = check_vlc_exception
    libvlc_media_player_set_media.__doc__ = """Set the media that will be used by the media_player. If any,
previous md will be released.
@param p_mi the Media Player
@param p_md the Media. Afterwards the p_md can be safely
       destroyed.
@param p_e an initialized exception pointer
"""

if hasattr(dll, 'libvlc_media_player_get_media'):
    prototype=ctypes.CFUNCTYPE(Media, MediaPlayer, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_media_player_get_media = prototype( ("libvlc_media_player_get_media", dll), paramflags )
    libvlc_media_player_get_media.errcheck = check_vlc_exception
    libvlc_media_player_get_media.__doc__ = """Get the media used by the media_player.
@param p_mi the Media Player
@param p_e an initialized exception pointer
@return the media associated with p_mi, or NULL if no
        media is associated
"""

if hasattr(dll, 'libvlc_media_player_event_manager'):
    prototype=ctypes.CFUNCTYPE(EventManager, MediaPlayer, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_media_player_event_manager = prototype( ("libvlc_media_player_event_manager", dll), paramflags )
    libvlc_media_player_event_manager.errcheck = check_vlc_exception
    libvlc_media_player_event_manager.__doc__ = """Get the Event Manager from which the media player send event.
@param p_mi the Media Player
@param p_e an initialized exception pointer
@return the event manager associated with p_mi
"""

if hasattr(dll, 'libvlc_media_player_is_playing'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaPlayer, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_media_player_is_playing = prototype( ("libvlc_media_player_is_playing", dll), paramflags )
    libvlc_media_player_is_playing.errcheck = check_vlc_exception
    libvlc_media_player_is_playing.__doc__ = """is_playing
@param p_mi the Media Player
@param p_e an initialized exception pointer
@return 1 if the media player is playing, 0 otherwise
"""

if hasattr(dll, 'libvlc_media_player_play'):
    prototype=ctypes.CFUNCTYPE(None, MediaPlayer, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_media_player_play = prototype( ("libvlc_media_player_play", dll), paramflags )
    libvlc_media_player_play.errcheck = check_vlc_exception
    libvlc_media_player_play.__doc__ = """Play
@param p_mi the Media Player
@param p_e an initialized exception pointer
"""

if hasattr(dll, 'libvlc_media_player_pause'):
    prototype=ctypes.CFUNCTYPE(None, MediaPlayer, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_media_player_pause = prototype( ("libvlc_media_player_pause", dll), paramflags )
    libvlc_media_player_pause.errcheck = check_vlc_exception
    libvlc_media_player_pause.__doc__ = """Pause
@param p_mi the Media Player
@param p_e an initialized exception pointer
"""

if hasattr(dll, 'libvlc_media_player_stop'):
    prototype=ctypes.CFUNCTYPE(None, MediaPlayer, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_media_player_stop = prototype( ("libvlc_media_player_stop", dll), paramflags )
    libvlc_media_player_stop.errcheck = check_vlc_exception
    libvlc_media_player_stop.__doc__ = """Stop
@param p_mi the Media Player
@param p_e an initialized exception pointer
"""

if hasattr(dll, 'libvlc_media_player_set_nsobject'):
    prototype=ctypes.CFUNCTYPE(None, MediaPlayer, ctypes.c_void_p, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (3,)
    libvlc_media_player_set_nsobject = prototype( ("libvlc_media_player_set_nsobject", dll), paramflags )
    libvlc_media_player_set_nsobject.errcheck = check_vlc_exception
    libvlc_media_player_set_nsobject.__doc__ = """Set the agl handler where the media player should render its video output.
@param p_mi the Media Player
@param drawable the agl handler
@param p_e an initialized exception pointer
"""

if hasattr(dll, 'libvlc_media_player_get_nsobject'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_void_p, MediaPlayer)
    paramflags=( (1, ), )
    libvlc_media_player_get_nsobject = prototype( ("libvlc_media_player_get_nsobject", dll), paramflags )
    libvlc_media_player_get_nsobject.__doc__ = """Get the agl handler previously set with libvlc_media_player_set_agl().
@return the agl handler or 0 if none where set
"""

if hasattr(dll, 'libvlc_media_player_set_agl'):
    prototype=ctypes.CFUNCTYPE(None, MediaPlayer, ctypes.c_uint, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (3,)
    libvlc_media_player_set_agl = prototype( ("libvlc_media_player_set_agl", dll), paramflags )
    libvlc_media_player_set_agl.errcheck = check_vlc_exception
    libvlc_media_player_set_agl.__doc__ = """Set the agl handler where the media player should render its video output.
@param p_mi the Media Player
@param drawable the agl handler
@param p_e an initialized exception pointer
"""

if hasattr(dll, 'libvlc_media_player_get_agl'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_uint, MediaPlayer)
    paramflags=( (1, ), )
    libvlc_media_player_get_agl = prototype( ("libvlc_media_player_get_agl", dll), paramflags )
    libvlc_media_player_get_agl.__doc__ = """Get the agl handler previously set with libvlc_media_player_set_agl().
@param p_mi the Media Player
@return the agl handler or 0 if none where set
"""

if hasattr(dll, 'libvlc_media_player_set_xwindow'):
    prototype=ctypes.CFUNCTYPE(None, MediaPlayer, ctypes.c_uint, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (3,)
    libvlc_media_player_set_xwindow = prototype( ("libvlc_media_player_set_xwindow", dll), paramflags )
    libvlc_media_player_set_xwindow.errcheck = check_vlc_exception
    libvlc_media_player_set_xwindow.__doc__ = """Set an X Window System drawable where the media player should render its
video output. If LibVLC was built without X11 output support, then this has
no effects.
The specified identifier must correspond to an existing Input/Output class
X11 window. Pixmaps are <b>not</b> supported. The caller shall ensure that
the X11 server is the same as the one the VLC instance has been configured
with.
If XVideo is <b>not</b> used, it is assumed that the drawable has the
following properties in common with the default X11 screen: depth, scan line
pad, black pixel. This is a bug.
@param p_mi the Media Player
@param drawable the ID of the X window
@param p_e an initialized exception pointer
"""

if hasattr(dll, 'libvlc_media_player_get_xwindow'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_uint, MediaPlayer)
    paramflags=( (1, ), )
    libvlc_media_player_get_xwindow = prototype( ("libvlc_media_player_get_xwindow", dll), paramflags )
    libvlc_media_player_get_xwindow.__doc__ = """Get the X Window System window identifier previously set with
libvlc_media_player_set_xwindow(). Note that this will return the identifier
even if VLC is not currently using it (for instance if it is playing an
audio-only input).
@return an X window ID, or 0 if none where set.
"""

if hasattr(dll, 'libvlc_media_player_set_hwnd'):
    prototype=ctypes.CFUNCTYPE(None, MediaPlayer, ctypes.c_void_p, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (3,)
    libvlc_media_player_set_hwnd = prototype( ("libvlc_media_player_set_hwnd", dll), paramflags )
    libvlc_media_player_set_hwnd.errcheck = check_vlc_exception
    libvlc_media_player_set_hwnd.__doc__ = """Set a Win32/Win64 API window handle (HWND) where the media player should
render its video output. If LibVLC was built without Win32/Win64 API output
support, then this has no effects.
@param p_mi the Media Player
@param drawable windows handle of the drawable
@param p_e an initialized exception pointer
"""

if hasattr(dll, 'libvlc_media_player_get_hwnd'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_void_p, MediaPlayer)
    paramflags=( (1, ), )
    libvlc_media_player_get_hwnd = prototype( ("libvlc_media_player_get_hwnd", dll), paramflags )
    libvlc_media_player_get_hwnd.__doc__ = """Get the Windows API window handle (HWND) previously set with
libvlc_media_player_set_hwnd(). The handle will be returned even if LibVLC
is not currently outputting any video to it.
@return a window handle or NULL if there are none.
"""

if hasattr(dll, 'libvlc_media_player_get_length'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_longlong, MediaPlayer, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_media_player_get_length = prototype( ("libvlc_media_player_get_length", dll), paramflags )
    libvlc_media_player_get_length.errcheck = check_vlc_exception
    libvlc_media_player_get_length.__doc__ = """Get the current movie length (in ms).
@param p_mi the Media Player
@param p_e an initialized exception pointer
@return the movie length (in ms).
"""

if hasattr(dll, 'libvlc_media_player_get_time'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_longlong, MediaPlayer, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_media_player_get_time = prototype( ("libvlc_media_player_get_time", dll), paramflags )
    libvlc_media_player_get_time.errcheck = check_vlc_exception
    libvlc_media_player_get_time.__doc__ = """Get the current movie time (in ms).
@param p_mi the Media Player
@param p_e an initialized exception pointer
@return the movie time (in ms).
"""

if hasattr(dll, 'libvlc_media_player_set_time'):
    prototype=ctypes.CFUNCTYPE(None, MediaPlayer, ctypes.c_longlong, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (3,)
    libvlc_media_player_set_time = prototype( ("libvlc_media_player_set_time", dll), paramflags )
    libvlc_media_player_set_time.errcheck = check_vlc_exception
    libvlc_media_player_set_time.__doc__ = """Set the movie time (in ms).
@param p_mi the Media Player
@param the movie time (in ms).
@param p_e an initialized exception pointer
"""

if hasattr(dll, 'libvlc_media_player_get_position'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_float, MediaPlayer, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_media_player_get_position = prototype( ("libvlc_media_player_get_position", dll), paramflags )
    libvlc_media_player_get_position.errcheck = check_vlc_exception
    libvlc_media_player_get_position.__doc__ = """Get movie position.
@param p_mi the Media Player
@param p_e an initialized exception pointer
@return movie position
"""

if hasattr(dll, 'libvlc_media_player_set_position'):
    prototype=ctypes.CFUNCTYPE(None, MediaPlayer, ctypes.c_float, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (3,)
    libvlc_media_player_set_position = prototype( ("libvlc_media_player_set_position", dll), paramflags )
    libvlc_media_player_set_position.errcheck = check_vlc_exception
    libvlc_media_player_set_position.__doc__ = """Set movie position.
@param p_mi the Media Player
@param f_pos the position
@param p_e an initialized exception pointer
"""

if hasattr(dll, 'libvlc_media_player_set_chapter'):
    prototype=ctypes.CFUNCTYPE(None, MediaPlayer, ctypes.c_int, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (3,)
    libvlc_media_player_set_chapter = prototype( ("libvlc_media_player_set_chapter", dll), paramflags )
    libvlc_media_player_set_chapter.errcheck = check_vlc_exception
    libvlc_media_player_set_chapter.__doc__ = """Set movie chapter
@param p_mi the Media Player
@param i_chapter chapter number to play
@param p_e an initialized exception pointer
"""

if hasattr(dll, 'libvlc_media_player_get_chapter'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaPlayer, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_media_player_get_chapter = prototype( ("libvlc_media_player_get_chapter", dll), paramflags )
    libvlc_media_player_get_chapter.errcheck = check_vlc_exception
    libvlc_media_player_get_chapter.__doc__ = """Get movie chapter
@param p_mi the Media Player
@param p_e an initialized exception pointer
@return chapter number currently playing
"""

if hasattr(dll, 'libvlc_media_player_get_chapter_count'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaPlayer, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_media_player_get_chapter_count = prototype( ("libvlc_media_player_get_chapter_count", dll), paramflags )
    libvlc_media_player_get_chapter_count.errcheck = check_vlc_exception
    libvlc_media_player_get_chapter_count.__doc__ = """Get movie chapter count
@param p_mi the Media Player
@param p_e an initialized exception pointer
@return number of chapters in movie
"""

if hasattr(dll, 'libvlc_media_player_will_play'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaPlayer, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_media_player_will_play = prototype( ("libvlc_media_player_will_play", dll), paramflags )
    libvlc_media_player_will_play.errcheck = check_vlc_exception
    libvlc_media_player_will_play.__doc__ = """Will the player play
@param p_mi the Media Player
@param p_e an initialized exception pointer
@return boolean
"""

if hasattr(dll, 'libvlc_media_player_get_chapter_count_for_title'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaPlayer, ctypes.c_int, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (3,)
    libvlc_media_player_get_chapter_count_for_title = prototype( ("libvlc_media_player_get_chapter_count_for_title", dll), paramflags )
    libvlc_media_player_get_chapter_count_for_title.errcheck = check_vlc_exception
    libvlc_media_player_get_chapter_count_for_title.__doc__ = """Get title chapter count
@param p_mi the Media Player
@param i_title title
@param p_e an initialized exception pointer
@return number of chapters in title
"""

if hasattr(dll, 'libvlc_media_player_set_title'):
    prototype=ctypes.CFUNCTYPE(None, MediaPlayer, ctypes.c_int, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (3,)
    libvlc_media_player_set_title = prototype( ("libvlc_media_player_set_title", dll), paramflags )
    libvlc_media_player_set_title.errcheck = check_vlc_exception
    libvlc_media_player_set_title.__doc__ = """Set movie title
@param p_mi the Media Player
@param i_title title number to play
@param p_e an initialized exception pointer
"""

if hasattr(dll, 'libvlc_media_player_get_title'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaPlayer, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_media_player_get_title = prototype( ("libvlc_media_player_get_title", dll), paramflags )
    libvlc_media_player_get_title.errcheck = check_vlc_exception
    libvlc_media_player_get_title.__doc__ = """Get movie title
@param p_mi the Media Player
@param p_e an initialized exception pointer
@return title number currently playing
"""

if hasattr(dll, 'libvlc_media_player_get_title_count'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaPlayer, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_media_player_get_title_count = prototype( ("libvlc_media_player_get_title_count", dll), paramflags )
    libvlc_media_player_get_title_count.errcheck = check_vlc_exception
    libvlc_media_player_get_title_count.__doc__ = """Get movie title count
@param p_mi the Media Player
@param p_e an initialized exception pointer
@return title number count
"""

if hasattr(dll, 'libvlc_media_player_previous_chapter'):
    prototype=ctypes.CFUNCTYPE(None, MediaPlayer, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_media_player_previous_chapter = prototype( ("libvlc_media_player_previous_chapter", dll), paramflags )
    libvlc_media_player_previous_chapter.errcheck = check_vlc_exception
    libvlc_media_player_previous_chapter.__doc__ = """Set previous chapter
@param p_mi the Media Player
@param p_e an initialized exception pointer
"""

if hasattr(dll, 'libvlc_media_player_next_chapter'):
    prototype=ctypes.CFUNCTYPE(None, MediaPlayer, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_media_player_next_chapter = prototype( ("libvlc_media_player_next_chapter", dll), paramflags )
    libvlc_media_player_next_chapter.errcheck = check_vlc_exception
    libvlc_media_player_next_chapter.__doc__ = """Set next chapter
@param p_mi the Media Player
@param p_e an initialized exception pointer
"""

if hasattr(dll, 'libvlc_media_player_get_rate'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_float, MediaPlayer, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_media_player_get_rate = prototype( ("libvlc_media_player_get_rate", dll), paramflags )
    libvlc_media_player_get_rate.errcheck = check_vlc_exception
    libvlc_media_player_get_rate.__doc__ = """Get movie play rate
@param p_mi the Media Player
@param p_e an initialized exception pointer
@return movie play rate
"""

if hasattr(dll, 'libvlc_media_player_set_rate'):
    prototype=ctypes.CFUNCTYPE(None, MediaPlayer, ctypes.c_float, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (3,)
    libvlc_media_player_set_rate = prototype( ("libvlc_media_player_set_rate", dll), paramflags )
    libvlc_media_player_set_rate.errcheck = check_vlc_exception
    libvlc_media_player_set_rate.__doc__ = """Set movie play rate
@param p_mi the Media Player
@param movie play rate to set
@param p_e an initialized exception pointer
"""

if hasattr(dll, 'libvlc_media_player_get_state'):
    prototype=ctypes.CFUNCTYPE(State, MediaPlayer, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_media_player_get_state = prototype( ("libvlc_media_player_get_state", dll), paramflags )
    libvlc_media_player_get_state.errcheck = check_vlc_exception
    libvlc_media_player_get_state.__doc__ = """Get current movie state
@param p_mi the Media Player
@param p_e an initialized exception pointer
@return current movie state as libvlc_state_t
"""

if hasattr(dll, 'libvlc_media_player_get_fps'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_float, MediaPlayer, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_media_player_get_fps = prototype( ("libvlc_media_player_get_fps", dll), paramflags )
    libvlc_media_player_get_fps.errcheck = check_vlc_exception
    libvlc_media_player_get_fps.__doc__ = """Get movie fps rate
@param p_mi the Media Player
@param p_e an initialized exception pointer
@return frames per second (fps) for this playing movie
"""

if hasattr(dll, 'libvlc_media_player_has_vout'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaPlayer, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_media_player_has_vout = prototype( ("libvlc_media_player_has_vout", dll), paramflags )
    libvlc_media_player_has_vout.errcheck = check_vlc_exception
    libvlc_media_player_has_vout.__doc__ = """Does this media player have a video output?
@param p_md the media player
@param p_e an initialized exception pointer
"""

if hasattr(dll, 'libvlc_media_player_is_seekable'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaPlayer, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_media_player_is_seekable = prototype( ("libvlc_media_player_is_seekable", dll), paramflags )
    libvlc_media_player_is_seekable.errcheck = check_vlc_exception
    libvlc_media_player_is_seekable.__doc__ = """Is this media player seekable?
@param p_input the input
@param p_e an initialized exception pointer
"""

if hasattr(dll, 'libvlc_media_player_can_pause'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaPlayer, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_media_player_can_pause = prototype( ("libvlc_media_player_can_pause", dll), paramflags )
    libvlc_media_player_can_pause.errcheck = check_vlc_exception
    libvlc_media_player_can_pause.__doc__ = """Can this media player be paused?
@param p_input the input
@param p_e an initialized exception pointer
"""

if hasattr(dll, 'libvlc_track_description_release'):
    prototype=ctypes.CFUNCTYPE(None, TrackDescription)
    paramflags=( (1, ), )
    libvlc_track_description_release = prototype( ("libvlc_track_description_release", dll), paramflags )
    libvlc_track_description_release.__doc__ = """Release (free) libvlc_track_description_t
@param p_track_description the structure to release
"""

if hasattr(dll, 'libvlc_toggle_fullscreen'):
    prototype=ctypes.CFUNCTYPE(None, MediaPlayer, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_toggle_fullscreen = prototype( ("libvlc_toggle_fullscreen", dll), paramflags )
    libvlc_toggle_fullscreen.errcheck = check_vlc_exception
    libvlc_toggle_fullscreen.__doc__ = """Toggle fullscreen status on video output.
@param p_mediaplayer the media player
@param p_e an initialized exception pointer
"""

if hasattr(dll, 'libvlc_set_fullscreen'):
    prototype=ctypes.CFUNCTYPE(None, MediaPlayer, ctypes.c_int, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (3,)
    libvlc_set_fullscreen = prototype( ("libvlc_set_fullscreen", dll), paramflags )
    libvlc_set_fullscreen.errcheck = check_vlc_exception
    libvlc_set_fullscreen.__doc__ = """Enable or disable fullscreen on a video output.
@param p_mediaplayer the media player
@param b_fullscreen boolean for fullscreen status
@param p_e an initialized exception pointer
"""

if hasattr(dll, 'libvlc_get_fullscreen'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaPlayer, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_get_fullscreen = prototype( ("libvlc_get_fullscreen", dll), paramflags )
    libvlc_get_fullscreen.errcheck = check_vlc_exception
    libvlc_get_fullscreen.__doc__ = """Get current fullscreen status.
@param p_mediaplayer the media player
@param p_e an initialized exception pointer
@return the fullscreen status (boolean)
"""

if hasattr(dll, 'libvlc_video_get_height'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaPlayer, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_video_get_height = prototype( ("libvlc_video_get_height", dll), paramflags )
    libvlc_video_get_height.errcheck = check_vlc_exception
    libvlc_video_get_height.__doc__ = """Get current video height.
@param p_mediaplayer the media player
@param p_e an initialized exception pointer
@return the video height
"""

if hasattr(dll, 'libvlc_video_get_width'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaPlayer, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_video_get_width = prototype( ("libvlc_video_get_width", dll), paramflags )
    libvlc_video_get_width.errcheck = check_vlc_exception
    libvlc_video_get_width.__doc__ = """Get current video width.
@param p_mediaplayer the media player
@param p_e an initialized exception pointer
@return the video width
"""

if hasattr(dll, 'libvlc_video_get_scale'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_float, MediaPlayer, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_video_get_scale = prototype( ("libvlc_video_get_scale", dll), paramflags )
    libvlc_video_get_scale.errcheck = check_vlc_exception
    libvlc_video_get_scale.__doc__ = """Get the current video scaling factor.
See also libvlc_video_set_scale().
@param p_mediaplayer the media player
@param p_e an initialized exception pointer
@return the currently configured zoom factor, or 0. if the video is set
to fit to the output window/drawable automatically.
"""

if hasattr(dll, 'libvlc_video_set_scale'):
    prototype=ctypes.CFUNCTYPE(None, MediaPlayer, ctypes.c_float, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (3,)
    libvlc_video_set_scale = prototype( ("libvlc_video_set_scale", dll), paramflags )
    libvlc_video_set_scale.errcheck = check_vlc_exception
    libvlc_video_set_scale.__doc__ = """Set the video scaling factor. That is the ratio of the number of pixels on
screen to the number of pixels in the original decoded video in each
dimension. Zero is a special value; it will adjust the video to the output
window/drawable (in windowed mode) or the entire screen.
Note that not all video outputs support scaling.
@param p_mediaplayer the media player
@param i_factor the scaling factor, or zero
@param p_e an initialized exception pointer
"""

if hasattr(dll, 'libvlc_video_get_aspect_ratio'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_char_p, MediaPlayer, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_video_get_aspect_ratio = prototype( ("libvlc_video_get_aspect_ratio", dll), paramflags )
    libvlc_video_get_aspect_ratio.errcheck = check_vlc_exception
    libvlc_video_get_aspect_ratio.__doc__ = """Get current video aspect ratio.
@param p_mediaplayer the media player
@param p_e an initialized exception pointer
@return the video aspect ratio
"""

if hasattr(dll, 'libvlc_video_set_aspect_ratio'):
    prototype=ctypes.CFUNCTYPE(None, MediaPlayer, ctypes.c_char_p, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (3,)
    libvlc_video_set_aspect_ratio = prototype( ("libvlc_video_set_aspect_ratio", dll), paramflags )
    libvlc_video_set_aspect_ratio.errcheck = check_vlc_exception
    libvlc_video_set_aspect_ratio.__doc__ = """Set new video aspect ratio.
@param p_mediaplayer the media player
@param psz_aspect new video aspect-ratio
@param p_e an initialized exception pointer
"""

if hasattr(dll, 'libvlc_video_get_spu'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaPlayer, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_video_get_spu = prototype( ("libvlc_video_get_spu", dll), paramflags )
    libvlc_video_get_spu.errcheck = check_vlc_exception
    libvlc_video_get_spu.__doc__ = """Get current video subtitle.
@param p_mediaplayer the media player
@param p_e an initialized exception pointer
@return the video subtitle selected
"""

if hasattr(dll, 'libvlc_video_get_spu_count'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaPlayer, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_video_get_spu_count = prototype( ("libvlc_video_get_spu_count", dll), paramflags )
    libvlc_video_get_spu_count.errcheck = check_vlc_exception
    libvlc_video_get_spu_count.__doc__ = """Get the number of available video subtitles.
@param p_mediaplayer the media player
@param p_e an initialized exception pointer
@return the number of available video subtitles
"""

if hasattr(dll, 'libvlc_video_get_spu_description'):
    prototype=ctypes.CFUNCTYPE(TrackDescription, MediaPlayer, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_video_get_spu_description = prototype( ("libvlc_video_get_spu_description", dll), paramflags )
    libvlc_video_get_spu_description.errcheck = check_vlc_exception
    libvlc_video_get_spu_description.__doc__ = """Get the description of available video subtitles.
@param p_mediaplayer the media player
@param p_e an initialized exception pointer
@return list containing description of available video subtitles
"""

if hasattr(dll, 'libvlc_video_set_spu'):
    prototype=ctypes.CFUNCTYPE(None, MediaPlayer, ctypes.c_int, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (3,)
    libvlc_video_set_spu = prototype( ("libvlc_video_set_spu", dll), paramflags )
    libvlc_video_set_spu.errcheck = check_vlc_exception
    libvlc_video_set_spu.__doc__ = """Set new video subtitle.
@param p_mediaplayer the media player
@param i_spu new video subtitle to select
@param p_e an initialized exception pointer
"""

if hasattr(dll, 'libvlc_video_set_subtitle_file'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaPlayer, ctypes.c_char_p, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (3,)
    libvlc_video_set_subtitle_file = prototype( ("libvlc_video_set_subtitle_file", dll), paramflags )
    libvlc_video_set_subtitle_file.errcheck = check_vlc_exception
    libvlc_video_set_subtitle_file.__doc__ = """Set new video subtitle file.
@param p_mediaplayer the media player
@param psz_subtitle new video subtitle file
@param p_e an initialized exception pointer
@return the success status (boolean)
"""

if hasattr(dll, 'libvlc_video_get_title_description'):
    prototype=ctypes.CFUNCTYPE(TrackDescription, MediaPlayer, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_video_get_title_description = prototype( ("libvlc_video_get_title_description", dll), paramflags )
    libvlc_video_get_title_description.errcheck = check_vlc_exception
    libvlc_video_get_title_description.__doc__ = """Get the description of available titles.
@param p_mediaplayer the media player
@param p_e an initialized exception pointer
@return list containing description of available titles
"""

if hasattr(dll, 'libvlc_video_get_chapter_description'):
    prototype=ctypes.CFUNCTYPE(TrackDescription, MediaPlayer, ctypes.c_int, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (3,)
    libvlc_video_get_chapter_description = prototype( ("libvlc_video_get_chapter_description", dll), paramflags )
    libvlc_video_get_chapter_description.errcheck = check_vlc_exception
    libvlc_video_get_chapter_description.__doc__ = """Get the description of available chapters for specific title.
@param p_mediaplayer the media player
@param i_title selected title
@param p_e an initialized exception pointer
@return list containing description of available chapter for title i_title
"""

if hasattr(dll, 'libvlc_video_get_crop_geometry'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_char_p, MediaPlayer, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_video_get_crop_geometry = prototype( ("libvlc_video_get_crop_geometry", dll), paramflags )
    libvlc_video_get_crop_geometry.errcheck = check_vlc_exception
    libvlc_video_get_crop_geometry.__doc__ = """Get current crop filter geometry.
@param p_mediaplayer the media player
@param p_e an initialized exception pointer
@return the crop filter geometry
"""

if hasattr(dll, 'libvlc_video_set_crop_geometry'):
    prototype=ctypes.CFUNCTYPE(None, MediaPlayer, ctypes.c_char_p, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (3,)
    libvlc_video_set_crop_geometry = prototype( ("libvlc_video_set_crop_geometry", dll), paramflags )
    libvlc_video_set_crop_geometry.errcheck = check_vlc_exception
    libvlc_video_set_crop_geometry.__doc__ = """Set new crop filter geometry.
@param p_mediaplayer the media player
@param psz_geometry new crop filter geometry
@param p_e an initialized exception pointer
"""

if hasattr(dll, 'libvlc_toggle_teletext'):
    prototype=ctypes.CFUNCTYPE(None, MediaPlayer, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_toggle_teletext = prototype( ("libvlc_toggle_teletext", dll), paramflags )
    libvlc_toggle_teletext.errcheck = check_vlc_exception
    libvlc_toggle_teletext.__doc__ = """Toggle teletext transparent status on video output.
@param p_mediaplayer the media player
@param p_e an initialized exception pointer
"""

if hasattr(dll, 'libvlc_video_get_teletext'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaPlayer, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_video_get_teletext = prototype( ("libvlc_video_get_teletext", dll), paramflags )
    libvlc_video_get_teletext.errcheck = check_vlc_exception
    libvlc_video_get_teletext.__doc__ = """Get current teletext page requested.
@param p_mediaplayer the media player
@param p_e an initialized exception pointer
@return the current teletext page requested.
"""

if hasattr(dll, 'libvlc_video_set_teletext'):
    prototype=ctypes.CFUNCTYPE(None, MediaPlayer, ctypes.c_int, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (3,)
    libvlc_video_set_teletext = prototype( ("libvlc_video_set_teletext", dll), paramflags )
    libvlc_video_set_teletext.errcheck = check_vlc_exception
    libvlc_video_set_teletext.__doc__ = """Set new teletext page to retrieve.
@param p_mediaplayer the media player
@param i_page teletex page number requested
@param p_e an initialized exception pointer
"""

if hasattr(dll, 'libvlc_video_get_track_count'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaPlayer, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_video_get_track_count = prototype( ("libvlc_video_get_track_count", dll), paramflags )
    libvlc_video_get_track_count.errcheck = check_vlc_exception
    libvlc_video_get_track_count.__doc__ = """Get number of available video tracks.
@param p_mi media player
@param p_e an initialized exception
@return the number of available video tracks (int)
"""

if hasattr(dll, 'libvlc_video_get_track_description'):
    prototype=ctypes.CFUNCTYPE(TrackDescription, MediaPlayer, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_video_get_track_description = prototype( ("libvlc_video_get_track_description", dll), paramflags )
    libvlc_video_get_track_description.errcheck = check_vlc_exception
    libvlc_video_get_track_description.__doc__ = """Get the description of available video tracks.
@param p_mi media player
@param p_e an initialized exception
@return list with description of available video tracks
"""

if hasattr(dll, 'libvlc_video_get_track'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaPlayer, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_video_get_track = prototype( ("libvlc_video_get_track", dll), paramflags )
    libvlc_video_get_track.errcheck = check_vlc_exception
    libvlc_video_get_track.__doc__ = """Get current video track.
@param p_mi media player
@param p_e an initialized exception pointer
@return the video track (int)
"""

if hasattr(dll, 'libvlc_video_set_track'):
    prototype=ctypes.CFUNCTYPE(None, MediaPlayer, ctypes.c_int, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (3,)
    libvlc_video_set_track = prototype( ("libvlc_video_set_track", dll), paramflags )
    libvlc_video_set_track.errcheck = check_vlc_exception
    libvlc_video_set_track.__doc__ = """Set video track.
@param p_mi media player
@param i_track the track (int)
@param p_e an initialized exception pointer
"""

if hasattr(dll, 'libvlc_video_take_snapshot'):
    prototype=ctypes.CFUNCTYPE(None, MediaPlayer, ctypes.c_char_p, ctypes.c_uint, ctypes.c_uint, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (1,), (1,), (3,)
    libvlc_video_take_snapshot = prototype( ("libvlc_video_take_snapshot", dll), paramflags )
    libvlc_video_take_snapshot.errcheck = check_vlc_exception
    libvlc_video_take_snapshot.__doc__ = """Take a snapshot of the current video window.
If i_width AND i_height is 0, original size is used.
If i_width XOR i_height is 0, original aspect-ratio is preserved.
@param p_mi media player instance
@param psz_filepath the path where to save the screenshot to
@param i_width the snapshot's width
@param i_height the snapshot's height
@param p_e an initialized exception pointer
"""

if hasattr(dll, 'libvlc_audio_output_list_get'):
    prototype=ctypes.CFUNCTYPE(AudioOutput, Instance, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_audio_output_list_get = prototype( ("libvlc_audio_output_list_get", dll), paramflags )
    libvlc_audio_output_list_get.errcheck = check_vlc_exception
    libvlc_audio_output_list_get.__doc__ = """Get the list of available audio outputs
@param p_instance libvlc instance
@param p_e an initialized exception pointer
@return list of available audio outputs, at the end free it with
"""

if hasattr(dll, 'libvlc_audio_output_list_release'):
    prototype=ctypes.CFUNCTYPE(None, AudioOutput)
    paramflags=( (1, ), )
    libvlc_audio_output_list_release = prototype( ("libvlc_audio_output_list_release", dll), paramflags )
    libvlc_audio_output_list_release.__doc__ = """Free the list of available audio outputs
@param p_list list with audio outputs for release
"""

if hasattr(dll, 'libvlc_audio_output_set'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, Instance, ctypes.c_char_p)
    paramflags=(1,), (1,)
    libvlc_audio_output_set = prototype( ("libvlc_audio_output_set", dll), paramflags )
    libvlc_audio_output_set.__doc__ = """Set the audio output.
Change will be applied after stop and play.
@param p_instance libvlc instance
@param psz_name name of audio output,
              use psz_name of \see libvlc_audio_output_t
@return true if function succeded
"""

if hasattr(dll, 'libvlc_audio_output_device_count'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, Instance, ctypes.c_char_p)
    paramflags=(1,), (1,)
    libvlc_audio_output_device_count = prototype( ("libvlc_audio_output_device_count", dll), paramflags )
    libvlc_audio_output_device_count.__doc__ = """Get count of devices for audio output, these devices are hardware oriented
like analor or digital output of sound card
@param p_instance libvlc instance
@param psz_audio_output - name of audio output, \see libvlc_audio_output_t
@return number of devices
"""

if hasattr(dll, 'libvlc_audio_output_device_longname'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_char_p, Instance, ctypes.c_char_p, ctypes.c_int)
    paramflags=(1,), (1,), (1,)
    libvlc_audio_output_device_longname = prototype( ("libvlc_audio_output_device_longname", dll), paramflags )
    libvlc_audio_output_device_longname.__doc__ = """Get long name of device, if not available short name given
@param p_instance libvlc instance
@param psz_audio_output - name of audio output, \see libvlc_audio_output_t
@param i_device device index
@return long name of device
"""

if hasattr(dll, 'libvlc_audio_output_device_id'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_char_p, Instance, ctypes.c_char_p, ctypes.c_int)
    paramflags=(1,), (1,), (1,)
    libvlc_audio_output_device_id = prototype( ("libvlc_audio_output_device_id", dll), paramflags )
    libvlc_audio_output_device_id.__doc__ = """Get id name of device
@param p_instance libvlc instance
@param psz_audio_output - name of audio output, \see libvlc_audio_output_t
@param i_device device index
@return id name of device, use for setting device, need to be free after use
"""

if hasattr(dll, 'libvlc_audio_output_device_set'):
    prototype=ctypes.CFUNCTYPE(None, Instance, ctypes.c_char_p, ctypes.c_char_p)
    paramflags=(1,), (1,), (1,)
    libvlc_audio_output_device_set = prototype( ("libvlc_audio_output_device_set", dll), paramflags )
    libvlc_audio_output_device_set.__doc__ = """Set device for using
@param p_instance libvlc instance
@param psz_audio_output - name of audio output, \see libvlc_audio_output_t
@param psz_device_id device
"""

if hasattr(dll, 'libvlc_audio_output_get_device_type'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, Instance, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_audio_output_get_device_type = prototype( ("libvlc_audio_output_get_device_type", dll), paramflags )
    libvlc_audio_output_get_device_type.errcheck = check_vlc_exception
    libvlc_audio_output_get_device_type.__doc__ = """Get current audio device type. Device type describes something like
character of output sound - stereo sound, 2.1, 5.1 etc
@param p_instance vlc instance
@param p_e an initialized exception pointer
@return the audio devices type \see libvlc_audio_output_device_types_t
"""

if hasattr(dll, 'libvlc_audio_output_set_device_type'):
    prototype=ctypes.CFUNCTYPE(None, Instance, ctypes.c_int, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (3,)
    libvlc_audio_output_set_device_type = prototype( ("libvlc_audio_output_set_device_type", dll), paramflags )
    libvlc_audio_output_set_device_type.errcheck = check_vlc_exception
    libvlc_audio_output_set_device_type.__doc__ = """Set current audio device type.
@param p_instance vlc instance
@param device_type the audio device type,
@param p_e an initialized exception pointer
"""

if hasattr(dll, 'libvlc_audio_toggle_mute'):
    prototype=ctypes.CFUNCTYPE(None, Instance, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_audio_toggle_mute = prototype( ("libvlc_audio_toggle_mute", dll), paramflags )
    libvlc_audio_toggle_mute.errcheck = check_vlc_exception
    libvlc_audio_toggle_mute.__doc__ = """Toggle mute status.
@param p_instance libvlc instance
@param p_e an initialized exception pointer
"""

if hasattr(dll, 'libvlc_audio_get_mute'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, Instance, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_audio_get_mute = prototype( ("libvlc_audio_get_mute", dll), paramflags )
    libvlc_audio_get_mute.errcheck = check_vlc_exception
    libvlc_audio_get_mute.__doc__ = """Get current mute status.
@param p_instance libvlc instance
@param p_e an initialized exception pointer
@return the mute status (boolean)
"""

if hasattr(dll, 'libvlc_audio_set_mute'):
    prototype=ctypes.CFUNCTYPE(None, Instance, ctypes.c_int, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (3,)
    libvlc_audio_set_mute = prototype( ("libvlc_audio_set_mute", dll), paramflags )
    libvlc_audio_set_mute.errcheck = check_vlc_exception
    libvlc_audio_set_mute.__doc__ = """Set mute status.
@param p_instance libvlc instance
@param status If status is true then mute, otherwise unmute
@param p_e an initialized exception pointer
"""

if hasattr(dll, 'libvlc_audio_get_volume'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, Instance, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_audio_get_volume = prototype( ("libvlc_audio_get_volume", dll), paramflags )
    libvlc_audio_get_volume.errcheck = check_vlc_exception
    libvlc_audio_get_volume.__doc__ = """Get current audio level.
@param p_instance libvlc instance
@param p_e an initialized exception pointer
@return the audio level (int)
"""

if hasattr(dll, 'libvlc_audio_set_volume'):
    prototype=ctypes.CFUNCTYPE(None, Instance, ctypes.c_int, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (3,)
    libvlc_audio_set_volume = prototype( ("libvlc_audio_set_volume", dll), paramflags )
    libvlc_audio_set_volume.errcheck = check_vlc_exception
    libvlc_audio_set_volume.__doc__ = """Set current audio level.
@param p_instance libvlc instance
@param i_volume the volume (int)
@param p_e an initialized exception pointer
"""

if hasattr(dll, 'libvlc_audio_get_track_count'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaPlayer, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_audio_get_track_count = prototype( ("libvlc_audio_get_track_count", dll), paramflags )
    libvlc_audio_get_track_count.errcheck = check_vlc_exception
    libvlc_audio_get_track_count.__doc__ = """Get number of available audio tracks.
@param p_mi media player
@param p_e an initialized exception
@return the number of available audio tracks (int)
"""

if hasattr(dll, 'libvlc_audio_get_track_description'):
    prototype=ctypes.CFUNCTYPE(TrackDescription, MediaPlayer, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_audio_get_track_description = prototype( ("libvlc_audio_get_track_description", dll), paramflags )
    libvlc_audio_get_track_description.errcheck = check_vlc_exception
    libvlc_audio_get_track_description.__doc__ = """Get the description of available audio tracks.
@param p_mi media player
@param p_e an initialized exception
@return list with description of available audio tracks
"""

if hasattr(dll, 'libvlc_audio_get_track'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaPlayer, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_audio_get_track = prototype( ("libvlc_audio_get_track", dll), paramflags )
    libvlc_audio_get_track.errcheck = check_vlc_exception
    libvlc_audio_get_track.__doc__ = """Get current audio track.
@param p_mi media player
@param p_e an initialized exception pointer
@return the audio track (int)
"""

if hasattr(dll, 'libvlc_audio_set_track'):
    prototype=ctypes.CFUNCTYPE(None, MediaPlayer, ctypes.c_int, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (3,)
    libvlc_audio_set_track = prototype( ("libvlc_audio_set_track", dll), paramflags )
    libvlc_audio_set_track.errcheck = check_vlc_exception
    libvlc_audio_set_track.__doc__ = """Set current audio track.
@param p_mi media player
@param i_track the track (int)
@param p_e an initialized exception pointer
"""

if hasattr(dll, 'libvlc_audio_get_channel'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, Instance, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_audio_get_channel = prototype( ("libvlc_audio_get_channel", dll), paramflags )
    libvlc_audio_get_channel.errcheck = check_vlc_exception
    libvlc_audio_get_channel.__doc__ = """Get current audio channel.
@param p_instance vlc instance
@param p_e an initialized exception pointer
@return the audio channel \see libvlc_audio_output_channel_t
"""

if hasattr(dll, 'libvlc_audio_set_channel'):
    prototype=ctypes.CFUNCTYPE(None, Instance, ctypes.c_int, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (3,)
    libvlc_audio_set_channel = prototype( ("libvlc_audio_set_channel", dll), paramflags )
    libvlc_audio_set_channel.errcheck = check_vlc_exception
    libvlc_audio_set_channel.__doc__ = """Set current audio channel.
@param p_instance vlc instance
@param channel the audio channel, \see libvlc_audio_output_channel_t
@param p_e an initialized exception pointer
"""

if hasattr(dll, 'libvlc_vlm_release'):
    prototype=ctypes.CFUNCTYPE(None, Instance, ctypes.POINTER(VLCException))
    paramflags=(1,), (3,)
    libvlc_vlm_release = prototype( ("libvlc_vlm_release", dll), paramflags )
    libvlc_vlm_release.errcheck = check_vlc_exception
    libvlc_vlm_release.__doc__ = """Release the vlm instance related to the given libvlc_instance_t
@param p_instance the instance
@param p_e an initialized exception pointer
"""

if hasattr(dll, 'libvlc_vlm_add_broadcast'):
    prototype=ctypes.CFUNCTYPE(None, Instance, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, ListPOINTER(ctypes.c_char_p), ctypes.c_int, ctypes.c_int, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (1,), (1,), (1,), (1,), (1,), (1,), (3,)
    libvlc_vlm_add_broadcast = prototype( ("libvlc_vlm_add_broadcast", dll), paramflags )
    libvlc_vlm_add_broadcast.errcheck = check_vlc_exception
    libvlc_vlm_add_broadcast.__doc__ = """Add a broadcast, with one input.
@param p_instance the instance
@param psz_name the name of the new broadcast
@param psz_input the input MRL
@param psz_output the output MRL (the parameter to the "sout" variable)
@param i_options number of additional options
@param ppsz_options additional options
@param b_enabled boolean for enabling the new broadcast
@param b_loop Should this broadcast be played in loop ?
@param p_e an initialized exception pointer
"""

if hasattr(dll, 'libvlc_vlm_add_vod'):
    prototype=ctypes.CFUNCTYPE(None, Instance, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, ListPOINTER(ctypes.c_char_p), ctypes.c_int, ctypes.c_char_p, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (1,), (1,), (1,), (1,), (1,), (3,)
    libvlc_vlm_add_vod = prototype( ("libvlc_vlm_add_vod", dll), paramflags )
    libvlc_vlm_add_vod.errcheck = check_vlc_exception
    libvlc_vlm_add_vod.__doc__ = """Add a vod, with one input.
@param p_instance the instance
@param psz_name the name of the new vod media
@param psz_input the input MRL
@param i_options number of additional options
@param ppsz_options additional options
@param b_enabled boolean for enabling the new vod
@param psz_mux the muxer of the vod media
@param p_e an initialized exception pointer
"""

if hasattr(dll, 'libvlc_vlm_del_media'):
    prototype=ctypes.CFUNCTYPE(None, Instance, ctypes.c_char_p, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (3,)
    libvlc_vlm_del_media = prototype( ("libvlc_vlm_del_media", dll), paramflags )
    libvlc_vlm_del_media.errcheck = check_vlc_exception
    libvlc_vlm_del_media.__doc__ = """Delete a media (VOD or broadcast).
@param p_instance the instance
@param psz_name the media to delete
@param p_e an initialized exception pointer
"""

if hasattr(dll, 'libvlc_vlm_set_enabled'):
    prototype=ctypes.CFUNCTYPE(None, Instance, ctypes.c_char_p, ctypes.c_int, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (1,), (3,)
    libvlc_vlm_set_enabled = prototype( ("libvlc_vlm_set_enabled", dll), paramflags )
    libvlc_vlm_set_enabled.errcheck = check_vlc_exception
    libvlc_vlm_set_enabled.__doc__ = """Enable or disable a media (VOD or broadcast).
@param p_instance the instance
@param psz_name the media to work on
@param b_enabled the new status
@param p_e an initialized exception pointer
"""

if hasattr(dll, 'libvlc_vlm_set_output'):
    prototype=ctypes.CFUNCTYPE(None, Instance, ctypes.c_char_p, ctypes.c_char_p, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (1,), (3,)
    libvlc_vlm_set_output = prototype( ("libvlc_vlm_set_output", dll), paramflags )
    libvlc_vlm_set_output.errcheck = check_vlc_exception
    libvlc_vlm_set_output.__doc__ = """Set the output for a media.
@param p_instance the instance
@param psz_name the media to work on
@param psz_output the output MRL (the parameter to the "sout" variable)
@param p_e an initialized exception pointer
"""

if hasattr(dll, 'libvlc_vlm_set_input'):
    prototype=ctypes.CFUNCTYPE(None, Instance, ctypes.c_char_p, ctypes.c_char_p, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (1,), (3,)
    libvlc_vlm_set_input = prototype( ("libvlc_vlm_set_input", dll), paramflags )
    libvlc_vlm_set_input.errcheck = check_vlc_exception
    libvlc_vlm_set_input.__doc__ = """Set a media's input MRL. This will delete all existing inputs and
add the specified one.
@param p_instance the instance
@param psz_name the media to work on
@param psz_input the input MRL
@param p_e an initialized exception pointer
"""

if hasattr(dll, 'libvlc_vlm_add_input'):
    prototype=ctypes.CFUNCTYPE(None, Instance, ctypes.c_char_p, ctypes.c_char_p, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (1,), (3,)
    libvlc_vlm_add_input = prototype( ("libvlc_vlm_add_input", dll), paramflags )
    libvlc_vlm_add_input.errcheck = check_vlc_exception
    libvlc_vlm_add_input.__doc__ = """Add a media's input MRL. This will add the specified one.
@param p_instance the instance
@param psz_name the media to work on
@param psz_input the input MRL
@param p_e an initialized exception pointer
"""

if hasattr(dll, 'libvlc_vlm_set_loop'):
    prototype=ctypes.CFUNCTYPE(None, Instance, ctypes.c_char_p, ctypes.c_int, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (1,), (3,)
    libvlc_vlm_set_loop = prototype( ("libvlc_vlm_set_loop", dll), paramflags )
    libvlc_vlm_set_loop.errcheck = check_vlc_exception
    libvlc_vlm_set_loop.__doc__ = """Set a media's loop status.
@param p_instance the instance
@param psz_name the media to work on
@param b_loop the new status
@param p_e an initialized exception pointer
"""

if hasattr(dll, 'libvlc_vlm_set_mux'):
    prototype=ctypes.CFUNCTYPE(None, Instance, ctypes.c_char_p, ctypes.c_char_p, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (1,), (3,)
    libvlc_vlm_set_mux = prototype( ("libvlc_vlm_set_mux", dll), paramflags )
    libvlc_vlm_set_mux.errcheck = check_vlc_exception
    libvlc_vlm_set_mux.__doc__ = """Set a media's vod muxer.
@param p_instance the instance
@param psz_name the media to work on
@param psz_mux the new muxer
@param p_e an initialized exception pointer
"""

if hasattr(dll, 'libvlc_vlm_change_media'):
    prototype=ctypes.CFUNCTYPE(None, Instance, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, ListPOINTER(ctypes.c_char_p), ctypes.c_int, ctypes.c_int, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (1,), (1,), (1,), (1,), (1,), (1,), (3,)
    libvlc_vlm_change_media = prototype( ("libvlc_vlm_change_media", dll), paramflags )
    libvlc_vlm_change_media.errcheck = check_vlc_exception
    libvlc_vlm_change_media.__doc__ = """Edit the parameters of a media. This will delete all existing inputs and
add the specified one.
@param p_instance the instance
@param psz_name the name of the new broadcast
@param psz_input the input MRL
@param psz_output the output MRL (the parameter to the "sout" variable)
@param i_options number of additional options
@param ppsz_options additional options
@param b_enabled boolean for enabling the new broadcast
@param b_loop Should this broadcast be played in loop ?
@param p_e an initialized exception pointer
"""

if hasattr(dll, 'libvlc_vlm_play_media'):
    prototype=ctypes.CFUNCTYPE(None, Instance, ctypes.c_char_p, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (3,)
    libvlc_vlm_play_media = prototype( ("libvlc_vlm_play_media", dll), paramflags )
    libvlc_vlm_play_media.errcheck = check_vlc_exception
    libvlc_vlm_play_media.__doc__ = """Play the named broadcast.
@param p_instance the instance
@param psz_name the name of the broadcast
@param p_e an initialized exception pointer
"""

if hasattr(dll, 'libvlc_vlm_stop_media'):
    prototype=ctypes.CFUNCTYPE(None, Instance, ctypes.c_char_p, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (3,)
    libvlc_vlm_stop_media = prototype( ("libvlc_vlm_stop_media", dll), paramflags )
    libvlc_vlm_stop_media.errcheck = check_vlc_exception
    libvlc_vlm_stop_media.__doc__ = """Stop the named broadcast.
@param p_instance the instance
@param psz_name the name of the broadcast
@param p_e an initialized exception pointer
"""

if hasattr(dll, 'libvlc_vlm_pause_media'):
    prototype=ctypes.CFUNCTYPE(None, Instance, ctypes.c_char_p, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (3,)
    libvlc_vlm_pause_media = prototype( ("libvlc_vlm_pause_media", dll), paramflags )
    libvlc_vlm_pause_media.errcheck = check_vlc_exception
    libvlc_vlm_pause_media.__doc__ = """Pause the named broadcast.
@param p_instance the instance
@param psz_name the name of the broadcast
@param p_e an initialized exception pointer
"""

if hasattr(dll, 'libvlc_vlm_seek_media'):
    prototype=ctypes.CFUNCTYPE(None, Instance, ctypes.c_char_p, ctypes.c_float, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (1,), (3,)
    libvlc_vlm_seek_media = prototype( ("libvlc_vlm_seek_media", dll), paramflags )
    libvlc_vlm_seek_media.errcheck = check_vlc_exception
    libvlc_vlm_seek_media.__doc__ = """Seek in the named broadcast.
@param p_instance the instance
@param psz_name the name of the broadcast
@param f_percentage the percentage to seek to
@param p_e an initialized exception pointer
"""

if hasattr(dll, 'libvlc_vlm_show_media'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_char_p, Instance, ctypes.c_char_p, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (3,)
    libvlc_vlm_show_media = prototype( ("libvlc_vlm_show_media", dll), paramflags )
    libvlc_vlm_show_media.errcheck = check_vlc_exception
    libvlc_vlm_show_media.__doc__ = """Return information about the named broadcast.
\bug will always return NULL
@param p_instance the instance
@param psz_name the name of the broadcast
@param p_e an initialized exception pointer
@return string with information about named media
"""

if hasattr(dll, 'libvlc_vlm_get_media_instance_position'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_float, Instance, ctypes.c_char_p, ctypes.c_int, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (1,), (3,)
    libvlc_vlm_get_media_instance_position = prototype( ("libvlc_vlm_get_media_instance_position", dll), paramflags )
    libvlc_vlm_get_media_instance_position.errcheck = check_vlc_exception
    libvlc_vlm_get_media_instance_position.__doc__ = """Get vlm_media instance position by name or instance id
@param p_instance a libvlc instance
@param psz_name name of vlm media instance
@param i_instance instance id
@param p_e an initialized exception pointer
@return position as float
"""

if hasattr(dll, 'libvlc_vlm_get_media_instance_time'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, Instance, ctypes.c_char_p, ctypes.c_int, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (1,), (3,)
    libvlc_vlm_get_media_instance_time = prototype( ("libvlc_vlm_get_media_instance_time", dll), paramflags )
    libvlc_vlm_get_media_instance_time.errcheck = check_vlc_exception
    libvlc_vlm_get_media_instance_time.__doc__ = """Get vlm_media instance time by name or instance id
@param p_instance a libvlc instance
@param psz_name name of vlm media instance
@param i_instance instance id
@param p_e an initialized exception pointer
@return time as integer
"""

if hasattr(dll, 'libvlc_vlm_get_media_instance_length'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, Instance, ctypes.c_char_p, ctypes.c_int, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (1,), (3,)
    libvlc_vlm_get_media_instance_length = prototype( ("libvlc_vlm_get_media_instance_length", dll), paramflags )
    libvlc_vlm_get_media_instance_length.errcheck = check_vlc_exception
    libvlc_vlm_get_media_instance_length.__doc__ = """Get vlm_media instance length by name or instance id
@param p_instance a libvlc instance
@param psz_name name of vlm media instance
@param i_instance instance id
@param p_e an initialized exception pointer
@return length of media item
"""

if hasattr(dll, 'libvlc_vlm_get_media_instance_rate'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, Instance, ctypes.c_char_p, ctypes.c_int, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (1,), (3,)
    libvlc_vlm_get_media_instance_rate = prototype( ("libvlc_vlm_get_media_instance_rate", dll), paramflags )
    libvlc_vlm_get_media_instance_rate.errcheck = check_vlc_exception
    libvlc_vlm_get_media_instance_rate.__doc__ = """Get vlm_media instance playback rate by name or instance id
@param p_instance a libvlc instance
@param psz_name name of vlm media instance
@param i_instance instance id
@param p_e an initialized exception pointer
@return playback rate
"""

if hasattr(dll, 'libvlc_vlm_get_media_instance_title'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, Instance, ctypes.c_char_p, ctypes.c_int, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (1,), (3,)
    libvlc_vlm_get_media_instance_title = prototype( ("libvlc_vlm_get_media_instance_title", dll), paramflags )
    libvlc_vlm_get_media_instance_title.errcheck = check_vlc_exception
    libvlc_vlm_get_media_instance_title.__doc__ = """Get vlm_media instance title number by name or instance id
\bug will always return 0
@param p_instance a libvlc instance
@param psz_name name of vlm media instance
@param i_instance instance id
@param p_e an initialized exception pointer
@return title as number
"""

if hasattr(dll, 'libvlc_vlm_get_media_instance_chapter'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, Instance, ctypes.c_char_p, ctypes.c_int, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (1,), (3,)
    libvlc_vlm_get_media_instance_chapter = prototype( ("libvlc_vlm_get_media_instance_chapter", dll), paramflags )
    libvlc_vlm_get_media_instance_chapter.errcheck = check_vlc_exception
    libvlc_vlm_get_media_instance_chapter.__doc__ = """Get vlm_media instance chapter number by name or instance id
\bug will always return 0
@param p_instance a libvlc instance
@param psz_name name of vlm media instance
@param i_instance instance id
@param p_e an initialized exception pointer
@return chapter as number
"""

if hasattr(dll, 'libvlc_vlm_get_media_instance_seekable'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, Instance, ctypes.c_char_p, ctypes.c_int, ctypes.POINTER(VLCException))
    paramflags=(1,), (1,), (1,), (3,)
    libvlc_vlm_get_media_instance_seekable = prototype( ("libvlc_vlm_get_media_instance_seekable", dll), paramflags )
    libvlc_vlm_get_media_instance_seekable.errcheck = check_vlc_exception
    libvlc_vlm_get_media_instance_seekable.__doc__ = """Is libvlc instance seekable ?
\bug will always return 0
@param p_instance a libvlc instance
@param psz_name name of vlm media instance
@param i_instance instance id
@param p_e an initialized exception pointer
@return 1 if seekable, 0 if not
"""

if hasattr(dll, 'mediacontrol_RGBPicture__free'):
    prototype=ctypes.CFUNCTYPE(None, ctypes.POINTER(RGBPicture))
    paramflags=( (1, ), )
    mediacontrol_RGBPicture__free = prototype( ("mediacontrol_RGBPicture__free", dll), paramflags )
    mediacontrol_RGBPicture__free.__doc__ = """Free a RGBPicture structure.
@param pic: the RGBPicture structure
"""

if hasattr(dll, 'mediacontrol_StreamInformation__free'):
    prototype=ctypes.CFUNCTYPE(None, ctypes.POINTER(MediaControlStreamInformation))
    paramflags=( (1, ), )
    mediacontrol_StreamInformation__free = prototype( ("mediacontrol_StreamInformation__free", dll), paramflags )
    mediacontrol_StreamInformation__free.__doc__ = """Free a StreamInformation structure.
@param pic: the StreamInformation structure
"""

if hasattr(dll, 'mediacontrol_exception_create'):
    prototype=ctypes.CFUNCTYPE(MediaControlException)
    paramflags= tuple()
    mediacontrol_exception_create = prototype( ("mediacontrol_exception_create", dll), paramflags )
    mediacontrol_exception_create.__doc__ = """Instanciate and initialize an exception structure.
@return the exception
"""

if hasattr(dll, 'mediacontrol_exception_init'):
    prototype=ctypes.CFUNCTYPE(None, MediaControlException)
    paramflags=( (1, ), )
    mediacontrol_exception_init = prototype( ("mediacontrol_exception_init", dll), paramflags )
    mediacontrol_exception_init.__doc__ = """Initialize an existing exception structure.
@param p_exception the exception to initialize.
"""

if hasattr(dll, 'mediacontrol_exception_cleanup'):
    prototype=ctypes.CFUNCTYPE(None, MediaControlException)
    paramflags=( (1, ), )
    mediacontrol_exception_cleanup = prototype( ("mediacontrol_exception_cleanup", dll), paramflags )
    mediacontrol_exception_cleanup.__doc__ = """Clean up an existing exception structure after use.
@param p_exception the exception to clean up.
"""

if hasattr(dll, 'mediacontrol_exception_free'):
    prototype=ctypes.CFUNCTYPE(None, MediaControlException)
    paramflags=( (1, ), )
    mediacontrol_exception_free = prototype( ("mediacontrol_exception_free", dll), paramflags )
    mediacontrol_exception_free.__doc__ = """Free an exception structure created with mediacontrol_exception_create().
@return the exception
"""

if hasattr(dll, 'mediacontrol_new'):
    prototype=ctypes.CFUNCTYPE(MediaControl, ctypes.c_int, ListPOINTER(ctypes.c_char_p), MediaControlException)
    paramflags=(1,), (1,), (1,)
    mediacontrol_new = prototype( ("mediacontrol_new", dll), paramflags )
    mediacontrol_new.__doc__ = """Create a MediaControl instance with parameters
@param argc the number of arguments
@param argv parameters
@param exception an initialized exception pointer
@return a mediacontrol_Instance
"""

if hasattr(dll, 'mediacontrol_new_from_instance'):
    prototype=ctypes.CFUNCTYPE(MediaControl, Instance, MediaControlException)
    paramflags=(1,), (1,)
    mediacontrol_new_from_instance = prototype( ("mediacontrol_new_from_instance", dll), paramflags )
    mediacontrol_new_from_instance.__doc__ = """Create a MediaControl instance from an existing libvlc instance
@param p_instance the libvlc instance
@param exception an initialized exception pointer
@return a mediacontrol_Instance
"""

if hasattr(dll, 'mediacontrol_get_libvlc_instance'):
    prototype=ctypes.CFUNCTYPE(Instance, MediaControl)
    paramflags=( (1, ), )
    mediacontrol_get_libvlc_instance = prototype( ("mediacontrol_get_libvlc_instance", dll), paramflags )
    mediacontrol_get_libvlc_instance.__doc__ = """Get the associated libvlc instance
@param self: the mediacontrol instance
@return a libvlc instance
"""

if hasattr(dll, 'mediacontrol_get_media_player'):
    prototype=ctypes.CFUNCTYPE(MediaPlayer, MediaControl)
    paramflags=( (1, ), )
    mediacontrol_get_media_player = prototype( ("mediacontrol_get_media_player", dll), paramflags )
    mediacontrol_get_media_player.__doc__ = """Get the associated libvlc_media_player
@param self: the mediacontrol instance
@return a libvlc_media_player_t instance
"""

if hasattr(dll, 'mediacontrol_get_media_position'):
    prototype=ctypes.CFUNCTYPE(ctypes.POINTER(MediaControlPosition), MediaControl, PositionOrigin, PositionKey, MediaControlException)
    paramflags=(1,), (1,), (1,), (1,)
    mediacontrol_get_media_position = prototype( ("mediacontrol_get_media_position", dll), paramflags )
    mediacontrol_get_media_position.__doc__ = """Get the current position
@param self the mediacontrol instance
@param an_origin the position origin
@param a_key the position unit
@param exception an initialized exception pointer
@return a mediacontrol_Position
"""

if hasattr(dll, 'mediacontrol_set_media_position'):
    prototype=ctypes.CFUNCTYPE(None, MediaControl, ctypes.POINTER(MediaControlPosition), MediaControlException)
    paramflags=(1,), (1,), (1,)
    mediacontrol_set_media_position = prototype( ("mediacontrol_set_media_position", dll), paramflags )
    mediacontrol_set_media_position.__doc__ = """Set the position
@param self the mediacontrol instance
@param a_position a mediacontrol_Position
@param exception an initialized exception pointer
"""

if hasattr(dll, 'mediacontrol_start'):
    prototype=ctypes.CFUNCTYPE(None, MediaControl, ctypes.POINTER(MediaControlPosition), MediaControlException)
    paramflags=(1,), (1,), (1,)
    mediacontrol_start = prototype( ("mediacontrol_start", dll), paramflags )
    mediacontrol_start.__doc__ = """Play the movie at a given position
@param self the mediacontrol instance
@param a_position a mediacontrol_Position
@param exception an initialized exception pointer
"""

if hasattr(dll, 'mediacontrol_pause'):
    prototype=ctypes.CFUNCTYPE(None, MediaControl, MediaControlException)
    paramflags=(1,), (1,)
    mediacontrol_pause = prototype( ("mediacontrol_pause", dll), paramflags )
    mediacontrol_pause.__doc__ = """Pause the movie at a given position
@param self the mediacontrol instance
@param exception an initialized exception pointer
"""

if hasattr(dll, 'mediacontrol_resume'):
    prototype=ctypes.CFUNCTYPE(None, MediaControl, MediaControlException)
    paramflags=(1,), (1,)
    mediacontrol_resume = prototype( ("mediacontrol_resume", dll), paramflags )
    mediacontrol_resume.__doc__ = """Resume the movie at a given position
@param self the mediacontrol instance
@param exception an initialized exception pointer
"""

if hasattr(dll, 'mediacontrol_stop'):
    prototype=ctypes.CFUNCTYPE(None, MediaControl, MediaControlException)
    paramflags=(1,), (1,)
    mediacontrol_stop = prototype( ("mediacontrol_stop", dll), paramflags )
    mediacontrol_stop.__doc__ = """Stop the movie at a given position
@param self the mediacontrol instance
@param exception an initialized exception pointer
"""

if hasattr(dll, 'mediacontrol_exit'):
    prototype=ctypes.CFUNCTYPE(None, MediaControl)
    paramflags=( (1, ), )
    mediacontrol_exit = prototype( ("mediacontrol_exit", dll), paramflags )
    mediacontrol_exit.__doc__ = """Exit the player
@param self the mediacontrol instance
"""

if hasattr(dll, 'mediacontrol_set_mrl'):
    prototype=ctypes.CFUNCTYPE(None, MediaControl, ctypes.c_char_p, MediaControlException)
    paramflags=(1,), (1,), (1,)
    mediacontrol_set_mrl = prototype( ("mediacontrol_set_mrl", dll), paramflags )
    mediacontrol_set_mrl.__doc__ = """Set the MRL to be played.
@param self the mediacontrol instance
@param psz_file the MRL
@param exception an initialized exception pointer
"""

if hasattr(dll, 'mediacontrol_get_mrl'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_char_p, MediaControl, MediaControlException)
    paramflags=(1,), (1,)
    mediacontrol_get_mrl = prototype( ("mediacontrol_get_mrl", dll), paramflags )
    mediacontrol_get_mrl.__doc__ = """Get the MRL to be played.
@param self the mediacontrol instance
@param exception an initialized exception pointer
"""

if hasattr(dll, 'mediacontrol_snapshot'):
    prototype=ctypes.CFUNCTYPE(ctypes.POINTER(RGBPicture), MediaControl, ctypes.POINTER(MediaControlPosition), MediaControlException)
    paramflags=(1,), (1,), (1,)
    mediacontrol_snapshot = prototype( ("mediacontrol_snapshot", dll), paramflags )
    mediacontrol_snapshot.__doc__ = """Get a snapshot
@param self the mediacontrol instance
@param a_position the desired position (ignored for now)
@param exception an initialized exception pointer
@return a RGBpicture
"""

if hasattr(dll, 'mediacontrol_display_text'):
    prototype=ctypes.CFUNCTYPE(None, MediaControl, ctypes.c_char_p, ctypes.POINTER(MediaControlPosition), ctypes.POINTER(MediaControlPosition), MediaControlException)
    paramflags=(1,), (1,), (1,), (1,), (1,)
    mediacontrol_display_text = prototype( ("mediacontrol_display_text", dll), paramflags )
    mediacontrol_display_text.__doc__ = """ Displays the message string, between "begin" and "end" positions.
@param self the mediacontrol instance
@param message the message to display
@param begin the begin position
@param end the end position
@param exception an initialized exception pointer
"""

if hasattr(dll, 'mediacontrol_get_stream_information'):
    prototype=ctypes.CFUNCTYPE(ctypes.POINTER(MediaControlStreamInformation), MediaControl, PositionKey, MediaControlException)
    paramflags=(1,), (1,), (1,)
    mediacontrol_get_stream_information = prototype( ("mediacontrol_get_stream_information", dll), paramflags )
    mediacontrol_get_stream_information.__doc__ = """ Get information about a stream
@param self the mediacontrol instance
@param a_key the time unit
@param exception an initialized exception pointer
@return a mediacontrol_StreamInformation
"""

if hasattr(dll, 'mediacontrol_sound_get_volume'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_short, MediaControl, MediaControlException)
    paramflags=(1,), (1,)
    mediacontrol_sound_get_volume = prototype( ("mediacontrol_sound_get_volume", dll), paramflags )
    mediacontrol_sound_get_volume.__doc__ = """Get the current audio level, normalized in [0..100]
@param self the mediacontrol instance
@param exception an initialized exception pointer
@return the volume
"""

if hasattr(dll, 'mediacontrol_sound_set_volume'):
    prototype=ctypes.CFUNCTYPE(None, MediaControl, ctypes.c_short, MediaControlException)
    paramflags=(1,), (1,), (1,)
    mediacontrol_sound_set_volume = prototype( ("mediacontrol_sound_set_volume", dll), paramflags )
    mediacontrol_sound_set_volume.__doc__ = """Set the audio level
@param self the mediacontrol instance
@param volume the volume (normalized in [0..100])
@param exception an initialized exception pointer
"""

if hasattr(dll, 'mediacontrol_set_visual'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaControl, ctypes.c_ulong, MediaControlException)
    paramflags=(1,), (1,), (1,)
    mediacontrol_set_visual = prototype( ("mediacontrol_set_visual", dll), paramflags )
    mediacontrol_set_visual.__doc__ = """Set the video output window
@param self the mediacontrol instance
@param visual_id the Xid or HWND, depending on the platform
@param exception an initialized exception pointer
"""

if hasattr(dll, 'mediacontrol_get_rate'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaControl, MediaControlException)
    paramflags=(1,), (1,)
    mediacontrol_get_rate = prototype( ("mediacontrol_get_rate", dll), paramflags )
    mediacontrol_get_rate.__doc__ = """Get the current playing rate, in percent
@param self the mediacontrol instance
@param exception an initialized exception pointer
@return the rate
"""

if hasattr(dll, 'mediacontrol_set_rate'):
    prototype=ctypes.CFUNCTYPE(None, MediaControl, ctypes.c_int, MediaControlException)
    paramflags=(1,), (1,), (1,)
    mediacontrol_set_rate = prototype( ("mediacontrol_set_rate", dll), paramflags )
    mediacontrol_set_rate.__doc__ = """Set the playing rate, in percent
@param self the mediacontrol instance
@param rate the desired rate
@param exception an initialized exception pointer
"""

if hasattr(dll, 'mediacontrol_get_fullscreen'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaControl, MediaControlException)
    paramflags=(1,), (1,)
    mediacontrol_get_fullscreen = prototype( ("mediacontrol_get_fullscreen", dll), paramflags )
    mediacontrol_get_fullscreen.__doc__ = """Get current fullscreen status
@param self the mediacontrol instance
@param exception an initialized exception pointer
@return the fullscreen status
"""

if hasattr(dll, 'mediacontrol_set_fullscreen'):
    prototype=ctypes.CFUNCTYPE(None, MediaControl, ctypes.c_int, MediaControlException)
    paramflags=(1,), (1,), (1,)
    mediacontrol_set_fullscreen = prototype( ("mediacontrol_set_fullscreen", dll), paramflags )
    mediacontrol_set_fullscreen.__doc__ = """Set fullscreen status
@param self the mediacontrol instance
@param b_fullscreen the desired status
@param exception an initialized exception pointer
"""

### Start of footer.py ###

class MediaEvent(ctypes.Structure):
    _fields_ = [
        ('media_name', ctypes.c_char_p),
        ('instance_name', ctypes.c_char_p),
        ]

class EventUnion(ctypes.Union):
    _fields_ = [
        ('meta_type', ctypes.c_uint),
        ('new_child', ctypes.c_uint),
        ('new_duration', ctypes.c_longlong),
        ('new_status', ctypes.c_int),
        ('media', ctypes.c_void_p),
        ('new_state', ctypes.c_uint),
        # Media instance
        ('new_position', ctypes.c_float),
        ('new_time', ctypes.c_longlong),
        ('new_title', ctypes.c_int),
        ('new_seekable', ctypes.c_longlong),
        ('new_pausable', ctypes.c_longlong),
        # FIXME: Skipped MediaList and MediaListView...
        ('filename', ctypes.c_char_p),
        ('new_length', ctypes.c_longlong),
        ('media_event', MediaEvent),
        ]

class Event(ctypes.Structure):
    _fields_ = [
        ('type', EventType),
        ('object', ctypes.c_void_p),
        ('u', EventUnion),
        ]

# Decorator for callback methods
callbackmethod=ctypes.CFUNCTYPE(None, Event, ctypes.c_void_p)

# Example callback method
@callbackmethod
def debug_callback(event, data):
    print "Debug callback method"
    print "Event:", event.type
    print "Data", data

if __name__ == '__main__':
    try:
        from msvcrt import getch
    except ImportError:
        def getch():
            import tty
            import termios
            fd=sys.stdin.fileno()
            old_settings=termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                ch=sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch

    @callbackmethod
    def end_callback(event, data):
        print "End of stream"
        sys.exit(0)

    if sys.argv[1:]:
        instance=Instance()
        media=instance.media_new(sys.argv[1])
        player=instance.media_player_new()
        player.set_media(media)
        player.play()

        event_manager=player.event_manager()
        event_manager.event_attach(EventType.MediaPlayerEndReached, end_callback, None)

        def print_info():
            """Print information about the media."""
            media=player.get_media()
            print "State:", player.get_state()
            print "Media:", media.get_mrl()
            try:
                print "Current time:", player.get_time(), "/", media.get_duration()
                print "Position:", player.get_position()
                print "FPS:", player.get_fps()
                print "Rate:", player.get_rate()
                print "Video size: (%d, %d)" % (player.video_get_width(), player.video_get_height())
            except Exception:
                pass

        def forward():
            """Go forward 1s"""
            player.set_time(player.get_time() + 1000)

        def one_frame_forward():
            """Go forward one frame"""
            player.set_time(player.get_time() + long(1000 / (player.get_fps() or 25)))

        def one_frame_backward():
            """Go backward one frame"""
            player.set_time(player.get_time() - long(1000 / (player.get_fps() or 25)))

        def backward():
            """Go backward 1s"""
            player.set_time(player.get_time() - 1000)

        def print_help():
            """Print help
            """
            print "Commands:"
            for k, m in keybindings.iteritems():
                print "  %s: %s" % (k, (m.__doc__ or m.__name__).splitlines()[0])
            print " 1-9: go to the given fraction of the movie"

        def quit_app():
            """Exit."""
            sys.exit(0)

        keybindings={
            'f': player.toggle_fullscreen,
            ' ': player.pause,
            '+': forward,
            '-': backward,
            '.': one_frame_forward,
            ',': one_frame_backward,
            '?': print_help,
            'i': print_info,
            'q': quit_app,
            }

        print "Press q to quit, ? to get help."
        while True:
            k=getch()
            o=ord(k)
            method=keybindings.get(k, None)
            if method is not None:
                method()
            elif o >= 49 and o <= 57:
                # Numeric value. Jump to a fraction of the movie.
                v=0.1*(o-48)
                player.set_position(v)


# Not wrapped methods:
#    libvlc_get_version
#    libvlc_exception_get_message
#    libvlc_media_list_view_remove_at_index
#    libvlc_media_list_view_insert_at_index
#    libvlc_get_compiler
#    mediacontrol_RGBPicture__free
#    libvlc_free
#    libvlc_event_type_name
#    libvlc_get_vlc_instance
#    libvlc_media_list_view_add_item
#    libvlc_get_changeset
#    libvlc_exception_init
#    mediacontrol_exception_init
#    mediacontrol_exception_create
#    libvlc_new
#    mediacontrol_exception_cleanup
#    libvlc_exception_raise
#    mediacontrol_new
#    libvlc_media_list_view_index_of_item
#    libvlc_exception_raised
#    mediacontrol_StreamInformation__free
#    mediacontrol_PlaylistSeq__free
#    libvlc_exception_clear
#    mediacontrol_exception_free
