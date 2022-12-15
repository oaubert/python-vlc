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
# and 3.7.4 and with tkinter/Tk 8.6.9 on macOS 13.0.1 (amd64 M1), 11.6.1
# (10.16 amd64 M1), 11.0.1 (10.16 x86-64) and 10.13.6 and with VLC 3.0.18,
# Python 3.11.0 and tkinter/Tk 8.6.9 on Windows 10, all in 64-bit only.
__version__ = '22.12.14'  # mrJean1 at Gmail

import sys
try:  # Python 3.4+ only
    import tkinter as Tk
    from tkinter import TclError, ttk  # PYCHOK ttk = Tk.ttk
    from tkinter.filedialog import askopenfilename
    from tkinter.messagebox import showerror
except ImportError:
    sys.exit('%s requires Python 3.4 or later' % (sys.argv[0],))
    # import Tkinter as Tk; ttk = Tk
import os
import time
import vlc

_isMacOS   = sys.platform.startswith('darwin')
_isLinux   = sys.platform.startswith('linux')
_isWindows = sys.platform.startswith('win')

_ANCHORED    = 'Anchored'
_BANNER_H    =  32 if _isMacOS else 64
_BUTTONS     = 'Buttons'
_DISABLED    = (      Tk.DISABLED,)
_ENABLED     = ('!' + Tk.DISABLED,)
_FULL_OFF    = 'Full Off'
_FULL_SCREEN = 'Full Screen'
# see _Tk_Menu.add_item and .bind_shortcut below
# <https://www.Tcl.Tk/man/tcl8.6/TkCmd/keysyms.html>
_KEY_SYMBOL  = {'~': 'asciitilde',  '`': 'grave',
                '!': 'exclam',      '@': 'at',
                '#': 'numbersign',  '$': 'dollar',
                '%': 'percent',     '^': 'asciicirum',
                '&': 'ampersand',   '*': 'asterisk',
                '(': 'parenleft',   ')': 'parenright',
                '_': 'underscore',  '-': 'minus',
                '+': 'plus',        '=': 'equal',
                '{': 'braceleft',   '}': 'braceright',
                '[': 'bracketleft', ']': 'bracketright',
                '|': 'bar',        '\\': 'backslash',
                ':': 'colon',       ';': 'semicolon',
                '"': 'quotedbl',    "'": 'apostrophe',
                '<': 'less',        '>': 'greater',
                ',': 'comma',       '.': 'period',
                '?': 'question',    '/': 'slash',
                ' ': 'space',      '\b': 'BackSpace',
               '\n': 'KP_Enter',   '\r': 'Return',
               '\f': 'Next',       '\v': 'Prior',
               '\t': 'Tab'}  # '\a': 'space'?
# see definition of specialAccelerators in <https://
# GitHub.com/tcltk/tk/blob/main/macosx/tkMacOSXMenu.c>
_MAC_ACCEL   = {' ': 'Space',       '\b': 'Backspace',
               '\n': 'Enter',       '\r': 'Return',
               '\f': 'PageDown',    '\v': 'PageUp',
               '\t': 'Tab',  # 'BackTab', 'Eject'?
             'Next': 'PageDown', 'Prior': 'PageUp'}
_MIN_W       =  420
_OPACITY     = 'Opacity %s%%'
_TAB_X       =  32
_T_CONFIGURE =  Tk.EventType.Configure
_TICK_MS     =  100  # millisecs per time tick
_UN_ANCHORED = 'Un-' + _ANCHORED
_VOLUME      = 'Volume'

_TKVLC_LIBTK_PATH = 'TKVLC_LIBTK_PATH'

if _isMacOS:  # MCCABE 14
    from ctypes import cdll, c_void_p
    from ctypes.util import find_library as _find

    # libtk = cdll.LoadLibrary(ctypes.util.find_library('tk'))
    # returns (None or) the tk library /usr/lib/libtk.dylib
    # from macOS, but we need the tkX.Y library bundled with
    # Python 3+ or one matching the version of tkinter

    # Homebrew-built Python, Tcl/Tk, etc. are installed in
    # different places, usually something like (/usr/- or)
    # /opt/local/Cellar/tcl-tk/8.6.11_1/lib/libtk8.6.dylib,
    # found by command line `find /opt -name libtk8.6.dylib`

    def _find_lib(name, *paths):
        assert os.path.sep == '/'
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
        _GetNSView.restype  =  c_void_p
        _GetNSView.argtypes = (c_void_p,)

    except (NameError, OSError) as x:  # lib, image or symbol not found
        libtk = str(x)  # imported by psgvlc.py

        def _GetNSView(unused):  # imported by psgvlc.py
            return None

    del cdll, c_void_p, env, _find
    Cmd_ = 'Command+'  # 'Meta_L' shortcut key modifier

else:  # Windows OK, untested *nix, Xwindows
    libtk = 'N/A'
    Cmd_  = 'Ctrl+'  # shortcut key modifier, Control!


def _frontmost(panel, *ontop):
    # move panel to the front
    t = panel.attributes('-topmost')
    if ontop:  # move on top ...
        m = bool(ontop[0])
        panel.attributes('-topmost', m)
        panel.update_idletasks()
        if m:  # ... but only temporarily
            panel.attributes('-topmost', False)
            try:  # no Toplevel.force_focus
                panel.force_focus()
            except AttributeError:
                pass
    return bool(t)


def _fullscreen(panel, *full):
    # get/set a panel full-screen or -off
    f = panel.attributes('-fullscreen')  # or .wm_attributes
    if full:
        panel.attributes('-fullscreen', bool(full[0]))
        panel.update_idletasks()
    return f


