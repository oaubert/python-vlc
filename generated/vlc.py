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

build_date="Thu Apr 29 18:09:35 2010"

# Used for win32 and MacOS X
detected_plugin_path=None

if sys.platform == 'linux2':
    dll=ctypes.CDLL('libvlc.so.2')
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
        dll=ctypes.CDLL(d+'/Contents/MacOS/lib/libvlc.dylib')
        detected_plugin_path=d+'/Contents/MacOS/modules'
    else:
        # Hope some default path is set...
        dll=ctypes.CDLL('libvlc.dylib')

#
# Generated enum types.
#

class Event(ctypes.c_ulong):
    """*
Event types

    """
    _names={
        0: 'MediaMetaChanged',
        1: 'MediaSubItemAdded',
        2: 'MediaDurationChanged',
        3: 'MediaParsedChanged',
        4: 'MediaFreed',
        5: 'MediaStateChanged',
        0x100: 'MediaPlayerMediaChanged',
        257: 'MediaPlayerNothingSpecial',
        258: 'MediaPlayerOpening',
        259: 'MediaPlayerBuffering',
        260: 'MediaPlayerPlaying',
        261: 'MediaPlayerPaused',
        262: 'MediaPlayerStopped',
        263: 'MediaPlayerForward',
        264: 'MediaPlayerBackward',
        265: 'MediaPlayerEndReached',
        266: 'MediaPlayerEncounteredError',
        267: 'MediaPlayerTimeChanged',
        268: 'MediaPlayerPositionChanged',
        269: 'MediaPlayerSeekableChanged',
        270: 'MediaPlayerPausableChanged',
        271: 'MediaPlayerTitleChanged',
        272: 'MediaPlayerSnapshotTaken',
        273: 'MediaPlayerLengthChanged',
        0x200: 'MediaListItemAdded',
        513: 'MediaListWillAddItem',
        514: 'MediaListItemDeleted',
        515: 'MediaListWillDeleteItem',
        0x300: 'MediaListViewItemAdded',
        769: 'MediaListViewWillAddItem',
        770: 'MediaListViewItemDeleted',
        771: 'MediaListViewWillDeleteItem',
        0x400: 'MediaListPlayerPlayed',
        1025: 'MediaListPlayerNextItemSet',
        1026: 'MediaListPlayerStopped',
        0x500: 'MediaDiscovererStarted',
        1281: 'MediaDiscovererEnded',
        0x600: 'VlmMediaAdded',
        1537: 'VlmMediaRemoved',
        1538: 'VlmMediaChanged',
        1539: 'VlmMediaInstanceStarted',
        1540: 'VlmMediaInstanceStopped',
        1541: 'VlmMediaInstanceStatusInit',
        1542: 'VlmMediaInstanceStatusOpening',
        1543: 'VlmMediaInstanceStatusPlaying',
        1544: 'VlmMediaInstanceStatusPause',
        1545: 'VlmMediaInstanceStatusEnd',
        1546: 'VlmMediaInstanceStatusError',
    }

    def __repr__(self):
        return ".".join((self.__class__.__module__, self.__class__.__name__, self._names[self.value]))

    def __eq__(self, other):
        return ( (isinstance(other, ctypes.c_ulong) and self.value == other.value)
                 or (isinstance(other, (int, long)) and self.value == other ) )

    def __ne__(self, other):
        return not self.__eq__(other)
    
Event.MediaMetaChanged=Event(0)
Event.MediaSubItemAdded=Event(1)
Event.MediaDurationChanged=Event(2)
Event.MediaParsedChanged=Event(3)
Event.MediaFreed=Event(4)
Event.MediaStateChanged=Event(5)
Event.MediaPlayerMediaChanged=Event(0x100)
Event.MediaPlayerNothingSpecial=Event(257)
Event.MediaPlayerOpening=Event(258)
Event.MediaPlayerBuffering=Event(259)
Event.MediaPlayerPlaying=Event(260)
Event.MediaPlayerPaused=Event(261)
Event.MediaPlayerStopped=Event(262)
Event.MediaPlayerForward=Event(263)
Event.MediaPlayerBackward=Event(264)
Event.MediaPlayerEndReached=Event(265)
Event.MediaPlayerEncounteredError=Event(266)
Event.MediaPlayerTimeChanged=Event(267)
Event.MediaPlayerPositionChanged=Event(268)
Event.MediaPlayerSeekableChanged=Event(269)
Event.MediaPlayerPausableChanged=Event(270)
Event.MediaPlayerTitleChanged=Event(271)
Event.MediaPlayerSnapshotTaken=Event(272)
Event.MediaPlayerLengthChanged=Event(273)
Event.MediaListItemAdded=Event(0x200)
Event.MediaListWillAddItem=Event(513)
Event.MediaListItemDeleted=Event(514)
Event.MediaListWillDeleteItem=Event(515)
Event.MediaListViewItemAdded=Event(0x300)
Event.MediaListViewWillAddItem=Event(769)
Event.MediaListViewItemDeleted=Event(770)
Event.MediaListViewWillDeleteItem=Event(771)
Event.MediaListPlayerPlayed=Event(0x400)
Event.MediaListPlayerNextItemSet=Event(1025)
Event.MediaListPlayerStopped=Event(1026)
Event.MediaDiscovererStarted=Event(0x500)
Event.MediaDiscovererEnded=Event(1281)
Event.VlmMediaAdded=Event(0x600)
Event.VlmMediaRemoved=Event(1537)
Event.VlmMediaChanged=Event(1538)
Event.VlmMediaInstanceStarted=Event(1539)
Event.VlmMediaInstanceStopped=Event(1540)
Event.VlmMediaInstanceStatusInit=Event(1541)
Event.VlmMediaInstanceStatusOpening=Event(1542)
Event.VlmMediaInstanceStatusPlaying=Event(1543)
Event.VlmMediaInstanceStatusPause=Event(1544)
Event.VlmMediaInstanceStatusEnd=Event(1545)
Event.VlmMediaInstanceStatusError=Event(1546)

class Meta(ctypes.c_ulong):
    """* Meta data types */

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
    """*
Note the order of libvlc_state_t enum must match exactly the order of
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

class TrackType(ctypes.c_ulong):
    """
    """
    _names={
        -1: 'unknown',
        0: 'audio',
        1: 'video',
        2: 'text',
    }

    def __repr__(self):
        return ".".join((self.__class__.__module__, self.__class__.__name__, self._names[self.value]))

    def __eq__(self, other):
        return ( (isinstance(other, ctypes.c_ulong) and self.value == other.value)
                 or (isinstance(other, (int, long)) and self.value == other ) )

    def __ne__(self, other):
        return not self.__eq__(other)
    
TrackType.unknown=TrackType(-1)
TrackType.audio=TrackType(0)
TrackType.video=TrackType(1)
TrackType.text=TrackType(2)

class PlaybackMode(ctypes.c_ulong):
    """*
 Defines playback modes for playlist.

    """
    _names={
        0: 'default',
        1: 'loop',
        2: 'repeat',
    }

    def __repr__(self):
        return ".".join((self.__class__.__module__, self.__class__.__name__, self._names[self.value]))

    def __eq__(self, other):
        return ( (isinstance(other, ctypes.c_ulong) and self.value == other.value)
                 or (isinstance(other, (int, long)) and self.value == other ) )

    def __ne__(self, other):
        return not self.__eq__(other)
    
PlaybackMode.default=PlaybackMode(0)
PlaybackMode.loop=PlaybackMode(1)
PlaybackMode.repeat=PlaybackMode(2)

class VideoMarqueeOption(ctypes.c_ulong):
    """*
Marq options definition

    """
    _names={
        0: 'Enable',
        1: 'Text',
        2: 'Color',
        3: 'Opacity',
        4: 'Position',
        5: 'Refresh',
        6: 'Size',
        7: 'Timeout',
        8: 'marquee_X',
        9: 'marquee_Y',
    }

    def __repr__(self):
        return ".".join((self.__class__.__module__, self.__class__.__name__, self._names[self.value]))

    def __eq__(self, other):
        return ( (isinstance(other, ctypes.c_ulong) and self.value == other.value)
                 or (isinstance(other, (int, long)) and self.value == other ) )

    def __ne__(self, other):
        return not self.__eq__(other)
    
VideoMarqueeOption.Enable=VideoMarqueeOption(0)
VideoMarqueeOption.Text=VideoMarqueeOption(1)
VideoMarqueeOption.Color=VideoMarqueeOption(2)
VideoMarqueeOption.Opacity=VideoMarqueeOption(3)
VideoMarqueeOption.Position=VideoMarqueeOption(4)
VideoMarqueeOption.Refresh=VideoMarqueeOption(5)
VideoMarqueeOption.Size=VideoMarqueeOption(6)
VideoMarqueeOption.Timeout=VideoMarqueeOption(7)
VideoMarqueeOption.marquee_X=VideoMarqueeOption(8)
VideoMarqueeOption.marquee_Y=VideoMarqueeOption(9)

class VideoLogoOption(ctypes.c_ulong):
    """* option values for libvlc_video_{get,set}_logo_{int,string} */

    """
    _names={
        0: 'enable',
        1: 'file',
        2: 'logo_x',
        3: 'logo_y',
        4: 'delay',
        5: 'repeat',
        6: 'opacity',
        7: 'position',
    }

    def __repr__(self):
        return ".".join((self.__class__.__module__, self.__class__.__name__, self._names[self.value]))

    def __eq__(self, other):
        return ( (isinstance(other, ctypes.c_ulong) and self.value == other.value)
                 or (isinstance(other, (int, long)) and self.value == other ) )

    def __ne__(self, other):
        return not self.__eq__(other)
    
VideoLogoOption.enable=VideoLogoOption(0)
VideoLogoOption.file=VideoLogoOption(1)
VideoLogoOption.logo_x=VideoLogoOption(2)
VideoLogoOption.logo_y=VideoLogoOption(3)
VideoLogoOption.delay=VideoLogoOption(4)
VideoLogoOption.repeat=VideoLogoOption(5)
VideoLogoOption.opacity=VideoLogoOption(6)
VideoLogoOption.position=VideoLogoOption(7)

class AudioOutputDeviceTypes(ctypes.c_ulong):
    """*
Audio device types

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
    """*
Audio channels

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

class MediaTrackInfo(ctypes.Structure):
    _fields_= [
        ('codec'   , ctypes.c_uint32),
        ('id'      , ctypes.c_int),
        ('type'    , TrackType),
        ('profile' , ctypes.c_int),
        ('level'   , ctypes.c_int),
        ('channels_or_height',  ctypes.c_uint),
        ('rate_or_width'    , ctypes.c_uint),
        ]

    def __str__(self):
        return "MediaTrackInfo \n%s" % "\n".join( "%s:\t%s" % (n, getattr(self, n)) for n in self._fields_ )

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
@return: 0 on success, ENOMEM on error
        """
            return libvlc_event_attach(self, i_event_type, f_callback, user_data)

    if hasattr(dll, 'libvlc_event_detach'):
        def event_detach(self, i_event_type, f_callback, p_user_data):
            """Unregister an event notification.
@param i_event_type: the desired event to which we want to unregister
@param f_callback: the function to call when i_event_type occurs
        """
            return libvlc_event_detach(self, i_event_type, f_callback, p_user_data)

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
            return libvlc_new(len(p), p)

    def media_player_new(self, uri=None):
        """Create a new Media Player object.

        @param uri: an optional URI to play in the player.
        """
        p=libvlc_media_player_new(self)
        if uri:
            p.set_media(self.media_new(uri))
        p._instance=self
        return p

    def media_list_player_new(self):
        """Create an empty Media Player object
        """
        p=libvlc_media_list_player_new(self)
        p._instance=self
        return p

    def media_new(self, mrl, *options):
        """Create an empty Media Player object

        Options can be specified as supplementary string parameters, e.g.
        m=i.media_new('foo.avi', 'sub-filter=marq{marquee=Hello}', 'vout-filter=invert')
        """
        m=libvlc_media_new(self, mrl)
        for o in options:
            libvlc_media_add_option(m, o)
        return m


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
@return: 0 on success, -1 on error.
        """
            return libvlc_add_intf(self, name)

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
            return libvlc_get_log_verbosity(self)

    if hasattr(dll, 'libvlc_set_log_verbosity'):
        def set_log_verbosity(self, level):
            """Set the VLC messaging verbosity level.
        """
            return libvlc_set_log_verbosity(self, level)

    if hasattr(dll, 'libvlc_log_open'):
        def log_open(self):
            """Open a VLC message log instance.
@return: log message instance or NULL on error
        """
            return libvlc_log_open(self)

    if hasattr(dll, 'libvlc_media_discoverer_new_from_name'):
        def media_discoverer_new_from_name(self, psz_name):
            """Discover media service by name.
@return: media discover object or NULL in case of error
        """
            return libvlc_media_discoverer_new_from_name(self, psz_name)

    if hasattr(dll, 'libvlc_media_new_location'):
        def media_new_location(self, psz_mrl):
            """Create a media with a certain given media resource location.
\see libvlc_media_release
@return: the newly created media or NULL on error
        """
            return libvlc_media_new_location(self, psz_mrl)

    if hasattr(dll, 'libvlc_media_new_path'):
        def media_new_path(self, path):
            """Create a media with a certain file path.
\see libvlc_media_release
@return: the newly created media or NULL on error
        """
            return libvlc_media_new_path(self, path)

    if hasattr(dll, 'libvlc_media_new_as_node'):
        def media_new_as_node(self, psz_name):
            """Create a media as an empty node with a given name.
\see libvlc_media_release
@return: the new empty media or NULL on error
        """
            return libvlc_media_new_as_node(self, psz_name)

    if hasattr(dll, 'libvlc_media_library_new'):
        def media_library_new(self):
            """Create an new Media Library object
@return: a new object or NULL on error
        """
            return libvlc_media_library_new(self)

    if hasattr(dll, 'libvlc_media_list_new'):
        def media_list_new(self):
            """Create an empty media list.
@return: empty media list, or NULL on error
        """
            return libvlc_media_list_new(self)

    if hasattr(dll, 'libvlc_audio_output_list_get'):
        def audio_output_list_get(self):
            """Get the list of available audio outputs
@return: list of available audio outputs. It must be freed it with
        """
            return libvlc_audio_output_list_get(self)

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

    if hasattr(dll, 'libvlc_vlm_release'):
        def vlm_release(self):
            """Release the vlm instance related to the given libvlc_instance_t
        """
            return libvlc_vlm_release(self)

    if hasattr(dll, 'libvlc_vlm_add_broadcast'):
        def vlm_add_broadcast(self, psz_name, psz_input, psz_output, i_options,  ppsz_options, b_enabled, b_loop):
            """Add a broadcast, with one input.
@param psz_name: the name of the new broadcast
@param psz_input: the input MRL
@param psz_output: the output MRL (the parameter to the "sout" variable)
@param i_options: number of additional options
@param ppsz_options: additional options
@param b_enabled: boolean for enabling the new broadcast
@return: 0 on success, -1 on error
        """
            return libvlc_vlm_add_broadcast(self, psz_name, psz_input, psz_output, i_options,  ppsz_options, b_enabled, b_loop)

    if hasattr(dll, 'libvlc_vlm_add_vod'):
        def vlm_add_vod(self, psz_name, psz_input, i_options,  ppsz_options, b_enabled, psz_mux):
            """Add a vod, with one input.
@param psz_name: the name of the new vod media
@param psz_input: the input MRL
@param i_options: number of additional options
@param ppsz_options: additional options
@param b_enabled: boolean for enabling the new vod
@return: 0 on success, -1 on error
        """
            return libvlc_vlm_add_vod(self, psz_name, psz_input, i_options,  ppsz_options, b_enabled, psz_mux)

    if hasattr(dll, 'libvlc_vlm_del_media'):
        def vlm_del_media(self, psz_name):
            """Delete a media (VOD or broadcast).
@return: 0 on success, -1 on error
        """
            return libvlc_vlm_del_media(self, psz_name)

    if hasattr(dll, 'libvlc_vlm_set_enabled'):
        def vlm_set_enabled(self, psz_name, b_enabled):
            """Enable or disable a media (VOD or broadcast).
@param psz_name: the media to work on
@return: 0 on success, -1 on error
        """
            return libvlc_vlm_set_enabled(self, psz_name, b_enabled)

    if hasattr(dll, 'libvlc_vlm_set_output'):
        def vlm_set_output(self, psz_name, psz_output):
            """Set the output for a media.
@param psz_name: the media to work on
@return: 0 on success, -1 on error
        """
            return libvlc_vlm_set_output(self, psz_name, psz_output)

    if hasattr(dll, 'libvlc_vlm_set_input'):
        def vlm_set_input(self, psz_name, psz_input):
            """Set a media's input MRL. This will delete all existing inputs and
add the specified one.
@param psz_name: the media to work on
@return: 0 on success, -1 on error
        """
            return libvlc_vlm_set_input(self, psz_name, psz_input)

    if hasattr(dll, 'libvlc_vlm_add_input'):
        def vlm_add_input(self, psz_name, psz_input):
            """Add a media's input MRL. This will add the specified one.
@param psz_name: the media to work on
@return: 0 on success, -1 on error
        """
            return libvlc_vlm_add_input(self, psz_name, psz_input)

    if hasattr(dll, 'libvlc_vlm_set_loop'):
        def vlm_set_loop(self, psz_name, b_loop):
            """Set a media's loop status.
@param psz_name: the media to work on
@return: 0 on success, -1 on error
        """
            return libvlc_vlm_set_loop(self, psz_name, b_loop)

    if hasattr(dll, 'libvlc_vlm_set_mux'):
        def vlm_set_mux(self, psz_name, psz_mux):
            """Set a media's vod muxer.
@param psz_name: the media to work on
@return: 0 on success, -1 on error
        """
            return libvlc_vlm_set_mux(self, psz_name, psz_mux)

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
@return: 0 on success, -1 on error
        """
            return libvlc_vlm_change_media(self, psz_name, psz_input, psz_output, i_options, ppsz_options, b_enabled, b_loop)

    if hasattr(dll, 'libvlc_vlm_play_media'):
        def vlm_play_media(self, psz_name):
            """Play the named broadcast.
@return: 0 on success, -1 on error
        """
            return libvlc_vlm_play_media(self, psz_name)

    if hasattr(dll, 'libvlc_vlm_stop_media'):
        def vlm_stop_media(self, psz_name):
            """Stop the named broadcast.
