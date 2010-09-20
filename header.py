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
U{libvlc<http://wiki.videolan.org/ExternalAPI>}.

You can find documentation at U{http://www.advene.org/download/python-ctypes/}.

Basically, the most important class is L{Instance}, which is used to
create a libvlc Instance. From this instance, you can then create
L{MediaPlayer} and L{MediaListPlayer} instances.
"""

import logging
import ctypes
import sys

build_date="This will be replaced by the build date"

# Used for win32 and MacOS X
detected_plugin_path=None

if sys.platform == 'linux2':
    try:
        dll=ctypes.CDLL('libvlc.so')
    except OSError:
        dll=ctypes.CDLL('libvlc.so.5')
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

# GENERATED_ENUMS

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


class AudioOutput(ctypes.Structure):
    def __str__(self):
        return "vlc.AudioOutput(%s:%s)" % (self.name, self.description)
AudioOutput._fields_= [
    ('name', ctypes.c_char_p),
    ('description', ctypes.c_char_p),
    ('next', ctypes.POINTER(AudioOutput)),
    ]

class TrackDescription(ctypes.Structure):
    def __str__(self):
        return "vlc.TrackDescription(%d:%s)" % (self.id, self.name)
TrackDescription._fields_= [
    ('id', ctypes.c_int),
    ('name', ctypes.c_char_p),
    ('next', ctypes.POINTER(TrackDescription)),
    ]
def track_description_list(head):
    """Convert a TrackDescription linked list to a python list, and release the linked list.
    """
    l = []
    item = head
    while item:
        l.append( (item.contents.id, item.contents.name) )
        item = item.contents.next
    if head:
        libvlc_track_description_release(head)
    return l

### End of header.py ###
