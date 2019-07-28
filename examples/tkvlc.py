#! /usr/bin/python
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
"""A simple example for VLC python bindings using tkinter.

Requires Python 3.4 or later.

Author: Patrick Fay
Date: 23-09-2015
"""

# Tested with Python 3.7.4, tkinter/Tk 8.6.9 on macOS 10.13.6 only.
__version__ = '19.07.28'  # mrJean1 at Gmail dot com

# import external libraries
import vlc
# import standard libraries
import sys
if sys.version_info[0] < 3:
    import Tkinter as Tk
    from Tkinter import ttk
    from Tkinter.filedialog import askopenfilename
    from Tkinter.tkMessageBox import showerror
else:
    import tkinter as Tk
    from tkinter import ttk
    from tkinter.filedialog import askopenfilename
    from tkinter.messagebox import showerror
import os
from os.path import basename, expanduser, isfile, join as joined
from pathlib import Path
import time

_isMacOS   = sys.platform.startswith('darwin')
_isWindows = sys.platform.startswith('win')

if _isMacOS:
    from ctypes import c_void_p, cdll
    # libtk = cdll.LoadLibrary(ctypes.util.find_library('tk'))
    # returns the tk library /usr/lib/libtk.dylib from macOS,
    # but we need the tkX.Y library bundled with Python 3+,
    # to match the version number of tkinter, _tkinter, etc.
    try:
        libtk = 'libtk%s.dylib' % (Tk.TkVersion,)
        libtk = joined(sys.prefix, 'lib', libtk)
        dylib = cdll.LoadLibrary(libtk)
        # getNSView = dylib.TkMacOSXDrawableView  # private
        _getNSView = dylib.TkMacOSXGetRootControl
        # C signature: void *_getNSView(void *drawable)
        # get the Cocoa NSWindow.contentView attribute,
        # an NSView instance of the drawable NSWindow
        _getNSView.restype = c_void_p
        _getNSView.argtypes = c_void_p,
        del dylib

    except (NameError, OSError):  # image or symbol not found
        def _getNSView(unused):
            return None
        libtk = 'N/A'

    # _Shift   = 1   # if set, Shift key is down
    # _Lock    = 2   # if set, Caps Lock key is down
    # _Control = 4   # if set, Control key is down
    _Mod1      = 8   # if set, Command key is down
    # _Mod2    = 16  # if set, Option key is down
    # etc. ... several more see tkinter.__init__.py at
    # <https://GitHub.com/python/cpython/blob/master/
    # Lib/tkinter/__init__.py> in method Event.__repr__.

    # The Tk modifier for the macOS Command key is called
    # Meta, but there is only Meta_L, no Meta_R and both
    # keyboard command keys generate Meta_L events.  Same
    # for the macOS Option key, the modified is called Alt
    # and there's only Alt_L, no Alt_R and both keyboard
    # option keys generate Alt_L events. See answers at:
    # <https://StackOverflow.com/questions/6378556/
    # multiple-key-event-bindings-in-tkinter-control-e-command-apple-e-etc>

    def _handle_shortcuts(event):  # all KeyPress events
        # .state is <int> for for KeyPress and -Release
        # XXX use if .state in (_Mod1, _Shift|_Mod1) ...
        # menu items with shortcuts specified without the
        # Shift- accelerator do flash for shift-key press
        if event.state == _Mod1 and event.char in _Tk_Menu._shortcuts:
            _Tk_Menu._shortcuts[event.char](event)

else:  # *nix, Xwindows and Windows, UNTESTED

    libtk = 'N/A'


