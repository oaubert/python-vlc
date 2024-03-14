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

from generator.generate import Enum, Func, Struct, Par, Parser, Val
logger = logging.getLogger(__name__)

import ctypes
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
except SyntaxError:
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
        if vlc.__version__ < "4":
            vp.contents.yaw = 2
            self.assertEqual(vp.contents.yaw, 2)
        else:
            vp.contents.f_yaw = 2
            self.assertEqual(vp.contents.f_yaw, 2)

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
        if vlc.__version__ < "4":
            self.assertEqual(audiotrack.original_fourcc, 0x6134706d)
        else:
            self.assertEqual(audiotrack.i_original_fourcc, 0x6134706d)
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

    class TestParser(unittest.TestCase):
        def get_parser(self, code_file: Path | str) -> Parser:
            return Parser(
                [],
                code_file,
                "./tests/test_parser_inputs/libvlc_version.h",
            )

        def test_parse_enums(self):
            expected_enums = [
                Enum(
                    "libvlc_enum_no_values_specified",
                    "enum",
                    [
                        Val("G", "0"),
                        Val("H", "1"),
                        Val("I", "2"),
                    ],
                    "",
                ),
                Enum(
                    "libvlc_enum_all_values_specified",
                    "enum",
                    [
                        Val("J", "2"),
                        Val("K", "4"),
                        Val("L", "6"),
                    ],
                    "",
                ),
                Enum(
                    "libvlc_enum_values_specified_or_not",
                    "enum",
                    [
                        Val("M", "5"),
                        Val("N", "6"),
                        Val("O", "8"),
                        Val("P", "9"),
                    ],
                    "",
                ),
                Enum(
                    "libvlc_enum_with_docs",
                    "enum",
                    [
                        Val("Q", "5"),
                        Val("R", "6"),
                        Val("S", "8"),
                        Val("T", "9"),
                    ],
                    """Some Doxygen
documentation
that spans
multiple lines""",
                ),
                Enum(
                    "libvlc_enum_with_hex_values",
                    "enum",
                    [
                        Val("U", "0x1"),
                        Val("V", "0xf"),
                    ],
                    "",
                ),
                Enum(
                    "libvlc_enum_with_bit_shifted_values",
                    "enum",
                    [
                        Val("W", "7471104"),
                        Val("X", "6750208"),
                    ],
                    "",
                ),
                Enum(
                    "libvlc_enum_no_values_specified_t",
                    "enum",
                    [
                        Val("GG", "0"),
                        Val("HH", "1"),
                        Val("II", "2"),
                    ],
                    "",
                ),
                Enum(
                    "libvlc_enum_all_values_specified_t",
                    "enum",
                    [
                        Val("JJ", "2"),
                        Val("KK", "4"),
                        Val("LL", "6"),
                    ],
                    "",
                ),
                Enum(
                    "libvlc_enum_values_specified_or_not_t",
                    "enum",
                    [
                        Val("MM", "5"),
                        Val("NN", "6"),
                        Val("OO", "8"),
                        Val("PP", "9"),
                    ],
                    "",
                ),
                Enum(
                    "libvlc_enum_with_docs_t",
                    "enum",
                    [
                        Val("QQ", "5"),
                        Val("RR", "6"),
                        Val("SS", "8"),
                        Val("TT", "9"),
                    ],
                    """Some Doxygen
documentation
that spans
multiple lines""",
                ),
                Enum(
                    "libvlc_enum_with_hex_values_t",
                    "enum",
                    [
                        Val("UU", "0x1"),
                        Val("VV", "0xf"),
                    ],
                    "",
                ),
                Enum(
                    "libvlc_enum_with_bit_shifted_values_t",
                    "enum",
                    [
                        Val("WW", "7471104"),
                        Val("XX", "6750208"),
                    ],
                    "",
                ),
                Enum(
                    "libvlc_enum_t",
                    "enum",
                    [
                        Val("ZZ", "0"),
                    ],
                    "",
                ),
            ]

            p = self.get_parser("./tests/test_parser_inputs/enums.h")
            self.assertListEqual(p.enums_with_ts, expected_enums)
            
        def test_parse_structs(self):
            expected_structs = [
                Struct(
                    "libvlc_struct_no_values_specified",
                    "struct",
                    [
                        Par("a", "int",[False]),
                        Par("b", "char",[False]),
                        Par("c", "double",[False]),
                    ],
                    "",
                ),
                Struct(
                    "libvlc_struct_all_values_specified",
                    "struct",
                    [
                        Par("a", "int",[False]),
                        Par("b", "char",[False]),
                        Par("c", "double",[False]),
                    ],
                    "",
                ),
                Struct(
                    "libvlc_struct_with_docs",
                    "struct",
                    [
                        Par("a", "int",[False]),
                        Par("b", "char",[False]),
                        Par("c", "double",[False]),
                    ],
                    """Some Doxygen
documentation
that spans
multiple lines""",
                ),
                Struct(
                    "libvlc_struct_with_const",
                    "struct",
                    [
                        Par("x", "char",[True]),
                    ],
                    "",
                ),
                Struct(
                    "libvlc_struct_pointers",
                    "struct",
                    [
                        Par("x", "int*",[True,False]),
                        Par("y", "double*",[False,True]),
                    ],
                    "",
                ),
                Struct(
                    "libvlc_struct_no_values_specified_t",
                    "struct",
                    [
                        Par("a", "int",[False]),
                        Par("b", "char",[False]),
                        Par("c", "double",[False]),
                    ],
                    "",
                ),
                Struct(
                    "libvlc_struct_all_values_specified_t",
                    "struct",
                    [
                        Par("a", "int",[False]),
                        Par("b", "char",[False]),
                        Par("c", "double",[False]),
                    ],
                    "",
                ),
                Struct(
                    "libvlc_struct_with_docs_t",
                    "struct",
                    [
                        Par("a", "int",[False]),
                        Par("b", "char",[False]),
                        Par("c", "double",[False]),
                    ],
                     """Some Doxygen
documentation
that spans
multiple lines""",
                ),
                Struct(
                    "libvlc_struct_t",
                    "struct",
                    [
                        Par("x", "char",[False]),
                    ],
                    "",
                ),
                Struct(
                    "libvlc_struct_with_const_t",
                    "struct",
                    [
                        Par("x", "char",[True]),
                    ],
                    "",
                ),
                Struct(
                    "libvlc_struct_pointers_t",
                    "struct",
                    [
                        Par("x", "int*",[True,False]),
                        Par("y", "double*",[False,True]),
                    ],
                    "",
                ),
            ]

            p = self.get_parser("./tests/test_parser_inputs/structs.h")
            self.assertListEqual(p.structs_with_ts, expected_structs)

        def test_parse_funcs(self):
            expected_funcs = [
                Func("libvlc_simple", "void", [], ""),
                Func("libvlc_simple_with_void", "void", [], ""),
                Func("libvlc_attribute_on_the_previous_line", "void", [], ""),
                Func(
                    "libvlc_with_docs",
                    "void",
                    [],
                    """Some Doxygen
documentation
that spans
multiple lines""",
                ),
                Func(
                    "libvlc_simple_types",
                    "char",
                    [
                        Par("a", "int", [False]),
                        Par("b", "float", [False]),
                    ],
                    "",
                ),
                Func(
                    "libvlc_pointer_as_return_type",
                    "char*",
                    [
                        Par("a", "int", [False]),
                        Par("b", "float", [False]),
                    ],
                    "",
                ),
                Func(
                    "libvlc_pointer_as_return_type_with_qualifier",
                    "char*",
                    [
                        Par("a", "int", [False]),
                        Par("b", "float", [False]),
                    ],
                    "",
                ),
                Func(
                    "libvlc_pointers_and_qualifiers_everywhere",
                    "char*",
                    [
                        Par("c1", "char*", [True, False]),
                        Par("c2", "char*", [True, False]),
                    ],
                    "",
                ),
                Func(
                    "libvlc_multiple_pointers",
                    "char**",
                    [
                        Par("c1", "char**", [False, False, False]),
                        Par("c2", "char***", [False, False, False, False]),
                    ],
                    "",
                ),
                Func(
                    "libvlc_multiple_pointers_and_qualifiers",
                    "char**",
                    [
                        Par("c1", "char**", [True, False, True]),
                        Par(
                            "c2",
                            "char***",
                            [False, True, True, True],
                        ),
                    ],
                    "",
                ),
            ]

            p = self.get_parser("./tests/test_parser_inputs/funcs.h")
            self.assertListEqual(p.funcs_with_ts, expected_funcs)

        def test_parse_callbacks(self):
            expected_callbacks = [
                Func("libvlc_simple_cb", "void", [], ""),
                Func("libvlc_simple_with_void_cb", "void", [], ""),
                Func(
                    "libvlc_simple_with_void_pointers_cb",
                    "void*",
                    [
                        Par("p", "void*", [False, False]),
                    ],
                    "",
                ),
                Func(
                    "libvlc_simple_types_cb",
                    "char",
                    [
                        Par("a", "int", [False]),
                        Par("b", "float", [False]),
                    ],
                    "",
                ),
                Func(
                    "libvlc_with_docs_cb",
                    "char",
                    [
                        Par("a", "int", [False]),
                        Par("b", "float", [False]),
                    ],
                    """Some Doxygen
documentation
that spans
multiple lines""",
                ),
                Func(
                    "libvlc_one_pointer_cb",
                    "char*",
                    [
                        Par("c1", "char*", [False, False]),
                        Par("c2", "char*", [False, False]),
                        Par("c3", "char*", [False, False]),
                    ],
                    "",
                ),
                Func(
                    "libvlc_one_pointer_and_const_cb",
                    "char*",
                    [
                        Par("c1", "char*", [True, False]),
                        Par("c2", "char*", [False, False]),
                        Par("c3", "char*", [False, False]),
                    ],
                    "",
                ),
                Func(
                    "libvlc_multiple_pointers_cb",
                    "char**",
                    [
                        Par("c1", "char**", [False, False, False]),
                        Par("c2", "char***", [False, False, False, False]),
                        Par("c3", "char****", [False, False, False, False, False]),
                    ],
                    "",
                ),
                Func(
                    "libvlc_multiple_pointers_with_const_cb",
                    "char**",
                    [
                        Par("c1", "char**", [True, True, False]),
                        Par("c2", "char***", [False, True, True, True]),
                        Par("c3", "char****", [False, True, False, True, False]),
                    ],
                    "",
                ),
            ]

            p = self.get_parser("./tests/test_parser_inputs/callbacks.h")
            self.assertListEqual(p.callbacks_with_ts, expected_callbacks)

if __name__ == '__main__':
    logging.basicConfig()
    unittest.main()
