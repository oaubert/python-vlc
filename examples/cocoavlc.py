#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# Example of using PyCocoa <https://PyPI.org/project/PyCocoa> to create a
# window, table and an application menu to run a video using VLC on macOS.
# The Python-VLC binding <https://PyPI.Python.org/pypi/python-vlc> and the
# corresponding VLC App, see <https://www.VideoLan.org/index.html>.

# PyCocoa version 21.8.18 or later must be installed.

# This VLC player has been tested with VLC 3.0.10-12, 3.0.6-8, 3.0.4,
# 3.0.1-2, 2.2.8 and 2.2.6 and the compatible vlc.py Python-VLC binding
# using 64-bit Python 3.10.0.rc1, 3.9.6, 3.9.0-1, 3.8.10, 3.8.6, 3.7.0-4,
# 3.6.4-5 and 2.7.14-18 on macOS 11.5.2 Big Sur (aka 10.16), 10.15.6
# Catalina, 10.14.6 Mojave and 10.13.4-6 High Sierra.  This player
# does not work with PyPy <https://PyPy.org> nor with Intel(R) Python
# <https://Software.Intel.com/en-us/distribution-for-python>.  Python
# 3.10.0rc1, 3.9.6 and macOS' Python 2.7.16 run on Apple Silicon (C{arm64}),
# all other Python versions run on Intel (C{x86_64}) or I{emulated} Intel
# (C{"arm64_x86_64"}, see function C{pycocoa.machine}).

# MIT License <https://OpenSource.org/licenses/MIT>
#
# Copyright (C) 2017-2021 -- mrJean1 at Gmail -- All Rights Reserved.
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

def _PyPI(package):
    return 'see <https://PyPI.org/project/%s>' % (package,)

__all__  = ('AppVLC',)  # PYCHOK expected
__version__ = '21.08.18'

try:
    import vlc
except ImportError:
    raise ImportError('no %s, %s' % ('vlc.py', _PyPI('Python-VLC')))
try:
    from pycocoa import __name__    as _pycocoa_, \
                        __version__ as _pycocoa_version
except ImportError:
    raise ImportError('no %s, %s' % (_pycocoa_, _PyPI('PyCocoa')))
if _pycocoa_version < __version__:
    raise ImportError('%s %s or later required, %s' % (
                      _pycocoa_, __version__, _PyPI('PyCocoa')))
del _PyPI

# all imports listed explicitly to help PyChecker
from pycocoa import App, app_title, aspect_ratio, bytes2str, closeTables, \
                    get_printer, Item, ItemSeparator, machine, MediaWindow, Menu, \
                    OpenPanel, printf, str2bytes, Table, z1000str, zSIstr

from os.path import basename, getsize, isfile, splitext
import platform as _platform
import sys
from threading import Thread
from time import sleep, strftime, strptime
try:
    from urllib import unquote as mrl_unquote  # Python 2
except ImportError:
    from urllib.parse import unquote as mrl_unquote  # Python 3+

_Adjust  = vlc.VideoAdjustOption  # Enum
# <https://Wiki.VideoLan.org/Documentation:Modules/adjust>
_Adjust3 = {_Adjust.Brightness: (0, 1, 2),
            _Adjust.Contrast:   (0, 1, 2),
            _Adjust.Gamma:   (0.01, 1, 10),
            _Adjust.Hue:     (-180, 0, 180),
            _Adjust.Saturation: (0, 1, 3)}
_Argv0   = splitext(basename(__file__))[0]
_Movies  = '.m4v', '.mov', '.mp4'  # lower-case file types for movies, videos
_Python  = sys.version.split()[0], _platform.architecture()[0]  # PYCHOK false
_Select  = 'Select a video file from the panel'
_VLC_3_  = vlc.__version__.split('.')[0] > '2' and \
           bytes2str(vlc.libvlc_get_version().split(b'.')[0]) > '2'


