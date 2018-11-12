#! /usr/bin/python
# This Python file uses the following encoding: utf-8

#
# Code generator for python ctypes bindings for VLC
# Copyright (C) 2009 the VideoLAN team
# $Id: $
#
# Authors: Olivier Aubert <contact at olivieraubert.net>
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

"""Unittest module.
"""

import os
import unittest
try:
    import urllib.parse as urllib # python3
except ImportError:
    import urllib # python2

try:
    import vlc
except ImportError:
    import generated.vlc as vlc

SAMPLE = os.path.join(os.path.dirname(__file__), 'samples/sample.mp4')
print ("Checking " + vlc.__file__)

class TestVLCAPI(unittest.TestCase):
    #def setUp(self):
    #    self.seq = range(10)
    #self.assert_(element in self.seq)

    # We check enum definitions against hardcoded values. In case of
    # failure, check that the reason is not a change in the .h
    # definitions.
    def test_enum_event_type(self):
        self.assertEqual(vlc.EventType.MediaStateChanged.value, 5)

    def test_enum_meta(self):
        self.assertEqual(vlc.Meta.Description.value, 6)

    def test_enum_state(self):
        self.assertEqual(vlc.State.Playing.value, 3)

    def test_enum_playback_mode(self):
        self.assertEqual(vlc.PlaybackMode.repeat.value, 2)

    def test_enum_marquee_int_option(self):
        self.assertEqual(vlc.VideoMarqueeOption.Size.value, 6)

    def test_enum_output_device_type(self):
        self.assertEqual(vlc.AudioOutputDeviceTypes._2F2R.value, 4)

    def test_enum_output_channel(self):
        self.assertEqual(vlc.AudioOutputChannel.Dolbys.value, 5)

    # Basic libvlc tests
    def test_instance_creation(self):
        i=vlc.Instance()
        self.assertTrue(i)

    def test_libvlc_media(self):
        mrl='/tmp/foo.avi'
        i=vlc.Instance()
        m=i.media_new(mrl)
        self.assertEqual(m.get_mrl(), 'file://' + mrl)

    def test_wrapper_media(self):
        mrl = '/tmp/foo.avi'
        m = vlc.Media(mrl)
        self.assertEqual(m.get_mrl(), 'file://' + mrl)

    def test_wrapper_medialist(self):
        mrl1 = '/tmp/foo.avi'
        mrl2 = '/tmp/bar.avi'
        l = vlc.MediaList( [mrl1, mrl2] )
        self.assertEqual(l[1].get_mrl(), 'file://' + mrl2)

    def test_libvlc_player(self):
        mrl='/tmp/foo.avi'
        i=vlc.Instance()
        p=i.media_player_new(mrl)
        self.assertEqual(p.get_media().get_mrl(), 'file://' + mrl)

    def test_libvlc_none_object(self):
        i=vlc.Instance()
        p=i.media_player_new()
        p.set_media(None)
        self.assertEqual(p.get_media(), None)

    def test_libvlc_player_state(self):
        mrl='/tmp/foo.avi'
        i=vlc.Instance()
        p=i.media_player_new(mrl)
        self.assertEqual(p.get_state(), vlc.State.NothingSpecial)

    # Test that the VLC bindings can handle special characters in the filenames
    def test_libvlc_player_special_chars(self):
        mrl = u'/tmp/Test 韓 Korean.mp4'
        i = vlc.Instance()
        m = i.media_new(mrl)
        url_encoded_mrl = urllib.quote(mrl.encode('utf-8'))
        self.assertEqual(m.get_mrl(), 'file://' + url_encoded_mrl)

    def test_libvlc_video_new_viewpoint(self):
        vp = vlc.libvlc_video_new_viewpoint()
        vp.contents.yaw = 2
        self.assertEqual(vp.contents.yaw, 2)

    def no_test_callback(self):

        @vlc.CallbackDecorators.LogCb
        def log_handler(instance, log_level, ctx, fmt, va_list):
            try:
                module, _file, _line = vlc.libvlc_log_get_context(ctx)
            except TypeError:
                print("vlc.libvlc_log_get_context(ctx)")

        instance = vlc.Instance('--vout dummy --aout dummy')
        instance.log_set(log_handler, None)
        player = instance.media_player_new()

    def test_equalizer(self):
        val = 9.5
        eq = vlc.AudioEqualizer()
        self.assertEqual(eq.get_amp_at_index(0), 0)
        eq.set_amp_at_index(val, 1)
        self.assertEqual(eq.get_amp_at_index(1), val)

    def test_tracks_get(self):
        self.assertTrue(os.path.exists(SAMPLE))
        m = vlc.Media(SAMPLE)
        m.parse()
        # Audiotrack is the second one
        audiotrack = list(m.tracks_get())[1]
        self.assertEqual(audiotrack.language, b"eng")
        self.assertEqual(audiotrack.description, b"Stereo")
        self.assertEqual(audiotrack.bitrate, 83051)
        self.assertEqual(m.get_duration(), 5568)

if __name__ == '__main__':
    unittest.main()
