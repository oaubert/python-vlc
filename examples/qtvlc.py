#! /usr/bin/python

#
# Qt example for VLC Python bindings
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

import sys
import os
import user
import vlc
from PyQt4 import QtGui, QtCore

class Player(QtGui.QMainWindow):
    """A simple Media Player using VLC and Qt
    """
    def __init__(self, master=None):
        QtGui.QMainWindow.__init__(self, master)
        self.setWindowTitle("Media Player")

        # creating a basic vlc instance
        self.Instance = vlc.Instance()
        # creating an empty vlc media player
        self.MediaPlayer = self.Instance.media_player_new()

        self.createUI()
        self.isPaused = False

    def createUI(self):
        """Set up the user interface, signals & slots
        """
        self.Widget = QtGui.QWidget(self)
        self.setCentralWidget(self.Widget)

        # In this widget, the video will be drawn
        self.VideoFrame = QtGui.QFrame()
        self.Palette = self.VideoFrame.palette()
        self.Palette.setColor (QtGui.QPalette.Window,
                               QtGui.QColor(0,0,0))
        self.VideoFrame.setPalette(self.Palette)
        self.VideoFrame.setAutoFillBackground(True)

        self.PositionSlider = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.PositionSlider.setToolTip("Position")
        self.PositionSlider.setMaximum(1000)
        self.connect(self.PositionSlider,
                     QtCore.SIGNAL("sliderMoved(int)"), self.setPosition)

        self.HButtonBox = QtGui.QHBoxLayout()
        self.PlayButton = QtGui.QPushButton("Play")
        self.HButtonBox.addWidget(self.PlayButton)
        self.connect(self.PlayButton, QtCore.SIGNAL("clicked()"),
                     self.PlayPause)

        self.StopButton = QtGui.QPushButton("Stop")
        self.HButtonBox.addWidget(self.StopButton)
        self.connect(self.StopButton, QtCore.SIGNAL("clicked()"),
                     self.Stop)

        self.HButtonBox.addStretch(1)
        self.VolumeSlider = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.VolumeSlider.setMaximum(100)
        self.VolumeSlider.setValue(self.MediaPlayer.audio_get_volume())
        self.VolumeSlider.setToolTip("Volume")
        self.HButtonBox.addWidget(self.VolumeSlider)
        self.connect(self.VolumeSlider,
                     QtCore.SIGNAL("valueChanged(int)"),self.setVolume)

        self.VBoxLayout = QtGui.QVBoxLayout()
        self.VBoxLayout.addWidget(self.VideoFrame)
        self.VBoxLayout.addWidget(self.PositionSlider)
        self.VBoxLayout.addLayout(self.HButtonBox)

        self.Widget.setLayout(self.VBoxLayout)

        open = QtGui.QAction("&Open", self)
        self.connect(open, QtCore.SIGNAL("triggered()"), self.OpenFile)
        exit = QtGui.QAction("&Exit", self)
        self.connect(exit, QtCore.SIGNAL("triggered()"), sys.exit)
        menubar = self.menuBar()
        file = menubar.addMenu("&File")
        file.addAction(open)
        file.addSeparator()
        file.addAction(exit)

        self.Timer = QtCore.QTimer(self)
        self.Timer.setInterval(200)
        self.connect(self.Timer, QtCore.SIGNAL("timeout()"),
                     self.updateUI)

    def PlayPause(self):
        """Toggle play/pause status
        """
        if self.MediaPlayer.is_playing():
            self.MediaPlayer.pause()
            self.PlayButton.setText("Play")
            self.isPaused = True
        else:
            if self.MediaPlayer.play() == -1:
                self.OpenFile()
                return
            self.MediaPlayer.play()
            self.PlayButton.setText("Pause")
            self.Timer.start()
            self.isPaused = False

    def Stop(self):
        """Stop player
        """
        self.MediaPlayer.stop()
        self.PlayButton.setText("Play")

    def OpenFile(self):
        """Open a media file in a MediaPlayer
        """
        filename = QtGui.QFileDialog.getOpenFileName(self,
                                                     "Open File", user.home)
        if not filename:
            return

        # create the media
        self.Media = self.Instance.media_new(unicode(filename))
        # put the media in the media player
        self.MediaPlayer.set_media(self.Media)

        # parse the metadata of the file
        self.Media.parse()
        # set the title of the track as window title
        self.setWindowTitle(self.Media.get_meta(0))

        # the media player has to be 'connected' to the QFrame
        # (otherwise a video would be displayed in it's own window)
        # this is platform specific!
        # you have to give the id of the QFrame (or similar object) to
        # vlc, different platforms have different functions for this
        if sys.platform == "linux2": # for Linux using the X Server
            self.MediaPlayer.set_xwindow(self.VideoFrame.winId())
        elif sys.platform == "win32": # for Windows
            self.MediaPlayer.set_hwnd(self.VideoFrame.winId())
        elif sys.platform == "darwin": # for MacOS
            self.MediaPlayer.set_agl(self.VideoFrame.windId())
        self.PlayPause()

    def setVolume(self, Volume):
        """Set the volume
        """
        self.MediaPlayer.audio_set_volume(Volume)

    def setPosition(self, Position):
        """Set the position
        """
        # setting the position to where the slider was dragged
        self.MediaPlayer.set_position(Position / 1000.0)
        # the vlc MediaPlayer needs a float value between 0 and 1, Qt
        # uses integer variables, so you need a factor; the higher the
        # factor, the more precise are the results
        # (1000 should be enough)

    def updateUI(self):
        """updates the user interface"""
        # setting the slider to the desired position
        self.PositionSlider.setValue(self.MediaPlayer.get_position() * 1000)

        if not self.MediaPlayer.is_playing():
            # no need to call this function if nothing is played
            self.Timer.stop()
            if not self.isPaused:
                # after the video finished, the play button stills shows
                # "Pause", not the desired behavior of a media player
                # this will fix it
                self.Stop()

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    MediaPlayer = Player()
    MediaPlayer.show()
    MediaPlayer.resize(640, 480)
    sys.exit(app.exec_())