def _geometry(panel, g_w, *h_x_y):
    # set a panel geometry to C{g} or C{w, h, x, y}.
    g = _geometrystr(g_w, *h_x_y) if h_x_y else g_w
    panel.geometry(g)  # update geometry
    panel._g = g = _geometry1(panel)  # get actual
    return g


def _geometry1(panel):
    # get a panel geometry as C{str}
    panel.update_idletasks()
    return panel.geometry()


def _geometry5(panel):
    # get a panel geometry as 5-tuple of C{str}s
    g = _geometry1(panel)  # '+-x' means absolute -x
    z, x, y = g.split('+')
    w, h = z.split('x')
    return g, w, h, x, y


def _geometrystr(w, *h_x_y):
    # return geometry as str "wxh+x+y"
    t = '+'.join(map(str, h_x_y))
    g = 'x'.join((str(w), t))
    return g


def _hms(tensecs, secs=''):
    # format a time (in 1/10-secs) as h:mm:ss.s
    s = tensecs * 0.1
    if s < 60:
        t = '%3.1f%s' % (s, secs)
    else:
        m, s = divmod(s, 60)
        if m < 60:
            t = '%d:%04.1f' % (int(m), s)
        else:
            h, m = divmod(m, 60)
            t = '%d:%02d:%04.1f' % (int(h), int(m), s)
    return t


def _underline2(c, label='', underline=-1, **cfg):
    # update cfg with C{underline=index} or remove C{underline=.}
    u = label.find(c) if c and label else underline
    if u >= 0:
        cfg.update(underline=u)
    else:  # no underlining
        c = ''
    cfg.update(label=label)
    return c, cfg


class _Tk_Button(ttk.Button):
    '''A C{_Tk_Button} with a label, inlieu of text.
    '''
    def __init__(self, frame, **kwds):
        cfg = self._cfg(**kwds)
        ttk.Button.__init__(self, frame, **cfg)

    def _cfg(self, label=None, **kwds):
        if label is None:
            cfg = kwds
        else:
            cfg = dict(text=label)
            cfg.update(kwds)
        return cfg

    def config(self, **kwds):
        cfg = self._cfg(**kwds)
        ttk.Button.config(self, **cfg)

    def disabled(self, *disable):
        '''Dis-/enable this button.
        '''
        # <https://TkDocs.com/tutorial/widgets.html>
        p = self.instate(_DISABLED)
        if disable:
            self.state(_DISABLED if disable[0] else _ENABLED)
        return bool(p)


class _Tk_Item(object):
    '''A re-configurable C{_Tk_Menu} item.
    '''
    def __init__(self, menu, label='', key='', under='', **kwds):
        '''New menu item.
        '''
        self.menu = menu
        self.item = menu.index(label)
        self.key  = key  # <...>

        self._cfg_d = dict(label=label, **kwds)
        self._dis_d = False
        self._under = under  # lower case

    def config(self, **kwds):
        '''Reconfigure this menu item.
        '''
        cfg = self._cfg_d.copy()
        cfg.update(kwds)
        if self._under:  # update underlining
            _, cfg = _underline2(self._under, **cfg)
        self.menu.entryconfig(self.item, **cfg)

    def disabled(self, *disable):
        '''Dis-/enable this menu item.
        '''
        # <https://TkDocs.com/tutorial/menus.html>
        p = self._dis_d
        if disable:
            self._dis_d = d = bool(disable[0])
            self.config(state=Tk.DISABLED if d else Tk.NORMAL)
        return p


