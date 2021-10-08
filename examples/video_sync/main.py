#! /usr/bin/env python3
#
# PyQt5-based video-sync example for VLC Python bindings
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
A VLC python bindings player implemented with PyQt5 that is meant to be utilized
as the "master" player that controls all "slave players".

Author: Saveliy Yusufov, Columbia University, sy2685@columbia.edu
Date: 25 January 2019
"""

import platform
import queue
import os
import subprocess
import sys

from PyQt5 import QtWidgets, QtGui, QtCore
import vlc
from network import Server


class Player(QtWidgets.QMainWindow):
    """A "master" Media Player using VLC and Qt
    """

    def __init__(self, master=None):
        QtWidgets.QMainWindow.__init__(self, master)
        self.setWindowTitle("Main Media Player")

        # Create a basic vlc instance
        self.instance = vlc.Instance()

        self.media = None

        # Create an empty vlc media player
        self.mediaplayer = self.instance.media_player_new()

        self.create_ui()
        self.data_queue = queue.Queue()
        self.is_paused = False

        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_ui)
        self.timer.timeout.connect(self.update_time_label)

    def create_ui(self):
        """Set up the user interface, signals & slots
        """
        self.widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.widget)

        # In this widget, the video will be drawn
        if platform.system() == "Darwin":  # for MacOS
            self.videoframe = QtWidgets.QMacCocoaViewContainer(0)
        else:
            self.videoframe = QtWidgets.QFrame()

        self.palette = self.videoframe.palette()
        self.palette.setColor(QtGui.QPalette.Window, QtGui.QColor(0, 0, 0))
        self.videoframe.setPalette(self.palette)
        self.videoframe.setAutoFillBackground(True)

        # Create the time display
        self.timelabel = QtWidgets.QLabel("00:00:00", self)

        # Create the position slider (QSlider)
        self.positionslider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.positionslider.setToolTip("Position")
        self.positionslider.setMaximum(1000)
        self.positionslider.sliderMoved.connect(self.set_position)
        # self.positionslider.sliderPressed.connect(self.set_position)
        self.positionslider.sliderMoved.connect(self.update_time_label)

        # Create the "previous frame" button
        self.previousframe = QtWidgets.QPushButton()
        self.previousframe.setFixedWidth(25)
        self.previousframe.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaSkipBackward))
        self.previousframe.clicked.connect(self.on_previous_frame)

        # Create the play button and connect it to the play/pause function
        self.playbutton = QtWidgets.QPushButton()
        self.playbutton.setFixedWidth(40)
        self.playbutton.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay))
        self.playbutton.clicked.connect(self.play_pause)

        # Create the "next frame" button
        self.nextframe = QtWidgets.QPushButton()
        self.nextframe.setFixedWidth(25)
        self.nextframe.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaSkipForward))
        self.nextframe.clicked.connect(self.on_next_frame)

        # Create the "Playback rate" label
        self.pb_rate_label = QtWidgets.QLabel("Playback rate: {}x".format(self.mediaplayer.get_rate()), self)

        # Create the "decrease playback rate" button
        self.decr_pb_rate = QtWidgets.QPushButton()
        self.decr_pb_rate.setFixedWidth(30)
        self.decr_pb_rate.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaSeekBackward))
        self.decr_pb_rate.clicked.connect(self.decr_mov_play_rate)

        # Create the stop button and connect it to the stop function
        self.stopbutton = QtWidgets.QPushButton()
        self.stopbutton.setFixedWidth(30)
        self.stopbutton.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaStop))
        self.stopbutton.clicked.connect(self.stop)

        # Create the "increase playback rate" button
        self.incr_pb_rate = QtWidgets.QPushButton()
        self.incr_pb_rate.setFixedWidth(30)
        self.incr_pb_rate.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaSeekForward))
        self.incr_pb_rate.clicked.connect(self.incr_mov_play_rate)

        self.top_control_box = QtWidgets.QHBoxLayout()

        # Add the time and position slider to the 1st controls layout
        self.top_control_box.addWidget(self.timelabel)
        self.top_control_box.addWidget(self.positionslider)

        self.bottom_control_box = QtWidgets.QHBoxLayout()

        # Add the buttons to the 2nd controls layout
        self.bottom_control_box.addWidget(self.previousframe)
        self.bottom_control_box.addWidget(self.playbutton)
        self.bottom_control_box.addWidget(self.nextframe)
        self.bottom_control_box.addWidget(self.pb_rate_label)
        self.bottom_control_box.addWidget(self.decr_pb_rate)
        self.bottom_control_box.addWidget(self.stopbutton)
        self.bottom_control_box.addWidget(self.incr_pb_rate)

        self.vboxlayout = QtWidgets.QVBoxLayout()

        self.vboxlayout.addWidget(self.videoframe)
        self.vboxlayout.addLayout(self.top_control_box)
        self.vboxlayout.addLayout(self.bottom_control_box)

        self.widget.setLayout(self.vboxlayout)

        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("File")

        # Create submenu to start new processes from file menu
        new_menu = QtWidgets.QMenu("Launch", self)
        file_menu.addMenu(new_menu)
        new_video_action = QtWidgets.QAction("New Video", self)
        new_menu.addAction(new_video_action)
        new_video_action.triggered.connect(on_new_video)

        # Create actions to load a new media file and to close the app
        open_action = QtWidgets.QAction("Load Video", self)
        close_action = QtWidgets.QAction("Close App", self)
        file_menu.addAction(open_action)
        file_menu.addAction(close_action)
        open_action.triggered.connect(self.open_file)
        close_action.triggered.connect(sys.exit)

    def play_pause(self):
        """Toggle play/pause status
        """
        if self.mediaplayer.is_playing():
            signal = 'p'
            self.mediaplayer.pause()
            self.playbutton.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay))
            self.is_paused = True
            self.timer.stop()
        else:
            if self.mediaplayer.play() == -1:
                self.open_file()
                return

            signal = 'P'
            self.mediaplayer.play()
            self.playbutton.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaPause))
            self.timer.start()
            self.is_paused = False

        # Reset the queue & send the appropriate signal, i.e., play/pause
        self.data_queue.queue.clear()
        self.data_queue.put('d')
        self.data_queue.put(signal)

    def stop(self):
        """Stop player
        """
        self.mediaplayer.stop()
        self.playbutton.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay))

        # Reset the time label back to 00:00:00
        time = QtCore.QTime(0, 0, 0, 0)
        self.timelabel.setText(time.toString())

        # Reset the queue
        self.data_queue.queue.clear()
        self.data_queue.put('d')
        self.data_queue.put('S')

        # Reset the media position slider
        self.positionslider.setValue(0)

        self.timer.stop()

    def on_next_frame(self):
        """Go forward one frame.

            The Python VLC binding next_frame function causes a:

            "direct3d11 vout display error: SetThumbNailClip failed"

            error when next_frame is called while the video is playing,
            so we are using our own fucntion to get the next frame.
        """
        # self.mediaplayer.next_frame()
        next_frame_time = self.mediaplayer.get_time() + self.mspf()

        # Reset the queue & put the next frame's time into the queue
        self.data_queue.queue.clear()
        self.data_queue.put('d')
        self.data_queue.put(next_frame_time)
        self.update_time_label()
        self.mediaplayer.set_time(next_frame_time)

    def on_previous_frame(self):
        """Go backward one frame"""
        next_frame_time = self.mediaplayer.get_time() - self.mspf()

        # Reset the queue & put the next frame's time into the queue
        self.data_queue.queue.clear()
        self.data_queue.put('d')
        self.data_queue.put(next_frame_time)
        self.update_time_label()
        self.mediaplayer.set_time(next_frame_time)

    def mspf(self):
        """Milliseconds per frame"""
        return int(1000 // (self.mediaplayer.get_fps() or 25))

    def incr_mov_play_rate(self):
        """Increase the movie play rate by a factor of 2."""
        if self.mediaplayer.get_rate() >= 64:
            return

        rate = self.mediaplayer.get_rate() * 2
        result = self.mediaplayer.set_rate(rate)
        if result == 0:
            self.data_queue.queue.clear()
            self.data_queue.put('d')
            self.data_queue.put('>')
            self.update_pb_rate_label()

    def decr_mov_play_rate(self):
        """Decrease the movie play rate by a factor of 2."""
        if self.mediaplayer.get_rate() <= 0.125:
            return

        rate = self.mediaplayer.get_rate() * 0.5
        result = self.mediaplayer.set_rate(rate)
        if result == 0:
            self.data_queue.queue.clear()
            self.data_queue.put('d')
            self.data_queue.put('<')
            self.update_pb_rate_label()

    def open_file(self):
        """Open a media file in a MediaPlayer
        """
        dialog_txt = "Choose Media File"
        filename = QtWidgets.QFileDialog.getOpenFileName(self, dialog_txt, os.path.expanduser('~'))
        if not filename[0]:
            return

        # getOpenFileName returns a tuple, so use only the actual file name
        self.media = self.instance.media_new(filename[0])

        # Put the media in the media player
        self.mediaplayer.set_media(self.media)

        # Parse the metadata of the file
        self.media.parse()

        # Set the title of the track as window title
        self.setWindowTitle("Main Media Player: {}".format(self.media.get_meta(0)))

        # The media player has to be 'connected' to the QFrame (otherwise the
        # video would be displayed in it's own window). This is platform
        # specific, so we must give the ID of the QFrame (or similar object) to
        # vlc. Different platforms have different functions for this.
        if platform.system() == "Linux":  # for Linux using the X Server
            self.mediaplayer.set_xwindow(int(self.videoframe.winId()))
        elif platform.system() == "Windows":  # for Windows
            self.mediaplayer.set_hwnd(int(self.videoframe.winId()))
        elif platform.system() == "Darwin":  # for MacOS
            self.mediaplayer.set_nsobject(int(self.videoframe.winId()))

        self.play_pause()

    def set_position(self):
        """Set the movie position according to the position slider.

        The vlc MediaPlayer needs a float value between 0 and 1, Qt uses
        integer variables, so you need a factor; the higher the factor,
        the more precise are the results (1000 should suffice).
        """
        # Set the media position to where the slider was dragged
        self.timer.stop()
        pos = self.positionslider.value()

        if pos >= 0:
            self.data_queue.queue.clear()
            self.data_queue.put('d')
            current_time = self.mediaplayer.get_time()

            # If the player is stopped, do not attempt to send a -1!!!
            if current_time == -1:
                self.timer.start()
                return
            self.data_queue.put(current_time)

        self.mediaplayer.set_position(pos * .001)
        self.timer.start()

    def update_ui(self):
        """Updates the user interface"""

        # Set the slider's position to its corresponding media position
        # Note that the setValue function only takes values of type int,
        # so we must first convert the corresponding media position.
        media_pos = int(self.mediaplayer.get_position() * 1000)
        self.positionslider.setValue(media_pos)

        if media_pos >= 0 and self.mediaplayer.is_playing():
            current_time = self.mediaplayer.get_time()
            self.data_queue.put(current_time)
        else:
            self.data_queue.queue.clear()

        # No need to call this function if nothing is played
        if not self.mediaplayer.is_playing():
            self.timer.stop()

            # After the video finished, the play button stills shows "Pause",
            # which is not the desired behavior of a media player.
            # This fixes that "bug".
            if not self.is_paused:
                self.stop()

    def update_time_label(self):
        mtime = QtCore.QTime(0, 0, 0, 0)
        self.time = mtime.addMSecs(self.mediaplayer.get_time())
        self.timelabel.setText(self.time.toString())

    def update_pb_rate_label(self):
        self.pb_rate_label.setText("Playback rate: {}x".format(str(self.mediaplayer.get_rate())))


def on_new_video():
    """Launches a new PyQt5-based "mini" media player
    """
    if platform.system() == "Windows":
        subprocess.Popen(["python", "mini_player.py"], shell=True)
    else:
        subprocess.Popen(["python", "mini_player.py"])


def main():
    """Entry point for our simple vlc player
    """
    app = QtWidgets.QApplication(sys.argv)
    player = Player()

    _ = Server("localhost", 10000, player.data_queue)

    player.show()
    player.resize(640, 480)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