class _Tk_Menu(Tk.Menu):
    '''Tk.Menu extended with .add_shortcut method.

       Note, this is a kludge just to get Command-key shortcuts to
       work on macOS.  Other modifiers like Ctrl-, Shift- and Option-
       are not handled in this code.
    '''
    _shortcuts = {}  # XXX should be an instance attribute, not global
    _shortcuts_bind = None

    def add_shortcut(self, label='', key='', command=None, **kwds):
        '''Like Tk.menu.add_command extended with shortcut key.
        '''
        # <https://TkDocs.com/tutorial/menus.html>
        if not key:
            self.add_command(label=label, command=command, **kwds)
        elif len(key) > 1:  # XXX single char only
            raise NotImplemented('shortcut key: %r[%s]' % (key, len(key)))

        elif _isMacOS:
            # keys show as upper-case, always
            self.add_command(label=label, accelerator='Command-' + key,
                                          command=command, **kwds)
            # The accelerator modifiers on macOS are Ctrl-, Option-,
            # Shift- and Command-, but for .bind use Ctrl-, Shift-,
            # Mod1- instead of Command and Mod2- instead of Option.
            # However, .bind does not seem to work that anyway, so ...
            # if self._shortcuts_bind:
            #     self._shortcuts_bind.bind('Mod1-' + key, command)
            _Tk_Menu._shortcuts[key] = command  # ... use a kludge

        else:  # XXX not tested, not tested, not tested
            self.add_command(label=label, underline=label.lower().index(key),
                                          command=command, **kwds)
            if self._shortcuts_bind:
                self._shortcuts_bind.bind('Control-%s>' % (key,), command)

    def bind_shortcuts(self, frame):
        '''Bind the handler for the shortcut keys.
        '''
        self._shortcuts_bind = frame
        if _isMacOS:  # handler command keys only for now
            frame.bind('<Key>', _handle_shortcuts)


