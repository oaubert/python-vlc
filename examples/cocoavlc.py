
# -*- coding: utf-8 -*-

# Original <http://code.google.com/archive/p/cocoa-python>

# Example of using ctypes with PyCocoa to create a window and table
# with an application menu to run a video using VLC.  The VLC App must
# be installed on macOS, see <http://www.VideoLan.org/index.html> with
# the Python-VLC binding, see <http://PyPI.Python.org/pypi/python-vlc>.

# This VLC player has only been tested with VLC 2.2.6 and 3.0.1 and the
# corresponding vlc.py Python-VLC binding using 64-bit Python 2.7.14 and
# 3.6.4 on macOS 10.13.4 High Sierra.  The player does not work (yet)
# with PyPy Python <http://pypy.org> nor with Intel(R) Python
# <http://software.intel.com/en-us/distribution-for-python>.

# MIT License <http://opensource.org/licenses/MIT>
#
# Copyright (C) 2017-2018 -- mrJean1 at Gmail dot com
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

import os
import platform
import sys
from time import strftime, strptime

try:  # the imports listed explicitly to help PyChecker
    from pycocoa import App, aspect_ratio, closeTables, Item, \
                        MediaWindow, Menu, MenuBar, OpenPanel, printf, \
                        Table, z1000str, zSIstr, \
                        __version__ as __PyCocoa__  # PYCHOK false
except ImportError:
    raise ImportError('no %s module, see %s' % ('pycocoa',
                      '<http://PyPI.Python.org/pypi/PyCocoa>'))
try:
    import vlc
except ImportError:
    raise ImportError('no %s module, see %s' % ('vlc.py',
                      '<http://PyPI.Python.org/pypi/python-vlc>'))

__all__  = ('AppVLC',)
__version__ = '18.04.26'

_macOS  = platform.mac_ver()[0:3:2]  # PYCHOK false
_Movies = '.mov', '.mp4'  # lower-case file types for movies, videos
_Python = sys.version.split()[0], platform.architecture()[0]  # PYCHOK false
_Title  = os.path.basename(__file__)

_b2str = vlc.bytes_to_str  # pycocoa.bytes2str
_str2b = vlc.str_to_bytes  # pycocoa.str2bytes


def _mspf(fps):
    # convert frames per second to frame length in millisecs
    return 1000.0 / (fps or 25)


