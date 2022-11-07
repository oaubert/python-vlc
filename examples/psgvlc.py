#! /usr/bin/env python3
# -*- coding: utf-8 -*-

u'''Bare Bones VLC Media Player Demo with Playlist.

1 - Originally the  Demo_Media_Player_VLC_Based.py  duplicated from
    <https://GitHub.com/PySimpleGUI/PySimpleGUI/blob/master/DemoPrograms>
    and modified to work and showing videos on recent macOS versions.

2 - This script uses PySimpleGUI under its LGPL3+ stipulations.

3 - You will need to install the Python bindings for VLC, for example
    using pip:  python3 -m pip install python-vlc

4 - You need the VLC player itself from <https://www.VideoLan.org>.

5 - On macOS, you also need to get tkvlc.py from this location
    <https://GitHub.com/oaubert/python-vlc/tree/master/examples>
    to get video and audio.

6 - On macOS, the video plays full-frame, overwriting the buttons.

7 - Original <https://GitHub.com/israel-dryer/Media-Player> by Israel
    Dryer, modified to be a PySimpleGUI Demo Program and a python-vlc
    example for you to customize.  Uses the VLC player to playback
    local media files (and YouTube streams).
'''
import sys
if sys.version_info[0] < 3:  # Python 3.4+ only
    sys.exit('%s requires Python 3.4 or later' % (sys.argv[0],))
    # import Tkinter as tk
import PySimpleGUI as sg
import vlc

__all__ = ('libtk',)
__version__ = '22.11.07'  # mrJean1 at Gmail

_Load_  = 'Load'
_Next_  = 'Next'
_Path_  = 'Media URL or local path:'
_Pause_ = 'Pause'
_Play_  = 'Play'
_Prev_  = 'Previous'
_Stop_  = 'Stop'

# GUI definition & setup
sg.theme('DarkBlue')

def Bn(name):  # a PySimpleGUI "User Defined Element" (see docs)
    return sg.Button(name, size=(8, 1), pad=(1, 1))

layout = [[sg.Input(default_text=_Path_, size=(40, 1), key='-VIDEO_PATH-'), sg.Button(_Load_)],
          [sg.Frame('', [], size=(300, 170), key='-VID_OUT-')],  # was [sg.Image('', ...)],
          [Bn(_Prev_), Bn(_Play_), Bn(_Next_), Bn(_Pause_), Bn(_Stop_)],
          [sg.Text('Load media to start', key='-MESSAGE_AREA-')]]

window = sg.Window('PySimpleGUI VLC Player', layout, element_justification='center', finalize=True, resizable=True)

window['-VID_OUT-'].expand(True, True)  # type: sg.Element

# Media Player Setup
inst = vlc.Instance()
list_player = inst.media_list_player_new()
media_list = inst.media_list_new([])
list_player.set_media_list(media_list)
player = list_player.get_media_player()
# tell VLC where to render the video(s)
tk_id = window['-VID_OUT-'].Widget.winfo_id()
libtk = ''
if sg.running_linux():
    player.set_xwindow(tk_id)
elif sg.running_windows():
    player.set_hwnd(tk_id)
elif sg.running_mac():
    try:
        from tkvlc import _GetNSView, libtk
        ns = _GetNSView(tk_id)
    except ImportError:
        ns = None
        libtk = 'none, install tkvlc.py from <https://GitHub.com/oaubert/python-vlc> examples'
    if ns:  # drawable NSview
        player.set_nsobject(ns)
    else:  # no video, only audio
        player.set_xwindow(tk_id)
else:  # running trinket, etc.
    player.set_hwnd(tk_id)  # TBD

if __name__ == '__main__':  # MCCABE 20

    if len(sys.argv) > 1:
        if sys.argv[1].lower() in ('-v', '--version'):
            # show all versions, this vlc.py, libvlc, etc. (sample output on macOS):
            # ...
            # % python3 ./psgvlc.py -v
            # psgvlc.py: 22.11.06
            # tkinter: 8.6
            # libTk: /Library/Frameworks/Python.framework/Versions/3.11/lib/libtk8.6.dylib
            # vlc.py: 3.0.12119 (Mon May 31 18:25:17 2021 3.0.12)
            # libVLC: 3.0.16 Vetinari (0x3001000)
            # plugins: /Applications/VLC.app/Contents/MacOS/plugins
            # Python: 3.11.0 (64bit) macOS 13.0 arm64
            for t in ((sys.argv[0], __version__), (sg.tk.__name__, sg.tk.TkVersion), ('libTk', libtk)):
                print('{}: {}'.format(*t))
            try:
                vlc.print_version()
                vlc.print_python()
            except AttributeError:
                pass
            sys.exit(0)

        if sys.argv[1]:
            media_list.add_media(sys.argv[1])
            list_player.set_media_list(media_list)

    # The Event Loop
    while True:
        # run with a timeout so that current location can be updated
        event, values = window.read(timeout=1000)

        if event == sg.WIN_CLOSED:
            break

        if event == _Pause_:
            list_player.pause()
        elif event == _Stop_:
            list_player.stop()
        elif event == _Next_:
            list_player.next()
            list_player.play()
        elif event == _Prev_:
            list_player.previous()  # first call causes current video to start over
            list_player.previous()  # second call moves back 1 video from current
            list_player.play()
        elif event == _Play_:
            list_player.play()
        elif event == _Load_:
            path = values['-VIDEO_PATH-']
            if path and _Path_ not in path:
                media_list.add_media(path)
                list_player.set_media_list(media_list)
                window['-VIDEO_PATH-'].update(_Path_)  # only add a legit submit

        # update elapsed time if a video loaded and playing
        if player.is_playing():
            text = '{:02d}:{:02d}'.format(*divmod(player.get_time()   // 1000, 60)) + ' / ' + \
                   '{:02d}:{:02d}'.format(*divmod(player.get_length() // 1000, 60))
            if sg.running_mac():
                print('{}: {}'.format(sys.argv[0], text))

        elif not media_list.count():
            text = 'Load media to start'
        else:
            text = 'Ready to play media'
        window['-MESSAGE_AREA-'].update(text)

    window.close()