class _Tk_Menu(Tk.Menu):
    '''C{Tk.Menu} extended with an C{.add_shortcut} method.

       Note, make C{Command-key} shortcuts on macOS work like
       C{Control-key} shotcuts on X-/Windows using a *single*
       character shortcut.

       Other modifiers like Shift- and Option- passed thru,
       unmodified.
    '''
    _shortcuts_entries = None  # {}, see .bind_shortcuts_to
    _shortcuts_widgets = ()

    def __init__(self, master=None, **kwds):
        # remove dashed line from X-/Windows tearoff menus
        # like idlelib.editor.EditorWindow.createmenubar
        # or use root.option_add('*tearOff', False)  Off?
        # as per <https://TkDocs.com/tutorial/menus.html>
        Tk.Menu.__init__(self, master, tearoff=False, **kwds)

    def add_item(self, label='', command=None, key='', **kwds):
        '''C{Tk.menu.add_command} extended with shortcut key
           accelerator, underline and binding and returning
           a C{_Tk_Item} instance instead of an C{item} index.

           If needed use modifiers like Shift- and Alt_ or Option-
           before the *single* shortcut key character.  Do NOT
           include the Command- or Control- modifier, instead use
           the platform-specific Cmd_, like Cmd_ + key.  Also,
           do NOT enclose the key in <...> brackets since those
           are handled here as needed for the shortcut binding.
        '''
        assert callable(command), 'command=%r' % (command,)
        return self._Item(Tk.Menu.add_command, key, label,
                                  command=command, **kwds)

    def add_menu(self, label='', menu=None, key='', **kwds):  # untested
        '''C{Tk.menu.add_cascade} extended with shortcut key
           accelerator, underline and binding and returning
           a C{_Tk_Item} instance instead of an C{item} index.
        '''
        assert isinstance(menu, _Tk_Menu), 'menu=%r' % (menu,)
        return self._Item(Tk.Menu.add_cascade, key, label,
                                  menu=menu, **kwds)

    def bind_shortcut(self, key='', command=None, label='', **unused):
        '''Bind shortcut key "<modifier-...-name>".
        '''
        # C{Accelerator} modifiers on macOS are Command-,
        # Ctrl-, Option- and Shift-, but for .bind[_all] use
        # <Command-..>, <Ctrl-..>, <Option_..> and <Shift-..>
        # with a shortcut key name or character (replaced
        # with its _KEY_SYMBOL if non-alphanumeric)
        # <https://www.Tcl.Tk/man/tcl8.6/TkCmd/bind.htm#M6>
        # <https://www.Tcl.Tk/man/tcl8.6/TkCmd/keysyms.html>
        if key and callable(command) and self._shortcuts_widgets:
            for w in self._shortcuts_widgets:
                w.bind(key, command)
            if label:  # remember the key in this menu
                item = self.index(label)
                self._shortcuts_entries[item] = key
        # The Tk modifier for macOS' Command key is called Meta
        # with Meta_L and Meta_R for the left and right keyboard
        # keys.  Similarly for macOS' Option key, the modifier
        # name Alt with Alt_L and Alt_R.  Previously, there were
        # only the Meta_L and Alt_L keys/modifiers.  See also
        # <https://StackOverflow.com/questions/6378556/multiple-
        # key-event-bindings-in-tkinter-control-e-command-apple-e-etc>

    def bind_shortcuts_to(self, *widgets):
        '''Set widget(s) to bind shortcut keys to, usually the
           root and/or Toplevel widgets.
        '''
        self._shortcuts_entries = {}
        self._shortcuts_widgets = widgets

    def entryconfig(self, idx, command=None, **kwds):  # PYCHOK signature
        '''Update a menu item and the shortcut key binding
           if the menu item command is being changed.

           Note, C{idx} is the item's index in the menu,
           see C{_Tk_Item} above.
        '''
        if command is None:  # XXX postcommand for sub-menu
            Tk.Menu.entryconfig(self, idx, **kwds)
        else:  # adjust the shortcut key binding also
            Tk.Menu.entryconfig(self, idx, command=command, **kwds)
            key = self._shortcuts_entries.get(idx, None)
            if key is not None:
                for w in self._shortcuts_widgets:
                    w.bind(key, command)

    def _Item(self, _add, key, label, **kwds):
        # Add and bind a menu item or sub~menu with an
        # optional accelerator key (not <..> enclosed)
        # or underline letter (preceded by underscore),
        # see <https://TkDocs.com/tutorial/menus.html>.
        cfg = dict(label=label)
        if key:  # Use '+' sign, like key = "Ctrl+Shift+X"
            if key.startswith('<') and key.endswith('>'):
                c = ''  # pass as-is, e.g. <<virtual event>>
            else:
                c = '+'  # split into modifiers and char
                if key.endswith(c):
                    m = key.rstrip(c).split(c)
                else:
                    m = key.split(c)
                    c = m.pop()
                # adjust accelerator key for specials like KP_1,
                # PageDown and PageUp (on macOS, see function
                # ParseAccelerator in <https://GitHub.com/tcltk/tk/
                # blob/main/macosx/tkMacOSXMenu.c> and definition
                # of specialAccelerators in <https://GitHub.com/
                # tcltk/tk/blob/main/macosx/tkMacOSXMenu.c>)
                a = _MAC_ACCEL.get(c, c) if _isMacOS else c
                if a.upper().startswith('KP_'):
                    a = a[3:]
                # accelerator strings are only used for display
                cfg.update(accelerator='+'.join(m + [a]))
                # replace key with Tk keysymb, allow F1 thru F35
                # (F19 on macOS) and because shortcut keys are
                # case-sensitive, use lower-case unless specified
                # as an upper-case letter with Shift+ modifier
                s = _KEY_SYMBOL.get(c, c)
                if len(s) == 1 and s.isupper() \
                               and 'Shift' not in m:
                    s = s.lower()
                # replace Ctrl modifier with Tk Control
                while 'Ctrl' in m:
                    m[m.index('Ctrl')] = 'Control'
                # <enclosed> for .bind_shortcut/.bind
                key = '<' + '-'.join(m + [s]) + '>'
                if _isMacOS or len(c) != 1 or not c.isalnum():
                    c = ''  # no underlining
                else:  # only Windows?
                    c, cfg = _underline2(c, **cfg)

        else:  # like idlelib, underline char after ...
            c, u = '', label.find('_')  # ... underscore
            if u >= 0:  # ... and remove underscore
                label = label[:u] + label[u+1:]
                cfg.update(label=label)
                if u < len(label) and not _isMacOS:
#                   c = label[u]
                    cfg.update(underline=u)

        if kwds:  # may still override accelerator ...
            cfg.update(kwds)  # ... and underline
        _add(self, **cfg)  # first _add then ...
        self.bind_shortcut(key, **cfg)  # ... bind
        return _Tk_Item(self, key=key, under=c, **cfg)


class _Tk_Slider(Tk.Scale):
    '''Scale with some add'l attributres
    '''
    _var = None

    def __init__(self, frame, to=1, **kwds):
        if isinstance(to, int):
            f, v = 0, Tk.IntVar()
        else:
            f, v = 0.0, Tk.DoubleVar()
        cfg = dict(from_=f, to=to,
                   orient=Tk.HORIZONTAL,
                   showvalue=0,
                   variable=v)
        cfg.update(kwds)
        Tk.Scale.__init__(self, frame, **cfg)
        self._var = v

    def set(self, value):
        # doesn't move the slider
        self._var.set(value)
        Tk.Scale.set(self, value)