class Player(Tk.Frame):
    """The main window has to deal with events.
    """

    def __init__(self, parent, title=None, video=''):
        Tk.Frame.__init__(self, parent)

        self.parent = parent  # == root
        self.parent.title(title or "tkVLCplayer")
        self.video = expanduser(video)

        # Menu Bar
        #   File Menu
        menubar = Tk.Menu(self.parent)
        self.parent.config(menu=menubar)

        fileMenu = _Tk_Menu(menubar)
        fileMenu.bind_shortcuts(parent)  # XXX must be root?

        fileMenu.add_shortcut("Open...", 'o', self.OnOpen)
        fileMenu.add_separator()
        fileMenu.add_shortcut("Play", 'p', self.OnPlay)  # Play/Pause
        fileMenu.add_command(label="Stop", command=self.OnStop)
        fileMenu.add_separator()
        fileMenu.add_shortcut("Mute", 'm', self.OnMute)
        fileMenu.add_separator()
        fileMenu.add_shortcut("Close", 'w' if _isMacOS else 's', self.OnClose)
        menubar.add_cascade(label="File", menu=fileMenu)
        self.fileMenu = fileMenu
        self.playIndex = fileMenu.index('Play')
        self.muteIndex = fileMenu.index('Mute')

        # first, top panel shows video
        self.videopanel = ttk.Frame(self.parent)
        self.canvas = Tk.Canvas(self.videopanel)
        self.canvas.pack(fill=Tk.BOTH, expand=1)
        self.videopanel.pack(fill=Tk.BOTH, expand=1)

        # panel to hold buttons
        buttons = ttk.Frame(self.parent)
        self.playButton = ttk.Button(buttons, text="Play", command=self.OnPlay)
        stop            = ttk.Button(buttons, text="Stop", command=self.OnStop)
        self.muteButton = ttk.Button(buttons, text="Mute", command=self.OnMute)
        self.playButton.pack(side=Tk.LEFT)
        stop.pack(side=Tk.LEFT)
        self.muteButton.pack(side=Tk.LEFT)
        self.muted = False

        self.volMuted = ''
        self.volVar = Tk.IntVar()
        self.volSlider = Tk.Scale(buttons, variable=self.volVar, command=self.OnVolume,
                                  from_=0, to=100, orient=Tk.HORIZONTAL, length=200,
                                  showvalue=0, label='Volume')
        self.volSlider.pack(side=Tk.LEFT)
        buttons.pack(side=Tk.BOTTOM)

        # panel to hold time slider
        timers = ttk.Frame(self.parent)
        self.timeVar = Tk.DoubleVar()
        self.timeSliderLast = 0
        self.timeSlider = Tk.Scale(timers, variable=self.timeVar, command=self.OnTime,
                                   from_=0, to=1000, orient=Tk.HORIZONTAL, length=500,
                                   showvalue=0)  # label='Time',
        self.timeSlider.pack(side=Tk.BOTTOM, fill=Tk.X, expand=1)
        self.timeSliderUpdate = time.time()
        timers.pack(side=Tk.BOTTOM, fill=Tk.X)

        # VLC player controls
        self.Instance = vlc.Instance()
        self.player = self.Instance.media_player_new()

        self.parent.update()

        self.OnTick()  # set the timer up

    def OnClose(self, *unused):
        """Closes the window and quit.
        """
        # print("_quit: bye")
        self.parent.quit()  # stops mainloop
        self.parent.destroy()  # this is necessary on Windows to avoid
        # ... Fatal Python Error: PyEval_RestoreThread: NULL tstate
        os._exit(1)

    def OnMute(self, *unused):
        """Mute/Unmute audio.

           Note, audio un/mute may be unreliable, see vlc.py docs.
        """
        self.muted = m = not self.muted  # self.player.audio_get_mute()
        self.player.audio_set_mute(m)
        u = "Unmute" if m else "Mute"
        self.fileMenu.entryconfig(self.muteIndex, label=u)
        self.muteButton.config(text=u)
        # update the volume slider
        self.OnVolume()

    def OnOpen(self, *unused):
        """Pop up a new dialow window to choose a file, then play the selected file.
        """
        # if a file is already running, then stop it.
        self.OnStop()
        # Create a file dialog opened in the current home directory, where
        # you can display all kind of files, having as title "Choose a video".
        video = askopenfilename(initialdir = Path(expanduser("~")),
                                title = "Choose a video",
                                filetypes = (("all files", "*.*"),
                                             ("mp4 files", "*.mp4"),
                                             ("mov files", "*.mov")))
        self._Play(video)

    def _Pause(self, playing):
        # re-label menu item and button, re-set callback
        c = self.OnPlay if playing is None else self.OnPause
        p = 'Pause' if playing else 'Play'
        self.fileMenu.entryconfig(self.playIndex, label=p, command=c)
        self.playButton.config(text=p, command=c)
        # including macOS shortcut callback kludge
        _Tk_Menu._shortcuts['p'] = c

    def _Play(self, video):
        # helper for OnOpen and OnPlay
        if isfile(video):  # Creation
            m = self.Instance.media_new(str(video))  # Path, unicode
            self.player.set_media(m)
            self.parent.title("tkVLCplayer - %s" % (basename(video),))

            # set the window id where to render VLC's video output
            h = self.videopanel.winfo_id()  # .winfo_visualid()?
            if _isWindows:
                self.player.set_hwnd(h)
            elif _isMacOS:
                # XXX using the videopanel.winfo_id() handle
                # causes the video to play in the entire panel,
                # overwriting the buttons, slider, etc.
                v = _getNSView(h)
                if v:
                    self.player.set_nsobject(v)
                else:
                    self.player.set_xwindow(h)  # plays audio, no video
            else:
                self.player.set_xwindow(h)  # fails on Windows
            # FIXME: this should be made cross-platform
            self.OnPlay()

    def OnPause(self, *unused):
        """Toggle between Pause and Play.
        """
        if self.player.get_media():
            self._Pause(not self.player.is_playing())
            self.player.pause()  # toggles

    def OnPlay(self, *unused):
        """Play video, if none is loaded, open the dialog window.
        """
        # if there's no video to play or playing,
        # open a Tk.FileDialog to select a file
        if not self.player.get_media():
            if self.video:
                self._Play(expanduser(self.video))
                self.video = ''
            else:
                self.OnOpen()
        # Try to play, if this fails display an error message
        elif self.player.play():  # == -1
            self.showError("Unable to play a video.")
        else:
            self._Pause(True)
            # set volume slider to audio level
            vol = self.player.audio_get_volume()
            if vol > 0:
                self.volVar.set(vol)
                self.volSlider.set(vol)
            # adjust window to video aspect ratio
            # w, h = self.player.video_get_size()
            # if h > 0 and w > 0:  # often (0, 0)
            #     self.parent.geometry("%sx%s+0+0" % (w, h))

    def OnStop(self, *unused):
        """Stop the player, resets media.
        """
        if self.player:
            self.player.stop()
            self._Pause(None)
            # reset the time slider
            self.timeSlider.set(0)

    def OnTick(self):
        """Timer tick, update the time slider to the video time.
        """
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

    def OnTime(self, *unused):
        if self.player:
            t = self.timeVar.get()
            if self.timeSliderLast != int(t):
                # this is a hack. The timer updates the time slider.
                # This change causes this rtn (the 'slider has changed' rtn)
                # to be invoked.  I can't tell the difference between when
                # the user has manually moved the slider and when the timer
                # changed the slider.  But when the user moves the slider
                # tkinter only notifies this rtn about once per second and
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
        """Volume slider changed, adjust the audio volume.
        """
        vol = min(self.volVar.get(), 100)
        v_M = "%d%s" % (vol, " (Muted)" if self.muted else '')
        self.volSlider.config(label="Volume " + v_M)
        if self.player and vol > 0:  # and not self.muted:
            # .audio_set_volume returns 0 if success, -1 otherwise,
            # for example if the player doesn't haven any media
            if self.player.audio_set_volume(vol):  # and self.player.get_media():
                self.showError("Failed to set the volume: %s." % (v_M,))

    def showError(self, message):
        """Display a simple error dialog.
        """
        self.OnStop()
        showerror(self.parent.title(), message)


