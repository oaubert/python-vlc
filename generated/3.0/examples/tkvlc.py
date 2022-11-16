#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# tkinter example for VLC Python bindings
# Copyright (C) 2015 the VideoLAN team
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
'''A simple example for VLC python bindings using tkinter.

Author: Patrick Fay
Date: 23-09-2015
'''

# Tested with VLC 3.0.16, 3.0.12, 3.0.11, 3.0.10, 3.0.8 and 3.0.6 with
# the compatible vlc.py Python-VLC binding, Python 3.11.0, 3.10.0, 3.9.0
# and 3.7.4 with tkinter/Tk 8.6.9 on macOS 13.0 (amd64 M1), 11.6.1 (10.16
# amd64 M1), 11.0.1 (10.16 x86-64) and 10.13.6 only.
__version__ = '22.11.11'  # mrJean1 at Gmail

import sys
try:  # Python 3.4+ only
    import tkinter as Tk
    from tkinter import ttk  # PYCHOK ttk = Tk.ttk
    from tkinter.filedialog import askopenfilename
    from tkinter.messagebox import showerror
    from pathlib import Path
except ImportError:
    sys.exit('%s requires Python 3.4 or later' % (sys.argv[0],))
    # import Tkinter as Tk
import os
import time
import vlc

_dragging  = False  # use -dragging option

_isMacOS   = sys.platform.startswith('darwin')
_isWindows = sys.platform.startswith('win')
_isLinux   = sys.platform.startswith('linux')

_TKVLC_LIBTK_PATH = 'TKVLC_LIBTK_PATH'

if _isMacOS:  # MCCABE 14
    from ctypes import cdll, c_void_p
    from ctypes.util import find_library as _find

    # libtk = cdll.LoadLibrary(ctypes.util.find_library('tk'))
    # returns (None or) the tk library /usr/lib/libtk.dylib
    # from macOS, but we need the tkX.Y library bundled with
    # Python 3+ or one matching the version of tkinter

    # Homebrew-built Python, Tcl/Tk, etc. are installed in
    # different places, usually something like /usr/- or
    # /opt/local/Cellar/tcl-tk/8.6.11_1/lib/libtk8.6.dylib,
    # found by command line `find /opt -name libtk8.6.dylib`

    def _find_lib(name, *paths):
        # 1. built into Python
        for p in (getattr(sys, 'base_prefix', ''), sys.prefix):
            if p:
                yield p + '/lib/' + name
        # 2. from ctypes.find_library, env variable
        for p in paths:
            if p:  # is not None
                p = os.path.expanduser(p)
                yield p
                if not p.endswith(name):
                    yield p + '/' + name
        # 3. try Homebrew basement
        from glob import iglob
        for t in ('/opt', '/usr'):
            t += '/local/Cellar/tcl-tk/*/lib/' + name
            for p in iglob(t):
                yield p
        assert os.path.sep == '/'

    try:
        env = os.environ.get(_TKVLC_LIBTK_PATH, '')
        lib = 'libtk%s.dylib' % (Tk.TkVersion,)
        for libtk in _find_lib(lib, _find(lib), *env.split(os.pathsep)):
            if libtk and lib in libtk and os.access(libtk, os.F_OK):
                break
        else:  # not found anywhere
            if env:  # bad env?
                t = 'no %s in %%s=%r' % (lib, env)
            else:  # env not set, suggest
                t = 'no %s found, use %%s to set a path' % (lib,)
            raise NameError(t % (_TKVLC_LIBTK_PATH,))

        lib = cdll.LoadLibrary(libtk)
        # getNSView = tklib.TkMacOSXDrawableView is the
        # proper function to call, but that is non-public
        # (in Tk source file macosx/TkMacOSXSubwindows.c)
        # Fortunately, tklib.TkMacOSXGetRootControl calls
        # tklib.TkMacOSXDrawableView and returns the NSView
        _GetNSView = lib.TkMacOSXGetRootControl
        # C signature: void *_GetNSView(void *drawable) to get
        # the Cocoa/Obj-C NSWindow.contentView attribute, the
        # drawable NSView object of the (drawable) NSWindow
        _GetNSView.restype = c_void_p
        _GetNSView.argtypes = (c_void_p,)

    except (NameError, OSError) as x:  # lib, image or symbol not found
        libtk = str(x)  # imported by psgvlc.py

        def _GetNSView(unused):  # imported by psgvlc.py
            return None

    del cdll, c_void_p, env, _find
    C_Key = 'Command-'  # shortcut key modifier

