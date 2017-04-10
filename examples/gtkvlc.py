#! /usr/bin/python

#
# gtk3 example/widget for VLC Python bindings
# Copyright (C) 2017 Olivier Aubert <contact@olivieraubert.net>
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

"""VLC Gtk3 Widget classes + example application.

This module provides two helper classes, to ease the embedding of a
VLC component inside a pygtk application.

VLCWidget is a simple VLC widget.

DecoratedVLCWidget provides simple player controls.

When called as an application, it behaves as a video player.
"""

import gi
gi.require_version('Gdk', '3.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gdk
from gi.repository import Gtk

Gdk.threads_init ()

import sys
import vlc

from gettext import gettext as _

# Create a single vlc.Instance() to be shared by (possible) multiple players.
if 'linux' in sys.platform:
    # Inform libvlc that Xlib is not initialized for threads
    instance = vlc.Instance("--no-xlib")
else:
    instance = vlc.Instance()

class VLCWidget(Gtk.DrawingArea):
    """Simple VLC widget.

    Its player can be controlled through the 'player' attribute, which
    is a vlc.MediaPlayer() instance.
    """
    __gtype_name__ = 'VLCWidget'

    def __init__(self, *p):
        Gtk.DrawingArea.__init__(self)
        self.player = instance.media_player_new()
        def handle_embed(*args):
            if sys.platform == 'win32':
                self.player.set_hwnd(self.get_window().get_handle())
            else:
                self.player.set_xwindow(self.get_window().get_xid())
            return True
        self.connect("realize", handle_embed)
        self.set_size_request(320, 200)

class DecoratedVLCWidget(Gtk.VBox):
    """Decorated VLC widget.

    VLC widget decorated with a player control toolbar.

    Its player can be controlled through the 'player' attribute, which
    is a Player instance.
    """
    __gtype_name__ = 'DecoratedVLCWidget'

    def __init__(self, *p):
        super(DecoratedVLCWidget, self).__init__()
        self._vlc_widget = VLCWidget(*p)
        self.player = self._vlc_widget.player
        self.add(self._vlc_widget)
        self._toolbar = self.get_player_control_toolbar()
        self.pack_start(self._toolbar, False, False, 0)
        self.show_all()

    def get_player_control_toolbar(self):
        """Return a player control toolbar
        """
        tb = Gtk.Toolbar.new()
        for text, tooltip, iconname, callback in (
            (_("Play"), _("Play"), 'gtk-media-play', lambda b: self.player.play()),
            (_("Pause"), _("Pause"), 'gtk-media-pause', lambda b: self.player.pause()),
            (_("Stop"), _("Stop"), 'gtk-media-stop', lambda b: self.player.stop()),
            (_("Quit"), _("Quit"), 'gtk-quit', Gtk.main_quit),
            ):
            i = Gtk.Image.new_from_icon_name(iconname, Gtk.IconSize.MENU)
            b = Gtk.ToolButton(i, text)
            b.set_tooltip_text(tooltip)
            b.connect("clicked", callback)
            tb.insert(b, -1)
        return tb

class VideoPlayer:
    """Example simple video player.
    """
    def __init__(self):
        self.vlc = DecoratedVLCWidget()

    def main(self, fname):
        self.vlc.player.set_media(instance.media_new(fname))
        w = Gtk.Window()
        w.add(self.vlc)
        w.show_all()
        w.connect("destroy", Gtk.main_quit)
        Gtk.main()

class MultiVideoPlayer:
    """Example multi-video player.

    It plays multiple files side-by-side, with per-view and global controls.
    """
    def main(self, filenames):
        # Build main window
        window=Gtk.Window()
        mainbox=Gtk.VBox()
        videos=Gtk.HBox()

        window.add(mainbox)
        mainbox.add(videos)

        # Create VLC widgets
        for fname in filenames:
            v = DecoratedVLCWidget()
            v.player.set_media(instance.media_new(fname))
            videos.add(v)

        # Create global toolbar
        tb = Gtk.Toolbar.new()

        def execute(b, methodname):
            """Execute the given method on all VLC widgets.
            """
            for v in videos.get_children():
                getattr(v.player, methodname)()
            return True

        for text, tooltip, iconname, callback, arg in (
            (_("Play"), _("Global play"), 'gtk-media-play', execute, "play"),
            (_("Pause"), _("Global pause"), 'gtk-media-pause', execute, "pause"),
            (_("Stop"), _("Global stop"), 'gtk-media-stop', execute, "stop"),
            (_("Quit"), _("Quit"), 'gtk-quit', Gtk.main_quit, None),
            ):
            i = Gtk.Image.new_from_icon_name(iconname, Gtk.IconSize.MENU)
            b = Gtk.ToolButton.new(i, text)
            b.set_tooltip_text(tooltip)
            b.connect("clicked", callback, arg)
            tb.insert(b, -1)

        mainbox.pack_start(tb, False, False, 0)

        window.show_all()
        window.connect("destroy", Gtk.main_quit)
        Gtk.main()

if __name__ == '__main__':
    if not sys.argv[1:]:
       print('You must provide at least 1 movie filename')
       sys.exit(1)
    if len(sys.argv[1:]) == 1:
        # Only 1 file. Simple interface
        p=VideoPlayer()
        from evaluator import Evaluator
        e = Evaluator(globals(), locals())
        e.popup()
        p.main(sys.argv[1])
    else:
        # Multiple files.
        p=MultiVideoPlayer()
        p.main(sys.argv[1:])
    instance.release()
