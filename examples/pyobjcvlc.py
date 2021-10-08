#! /usr/bin/env python3

# -*- coding: utf-8 -*-

# License at the end of this file.  This module is equivalent to
# PyCocoa/test/simple_VLCplayer.py but based on PyObjC instead
# of PyCocoa <https://PyPI.org/project/PyCocoa>.  Until macOS
# release Catalina, macOS' Python includes PyObjC.

# See also a more comprehensive VLC player example cocoavlc.py
# <https://GitHub.com/oaubert/python-vlc/tree/master/examples>

# This VLC player has only been tested with VLC 2.2.8 and 3.0.8,
# and a compatible vlc.py <https://PyPI.org/project/Python-VLC>
# binding using Python 2.7.10 with macOS' PyObjC 2.5.1 and Python
# 3.7.4 with PyObjC 5.2b1 on macOS 10.13.6 High Sierra or 10.14.6
# Mojave, all in 64-bit only.  This player has not been tested
# on iOS, nor with PyPy and Intel(R) Python.

from os.path import basename  # PYCHOK expected
from platform import architecture, mac_ver  # PYCHOK false
import sys

_argv0 = basename(__file__)
if not sys.platform.startswith('darwin'):
    raise ImportError('%s only supported on %s' % (_argv0, 'macOS'))

class _ImportError(ImportError):  # PYCHOK expected
    def __init__(self, package, PyPI):
        PyPI = '<https://PyPI.org/project/%s>' % (PyPI,)
        t = 'no module %s, see %s' % (package, PyPI)
        ImportError.__init__(self, t)

try:  # PYCHOK expected
    from objc import __version__ as __PyObjC__
except ImportError:
    raise _ImportError('objc', 'PyObjC')

# the imports listed explicitly to help PyChecker
from Cocoa import NSAlternateKeyMask, NSApplication, \
                  NSBackingStoreBuffered, NSBundle, \
                  NSCommandKeyMask, NSControlKeyMask, \
                  NSMakeRect, NSMenu, NSMenuItem, \
                  NSObject, \
                  NSScreen, NSShiftKeyMask, NSSize, \
                  NSView, NSWindow
try:
    from Cocoa import NSWindowStyleMaskClosable, NSWindowStyleMaskMiniaturizable, \
                      NSWindowStyleMaskResizable, NSWindowStyleMaskTitled
except ImportError:  # previously, NSWindowStyleMaskXxx was named NSXxxWindowMask
    from Cocoa import NSClosableWindowMask as NSWindowStyleMaskClosable, \
                      NSMiniaturizableWindowMask as NSWindowStyleMaskMiniaturizable, \
                      NSResizableWindowMask as NSWindowStyleMaskResizable, \
                      NSTitledWindowMask as NSWindowStyleMaskTitled

NSStr = bytes if sys.version_info.major < 3 else str
NSWindowStyleMaskUsual = NSWindowStyleMaskClosable | NSWindowStyleMaskMiniaturizable \
                       | NSWindowStyleMaskResizable | NSWindowStyleMaskTitled

__all__  = ('simpleVLCplay',)
__version__ = '19.09.27'


try:  # all imports listed explicitly to help PyChecker
    from math import gcd  # Python 3+
except ImportError:
    try:
        from fractions import gcd  # Python 2-
    except ImportError:

        def gcd(a, b):
            a, b = abs(a), abs(b)
            if a < b:
                a, b = b, a
            while b:
                a, b = b, (a % b)
            return a


def mspf(fps):
    '''Convert frames per second to frame length in millisecs.
    '''
    return 1000.0 / (fps or 25)


