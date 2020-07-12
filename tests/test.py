#! /usr/bin/env python
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

import logging
logger = logging.getLogger(__name__)

import ctypes
import re
import os
import unittest

try:
    import urllib.parse as urllib # python3
except ImportError:
    import urllib # python2

try:
    from pathlib import Path
except ImportError:
    Path = None

try:
    import vlc
except ImportError:
    import generated.vlc as vlc

try:
    from generator import generate
except ImportError:
    generate = None

SAMPLE = os.path.join(os.path.dirname(__file__), 'samples/sample.mp4')
print ("Checking " + vlc.__file__)


class TestAuxMethods(unittest.TestCase):
    if Path is not None:
        def test_try_fspath_path_like_object(self):
            test_object = Path('test', 'path')
            result = vlc.try_fspath(test_object)
            self.assertEqual(result, os.path.join('test', 'path'))

    def test_try_fspath_str_object(self):
        test_object = os.path.join('test', 'path')
        result = vlc.try_fspath(test_object)
        self.assertEqual(result, os.path.join('test', 'path'))


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

    if hasattr(vlc, 'AudioOutputDeviceTypes'):
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

    def test_meta_get(self):
        self.assertTrue(os.path.exists(SAMPLE))
        m = vlc.Media(SAMPLE)
        m.parse()
        self.assertEqual(m.get_meta(vlc.Meta.Title), 'Title')
        self.assertEqual(m.get_meta(vlc.Meta.Artist), 'Artist')
        self.assertEqual(m.get_meta(vlc.Meta.Description), 'Comment')
        self.assertEqual(m.get_meta(vlc.Meta.Album), 'Album')
        self.assertEqual(m.get_meta(vlc.Meta.AlbumArtist), 'Album Artist')
        self.assertEqual(m.get_meta(vlc.Meta.Date), '2013')
        self.assertEqual(m.get_meta(vlc.Meta.Genre), 'Sample')

    def notest_log_get_context(self):
        """Semi-working test for log_get_context.

        It crashes with a Segmentation fault after displaying some
        messages. This should be fixed + a better test should be
        devised so that we do not clutter the terminal.
        """
        libc = ctypes.cdll.LoadLibrary("libc.{}".format("so.6" if os.uname()[0] == 'Linux' else "dylib"))
        @vlc.CallbackDecorators.LogCb
        def log_handler(instance, log_level, ctx, fmt, va_list):
            bufferString = ctypes.create_string_buffer(4096)
            libc.vsprintf(bufferString, fmt, ctypes.cast(va_list, ctypes.c_void_p))
            msg = bufferString.value.decode('utf-8')
            module, _file, _line = vlc.libvlc_log_get_context(ctx)
            module = module.decode('utf-8')
            try:
                logger.warn(u"log_level={log_level}, module={module}, msg={msg}".format(log_level=log_level, module=module, msg=msg))
            except Exception as e:
                logger.exception(e)
                import pdb; pdb.set_trace()

        instance = vlc.Instance('--vout dummy --aout dummy')
        instance.log_set(log_handler, None)
        player = instance.media_player_new()
        media = instance.media_new(SAMPLE)
        player.set_media(media)
        player.play()


