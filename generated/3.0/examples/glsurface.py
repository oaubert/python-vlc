#! /usr/bin/env python3

#
# GlSurface example code for VLC Python bindings
# Copyright (C) 2020 Daniël van Adrichem <daniel5gh@spiet.nl>

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

"""VLC GlSurface example
"""

import time
import ctypes
from threading import Lock

import numpy as np
from OpenGL.GL import (GL_TEXTURE_2D, glTexSubImage2D, glTexImage2D,
                       GL_BGR, GL_RGB,
                       GL_UNSIGNED_BYTE)
import vlc

class Surface(object):
    """A lockable image buffer
    """
    def __init__(self, w, h):
        self._width = w
        self._height = h

        # size in bytes when RV32 *4 or RV24 * 3
        self._row_size = self._width * 3
        self._buf_size = self._height * self._row_size
        # allocate buffer
        self._buf1 = np.zeros(self._buf_size, dtype=np.ubyte)
        # get pointer to buffer
        self._buf_p = self._buf1.ctypes.data_as(ctypes.c_void_p)
        self._lock = Lock()

    def update_gl(self):
        # with self._lock:
        glTexSubImage2D(GL_TEXTURE_2D,
                        0, 0, 0,
                        self._width,
                        self._height,
                        GL_BGR,
                        GL_UNSIGNED_BYTE,
                        self._buf1)

    def create_texture_gl(self):
        glTexImage2D(GL_TEXTURE_2D,
                     0,
                     GL_RGB,
                     self._width,  # width
                     self._height,  # height
                     0,
                     GL_BGR,
                     GL_UNSIGNED_BYTE,
                     None)

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def row_size(self):
        return self._row_size

    @property
    def buf(self):
        return self._buf1

    @property
    def buf_pointer(self):
        return self._buf_p

    def lock(self):
        self._lock.acquire()

    def unlock(self):
        self._lock.release()

    def __enter__(self, *args):
        return self._lock.__enter__(*args)

    def __exit__(self, *args):
        return self._lock.__exit__(*args)

    def get_libvlc_lock_callback(self):
        @vlc.VideoLockCb
        def _cb(opaque, planes):
            self._lock.acquire()
            planes[0] = self._buf_p

        return _cb

    def get_libvlc_unlock_callback(self):
        @vlc.VideoUnlockCb
        def _cb(opaque, picta, planes):
            self._lock.release()

        return _cb

if __name__ == '__main__':
    import sys
    player = vlc.MediaPlayer(sys.argv[1])
    # play and stop so video_get_size gets a correct value
    # setting all callbacks to None prevents a window being created on play
    player.video_set_callbacks(None, None, None, None)
    # play and stop so video_get_size gets a correct value
    player.play()
    time.sleep(1)
    player.stop()
    w, h = player.video_get_size()
    surface = Surface(w, h)
    # need to keep a reference to the CFUNCTYPEs or else it will get GCed
    _lock_cb = surface.get_libvlc_lock_callback()
    _unlock_cb = surface.get_libvlc_unlock_callback()
    player.video_set_callbacks(_lock_cb, _unlock_cb, None, None)
    player.video_set_format(
        "RV24",
        surface.width,
        surface.height,
        surface.row_size)
    # this starts populating the surface's buf with pixels, from another thread
    player.play()
    # in main thread, where gl context is current:
    # FIXME: add some code to embed the surface + a mainloop
    # v.surface.update_gl()