else:  # *nix, Xwindows and Windows, UNTESTED

    libtk = 'N/A'
    C_Key = 'Control-'  # shortcut key modifier


class _Tk_Menu(Tk.Menu):
    '''Tk.Menu extended with .add_shortcut method.  Note, this is a
       kludge just to get Command-key shortcuts to work on macOS.
       Modifiers like Ctrl-, Shift- and Option- are not handled!
    '''
    _shortcuts_entries = {}
    _shortcuts_widget  = None

    def add_shortcut(self, label='', key='', command=None, **kwds):
        '''Like Tk.menu.add_command extended with shortcut key.
           If needed use modifiers like Shift- and Alt_ or Option-
           as before the shortcut key character.  Do not include
           the Command- or Control- modifier nor the <...> brackets
           since those are handled here, depending on platform and
           as needed for the binding.
        '''
        # <https://TkDocs.com/tutorial/menus.html>
        if not key:
            self.add_command(label=label, command=command, **kwds)

        elif _isMacOS:
            # keys show as upper-case, always
            self.add_command(label=label, accelerator=C_Key + key,
                                          command=command, **kwds)
            self.bind_shortcut(key, command, label)

        else:  # XXX not tested, not tested, not tested
            self.add_command(label=label, underline=label.lower().index(key),
                                          command=command, **kwds)
            self.bind_shortcut(key, command, label)

    def bind_shortcut(self, key, command, label=None):
        '''Bind shortcut key, default modifier Command/Control.
        '''
        # The accelerator modifiers on macOS are Command-,
        # Ctrl-, Option- and Shift-, but for .bind[_all] use
        # <Command-..>, <Ctrl-..>, <Option_..> and <Shift-..>,
        # <https://www.Tcl.Tk/man/tcl8.6/TkCmd/bind.htm#M6>
        if self._shortcuts_widget:
            if C_Key.lower() not in key.lower():
                key = '<%s%s>' % (C_Key, key.lstrip('<').rstrip('>'))
            self._shortcuts_widget.bind(key, command)
            # remember the shortcut key for this menu item
            if label is not None:
                item = self.index(label)
                self._shortcuts_entries[item] = key
        # The Tk modifier for macOS' Command key is called
        # Meta, but there is only Meta_L[eft], no Meta_R[ight]
        # and both keyboard command keys generate Meta_L events.
        # Similarly for macOS' Option key, the modifier name is
        # Alt and there's only Alt_L[eft], no Alt_R[ight] and
        # both keyboard option keys generate Alt_L events.  See:
        # <https://StackOverflow.com/questions/6378556/multiple-
        # key-event-bindings-in-tkinter-control-e-command-apple-e-etc>

    def bind_shortcuts_to(self, widget):
        '''Set the widget for the shortcut keys, usually root.
        '''
        self._shortcuts_widget = widget

    def entryconfig(self, item, **kwds):  # PYCHOK signature
        '''Update shortcut key binding if menu entry changed.
        '''
        Tk.Menu.entryconfig(self, item, **kwds)
        # adjust the shortcut key binding also
        if self._shortcuts_widget:
            key = self._shortcuts_entries.get(item, None)
            if key is not None and 'command' in kwds:
                self._shortcuts_widget.bind(key, kwds['command'])