class Player(Tk.Frame):
    '''The main window handling with events, etc.
    '''
    _anchored  =  True  # under the video panel
    _BUTTON_H  = _BANNER_H
    _debugs    =  0
    _isFull    = ''  # or geometry
    _length    =  0  # length time ticks
    _lengthstr = ''  # length h:m:s
    _muted     =  False
    _opacity   =  90 if _isMacOS else 100  # percent
    _opaque    =  False
    _rate      =  0.0
    _scaleX    =  1
    _scaleXstr = ''
    _sliding   =  False
    _snapshots =  0
    _stopped   =  None
    _title     = 'tkVLCplayer'
    _volume    =  50  # percent

    def __init__(self, parent, title='', video='', debug=False):  # PYCHOK called!
        Tk.Frame.__init__(self, parent)

        self.debug  = bool(debug)
        self.parent = parent  # == root
        self.video  = os.path.expanduser(video)
        if title:
            self._title = str(title)
        parent.title(title)
#       parent.iconname(title)

        # set up tickers to avoid None error
        def _pass():
            pass
        self._tick_1 = self.after(1, _pass)
        self._tick_2 = self.after(2, _pass)
        self._tick_3 = self.after(3, _pass)
        self._tick_4 = self.after(4, _pass)  # .after_idle

        # panels to play videos and hold buttons, sliders,
        # created *before* the File menu to be able to bind
        # the shortcuts keys to both windows/panels.
        self.videoPanel = v = self._VideoPanel()
        self._handleEvents(v)  # or parent
        self.buttonsPanel = b = self._ButtonsPanel()
        self._handleEvents(b)

        mb = _Tk_Menu(self.parent)  # menu bar
        parent.config(menu=mb)
#       self.menuBar = mb

        # macOS shortcuts <https://Support.Apple.com/en-us/HT201236>
        m = _Tk_Menu(mb)  # Video menu, shortcuts to both panels
        m.bind_shortcuts_to(v, b)
        m.add_item('Open...', self.OnOpen, key=Cmd_ + 'O')
        m.add_separator()
        self.playItem = m.add_item('Play', self.OnPlay, key=Cmd_ + 'P')  # Play/Pause
        m.add_item('Stop', self.OnStop, key=Cmd_ + '\b')  # BackSpace
        m.add_separator()
        self.muteItem = m.add_item('Mute', self.OnMute, key=Cmd_ + 'M')
        m.add_separator()
        m.add_item('Zoom In',  self.OnZoomIn,  key=Cmd_ + 'Shift++')
        m.add_item('Zoom Out', self.OnZoomOut, key=Cmd_ + '-')
        m.add_separator()
        m.add_item('Normal 1X', self.OnNormal, key=Cmd_ + '=')
        m.add_separator()
        m.add_item('Faster', self.OnFaster, key=Cmd_ + 'Shift+>')
        m.add_item('Slower', self.OnSlower, key=Cmd_ + 'Shift+<')
        m.add_separator()
        m.add_item('Snapshot', self.OnSnapshot, key=Cmd_ + 'T')
        m.add_separator()
        self.fullItem = m.add_item(_FULL_SCREEN, self.OnFull, key=Cmd_ + 'F')
        m.add_separator()
        m.add_item('Close', self.OnClose, key=Cmd_ + 'W')
        mb.add_cascade(label='Video', menu=m)
#       self.videoMenu = m

        m = _Tk_Menu(mb)  # Video menu, shortcuts to both panels
        m.bind_shortcuts_to(v, b)
        self.anchorItem = m.add_item(_UN_ANCHORED, self.OnAnchor, key=Cmd_ + 'A')
        m.add_separator()
        self.opaqueItem = m.add_item(_OPACITY % (self._opacity,), self.OnOpacity, key=Cmd_ + 'Y')
        m.add_item('Normal 100%', self.OnOpacity100)
        mb.add_cascade(label=_BUTTONS, menu=m)
#       self.buttonsMenu = m

        if _isMacOS and self.debug:  # Special macOS "windows" menu
            # <https://TkDocs.com/tutorial/menus.html> "Providing a Window Menu"
            # XXX Which (virtual) events are generated other than Configure?
            m = _Tk_Menu(mb, name='window')  # must be name='window'
            mb.add_cascade(menu=m, label='Windows')

        # VLC player
        args = ['--no-xlib'] if _isLinux else []
        self.Instance = vlc.Instance(args)
        self.player = self.Instance.media_player_new()

        b.update_idletasks()
        v.update_idletasks()
        if self.video:  # play video for a second, adjusting the panel
            self._play(self.video)
            self.after(1000, self.OnPause)
#       elif _isMacOS:  # <https://StackOverflow.com/questions/18394597/
#           # is-there-a-way-to-create-transparent-windows-with-tkinter>
#           self._stopped = True
#           self._set_opacity()
        self.OnTick()  # set up the timer

        # Keep the video panel at least as wide as the buttons panel
        # and move it down enough to put the buttons panel above it.
        self._BUTTON_H = d = b.winfo_height()
        b.minsize(width=_MIN_W, height=d)
        v.minsize(width=_MIN_W, height=0)
        _, w, h, _, y = _geometry5(v)
        y = int(y) + d + _BANNER_H
        _geometry(v, w, h, _TAB_X, y)
        self._anchorPanels()
        self._set_volume()

    def _anchorPanels(self, video=False):
        # Put the buttons panel under the video
        # or the video panel above the buttons
        if self._anchored and not self._isFull:
            self._debug(self._anchorPanels)
            v = self.videoPanel
            if _isMacOS and _fullscreen(v):
                # macOS green button full-screen?
                _fullscreen(v, False)
                self.OnFull()
            else:
                b = self.buttonsPanel
                v.update_idletasks()
                b.update_idletasks()
                h = v.winfo_height()
                d = h + _BANNER_H  # vertical delta
                if video:  # move/adjust video panel
                    w = b.winfo_width()  # same as ...
                    x = b.winfo_x()      # ... buttons
                    y = b.winfo_y() - d  # ... and above
                    g = v
                else:  # move/adjust buttons panel
                    h = b.winfo_height()  # unchanged
                    if h > self._BUTTON_H and _fullscreen(b):
                        # macOS green button full-screen?
                        _fullscreen(b, False)
                        h = self._BUTTON_H
                    w = v.winfo_width()  # unchanged
                    x = v.winfo_x()  # same as the video
                    y = v.winfo_y() + d  # below the video
                    g = b