def nsBundleRename(title, match='Python'):
    '''Change the bundle title if the current title matches.

       @param title: New bundle title (C{str}).
       @keyword match: Optional, previous title to match (C{str}).

       @return: The previous bundle title (C{str}) or None.

       @note: Used to mimick C{NSApplication.setTitle_(ns_title)},
              the application name shown in the menu bar.
    '''
    # <https://Developer.Apple.com/documentation/
    #        foundation/nsbundle/1495012-bundlewithpath>
    # ns = NSBundle.bundleWithPath_(os.path.abspath(match))
    p, ns = None, NSBundle.mainBundle()
    if ns:
        ns = ns.localizedInfoDictionary() or ns.infoDictionary()
        if ns:
            k = NSStr('CFBundleName')
            p = ns.objectForKey_(k) or None
            if title and match in (p, '', None):  # can't be empty
                ns.setObject_forKey_(NSStr(title), k)
    return p


def printf(fmt, *args, **kwds):  # argv0='', nl=0, nt=0
    '''Formatted print I{fmt % args} with optional keywords.

       @param fmt: Print-like format (C{str}).
       @param args: Optional arguments to include (I{all positional}).
       @keyword argv0: Optional prefix (C{str}).
       @keyword nl: Number of leading blank lines (C{int}).
       @keyword nt: Number of trailing blank lines (C{int}).
    '''
    a = kwds.get('argv0', _argv0)
    t = (fmt % args) if args else fmt
    nl = '\n' * kwds.get('nl', 0)
    nt = '\n' * kwds.get('nt', 0)
    print(''.join((nl, a, ' ', t, nt)))


def terminating(app, timeout):
    '''Terminate C{app} after C{timeout} seconds.

       @param app: The application (C{NSApplication} instance).
       @patam timeout: Time in seconds (C{float}).
    '''
    try:
        secs = float(timeout)
    except (TypeError, ValueError):
        secs = 0

    if secs > 0:
        from threading import Thread

        def _t():
            from time import sleep

            sleep(secs + 0.5)
            app.terminate_()

        Thread(target=_t).start()