class Player(Tk.Frame):
    '''The main window has to deal with events.
    '''
    _debugs    = 0
    _geometry  = ''
    _MIN_WIDTH = 600
    _stopped   = None

    def __init__(self, parent, title=None, video='', debug=False):  # PYCHOK called!
        Tk.Frame.__init__(self, parent)

        self.debug  = bool(debug)
        self.parent = parent  # == root
        self.parent.title(title or 'tkVLCplayer')
        self.video = os.path.expanduser(video)

        # Menu Bar
        menubar = Tk.Menu(self.parent)
        self.parent.config(menu=menubar)
        # File Menu
        fileMenu = _Tk_Menu(menubar)
        fileMenu.bind_shortcuts_to(parent)  # XXX must be root?

        fileMenu.add_shortcut('Open...', 'o', self.OnOpen)
        fileMenu.add_separator()
        fileMenu.add_shortcut('Play', 'p', self.OnPlay)  # Play/Pause
        fileMenu.add_command(label='Stop', command=self.OnStop)
        fileMenu.add_separator()
        fileMenu.add_shortcut('Mute', 'm', self.OnMute)
        fileMenu.add_separator()
        fileMenu.add_shortcut('Close', 'w' if _isMacOS else 's', self.OnClose)
        fileMenu.add_separator()
        fileMenu.add_shortcut('Buttons Up', 'a', self.OnAnchor)
        self.anchorIndex = fileMenu.index('Buttons Up')
        fileMenu.add_separator()
        fileMenu.add_shortcut('Full Screen', 'f', self.OnScreen)
        self.fullIndex = fileMenu.index('Full Screen')
        menubar.add_cascade(label='File', menu=fileMenu)
        self.fileMenu = fileMenu
        self.playIndex = fileMenu.index('Play')
        self.muteIndex = fileMenu.index('Mute')

        # first, panel shows video
        self.videoPanel = ttk.Frame(self.parent)
        self.canvas = Tk.Canvas(self.videoPanel)
        self.canvas.pack(fill=Tk.BOTH, expand=1)
        self.videoPanel.pack(fill=Tk.BOTH, expand=1)

        # panel to hold buttons
        self.buttonsPanel = Tk.Toplevel(self.parent)
        self.buttonsPanel.title('')
        self.buttonsPanel_anchored = False
        self.buttonsPanel_clicked  = False
        self.buttonsPanel_dragged  = False

        buttons = ttk.Frame(self.buttonsPanel)
        self.playButton   = ttk.Button(buttons, text='Play', command=self.OnPlay, underline=0)
        stop              = ttk.Button(buttons, text='Stop', command=self.OnStop)
        self.muteButton   = ttk.Button(buttons, text='Mute', command=self.OnMute, underline=0)
        self.playButton.pack(side=Tk.LEFT, padx=8)
        stop.pack(side=Tk.LEFT)
        self.muteButton.pack(side=Tk.LEFT, padx=8)
        self.volMuted = False
        self.volVar = Tk.IntVar()
        self.volSlider = Tk.Scale(buttons, variable=self.volVar, command=self.OnVolume,
                                  from_=0, to=100, orient=Tk.HORIZONTAL, length=170,
                                  showvalue=0, label='Volume')
        self.volSlider.pack(side=Tk.LEFT)

        self.anchorButton = ttk.Button(buttons, text='Up', command=self.OnAnchor,
                                       width=2)  # in characters
        self.anchorButton.pack(side=Tk.RIGHT, padx=8)
        buttons.pack(side=Tk.BOTTOM, fill=Tk.X)

        # <https://www.PythonTutorial.net/tkinter/tkinter-window>
        # <https://TkDocs.com/tutorial/windows.html>
        # self.buttonsPanel.attributes('-topmost', 1)

        self.buttonsPanel.update()
        self.videoPanel.update()

        # panel to hold player time slider
        timers = ttk.Frame(self.buttonsPanel)
        self.timeVar = Tk.DoubleVar()
        self.timeSliderLast = 0
        self.timeSlider = Tk.Scale(timers, variable=self.timeVar, command=self.OnTime,
                                   from_=0, to=1000, orient=Tk.HORIZONTAL, length=500,
                                   showvalue=0)  # label='Time',
        self.timeSlider.pack(side=Tk.BOTTOM, fill=Tk.X, expand=1)
        self.timeSliderUpdate = time.time()
        timers.pack(side=Tk.BOTTOM, fill=Tk.X)

        # VLC player
        args = []
        if _isLinux:
            args.append('--no-xlib')
        self.Instance = vlc.Instance(args)
        self.player = self.Instance.media_player_new()

        self.parent.bind('<Configure>', self.OnConfigure)  # catch window resize, etc.
        self.parent.update()

        # After parent.update() otherwise panel is ignored.
        self.buttonsPanel.overrideredirect(True)
        self.buttonsPanel_anchored = True  # down, under the video panel

        if _dragging:  # Detect dragging of the buttons panel.
            self.buttonsPanel.bind('<Button-1>',        self._Button1Down)
            self.buttonsPanel.bind('<B1-Motion>',       self._Button1Motion)
            self.buttonsPanel.bind('<ButtonRelease-1>', self._Button1Up)

        # Keep the video panel at least as wide as thebuttons panel.
        self.parent.minsize(width=self._MIN_WIDTH, height=0)

        self._AnchorPanels(force=True)

        self.OnTick()  # set up the timer

        if self.video:  # play for a second
            self.OnPlay()
            self.parent.after(1000, self.OnPause)

    def _Button1Down(self, *unused):  # only if -dragging
        self._debug(self._Button1Down)
        # Left-mouse-button pressed inside the buttons
        # panel, but not in and over a slider-/button.
        self.buttonsPanel_clicked = True
        self.buttonsPanel_dragged = False

    def _Button1Motion(self, *unused):  # only if -dragging
        self._debug(self._Button1Motion)
        # Mouse dragged, moved with left-mouse-button down?
        self.buttonsPanel_dragged = self.buttonsPanel_clicked

    def _Button1Up(self, *unused):  # only if -dragging
        self._debug(self._Button1Up)
        # Left-mouse-button release
        if self.buttonsPanel_clicked:
            if self.buttonsPanel_dragged:
                # If the mouse was dragged in the buttons
                # panel on the background, un-/anchor it.
                self.OnAnchor()