@return: 0 on success, -1 on error
        """
            return libvlc_vlm_stop_media(self, psz_name)

    if hasattr(dll, 'libvlc_vlm_pause_media'):
        def vlm_pause_media(self, psz_name):
            """Pause the named broadcast.
@return: 0 on success, -1 on error
        """
            return libvlc_vlm_pause_media(self, psz_name)

    if hasattr(dll, 'libvlc_vlm_seek_media'):
        def vlm_seek_media(self, psz_name, f_percentage):
            """Seek in the named broadcast.
@param psz_name: the name of the broadcast
@return: 0 on success, -1 on error
        """
            return libvlc_vlm_seek_media(self, psz_name, f_percentage)

    if hasattr(dll, 'libvlc_vlm_show_media'):
        def vlm_show_media(self, psz_name):
            """Return information about the named media as a JSON
string representation.
This function is mainly intended for debugging use,
if you want programmatic access to the state of
a vlm_media_instance_t, please use the corresponding
libvlc_vlm_get_media_instance_xxx -functions.
Currently there are no such functions available for
vlm_media_t though.
@return: string with information about named media, or NULL on error
        """
            return libvlc_vlm_show_media(self, psz_name)

    if hasattr(dll, 'libvlc_vlm_get_media_instance_position'):
        def vlm_get_media_instance_position(self, psz_name, i_instance):
            """Get vlm_media instance position by name or instance id
@param psz_name: name of vlm media instance
@return: position as float or -1. on error
        """
            return libvlc_vlm_get_media_instance_position(self, psz_name, i_instance)

    if hasattr(dll, 'libvlc_vlm_get_media_instance_time'):
        def vlm_get_media_instance_time(self, psz_name, i_instance):
            """Get vlm_media instance time by name or instance id
@param psz_name: name of vlm media instance
@return: time as integer or -1 on error
        """
            return libvlc_vlm_get_media_instance_time(self, psz_name, i_instance)

    if hasattr(dll, 'libvlc_vlm_get_media_instance_length'):
        def vlm_get_media_instance_length(self, psz_name, i_instance):
            """Get vlm_media instance length by name or instance id
@param psz_name: name of vlm media instance
@return: length of media item or -1 on error
        """
            return libvlc_vlm_get_media_instance_length(self, psz_name, i_instance)

    if hasattr(dll, 'libvlc_vlm_get_media_instance_rate'):
        def vlm_get_media_instance_rate(self, psz_name, i_instance):
            """Get vlm_media instance playback rate by name or instance id
@param psz_name: name of vlm media instance
@return: playback rate or -1 on error
        """
            return libvlc_vlm_get_media_instance_rate(self, psz_name, i_instance)

    if hasattr(dll, 'libvlc_vlm_get_media_instance_title'):
        def vlm_get_media_instance_title(self, psz_name, i_instance):
            """Get vlm_media instance title number by name or instance id
\bug will always return 0
@param psz_name: name of vlm media instance
@return: title as number or -1 on error
        """
            return libvlc_vlm_get_media_instance_title(self, psz_name, i_instance)

    if hasattr(dll, 'libvlc_vlm_get_media_instance_chapter'):
        def vlm_get_media_instance_chapter(self, psz_name, i_instance):
            """Get vlm_media instance chapter number by name or instance id
\bug will always return 0
@param psz_name: name of vlm media instance
@return: chapter as number or -1 on error
        """
            return libvlc_vlm_get_media_instance_chapter(self, psz_name, i_instance)

    if hasattr(dll, 'libvlc_vlm_get_media_instance_seekable'):
        def vlm_get_media_instance_seekable(self, psz_name, i_instance):
            """Is libvlc instance seekable ?
\bug will always return 0
@param psz_name: name of vlm media instance
@return: 1 if seekable, 0 if not, -1 if media does not exist
        """
            return libvlc_vlm_get_media_instance_seekable(self, psz_name, i_instance)

    if hasattr(dll, 'libvlc_vlm_get_event_manager'):
        def vlm_get_event_manager(self):
            """Get libvlc_event_manager from a vlm media.
The p_event_manager is immutable, so you don't have to hold the lock
@return: libvlc_event_manager
        """
            return libvlc_vlm_get_event_manager(self)

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
            return libvlc_log_close(self)

    if hasattr(dll, 'libvlc_log_count'):
        def count(self):
            """Returns the number of messages in a log instance.
@return: number of log messages, 0 if p_log is NULL
        """
            return libvlc_log_count(self)

    def __len__(self):
        return libvlc_log_count(self)

    if hasattr(dll, 'libvlc_log_clear'):
        def clear(self):
            """Clear a log instance.
All messages in the log are removed. The log should be cleared on a
regular basis to avoid clogging.
        """
            return libvlc_log_clear(self)

    if hasattr(dll, 'libvlc_log_get_iterator'):
        def get_iterator(self):
            """Allocate and returns a new iterator to messages in log.
@return: log iterator object or NULL on error
        """
            return libvlc_log_get_iterator(self)

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
        ret=libvlc_log_iterator_next(self, buf)
        return ret.contents


    if hasattr(dll, 'libvlc_log_iterator_free'):
        def free(self):
            """Release a previoulsy allocated iterator.
        """
            return libvlc_log_iterator_free(self)

    if hasattr(dll, 'libvlc_log_iterator_has_next'):
        def has_next(self):
            """Return whether log iterator has more messages.
@return: true if iterator has more message objects, else false
        """
            return libvlc_log_iterator_has_next(self)

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
        """
            return libvlc_media_add_option(self, ppsz_options)

    if hasattr(dll, 'libvlc_media_add_option_flag'):
        def add_option_flag(self, ppsz_options, i_flags):
            """Add an option to the media with configurable flags.
This option will be used to determine how the media_player will
read the media. This allows to use VLC's advanced
reading/streaming options on a per-media basis.
The options are detailed in vlc --long-help, for instance "--sout-all"
@param ppsz_options: the options (as a string)
        """
            return libvlc_media_add_option_flag(self, ppsz_options, i_flags)

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
            return libvlc_media_get_mrl(self)

    if hasattr(dll, 'libvlc_media_duplicate'):
        def duplicate(self):
            """Duplicate a media descriptor object.
        """
            return libvlc_media_duplicate(self)

    if hasattr(dll, 'libvlc_media_get_meta'):
        def get_meta(self, e_meta):
            """Read the meta of the media.
If the media has not yet been parsed this will return NULL.
This methods automatically calls libvlc_media_parse_async(), so after calling
it you may receive a libvlc_MediaMetaChanged event. If you prefer a synchronous
version ensure that you call libvlc_media_parse() before get_meta().
\see libvlc_media_parse
\see libvlc_media_parse_async
\see libvlc_MediaMetaChanged
@return: the media's meta
        """
            return libvlc_media_get_meta(self, e_meta)

    if hasattr(dll, 'libvlc_media_set_meta'):
        def set_meta(self, e_meta, psz_value):
            """Set the meta of the media (this function will not save the meta, call
libvlc_media_save_meta in order to save the meta)
@param e_meta: the meta to write
        """
            return libvlc_media_set_meta(self, e_meta, psz_value)

    if hasattr(dll, 'libvlc_media_save_meta'):
        def save_meta(self):
            """Save the meta previously set
@return: true if the write operation was successfull
        """
            return libvlc_media_save_meta(self)

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
            return libvlc_media_get_state(self)

    if hasattr(dll, 'libvlc_media_get_stats'):
        def get_stats(self, p_stats):
            """get the current statistics about the media
@return: true if the statistics are available, false otherwise
        """
            return libvlc_media_get_stats(self, p_stats)

    if hasattr(dll, 'libvlc_media_subitems'):
        def subitems(self):
            """Get subitems of media descriptor object. This will increment
the reference count of supplied media descriptor object. Use
libvlc_media_list_release() to decrement the reference counting.
@return: list of media descriptor subitems or NULL
        """
            return libvlc_media_subitems(self)

    if hasattr(dll, 'libvlc_media_event_manager'):
        def event_manager(self):
            """Get event manager from media descriptor object.
NOTE: this function doesn't increment reference counting.
@return: event manager object
        """
            return libvlc_media_event_manager(self)

    if hasattr(dll, 'libvlc_media_get_duration'):
        def get_duration(self):
            """Get duration (in ms) of media descriptor object item.
@return: duration of media item or -1 on error
        """
            return libvlc_media_get_duration(self)

    if hasattr(dll, 'libvlc_media_parse'):
        def parse(self):
            """Parse a media.
This fetches (local) meta data and tracks information.
The method is synchronous.
\see libvlc_media_parse_async
\see libvlc_media_get_meta
\see libvlc_media_get_tracks_info
        """
            return libvlc_media_parse(self)

    if hasattr(dll, 'libvlc_media_parse_async'):
        def parse_async(self):
            """Parse a media.
This fetches (local) meta data and tracks information.
The method is the asynchronous of libvlc_media_parse_async().
To track when this is over you can listen to libvlc_MediaParsedChanged
event. However if the media was already parsed you will not receive this
event.
\see libvlc_media_parse
\see libvlc_MediaParsedChanged
\see libvlc_media_get_meta
\see libvlc_media_get_tracks_info
        """
            return libvlc_media_parse_async(self)

    if hasattr(dll, 'libvlc_media_is_parsed'):
        def is_parsed(self):
            """Get Parsed status for media descriptor object.
\see libvlc_MediaParsedChanged
@return: true if media object has been parsed otherwise it returns false
        """
            return libvlc_media_is_parsed(self)

    if hasattr(dll, 'libvlc_media_set_user_data'):
        def set_user_data(self, p_new_user_data):
            """Sets media descriptor's user_data. user_data is specialized data
accessed by the host application, VLC.framework uses it as a pointer to
an native object that references a libvlc_media_t pointer
        """
            return libvlc_media_set_user_data(self, p_new_user_data)

    if hasattr(dll, 'libvlc_media_get_user_data'):
        def get_user_data(self):
            """Get media descriptor's user_data. user_data is specialized data
accessed by the host application, VLC.framework uses it as a pointer to
an native object that references a libvlc_media_t pointer
        """
            return libvlc_media_get_user_data(self)

    if hasattr(dll, 'libvlc_media_get_tracks_info'):
        def get_tracks_info(self, tracks):
            """Get media descriptor's elementary streams description
Note, you need to play the media _one_ time with --sout="#description"
Not doing this will result in an empty array, and doing it more than once
will duplicate the entries in the array each time. Something like this:
@begincode
libvlc_media_player_t *player = libvlc_media_player_new_from_media(media);
libvlc_media_add_option_flag(media, "sout=\"#description\"");
libvlc_media_player_play(player);
// ... wait until playing
libvlc_media_player_release(player);
@endcode
This is very likely to change in next release, and be done at the parsing
phase.
        """
            return libvlc_media_get_tracks_info(self, tracks)

    if hasattr(dll, 'libvlc_media_player_new_from_media'):
        def player_new_from_media(self):
            """Create a Media Player object from a Media
@return: a new media player object, or NULL on error.
        """
            return libvlc_media_player_new_from_media(self)

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
@return: 0 on success, -1 on error
        """
            return libvlc_media_library_load(self)

    if hasattr(dll, 'libvlc_media_library_media_list'):
        def media_list(self):
            """Get media library subitems.
@return: media list subitems
        """
            return libvlc_media_library_media_list(self)

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
        def set_media(self, p_md):
            """Associate media instance with this media list instance.
If another media instance was present it will be released.
The libvlc_media_list_lock should NOT be held upon entering this function.
        """
            return libvlc_media_list_set_media(self, p_md)

    if hasattr(dll, 'libvlc_media_list_media'):
        def media(self):
            """Get media instance from this media list instance. This action will increase
the refcount on the media instance.
The libvlc_media_list_lock should NOT be held upon entering this function.
@return: media instance
        """
            return libvlc_media_list_media(self)

    if hasattr(dll, 'libvlc_media_list_add_media'):
        def add_media(self, p_md):
            """Add media instance to media list
The libvlc_media_list_lock should be held upon entering this function.
@return: 0 on success, -1 if the media list is read-only
        """
            return libvlc_media_list_add_media(self, p_md)

    if hasattr(dll, 'libvlc_media_list_insert_media'):
        def insert_media(self, p_md, i_pos):
            """Insert media instance in media list on a position
The libvlc_media_list_lock should be held upon entering this function.
@param p_md: a media instance
@return: 0 on success, -1 if the media list si read-only
        """
            return libvlc_media_list_insert_media(self, p_md, i_pos)

    if hasattr(dll, 'libvlc_media_list_remove_index'):
        def remove_index(self, i_pos):
            """Remove media instance from media list on a position
The libvlc_media_list_lock should be held upon entering this function.
@return: 0 on success, -1 if the list is read-only or the item was not found
        """
            return libvlc_media_list_remove_index(self, i_pos)

    if hasattr(dll, 'libvlc_media_list_count'):
        def count(self):
            """Get count on media list items
The libvlc_media_list_lock should be held upon entering this function.
@return: number of items in media list
        """
            return libvlc_media_list_count(self)

    def __len__(self):
        return libvlc_media_list_count(self)

    if hasattr(dll, 'libvlc_media_list_item_at_index'):
        def item_at_index(self, i_pos):
            """List media instance in media list at a position
The libvlc_media_list_lock should be held upon entering this function.
@return: media instance at position i_pos, or NULL if not found.
        """
            return libvlc_media_list_item_at_index(self, i_pos)

    def __getitem__(self, i):
        e=VLCException()
        return libvlc_media_list_item_at_index(self, i, e)

    def __iter__(self):
        e=VLCException()
        for i in xrange(len(self)):
            yield self[i]

    if hasattr(dll, 'libvlc_media_list_index_of_item'):
        def index_of_item(self, p_md):
            """Find index position of List media instance in media list.
Warning: the function will return the first matched position.
The libvlc_media_list_lock should be held upon entering this function.
@return: position of media instance
        """
            return libvlc_media_list_index_of_item(self, p_md)

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

    if hasattr(dll, 'libvlc_media_list_event_manager'):
        def event_manager(self):
            """Get libvlc_event_manager from this media list instance.
The p_event_manager is immutable, so you don't have to hold the lock
@return: libvlc_event_manager
        """
            return libvlc_media_list_event_manager(self)

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

    if hasattr(dll, 'libvlc_media_list_player_event_manager'):
        def event_manager(self):
            """Return the event manager of this media_list_player.
@return: the event manager
        """
            return libvlc_media_list_player_event_manager(self)

    if hasattr(dll, 'libvlc_media_list_player_set_media_player'):
        def set_media_player(self, p_mi):
            """Replace media player in media_list_player with this instance.
        """
            return libvlc_media_list_player_set_media_player(self, p_mi)

    if hasattr(dll, 'libvlc_media_list_player_set_media_list'):
        def set_media_list(self, p_mlist):
            """Set the media list associated with the player
        """
            return libvlc_media_list_player_set_media_list(self, p_mlist)

    if hasattr(dll, 'libvlc_media_list_player_play'):
        def play(self):
            """Play media list
        """
            return libvlc_media_list_player_play(self)

    if hasattr(dll, 'libvlc_media_list_player_pause'):
        def pause(self):
            """Pause media list
        """
            return libvlc_media_list_player_pause(self)

    if hasattr(dll, 'libvlc_media_list_player_is_playing'):
        def is_playing(self):
            """Is media list playing?
@return: true for playing and false for not playing
        """
            return libvlc_media_list_player_is_playing(self)

    if hasattr(dll, 'libvlc_media_list_player_get_state'):
        def get_state(self):
            """Get current libvlc_state of media list player
@return: libvlc_state_t for media list player
        """
            return libvlc_media_list_player_get_state(self)

    if hasattr(dll, 'libvlc_media_list_player_play_item_at_index'):
        def play_item_at_index(self, i_index):
            """Play media list item at position index
@return: 0 upon success -1 if the item wasn't found
        """
            return libvlc_media_list_player_play_item_at_index(self, i_index)

    def __getitem__(self, i):
        e=VLCException()
        return libvlc_media_list_player_play_item_at_index(self, i, e)

    def __iter__(self):
        e=VLCException()
        for i in xrange(len(self)):
            yield self[i]

    if hasattr(dll, 'libvlc_media_list_player_play_item'):
        def play_item(self, p_md):
            """Play the given media item
@return: 0 upon success, -1 if the media is not part of the media list
        """
            return libvlc_media_list_player_play_item(self, p_md)

    if hasattr(dll, 'libvlc_media_list_player_stop'):
        def stop(self):
            """Stop playing media list
        """
            return libvlc_media_list_player_stop(self)

    if hasattr(dll, 'libvlc_media_list_player_next'):
        def next(self):
            """Play next item from media list
@return: 0 upon success -1 if there is no next item
        """
            return libvlc_media_list_player_next(self)

    if hasattr(dll, 'libvlc_media_list_player_previous'):
        def previous(self):
            """Play previous item from media list
@return: 0 upon success -1 if there is no previous item
        """
            return libvlc_media_list_player_previous(self)

    if hasattr(dll, 'libvlc_media_list_player_set_playback_mode'):
        def set_playback_mode(self, e_mode):
            """Sets the playback mode for the playlist
        """
            return libvlc_media_list_player_set_playback_mode(self, e_mode)

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
        """
            return libvlc_media_player_set_media(self, p_md)

    if hasattr(dll, 'libvlc_media_player_get_media'):
        def get_media(self):
            """Get the media used by the media_player.
@return: the media associated with p_mi, or NULL if no
        """
            return libvlc_media_player_get_media(self)

    if hasattr(dll, 'libvlc_media_player_event_manager'):
        def event_manager(self):
            """Get the Event Manager from which the media player send event.
@return: the event manager associated with p_mi
        """
            return libvlc_media_player_event_manager(self)

    if hasattr(dll, 'libvlc_media_player_is_playing'):
        def is_playing(self):
            """is_playing
@return: 1 if the media player is playing, 0 otherwise
        """
            return libvlc_media_player_is_playing(self)

    if hasattr(dll, 'libvlc_media_player_play'):
        def play(self):
            """Play
@return: 0 if playback started (and was already started), or -1 on error.
        """
            return libvlc_media_player_play(self)

    if hasattr(dll, 'libvlc_media_player_pause'):
        def pause(self):
            """Toggle pause (no effect if there is no media)
        """
            return libvlc_media_player_pause(self)

    if hasattr(dll, 'libvlc_media_player_stop'):
        def stop(self):
            """Stop (no effect if there is no media)
        """
            return libvlc_media_player_stop(self)

    if hasattr(dll, 'libvlc_media_player_set_nsobject'):
        def set_nsobject(self, drawable):
            """Set the NSView handler where the media player should render its video output.
Use the vout called "macosx".
The drawable is an NSObject that follow the VLCOpenGLVideoViewEmbedding
protocol:
@begincode
\@protocol VLCOpenGLVideoViewEmbedding <NSObject>
- (void)addVoutSubview:(NSView *)view;
- (void)removeVoutSubview:(NSView *)view;
\@end
@endcode
Or it can be an NSView object.
If you want to use it along with Qt4 see the QMacCocoaViewContainer. Then
the following code should work:
@begincode
{
    NSView *video = [[NSView alloc] init];
    QMacCocoaViewContainer *container = new QMacCocoaViewContainer(video, parent);
    libvlc_media_player_set_nsobject(mp, video);
    [video release];
}
@endcode
You can find a live example in VLCVideoView in VLCKit.framework.
        """
            return libvlc_media_player_set_nsobject(self, drawable)

    if hasattr(dll, 'libvlc_media_player_get_nsobject'):
        def get_nsobject(self):
            """Get the NSView handler previously set with libvlc_media_player_set_nsobject().
@return: the NSView handler or 0 if none where set
        """
            return libvlc_media_player_get_nsobject(self)

    if hasattr(dll, 'libvlc_media_player_set_agl'):
        def set_agl(self, drawable):
            """Set the agl handler where the media player should render its video output.
        """
            return libvlc_media_player_set_agl(self, drawable)

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
        """
            return libvlc_media_player_set_xwindow(self, drawable)

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
        """
            return libvlc_media_player_set_hwnd(self, drawable)

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
@return: the movie length (in ms), or -1 if there is no media.
        """
            return libvlc_media_player_get_length(self)

    if hasattr(dll, 'libvlc_media_player_get_time'):
        def get_time(self):
            """Get the current movie time (in ms).
