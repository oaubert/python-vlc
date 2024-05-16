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

"""Unittest module for testing the VLC bindings generated."""

import logging

logger = logging.getLogger(__name__)

import ctypes
import os
import unittest
from time import sleep

try:
    import urllib.parse as urllib  # python3
except ImportError:
    import urllib  # python2

try:
    from pathlib import Path
except ImportError:
    Path = None

try:
    import vlc
except ImportError:
    import generated.vlc as vlc


SAMPLE = os.path.join(os.path.dirname(__file__), "samples/sample.mp4")
print("Checking " + vlc.__file__)

__calls_stats__ = {}


def call_stats(f):
    def wrapper(*args, **kwargs):
        global __calls_stats__
        ret = f(*args, **kwargs)
        if f.__name__ in __calls_stats__:
            __calls_stats__[f.__name__]["n_calls"] += 1
            __calls_stats__[f.__name__]["last_return_value"] = ret
        else:
            __calls_stats__[f.__name__] = {"n_calls": 1, "last_return_value": ret}
        return ret

    return wrapper


class TestAuxMethods(unittest.TestCase):
    if Path is not None:

        def test_try_fspath_path_like_object(self):
            test_object = Path("test", "path")
            result = vlc.try_fspath(test_object)
            self.assertEqual(result, os.path.join("test", "path"))

    def test_try_fspath_str_object(self):
        test_object = os.path.join("test", "path")
        result = vlc.try_fspath(test_object)
        self.assertEqual(result, os.path.join("test", "path"))