# <https://Wiki.Videolan.org/Documentation:Modules/marq/#appendix_marq-color>
class _Color(object):  # PYCHOK expected
    Aqua    = 0x00FFFF
    Black   = 0x000000
    Blue    = 0x0000FF
    Fuchsia = 0xFF00FF
    Gray    = 0x808080
    Green   = 0x008000
    Lime    = 0x00FF00
    Maroon  = 0x800000
    Navy    = 0x000080
    Olive   = 0x808000
    Purple  = 0x800080
    Red     = 0xFF0000
    Silver  = 0xC0C0C0
    Teal    = 0x008080
    White   = 0xFFFFFF
    Yellow  = 0xFFFF00

_Color = _Color()  # PYCHOK enum-like


def _macOS(sep=None):
    # get macOS version and extended platform.machine
    t = 'macOS', _platform.mac_ver()[0], machine()
    return sep.join(t) if sep else t


def _mspf(fps):
    # convert frames per second to frame length in millisecs per frame
    return 1000.0 / (fps or 25)


def _ms2str(ms):
    # convert milliseconds to seconds string
    return '%.3f s' % (max(ms, 0) * 0.001,)


def _ratio2str(by, *w_h):
    # aspect ratio as string
    return by.join(map(str, (w_h + ('-', '-'))[:2]))


class AppVLC(App):
    '''The application with callback methods for C{app..._},
       C{menu..._} and C{window..._} events.

       Set things up inside the C{.__init__} and C{.appLauched_}
       methods, start by calling the C{.run} method.
    '''
    adjustr   = ''
    marquee   = None
    logostr   = ''
    player    = None
    raiser    = False
    scale     = 1  # media zoom factor
    sized     = None  # video width, height
    Snapshot  = Item('Snapshot', key='s', alt=True)
    snapshot  = '.png'  # default, or .jpg or .tiff
    snapshots = 0
    Toggle    = None
    video     = None
    window    = None

    def __init__(self, video=None,       # video file name
                       adjustr='',       # vlc.VideoAdjustOption
                       logostr='',       # vlc.VideoLogoOption
                       marquee=False,    # vlc.VideoMarqueeOption
                       raiser=False,     # re-raise errors
                       snapshot='png',   # png, jpg or tiff format
                       title='AppVLC'):  # window title
        super(AppVLC, self).__init__(raiser=raiser, title=title)
        self.adjustr  = adjustr
        self.logostr  = logostr
        self.marquee  = marquee
        self.media    = None
        self.raiser   = raiser
        self.snapshot = '.' + snapshot.lstrip('.').lower()
        self.Toggle   = Item('Play', self.menuToggle_, key='p', ctrl=True)
        self.video    = video

        if self.snapshot == '.png':
            self.player = vlc.MediaPlayer()