@return: the movie time (in ms), or -1 if there is no media.
        """
            return libvlc_media_player_get_time(self)

    if hasattr(dll, 'libvlc_media_player_set_time'):
        def set_time(self, i_time):
            """Set the movie time (in ms). This has no effect if no media is being played.
Not all formats and protocols support this.
        """
            return libvlc_media_player_set_time(self, i_time)

    if hasattr(dll, 'libvlc_media_player_get_position'):
        def get_position(self):
            """Get movie position.
@return: movie position, or -1. in case of error
        """
            return libvlc_media_player_get_position(self)

    if hasattr(dll, 'libvlc_media_player_set_position'):
        def set_position(self, f_pos):
            """Set movie position. This has no effect if playback is not enabled.
This might not work depending on the underlying input format and protocol.
        """
            return libvlc_media_player_set_position(self, f_pos)

    if hasattr(dll, 'libvlc_media_player_set_chapter'):
        def set_chapter(self, i_chapter):
            """Set movie chapter (if applicable).
        """
            return libvlc_media_player_set_chapter(self, i_chapter)

    if hasattr(dll, 'libvlc_media_player_get_chapter'):
        def get_chapter(self):
            """Get movie chapter.
@return: chapter number currently playing, or -1 if there is no media.
        """
            return libvlc_media_player_get_chapter(self)

    if hasattr(dll, 'libvlc_media_player_get_chapter_count'):
        def get_chapter_count(self):
            """Get movie chapter count
@return: number of chapters in movie, or -1.
        """
            return libvlc_media_player_get_chapter_count(self)

    if hasattr(dll, 'libvlc_media_player_will_play'):
        def will_play(self):
            """Is the player able to play
@return: boolean
        """
            return libvlc_media_player_will_play(self)

    if hasattr(dll, 'libvlc_media_player_get_chapter_count_for_title'):
        def get_chapter_count_for_title(self, i_title):
            """Get title chapter count
@return: number of chapters in title, or -1
        """
            return libvlc_media_player_get_chapter_count_for_title(self, i_title)

    if hasattr(dll, 'libvlc_media_player_set_title'):
        def set_title(self, i_title):
            """Set movie title
        """
            return libvlc_media_player_set_title(self, i_title)

    if hasattr(dll, 'libvlc_media_player_get_title'):
        def get_title(self):
            """Get movie title
@return: title number currently playing, or -1
        """
            return libvlc_media_player_get_title(self)

    if hasattr(dll, 'libvlc_media_player_get_title_count'):
        def get_title_count(self):
            """Get movie title count
@return: title number count, or -1
        """
            return libvlc_media_player_get_title_count(self)

    if hasattr(dll, 'libvlc_media_player_previous_chapter'):
        def previous_chapter(self):
            """Set previous chapter (if applicable)
        """
            return libvlc_media_player_previous_chapter(self)

    if hasattr(dll, 'libvlc_media_player_next_chapter'):
        def next_chapter(self):
            """Set next chapter (if applicable)
        """
            return libvlc_media_player_next_chapter(self)

    if hasattr(dll, 'libvlc_media_player_get_rate'):
        def get_rate(self):
            """Get the requested movie play rate.
@warning Depending on the underlying media, the requested rate may be
different from the real playback rate.
@return: movie play rate
        """
            return libvlc_media_player_get_rate(self)

    if hasattr(dll, 'libvlc_media_player_set_rate'):
        def set_rate(self, rate):
            """Set movie play rate
@return: -1 if an error was detected, 0 otherwise (but even then, it might
        """
            return libvlc_media_player_set_rate(self, rate)

    if hasattr(dll, 'libvlc_media_player_get_state'):
        def get_state(self):
            """Get current movie state
@return: the current state of the media player (playing, paused, ...) \see libvlc_state_t
        """
            return libvlc_media_player_get_state(self)

    if hasattr(dll, 'libvlc_media_player_get_fps'):
        def get_fps(self):
            """Get movie fps rate
@return: frames per second (fps) for this playing movie, or 0 if unspecified
        """
            return libvlc_media_player_get_fps(self)

    if hasattr(dll, 'libvlc_media_player_has_vout'):
        def has_vout(self):
            """How many video outputs does this media player have?
@return: the number of video outputs
        """
            return libvlc_media_player_has_vout(self)

    if hasattr(dll, 'libvlc_media_player_is_seekable'):
        def is_seekable(self):
            """Is this media player seekable?
@return: true if the media player can seek
        """
            return libvlc_media_player_is_seekable(self)

    if hasattr(dll, 'libvlc_media_player_can_pause'):
        def can_pause(self):
            """Can this media player be paused?
@return: true if the media player can pause
        """
            return libvlc_media_player_can_pause(self)

    if hasattr(dll, 'libvlc_media_player_next_frame'):
        def next_frame(self):
            """Display the next frame (if supported)
        """
            return libvlc_media_player_next_frame(self)

    if hasattr(dll, 'libvlc_toggle_fullscreen'):
        def toggle_fullscreen(self):
            """Toggle fullscreen status on non-embedded video outputs.
@warning The same limitations applies to this function
as to libvlc_set_fullscreen().
        """
            return libvlc_toggle_fullscreen(self)

    if hasattr(dll, 'libvlc_set_fullscreen'):
        def set_fullscreen(self, b_fullscreen):
            """Enable or disable fullscreen.
@warning With most window managers, only a top-level windows can be in
full-screen mode. Hence, this function will not operate properly if
libvlc_media_player_set_xid() was used to embed the video in a non-top-level
window. In that case, the embedding window must be reparented to the root
window <b>before</b> fullscreen mode is enabled. You will want to reparent
it back to its normal parent when disabling fullscreen.
        """
            return libvlc_set_fullscreen(self, b_fullscreen)

    if hasattr(dll, 'libvlc_get_fullscreen'):
        def get_fullscreen(self):
            """Get current fullscreen status.
@return: the fullscreen status (boolean)
        """
            return libvlc_get_fullscreen(self)

    if hasattr(dll, 'libvlc_video_set_key_input'):
        def video_set_key_input(self, on):
            """Enable or disable key press events handling, according to the LibVLC hotkeys
configuration. By default and for historical reasons, keyboard events are
handled by the LibVLC video widget.
\note On X11, there can be only one subscriber for key press and mouse
click events per window. If your application has subscribed to those events
for the X window ID of the video widget, then LibVLC will not be able to
handle key presses and mouse clicks in any case.
\warning This function is only implemented for X11 at the moment.
        """
            return libvlc_video_set_key_input(self, on)

    if hasattr(dll, 'libvlc_video_set_mouse_input'):
        def video_set_mouse_input(self, on):
            """Enable or disable mouse click events handling. By default, those events are
handled. This is needed for DVD menus to work, as well as a few video
filters such as "puzzle".
\note See also libvlc_video_set_key_input().
\warning This function is only implemented for X11 at the moment.
        """
            return libvlc_video_set_mouse_input(self, on)

    if hasattr(dll, 'libvlc_video_get_size'):
        def video_get_size(self, num, px, py):
            """Get the pixel dimensions of a video.
@param num: number of the video (starting from, and most commonly 0)
@param px: pointer to get the pixel width [OUT]
@return: 0 on success, -1 if the specified video does not exist
        """
            return libvlc_video_get_size(self, num, px, py)

    if hasattr(dll, 'libvlc_video_get_cursor'):
        def video_get_cursor(self, num, px, py):
            """Get the mouse pointer coordinates over a video.
Coordinates are expressed in terms of the decoded video resolution,
<b>not</b> in terms of pixels on the screen/viewport (to get the latter,
you can query your windowing system directly).
Either of the coordinates may be negative or larger than the corresponding
dimension of the video, if the cursor is outside the rendering area.
@warning The coordinates may be out-of-date if the pointer is not located
on the video rendering area. LibVLC does not track the pointer if it is
outside of the video widget.
@note LibVLC does not support multiple pointers (it does of course support
multiple input devices sharing the same pointer) at the moment.
@param num: number of the video (starting from, and most commonly 0)
@param px: pointer to get the abscissa [OUT]
@return: 0 on success, -1 if the specified video does not exist
        """
            return libvlc_video_get_cursor(self, num, px, py)

    if hasattr(dll, 'libvlc_video_get_scale'):
        def video_get_scale(self):
            """Get the current video scaling factor.
See also libvlc_video_set_scale().
@return: the currently configured zoom factor, or 0. if the video is set
        """
            return libvlc_video_get_scale(self)

    if hasattr(dll, 'libvlc_video_set_scale'):
        def video_set_scale(self, f_factor):
            """Set the video scaling factor. That is the ratio of the number of pixels on
screen to the number of pixels in the original decoded video in each
dimension. Zero is a special value; it will adjust the video to the output
window/drawable (in windowed mode) or the entire screen.
Note that not all video outputs support scaling.
        """
            return libvlc_video_set_scale(self, f_factor)

    if hasattr(dll, 'libvlc_video_get_aspect_ratio'):
        def video_get_aspect_ratio(self):
            """Get current video aspect ratio.
@return: the video aspect ratio or NULL if unspecified
        """
            return libvlc_video_get_aspect_ratio(self)

    if hasattr(dll, 'libvlc_video_set_aspect_ratio'):
        def video_set_aspect_ratio(self, psz_aspect):
            """Set new video aspect ratio.
        """
            return libvlc_video_set_aspect_ratio(self, psz_aspect)

    if hasattr(dll, 'libvlc_video_get_spu'):
        def video_get_spu(self):
            """Get current video subtitle.
@return: the video subtitle selected, or -1 if none
        """
            return libvlc_video_get_spu(self)

    if hasattr(dll, 'libvlc_video_get_spu_count'):
        def video_get_spu_count(self):
            """Get the number of available video subtitles.
@return: the number of available video subtitles
        """
            return libvlc_video_get_spu_count(self)

    if hasattr(dll, 'libvlc_video_get_spu_description'):
        def video_get_spu_description(self):
            """Get the description of available video subtitles.
@return: list containing description of available video subtitles
        """
            return libvlc_video_get_spu_description(self)

    if hasattr(dll, 'libvlc_video_set_spu'):
        def video_set_spu(self, i_spu):
            """Set new video subtitle.
@return: 0 on success, -1 if out of range
        """
            return libvlc_video_set_spu(self, i_spu)

    if hasattr(dll, 'libvlc_video_set_subtitle_file'):
        def video_set_subtitle_file(self, psz_subtitle):
            """Set new video subtitle file.
@return: the success status (boolean)
        """
            return libvlc_video_set_subtitle_file(self, psz_subtitle)

    if hasattr(dll, 'libvlc_video_get_title_description'):
        def video_get_title_description(self):
            """Get the description of available titles.
@return: list containing description of available titles
        """
            return libvlc_video_get_title_description(self)

    if hasattr(dll, 'libvlc_video_get_chapter_description'):
        def video_get_chapter_description(self, i_title):
            """Get the description of available chapters for specific title.
@return: list containing description of available chapter for title i_title
        """
            return libvlc_video_get_chapter_description(self, i_title)

    if hasattr(dll, 'libvlc_video_get_crop_geometry'):
        def video_get_crop_geometry(self):
            """Get current crop filter geometry.
@return: the crop filter geometry or NULL if unset
        """
            return libvlc_video_get_crop_geometry(self)

    if hasattr(dll, 'libvlc_video_set_crop_geometry'):
        def video_set_crop_geometry(self, psz_geometry):
            """Set new crop filter geometry.
        """
            return libvlc_video_set_crop_geometry(self, psz_geometry)

    if hasattr(dll, 'libvlc_video_get_teletext'):
        def video_get_teletext(self):
            """Get current teletext page requested.
@return: the current teletext page requested.
        """
            return libvlc_video_get_teletext(self)

    if hasattr(dll, 'libvlc_video_set_teletext'):
        def video_set_teletext(self, i_page):
            """Set new teletext page to retrieve.
        """
            return libvlc_video_set_teletext(self, i_page)

    if hasattr(dll, 'libvlc_toggle_teletext'):
        def toggle_teletext(self):
            """Toggle teletext transparent status on video output.
        """
            return libvlc_toggle_teletext(self)

    if hasattr(dll, 'libvlc_video_get_track_count'):
        def video_get_track_count(self):
            """Get number of available video tracks.
@return: the number of available video tracks (int)
        """
            return libvlc_video_get_track_count(self)

    if hasattr(dll, 'libvlc_video_get_track_description'):
        def video_get_track_description(self):
            """Get the description of available video tracks.
@return: list with description of available video tracks, or NULL on error
        """
            return libvlc_video_get_track_description(self)

    if hasattr(dll, 'libvlc_video_get_track'):
        def video_get_track(self):
            """Get current video track.
@return: the video track (int) or -1 if none
        """
            return libvlc_video_get_track(self)

    if hasattr(dll, 'libvlc_video_set_track'):
        def video_set_track(self, i_track):
            """Set video track.
@return: 0 on success, -1 if out of range
        """
            return libvlc_video_set_track(self, i_track)

    if hasattr(dll, 'libvlc_video_take_snapshot'):
        def video_take_snapshot(self, num, psz_filepath, i_width, i_height):
            """Take a snapshot of the current video window.
If i_width AND i_height is 0, original size is used.
If i_width XOR i_height is 0, original aspect-ratio is preserved.
@param num: number of video output (typically 0 for the first/only one)
@param psz_filepath: the path where to save the screenshot to
@param i_width: the snapshot's width
@return: 0 on success, -1 if the video was not found
        """
            return libvlc_video_take_snapshot(self, num, psz_filepath, i_width, i_height)

    if hasattr(dll, 'libvlc_video_set_deinterlace'):
        def video_set_deinterlace(self, psz_mode):
            """Enable or disable deinterlace filter
        """
            return libvlc_video_set_deinterlace(self, psz_mode)

    if hasattr(dll, 'libvlc_video_get_marquee_int'):
        def video_get_marquee_int(self, option):
            """Get an integer marquee option value
        """
            return libvlc_video_get_marquee_int(self, option)

    if hasattr(dll, 'libvlc_video_get_marquee_string'):
        def video_get_marquee_string(self, option):
            """Get a string marquee option value
        """
            return libvlc_video_get_marquee_string(self, option)

    if hasattr(dll, 'libvlc_video_set_marquee_int'):
        def video_set_marquee_int(self, option, i_val):
            """Enable, disable or set an integer marquee option
Setting libvlc_marquee_Enable has the side effect of enabling (arg !0)
or disabling (arg 0) the marq filter.
@param option: marq option to set \see libvlc_video_marquee_int_option_t
        """
            return libvlc_video_set_marquee_int(self, option, i_val)

    if hasattr(dll, 'libvlc_video_set_marquee_string'):
        def video_set_marquee_string(self, option, psz_text):
            """Set a marquee string option
@param option: marq option to set \see libvlc_video_marquee_string_option_t
        """
            return libvlc_video_set_marquee_string(self, option, psz_text)

    if hasattr(dll, 'libvlc_video_get_logo_int'):
        def video_get_logo_int(self, option):
            """Get integer logo option.
        """
            return libvlc_video_get_logo_int(self, option)

    if hasattr(dll, 'libvlc_video_set_logo_int'):
        def video_set_logo_int(self, option, value):
            """Set logo option as integer. Options that take a different type value
are ignored.
Passing libvlc_logo_enable as option value has the side effect of
starting (arg !0) or stopping (arg 0) the logo filter.
@param option: logo option to set, values of libvlc_video_logo_option_t
        """
            return libvlc_video_set_logo_int(self, option, value)

    if hasattr(dll, 'libvlc_video_set_logo_string'):
        def video_set_logo_string(self, option, psz_value):
            """Set logo option as string. Options that take a different type value
are ignored.
@param option: logo option to set, values of libvlc_video_logo_option_t
        """
            return libvlc_video_set_logo_string(self, option, psz_value)

    if hasattr(dll, 'libvlc_audio_output_set'):
        def audio_output_set(self, psz_name):
            """Set the audio output.
Change will be applied after stop and play.
@return: true if function succeded
        """
            return libvlc_audio_output_set(self, psz_name)

    if hasattr(dll, 'libvlc_audio_output_device_set'):
        def audio_output_device_set(self, psz_audio_output, psz_device_id):
            """Set audio output device. Changes are only effective after stop and play.
@param psz_audio_output: - name of audio output, \see libvlc_audio_output_t
        """
            return libvlc_audio_output_device_set(self, psz_audio_output, psz_device_id)

    if hasattr(dll, 'libvlc_audio_output_get_device_type'):
        def audio_output_get_device_type(self):
            """Get current audio device type. Device type describes something like
character of output sound - stereo sound, 2.1, 5.1 etc
@return: the audio devices type \see libvlc_audio_output_device_types_t
        """
            return libvlc_audio_output_get_device_type(self)

    if hasattr(dll, 'libvlc_audio_output_set_device_type'):
        def audio_output_set_device_type(self, device_type):
            """Set current audio device type.
        """
            return libvlc_audio_output_set_device_type(self, device_type)

    if hasattr(dll, 'libvlc_audio_toggle_mute'):
        def audio_toggle_mute(self):
            """Toggle mute status.
        """
            return libvlc_audio_toggle_mute(self)

    if hasattr(dll, 'libvlc_audio_get_mute'):
        def audio_get_mute(self):
            """Get current mute status.
@return: the mute status (boolean)
        """
            return libvlc_audio_get_mute(self)

    if hasattr(dll, 'libvlc_audio_set_mute'):
        def audio_set_mute(self, status):
            """Set mute status.
        """
            return libvlc_audio_set_mute(self, status)

    if hasattr(dll, 'libvlc_audio_get_volume'):
        def audio_get_volume(self):
            """Get current audio level.
@return: the audio level (int)
        """
            return libvlc_audio_get_volume(self)

    if hasattr(dll, 'libvlc_audio_set_volume'):
        def audio_set_volume(self, i_volume):
            """Set current audio level.
@return: 0 if the volume was set, -1 if it was out of range
        """
            return libvlc_audio_set_volume(self, i_volume)

    if hasattr(dll, 'libvlc_audio_get_track_count'):
        def audio_get_track_count(self):
            """Get number of available audio tracks.
@return: the number of available audio tracks (int), or -1 if unavailable
        """
            return libvlc_audio_get_track_count(self)

    if hasattr(dll, 'libvlc_audio_get_track_description'):
        def audio_get_track_description(self):
            """Get the description of available audio tracks.
@return: list with description of available audio tracks, or NULL
        """
            return libvlc_audio_get_track_description(self)

    if hasattr(dll, 'libvlc_audio_get_track'):
        def audio_get_track(self):
            """Get current audio track.
@return: the audio track (int), or -1 if none.
        """
            return libvlc_audio_get_track(self)

    if hasattr(dll, 'libvlc_audio_set_track'):
        def audio_set_track(self, i_track):
            """Set current audio track.
@return: 0 on success, -1 on error
        """
            return libvlc_audio_set_track(self, i_track)

    if hasattr(dll, 'libvlc_audio_get_channel'):
        def audio_get_channel(self):
            """Get current audio channel.
@return: the audio channel \see libvlc_audio_output_channel_t
        """
            return libvlc_audio_get_channel(self)

    if hasattr(dll, 'libvlc_audio_set_channel'):
        def audio_set_channel(self, channel):
            """Set current audio channel.
@return: 0 on success, -1 on error
        """
            return libvlc_audio_set_channel(self, channel)

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

if hasattr(dll, 'libvlc_errmsg'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_char_p)
    paramflags= tuple()
    libvlc_errmsg = prototype( ("libvlc_errmsg", dll), paramflags )
    libvlc_errmsg.__doc__ = """A human-readable error message for the last LibVLC error in the calling
thread. The resulting string is valid until another error occurs (at least
until the next LibVLC call).
@warning
This will be NULL if there was no error.
"""

if hasattr(dll, 'libvlc_clearerr'):
    prototype=ctypes.CFUNCTYPE(None)
    paramflags= tuple()
    libvlc_clearerr = prototype( ("libvlc_clearerr", dll), paramflags )
    libvlc_clearerr.__doc__ = """Clears the LibVLC error status for the current thread. This is optional.
By default, the error status is automatically overriden when a new error
occurs, and destroyed when the thread exits.
"""

if hasattr(dll, 'libvlc_new'):
    prototype=ctypes.CFUNCTYPE(Instance, ctypes.c_int, ListPOINTER(ctypes.c_char_p))
    paramflags=(1,), (1,)
    libvlc_new = prototype( ("libvlc_new", dll), paramflags )
    libvlc_new.__doc__ = """Create and initialize a libvlc instance.
@param argc the number of arguments
@param argv command-line-type arguments
@return the libvlc instance or NULL in case of error
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
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, Instance, ctypes.c_char_p)
    paramflags=(1,), (1,)
    libvlc_add_intf = prototype( ("libvlc_add_intf", dll), paramflags )
    libvlc_add_intf.__doc__ = """Try to start a user interface for the libvlc instance.
@param p_instance the instance
@param name interface name, or NULL for default
@return 0 on success, -1 on error.
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
Example: "1.1.0-git The Luggage"
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

if hasattr(dll, 'libvlc_event_attach'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, EventManager, ctypes.c_uint, ctypes.c_void_p, ctypes.c_void_p)
    paramflags=(1,), (1,), (1,), (1,)
    libvlc_event_attach = prototype( ("libvlc_event_attach", dll), paramflags )
    libvlc_event_attach.__doc__ = """Register for an event notification.