#               _g = g._g
                _geometry(g, max(w, _MIN_W), h, x, y)
                if video:  # and g._g != _g:
                    self._set_aspect(True)

    def _ButtonsPanel(self):
        # create panel with buttons and sliders
        b = Tk.Toplevel(self.parent, name='buttons')
        t = '%s - %s' % (self._title, _BUTTONS)
        b.title(t)  # '' removes the banner
        b.resizable(True, False)

        f = ttk.Frame(b)
        # button are too small on Windows if width is given
        p = _Tk_Button(f, label='Play', command=self.OnPlay)
        #                 width=len('Pause'), underline=0
        s = _Tk_Button(f, label='Stop', command=self.OnStop)
        m = _Tk_Button(f, label='Mute', command=self.OnMute)
        #                 width=len('Unmute'), underline=0
        q = _Tk_Slider(f, command=self.OnPercent, to=100,
                          label=_VOLUME)  # length=170
        p.pack(side=Tk.LEFT, padx=8)
        s.pack(side=Tk.LEFT)
        m.pack(side=Tk.LEFT, padx=8)
        q.pack(fill=Tk.X,    padx=4, expand=1)
        f.pack(side=Tk.BOTTOM, fill=Tk.X)

        f = ttk.Frame(b)  # new frame?
        t = _Tk_Slider(f, command=self.OnTime, to=1000,  # millisecs
                          length=_MIN_W)  # label='Time'
        t.pack(side=Tk.BOTTOM, fill=Tk.X, expand=1)
        f.pack(side=Tk.BOTTOM, fill=Tk.X)

        # <https://www.PythonTutorial.net/tkinter/tkinter-window>
        # <https://TkDocs.com/tutorial/windows.html>
        # b.attributes('-topmost', 1)

        # self.videoPanel.update()  # needed to ...
# #     b.overrideredirect(True)  # ignore the panel
        b.update_idletasks()

        self.muteButton    = m
        self.playButton    = p
        self.timeSlider    = t
        self.percentSlider = q
        return b

    def _debug(self, where, *event, **kwds):
        # Print where an event is are handled.
        if self.debug:
            self._debugs += 1
            d = dict(anchored=self._anchored,
                       isFull=bool(self._isFull),
                      opacity=self._opacity,
                       opaque=self._opaque,
                      stopped=self._stopped,
                       volume=self._volume)
            p = self.player
            if p and p.get_media():
                d.update(playing=p.is_playing(),
                            rate=p.get_rate(),
                           scale=p.video_get_scale(),
                           scaleX=self._scaleX)
            try:  # final OnClose may throw TclError
                d.update(Buttons=_geometry1(self.buttonsPanel))
                d.update(  Video=_geometry1(self.videoPanel))
                if event:  # an event
                    event = event[0]
                    d.update(event=event)
                    w = str(event.widget)
#                   d.update(widget=type(event.widget))  # may fail
                    d.update(Widget={'.':        'Video',
                                     '.buttons': _BUTTONS}.get(w, w))
            except (AttributeError, TclError):
                pass
            d.update(kwds)
            d = ', '.join('%s=%s' % t for t in sorted(d.items()))
            print('%4s: %s %s' % (self._debugs, where.__name__, d))

    def _handleEvents(self, panel):
        # set up handlers for several events
        panel._g = ''  # holds most recent _geometry
        try:
            p  = panel
            p_ = p.protocol
        except AttributeError:
            p  = p.master  # == p.parent
            p_ = p.protocol
        if _isWindows:  # OK for macOS
            p_('WM_DELETE_WINDOW', self.OnClose)
#       Event Types <https://www.Tcl.Tk/man/tcl8.6/TkCmd/bind.html#M7>
        p.bind('<Configure>',  self.OnConfigure)  # window resize, position, etc.
        # needed on macOS to catch window close events
        p.bind('<Destroy>',    self.OnClose)      # window half-dead
#       p.bind('<Activate>',   self.OnActive)     # window activated
#       p.bind('<Deactivate>', self.OffActive)    # window deactivated
        p.bind('<FocusIn>',    self.OnFocus)      # getting keyboard focus
#       p.bind('<FocusOut>',   self.OffFocus)     # losing keyboard focus

    def OnAnchor(self, *unused):
        '''Toggle anchoring of the panels.
        '''
        self._debug(self.OnAnchor)
        self._anchored = not self._anchored
        if self._anchored:
            self._anchorPanels()
            a = _UN_ANCHORED
        else:  # move the buttons panel to the top-left
            b = self.buttonsPanel
            h = b.winfo_height()  # unchanged
            _geometry(b, _MIN_W, h, _TAB_X, _BANNER_H)
            a = _ANCHORED
        self.anchorItem.config(label=a)

    def OnClose(self, *event):
        '''Closes the window(s) and quit.
        '''
        self._debug(self.OnClose, *event)
        # print('_quit: bye')
        self.after_cancel(self._tick_1)
        self.after_cancel(self._tick_2)
        self.after_cancel(self._tick_3)
        self.after_cancel(self._tick_4)
        v = self.videoPanel
        v.update_idletasks()
        self.quit()  # stops .mainloop

    def OnConfigure(self, event):
        '''Some widget configuration changed.
        '''
        w, T = event.widget, event.type  # int
        if T == _T_CONFIGURE and w.winfo_toplevel() is w:
            # i.e. w is videoFrame/Panel or buttonsPanel
            if w is self.videoPanel:
                a = self._set_aspect  # force=True
            elif w is self.buttonsPanel and self._anchored:
                a = self._anchorPanels  # video=True
            else:
                a = None
            # prevent endless, recursive onConfigure events due to changing
            # the buttons- and videoPanel geometry, especially on Windows
            if a and w._g != _geometrystr(event.width, event.height, event.x, event.y):
                self.after_cancel(self._tick_1)
                self._debug(self.OnConfigure, event)
                self._tick_1 = self.after(250, a, True)

    def OnFaster(self, *unused):
        '''Speed the video up by 25%.
        '''
        self._set_rate(1.25)
        self._debug(self.OnFaster)

    def OnFocus(self, *unused):
        '''Got the keyboard focus.
        '''
        self._debug(self.OnFocus)
        self._set_aspect()
