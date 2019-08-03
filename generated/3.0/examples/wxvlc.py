#! /usr/bin/python
# -*- coding: utf-8 -*-

# <https://github.com/oaubert/python-vlc/blob/master/examples/wxvlc.py>
#
# WX example for VLC Python bindings
# Copyright (C) 2009-2010 the VideoLAN team
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
"""
A simple example for VLC python bindings using wxPython.

Author: Michele Orrù
Date: 23-11-2010
"""

# Tested with Python 3.7.4, wxPython 4.0.6 on macOS 10.13.6 only.
__version__ = '19.07.28'  # mrJean1 at Gmail dot com

# import external libraries
import wx  # 2.8 ... 4.0.6
import vlc

# import standard libraries
from os.path import basename, expanduser, isfile, join as joined
import sys

try:
    unicode        # Python 2
except NameError:
    unicode = str  # Python 3


class Player(wx.Frame):
    """The main window has to deal with events.
    """
    def __init__(self, title='', video=''):
        wx.Frame.__init__(self, None, -1, title=title or 'wxVLC',
                          pos=wx.DefaultPosition, size=(550, 500))

        self.video = video

        # Menu Bar
        #   File Menu
        self.frame_menubar = wx.MenuBar()
        self.file_menu = wx.Menu()
        self.file_menu.Append(1, "&Open...", "Open from file...")
        self.file_menu.AppendSeparator()
        self.file_menu.Append(2, "&Close", "Quit")
        self.Bind(wx.EVT_MENU, self.OnOpen, id=1)
        self.Bind(wx.EVT_MENU, self.OnExit, id=2)
        self.frame_menubar.Append(self.file_menu, "File")
        self.SetMenuBar(self.frame_menubar)

        # Panels
        # The first panel holds the video and it's all black
        self.videopanel = wx.Panel(self, -1)
        self.videopanel.SetBackgroundColour(wx.BLACK)

        # The second panel holds controls
        ctrlpanel = wx.Panel(self, -1)
        self.timeslider = wx.Slider(ctrlpanel, -1, 0, 0, 1000)
        self.timeslider.SetRange(0, 1000)
        self.pause = wx.Button(ctrlpanel, label="Pause")
        self.pause.Disable()
        self.play = wx.Button(ctrlpanel, label="Play")
        self.stop = wx.Button(ctrlpanel, label="Stop")
        self.stop.Disable()
        self.mute = wx.Button(ctrlpanel, label="Mute")
        self.volslider = wx.Slider(ctrlpanel, -1, 0, 0, 100, size=(100, -1))

        # Bind controls to events
        self.Bind(wx.EVT_BUTTON, self.OnPlay,   self.play)
        self.Bind(wx.EVT_BUTTON, self.OnPause,  self.pause)
        self.Bind(wx.EVT_BUTTON, self.OnStop,   self.stop)
        self.Bind(wx.EVT_BUTTON, self.OnMute,   self.mute)
        self.Bind(wx.EVT_SLIDER, self.OnVolume, self.volslider)

        # Give a pretty layout to the controls
        ctrlbox = wx.BoxSizer(wx.VERTICAL)
        box1 = wx.BoxSizer(wx.HORIZONTAL)
        box2 = wx.BoxSizer(wx.HORIZONTAL)
        # box1 contains the timeslider
        box1.Add(self.timeslider, 1)
        # box2 contains some buttons and the volume controls
        box2.Add(self.play, flag=wx.RIGHT, border=5)
        box2.Add(self.pause)
        box2.Add(self.stop)
        box2.Add((-1, -1), 1)
        box2.Add(self.mute)
        box2.Add(self.volslider, flag=wx.TOP | wx.LEFT, border=5)
        # Merge box1 and box2 to the ctrlsizer
        ctrlbox.Add(box1, flag=wx.EXPAND | wx.BOTTOM, border=10)
        ctrlbox.Add(box2, 1, wx.EXPAND)
        ctrlpanel.SetSizer(ctrlbox)
        # Put everything togheter
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.videopanel, 1, flag=wx.EXPAND)
        sizer.Add(ctrlpanel, flag=wx.EXPAND | wx.BOTTOM | wx.TOP, border=10)
        self.SetSizer(sizer)
        self.SetMinSize((350, 300))

        # finally create the timer, which updates the timeslider
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)

        # VLC player controls
        self.Instance = vlc.Instance()
        self.player = self.Instance.media_player_new()

    def OnExit(self, evt):
        """Closes the window.
        """
        self.Close()

    def OnOpen(self, evt):
        """Pop up a new dialow window to choose a file, then play the selected file.
        """
        # if a file is already running, then stop it.
        self.OnStop(None)

        video = self.video
        if video:
            self.video = ''
        else:  # Create a file dialog opened in the current home directory,
            # to show all kind of files, having as title "Choose a ...".
            dlg = wx.FileDialog(self, "Choose a video file", expanduser('~'),
                                      "", "*.*", wx.FD_OPEN)  # XXX wx.OPEN
            if dlg.ShowModal() == wx.ID_OK:
                video = joined(dlg.GetDirectory(), dlg.GetFilename())
            # finally destroy the dialog
            dlg.Destroy()

        if isfile(video):  # Creation
            self.Media = self.Instance.media_new(unicode(video))
            self.player.set_media(self.Media)
            # Report the title of the file chosen
            title = self.player.get_title()
            # if an error was encountred while retrieving the title,
            # otherwise use filename
            self.SetTitle("%s - %s" % (title if title != -1 else 'wxVLC', basename(video)))

            # set the window id where to render VLC's video output
            handle = self.videopanel.GetHandle()
            if sys.platform.startswith('linux'):  # for Linux using the X Server
                self.player.set_xwindow(handle)
            elif sys.platform == "win32":  # for Windows
                self.player.set_hwnd(handle)
            elif sys.platform == "darwin":  # for MacOS
                self.player.set_nsobject(handle)
            self.OnPlay(None)

            # set the volume slider to the current volume
            self.volslider.SetValue(self.player.audio_get_volume() / 2)

    def OnPlay(self, evt):
        """Toggle the status to Play/Pause.

        If no file is loaded, open the dialog window.
        """
        # check if there is a file to play, otherwise open a
        # wx.FileDialog to select a file
        if not self.player.get_media():
            self.OnOpen(None)
            # Try to launch the media, if this fails display an error message
        elif self.player.play():  # == -1:
            self.errorDialog("Unable to play.")
        else:
            # adjust window to video aspect ratio
            # w, h = self.player.video_get_size()
            # if h > 0 and w > 0:  # often (0, 0)
            #     self.videopanel....
            self.timer.Start(1000)  # XXX millisecs
            self.play.Disable()
            self.pause.Enable()
            self.stop.Enable()

    def OnPause(self, evt):
        """Pause the player.
        """
        if self.player.is_playing():
            self.play.Enable()
            self.pause.Disable()
        else:
            self.play.Disable()
            self.pause.Enable()
        self.player.pause()

    def OnStop(self, evt):
        """Stop the player.
        """
        self.player.stop()
        # reset the time slider
        self.timeslider.SetValue(0)
        self.timer.Stop()
        self.play.Enable()
        self.pause.Disable()
        self.stop.Disable()

    def OnTimer(self, evt):
        """Update the time slider according to the current movie time.
        """
        # since the self.player.get_length can change while playing,
        # re-set the timeslider to the correct range.
        length = self.player.get_length()
        self.timeslider.SetRange(-1, length)

        # update the time on the slider
        time = self.player.get_time()
        self.timeslider.SetValue(time)

    def OnMute(self, evt):
        """Mute/Unmute according to the audio button.
        """
        muted = self.player.audio_get_mute()
        self.player.audio_set_mute(not muted)
        self.mute.SetLabel("Mute" if muted else "Unmute")
        # update the volume slider;
        # since vlc volume range is in [0, 200],
        # and our volume slider has range [0, 100], just divide by 2.
        # self.volslider.SetValue(self.player.audio_get_volume() / 2)

    def OnVolume(self, evt):
        """Set the volume according to the volume sider.
        """
        volume = self.volslider.GetValue() * 2
        # vlc.MediaPlayer.audio_set_volume returns 0 if success, -1 otherwise
        if self.player.audio_set_volume(volume) == -1:
            self.errorDialog("Failed to set volume")

    def errorDialog(self, errormessage):
        """Display a simple error dialog.
        """
        edialog = wx.MessageDialog(self, errormessage, 'Error', wx.OK|
                                                                wx.ICON_ERROR)
        edialog.ShowModal()