class TestVLCAPI(unittest.TestCase):
    # def setUp(self):
    #    self.seq = range(10)
    # self.assert_(element in self.seq)

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

    if hasattr(vlc, "AudioOutputDeviceTypes"):

        def test_enum_output_device_type(self):
            self.assertEqual(vlc.AudioOutputDeviceTypes._2F2R.value, 4)

    def test_enum_output_channel(self):
        self.assertEqual(vlc.AudioOutputChannel.Dolbys.value, 5)

    # Basic libvlc tests
    def test_instance_creation(self):
        i = vlc.Instance()
        self.assertTrue(i)

    def test_libvlc_media(self):
        mrl = "/tmp/foo.avi"
        i = vlc.Instance()
        m = i.media_new(mrl)
        self.assertEqual(m.get_mrl(), "file://" + mrl)

    def test_wrapper_media(self):
        mrl = "/tmp/foo.avi"
        m = vlc.Media(mrl)
        self.assertEqual(m.get_mrl(), "file://" + mrl)

    def test_wrapper_medialist(self):
        mrl1 = "/tmp/foo.avi"
        mrl2 = "/tmp/bar.avi"
        l = vlc.MediaList([mrl1, mrl2])
        self.assertEqual(l[1].get_mrl(), "file://" + mrl2)

    def test_libvlc_player(self):
        mrl = "/tmp/foo.avi"
        i = vlc.Instance()
        p = i.media_player_new(mrl)
        self.assertEqual(p.get_media().get_mrl(), "file://" + mrl)

    def test_libvlc_none_object(self):
        i = vlc.Instance()
        p = i.media_player_new()
        p.set_media(None)
        self.assertEqual(p.get_media(), None)

    def test_libvlc_player_state(self):
        mrl = "/tmp/foo.avi"
        i = vlc.Instance()
        p = i.media_player_new(mrl)
        self.assertEqual(p.get_state(), vlc.State.NothingSpecial)

    # Test that the VLC bindings can handle special characters in the filenames
    def test_libvlc_player_special_chars(self):
        mrl = "/tmp/Test 韓 Korean.mp4"
        i = vlc.Instance()
        m = i.media_new(mrl)
        url_encoded_mrl = urllib.quote(mrl.encode("utf-8"))
        self.assertEqual(m.get_mrl(), "file://" + url_encoded_mrl)

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

        instance = vlc.Instance("--vout dummy --aout dummy")
        instance.log_set(log_handler, None)
        _player = instance.media_player_new()

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
            self.assertEqual(audiotrack.original_fourcc, 0x6134706D)
        else:
            self.assertEqual(audiotrack.i_original_fourcc, 0x6134706D)
        self.assertEqual(m.get_duration(), 5568)

    def test_meta_get(self):
        self.assertTrue(os.path.exists(SAMPLE))
        m = vlc.Media(SAMPLE)
        m.parse()
        self.assertEqual(m.get_meta(vlc.Meta.Title), "Title")
        self.assertEqual(m.get_meta(vlc.Meta.Artist), "Artist")
        self.assertEqual(m.get_meta(vlc.Meta.Description), "Comment")
        self.assertEqual(m.get_meta(vlc.Meta.Album), "Album")
        self.assertEqual(m.get_meta(vlc.Meta.AlbumArtist), "Album Artist")
        self.assertEqual(m.get_meta(vlc.Meta.Date), "2013")
        self.assertEqual(m.get_meta(vlc.Meta.Genre), "Sample")

    def notest_log_get_context(self):
        """Semi-working test for log_get_context.

        It crashes with a Segmentation fault after displaying some
        messages. This should be fixed + a better test should be
        devised so that we do not clutter the terminal.
        """
        libc = ctypes.cdll.LoadLibrary(
            "libc.{}".format("so.6" if os.uname()[0] == "Linux" else "dylib")
        )

        @vlc.CallbackDecorators.LogCb
        def log_handler(instance, log_level, ctx, fmt, va_list):
            bufferString = ctypes.create_string_buffer(4096)
            libc.vsprintf(bufferString, fmt, ctypes.cast(va_list, ctypes.c_void_p))
            msg = bufferString.value.decode("utf-8")
            module, _file, _line = vlc.libvlc_log_get_context(ctx)
            module = module.decode("utf-8")
            try:
                logger.warn(
                    "log_level={log_level}, module={module}, msg={msg}".format(
                        log_level=log_level, module=module, msg=msg
                    )
                )
            except Exception as e:
                logger.exception(e)
                import pdb

                pdb.set_trace()

        instance = vlc.Instance("--vout dummy --aout dummy")
        instance.log_set(log_handler, None)
        player = instance.media_player_new()
        media = instance.media_new(SAMPLE)
        player.set_media(media)
        player.play()

    if vlc.__generator_version__ >= "2":

        def test_dialog_cbs(self):
            global __calls_stats__
            __calls_stats__ = {}

            class MyData:
                def __init__(self, data):
                    self.data = data

            @vlc.DialogCbs.PfDisplayError
            @call_stats
            def display_error_cb(p_data, psz_title, psz_text):
                data = ctypes.cast(
                    p_data, ctypes.POINTER(ctypes.py_object)
                ).contents.value.data
                return data

            @vlc.DialogCbs.PfDisplayLogin
            @call_stats
            def display_login_cb(
                p_data, p_id, psz_title, psz_text, psz_default_username, b_ask_store
            ):
                data = ctypes.cast(
                    p_data, ctypes.POINTER(ctypes.py_object)
                ).contents.value.data
                return data

            @vlc.DialogCbs.PfDisplayQuestion
            @call_stats
            def display_question_cb(
                p_data,
                p_id,
                psz_title,
                psz_text,
                i_type,
                psz_cancel,
                psz_actypesion1,
                psz_actypesion2,
            ):
                data = ctypes.cast(
                    p_data, ctypes.POINTER(ctypes.py_object)
                ).contents.value.data
                return data

            @vlc.DialogCbs.PfDisplayProgress
            @call_stats
            def display_progress_cb(
                p_data,
                p_id,
                psz_title,
                psz_text,
                b_indeterminate,
                f_position,
                psz_cancel,
            ):
                data = ctypes.cast(
                    p_data, ctypes.POINTER(ctypes.py_object)
                ).contents.value.data
                return data

            @vlc.DialogCbs.PfCancel
            @call_stats
            def cancel_cb(p_data, p_id):
                data = ctypes.cast(
                    p_data, ctypes.POINTER(ctypes.py_object)
                ).contents.value.data
                return data

            @vlc.DialogCbs.PfUpdateProgress
            @call_stats
            def update_progress_cb(p_data, p_id, f_position, psz_text):
                data = ctypes.cast(
                    p_data, ctypes.POINTER(ctypes.py_object)
                ).contents.value.data
                return data

            inst = vlc.Instance("--vout dummy --aout dummy")
            dialog_cbs = vlc.DialogCbs()
            dialog_cbs.pf_display_error = display_error_cb
            dialog_cbs.pf_display_login = display_login_cb
            dialog_cbs.pf_display_question = display_question_cb
            dialog_cbs.pf_display_progress = display_progress_cb
            dialog_cbs.pf_cancel = cancel_cb
            dialog_cbs.pf_update_progress = update_progress_cb
            dialog_cbs_ptr = ctypes.pointer(dialog_cbs)
            data_str = "some data"
            data = MyData(data_str)
            data_obj = ctypes.py_object(data)
            data_ptr = ctypes.byref(data_obj)
            vlc.libvlc_dialog_set_callbacks(inst, dialog_cbs_ptr, data_ptr)

            # Check that display_error_cb gets called when an invalid MRL is played.
            # Other callbacks are hard to trigger progammatically, so we only test the error one.
            m = inst.media_new_path("invalid_path_that_will_trigger_error_dialog")
            mp = vlc.MediaPlayer(inst)
            mp.set_media(m)
            mp.play()
            # need some time for the player to launch and the error dialog to get triggered
            sleep(0.2)
            mp.release()
            m.release()
            inst.release()

            assert __calls_stats__["display_error_cb"]["n_calls"] == 1
            assert __calls_stats__["display_error_cb"]["last_return_value"] == data_str


if __name__ == "__main__":
    logging.basicConfig()
    unittest.main()