class _NSDelegate(NSObject):
    '''(INTERNAL) Delegate for NSApplication and NSWindow,
        handling PyObjC events, notifications and callbacks.
    '''
    app    = None  # NSApplication
    NSItem = None  # NSMenuItem
    player = None  # vlc.MediaPlayer
    ratio  = 2     # aspect_ratio calls
    title  = ''    # top-level menu title
    video  = None  # video file name
    window = None  # main NSWindow

    def applicationDidFinishLaunching_(self, notification):

        # the VLC player needs an NSView object
        self.window, view = _Window2(title=self.video or self.title)
        # set the window's delegate to the app's to
        # make method .windowWillClose_ work, see
        # <https://Gist.GitHub.com/kaloprominat/6105220>
        self.window.setDelegate_(self)
        # pass viewable to VLC player, see PyObjC Generated types ...
        # <https://PyObjC.ReadTheDocs.io/en/latest/core/type-wrapper.html>
        self.player.set_nsobject(view.__c_void_p__())

        menu = NSMenu.alloc().init()  # create main menu
        menu.addItem_(_MenuItem('Full ' + 'Screen', 'enterFullScreenMode:', 'f', ctrl=True))  # Ctrl-Cmd-F, Esc to exit
        menu.addItem_(_MenuItem('Info', 'info:', 'i'))

        menu.addItem_(_MenuItemSeparator())
        self.NSitem = _MenuItem('Pause', 'toggle:', 'p', ctrl=True)  # Ctrl-Cmd-P
        menu.addItem_(self.NSitem)
        menu.addItem_(_MenuItem('Rewind', 'rewind:', 'r', ctrl=True))  # Ctrl-Cmd-R

        menu.addItem_(_MenuItemSeparator())
        menu.addItem_(_MenuItem('Hide ' + self.title, 'hide:', 'h'))  # Cmd-H, implied
        menu.addItem_(_MenuItem('Hide Others', 'hideOtherApplications:', 'h', alt=True))  # Alt-Cmd-H
        menu.addItem_(_MenuItem('Show All', 'unhideAllApplications:'))  # no key

        menu.addItem_(_MenuItemSeparator())
        menu.addItem_(_MenuItem('Quit ' + self.title, 'terminate:', 'q'))  # Cmd-Q

        subMenu = NSMenuItem.alloc().init()
        subMenu.setSubmenu_(menu)

        menuBar = NSMenu.alloc().init()
        menuBar.addItem_(subMenu)
        self.app.setMainMenu_(menuBar)

        self.player.play()
        # adjust the contents' aspect ratio
        self.windowDidResize_(None)

    def info_(self, notification):
        try:
            p = self.player
            if p.is_playing():
                p.pause()
            m = p.get_media()
            v = sys.modules[p.__class__.__module__]  # import vlc
            b = v.bytes_to_str

            printf(__version__, nl=1)
            # print Python, vlc, libVLC, media info
            printf('PyObjC %s', __PyObjC__, nl=1)
            printf('Python %s %s', sys.version.split()[0], architecture()[0])
            printf('macOS %s', ' '.join(mac_ver()[0:3:2]), nt=1)

            printf('vlc.py %s (%#x)', v.__version__, v.hex_version())
            printf('built: %s', v.build_date)

            printf('libVLC %s (%#x)', b(v.libvlc_get_version()), v.libvlc_hex_version())
            printf('libVLC %s', b(v.libvlc_get_compiler()), nt=1)

            printf('media: %s', b(m.get_mrl()))
            printf('state: %s', p.get_state())

            printf('track/count: %s/%s', p.video_get_track(), p.video_get_track_count())
            printf('time/duration: %s/%s ms', p.get_time(), m.get_duration())
            printf('position/length: %.2f%%/%s ms', p.get_position() * 100.0, p.get_length())
            f = p.get_fps()
            printf('fps: %.3f (%.3f ms)', f, mspf(f))
            printf('rate: %s', p.get_rate())

            w, h = p.video_get_size(0)
            printf('video size: %sx%s', w, h)
            r = gcd(w, h) or ''
            if r and w and h:
                r = ' (%s:%s)' % (w // r, h // r)
            printf('aspect ratio: %s%s', p.video_get_aspect_ratio(), r)

            printf('scale: %.3f', p.video_get_scale())
            o = p.get_nsobject()  # for macOS only
            printf('nsobject: %r (%#x)', o, o, nt=1)
        except Exception as x:
            printf('%r', x, nl=1, nt=1)

    def rewind_(self, notification):
        self.player.set_position(0.0)
        # can't re-play once at the end
        # self.player.play()

    def toggle_(self, notification):
        # toggle between Pause and Play
        if self.player.is_playing():
            # note, .pause() pauses and un-pauses the video,
            # .stop() stops the video and blanks the window
            self.player.pause()
            t = 'Play'
        else:
            self.player.play()
            t = 'Pause'
        self.NSitem.setTitle_(NSStr(t))

    def windowDidResize_(self, notification):
        if self.window and self.ratio:
            # get and maintain the aspect ratio
            # (the first player.video_get_size()
            #  call returns (0, 0), subsequent
            #  calls return (w, h) correctly)
            w, h = self.player.video_get_size(0)
            r = gcd(w, h)
            if r and w and h:
                r = NSSize(w // r , h // r)
                self.window.setContentAspectRatio_(r)
                self.ratio -= 1

    def windowWillClose_(self, notification):
        self.app.terminate_(self)


def _MenuItem(label, action=None, key='', alt=False, cmd=True, ctrl=False, shift=False):
    '''New NS menu item with action and optional shortcut key.
    '''
    # <http://Developer.Apple.com/documentation/appkit/nsmenuitem/1514858-initwithtitle>
    ns = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                            NSStr(label), NSStr(action), NSStr(key))
    if key:
        mask = 0
        if alt:
            mask |= NSAlternateKeyMask
        if cmd:
            mask |= NSCommandKeyMask
        if ctrl:
            mask |= NSControlKeyMask
        if shift:
            mask |= NSShiftKeyMask  # NSAlphaShiftKeyMask
        if mask:
            ns.setKeyEquivalentModifierMask_(mask)
    return ns


def _MenuItemSeparator():
    '''A menu separator item.
    '''
    return NSMenuItem.separatorItem()


def _Window2(title=_argv0, fraction=0.5):
    '''Create the main NS window and the drawable NS view.
    '''
    frame = NSScreen.mainScreen().frame()
    if 0.1 < fraction < 1.0:
        # use the lower left quarter of the screen size as frame
        w = int(frame.size.width * fraction + 0.5)
        h = int(frame.size.height * w / frame.size.width)
        frame = NSMakeRect(frame.origin.x + 10, frame.origin.y + 10, w, h)

    window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
                              frame,
                              NSWindowStyleMaskUsual,
                              NSBackingStoreBuffered,
                              False)  # or 0
    window.setTitle_(NSStr(title))

    # create the drawable_nsobject NSView for vlc.py, see vlc.MediaPlayer.set_nsobject()
    # for an alternate NSView object with protocol VLCOpenGLVideoViewEmbedding
    # <http://StackOverflow.com/questions/11562587/create-nsview-directly-from-code>
    # <http://GitHub.com/ariabuckles/pyobjc-framework-Cocoa/blob/master/Examples/AppKit/DotView/DotView.py>
    view = NSView.alloc().initWithFrame_(frame)
    window.setContentView_(view)
    # force the video/window aspect ratio, adjusted
    # above when the window is/has been resized
    window.setContentAspectRatio_(frame.size)

    window.makeKeyAndOrderFront_(None)
    return window, view