#               if _dragged:
#                   self.buttonsPanel.unbind('<Button-1>')
#                   self.buttonsPanel.unbind('<B1-Motion>')
#                   self.buttonsPanel.unbind('<ButtonRelease-1>')
        self.buttonsPanel_clicked = False
        self.buttonsPanel_dragged = False

    def _debug(self, where, **kwds):
        # Print where an event is are handled.
        if self.debug:
            self._debugs += 1
            d = dict(anchored=self.buttonsPanel_anchored,
                      clicked=self.buttonsPanel_clicked,
                      dragged=self.buttonsPanel_dragged,
                      playing=self.player.is_playing(),
                      stopped=self._stopped)
            d.update(kwds)
            d = ', '.join('%s=%s' % t for t in sorted(d.items()))
            print('%4s: %s %s' % (self._debugs, where.__name__, d))

    def _AnchorPanels(self, force=False):
        # Un-/anchor the buttons under the video panel, at the same width.
        self._debug(self._AnchorPanels)
        if (force or self.buttonsPanel_anchored):
            video = self.parent
            h = video.winfo_height()
            w = video.winfo_width()
            x = video.winfo_x()  # i.e. same as the video
            y = video.winfo_y() + h + 32  # i.e. below the video
            h = self.buttonsPanel.winfo_height()  # unchanged
            w = max(w, self._MIN_WIDTH)  # i.e. same a video width
            self.buttonsPanel.geometry('%sx%s+%s+%s' % (w, h, x, y))

    def OnAnchor(self, *unused):
        '''Toggle buttons panel anchoring.
        '''
        c = self.OnAnchor
        self._debug(c)
        self.buttonsPanel_anchored = not self.buttonsPanel_anchored
        if self.buttonsPanel_anchored:
            a = 'Up'
            self._AnchorPanels(force=True)
        else:  # move the panel to the top left corner
            a = 'Down'
            h = self.buttonsPanel.winfo_height()  # unchanged
            self.buttonsPanel.geometry('%sx%s+8+32' % (self._MIN_WIDTH, h))
        self.anchorButton.config(text=a, width=len(a))
        a = 'Buttons ' + a
        self.fileMenu.entryconfig(self.anchorIndex, label=a, command=c)
        # self.fileMenu.bind_shortcut('a', c)  # XXX handled

    def OnClose(self, *unused):
        '''Closes the window and quit.
        '''
        self._debug(self.OnClose)
        # print('_quit: bye')
        self.parent.quit()  # stops mainloop
        self.parent.destroy()  # this is necessary on Windows to avoid
        # ... Fatal Python Error: PyEval_RestoreThread: NULL tstate

    def OnConfigure(self, *unused):
        '''Some widget configuration changed.
        '''
        self._debug(self.OnConfigure)
        # <https://www.Tcl.Tk/man/tcl8.6/TkCmd/bind.htm#M12>
        self._geometry = ''  # force .OnResize in .OnTick, recursive?
        self._AnchorPanels()

    def OnMute(self, *unused):
        '''Mute/Unmute audio.
        '''
        self._debug(self.OnMute)
        self.buttonsPanel_clicked = False
        # audio un/mute may be unreliable, see vlc.py docs.
        self.volMuted = m = not self.volMuted  # self.player.audio_get_mute()
        self.player.audio_set_mute(m)
        u = 'Unmute' if m else 'Mute'
        self.fileMenu.entryconfig(self.muteIndex, label=u)
        self.muteButton.config(text=u)
        # update the volume slider text
        self.OnVolume()

    def OnOpen(self, *unused):
        '''Pop up a new dialow window to choose a file, then play the selected file.
        '''
        # if a file is already running, then stop it.
        self.OnStop()
        # Create a file dialog opened in the current home directory, where
        # you can display all kind of files, having as title 'Choose a video'.
        video = askopenfilename(initialdir = Path(os.path.expanduser('~')),
                                title = 'Choose a video',
                                filetypes = (('all files', '*.*'),
                                             ('mp4 files', '*.mp4'),
                                             ('mov files', '*.mov')))
        self._Play(video)

    def _Pause_Play(self, playing):
        # re-label menu item and button, adjust callbacks
        p = 'Pause' if playing else 'Play'
        c = self.OnPlay if playing is None else self.OnPause  # PYCHOK attr
        self.fileMenu.entryconfig(self.playIndex, label=p, command=c)
        # self.fileMenu.bind_shortcut('p', c)  # XXX handled
        self.playButton.config(text=p, command=c)
        self._stopped = False

    def _Play(self, video):
        # helper for OnOpen and OnPlay
        if os.path.isfile(video):  # Creation
            m = self.Instance.media_new(str(video))  # Path, unicode
            self.player.set_media(m)
            self.parent.title('tkVLCplayer - %s' % (os.path.basename(video),))

            # set the window id where to render VLC's video output
            h = self.canvas.winfo_id()  # .winfo_visualid()?
            if _isWindows:
                self.player.set_hwnd(h)
            elif _isMacOS:
                # XXX 1) using the videoPanel.winfo_id() handle
                # causes the video to play in the entire panel on
                # macOS, covering the buttons, sliders, etc.
                # XXX 2) .winfo_id() to return NSView on macOS?
                v = _GetNSView(h)
                if v:
                    self.player.set_nsobject(v)
                else:
                    self.player.set_xwindow(h)  # plays audio, no video
            else:
                self.player.set_xwindow(h)  # fails on Windows
            # FIXME: this should be made cross-platform
            self.OnPlay(None)

    def OnPause(self, *unused):
        '''Toggle between Pause and Play.
        '''
        self._debug(self.OnPause)
        self.buttonsPanel_clicked = False
        if self.player.get_media():
            self._Pause_Play(not self.player.is_playing())
            self.player.pause()  # toggles

    def OnPlay(self, *unused):
        '''Play video, if not loaded, open the dialog window.
        '''
        self._debug(self.OnPlay)
        self.buttonsPanel_clicked = False
        # if there's no video to play or playing,
        # open a Tk.FileDialog to select a file
        if not self.player.get_media():
            if self.video:
                self._Play(os.path.expanduser(self.video))
                self.video = ''
            else:
                self.OnOpen()
        # Try to play, if this fails display an error message
        elif self.player.play():  # == -1
            self.showError('Unable to play the video.')
        else:
            self._Pause_Play(True)
            # set volume slider to audio level
            vol = self.player.audio_get_volume()
            if vol > 0:
                self.volVar.set(vol)
                self.volSlider.set(vol)
            self.OnResize()

    def OnResize(self, *unused):
        '''Adjust the video panel to the video aspect ratio.
        '''
        self._debug(self.OnResize)
        g = self.parent.geometry()
        if g != self._geometry and self.player:
            u, v = self.player.video_get_size()  # often (0, 0)
            if v > 0 and u > 0:
                # get window size and position
                g, x, y = g.split('+')
                w, h = g.split('x')
                # alternatively, use .winfo_...
                # w = self.parent.winfo_width()
                # h = self.parent.winfo_height()
                # x = self.parent.winfo_x()
                # y = self.parent.winfo_y()
                # use the video aspect ratio ...
                if u > v:  # ... for landscape
                    # adjust the window height
                    h = round(float(w) * v / u)
                else:  # ... for portrait
                    # adjust the window width
                    w = round(float(h) * u / v)
                self.parent.geometry('%sx%s+%s+%s' % (w, h, x, y))
                self._geometry = self.parent.geometry()  # actual
                self._AnchorPanels()

    def OnScreen(self, *unused):
        '''Toggle full/off screen.
        '''
        c = self.OnScreen
        self._debug(c)
        # <https://www.Tcl.Tk/man/tcl8.6/TkCmd/wm.htm#M10>
        f = not self.parent.attributes('-fullscreen')  # or .wm_attributes
        if f:
            self._previouscreen = self.parent.geometry()
            self.parent.attributes('-fullscreen', f)  # or .wm_attributes
            self.parent.bind('<Escape>', c)
            f = 'Off'
        else:
            self.parent.attributes('-fullscreen', f)  # or .wm_attributes
            self.parent.geometry(self._previouscreen)
            self.parent.unbind('<Escape>')
            f = 'Full'
        f += ' Screen'
        self.fileMenu.entryconfig(self.fullIndex, label=f, command=c)
        # self.fileMenu.bind_shortcut('f', c)  # XXX handled

    def OnStop(self, *unused):
        '''Stop the player, resets media.
        '''
        self._debug(self.OnStop)
        self.buttonsPanel_clicked = False
        if self.player:
            self.player.stop()
            self._Pause_Play(None)
            # reset the time slider
            self.timeSlider.set(0)
            self._stopped = True
        # XXX on macOS libVLC prints these error messages:
        # [h264 @ 0x7f84fb061200] get_buffer() failed
        # [h264 @ 0x7f84fb061200] thread_get_buffer() failed
        # [h264 @ 0x7f84fb061200] decode_slice_header error
        # [h264 @ 0x7f84fb061200] no frame!

    def OnTick(self):
        '''Timer tick, update the time slider to the video time.
        '''
        if self.player:
            # since the self.player.get_length may change while
            # playing, re-set the timeSlider to the correct range
            t = self.player.get_length() * 1e-3  # to seconds
            if t > 0:
                self.timeSlider.config(to=t)

                t = self.player.get_time() * 1e-3  # to seconds
                # don't change slider while user is messing with it
                if t > 0 and time.time() > (self.timeSliderUpdate + 2):
                    self.timeSlider.set(t)
                    self.timeSliderLast = int(self.timeVar.get())
        # start the 1 second timer again
        self.parent.after(1000, self.OnTick)
        # adjust window to video aspect ratio, done periodically
        # on purpose since the player.video_get_size() only
        # returns non-zero sizes after playing for a while
        self.OnResize()

    def OnTime(self, *unused):
        if self.player:
            t = self.timeVar.get()
            if self.timeSliderLast != int(t):
                # This is a hack. The timer updates the time slider and
                # that change causes this rtn (the 'slider has changed')
                # to be invoked.  I can't tell the difference between the
                # user moving the slider manually and the timer changing
                # the slider.  When the user moves the slider, tkinter
                # only notifies this method about once per second and
                # when the slider has quit moving.
                # Also, the tkinter notification value has no fractional
                # seconds.  The timer update rtn saves off the last update
                # value (rounded to integer seconds) in timeSliderLast if
                # the notification time (sval) is the same as the last saved
                # time timeSliderLast then we know that this notification is
                # due to the timer changing the slider.  Otherwise the
                # notification is due to the user changing the slider.  If
                # the user is changing the slider then I have the timer
                # routine wait for at least 2 seconds before it starts
                # updating the slider again (so the timer doesn't start
                # fighting with the user).
                self.player.set_time(int(t * 1e3))  # milliseconds
                self.timeSliderUpdate = time.time()

    def OnVolume(self, *unused):
        '''Volume slider changed, adjust the audio volume.
        '''
        self._debug(self.OnVolume)
        self.buttonsPanel_clicked = False
        self.buttonsPanel_dragged = False
        vol = min(self.volVar.get(), 100)
        v_M = '%d%s' % (vol, ' (Muted)' if self.volMuted else '')
        self.volSlider.config(label='Volume ' + v_M)
        if self.player and not self._stopped:
            # .audio_set_volume returns 0 if success, -1 otherwise,
            # e.g. if the player is stopped or doesn't have media
            if self.player.audio_set_volume(vol):  # and self.player.get_media():
                self.showError('Failed to set the volume: %s.' % (v_M,))

    def showError(self, message):
        '''Display a simple error dialog.
        '''
        self.OnStop()
        showerror(self.parent.title(), message)