class AppVLC(App):
    '''The application with callback methods for app..._, menu..._
    and window..._ events.  Set things up inside the __init__ and
    appLauched_ methods, start by calling the run method.
    '''
    ratio  = 2  # number of retries to get media aspect ratio
    scale  = 1  # media zoom factor
    video  = None  # media file name
    window = None

    def __init__(self, title=_Title, video=None, **attrs):
        super(AppVLC, self).__init__(title=title, **attrs)
        self.panel  = OpenPanel('Select a video file')
        self.player = vlc.MediaPlayer(video) if video else None

    def appLaunched_(self, app):
        App.appLaunched_(self, app)  # super(AppVLC, self)...
        self.window = MediaWindow(title=self.video or self.title)

        if self.player:
            # the player needs an NSView object
            self.player.set_nsobject(self.window.NSview)

            menu = Menu('VLC')
            menu.append(
                # the action/method for each item is
                # 'menu' + item.title + '_', with
                # spaces and dots removed, see the
                # method Item.title2action.
                menu.item('Open...', key='o'),
                menu.separator(),
                menu.item('Info', key='i'),
                menu.item('Close Windows', key='w'),
                menu.separator(),
                menu.item('Play',   key='p', ctrl=True),
                menu.item('Pause',  key='s', ctrl=True),
                menu.item('Rewind', key='r', ctrl=True),
                menu.separator(),
                menu.item('Zoom In',  key='+'),
                menu.item('Zoom Out', key='-'),
                menu.item('Faster', key='>', shift=True),
                menu.item('Slower', key='<', shift=True),
            )
            self.append(menu)

        self.menuPlay_(None)
        # adjust the contents' aspect ratio
        self.windowResize_(self.window)
        self.window.front()

    def menuCloseWindows_(self, item):  # PYCHOK expected
        # close window(s) from menu Cmd+W
        # printf('%s %r', 'close_', item)
        if not closeTables():
            self.terminate()

    def menuFaster_(self, item):
        self._rate(item, 1.25)

    def menuInfo_(self, item):
        try:
            self.menuPause_(item)

            # display Python, vlc, libVLC, media info
            p = self.player
            m = p.get_media()

            t = Table(' Name', ' Value:200', ' Alt:300')
            t.append('PyCocoa', __PyCocoa__, '20' + __version__)
            t.append('Python', *_Python)
            t.append('macOS', *_macOS)
            t.separator()

            t.append('vlc.py', vlc.__version__, hex(vlc.hex_version()))
            b = ' '.join(vlc.build_date.split()[:5])
            t.append('built', strftime('%x', strptime(b, '%c')), vlc.build_date)
            t.separator()
            t.append('libVLC', _b2str(vlc.libvlc_get_version()), hex(vlc.libvlc_hex_version()))
            t.append('libVLC', *_b2str(vlc.libvlc_get_compiler()).split(None, 1))
            t.separator()

            f = _b2str(m.get_mrl())
            t.append('media', os.path.basename(f), f)
            if f.startswith('file:///'):
                z = os.path.getsize(f[7:])
                t.append('size', z1000str(z), zSIstr(z))
            t.append('state', str(p.get_state()))
            t.append('track/count', z1000str(p.video_get_track()), z1000str(p.video_get_track_count()))
            t.append('time/duration', z1000str(p.get_time()), z1000str(m.get_duration()))
            f = max(p.get_position(), 0)
            t.append('position', '%.2f%%' % (f * 100,), f)
            t.separator()

            f = p.get_fps()
            t.append('fps/mspf', '%.6f' % (f,), '%.3f ms' % (_mspf(f),))
            r = p.get_rate()
            t.append('rate', '%s%%' % (int(r * 100),), r)
            w, h = p.video_get_size(0)
            r = aspect_ratio(w, h) or ''
            if r:
                r = '%s:%s' % r
            t.append('video size', '%sx%s' % (w, h))  # num=0
            t.append('aspect ratio', str(p.video_get_aspect_ratio()), r)
            t.append('scale', '%.3f' % (p.video_get_scale(),), '%.3f' % (self.scale,))
            t.display('Python, VLC & Media Information', width=600)

        except Exception as x:
            printf('%r', x, nl=1, nt=1)

    def menuOpen_(self, item):
        # stop the current video and show
        # the panel to select another video
        self.menuPause_(item)
        self.badge.label = 'O'
        video = self.panel.pick(_Movies)
        if video:
            inst = self.player.get_instance()
            media = inst.media_new(video)
            self.player.set_media(media)
            self.window.title = video

    def menuPause_(self, item):  # PYCHOK expected
        # note, .pause() pauses and un-pauses the video,
        # .stop() stops the video and blanks the window
        if self.player.is_playing():
            self.player.pause()
            self.badge.label = 'S'

    def menuPlay_(self, item_or_None):  # PYCHOK expected
        self.player.play()
        self.badge.label = 'P'

    def menuRewind_(self, item):  # PYCHOK expected
        self.player.set_position(0.0)
        # can't re-play once at the end
        # self.player.play()
        self.badge.label = 'R'

    def menuSlower_(self, item):
        self._rate(item, 0.80)

    def menuZoomIn_(self, item):
        self._zoom(item, 1.25)

    def menuZoomOut_(self, item):
        self._zoom(item, 0.80)

    def windowClose_(self, window):
        # quit or click of window close button
        if window is self.window:
            self.terminate()
        App.windowClose_(self, window)  # super(AppVLC, self)...

    def windowResize_(self, window):
        if window is self.window and self.ratio:
            # get and maintain the aspect ratio
            # (the first player.video_get_size()
            #  call returns (0, 0), subsequent
            #  calls return (w, h) correctly)
            self.window.ratio = self.player.video_get_size(0)
            self.ratio -= 1
        App.windowResize_(self, window)  # super(AppVLC, self)...

    def _rate(self, unused, factor):
        r = self.player.get_rate() * factor
        if 0.2 < r < 10.0:
            self.player.set_rate(r)

    def _zoom(self, unused, factor):
        self.scale *= factor
        self.player.video_set_scale(self.scale)


if __name__ == '__main__':

    _argv0   = os.path.basename(sys.argv[0])  # _Title
    _raiser  = False
    _timeout = None
    _title   = os.path.splitext(_argv0)[0]

    args = sys.argv[1:]
    while args and args[0].startswith('-'):
        o = args.pop(0)
        t = o.lower()
        if t in ('-h', '--help'):
            printf('usage:  [-h|--help]  [-raiser]  [-timeout <secs>]  [-title <string>]  [video_file_name]')
            sys.exit(0)
        elif '-raiser'.startswith(t) and len(t) > 1:
            _raiser = True
        elif '-timeout'.startswith(t) and len(t) > 3 and args:
            _timeout = args.pop(0)
        elif '-title'.startswith(t) and len(t) > 3 and args:
            _title = args.pop(0).strip()
        else:
            printf('invalid option: %s', o)
            sys.exit(1)

    if _raiser:  # get traceback at SIG- faults or ...
        try:  # ... use: python3 -X faulthandler ...
            import faulthandler
            faulthandler.enable()
        except ImportError:  # not in Python 3.3-
            pass

    if args:
        video = args.pop(0)
    else:
        printf('- select a video from the files panel', nl=1, nt=1)
        video = OpenPanel('Select a video file').pick(_Movies)

    if video:
        app = AppVLC(title=_title, raiser=_raiser, video=video)
        app.run(timeout=_timeout)  # never returns