def simpleVLCplay(player, title=_argv0, video='', timeout=None):
    '''Create a minimal NS application, drawable window and basic menu
       for the given VLC player (with media) and start the player.

       @note: This function never returns, but the VLC player and
              other Python thread(s) do run.
    '''
    if not player:
        raise ValueError('%s invalid: %r' % ('player', player))

    app = NSApplication.sharedApplication()
    nsBundleRename(NSStr(title))  # top-level menu title

    dlg = _NSDelegate.alloc().init()
    dlg.app = app
    dlg.player = player
    dlg.title = title or _argv0
    dlg.video = video or basename(player.get_media().get_mrl())
    app.setDelegate_(dlg)

    terminating(app, timeout)
    app.run()  # never returns


if __name__ == '__main__':

    try:
        import vlc
    except ImportError:
        raise _ImportError('vlc', 'Python-VLC')

    _argv0 = _name = basename(sys.argv[0])
    _timeout = None

    args = sys.argv[1:]
    while args and args[0].startswith('-'):
        o = args.pop(0)
        t = o.lower()
        if t in ('-h', '--help'):
            printf('usage:  [-h|--help]  [-name "%s"]  [-timeout <secs>]  %s',
                   _name, '<video_file_name>')
            sys.exit(0)
        elif args and len(t) > 1 and '-name'.startswith(t):
            _name = args.pop(0)
        elif args and len(t) > 1 and '-timeout'.startswith(t):
            _timeout = args.pop(0)
        elif t in ('-v', '--version'):
            print('%s: %s (%s %s)' % (basename(__file__), __version__,
                                      'PyObjC', __PyObjC__))
            try:
                vlc.print_version()
                vlc.print_python()
            except AttributeError:
                pass
            sys.exit(0)
        else:
            printf('invalid option: %s', o)
            sys.exit(1)

    if not args:
        printf('missing %s', '<video_file_name>')
        sys.exit(1)

    # create a VLC player and play the video
    p = vlc.MediaPlayer(args.pop(0))
    simpleVLCplay(p, title=_name, timeout=_timeout)  # never returns

# MIT License <http://OpenSource.org/licenses/MIT>
#
# Copyright (C) 2017-2020 -- mrJean1 at Gmail -- All Rights Reserved.
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