if __name__ == '__main__':  # MCCABE 13

    _argv0 = sys.argv[0]
    _debug = False
    _video = ''

    while len(sys.argv) > 1:
        arg = sys.argv.pop(1)
        if arg.lower() in ('-v', '--version'):
            # show all versions, this vlc.py, libvlc, etc. (sample output on macOS):
            # % python3 ./tkvlc.py -v
            # tkvlc.py: 22.11.10
            # tkinter: 8.6
            # libTk: /Library/Frameworks/Python.framework/Versions/3.11/lib/libtk8.6.dylib
            # vlc.py: 3.0.12119 (Mon May 31 18:25:17 2021 3.0.12)
            # libVLC: 3.0.16 Vetinari (0x3001000)
            # plugins: /Applications/VLC.app/Contents/MacOS/plugins
            # Python: 3.11.0 (64bit) macOS 13.0.1 arm64
            for t in ((_argv0, __version__), (Tk.__name__, Tk.TkVersion), ('libTk', libtk)):
                print('%s: %s' % t)
            try:
                vlc.print_version()
                vlc.print_python()
            except AttributeError:
                pass
            sys.exit(0)
        elif '-debug'.startswith(arg) and len(arg) > 2:
            _debug = True
        elif '-dragging'.startswith(arg) and len(arg) > 2:
            _dragging = True  # detect dragging in buttons panel for Buttons Up/Down
        elif arg.startswith('-'):
            print('usage: %s  [-v | --version]  [-debug]  [-dragging]  [<video_file_name>]' % (_argv0,))
            sys.exit(1)
        elif arg:  # video file
            _video = os.path.expanduser(arg)
            if not os.path.isfile(_video):
                print('%s error: no such file: %r' % (_argv0, arg))
                sys.exit(1)

    # Create a Tk.App() to handle the windowing event loop
    root = Tk.Tk()
    player = Player(root, video=_video, debug=_debug)
    root.protocol('WM_DELETE_WINDOW', player.OnClose)  # XXX unnecessary (on macOS)
    if _isWindows:  # see <https://GitHub.com/python/cpython/blob/3.11/Lib/tkinter/__init__.py>
        root.iconify()
        root.update()
        root.deiconify()
    root.mainloop()