if __name__ == "__main__":

    _video = ''

    while len(sys.argv) > 1:
        arg = sys.argv.pop(1)
        if arg.lower() in ('-v', '--version'):
            # show all versions, sample output on macOS:
            # % python3 ./wxvlc.py -v
            # wxvlc.py: 19.07.28 (wx 4.0.6 osx-cocoa (phoenix) wxWidgets 3.0.5 _core.cpython-37m-darwin.so)
            # vlc.py: 3.0.6109 (Sun Mar 31 20:14:16 2019 3.0.6)
            # LibVLC version: 3.0.6 Vetinari (0x3000600)
            # LibVLC compiler: clang: warning: argument unused during compilation: '-mmacosx-version-min=10.7' [-Wunused-command-line-argument]
            # Plugin path: /Applications/VLC3.0.6.app/Contents/MacOS/plugins
            # Python: 3.7.4 (64bit) macOS 10.13.6

            # Print version of this vlc.py and of the libvlc
            c = basename(str(wx._core).split()[-1].rstrip('>').strip("'").strip('"'))
            print('%s: %s (%s %s %s)' % (basename(__file__), __version__,
                                         wx.__name__, wx.version(), c))
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

    # Create a wx.App(), which handles the windowing system event loop
    app = wx.App()  # XXX wx.PySimpleApp()
    # Create the window containing our media player
    player = Player(video=_video)
    # show the player window centred
    player.Centre()
    player.Show()
    # run the application
    app.MainLoop()