#       # XXX does not work, snapshots are always png
#       elif self.snapshot in ('.jpg', '.tiff'):
#           i = vlc.Instance('--snapshot-format', self.snapshot[1:])  # --verbose 2
#           self.player = i.media_player_new()
        else:
            raise ValueError('invalid %s format: %r' % ('snapshot', snapshot))

    def appLaunched_(self, app):
        super(AppVLC, self).appLaunched_(app)
        self.window = MediaWindow(title=self.video or self.title)

        if self.player and self.video and isfile(self.video):
            # the VLC player on macOS needs an ObjC NSView
            self.media = self.player.set_mrl(self.video)
            self.player.set_nsobject(self.window.NSview)

            # if this window is on an external screen,
            # move it to the built-in screen, aka 0
            # if not self.window.screen.isBuiltIn:
            #     self.window.screen = 0  # == BuiltIn

            if self.adjustr:  # preset video options
                for o in self.adjustr.lower().split(','):
                    o, v = o.strip().split('=')
                    o = getattr(_Adjust, o.capitalize(), None)
                    if o is not None:
                        self._VLCadjust(o, value=v)

            if self.marquee:  # set up marquee
                self._VLCmarquee()

            if self.logostr:  # show logo
                self._VLClogo(self.logostr)

            menu = Menu('VLC')
            menu.append(
                # the action/method name for each item
                # is string 'menu' + item.title + '_',
                # without any spaces and trailing dots,
                # see function pycocoa.title2action.
                Item('Open...', key='o'),
                ItemSeparator(),
                Item('Info', key='i'),
                Item('Close Windows', key='w'),
                ItemSeparator(),
                self.Toggle,  # Play >< Pause
                Item('Rewind', key='r', ctrl=True),
                ItemSeparator(),
                Item('Zoom In',  key='+'),
                Item('Zoom Out', key='-'),
                ItemSeparator(),
                Item('Faster', key='>', shift=True),
                Item('Slower', key='<', shift=True))
            if _VLC_3_:
                menu.append(
                    Item('Brighter', key='b', shift=True),
                    Item('Darker',   key='d', shift=True))
            menu.append(
                ItemSeparator(),
                Item('Audio Filters', self.menuFilters_, key='a', shift=True),
                Item('Video Filters', self.menuFilters_, key='v', shift=True))
            menu.append(
                ItemSeparator(),
                self.Snapshot)
            self.append(menu)

        self.menuPlay_(None)
        self.window.front()

    def menuBrighter_(self, item):
        self._brightness(item, +0.1)

    def menuCloseWindows_(self, item):  # PYCHOK expected
        # close window(s) from menu Cmd+W
        # printf('%s %r', 'close_', item)
        if not closeTables():
            self.terminate()

    def menuDarker_(self, item):
        self._brightness(item, -0.1)

    def menuFaster_(self, item):
        self._rate(item, 1.25)

    def menuFilters_(self, item):
        try:
            self.menuPause_(item)
            # display a table of audio/video filters
            t = Table(' Name:150:bold', ' Short:150:Center:center', ' Long:300', 'Help')
            i = self.player.get_instance()
            b = item.title.split()[0]
            for f in sorted(i.audio_filter_list_get() if b == 'Audio'
                       else i.video_filter_list_get()):
                while f and not f[-1]:  # "rstrip" None
                    f = f[:-1]
                t.append(*map(bytes2str, f))

            t.display('VLC %s Filters' % (b,), width=800)

        except Exception as x:
            if self.raiser:
                raise
            printf('%s', x, nl=1, nt=1)

    def menuInfo_(self, item):
        try:
            self.menuPause_(item)
            # display Python, vlc, libVLC, media info table
            p = self.player
            m = p.get_media()

            t = Table(' Name:bold', ' Value:200:Center:center', ' Alt:100')
            t.append(_Argv0, __version__, '20' + __version__)
            t.append('PyCocoa', _pycocoa_version, '20' + _pycocoa_version)
            t.append('Python', *_Python)
            t.append(*_macOS())
            x = 'built-in' if self.window.screen.isBuiltIn else 'external'
            t.append('screen', x, str(self.window.screen.displayID))
            t.separator()

            t.append('vlc.py', vlc.__version__, hex(vlc.hex_version()))
            b = ' '.join(vlc.build_date.split()[:5])
            t.append('built', strftime('%x', strptime(b, '%c')), vlc.build_date)
            t.separator()
            t.append('libVLC', bytes2str(vlc.libvlc_get_version()), hex(vlc.libvlc_hex_version()))
            t.append('libVLC', *bytes2str(vlc.libvlc_get_compiler()).split(None, 1))
            t.separator()

            f = mrl_unquote(bytes2str(m.get_mrl()))
            t.append('media', basename(f), f)
            if f.lower().startswith('file://'):
                z = getsize(f[7:])
                t.append('size', z1000str(z), zSIstr(z))
            t.append('state', str(p.get_state()))
            f = max(p.get_position(), 0)
            t.append('position/length', '%.2f%%' % (f * 100,), _ms2str(p.get_length()))
            f = map(_ms2str, (p.get_time(), m.get_duration()))
            t.append('time/duration', *f)
            t.append('track/count', z1000str(p.video_get_track()), z1000str(p.video_get_track_count()))
            t.separator()

            f = p.get_fps()
            t.append('fps/mspf', '%.6f' % (f,), '%.3f ms' % (_mspf(f),))
            r = p.get_rate()
            t.append('rate', '%s%%' % (int(r * 100),), r)
            w, h = p.video_get_size(0)
            t.append('video size', _ratio2str('x', w, h))  # num=0
            r = _ratio2str(':', *aspect_ratio(w, h))  # p.video_get_aspect_ratio()
            t.append('aspect ratio', r, _ratio2str(':', *self.window.ratio))
            t.append('scale', '%.3f' % (p.video_get_scale(),), '%.3f' % (self.scale,))
            t.separator()

            def VLCadjustr2(option):  # get option value
                lo, _, hi = _Adjust3[option]
                f = self.player.video_get_adjust_float(option)
                p = max(0, (f - lo)) * 100.0 / (hi - lo)
                t = '%.2f %.1f%%' % (f, p)
                # return 2-tuple (value, percentage) as strings
                return t.replace('.0%', '%').replace('.00', '.0').split()

            t.append('brightness', *VLCadjustr2(_Adjust.Brightness))
            t.append('contrast',   *VLCadjustr2(_Adjust.Contrast))
            t.append('gamma',      *VLCadjustr2(_Adjust.Gamma))
            t.append('hue',        *VLCadjustr2(_Adjust.Hue))
            t.append('saturation', *VLCadjustr2(_Adjust.Saturation))
            t.separator()

            s = vlc.MediaStats()  # re-use single MediaStats instance?
            if m.get_stats(s):

                def Kops2bpstr2(bitrate):  # convert Ko/s to bits/sec
                    # bitrates are conventionally in kilo-octets-per-sec
                    return zSIstr(bitrate * 8000, B='bps', K=1000).split()

                t.append('media read',     *zSIstr(s.read_bytes).split())
                t.append('input bitrate',  *Kops2bpstr2(s.input_bitrate))
                if s.input_bitrate > 0:  # XXX approximate caching, based
                    # on <https://GitHub.com/oaubert/python-vlc/issues/61>
                    b = s.read_bytes - s.demux_read_bytes
                    t.append('input caching', _ms2str(b / s.input_bitrate), zSIstr(b))
                t.append('demux read',     *zSIstr(s.demux_read_bytes).split())
                t.append('stream bitrate', *Kops2bpstr2(s.demux_bitrate))

                t.append('video decoded', z1000str(s.decoded_video),      'blocks')
                t.append('video played',  z1000str(s.displayed_pictures), 'frames')
                t.append('video lost',    z1000str(s.lost_pictures),      'frames')

                t.append('audio decoded', z1000str(s.decoded_audio),   'blocks')
                t.append('audio played',  z1000str(s.played_abuffers), 'buffers')
                t.append('audio lost',    z1000str(s.lost_abuffers),   'buffers')

            t.display('Python, VLC & Media Information', width=500)

        except Exception as x:
            if self.raiser:
                raise
            printf('%s', x, nl=1, nt=1)

    def menuOpen_(self, item):
        # stop the current video and show
        # the panel to select another video
        self.menuPause_(item)
        self.badge.label = 'O'
        v = OpenPanel(_Select).pick(_Movies)
        if v:
            self.window.title = self.video = v
            self.player.set_mrl(v)
            self.sized = None

    def menuPause_(self, item, pause=False):  # PYCHOK expected
        # note, .player.pause() pauses and un-pauses the video,
        # .player.stop() stops the video and blanks the window
        if pause or self.player.is_playing():
            self.player.pause()
            self.badge.label = 'S'  # stopped
            self.Toggle.title = 'Play'  # item.title = 'Play'

    def menuPlay_(self, item_or_None):  # PYCHOK expected
        self.player.play()
        self._resizer()
        self.badge.label = 'P'  # Playing
        self.Toggle.title = 'Pause'  # item.title = 'Pause'

    def menuRewind_(self, item):  # PYCHOK expected
        self.player.set_position(0.0)
        # note, can't re-play once at the end
        # self.menuPlay_()
        self.badge.label = 'R'
        self.sized = None

    def menuSlower_(self, item):
        self._rate(item, 0.80)

    def menuSnapshot_(self, item):  # PYCHOK expected
        w = self.lastWindow
        if w:
            self.snapshots += 1
            s = '-'.join((_Argv0,
                          'snapshot%d' % (self.snapshots,),
                           w.__class__.__name__))
            if isinstance(w, MediaWindow):
                self.player.video_take_snapshot(0, s + self.snapshot, 0, 0)
            elif get_printer:  # in PyCocoa 18.08.04+
                get_printer().printView(w.PMview, toPDF=s + '.pdf')

    def menuToggle_(self, item):
        # toggle between Pause and Play
        if self.player.is_playing():
            self.menuPause_(item, pause=True)
        else:
            self.menuPlay_(item)

    def menuZoomIn_(self, item):
        self._zoom(item, 1.25)

    def menuZoomOut_(self, item):
        self._zoom(item, 0.80)

    def windowClose_(self, window):
        # quit or click of window close button
        if window is self.window:
            self.terminate()
        self.Snapshot.isEnabled = False
        super(AppVLC, self).windowClose_(window)

    def windowLast_(self, window):
        self.Snapshot.isEnabled = window.isPrintable or isinstance(window, MediaWindow)
        super(AppVLC, self).windowLast_(window)

    def windowResize_(self, window):
        if window is self.window:
            self._resizer()
        super(AppVLC, self).windowResize_(window)

    def windowScreen_(self, window, change):
        if window is self.window:
            self._resizer()
        super(AppVLC, self).windowScreen_(window, change)

    def _brightness(self, unused, fraction):  # change brightness
        self._VLCadjust(_Adjust.Brightness, fraction)

    def _contrast(self, unused, fraction):  # change contrast
        self._VLCadjust(_Adjust.Contrast, fraction)

    def _gamma(self, unused, fraction):  # change gamma
        self._VLCadjust(_Adjust.Gamma, fraction)

    def _hue(self, unused, fraction):  # change hue
        self._VLCadjust(_Adjust.Hue, fraction)

    def _saturation(self, unused, fraction):  # change saturation
        self._VLCadjust(_Adjust.Saturation, fraction)

    def _rate(self, unused, factor):  # change the video rate
        r = max(0.2, min(10.0, self.player.get_rate() * factor))
        self.player.set_rate(r)

    def _resizer(self):  # adjust aspect ratio and marquee height
        if self.sized:
            # window's contents' aspect ratio
            self.window.ratio = self.sized
        else:
            Thread(target=self._sizer).start()

    def _sizer(self, secs=0.1):
        while True:
            w, h = self.player.video_get_size(0)
            # the first call(s) returns (0, 0),
            # subsequent calls return (w, h)
            if h > 0 and w > 0:
                # window's contents' aspect ratio
                self.window.ratio = self.sized = w, h
                break
            elif secs > 0.001:
                sleep(secs)
            else:  # one-shot
                break

    def _VLCadjust(self, option, fraction=0, value=None):
        # adjust a video option like brightness, contrast, etc.
        p = self.player
        # <https://Wiki.VideoLan.org/Documentation:Modules/adjust>
        # note, .Enable must be set to 1, but once is sufficient
        p.video_set_adjust_int(_Adjust.Enable, 1)
        try:
            lo, _, hi = _Adjust3[option]
            if value is None:
                v = p.video_get_adjust_float(option)
            else:
                v = float(value)
            if fraction:
                v += fraction * (hi - lo)
            v = float(max(lo, min(hi, v)))
            p.video_set_adjust_float(option, v)
        except (KeyError, ValueError):
            pass

    def _VLClogo(self, logostr):
        # add a video logo, example "python cocoavlc.py -logo
        # cone-altglass2.png\;cone-icon-small.png ..."
        p = self.player
        g = vlc.VideoLogoOption  # Enum
        # <https://Wiki.VideoLan.org/Documentation:Modules/logo>
        p.video_set_logo_int(g.enable, 1)
        p.video_set_logo_int(g.position, vlc.Position.Center)
        p.video_set_logo_int(g.opacity, 128)  # 0-255
        # p.video_set_logo_int(g.delay, 1000)  # millisec
        # p.video_set_logo_int(g.repeat, -1)  # forever
        p.video_set_logo_string(g.file, logostr)

    def _VLCmarquee(self, size=36):
        # put video marquee at the bottom-center
        p = self.player
        m = vlc.VideoMarqueeOption  # Enum
        # <https://Wiki.VideoLan.org/Documentation:Modules/marq>
        p.video_set_marquee_int(m.Enable, 1)
        p.video_set_marquee_int(m.Size, int(size))  # pixels
        p.video_set_marquee_int(m.Position, vlc.Position.Bottom)
        p.video_set_marquee_int(m.Opacity, 255)  # 0-255
        p.video_set_marquee_int(m.Color, _Color.Yellow)
        p.video_set_marquee_int(m.Timeout, 0)  # millisec, 0==forever
        p.video_set_marquee_int(m.Refresh, 1000)  # millisec (or sec?)
        p.video_set_marquee_string(m.Text, str2bytes('%Y-%m-%d  %T  %z'))

    def _zoom(self, unused, factor):
        # zoom the video rate in/out
        if factor > 0:
            self.scale *= factor
            self.player.video_set_scale(self.scale)  # if abs(self.scale - 1.0) > 0.01 else 0.0)