if __name__ == "__main__":

    _video = ''

    while len(sys.argv) > 1:
        arg = sys.argv.pop(1)
        if arg.lower() in ('-v', '--version'):
            # show all versions, sample output on macOS:
            # % python3 ./tkvlc.py -v
            # tkvlc.py: 2019.07.28 (tkinter 8.6 /Library/Frameworks/Python.framework/Versions/3.7/lib/libtk8.6.dylib)
            # vlc.py: 3.0.6109 (Sun Mar 31 20:14:16 2019 3.0.6)
            # LibVLC version: 3.0.6 Vetinari (0x3000600)
            # LibVLC compiler: clang: warning: argument unused during compilation: '-mmacosx-version-min=10.7' [-Wunused-command-line-argument]
            # Plugin path: /Applications/VLC3.0.6.app/Contents/MacOS/plugins
            # Python: 3.7.4 (64bit) macOS 10.13.6

            # Print version of this vlc.py and of the libvlc
            print('%s: %s (%s %s %s)' % (basename(__file__), __version__,
                                         Tk.__name__, Tk.TkVersion, libtk))
            try:
                vlc.print_version()
                vlc.print_python()
            except AttributeError:
                pass
            sys.exit(0)

        elif arg.startswith('-'):
            print('usage: %s  [-v | --version]  [<video_file_name>]' % (sys.argv[0],))
            sys.exit(1)

        elif arg:  # video file
            _video = expanduser(arg)
            if not isfile(_video):
                print('%s error: no such file: %r' % (sys.argv[0], arg))
                sys.exit(1)

    # Create a Tk.App() to handle the windowing event loop
    root = Tk.Tk()
    player = Player(root, video=_video)
    root.protocol("WM_DELETE_WINDOW", player.OnClose)  # XXX unnecessary (on macOS)
    root.mainloop()
