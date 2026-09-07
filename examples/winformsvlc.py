"""
A simple example for VLC python bindings using Python.NET and Windows Forms.

Author: https://github.com/59de44955ebd, Berlin
Date: 26.08.2026

Python.NET (https://pypi.org/project/pythonnet/) can be installed with pip:
pip install pythonnet
"""
import clr
import System
clr.AddReference('System.Windows.Forms')
from System.Threading import Thread, ThreadStart, ApartmentState
import System.Windows.Forms as WinForms
from System.Drawing import Color, Size

import vlc


class Main(WinForms.Form):

    def __init__(self):
        super().__init__()

        self.Text = "Media Player"
        self.Size = Size(640, 480)
        self.StartPosition = WinForms.FormStartPosition.CenterScreen

        # Create a basic vlc instance
        self.instance = vlc.Instance(["--quiet", "--no-osd"])

        self.media = None

        # Create an empty vlc media player
        self.mediaplayer = self.instance.media_player_new()

        self.initialize_component()

        self.is_paused = False

        # The media player has to be "connected" to our VideoFrame
        self.mediaplayer.set_hwnd(self.video_frame.Handle.ToInt32())

        self.timer = WinForms.Timer()
        self.timer.Interval = 100
        self.timer.Tick += self.update_ui

    def initialize_component(self):
        self.SuspendLayout()

        self.Menu = WinForms.MainMenu()
        m = WinForms.MenuItem('&File')
        self.Menu.MenuItems.Add(m)
        action_item = WinForms.MenuItem('&Load Video')
        action_item.Shortcut = WinForms.Shortcut.CtrlO
        action_item.Click += self.open_file
        m.MenuItems.Add(action_item)
        m.MenuItems.Add(WinForms.MenuItem('-'))
        action_item = WinForms.MenuItem('&Close App')
        action_item.Click += self.quit
        m.MenuItems.Add(action_item)

        self.panel1 = WinForms.Panel()
        self.Controls.Add(self.panel1)
        self.panel1.Dock = WinForms.DockStyle.Fill

        self.video_frame = WinForms.UserControl()
        self.video_frame.BackColor = Color.Black
        self.video_frame.Dock = WinForms.DockStyle.Fill
        self.panel1.Controls.Add(self.video_frame)

        self.panel2 = WinForms.TableLayoutPanel()
        self.panel2.Padding = WinForms.Padding(7, 0, 7, 0)
        self.panel2.Height = 70
        self.panel2.Dock = WinForms.DockStyle.Bottom
        self.panel2.ColumnCount = 3
        self.panel2.RowCount = 2
        self.Controls.Add(self.panel2)

        self.trackbar_position = WinForms.TrackBar()
        self.trackbar_position.Maximum = 2000
        self.trackbar_position.Dock = WinForms.DockStyle.Bottom
        self.trackbar_position.AutoSize = False
        self.trackbar_position.Height = 30
        self.trackbar_position.TickStyle = getattr(WinForms.TickStyle, 'None')
        self.trackbar_position.Anchor = WinForms.AnchorStyles.Left | WinForms.AnchorStyles.Top | WinForms.AnchorStyles.Right
        self.trackbar_position.Enabled = False
        self.panel2.Controls.Add(self.trackbar_position, 0, 0)
        self.panel2.SetColumnSpan(self.trackbar_position, 3)
        self.trackbar_position.Scroll += lambda sender, args: self.set_position(self.trackbar_position.Value)

        def _on_click(sender, args):
            w = self.trackbar_position.Width - 28
            x = args.X - 14
            pos = max(0, min(2000, int(x / w * 2000)))
            self.trackbar_position.Value = pos
            self.set_position(pos)

        self.trackbar_position.MouseDown += _on_click

        self.button_play = WinForms.Button()
        self.button_play.Text = "Play"
        self.button_play.Anchor = WinForms.AnchorStyles.Left | WinForms.AnchorStyles.Top
        self.panel2.Controls.Add(self.button_play, 0, 1)
        self.button_play.Click += self.play_pause

        self.button_stop = WinForms.Button()
        self.button_stop.Text = "Stop"
        self.button_stop.Anchor = WinForms.AnchorStyles.Left | WinForms.AnchorStyles.Top
        self.panel2.Controls.Add(self.button_stop, 1, 1)
        self.button_stop.Click += self.stop

        self.trackbar_volume = WinForms.TrackBar()
        self.trackbar_volume.Maximum = 100
        self.trackbar_volume.Anchor = WinForms.AnchorStyles.Right | WinForms.AnchorStyles.Top
        self.trackbar_volume.AutoSize = False
        self.trackbar_volume.Height = 20
        self.trackbar_volume.TickStyle = getattr(WinForms.TickStyle, 'None')
        self.trackbar_volume.Value = self.mediaplayer.audio_get_volume()
        self.panel2.Controls.Add(self.trackbar_volume, 2, 1)
        self.trackbar_volume.Scroll += lambda *_: self.set_volume(self.trackbar_volume.Value)

        def _on_click(sender, args):
            w = self.trackbar_volume.Width - 28
            x = args.X - 14
            pos = max(0, min(100, int(x / w * 100)))
            self.trackbar_volume.Value = pos
            self.set_volume(pos)

        self.trackbar_volume.MouseDown += _on_click

        self.ResumeLayout(False)
        self.PerformLayout()

    def open_file(self, *_):
        ofd = WinForms.OpenFileDialog()
        ofd.Filter = "All Files (*.*)|*.*"
        ofd.RestoreDirectory = True
        if ofd.ShowDialog() != WinForms.DialogResult.OK:
            return

        self.media = self.instance.media_new(ofd.FileName)

        # Put the media in the media player
        self.mediaplayer.set_media(self.media)

        # Parse the metadata of the file
        self.media.parse()

        # Set the title of the track as window title
        self.Text = self.media.get_meta(0)

        self.play_pause()

    def play_pause(self, *_):
        """Toggle play/pause status"""
        if self.mediaplayer.is_playing():
            self.mediaplayer.pause()
            self.button_play.Text = "Play"
            self.is_paused = True
            self.timer.Stop()
        else:
            if self.mediaplayer.play() == -1:
                self.open_file()
                return

            self.mediaplayer.play()
            self.button_play.Text = "Pause"
            self.is_paused = False
            self.timer.Start()
        self.trackbar_position.Enabled = True

    def stop(self, *_):
        """Stop player"""
        self.mediaplayer.stop()
        self.button_play.Text = "Play"
        self.trackbar_position.Enabled = False

    def quit(self, *_):
        WinForms.Application.Exit()

    def set_volume(self, volume):
        """Set the volume"""
        self.mediaplayer.audio_set_volume(volume)

    def set_position(self, pos):
        """Set the movie position according to the position slider"""
        # Set the media position to where the slider was dragged
        self.timer.Stop()
        self.mediaplayer.set_position(pos / 2000.0)
        self.timer.Start()

    def update_ui(self, *_):
        """Update the user interface"""
        # Set the slider"s position to its corresponding media position
        self.trackbar_position.Value = min(2000, max(0, int(self.mediaplayer.get_position() * 2000)))

        # No need for a timer if nothing is played
        if not self.mediaplayer.is_playing():
            self.timer.Stop()

            # After the video finished, the play button stills shows "Pause",
            # which is not the desired behavior of a media player.
            # This fixes that "bug".
            if not self.is_paused:
                self.stop()


def app_thread():
    app = Main()
    WinForms.Application.Run(app)
    app.Dispose()

if __name__ == '__main__':
    thread = Thread(ThreadStart(app_thread))
    thread.SetApartmentState(ApartmentState.STA)
    thread.Start()
    thread.Join()
