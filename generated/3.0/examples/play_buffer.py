#!/usr/bin/env python3

# Author:   A.Invernizzi (@albestro on GitHub)
# Date:     Jun 03, 2020

# MIT License <http://OpenSource.org/licenses/MIT>
#
# Copyright (C) 2020 -- A. Invernizzi, @albestro on github
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

"""
Example usage of VLC API function `libvlc_media_new_callbacks`
This function allows to create a VLC media `libvlc_media_t` specifying custom
callbacks where the user can define how to manage and read the stream of data.

The general use case for this is when you have data in memory and you want to
play it (e.g. audio stream from a web radio).

In this example, we are going to read playable data from files in a specified
folder. In case you would want to read from a file, it is not the best way to do it,
but for the sake of this example we are going to read data into memory from files.

The example tries to highlight the separation of concerns between the callbacks and
the application logic, so it would hopefully make clear how to integrate the VLC API
with existing libraries.

In particular, we have two main parts:
    - StreamProvider: which is a class that implements the logic; "scrape" a folder
    for files with a specific extensions, and provide methods that retrieves data.
    - VLC callabacks that uses a StreamProvider object
"""

import argparse
import ctypes
import os

import vlc


class StreamProviderDir(object):
    def __init__(self, rootpath, file_ext):
        self._media_files = []
        self._rootpath = rootpath
        self._file_ext = file_ext
        self._index = 0

    def open(self):
        """
        this function is responsible of opening the media.
        it could have been done in the __init__, but it is just an example

        in this case it scan the specified folder, but it could also scan a
        remote url or whatever you prefer.
        """

        print("read file list")
        for entry in os.listdir(self._rootpath):
            if os.path.splitext(entry)[1] == f".{self._file_ext}":
                self._media_files.append(os.path.join(self._rootpath, entry))
        self._media_files.sort()

        print("playlist:")
        for index, media_file in enumerate(self._media_files):
            print(f"[{index}] {media_file}")

    def release_resources(self):
        """
        In this example this function is just a placeholder,
        in a more complex example this may release resources after the usage,
        e.g. closing the socket from where we retrieved media data
        """
        print("releasing stream provider")

    def seek(self, offset):
        """
        Again, a placeholder, not useful for the example
        """
        print(f"requested seek with offset={offset}")

    def get_data(self):
        """
        It reads the current file in the list and returns the binary data
        In this example it reads from file, but it could have downloaded data from an url
        """
        print(f"reading file [{self._index}] ", end='')

        if self._index == len(self._media_files):
            print("file list is over")
            return b''

        print(f"{self._media_files[self._index]}")
        with open(self._media_files[self._index], 'rb') as stream:
            data = stream.read()

        self._index = self._index + 1

        return data


# HERE THERE ARE THE CALLBACKS USED BY THE MEDIA CREATED IN THE "MAIN"
# a callback in its simplest form is a python function decorated with the specific @vlc.CallbackDecorators.*

@vlc.CallbackDecorators.MediaOpenCb
def media_open_cb(opaque, data_pointer, size_pointer):
    print("OPEN", opaque, data_pointer, size_pointer)

    stream_provider = ctypes.cast(opaque, ctypes.POINTER(ctypes.py_object)).contents.value

    stream_provider.open()

    data_pointer.contents.value = opaque
    size_pointer.value = 1 ** 64 - 1

    return 0


@vlc.CallbackDecorators.MediaReadCb
def media_read_cb(opaque, buffer, length):
    print("READ", opaque, buffer, length)

    stream_provider = ctypes.cast(opaque, ctypes.POINTER(ctypes.py_object)).contents.value

    new_data = stream_provider.get_data()
    bytes_read = len(new_data)

    if bytes_read > 0:
        buffer_array = ctypes.cast(buffer, ctypes.POINTER(ctypes.c_char * bytes_read))
        for index, b in enumerate(new_data):
            buffer_array.contents[index] = ctypes.c_char(b)

    print(f"just read f{bytes_read}B")
    return bytes_read


@vlc.CallbackDecorators.MediaSeekCb
def media_seek_cb(opaque, offset):
    print("SEEK", opaque, offset)

    stream_provider = ctypes.cast(opaque, ctypes.POINTER(ctypes.py_object)).contents.value

    stream_provider.seek(offset)

    return 0


@vlc.CallbackDecorators.MediaCloseCb
def media_close_cb(opaque):
    print("CLOSE", opaque)

    stream_provider = ctypes.cast(opaque, ctypes.POINTER(ctypes.py_object)).contents.value

    stream_provider.release_resources()


# MAIN
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='play files found in specified media folder (in alphabetic order)',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
            'media_folder',
            help='where to find files to play')
    parser.add_argument(
            '--extension',
            default='ts',
            help='file extension of the files to play')
    args = parser.parse_args()

    # helper object acting as media data provider
    # it is just to highlight how the opaque pointer in the callback can be used
    # and that the logic can be isolated from the callbacks
    stream_provider = StreamProviderDir(args.media_folder, args.extension)

    # these two lines to highlight how to pass a python object using ctypes
    # it is verbose, but you can see the steps required
    stream_provider_obj = ctypes.py_object(stream_provider)
    stream_provider_ptr = ctypes.byref(stream_provider_obj)

    # create an instance of vlc
    instance = vlc.Instance()

    # setup the callbacks for the media
    media = instance.media_new_callbacks(
            media_open_cb,
            media_read_cb,
            media_seek_cb,
            media_close_cb,
            stream_provider_ptr)
    player = media.player_new_from_media()

    # play/stop
    player.play()
    input("press enter to quit")
    player.stop()