#       self._wiggle()

    def OnFull(self, *unused):
        '''Toggle full/off screen.
        '''
        self._debug(self.OnFull)
        # <https://www.Tcl.Tk/man/tcl8.6/TkCmd/wm.htm#M10>
        # self.after_cancel(self._tick_2)
        v = self.videoPanel
        if not _fullscreen(v):
            self._isFull = _geometry1(v)
            _fullscreen(v, True)  # or .wm_attributes
            v.bind('<Escape>', self.OnFull)
            f = _FULL_OFF
        else:
            _fullscreen(v, False)
            v.unbind('<Escape>')
            _geometry(v, self._isFull)
            self._isFull = ''
            self._anchorPanels()
            f = _FULL_SCREEN
        self.fullItem.config(label=f)

    def OnMute(self, *unused):
        '''Mute/Unmute audio.
        '''
        if self._stopped or self._opaque:
            return  # button.disabled
        self._debug(self.OnMute)
        # audio un/mute may be unreliable, see vlc.py docs.
        self._muted = m = not self._muted  # self.player.audio_get_mute()
        self.player.audio_set_mute(m)
        u = 'Unmute' if m else 'Mute'
        # i = u.index('m' if m else 'M')  # 2 if m else 0
        self.muteItem.config(label=u)
        self.muteButton.config(label=u)  # width=len(u), underline=i
        self.OnPercent()  # re-label the slider

    def OnNormal(self, *unused):
        '''Normal speed and 1X zoom.
        '''
        self._set_rate(0.0)
        self._set_zoom(0.0)
#       self._wiggle()
        _frontmost(self.buttonsPanel, True)
        _frontmost(self.videoPanel, True)
        self._set_aspect(True)
        self._debug(self.OnNormal)

    def OnOpacity(self, *unused):
        '''Use the percent slider to adjust the opacity.
        '''
        self.muteButton.disabled(True)  # greyed out?
        self.muteItem.disabled(True)  # greyed out?
        self._opaque = True
        self._set_opacity()
        self._debug(self.OnOpacity)

    def OnOpacity100(self, *unused):
        '''Set the opacity to 100%.
        '''
        _frontmost(self.videoPanel, True)
        _frontmost(self.buttonsPanel, True)
        self._set_opacity(100)
        self._debug(self.OnOpacity100)

    def OnOpen(self, *unused):
        '''Show the file dialog to choose a video, then play it.
        '''
        self._debug(self.OnOpen)
        self._reset()
        # XXX ... +[CATransaction synchronize] called within transaction
        v = askopenfilename(initialdir=os.path.expanduser('~'),
                            title='Choose a video',
                            filetypes=(('all files', '*.*'),
                                       ('mp4 files', '*.mp4'),
                                       ('mov files', '*.mov')))
        self._play(os.path.expanduser(v))
        self._set_aspect(True)

    def OnPause(self, *unused):
        '''Toggle between Pause and Play.
        '''
        self._debug(self.OnPause)
        p = self.player
        if p.get_media():
            self._pause_play(not p.is_playing())