@param p_event_manager the event manager to which you want to attach to.
       Generally it is obtained by vlc_my_object_event_manager() where
       my_object is the object you want to listen to.
@param i_event_type the desired event to which we want to listen
@param f_callback the function to call when i_event_type occurs
@param user_data user provided data to carry with the event
@return 0 on success, ENOMEM on error
"""

if hasattr(dll, 'libvlc_event_detach'):
    prototype=ctypes.CFUNCTYPE(None, EventManager, ctypes.c_uint, ctypes.c_void_p, ctypes.c_void_p)
    paramflags=(1,), (1,), (1,), (1,)
    libvlc_event_detach = prototype( ("libvlc_event_detach", dll), paramflags )
    libvlc_event_detach.__doc__ = """Unregister an event notification.
@param p_event_manager the event manager
@param i_event_type the desired event to which we want to unregister
@param f_callback the function to call when i_event_type occurs
@param p_user_data user provided data to carry with the event
"""

if hasattr(dll, 'libvlc_event_type_name'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_char_p, ctypes.c_uint)
    paramflags=( (1, ), )
    libvlc_event_type_name = prototype( ("libvlc_event_type_name", dll), paramflags )
    libvlc_event_type_name.__doc__ = """Get an event's type name.
@param event_type the desired event
"""

if hasattr(dll, 'libvlc_get_log_verbosity'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_uint, Instance)
    paramflags=( (1, ), )
    libvlc_get_log_verbosity = prototype( ("libvlc_get_log_verbosity", dll), paramflags )
    libvlc_get_log_verbosity.__doc__ = """Return the VLC messaging verbosity level.
@param p_instance libvlc instance
@return verbosity level for messages
"""

if hasattr(dll, 'libvlc_set_log_verbosity'):
    prototype=ctypes.CFUNCTYPE(None, Instance, ctypes.c_uint)
    paramflags=(1,), (1,)
    libvlc_set_log_verbosity = prototype( ("libvlc_set_log_verbosity", dll), paramflags )
    libvlc_set_log_verbosity.__doc__ = """Set the VLC messaging verbosity level.
@param p_instance libvlc log instance
@param level log level
"""

if hasattr(dll, 'libvlc_log_open'):
    prototype=ctypes.CFUNCTYPE(Log, Instance)
    paramflags=( (1, ), )
    libvlc_log_open = prototype( ("libvlc_log_open", dll), paramflags )
    libvlc_log_open.__doc__ = """Open a VLC message log instance.
@param p_instance libvlc instance
@return log message instance or NULL on error
"""

if hasattr(dll, 'libvlc_log_close'):
    prototype=ctypes.CFUNCTYPE(None, Log)
    paramflags=( (1, ), )
    libvlc_log_close = prototype( ("libvlc_log_close", dll), paramflags )
    libvlc_log_close.__doc__ = """Close a VLC message log instance.
@param p_log libvlc log instance or NULL
"""

if hasattr(dll, 'libvlc_log_count'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_uint, Log)
    paramflags=( (1, ), )
    libvlc_log_count = prototype( ("libvlc_log_count", dll), paramflags )
    libvlc_log_count.__doc__ = """Returns the number of messages in a log instance.
@param p_log libvlc log instance or NULL
@return number of log messages, 0 if p_log is NULL
"""

if hasattr(dll, 'libvlc_log_clear'):
    prototype=ctypes.CFUNCTYPE(None, Log)
    paramflags=( (1, ), )
    libvlc_log_clear = prototype( ("libvlc_log_clear", dll), paramflags )
    libvlc_log_clear.__doc__ = """Clear a log instance.
All messages in the log are removed. The log should be cleared on a
regular basis to avoid clogging.
@param p_log libvlc log instance or NULL
"""

if hasattr(dll, 'libvlc_log_get_iterator'):
    prototype=ctypes.CFUNCTYPE(LogIterator, Log)
    paramflags=( (1, ), )
    libvlc_log_get_iterator = prototype( ("libvlc_log_get_iterator", dll), paramflags )
    libvlc_log_get_iterator.__doc__ = """Allocate and returns a new iterator to messages in log.
@param p_log libvlc log instance
@return log iterator object or NULL on error
"""

if hasattr(dll, 'libvlc_log_iterator_free'):
    prototype=ctypes.CFUNCTYPE(None, LogIterator)
    paramflags=( (1, ), )
    libvlc_log_iterator_free = prototype( ("libvlc_log_iterator_free", dll), paramflags )
    libvlc_log_iterator_free.__doc__ = """Release a previoulsy allocated iterator.
@param p_iter libvlc log iterator or NULL
"""

if hasattr(dll, 'libvlc_log_iterator_has_next'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, LogIterator)
    paramflags=( (1, ), )
    libvlc_log_iterator_has_next = prototype( ("libvlc_log_iterator_has_next", dll), paramflags )
    libvlc_log_iterator_has_next.__doc__ = """Return whether log iterator has more messages.
@param p_iter libvlc log iterator or NULL
@return true if iterator has more message objects, else false
"""

if hasattr(dll, 'libvlc_log_iterator_next'):
    prototype=ctypes.CFUNCTYPE(ctypes.POINTER(LogMessage), LogIterator, ctypes.POINTER(LogMessage))
    paramflags=(1,), (1,)
    libvlc_log_iterator_next = prototype( ("libvlc_log_iterator_next", dll), paramflags )
    libvlc_log_iterator_next.__doc__ = """Return the next log message.
The message contents must not be freed
@param p_iter libvlc log iterator or NULL
@param p_buffer log buffer
@return log message object or NULL if none left
"""

if hasattr(dll, 'libvlc_media_discoverer_new_from_name'):
    prototype=ctypes.CFUNCTYPE(MediaDiscoverer, Instance, ctypes.c_char_p)
    paramflags=(1,), (1,)
    libvlc_media_discoverer_new_from_name = prototype( ("libvlc_media_discoverer_new_from_name", dll), paramflags )
    libvlc_media_discoverer_new_from_name.__doc__ = """Discover media service by name.
@param p_inst libvlc instance
@param psz_name service name
@return media discover object or NULL in case of error
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
@param p_mdis media discover object
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

if hasattr(dll, 'libvlc_media_new_location'):
    prototype=ctypes.CFUNCTYPE(Media, Instance, ctypes.c_char_p)
    paramflags=(1,), (1,)
    libvlc_media_new_location = prototype( ("libvlc_media_new_location", dll), paramflags )
    libvlc_media_new_location.__doc__ = """Create a media with a certain given media resource location.
\see libvlc_media_release
@param p_instance the instance
@param psz_mrl the MRL to read
@return the newly created media or NULL on error
"""

if hasattr(dll, 'libvlc_media_new_path'):
    prototype=ctypes.CFUNCTYPE(Media, Instance, ctypes.c_char_p)
    paramflags=(1,), (1,)
    libvlc_media_new_path = prototype( ("libvlc_media_new_path", dll), paramflags )
    libvlc_media_new_path.__doc__ = """Create a media with a certain file path.
\see libvlc_media_release
@param p_instance the instance
@param path local filesystem path
@return the newly created media or NULL on error
"""

if hasattr(dll, 'libvlc_media_new_as_node'):
    prototype=ctypes.CFUNCTYPE(Media, Instance, ctypes.c_char_p)
    paramflags=(1,), (1,)
    libvlc_media_new_as_node = prototype( ("libvlc_media_new_as_node", dll), paramflags )
    libvlc_media_new_as_node.__doc__ = """Create a media as an empty node with a given name.
\see libvlc_media_release
@param p_instance the instance
@param psz_name the name of the node
@return the new empty media or NULL on error
"""

if hasattr(dll, 'libvlc_media_add_option'):
    prototype=ctypes.CFUNCTYPE(None, Media, ctypes.c_char_p)
    paramflags=(1,), (1,)
    libvlc_media_add_option = prototype( ("libvlc_media_add_option", dll), paramflags )
    libvlc_media_add_option.__doc__ = """Add an option to the media.
This option will be used to determine how the media_player will
read the media. This allows to use VLC's advanced
reading/streaming options on a per-media basis.
The options are detailed in vlc --long-help, for instance "--sout-all"
@param p_md the media descriptor
@param ppsz_options the options (as a string)
"""

if hasattr(dll, 'libvlc_media_add_option_flag'):
    prototype=ctypes.CFUNCTYPE(None, Media, ctypes.c_char_p, ctypes.c_uint)
    paramflags=(1,), (1,), (1,)
    libvlc_media_add_option_flag = prototype( ("libvlc_media_add_option_flag", dll), paramflags )
    libvlc_media_add_option_flag.__doc__ = """Add an option to the media with configurable flags.
This option will be used to determine how the media_player will
read the media. This allows to use VLC's advanced
reading/streaming options on a per-media basis.
The options are detailed in vlc --long-help, for instance "--sout-all"
@param p_md the media descriptor
@param ppsz_options the options (as a string)
@param i_flags the flags for this option
"""

if hasattr(dll, 'libvlc_media_retain'):
    prototype=ctypes.CFUNCTYPE(None, Media)
    paramflags=( (1, ), )
    libvlc_media_retain = prototype( ("libvlc_media_retain", dll), paramflags )
    libvlc_media_retain.__doc__ = """Retain a reference to a media descriptor object (libvlc_media_t). Use
libvlc_media_release() to decrement the reference count of a
media descriptor object.
@param p_md the media descriptor
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
@param p_md the media descriptor
"""

if hasattr(dll, 'libvlc_media_get_mrl'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_char_p, Media)
    paramflags=( (1, ), )
    libvlc_media_get_mrl = prototype( ("libvlc_media_get_mrl", dll), paramflags )
    libvlc_media_get_mrl.__doc__ = """Get the media resource locator (mrl) from a media descriptor object
@param p_md a media descriptor object
@return string with mrl of media descriptor object
"""

if hasattr(dll, 'libvlc_media_duplicate'):
    prototype=ctypes.CFUNCTYPE(Media, Media)
    paramflags=( (1, ), )
    libvlc_media_duplicate = prototype( ("libvlc_media_duplicate", dll), paramflags )
    libvlc_media_duplicate.__doc__ = """Duplicate a media descriptor object.
@param p_md a media descriptor object.
"""

if hasattr(dll, 'libvlc_media_get_meta'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_char_p, Media, Meta)
    paramflags=(1,), (1,)
    libvlc_media_get_meta = prototype( ("libvlc_media_get_meta", dll), paramflags )
    libvlc_media_get_meta.__doc__ = """Read the meta of the media.
If the media has not yet been parsed this will return NULL.
This methods automatically calls libvlc_media_parse_async(), so after calling
it you may receive a libvlc_MediaMetaChanged event. If you prefer a synchronous
version ensure that you call libvlc_media_parse() before get_meta().
\see libvlc_media_parse
\see libvlc_media_parse_async
\see libvlc_MediaMetaChanged
@param p_md the media descriptor
@param e_meta the meta to read
@return the media's meta
"""

if hasattr(dll, 'libvlc_media_set_meta'):
    prototype=ctypes.CFUNCTYPE(None, Media, Meta, ctypes.c_char_p)
    paramflags=(1,), (1,), (1,)
    libvlc_media_set_meta = prototype( ("libvlc_media_set_meta", dll), paramflags )
    libvlc_media_set_meta.__doc__ = """Set the meta of the media (this function will not save the meta, call
libvlc_media_save_meta in order to save the meta)
@param p_md the media descriptor
@param e_meta the meta to write
@param psz_value the media's meta
"""

if hasattr(dll, 'libvlc_media_save_meta'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, Media)
    paramflags=( (1, ), )
    libvlc_media_save_meta = prototype( ("libvlc_media_save_meta", dll), paramflags )
    libvlc_media_save_meta.__doc__ = """Save the meta previously set
@param p_md the media desriptor
@return true if the write operation was successfull
"""

if hasattr(dll, 'libvlc_media_get_state'):
    prototype=ctypes.CFUNCTYPE(State, Media)
    paramflags=( (1, ), )
    libvlc_media_get_state = prototype( ("libvlc_media_get_state", dll), paramflags )
    libvlc_media_get_state.__doc__ = """Get current state of media descriptor object. Possible media states
are defined in libvlc_structures.c ( libvlc_NothingSpecial=0,
libvlc_Opening, libvlc_Buffering, libvlc_Playing, libvlc_Paused,
libvlc_Stopped, libvlc_Ended,
libvlc_Error).
@see libvlc_state_t
@param p_meta_desc a media descriptor object
@return state of media descriptor object
"""

if hasattr(dll, 'libvlc_media_get_stats'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, Media, ctypes.POINTER(MediaStats))
    paramflags=(1,), (1,)
    libvlc_media_get_stats = prototype( ("libvlc_media_get_stats", dll), paramflags )
    libvlc_media_get_stats.__doc__ = """get the current statistics about the media
@param p_md: media descriptor object
@param p_stats: structure that contain the statistics about the media
                (this structure must be allocated by the caller)
@return true if the statistics are available, false otherwise
"""

if hasattr(dll, 'libvlc_media_subitems'):
    prototype=ctypes.CFUNCTYPE(MediaList, Media)
    paramflags=( (1, ), )
    libvlc_media_subitems = prototype( ("libvlc_media_subitems", dll), paramflags )
    libvlc_media_subitems.__doc__ = """Get subitems of media descriptor object. This will increment
the reference count of supplied media descriptor object. Use
libvlc_media_list_release() to decrement the reference counting.
@param p_md media descriptor object
@return list of media descriptor subitems or NULL
and this is here for convenience */
"""

if hasattr(dll, 'libvlc_media_event_manager'):
    prototype=ctypes.CFUNCTYPE(EventManager, Media)
    paramflags=( (1, ), )
    libvlc_media_event_manager = prototype( ("libvlc_media_event_manager", dll), paramflags )
    libvlc_media_event_manager.__doc__ = """Get event manager from media descriptor object.
NOTE: this function doesn't increment reference counting.
@param p_md a media descriptor object
@return event manager object
"""