if generate is not None:
    # Test internal generator only in python3
    class TestREs(unittest.TestCase):
        def test_api_re_comment(self):
            self.assertIsNone(generate.api_re.match('/* Avoid unhelpful warnings from libvlc with our deprecated APIs */'))

        def test_api_re_match(self):
            self.assertIsNotNone(generate.api_re.match('LIBVLC_API void libvlc_clearerr (void);'))

        def test_at_param_re(self):
            match = generate.at_param_re.match('@param p_mi media player')
            self.assertEqual(match.group(1, 2), ('@param p_mi', ' media player'))

        def test_class_re_method(self):
            self.assertIsNone(generate.class_re.match('    def __new__(cls, arg=None):\n'))

        def test_class_re(self):
            match = generate.class_re.match('class Instance:\n')
            self.assertEqual(match.group(1), 'Instance')

        def test_def_re(self):
            self.assertEqual(
                generate.def_re.findall(
                    '\n    def __new__(cls, *args):\n\n   def get_instance(self):\n\n    def add_media(self, mrl):\n\n'),
                ['__new__', 'get_instance', 'add_media'])

        def test_enum_pair_re_1(self):
            self.assertEqual(generate.enum_pair_re.split('LIBVLC_WARNING=3'), ['LIBVLC_WARNING', '3'])

        def test_enum_pair_re_2(self):
            self.assertEqual(
                generate.enum_pair_re.split('libvlc_AudioChannel_Left    =  3'), ['libvlc_AudioChannel_Left', '3'])

        def test_forward_re(self):
            match = generate.forward_re.match('VLC_FORWARD_DECLARE_OBJECT(libvlc_media_list_t *) libvlc_media_subitems')
            self.assertEqual(match.groups(), ('libvlc_media_list_t *', ' libvlc_media_subitems'))

    class TestPar(unittest.TestCase):
        def test_invalid(self):
            INVALID_TESTS = [
                # function pointers
                "int(*name)()",
                "int *(*name)()",
                "void *(*name)(const char * buffer)",
                "void(*name)(const char *, int)",
                "void(*)(const char *, int)",
            ]

            for test_instance in INVALID_TESTS:
                self.assertIsNone(generate.Par.parse_param(test_instance))

        def test_valid(self):
            VALID_TESTS = [
                # named param
                ('int integer_value', ('int', 'integer_value', [False])),
                ('float decimal_value', ('float', 'decimal_value', [False])),

                # anonymous param
                ('float', ('float', '', [False])),

                # pointer
                ('int *pointer_to_integer', ('int*', 'pointer_to_integer', [False, False])),
                ('const unsigned char * pointer_to_character', ('unsigned char*', 'pointer_to_character', [True, False])),
                ('const unsigned char * const pointer_to_character', ('unsigned char*', 'pointer_to_character', [True, True])),

                # pointer-to-pointers
                ('int * const * ptr_to_constptr_to_int',    ('int**', 'ptr_to_constptr_to_int', [False, True, False])),
                ('int *const * ptr_to_constptr_to_int',     ('int**', 'ptr_to_constptr_to_int', [False, True, False])),
                ('int * const* ptr_to_constptr_to_int',     ('int**', 'ptr_to_constptr_to_int', [False, True, False])),
                ('int* const* ptr_to_constptr_to_int',      ('int**', 'ptr_to_constptr_to_int', [False, True, False])),

                ('const int * const * ptr_to_constptr_to_constint', ('int**', 'ptr_to_constptr_to_constint', [True, True, False])),
                ('const int *const * ptr_to_constptr_to_constint',  ('int**', 'ptr_to_constptr_to_constint', [True, True, False])),
                ('const int * const* ptr_to_constptr_to_constint',  ('int**', 'ptr_to_constptr_to_constint', [True, True, False])),
                ('const int* const* ptr_to_constptr_to_constint',   ('int**', 'ptr_to_constptr_to_constint', [True, True, False])),

                ('const int * * ptr_to_ptr_to_constint',    ('int**', 'ptr_to_ptr_to_constint', [True, False, False])),
                ('const int ** ptr_to_ptr_to_constint',     ('int**', 'ptr_to_ptr_to_constint', [True, False, False])),
                ('const int * *ptr_to_ptr_to_constint',     ('int**', 'ptr_to_ptr_to_constint', [True, False, False])),
                ('const int* *ptr_to_ptr_to_constint',      ('int**', 'ptr_to_ptr_to_constint', [True, False, False])),
            ]

            for parse_raw, (expected_type, expected_name, expected_constness) in VALID_TESTS:
                param = generate.Par.parse_param(parse_raw)
                self.assertEqual(expected_type, param.type)
                self.assertEqual(expected_name, param.name)
                self.assertListEqual(expected_constness, param.constness)


if __name__ == '__main__':
    logging.basicConfig()
    unittest.main()