if __name__ == '__main__':  # MCCABE 24

    def _Adjustr():
        a = []  # get adjust default values
        for n in _Adjust._enum_names_.values():
            try:
                _, d, _ = _Adjust3[getattr(_Adjust, n)]
                a.append('%s=%s' % (n, d))
            except KeyError:  # ignore .Enable
                pass
        return ','.join(sorted(a))

    _adjustr  = ''
    _argv0    = basename(sys.argv[0])  # _Title
    _Argv0    = splitext(_argv0)[0]
    _logostr  = ''
    _marquee  = False
    _raiser   = False
    _snapshot = 'png'
    _timeout  = None
    _title    = splitext(_argv0)[0]
    _video    = None

    args = sys.argv[1:]
    while args and args[0].startswith('-'):
        o = args.pop(0)
        t = o.lower()
        if t in ('-h', '--help'):
            u = ('-h|--help',
                 '-adjust %s' % (_Adjustr(),))
            if _VLC_3_:  # requires VLC 3+ and libvlc 3+
                u += ('-logo <image_file_name>[\\;<image_file_name>...]',
                      '-marquee')
            u += ('-raiser',
                  '-snapshot-format jpg|png|tiff',
                  '-timeout <secs>',
                  '-title <string>',
                  '-v|--version',
                  '<video_file_name>')
            printf('usage:  [%s]', ']  ['.join(u), argv0=_argv0)
            sys.exit(0)
        elif '-adjust'.startswith(t) and len(t) > 1 and args:
            _adjustr = args.pop(0)
        elif '-logo'.startswith(t) and len(t) > 1 and args and _VLC_3_:
            _logostr = args.pop(0)
        elif '-marquee'.startswith(t) and len(t) > 1 and _VLC_3_:
            _marquee = True
        elif '-raiser'.startswith(t) and len(t) > 1:
            _raiser = True
        elif '-snapshot-format'.startswith(t) and len(t) > 1 and args:
            _snapshot = args.pop(0)
        elif '-timeout'.startswith(t) and len(t) > 3 and args:
            _timeout = args.pop(0)
        elif '-title'.startswith(t) and len(t) > 3 and args:
            _title = args.pop(0).strip()
        elif t in ('-v', '--version'):
            # Print version of this cocoavlc.py, PyCocoa, etc.
            print('%s: %s (%s %s %s)' % (basename(__file__), __version__,
                                        _pycocoa_, _pycocoa_version,
                                        _macOS(sep=' ')))
            try:
                vlc.print_version()  # PYCHOK expected
                vlc.print_python()   # PYCHOK expected
            except AttributeError:
                pass
            sys.exit(0)
        else:
            printf('invalid option: %s', o, argv0=_argv0)
            sys.exit(1)

    if _raiser:  # get traceback at SIG- faults or ...
        try:  # ... use: python3 -X faulthandler ...
            import faulthandler
            faulthandler.enable()
        except ImportError:  # not in Python 3.3-
            pass

    if args:
        _video = args.pop(0)
    else:
        printf('- %s', _Select.lower(), argv0=_argv0, nl=1, nt=1)
        app_title(_title)  # App.title when there's no App yet
        _video = OpenPanel('Select a video file').pick(_Movies)

    if _video:
        app = AppVLC(video=_video, adjustr=_adjustr,
                                   logostr=_logostr,
                                   marquee=_marquee,
                                    raiser=_raiser,
                                  snapshot=_snapshot,
                                     title=_title)
        app.run(timeout=_timeout)  # never returns