if hasattr(dll, 'libvlc_media_get_duration'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_longlong, Media)
    paramflags=( (1, ), )
    libvlc_media_get_duration = prototype( ("libvlc_media_get_duration", dll), paramflags )
    libvlc_media_get_duration.__doc__ = """Get duration (in ms) of media descriptor object item.
@param p_md media descriptor object
@return duration of media item or -1 on error
"""

if hasattr(dll, 'libvlc_media_parse'):
    prototype=ctypes.CFUNCTYPE(None, Media)
    paramflags=( (1, ), )
    libvlc_media_parse = prototype( ("libvlc_media_parse", dll), paramflags )
    libvlc_media_parse.__doc__ = """Parse a media.
This fetches (local) meta data and tracks information.
The method is synchronous.
\see libvlc_media_parse_async
\see libvlc_media_get_meta
\see libvlc_media_get_tracks_info
@param media media descriptor object
"""

if hasattr(dll, 'libvlc_media_parse_async'):
    prototype=ctypes.CFUNCTYPE(None, Media)
    paramflags=( (1, ), )
    libvlc_media_parse_async = prototype( ("libvlc_media_parse_async", dll), paramflags )
    libvlc_media_parse_async.__doc__ = """Parse a media.
This fetches (local) meta data and tracks information.
The method is the asynchronous of libvlc_media_parse_async().
To track when this is over you can listen to libvlc_MediaParsedChanged
event. However if the media was already parsed you will not receive this
event.
\see libvlc_media_parse
\see libvlc_MediaParsedChanged
\see libvlc_media_get_meta
\see libvlc_media_get_tracks_info
@param media media descriptor object
"""

if hasattr(dll, 'libvlc_media_is_parsed'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, Media)
    paramflags=( (1, ), )
    libvlc_media_is_parsed = prototype( ("libvlc_media_is_parsed", dll), paramflags )
    libvlc_media_is_parsed.__doc__ = """Get Parsed status for media descriptor object.
\see libvlc_MediaParsedChanged
@param p_md media descriptor object
@return true if media object has been parsed otherwise it returns false
"""

if hasattr(dll, 'libvlc_media_set_user_data'):
    prototype=ctypes.CFUNCTYPE(None, Media, ctypes.c_void_p)
    paramflags=(1,), (1,)
    libvlc_media_set_user_data = prototype( ("libvlc_media_set_user_data", dll), paramflags )
    libvlc_media_set_user_data.__doc__ = """Sets media descriptor's user_data. user_data is specialized data
accessed by the host application, VLC.framework uses it as a pointer to
an native object that references a libvlc_media_t pointer
@param p_md media descriptor object
@param p_new_user_data pointer to user data
"""

if hasattr(dll, 'libvlc_media_get_user_data'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_void_p, Media)
    paramflags=( (1, ), )
    libvlc_media_get_user_data = prototype( ("libvlc_media_get_user_data", dll), paramflags )
    libvlc_media_get_user_data.__doc__ = """Get media descriptor's user_data. user_data is specialized data
accessed by the host application, VLC.framework uses it as a pointer to
an native object that references a libvlc_media_t pointer
@param p_md media descriptor object
"""

if hasattr(dll, 'libvlc_media_get_tracks_info'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, Media, ctypes.POINTER(ctypes.POINTER(MediaTrackInfo)))
    paramflags=(1,), (1,)
    libvlc_media_get_tracks_info = prototype( ("libvlc_media_get_tracks_info", dll), paramflags )
    libvlc_media_get_tracks_info.__doc__ = """Get media descriptor's elementary streams description
Note, you need to play the media _one_ time with --sout="#description"
Not doing this will result in an empty array, and doing it more than once
will duplicate the entries in the array each time. Something like this:
@begincode
libvlc_media_player_t *player = libvlc_media_player_new_from_media(media);
libvlc_media_add_option_flag(media, "sout=\"#description\"");
libvlc_media_player_play(player);
// ... wait until playing
libvlc_media_player_release(player);
@endcode
This is very likely to change in next release, and be done at the parsing
phase.
@param media media descriptor object
@param tracks address to store an allocated array of Elementary Streams
descriptions (must be freed by the caller)
return the number of Elementary Streams
"""

if hasattr(dll, 'libvlc_media_library_new'):
    prototype=ctypes.CFUNCTYPE(MediaLibrary, Instance)
    paramflags=( (1, ), )
    libvlc_media_library_new = prototype( ("libvlc_media_library_new", dll), paramflags )
    libvlc_media_library_new.__doc__ = """Create an new Media Library object
@param p_instance the libvlc instance
@return a new object or NULL on error
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
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaLibrary)
    paramflags=( (1, ), )
    libvlc_media_library_load = prototype( ("libvlc_media_library_load", dll), paramflags )
    libvlc_media_library_load.__doc__ = """Load media library.
@param p_mlib media library object
@return 0 on success, -1 on error
"""

if hasattr(dll, 'libvlc_media_library_media_list'):
    prototype=ctypes.CFUNCTYPE(MediaList, MediaLibrary)
    paramflags=( (1, ), )
    libvlc_media_library_media_list = prototype( ("libvlc_media_library_media_list", dll), paramflags )
    libvlc_media_library_media_list.__doc__ = """Get media library subitems.
@param p_mlib media library object
@return media list subitems
"""

if hasattr(dll, 'libvlc_media_list_new'):
    prototype=ctypes.CFUNCTYPE(MediaList, Instance)
    paramflags=( (1, ), )
    libvlc_media_list_new = prototype( ("libvlc_media_list_new", dll), paramflags )
    libvlc_media_list_new.__doc__ = """Create an empty media list.
@param p_instance libvlc instance
@return empty media list, or NULL on error
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
    prototype=ctypes.CFUNCTYPE(None, MediaList, Media)
    paramflags=(1,), (1,)
    libvlc_media_list_set_media = prototype( ("libvlc_media_list_set_media", dll), paramflags )
    libvlc_media_list_set_media.__doc__ = """Associate media instance with this media list instance.
If another media instance was present it will be released.
The libvlc_media_list_lock should NOT be held upon entering this function.
@param p_ml a media list instance
@param p_md media instance to add
"""

if hasattr(dll, 'libvlc_media_list_media'):
    prototype=ctypes.CFUNCTYPE(Media, MediaList)
    paramflags=( (1, ), )
    libvlc_media_list_media = prototype( ("libvlc_media_list_media", dll), paramflags )
    libvlc_media_list_media.__doc__ = """Get media instance from this media list instance. This action will increase
the refcount on the media instance.
The libvlc_media_list_lock should NOT be held upon entering this function.
@param p_ml a media list instance
@return media instance
"""

if hasattr(dll, 'libvlc_media_list_add_media'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaList, Media)
    paramflags=(1,), (1,)
    libvlc_media_list_add_media = prototype( ("libvlc_media_list_add_media", dll), paramflags )
    libvlc_media_list_add_media.__doc__ = """Add media instance to media list
The libvlc_media_list_lock should be held upon entering this function.
@param p_ml a media list instance
@param p_md a media instance
@return 0 on success, -1 if the media list is read-only
"""

if hasattr(dll, 'libvlc_media_list_insert_media'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaList, Media, ctypes.c_int)
    paramflags=(1,), (1,), (1,)
    libvlc_media_list_insert_media = prototype( ("libvlc_media_list_insert_media", dll), paramflags )
    libvlc_media_list_insert_media.__doc__ = """Insert media instance in media list on a position
The libvlc_media_list_lock should be held upon entering this function.
@param p_ml a media list instance
@param p_md a media instance
@param i_pos position in array where to insert
@return 0 on success, -1 if the media list si read-only
"""

if hasattr(dll, 'libvlc_media_list_remove_index'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaList, ctypes.c_int)
    paramflags=(1,), (1,)
    libvlc_media_list_remove_index = prototype( ("libvlc_media_list_remove_index", dll), paramflags )
    libvlc_media_list_remove_index.__doc__ = """Remove media instance from media list on a position
The libvlc_media_list_lock should be held upon entering this function.
@param p_ml a media list instance
@param i_pos position in array where to insert
@return 0 on success, -1 if the list is read-only or the item was not found
"""

if hasattr(dll, 'libvlc_media_list_count'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaList)
    paramflags=( (1, ), )
    libvlc_media_list_count = prototype( ("libvlc_media_list_count", dll), paramflags )
    libvlc_media_list_count.__doc__ = """Get count on media list items
The libvlc_media_list_lock should be held upon entering this function.
@param p_ml a media list instance
@return number of items in media list
"""

if hasattr(dll, 'libvlc_media_list_item_at_index'):
    prototype=ctypes.CFUNCTYPE(Media, MediaList, ctypes.c_int)
    paramflags=(1,), (1,)
    libvlc_media_list_item_at_index = prototype( ("libvlc_media_list_item_at_index", dll), paramflags )
    libvlc_media_list_item_at_index.__doc__ = """List media instance in media list at a position
The libvlc_media_list_lock should be held upon entering this function.
@param p_ml a media list instance
@param i_pos position in array where to insert
@return media instance at position i_pos, or NULL if not found.
In case of success, libvlc_media_retain() is called to increase the refcount
on the media.
"""

if hasattr(dll, 'libvlc_media_list_index_of_item'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaList, Media)
    paramflags=(1,), (1,)
    libvlc_media_list_index_of_item = prototype( ("libvlc_media_list_index_of_item", dll), paramflags )
    libvlc_media_list_index_of_item.__doc__ = """Find index position of List media instance in media list.
Warning: the function will return the first matched position.
The libvlc_media_list_lock should be held upon entering this function.
@param p_ml a media list instance
@param p_md media list instance
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

if hasattr(dll, 'libvlc_media_list_event_manager'):
    prototype=ctypes.CFUNCTYPE(EventManager, MediaList)
    paramflags=( (1, ), )
    libvlc_media_list_event_manager = prototype( ("libvlc_media_list_event_manager", dll), paramflags )
    libvlc_media_list_event_manager.__doc__ = """Get libvlc_event_manager from this media list instance.
The p_event_manager is immutable, so you don't have to hold the lock
@param p_ml a media list instance
@return libvlc_event_manager
"""

if hasattr(dll, 'libvlc_media_list_player_new'):
    prototype=ctypes.CFUNCTYPE(MediaListPlayer, Instance)
    paramflags=( (1, ), )
    libvlc_media_list_player_new = prototype( ("libvlc_media_list_player_new", dll), paramflags )
    libvlc_media_list_player_new.__doc__ = """Create new media_list_player.
@param p_instance libvlc instance
@return media list player instance or NULL on error
"""

if hasattr(dll, 'libvlc_media_list_player_release'):
    prototype=ctypes.CFUNCTYPE(None, MediaListPlayer)
    paramflags=( (1, ), )
    libvlc_media_list_player_release = prototype( ("libvlc_media_list_player_release", dll), paramflags )
    libvlc_media_list_player_release.__doc__ = """Release media_list_player.
@param p_mlp media list player instance
"""

if hasattr(dll, 'libvlc_media_list_player_event_manager'):
    prototype=ctypes.CFUNCTYPE(EventManager, MediaListPlayer)
    paramflags=( (1, ), )
    libvlc_media_list_player_event_manager = prototype( ("libvlc_media_list_player_event_manager", dll), paramflags )
    libvlc_media_list_player_event_manager.__doc__ = """Return the event manager of this media_list_player.
@param p_mlp media list player instance
@return the event manager
"""

if hasattr(dll, 'libvlc_media_list_player_set_media_player'):
    prototype=ctypes.CFUNCTYPE(None, MediaListPlayer, MediaPlayer)
    paramflags=(1,), (1,)
    libvlc_media_list_player_set_media_player = prototype( ("libvlc_media_list_player_set_media_player", dll), paramflags )
    libvlc_media_list_player_set_media_player.__doc__ = """Replace media player in media_list_player with this instance.
@param p_mlp media list player instance
@param p_mi media player instance
"""

if hasattr(dll, 'libvlc_media_list_player_set_media_list'):
    prototype=ctypes.CFUNCTYPE(None, MediaListPlayer, MediaList)
    paramflags=(1,), (1,)
    libvlc_media_list_player_set_media_list = prototype( ("libvlc_media_list_player_set_media_list", dll), paramflags )
    libvlc_media_list_player_set_media_list.__doc__ = """Set the media list associated with the player
@param p_mlp media list player instance
@param p_mlist list of media
"""

if hasattr(dll, 'libvlc_media_list_player_play'):
    prototype=ctypes.CFUNCTYPE(None, MediaListPlayer)
    paramflags=( (1, ), )
    libvlc_media_list_player_play = prototype( ("libvlc_media_list_player_play", dll), paramflags )
    libvlc_media_list_player_play.__doc__ = """Play media list
@param p_mlp media list player instance
"""

if hasattr(dll, 'libvlc_media_list_player_pause'):
    prototype=ctypes.CFUNCTYPE(None, MediaListPlayer)
    paramflags=( (1, ), )
    libvlc_media_list_player_pause = prototype( ("libvlc_media_list_player_pause", dll), paramflags )
    libvlc_media_list_player_pause.__doc__ = """Pause media list
@param p_mlp media list player instance
"""

if hasattr(dll, 'libvlc_media_list_player_is_playing'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaListPlayer)
    paramflags=( (1, ), )
    libvlc_media_list_player_is_playing = prototype( ("libvlc_media_list_player_is_playing", dll), paramflags )
    libvlc_media_list_player_is_playing.__doc__ = """Is media list playing?
@param p_mlp media list player instance
@return true for playing and false for not playing
"""

if hasattr(dll, 'libvlc_media_list_player_get_state'):
    prototype=ctypes.CFUNCTYPE(State, MediaListPlayer)
    paramflags=( (1, ), )
    libvlc_media_list_player_get_state = prototype( ("libvlc_media_list_player_get_state", dll), paramflags )
    libvlc_media_list_player_get_state.__doc__ = """Get current libvlc_state of media list player
@param p_mlp media list player instance
@return libvlc_state_t for media list player
"""

if hasattr(dll, 'libvlc_media_list_player_play_item_at_index'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaListPlayer, ctypes.c_int)
    paramflags=(1,), (1,)
    libvlc_media_list_player_play_item_at_index = prototype( ("libvlc_media_list_player_play_item_at_index", dll), paramflags )
    libvlc_media_list_player_play_item_at_index.__doc__ = """Play media list item at position index
@param p_mlp media list player instance
@param i_index index in media list to play
@return 0 upon success -1 if the item wasn't found
"""

if hasattr(dll, 'libvlc_media_list_player_play_item'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaListPlayer, Media)
    paramflags=(1,), (1,)
    libvlc_media_list_player_play_item = prototype( ("libvlc_media_list_player_play_item", dll), paramflags )
    libvlc_media_list_player_play_item.__doc__ = """Play the given media item
@param p_mlp media list player instance
@param p_md the media instance
@return 0 upon success, -1 if the media is not part of the media list
"""

if hasattr(dll, 'libvlc_media_list_player_stop'):
    prototype=ctypes.CFUNCTYPE(None, MediaListPlayer)
    paramflags=( (1, ), )
    libvlc_media_list_player_stop = prototype( ("libvlc_media_list_player_stop", dll), paramflags )
    libvlc_media_list_player_stop.__doc__ = """Stop playing media list
@param p_mlp media list player instance
"""

if hasattr(dll, 'libvlc_media_list_player_next'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaListPlayer)
    paramflags=( (1, ), )
    libvlc_media_list_player_next = prototype( ("libvlc_media_list_player_next", dll), paramflags )
    libvlc_media_list_player_next.__doc__ = """Play next item from media list
@param p_mlp media list player instance
@return 0 upon success -1 if there is no next item
"""

if hasattr(dll, 'libvlc_media_list_player_previous'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaListPlayer)
    paramflags=( (1, ), )
    libvlc_media_list_player_previous = prototype( ("libvlc_media_list_player_previous", dll), paramflags )
    libvlc_media_list_player_previous.__doc__ = """Play previous item from media list
@param p_mlp media list player instance
@return 0 upon success -1 if there is no previous item
"""

if hasattr(dll, 'libvlc_media_list_player_set_playback_mode'):
    prototype=ctypes.CFUNCTYPE(None, MediaListPlayer, PlaybackMode)
    paramflags=(1,), (1,)
    libvlc_media_list_player_set_playback_mode = prototype( ("libvlc_media_list_player_set_playback_mode", dll), paramflags )
    libvlc_media_list_player_set_playback_mode.__doc__ = """Sets the playback mode for the playlist
@param p_mlp media list player instance
@param e_mode playback mode specification
"""

if hasattr(dll, 'libvlc_media_player_new'):
    prototype=ctypes.CFUNCTYPE(MediaPlayer, Instance)
    paramflags=( (1, ), )
    libvlc_media_player_new = prototype( ("libvlc_media_player_new", dll), paramflags )
    libvlc_media_player_new.__doc__ = """Create an empty Media Player object
@param p_libvlc_instance the libvlc instance in which the Media Player
       should be created.
@return a new media player object, or NULL on error.
"""

if hasattr(dll, 'libvlc_media_player_new_from_media'):
    prototype=ctypes.CFUNCTYPE(MediaPlayer, Media)
    paramflags=( (1, ), )
    libvlc_media_player_new_from_media = prototype( ("libvlc_media_player_new_from_media", dll), paramflags )
    libvlc_media_player_new_from_media.__doc__ = """Create a Media Player object from a Media
@param p_md the media. Afterwards the p_md can be safely
       destroyed.
@return a new media player object, or NULL on error.
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
    prototype=ctypes.CFUNCTYPE(None, MediaPlayer, Media)
    paramflags=(1,), (1,)
    libvlc_media_player_set_media = prototype( ("libvlc_media_player_set_media", dll), paramflags )
    libvlc_media_player_set_media.__doc__ = """Set the media that will be used by the media_player. If any,
previous md will be released.
@param p_mi the Media Player
@param p_md the Media. Afterwards the p_md can be safely
       destroyed.
"""

if hasattr(dll, 'libvlc_media_player_get_media'):
    prototype=ctypes.CFUNCTYPE(Media, MediaPlayer)
    paramflags=( (1, ), )
    libvlc_media_player_get_media = prototype( ("libvlc_media_player_get_media", dll), paramflags )
    libvlc_media_player_get_media.__doc__ = """Get the media used by the media_player.
@param p_mi the Media Player
@return the media associated with p_mi, or NULL if no
        media is associated
"""