#           self._wiggle()
            p.pause()  # toggles

    def OnPercent(self, *unused):
        '''Percent slider changed, adjust the opacity or volume.
        '''
        self._debug(self.OnPercent)
        s = max(0, min(100, self.percentSlider.get()))
        if self._opaque or self._stopped:
            self._set_opacity(s)
        else:
            self._set_volume(s)

    def OnPlay(self, *unused):
        '''Play video, if there's no video to play or
           playing, show a Tk.FileDialog to select one
        '''
        self._debug(self.OnPlay)
        p = self.player
        m = p.get_media()
        if not m:
            if self.video:
                self._play(self.video)
                self.video = ''
            else:
                self.OnOpen()
        elif p.play():  # == -1, play failed
            self._showError('play ' + repr(m))
        else:
            self._pause_play(True)
            if _isMacOS:
                self._wiggle()

    def OnSlower(self, *unused):
        '''Slow the video down by 20%.
        '''
        self._set_rate(0.80)
        self._debug(self.OnSlower)

    def OnSnapshot(self, *unused):
        '''Take a snapshot and save it (as .PNG only).
        '''
        p = self.player
        if p and p.get_media():
            self._snapshots += 1
            S = 'Snapshot%s' % (self._snapshots,)
            s = '%s-%s.PNG' % (self._title, S)  # PNG only
            if p.video_take_snapshot(0, s, 0, 0):
                self._showError('take ' + S)

    def OnStop(self, *unused):
        '''Stop the player, clear panel, etc.
        '''
        self._debug(self.OnStop)
        self._reset()

    def OnTick(self):
        '''Udate the time slider with the video time.
        '''
        p = self.player
        if p:
            s = self.timeSlider
            if self._length > 0:
                if not self._sliding:  # see .OnTime
                    t = max(0, p.get_time() // _TICK_MS)
                    if t != s.get():
                        s.set(t)
                        self._set_buttons(t)
            else:  # get video length in millisecs
                t = p.get_length()
                if t > 0:
                    self._length = t = max(1, t // _TICK_MS)
                    self._lengthstr = _hms(t, secs=' secs')
                    s.config(to=t)  # tickinterval=t / 5)
        # re-start the 1/4-second timer
        self._tick_2 = self.after(250, self.OnTick)

    def OnTime(self, *unused):
        '''Time slider has been moved by user.
        '''
        if self.player and self._length:
            self._sliding = True  # slider moving, see .OnTick
            self.after_cancel(self._tick_4)
            t = self.timeSlider.get()
            self._tick_4 = self.after_idle(self._set_time, t * _TICK_MS)
            self._set_buttons(t)
            self._debug(self.OnTime, tensecs=t)

    def OnZoomIn(self, *unused):
        '''Zoom in 25%.
        '''
        self._set_zoom(1.25)
        self._debug(self.OnZoomIn)

    def OnZoomOut(self, *unused):
        '''Zoom out 20%.
        '''
        self._set_zoom(0.80)
        self._debug(self.OnZoomOut)

    def _pause_play(self, playing):
        # re-label menu item and button, adjust callbacks
        p = 'Pause' if playing else 'Play'
        c = self.OnPlay if playing is None else self.OnPause  # PYCHOK attr
        self.playButton.config(label=p, command=c)
        self.playItem.config(label=p, command=c)
        self.muteButton.disabled(False)
        self.muteItem.disabled(False)
        self._stopped = self._opaque = False
        self._set_buttons(self.timeSlider.get())
        self._set_opacity()  # no re-label
        self._set_volume()
        self._set_aspect(True)

    def _play(self, video):
        # helper for OnOpen and OnPlay
        if os.path.isfile(video):  # Creation
            m = self.Instance.media_new(str(video))  # unicode
            p = self.player
            p.set_media(m)
            t = '%s - %s' % (self._title, os.path.basename(video))
            self.videoPanel.title(t)
#           self.buttonsPanel.title(t)

            # get the window handle for VLC to render the video
            h = self.videoCanvas.winfo_id()  # .winfo_visualid()?
            if _isWindows:
                p.set_hwnd(h)
            elif _isMacOS:
                # (1) the handle on macOS *must* be an NSView
                # (2) the video fills the entire panel, covering
                # all frames, buttons, sliders, etc. inside it
                ns = _GetNSView(h)
                if ns:
                    p.set_nsobject(ns)
                else:  # no libtk: no video, only audio
                    p.set_xwindow(h)
            else:  # *nix, Xwindows
                p.set_xwindow(h)  # fails on Windows
            self.OnPlay(None)

    def _reset(self):
        # stop playing, clear panel
        p = self.player
        if p:
            p.stop()
            self.timeSlider.set(0)
            self._pause_play(None)
            self._sliding = False
            self._stopped = True
            self.OnOpacity()

    def _set_aspect(self, force=False):
        # set the video panel aspect ratio and re-anchor
        p = self.player
        if p and not self._isFull:
            v = self.videoPanel
            g, w, h, x, y = _geometry5(v)
            if force or g != v._g:  # update
                self.after_cancel(self._tick_3)
                a, b = p.video_get_size(0)  # often (0, 0)
                if b > 0 and a > 0:
                    # adjust the video panel ...
                    if a > b:  # ... landscape height
                        h = round(float(w) * b / a)
                    else:  # ... or portrait width
                        w = round(float(h) * a / a)
                    _g = _geometry(v, w, h, x, y)
                    self._debug(self._set_aspect, a=a, b=b)
                    if self._anchored and (force or _g != g):
                        self._anchorPanels()
                # redo periodically since (1) player.video_get_size()
                # only returns non-zero width and height after playing
                # for a while and (2) avoid too frequent updates during
                # manual resizing of the video panel
                self._tick_3 = self.after(500, self._set_aspect)

    def _set_buttons(self, *tensecs):
        # set the buttons panel title
        s = self._length
        if s and tensecs:
            t =  tensecs[0]
            t = _hms(t) if t < s else self._lengthstr
            t = '%s - %s / %s%s' % (self._title, t, self._lengthstr, self._scaleXstr)
        else:  # reset panel title
            t = '%s - %s' % (self._title, _BUTTONS)
            self._length = 0
#           self._lengthstr = ''
        self.buttonsPanel.title(t)

    def _set_opacity(self, *percent):  # 100% fully opaque
        # set and re-label the opacity, panels and menu item
        if percent:
            self._opacity = p = percent[0]
        else:
            p = self._opacity
        a = max(0.2, min(1, p * 1e-2))
        self.videoPanel.attributes('-alpha', a if self._stopped else 1)
        self.buttonsPanel.attributes('-alpha', a)
#       if _isMacOS:  # <https://TkDocs.com/tutorial/windows.html>
#           self.buttonsPanel.attributes('-transparent', a)
        s = _OPACITY % (p,)
        self.opaqueItem.config(label=s)
        if self._opaque or self._stopped:
            self._set_percent(p, label=s)

    def _set_percent(self, percent, **cfg):
        # set and re-label the slider
        self.percentSlider.config(**cfg)
        self.percentSlider.set(percent)

    def _set_rate(self, factor):
        # change the video rate
        p = self.player
        if p:
            r = p.get_rate() * factor
            r = max(0.2, min(10.0, r)) if r > 0 else 1.0
            p.set_rate(r)
            self._rate = r

    def _set_time(self, millisecs):
        # set player to time
        p = self.player
        if p:
            p.set_time(millisecs)
        self._sliding = False  # see .OnTick

    def _set_volume(self, *volume):
        # set and re-label the volume
        if volume:
            self._volume = v = volume[0]
        else:
            v = self._volume
        m = ' (Muted)' if self._muted else ''
        V = '%s %s%%' % (_VOLUME, v)
        self._set_percent(v, label=V + m)
        p = self.player
        if p and p.is_playing() and not self._stopped:
            # .audio_set_volume returns 0 on success, -1 otherwise,
            # e.g. if the player is stopped or doesn't have media
            if p.audio_set_volume(v):  # and p.get_media():
                self._showError('set ' + V)

    def _set_zoom(self, factor):
        # zoom the video in/out, see cocoavlc.py
        p = self.player
        if p:
            x = self._scaleX * factor
            if x > 1:
                s = x
                t = ' - %.1fX' % (x,)
            else:
                x, s, t = 1, 0.0, ''
            p.video_set_scale(s)
#           self.videoPanel.update_idletasks()
            self._scaleX = x
            self._scaleXstr = t
            self._set_buttons(self.timeSlider.get())

    def _showError(self, verb):
        '''Display a simple error dialog.
        '''
        t = 'Unable to %s' % (verb,)
        showerror(self._title, t)
        # sys.exit(t)

    def _VideoPanel(self):
        # create panel to play video
        v = ttk.Frame(self.parent)
        c = Tk.Canvas(v)  # takefocus=True
        c.pack(fill=Tk.BOTH, expand=1)
        v.pack(fill=Tk.BOTH, expand=1)
        v.update_idletasks()

        self.videoCanvas = c
        self.videoFrame  = v
        # root is used for updates, NOT ...
        return self.parent  # ... the frame

    def _wiggle(self, d=4):
        # wiggle the video to fill the window on macOS
        if not self._isFull:
            v = self.videoPanel
            g, w, h, x, y = _geometry5(v)
            w = int(w) + d
            # x = int(x) - d
            # h = int(h) + d
            if _geometry(v, w, h, x, y) != g:
                self.after_idle(_geometry, v, g)
        if d > 1:  # repeat a few times
            self.after(100, self._wiggle, d - 1)


def print_version(name=''):  # imported by psgvlc.py
    # show all versions, this module, tkinter, libtk, vlc.py, libvlc, etc.

    # sample output on macOS:

    # % python3 ./tkvlc.py -v
    # tkvlc.py: 22.12.14
    # tkinter: 8.6
    # libTk: /Library/Frameworks/Python.framework/Versions/3.11/lib/libtk8.6.dylib
    # is_TK: aqua, isAquaTk, isCocoaTk
    # vlc.py: 3.0.12119 (Mon May 31 18:25:17 2021 3.0.12)
    # libVLC: 3.0.16 Vetinari (0x3001000)
    # plugins: /Applications/VLC.app/Contents/MacOS/plugins
    # Python: 3.11.0 (64bit) macOS 13.0.1 arm64

    # sample output on Windows:

    # PS C: python3 ./tkvlc.py -v
    # tkvlc.py: 22.12.14
    # tkinter: 8.6
    # libTk: N/A
    # is_TK: win32
    # vlc.py: 3.0.12119 (Mon May 31 18:25:17 2021 3.0.12)
    # libVLC: 3.0.18 Vetinari (0x3001200)
    # plugins: C:\Program Files\VideoLAN\VLC
    # Python: 3.11.0 (64bit) Windows 10

    try:  # private property
        t = Tk.Tk()._windowingsystem,
    except AttributeError:
        t = ()
    if _isMacOS:
        from idlelib import macosx
        m  = macosx.__dict__
        t += tuple(sorted(n for n, t in m.items() if n.startswith('is') and
                                                     n.endswith('Tk') and
                                                     callable(t) and t()))
    t = ', '.join(t) or 'n/a'

    n = os.path.basename(name or __file__)
    for t in ((n, __version__), (Tk.__name__, Tk.TkVersion), ('libTk', libtk), ('is_Tk', t)):
        print('%s: %s' % t)

    try:
        vlc.print_version()
        vlc.print_python()
    except AttributeError:
        try:
            os.system(sys.executable + ' -m vlc -v')
        except OSError:
            pass


if __name__ == '__main__':  # MCCABE 13

    _argv0 = sys.argv[0]
    _debug = False
    _video = ''

    while len(sys.argv) > 1:
        arg = sys.argv.pop(1)
        if arg.lower() in ('-v', '--version'):
            print_version()
            sys.exit(0)
        elif '-debug'.startswith(arg) and len(arg) > 2:
            _debug = True
        elif arg.startswith('-'):
            print('usage: %s  [-v | --version]  [-debug]  [<video_file_name>]' % (_argv0,))
            sys.exit(1)
        elif arg:  # video file
            _video = os.path.expanduser(arg)
            if not os.path.isfile(_video):
                print('%s error, no such file: %r' % (_argv0, arg))
                sys.exit(1)

    root = Tk.Tk()  # create a Tk.App()
    player = Player(root, video=_video, debug=_debug)
    if _isWindows:  # see function _test() at the bottom of ...
        # <https://GitHub.com/python/cpython/blob/3.11/Lib/tkinter/__init__.py>
        root.iconify()
        root.update()
        root.deiconify()
        root.mainloop()  # forever
        root.destroy()  # this is necessary on Windows to avoid ...
        # ... Fatal Python Error: PyEval_RestoreThread: NULL tstate
    else:
        root.mainloop()  # forever