if hasattr(dll, 'libvlc_media_player_event_manager'):
    prototype=ctypes.CFUNCTYPE(EventManager, MediaPlayer)
    paramflags=( (1, ), )
    libvlc_media_player_event_manager = prototype( ("libvlc_media_player_event_manager", dll), paramflags )
    libvlc_media_player_event_manager.__doc__ = """Get the Event Manager from which the media player send event.
@param p_mi the Media Player
@return the event manager associated with p_mi
"""

if hasattr(dll, 'libvlc_media_player_is_playing'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaPlayer)
    paramflags=( (1, ), )
    libvlc_media_player_is_playing = prototype( ("libvlc_media_player_is_playing", dll), paramflags )
    libvlc_media_player_is_playing.__doc__ = """is_playing
@param p_mi the Media Player
@return 1 if the media player is playing, 0 otherwise
"""

if hasattr(dll, 'libvlc_media_player_play'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaPlayer)
    paramflags=( (1, ), )
    libvlc_media_player_play = prototype( ("libvlc_media_player_play", dll), paramflags )
    libvlc_media_player_play.__doc__ = """Play
@param p_mi the Media Player
@return 0 if playback started (and was already started), or -1 on error.
"""

if hasattr(dll, 'libvlc_media_player_pause'):
    prototype=ctypes.CFUNCTYPE(None, MediaPlayer)
    paramflags=( (1, ), )
    libvlc_media_player_pause = prototype( ("libvlc_media_player_pause", dll), paramflags )
    libvlc_media_player_pause.__doc__ = """Toggle pause (no effect if there is no media)
@param p_mi the Media Player
"""

if hasattr(dll, 'libvlc_media_player_stop'):
    prototype=ctypes.CFUNCTYPE(None, MediaPlayer)
    paramflags=( (1, ), )
    libvlc_media_player_stop = prototype( ("libvlc_media_player_stop", dll), paramflags )
    libvlc_media_player_stop.__doc__ = """Stop (no effect if there is no media)
@param p_mi the Media Player
"""

if hasattr(dll, 'libvlc_media_player_set_nsobject'):
    prototype=ctypes.CFUNCTYPE(None, MediaPlayer, ctypes.c_void_p)
    paramflags=(1,), (1,)
    libvlc_media_player_set_nsobject = prototype( ("libvlc_media_player_set_nsobject", dll), paramflags )
    libvlc_media_player_set_nsobject.__doc__ = """Set the NSView handler where the media player should render its video output.
Use the vout called "macosx".
The drawable is an NSObject that follow the VLCOpenGLVideoViewEmbedding
protocol:
@begincode
\@protocol VLCOpenGLVideoViewEmbedding <NSObject>
- (void)addVoutSubview:(NSView *)view;
- (void)removeVoutSubview:(NSView *)view;
\@end
@endcode
Or it can be an NSView object.
If you want to use it along with Qt4 see the QMacCocoaViewContainer. Then
the following code should work:
@begincode
{
    NSView *video = [[NSView alloc] init];
    QMacCocoaViewContainer *container = new QMacCocoaViewContainer(video, parent);
    libvlc_media_player_set_nsobject(mp, video);
    [video release];
}
@endcode
You can find a live example in VLCVideoView in VLCKit.framework.
@param p_mi the Media Player
@param drawable the drawable that is either an NSView or an object following
the VLCOpenGLVideoViewEmbedding protocol.
"""

if hasattr(dll, 'libvlc_media_player_get_nsobject'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_void_p, MediaPlayer)
    paramflags=( (1, ), )
    libvlc_media_player_get_nsobject = prototype( ("libvlc_media_player_get_nsobject", dll), paramflags )
    libvlc_media_player_get_nsobject.__doc__ = """Get the NSView handler previously set with libvlc_media_player_set_nsobject().
@param p_mi the Media Player
@return the NSView handler or 0 if none where set
"""

if hasattr(dll, 'libvlc_media_player_set_agl'):
    prototype=ctypes.CFUNCTYPE(None, MediaPlayer, ctypes.c_uint)
    paramflags=(1,), (1,)
    libvlc_media_player_set_agl = prototype( ("libvlc_media_player_set_agl", dll), paramflags )
    libvlc_media_player_set_agl.__doc__ = """Set the agl handler where the media player should render its video output.
@param p_mi the Media Player
@param drawable the agl handler
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
    prototype=ctypes.CFUNCTYPE(None, MediaPlayer, ctypes.c_uint)
    paramflags=(1,), (1,)
    libvlc_media_player_set_xwindow = prototype( ("libvlc_media_player_set_xwindow", dll), paramflags )
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
"""

if hasattr(dll, 'libvlc_media_player_get_xwindow'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_uint, MediaPlayer)
    paramflags=( (1, ), )
    libvlc_media_player_get_xwindow = prototype( ("libvlc_media_player_get_xwindow", dll), paramflags )
    libvlc_media_player_get_xwindow.__doc__ = """Get the X Window System window identifier previously set with
libvlc_media_player_set_xwindow(). Note that this will return the identifier
even if VLC is not currently using it (for instance if it is playing an
audio-only input).
@param p_mi the Media Player
@return an X window ID, or 0 if none where set.
"""

if hasattr(dll, 'libvlc_media_player_set_hwnd'):
    prototype=ctypes.CFUNCTYPE(None, MediaPlayer, ctypes.c_void_p)
    paramflags=(1,), (1,)
    libvlc_media_player_set_hwnd = prototype( ("libvlc_media_player_set_hwnd", dll), paramflags )
    libvlc_media_player_set_hwnd.__doc__ = """Set a Win32/Win64 API window handle (HWND) where the media player should
render its video output. If LibVLC was built without Win32/Win64 API output
support, then this has no effects.
@param p_mi the Media Player
@param drawable windows handle of the drawable
"""

if hasattr(dll, 'libvlc_media_player_get_hwnd'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_void_p, MediaPlayer)
    paramflags=( (1, ), )
    libvlc_media_player_get_hwnd = prototype( ("libvlc_media_player_get_hwnd", dll), paramflags )
    libvlc_media_player_get_hwnd.__doc__ = """Get the Windows API window handle (HWND) previously set with
libvlc_media_player_set_hwnd(). The handle will be returned even if LibVLC
is not currently outputting any video to it.
@param p_mi the Media Player
@return a window handle or NULL if there are none.
"""

if hasattr(dll, 'libvlc_media_player_get_length'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_longlong, MediaPlayer)
    paramflags=( (1, ), )
    libvlc_media_player_get_length = prototype( ("libvlc_media_player_get_length", dll), paramflags )
    libvlc_media_player_get_length.__doc__ = """Get the current movie length (in ms).
@param p_mi the Media Player
@return the movie length (in ms), or -1 if there is no media.
"""

if hasattr(dll, 'libvlc_media_player_get_time'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_longlong, MediaPlayer)
    paramflags=( (1, ), )
    libvlc_media_player_get_time = prototype( ("libvlc_media_player_get_time", dll), paramflags )
    libvlc_media_player_get_time.__doc__ = """Get the current movie time (in ms).
@param p_mi the Media Player
@return the movie time (in ms), or -1 if there is no media.
"""

if hasattr(dll, 'libvlc_media_player_set_time'):
    prototype=ctypes.CFUNCTYPE(None, MediaPlayer, ctypes.c_longlong)
    paramflags=(1,), (1,)
    libvlc_media_player_set_time = prototype( ("libvlc_media_player_set_time", dll), paramflags )
    libvlc_media_player_set_time.__doc__ = """Set the movie time (in ms). This has no effect if no media is being played.
Not all formats and protocols support this.
@param p_mi the Media Player
@param i_time the movie time (in ms).
"""

if hasattr(dll, 'libvlc_media_player_get_position'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_float, MediaPlayer)
    paramflags=( (1, ), )
    libvlc_media_player_get_position = prototype( ("libvlc_media_player_get_position", dll), paramflags )
    libvlc_media_player_get_position.__doc__ = """Get movie position.
@param p_mi the Media Player
@return movie position, or -1. in case of error
"""

if hasattr(dll, 'libvlc_media_player_set_position'):
    prototype=ctypes.CFUNCTYPE(None, MediaPlayer, ctypes.c_float)
    paramflags=(1,), (1,)
    libvlc_media_player_set_position = prototype( ("libvlc_media_player_set_position", dll), paramflags )
    libvlc_media_player_set_position.__doc__ = """Set movie position. This has no effect if playback is not enabled.
This might not work depending on the underlying input format and protocol.
@param p_mi the Media Player
@param f_pos the position
"""

if hasattr(dll, 'libvlc_media_player_set_chapter'):
    prototype=ctypes.CFUNCTYPE(None, MediaPlayer, ctypes.c_int)
    paramflags=(1,), (1,)
    libvlc_media_player_set_chapter = prototype( ("libvlc_media_player_set_chapter", dll), paramflags )
    libvlc_media_player_set_chapter.__doc__ = """Set movie chapter (if applicable).
@param p_mi the Media Player
@param i_chapter chapter number to play
"""

if hasattr(dll, 'libvlc_media_player_get_chapter'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaPlayer)
    paramflags=( (1, ), )
    libvlc_media_player_get_chapter = prototype( ("libvlc_media_player_get_chapter", dll), paramflags )
    libvlc_media_player_get_chapter.__doc__ = """Get movie chapter.
@param p_mi the Media Player
@return chapter number currently playing, or -1 if there is no media.
"""

if hasattr(dll, 'libvlc_media_player_get_chapter_count'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaPlayer)
    paramflags=( (1, ), )
    libvlc_media_player_get_chapter_count = prototype( ("libvlc_media_player_get_chapter_count", dll), paramflags )
    libvlc_media_player_get_chapter_count.__doc__ = """Get movie chapter count
@param p_mi the Media Player
@return number of chapters in movie, or -1.
"""

if hasattr(dll, 'libvlc_media_player_will_play'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaPlayer)
    paramflags=( (1, ), )
    libvlc_media_player_will_play = prototype( ("libvlc_media_player_will_play", dll), paramflags )
    libvlc_media_player_will_play.__doc__ = """Is the player able to play
@param p_mi the Media Player
@return boolean
"""

if hasattr(dll, 'libvlc_media_player_get_chapter_count_for_title'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaPlayer, ctypes.c_int)
    paramflags=(1,), (1,)
    libvlc_media_player_get_chapter_count_for_title = prototype( ("libvlc_media_player_get_chapter_count_for_title", dll), paramflags )
    libvlc_media_player_get_chapter_count_for_title.__doc__ = """Get title chapter count
@param p_mi the Media Player
@param i_title title
@return number of chapters in title, or -1
"""

if hasattr(dll, 'libvlc_media_player_set_title'):
    prototype=ctypes.CFUNCTYPE(None, MediaPlayer, ctypes.c_int)
    paramflags=(1,), (1,)
    libvlc_media_player_set_title = prototype( ("libvlc_media_player_set_title", dll), paramflags )
    libvlc_media_player_set_title.__doc__ = """Set movie title
@param p_mi the Media Player
@param i_title title number to play
"""

if hasattr(dll, 'libvlc_media_player_get_title'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaPlayer)
    paramflags=( (1, ), )
    libvlc_media_player_get_title = prototype( ("libvlc_media_player_get_title", dll), paramflags )
    libvlc_media_player_get_title.__doc__ = """Get movie title
@param p_mi the Media Player
@return title number currently playing, or -1
"""

if hasattr(dll, 'libvlc_media_player_get_title_count'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaPlayer)
    paramflags=( (1, ), )
    libvlc_media_player_get_title_count = prototype( ("libvlc_media_player_get_title_count", dll), paramflags )
    libvlc_media_player_get_title_count.__doc__ = """Get movie title count
@param p_mi the Media Player
@return title number count, or -1
"""

if hasattr(dll, 'libvlc_media_player_previous_chapter'):
    prototype=ctypes.CFUNCTYPE(None, MediaPlayer)
    paramflags=( (1, ), )
    libvlc_media_player_previous_chapter = prototype( ("libvlc_media_player_previous_chapter", dll), paramflags )
    libvlc_media_player_previous_chapter.__doc__ = """Set previous chapter (if applicable)
@param p_mi the Media Player
"""

if hasattr(dll, 'libvlc_media_player_next_chapter'):
    prototype=ctypes.CFUNCTYPE(None, MediaPlayer)
    paramflags=( (1, ), )
    libvlc_media_player_next_chapter = prototype( ("libvlc_media_player_next_chapter", dll), paramflags )
    libvlc_media_player_next_chapter.__doc__ = """Set next chapter (if applicable)
@param p_mi the Media Player
"""

if hasattr(dll, 'libvlc_media_player_get_rate'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_float, MediaPlayer)
    paramflags=( (1, ), )
    libvlc_media_player_get_rate = prototype( ("libvlc_media_player_get_rate", dll), paramflags )
    libvlc_media_player_get_rate.__doc__ = """Get the requested movie play rate.
@warning Depending on the underlying media, the requested rate may be
different from the real playback rate.
@param p_mi the Media Player
@return movie play rate
"""

if hasattr(dll, 'libvlc_media_player_set_rate'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaPlayer, ctypes.c_float)
    paramflags=(1,), (1,)
    libvlc_media_player_set_rate = prototype( ("libvlc_media_player_set_rate", dll), paramflags )
    libvlc_media_player_set_rate.__doc__ = """Set movie play rate
@param p_mi the Media Player
@param rate movie play rate to set
@return -1 if an error was detected, 0 otherwise (but even then, it might
not actually work depending on the underlying media protocol)
"""

if hasattr(dll, 'libvlc_media_player_get_state'):
    prototype=ctypes.CFUNCTYPE(State, MediaPlayer)
    paramflags=( (1, ), )
    libvlc_media_player_get_state = prototype( ("libvlc_media_player_get_state", dll), paramflags )
    libvlc_media_player_get_state.__doc__ = """Get current movie state
@param p_mi the Media Player
@return the current state of the media player (playing, paused, ...) \see libvlc_state_t
"""

if hasattr(dll, 'libvlc_media_player_get_fps'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_float, MediaPlayer)
    paramflags=( (1, ), )
    libvlc_media_player_get_fps = prototype( ("libvlc_media_player_get_fps", dll), paramflags )
    libvlc_media_player_get_fps.__doc__ = """Get movie fps rate
@param p_mi the Media Player
@return frames per second (fps) for this playing movie, or 0 if unspecified
"""

if hasattr(dll, 'libvlc_media_player_has_vout'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_uint, MediaPlayer)
    paramflags=( (1, ), )
    libvlc_media_player_has_vout = prototype( ("libvlc_media_player_has_vout", dll), paramflags )
    libvlc_media_player_has_vout.__doc__ = """How many video outputs does this media player have?
@param p_mi the media player
@return the number of video outputs
"""

if hasattr(dll, 'libvlc_media_player_is_seekable'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaPlayer)
    paramflags=( (1, ), )
    libvlc_media_player_is_seekable = prototype( ("libvlc_media_player_is_seekable", dll), paramflags )
    libvlc_media_player_is_seekable.__doc__ = """Is this media player seekable?
@param p_mi the media player
@return true if the media player can seek
"""

if hasattr(dll, 'libvlc_media_player_can_pause'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaPlayer)
    paramflags=( (1, ), )
    libvlc_media_player_can_pause = prototype( ("libvlc_media_player_can_pause", dll), paramflags )
    libvlc_media_player_can_pause.__doc__ = """Can this media player be paused?
@param p_mi the media player
@return true if the media player can pause
"""

if hasattr(dll, 'libvlc_media_player_next_frame'):
    prototype=ctypes.CFUNCTYPE(None, MediaPlayer)
    paramflags=( (1, ), )
    libvlc_media_player_next_frame = prototype( ("libvlc_media_player_next_frame", dll), paramflags )
    libvlc_media_player_next_frame.__doc__ = """Display the next frame (if supported)
@param p_mi the media player
"""

if hasattr(dll, 'libvlc_track_description_release'):
    prototype=ctypes.CFUNCTYPE(None, TrackDescription)
    paramflags=( (1, ), )
    libvlc_track_description_release = prototype( ("libvlc_track_description_release", dll), paramflags )
    libvlc_track_description_release.__doc__ = """Release (free) libvlc_track_description_t
@param p_track_description the structure to release
"""

if hasattr(dll, 'libvlc_toggle_fullscreen'):
    prototype=ctypes.CFUNCTYPE(None, MediaPlayer)
    paramflags=( (1, ), )
    libvlc_toggle_fullscreen = prototype( ("libvlc_toggle_fullscreen", dll), paramflags )
    libvlc_toggle_fullscreen.__doc__ = """Toggle fullscreen status on non-embedded video outputs.
@warning The same limitations applies to this function
as to libvlc_set_fullscreen().
@param p_mi the media player
"""

if hasattr(dll, 'libvlc_set_fullscreen'):
    prototype=ctypes.CFUNCTYPE(None, MediaPlayer, ctypes.c_int)
    paramflags=(1,), (1,)
    libvlc_set_fullscreen = prototype( ("libvlc_set_fullscreen", dll), paramflags )
    libvlc_set_fullscreen.__doc__ = """Enable or disable fullscreen.
@warning With most window managers, only a top-level windows can be in
full-screen mode. Hence, this function will not operate properly if
libvlc_media_player_set_xid() was used to embed the video in a non-top-level
window. In that case, the embedding window must be reparented to the root
window <b>before</b> fullscreen mode is enabled. You will want to reparent
it back to its normal parent when disabling fullscreen.
@param p_mi the media player
@param b_fullscreen boolean for fullscreen status
"""

if hasattr(dll, 'libvlc_get_fullscreen'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaPlayer)
    paramflags=( (1, ), )
    libvlc_get_fullscreen = prototype( ("libvlc_get_fullscreen", dll), paramflags )
    libvlc_get_fullscreen.__doc__ = """Get current fullscreen status.
@param p_mi the media player
@return the fullscreen status (boolean)
"""

if hasattr(dll, 'libvlc_video_set_key_input'):
    prototype=ctypes.CFUNCTYPE(None, MediaPlayer, ctypes.c_uint)
    paramflags=(1,), (1,)
    libvlc_video_set_key_input = prototype( ("libvlc_video_set_key_input", dll), paramflags )
    libvlc_video_set_key_input.__doc__ = """Enable or disable key press events handling, according to the LibVLC hotkeys
configuration. By default and for historical reasons, keyboard events are
handled by the LibVLC video widget.
\note On X11, there can be only one subscriber for key press and mouse
click events per window. If your application has subscribed to those events
for the X window ID of the video widget, then LibVLC will not be able to
handle key presses and mouse clicks in any case.
\warning This function is only implemented for X11 at the moment.
@param p_mi the media player
@param on true to handle key press events, false to ignore them.
"""

if hasattr(dll, 'libvlc_video_set_mouse_input'):
    prototype=ctypes.CFUNCTYPE(None, MediaPlayer, ctypes.c_uint)
    paramflags=(1,), (1,)
    libvlc_video_set_mouse_input = prototype( ("libvlc_video_set_mouse_input", dll), paramflags )
    libvlc_video_set_mouse_input.__doc__ = """Enable or disable mouse click events handling. By default, those events are
handled. This is needed for DVD menus to work, as well as a few video
filters such as "puzzle".
\note See also libvlc_video_set_key_input().
\warning This function is only implemented for X11 at the moment.
@param p_mi the media player
@param on true to handle mouse click events, false to ignore them.
"""

if hasattr(dll, 'libvlc_video_get_size'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaPlayer, ctypes.c_uint, ctypes.POINTER(ctypes.c_uint), ctypes.POINTER(ctypes.c_uint))
    paramflags=(1,), (1,), (1,), (1,)
    libvlc_video_get_size = prototype( ("libvlc_video_get_size", dll), paramflags )
    libvlc_video_get_size.__doc__ = """Get the pixel dimensions of a video.
@param p_mi media player
@param num number of the video (starting from, and most commonly 0)
@param px pointer to get the pixel width [OUT]
@param py pointer to get the pixel height [OUT]
@return 0 on success, -1 if the specified video does not exist
"""

if hasattr(dll, 'libvlc_video_get_cursor'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaPlayer, ctypes.c_uint, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
    paramflags=(1,), (1,), (1,), (1,)
    libvlc_video_get_cursor = prototype( ("libvlc_video_get_cursor", dll), paramflags )
    libvlc_video_get_cursor.__doc__ = """Get the mouse pointer coordinates over a video.
Coordinates are expressed in terms of the decoded video resolution,
<b>not</b> in terms of pixels on the screen/viewport (to get the latter,
you can query your windowing system directly).
Either of the coordinates may be negative or larger than the corresponding
dimension of the video, if the cursor is outside the rendering area.
@warning The coordinates may be out-of-date if the pointer is not located
on the video rendering area. LibVLC does not track the pointer if it is
outside of the video widget.
@note LibVLC does not support multiple pointers (it does of course support
multiple input devices sharing the same pointer) at the moment.
@param p_mi media player
@param num number of the video (starting from, and most commonly 0)
@param px pointer to get the abscissa [OUT]
@param py pointer to get the ordinate [OUT]
@return 0 on success, -1 if the specified video does not exist
"""

if hasattr(dll, 'libvlc_video_get_scale'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_float, MediaPlayer)
    paramflags=( (1, ), )
    libvlc_video_get_scale = prototype( ("libvlc_video_get_scale", dll), paramflags )
    libvlc_video_get_scale.__doc__ = """Get the current video scaling factor.
See also libvlc_video_set_scale().
@param p_mi the media player
@return the currently configured zoom factor, or 0. if the video is set
to fit to the output window/drawable automatically.
"""

if hasattr(dll, 'libvlc_video_set_scale'):
    prototype=ctypes.CFUNCTYPE(None, MediaPlayer, ctypes.c_float)
    paramflags=(1,), (1,)
    libvlc_video_set_scale = prototype( ("libvlc_video_set_scale", dll), paramflags )
    libvlc_video_set_scale.__doc__ = """Set the video scaling factor. That is the ratio of the number of pixels on
screen to the number of pixels in the original decoded video in each
dimension. Zero is a special value; it will adjust the video to the output
window/drawable (in windowed mode) or the entire screen.
Note that not all video outputs support scaling.
@param p_mi the media player
@param f_factor the scaling factor, or zero
"""

if hasattr(dll, 'libvlc_video_get_aspect_ratio'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_char_p, MediaPlayer)
    paramflags=( (1, ), )
    libvlc_video_get_aspect_ratio = prototype( ("libvlc_video_get_aspect_ratio", dll), paramflags )
    libvlc_video_get_aspect_ratio.__doc__ = """Get current video aspect ratio.
@param p_mi the media player
@return the video aspect ratio or NULL if unspecified
(the result must be released with free()).
"""

if hasattr(dll, 'libvlc_video_set_aspect_ratio'):
    prototype=ctypes.CFUNCTYPE(None, MediaPlayer, ctypes.c_char_p)
    paramflags=(1,), (1,)
    libvlc_video_set_aspect_ratio = prototype( ("libvlc_video_set_aspect_ratio", dll), paramflags )
    libvlc_video_set_aspect_ratio.__doc__ = """Set new video aspect ratio.
@param p_mi the media player
@param psz_aspect new video aspect-ratio or NULL to reset to default
\note Invalid aspect ratios are ignored.
"""

if hasattr(dll, 'libvlc_video_get_spu'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaPlayer)
    paramflags=( (1, ), )
    libvlc_video_get_spu = prototype( ("libvlc_video_get_spu", dll), paramflags )
    libvlc_video_get_spu.__doc__ = """Get current video subtitle.
@param p_mi the media player
@return the video subtitle selected, or -1 if none
"""

if hasattr(dll, 'libvlc_video_get_spu_count'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaPlayer)
    paramflags=( (1, ), )
    libvlc_video_get_spu_count = prototype( ("libvlc_video_get_spu_count", dll), paramflags )
    libvlc_video_get_spu_count.__doc__ = """Get the number of available video subtitles.
@param p_mi the media player
@return the number of available video subtitles
"""

if hasattr(dll, 'libvlc_video_get_spu_description'):
    prototype=ctypes.CFUNCTYPE(TrackDescription, MediaPlayer)
    paramflags=( (1, ), )
    libvlc_video_get_spu_description = prototype( ("libvlc_video_get_spu_description", dll), paramflags )
    libvlc_video_get_spu_description.__doc__ = """Get the description of available video subtitles.
@param p_mi the media player
@return list containing description of available video subtitles
"""

if hasattr(dll, 'libvlc_video_set_spu'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaPlayer, ctypes.c_uint)
    paramflags=(1,), (1,)
    libvlc_video_set_spu = prototype( ("libvlc_video_set_spu", dll), paramflags )
    libvlc_video_set_spu.__doc__ = """Set new video subtitle.
@param p_mi the media player
@param i_spu new video subtitle to select
@return 0 on success, -1 if out of range
"""

if hasattr(dll, 'libvlc_video_set_subtitle_file'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaPlayer, ctypes.c_char_p)
    paramflags=(1,), (1,)
    libvlc_video_set_subtitle_file = prototype( ("libvlc_video_set_subtitle_file", dll), paramflags )
    libvlc_video_set_subtitle_file.__doc__ = """Set new video subtitle file.
@param p_mi the media player
@param psz_subtitle new video subtitle file
@return the success status (boolean)
"""

if hasattr(dll, 'libvlc_video_get_title_description'):
    prototype=ctypes.CFUNCTYPE(TrackDescription, MediaPlayer)
    paramflags=( (1, ), )
    libvlc_video_get_title_description = prototype( ("libvlc_video_get_title_description", dll), paramflags )
    libvlc_video_get_title_description.__doc__ = """Get the description of available titles.
@param p_mi the media player
@return list containing description of available titles
"""

if hasattr(dll, 'libvlc_video_get_chapter_description'):
    prototype=ctypes.CFUNCTYPE(TrackDescription, MediaPlayer, ctypes.c_int)
    paramflags=(1,), (1,)
    libvlc_video_get_chapter_description = prototype( ("libvlc_video_get_chapter_description", dll), paramflags )
    libvlc_video_get_chapter_description.__doc__ = """Get the description of available chapters for specific title.
@param p_mi the media player
@param i_title selected title
@return list containing description of available chapter for title i_title
"""

if hasattr(dll, 'libvlc_video_get_crop_geometry'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_char_p, MediaPlayer)
    paramflags=( (1, ), )
    libvlc_video_get_crop_geometry = prototype( ("libvlc_video_get_crop_geometry", dll), paramflags )
    libvlc_video_get_crop_geometry.__doc__ = """Get current crop filter geometry.
@param p_mi the media player
@return the crop filter geometry or NULL if unset
"""

if hasattr(dll, 'libvlc_video_set_crop_geometry'):
    prototype=ctypes.CFUNCTYPE(None, MediaPlayer, ctypes.c_char_p)
    paramflags=(1,), (1,)
    libvlc_video_set_crop_geometry = prototype( ("libvlc_video_set_crop_geometry", dll), paramflags )
    libvlc_video_set_crop_geometry.__doc__ = """Set new crop filter geometry.
@param p_mi the media player
@param psz_geometry new crop filter geometry (NULL to unset)
"""

if hasattr(dll, 'libvlc_video_get_teletext'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaPlayer)
    paramflags=( (1, ), )
    libvlc_video_get_teletext = prototype( ("libvlc_video_get_teletext", dll), paramflags )
    libvlc_video_get_teletext.__doc__ = """Get current teletext page requested.
@param p_mi the media player
@return the current teletext page requested.
"""

if hasattr(dll, 'libvlc_video_set_teletext'):
    prototype=ctypes.CFUNCTYPE(None, MediaPlayer, ctypes.c_int)
    paramflags=(1,), (1,)
    libvlc_video_set_teletext = prototype( ("libvlc_video_set_teletext", dll), paramflags )
    libvlc_video_set_teletext.__doc__ = """Set new teletext page to retrieve.
@param p_mi the media player
@param i_page teletex page number requested
"""

if hasattr(dll, 'libvlc_toggle_teletext'):
    prototype=ctypes.CFUNCTYPE(None, MediaPlayer)
    paramflags=( (1, ), )
    libvlc_toggle_teletext = prototype( ("libvlc_toggle_teletext", dll), paramflags )
    libvlc_toggle_teletext.__doc__ = """Toggle teletext transparent status on video output.
@param p_mi the media player
"""

if hasattr(dll, 'libvlc_video_get_track_count'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaPlayer)
    paramflags=( (1, ), )
    libvlc_video_get_track_count = prototype( ("libvlc_video_get_track_count", dll), paramflags )
    libvlc_video_get_track_count.__doc__ = """Get number of available video tracks.
@param p_mi media player
@return the number of available video tracks (int)
"""

if hasattr(dll, 'libvlc_video_get_track_description'):
    prototype=ctypes.CFUNCTYPE(TrackDescription, MediaPlayer)
    paramflags=( (1, ), )
    libvlc_video_get_track_description = prototype( ("libvlc_video_get_track_description", dll), paramflags )
    libvlc_video_get_track_description.__doc__ = """Get the description of available video tracks.
@param p_mi media player
@return list with description of available video tracks, or NULL on error
"""

if hasattr(dll, 'libvlc_video_get_track'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaPlayer)
    paramflags=( (1, ), )
    libvlc_video_get_track = prototype( ("libvlc_video_get_track", dll), paramflags )
    libvlc_video_get_track.__doc__ = """Get current video track.
@param p_mi media player
@return the video track (int) or -1 if none
"""

if hasattr(dll, 'libvlc_video_set_track'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaPlayer, ctypes.c_int)
    paramflags=(1,), (1,)
    libvlc_video_set_track = prototype( ("libvlc_video_set_track", dll), paramflags )
    libvlc_video_set_track.__doc__ = """Set video track.
@param p_mi media player
@param i_track the track (int)
@return 0 on success, -1 if out of range
"""

if hasattr(dll, 'libvlc_video_take_snapshot'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaPlayer, ctypes.c_uint, ctypes.c_char_p, ctypes.c_int, ctypes.c_int)
    paramflags=(1,), (1,), (1,), (1,), (1,)
    libvlc_video_take_snapshot = prototype( ("libvlc_video_take_snapshot", dll), paramflags )
    libvlc_video_take_snapshot.__doc__ = """Take a snapshot of the current video window.
If i_width AND i_height is 0, original size is used.
If i_width XOR i_height is 0, original aspect-ratio is preserved.
@param p_mi media player instance
@param num number of video output (typically 0 for the first/only one)
@param psz_filepath the path where to save the screenshot to
@param i_width the snapshot's width
@param i_height the snapshot's height
@return 0 on success, -1 if the video was not found
"""

if hasattr(dll, 'libvlc_video_set_deinterlace'):
    prototype=ctypes.CFUNCTYPE(None, MediaPlayer, ctypes.c_char_p)
    paramflags=(1,), (1,)
    libvlc_video_set_deinterlace = prototype( ("libvlc_video_set_deinterlace", dll), paramflags )
    libvlc_video_set_deinterlace.__doc__ = """Enable or disable deinterlace filter
@param p_mi libvlc media player
@param psz_mode type of deinterlace filter, NULL to disable
"""

if hasattr(dll, 'libvlc_video_get_marquee_int'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaPlayer, ctypes.c_uint)
    paramflags=(1,), (1,)
    libvlc_video_get_marquee_int = prototype( ("libvlc_video_get_marquee_int", dll), paramflags )
    libvlc_video_get_marquee_int.__doc__ = """Get an integer marquee option value
@param p_mi libvlc media player
@param option marq option to get \see libvlc_video_marquee_int_option_t
"""

if hasattr(dll, 'libvlc_video_get_marquee_string'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_char_p, MediaPlayer, ctypes.c_uint)
    paramflags=(1,), (1,)
    libvlc_video_get_marquee_string = prototype( ("libvlc_video_get_marquee_string", dll), paramflags )
    libvlc_video_get_marquee_string.__doc__ = """Get a string marquee option value
@param p_mi libvlc media player
@param option marq option to get \see libvlc_video_marquee_string_option_t
"""

if hasattr(dll, 'libvlc_video_set_marquee_int'):
    prototype=ctypes.CFUNCTYPE(None, MediaPlayer, ctypes.c_uint, ctypes.c_int)
    paramflags=(1,), (1,), (1,)
    libvlc_video_set_marquee_int = prototype( ("libvlc_video_set_marquee_int", dll), paramflags )
    libvlc_video_set_marquee_int.__doc__ = """Enable, disable or set an integer marquee option
Setting libvlc_marquee_Enable has the side effect of enabling (arg !0)
or disabling (arg 0) the marq filter.
@param p_mi libvlc media player
@param option marq option to set \see libvlc_video_marquee_int_option_t
@param i_val marq option value
"""

if hasattr(dll, 'libvlc_video_set_marquee_string'):
    prototype=ctypes.CFUNCTYPE(None, MediaPlayer, ctypes.c_uint, ctypes.c_char_p)
    paramflags=(1,), (1,), (1,)
    libvlc_video_set_marquee_string = prototype( ("libvlc_video_set_marquee_string", dll), paramflags )
    libvlc_video_set_marquee_string.__doc__ = """Set a marquee string option
@param p_mi libvlc media player
@param option marq option to set \see libvlc_video_marquee_string_option_t
@param psz_text marq option value
"""

if hasattr(dll, 'libvlc_video_get_logo_int'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaPlayer, ctypes.c_uint)
    paramflags=(1,), (1,)
    libvlc_video_get_logo_int = prototype( ("libvlc_video_get_logo_int", dll), paramflags )
    libvlc_video_get_logo_int.__doc__ = """Get integer logo option.
@param p_mi libvlc media player instance
@param option logo option to get, values of libvlc_video_logo_option_t
"""

if hasattr(dll, 'libvlc_video_set_logo_int'):
    prototype=ctypes.CFUNCTYPE(None, MediaPlayer, ctypes.c_uint, ctypes.c_int)
    paramflags=(1,), (1,), (1,)
    libvlc_video_set_logo_int = prototype( ("libvlc_video_set_logo_int", dll), paramflags )
    libvlc_video_set_logo_int.__doc__ = """Set logo option as integer. Options that take a different type value
are ignored.
Passing libvlc_logo_enable as option value has the side effect of
starting (arg !0) or stopping (arg 0) the logo filter.
@param p_mi libvlc media player instance
@param option logo option to set, values of libvlc_video_logo_option_t
@param value logo option value
"""

if hasattr(dll, 'libvlc_video_set_logo_string'):
    prototype=ctypes.CFUNCTYPE(None, MediaPlayer, ctypes.c_uint, ctypes.c_char_p)
    paramflags=(1,), (1,), (1,)
    libvlc_video_set_logo_string = prototype( ("libvlc_video_set_logo_string", dll), paramflags )
    libvlc_video_set_logo_string.__doc__ = """Set logo option as string. Options that take a different type value
are ignored.
@param p_mi libvlc media player instance
@param option logo option to set, values of libvlc_video_logo_option_t
@param psz_value logo option value
"""

if hasattr(dll, 'libvlc_audio_output_list_get'):
    prototype=ctypes.CFUNCTYPE(AudioOutput, Instance)
    paramflags=( (1, ), )
    libvlc_audio_output_list_get = prototype( ("libvlc_audio_output_list_get", dll), paramflags )
    libvlc_audio_output_list_get.__doc__ = """Get the list of available audio outputs
@param p_instance libvlc instance
@return list of available audio outputs. It must be freed it with
        In case of error, NULL is returned.
"""

if hasattr(dll, 'libvlc_audio_output_list_release'):
    prototype=ctypes.CFUNCTYPE(None, AudioOutput)
    paramflags=( (1, ), )
    libvlc_audio_output_list_release = prototype( ("libvlc_audio_output_list_release", dll), paramflags )
    libvlc_audio_output_list_release.__doc__ = """Free the list of available audio outputs
@param p_list list with audio outputs for release
"""

if hasattr(dll, 'libvlc_audio_output_set'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaPlayer, ctypes.c_char_p)
    paramflags=(1,), (1,)
    libvlc_audio_output_set = prototype( ("libvlc_audio_output_set", dll), paramflags )
    libvlc_audio_output_set.__doc__ = """Set the audio output.
Change will be applied after stop and play.
@param p_mi media player
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
    prototype=ctypes.CFUNCTYPE(None, MediaPlayer, ctypes.c_char_p, ctypes.c_char_p)
    paramflags=(1,), (1,), (1,)
    libvlc_audio_output_device_set = prototype( ("libvlc_audio_output_device_set", dll), paramflags )
    libvlc_audio_output_device_set.__doc__ = """Set audio output device. Changes are only effective after stop and play.
@param p_mi media player
@param psz_audio_output - name of audio output, \see libvlc_audio_output_t
@param psz_device_id device
"""

if hasattr(dll, 'libvlc_audio_output_get_device_type'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaPlayer)
    paramflags=( (1, ), )
    libvlc_audio_output_get_device_type = prototype( ("libvlc_audio_output_get_device_type", dll), paramflags )
    libvlc_audio_output_get_device_type.__doc__ = """Get current audio device type. Device type describes something like
character of output sound - stereo sound, 2.1, 5.1 etc
@param p_mi media player
@return the audio devices type \see libvlc_audio_output_device_types_t
"""

if hasattr(dll, 'libvlc_audio_output_set_device_type'):
    prototype=ctypes.CFUNCTYPE(None, MediaPlayer, ctypes.c_int)
    paramflags=(1,), (1,)
    libvlc_audio_output_set_device_type = prototype( ("libvlc_audio_output_set_device_type", dll), paramflags )
    libvlc_audio_output_set_device_type.__doc__ = """Set current audio device type.
@param p_mi vlc instance
@param device_type the audio device type,
"""

if hasattr(dll, 'libvlc_audio_toggle_mute'):
    prototype=ctypes.CFUNCTYPE(None, MediaPlayer)
    paramflags=( (1, ), )
    libvlc_audio_toggle_mute = prototype( ("libvlc_audio_toggle_mute", dll), paramflags )
    libvlc_audio_toggle_mute.__doc__ = """Toggle mute status.
@param p_mi media player
"""

if hasattr(dll, 'libvlc_audio_get_mute'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaPlayer)
    paramflags=( (1, ), )
    libvlc_audio_get_mute = prototype( ("libvlc_audio_get_mute", dll), paramflags )
    libvlc_audio_get_mute.__doc__ = """Get current mute status.
@param p_mi media player
@return the mute status (boolean)
"""

if hasattr(dll, 'libvlc_audio_set_mute'):
    prototype=ctypes.CFUNCTYPE(None, MediaPlayer, ctypes.c_int)
    paramflags=(1,), (1,)
    libvlc_audio_set_mute = prototype( ("libvlc_audio_set_mute", dll), paramflags )
    libvlc_audio_set_mute.__doc__ = """Set mute status.
@param p_mi media player
@param status If status is true then mute, otherwise unmute
"""

if hasattr(dll, 'libvlc_audio_get_volume'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaPlayer)
    paramflags=( (1, ), )
    libvlc_audio_get_volume = prototype( ("libvlc_audio_get_volume", dll), paramflags )
    libvlc_audio_get_volume.__doc__ = """Get current audio level.
@param p_mi media player
@return the audio level (int)
"""

if hasattr(dll, 'libvlc_audio_set_volume'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaPlayer, ctypes.c_int)
    paramflags=(1,), (1,)
    libvlc_audio_set_volume = prototype( ("libvlc_audio_set_volume", dll), paramflags )
    libvlc_audio_set_volume.__doc__ = """Set current audio level.
@param p_mi media player
@param i_volume the volume (int)
@return 0 if the volume was set, -1 if it was out of range
"""

if hasattr(dll, 'libvlc_audio_get_track_count'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaPlayer)
    paramflags=( (1, ), )
    libvlc_audio_get_track_count = prototype( ("libvlc_audio_get_track_count", dll), paramflags )
    libvlc_audio_get_track_count.__doc__ = """Get number of available audio tracks.
@param p_mi media player
@return the number of available audio tracks (int), or -1 if unavailable
"""

if hasattr(dll, 'libvlc_audio_get_track_description'):
    prototype=ctypes.CFUNCTYPE(TrackDescription, MediaPlayer)
    paramflags=( (1, ), )
    libvlc_audio_get_track_description = prototype( ("libvlc_audio_get_track_description", dll), paramflags )
    libvlc_audio_get_track_description.__doc__ = """Get the description of available audio tracks.
@param p_mi media player
@return list with description of available audio tracks, or NULL
"""

if hasattr(dll, 'libvlc_audio_get_track'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaPlayer)
    paramflags=( (1, ), )
    libvlc_audio_get_track = prototype( ("libvlc_audio_get_track", dll), paramflags )
    libvlc_audio_get_track.__doc__ = """Get current audio track.
@param p_mi media player
@return the audio track (int), or -1 if none.
"""

if hasattr(dll, 'libvlc_audio_set_track'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaPlayer, ctypes.c_int)
    paramflags=(1,), (1,)
    libvlc_audio_set_track = prototype( ("libvlc_audio_set_track", dll), paramflags )
    libvlc_audio_set_track.__doc__ = """Set current audio track.
@param p_mi media player
@param i_track the track (int)
@return 0 on success, -1 on error
"""

if hasattr(dll, 'libvlc_audio_get_channel'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaPlayer)
    paramflags=( (1, ), )
    libvlc_audio_get_channel = prototype( ("libvlc_audio_get_channel", dll), paramflags )
    libvlc_audio_get_channel.__doc__ = """Get current audio channel.
@param p_mi media player
@return the audio channel \see libvlc_audio_output_channel_t
"""

if hasattr(dll, 'libvlc_audio_set_channel'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, MediaPlayer, ctypes.c_int)
    paramflags=(1,), (1,)
    libvlc_audio_set_channel = prototype( ("libvlc_audio_set_channel", dll), paramflags )
    libvlc_audio_set_channel.__doc__ = """Set current audio channel.
@param p_mi media player
@param channel the audio channel, \see libvlc_audio_output_channel_t
@return 0 on success, -1 on error
"""

if hasattr(dll, 'libvlc_vlm_release'):
    prototype=ctypes.CFUNCTYPE(None, Instance)
    paramflags=( (1, ), )
    libvlc_vlm_release = prototype( ("libvlc_vlm_release", dll), paramflags )
    libvlc_vlm_release.__doc__ = """Release the vlm instance related to the given libvlc_instance_t
@param p_instance the instance
"""

if hasattr(dll, 'libvlc_vlm_add_broadcast'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, Instance, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, ListPOINTER(ctypes.c_char_p), ctypes.c_int, ctypes.c_int)
    paramflags=(1,), (1,), (1,), (1,), (1,), (1,), (1,), (1,)
    libvlc_vlm_add_broadcast = prototype( ("libvlc_vlm_add_broadcast", dll), paramflags )
    libvlc_vlm_add_broadcast.__doc__ = """Add a broadcast, with one input.
@param p_instance the instance
@param psz_name the name of the new broadcast
@param psz_input the input MRL
@param psz_output the output MRL (the parameter to the "sout" variable)
@param i_options number of additional options
@param ppsz_options additional options
@param b_enabled boolean for enabling the new broadcast
@param b_loop Should this broadcast be played in loop ?
@return 0 on success, -1 on error
"""

if hasattr(dll, 'libvlc_vlm_add_vod'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, Instance, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, ListPOINTER(ctypes.c_char_p), ctypes.c_int, ctypes.c_char_p)
    paramflags=(1,), (1,), (1,), (1,), (1,), (1,), (1,)
    libvlc_vlm_add_vod = prototype( ("libvlc_vlm_add_vod", dll), paramflags )
    libvlc_vlm_add_vod.__doc__ = """Add a vod, with one input.
@param p_instance the instance
@param psz_name the name of the new vod media
@param psz_input the input MRL
@param i_options number of additional options
@param ppsz_options additional options
@param b_enabled boolean for enabling the new vod
@param psz_mux the muxer of the vod media
@return 0 on success, -1 on error
"""

if hasattr(dll, 'libvlc_vlm_del_media'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, Instance, ctypes.c_char_p)
    paramflags=(1,), (1,)
    libvlc_vlm_del_media = prototype( ("libvlc_vlm_del_media", dll), paramflags )
    libvlc_vlm_del_media.__doc__ = """Delete a media (VOD or broadcast).
@param p_instance the instance
@param psz_name the media to delete
@return 0 on success, -1 on error
"""

if hasattr(dll, 'libvlc_vlm_set_enabled'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, Instance, ctypes.c_char_p, ctypes.c_int)
    paramflags=(1,), (1,), (1,)
    libvlc_vlm_set_enabled = prototype( ("libvlc_vlm_set_enabled", dll), paramflags )
    libvlc_vlm_set_enabled.__doc__ = """Enable or disable a media (VOD or broadcast).
@param p_instance the instance
@param psz_name the media to work on
@param b_enabled the new status
@return 0 on success, -1 on error
"""

if hasattr(dll, 'libvlc_vlm_set_output'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, Instance, ctypes.c_char_p, ctypes.c_char_p)
    paramflags=(1,), (1,), (1,)
    libvlc_vlm_set_output = prototype( ("libvlc_vlm_set_output", dll), paramflags )
    libvlc_vlm_set_output.__doc__ = """Set the output for a media.
@param p_instance the instance
@param psz_name the media to work on
@param psz_output the output MRL (the parameter to the "sout" variable)
@return 0 on success, -1 on error
"""

if hasattr(dll, 'libvlc_vlm_set_input'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, Instance, ctypes.c_char_p, ctypes.c_char_p)
    paramflags=(1,), (1,), (1,)
    libvlc_vlm_set_input = prototype( ("libvlc_vlm_set_input", dll), paramflags )
    libvlc_vlm_set_input.__doc__ = """Set a media's input MRL. This will delete all existing inputs and
add the specified one.
@param p_instance the instance
@param psz_name the media to work on
@param psz_input the input MRL
@return 0 on success, -1 on error
"""

if hasattr(dll, 'libvlc_vlm_add_input'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, Instance, ctypes.c_char_p, ctypes.c_char_p)
    paramflags=(1,), (1,), (1,)
    libvlc_vlm_add_input = prototype( ("libvlc_vlm_add_input", dll), paramflags )
    libvlc_vlm_add_input.__doc__ = """Add a media's input MRL. This will add the specified one.
@param p_instance the instance
@param psz_name the media to work on
@param psz_input the input MRL
@return 0 on success, -1 on error
"""

if hasattr(dll, 'libvlc_vlm_set_loop'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, Instance, ctypes.c_char_p, ctypes.c_int)
    paramflags=(1,), (1,), (1,)
    libvlc_vlm_set_loop = prototype( ("libvlc_vlm_set_loop", dll), paramflags )
    libvlc_vlm_set_loop.__doc__ = """Set a media's loop status.
@param p_instance the instance
@param psz_name the media to work on
@param b_loop the new status
@return 0 on success, -1 on error
"""

if hasattr(dll, 'libvlc_vlm_set_mux'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, Instance, ctypes.c_char_p, ctypes.c_char_p)
    paramflags=(1,), (1,), (1,)
    libvlc_vlm_set_mux = prototype( ("libvlc_vlm_set_mux", dll), paramflags )
    libvlc_vlm_set_mux.__doc__ = """Set a media's vod muxer.
@param p_instance the instance
@param psz_name the media to work on
@param psz_mux the new muxer
@return 0 on success, -1 on error
"""

if hasattr(dll, 'libvlc_vlm_change_media'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, Instance, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, ListPOINTER(ctypes.c_char_p), ctypes.c_int, ctypes.c_int)
    paramflags=(1,), (1,), (1,), (1,), (1,), (1,), (1,), (1,)
    libvlc_vlm_change_media = prototype( ("libvlc_vlm_change_media", dll), paramflags )
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
@return 0 on success, -1 on error
"""

if hasattr(dll, 'libvlc_vlm_play_media'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, Instance, ctypes.c_char_p)
    paramflags=(1,), (1,)
    libvlc_vlm_play_media = prototype( ("libvlc_vlm_play_media", dll), paramflags )
    libvlc_vlm_play_media.__doc__ = """Play the named broadcast.
@param p_instance the instance
@param psz_name the name of the broadcast
@return 0 on success, -1 on error
"""

if hasattr(dll, 'libvlc_vlm_stop_media'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, Instance, ctypes.c_char_p)
    paramflags=(1,), (1,)
    libvlc_vlm_stop_media = prototype( ("libvlc_vlm_stop_media", dll), paramflags )
    libvlc_vlm_stop_media.__doc__ = """Stop the named broadcast.
@param p_instance the instance
@param psz_name the name of the broadcast
@return 0 on success, -1 on error
"""

if hasattr(dll, 'libvlc_vlm_pause_media'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, Instance, ctypes.c_char_p)
    paramflags=(1,), (1,)
    libvlc_vlm_pause_media = prototype( ("libvlc_vlm_pause_media", dll), paramflags )
    libvlc_vlm_pause_media.__doc__ = """Pause the named broadcast.
@param p_instance the instance
@param psz_name the name of the broadcast
@return 0 on success, -1 on error
"""

if hasattr(dll, 'libvlc_vlm_seek_media'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, Instance, ctypes.c_char_p, ctypes.c_float)
    paramflags=(1,), (1,), (1,)
    libvlc_vlm_seek_media = prototype( ("libvlc_vlm_seek_media", dll), paramflags )
    libvlc_vlm_seek_media.__doc__ = """Seek in the named broadcast.
@param p_instance the instance
@param psz_name the name of the broadcast
@param f_percentage the percentage to seek to
@return 0 on success, -1 on error
"""

if hasattr(dll, 'libvlc_vlm_show_media'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_char_p, Instance, ctypes.c_char_p)
    paramflags=(1,), (1,)
    libvlc_vlm_show_media = prototype( ("libvlc_vlm_show_media", dll), paramflags )
    libvlc_vlm_show_media.__doc__ = """Return information about the named media as a JSON
string representation.
This function is mainly intended for debugging use,
if you want programmatic access to the state of
a vlm_media_instance_t, please use the corresponding
libvlc_vlm_get_media_instance_xxx -functions.
Currently there are no such functions available for
vlm_media_t though.
@param p_instance the instance
@param psz_name the name of the media,
     if the name is an empty string, all media is described
@return string with information about named media, or NULL on error
"""

if hasattr(dll, 'libvlc_vlm_get_media_instance_position'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_float, Instance, ctypes.c_char_p, ctypes.c_int)
    paramflags=(1,), (1,), (1,)
    libvlc_vlm_get_media_instance_position = prototype( ("libvlc_vlm_get_media_instance_position", dll), paramflags )
    libvlc_vlm_get_media_instance_position.__doc__ = """Get vlm_media instance position by name or instance id
@param p_instance a libvlc instance
@param psz_name name of vlm media instance
@param i_instance instance id
@return position as float or -1. on error
"""

if hasattr(dll, 'libvlc_vlm_get_media_instance_time'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, Instance, ctypes.c_char_p, ctypes.c_int)
    paramflags=(1,), (1,), (1,)
    libvlc_vlm_get_media_instance_time = prototype( ("libvlc_vlm_get_media_instance_time", dll), paramflags )
    libvlc_vlm_get_media_instance_time.__doc__ = """Get vlm_media instance time by name or instance id
@param p_instance a libvlc instance
@param psz_name name of vlm media instance
@param i_instance instance id
@return time as integer or -1 on error
"""

if hasattr(dll, 'libvlc_vlm_get_media_instance_length'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, Instance, ctypes.c_char_p, ctypes.c_int)
    paramflags=(1,), (1,), (1,)
    libvlc_vlm_get_media_instance_length = prototype( ("libvlc_vlm_get_media_instance_length", dll), paramflags )
    libvlc_vlm_get_media_instance_length.__doc__ = """Get vlm_media instance length by name or instance id
@param p_instance a libvlc instance
@param psz_name name of vlm media instance
@param i_instance instance id
@return length of media item or -1 on error
"""

if hasattr(dll, 'libvlc_vlm_get_media_instance_rate'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, Instance, ctypes.c_char_p, ctypes.c_int)
    paramflags=(1,), (1,), (1,)
    libvlc_vlm_get_media_instance_rate = prototype( ("libvlc_vlm_get_media_instance_rate", dll), paramflags )
    libvlc_vlm_get_media_instance_rate.__doc__ = """Get vlm_media instance playback rate by name or instance id
@param p_instance a libvlc instance
@param psz_name name of vlm media instance
@param i_instance instance id
@return playback rate or -1 on error
"""

if hasattr(dll, 'libvlc_vlm_get_media_instance_title'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, Instance, ctypes.c_char_p, ctypes.c_int)
    paramflags=(1,), (1,), (1,)
    libvlc_vlm_get_media_instance_title = prototype( ("libvlc_vlm_get_media_instance_title", dll), paramflags )
    libvlc_vlm_get_media_instance_title.__doc__ = """Get vlm_media instance title number by name or instance id
\bug will always return 0
@param p_instance a libvlc instance
@param psz_name name of vlm media instance
@param i_instance instance id
@return title as number or -1 on error
"""

if hasattr(dll, 'libvlc_vlm_get_media_instance_chapter'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, Instance, ctypes.c_char_p, ctypes.c_int)
    paramflags=(1,), (1,), (1,)
    libvlc_vlm_get_media_instance_chapter = prototype( ("libvlc_vlm_get_media_instance_chapter", dll), paramflags )
    libvlc_vlm_get_media_instance_chapter.__doc__ = """Get vlm_media instance chapter number by name or instance id
\bug will always return 0
@param p_instance a libvlc instance
@param psz_name name of vlm media instance
@param i_instance instance id
@return chapter as number or -1 on error
"""

if hasattr(dll, 'libvlc_vlm_get_media_instance_seekable'):
    prototype=ctypes.CFUNCTYPE(ctypes.c_int, Instance, ctypes.c_char_p, ctypes.c_int)
    paramflags=(1,), (1,), (1,)
    libvlc_vlm_get_media_instance_seekable = prototype( ("libvlc_vlm_get_media_instance_seekable", dll), paramflags )
    libvlc_vlm_get_media_instance_seekable.__doc__ = """Is libvlc instance seekable ?
\bug will always return 0
@param p_instance a libvlc instance
@param psz_name name of vlm media instance
@param i_instance instance id
@return 1 if seekable, 0 if not, -1 if media does not exist
"""

if hasattr(dll, 'libvlc_vlm_get_event_manager'):
    prototype=ctypes.CFUNCTYPE(EventManager, Instance)
    paramflags=( (1, ), )
    libvlc_vlm_get_event_manager = prototype( ("libvlc_vlm_get_event_manager", dll), paramflags )
    libvlc_vlm_get_event_manager.__doc__ = """Get libvlc_event_manager from a vlm media.
The p_event_manager is immutable, so you don't have to hold the lock
@param p_instance a libvlc instance
@return libvlc_event_manager
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
        ('type', Event),
        ('object', ctypes.c_void_p),
        ('u', EventUnion),
        ]

# Decorator for callback methods
callbackmethod=ctypes.CFUNCTYPE(None, ctypes.POINTER(Event), ctypes.c_void_p)

# Example callback method
@callbackmethod
def debug_callback(event, data):
    print "Debug callback method"
    print "Event:", event.contents.type
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
#    libvlc_get_changeset
#    libvlc_errmsg
#    libvlc_clearerr
#    libvlc_get_compiler
#    libvlc_new
#    libvlc_event_type_name
