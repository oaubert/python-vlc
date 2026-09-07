"""
A simple example for VLC python bindings using the plain Windows API.

Author: https://github.com/59de44955ebd, Berlin
Date: 25.08.2026
"""
from ctypes import *
from ctypes.wintypes import *
import sys

import vlc

########################################
# Additional used Windows API types
########################################
_is_64_bit = sys.maxsize > 2**32
LONG_PTR = c_longlong if _is_64_bit else c_long
UINT_PTR = WPARAM
WNDPROC = WINFUNCTYPE(LONG_PTR, HWND, UINT, WPARAM, LPARAM)

########################################
# Used Windows API structs
########################################
class MINMAXINFO(Structure):
    _fields_ = [
        ("ptReserved", POINT),
        ("ptMaxSize", POINT),
        ("ptMaxPosition", POINT),
        ("ptMinTrackSize", POINT),
        ("ptMaxTrackSize", POINT),
    ]

class OPENFILENAMEW(Structure):
    def __init__(self, *args, **kwargs):
        super(OPENFILENAMEW, self).__init__(*args, **kwargs)
        self.lStructSize = sizeof(OPENFILENAMEW)
    _fields_ = (
        ("lStructSize", DWORD),
        ("hwndOwner", HWND),
        ("hInstance", HINSTANCE),
        ("lpstrFilter", LPWSTR),
        ("lpstrCustomFilter", LPWSTR),
        ("nMaxCustFilter", DWORD),
        ("nFilterIndex", DWORD),
        ("lpstrFile", LPWSTR),
        ("nMaxFile", DWORD),
        ("lpstrFileTitle", LPWSTR),
        ("nMaxFileTitle", DWORD),
        ("lpstrInitialDir", LPCWSTR),
        ("lpstrTitle", LPCWSTR),
        ("Flags", DWORD),
        ("nFileOffset", WORD),
        ("nFileExtension", WORD),
        ("lpstrDefExt", LPCWSTR),
        ("lCustData", LPARAM),
        ("lpfnHook", LPVOID),  # LPOFNHOOKPROC, not used
        ("lpTemplateName", LPCWSTR),
        ("pvReserved", LPVOID),
        ("dwReserved", DWORD),
        ("FlagsEx", DWORD),
    )

class WNDCLASSEXW(Structure):
    def __init__(self, *args, **kwargs):
        super(WNDCLASSEXW, self).__init__(*args, **kwargs)
        self.cbSize = sizeof(self)
    _fields_ = [
        ("cbSize", UINT),
        ("style", UINT),
        ("lpfnWndProc", WNDPROC),
        ("cbClsExtra", INT),
        ("cbWndExtra", INT),
        ("hInstance", HANDLE),
        ("hIcon", HANDLE),
        ("hCursor", HANDLE),
        ("hbrBackground", HANDLE),
        ("lpszMenuName", LPCWSTR),
        ("lpszClassName", LPCWSTR),
        ("hIconSm", HANDLE)
    ]

########################################
# Used Windows API functions
########################################
comdlg32 = windll.comdlg32
comdlg32.GetOpenFileNameW.argtypes = (POINTER(OPENFILENAMEW),)

gdi32 = windll.gdi32
gdi32.CreateFontW.argtypes = (INT, INT, INT, INT, INT, DWORD, DWORD, DWORD, DWORD, DWORD, DWORD, DWORD, DWORD, LPCWSTR)
gdi32.CreateFontW.restype = HFONT
gdi32.CreateSolidBrush.argtypes = (COLORREF,)
gdi32.CreateSolidBrush.restype = HBRUSH

user32 = windll.user32
user32.AppendMenuW.argtypes = (HWND, UINT, UINT_PTR, LPCWSTR)
user32.CreateWindowExW.argtypes = (DWORD, LPCWSTR, LPCWSTR, DWORD, INT, INT, INT, INT, HWND, HMENU, HINSTANCE, LPVOID)
user32.DefWindowProcW.argtypes = (HWND, UINT, WPARAM, LPARAM)
user32.DispatchMessageW.argtypes = (LPMSG,)
user32.EnableWindow.argytpes = (HWND, BOOL)
user32.GetMessageW.argtypes = (LPMSG, HWND, UINT, UINT)
user32.GetWindowRect.argtypes = (HWND, LPRECT)
user32.InvalidateRect.argtypes = (HWND, LPRECT, BOOL)
user32.IsDialogMessageW.argtypes = (HWND, LPMSG)
user32.IsDialogMessageW.restype = BOOL
user32.SendMessageW.argtypes = (HWND, UINT, LPVOID, LPVOID)
user32.SetWindowPos.argtypes = (HWND, LONG_PTR, INT, INT, INT, INT, UINT)
user32.TranslateMessage.argtypes = (LPMSG,)

########################################
# Used Windows API constants
########################################
ANSI_CHARSET = 0
BN_CLICKED = 0
CLIP_DEFAULT_PRECIS = 0
COLOR_3DFACE = 15
CS_HREDRAW = 2
CS_VREDRAW = 1
CW_USEDEFAULT = -2147483648
DEFAULT_PITCH = 0
DEFAULT_QUALITY = 0
FF_DONTCARE = 0
FW_DONTCARE = 0
IDC_ARROW = 32512
MAX_PATH = 260
MF_POPUP = 16
MF_STRING = 0
OFN_ENABLESIZING = 8388608
OFN_PATHMUSTEXIST = 2048
OUT_TT_PRECIS = 4
SWP_NOMOVE = 2
SWP_NOSIZE = 1
SW_SHOWNORMAL = 1
TBM_SETPAGESIZE = 1045
TBM_SETPOS = 1029
TBM_SETRANGE = 1030
TBM_SETRANGEMAX = 1032
TB_ENDTRACK = 8
TB_PAGEDOWN = 3
TB_PAGEUP = 2
WC_BUTTON = "Button"
WC_TRACKBAR = "msctls_trackbar32"
WM_CLOSE = 16
WM_COMMAND = 273
WM_GETMINMAXINFO = 36
WM_HSCROLL = 276
WM_SETFONT = 48
WM_SIZE = 5
WM_TIMER = 275
WS_CHILD = 1073741824
WS_DISABLED = 134217728
WS_OVERLAPPEDWINDOW = 13565952
WS_VISIBLE = 268435456


class Player():
    """A simple Media Player using VLC and Windows API"""

    def __init__(self, master=None):

        # Create a "menubar"
        self.h_menu = user32.CreateMenu()
        hmenu_child = user32.CreateMenu()
        user32.AppendMenuW(self.h_menu, MF_POPUP, hmenu_child, "&File")
        user32.AppendMenuW(hmenu_child, MF_STRING, 1, "Load Video")
        user32.AppendMenuW(hmenu_child, MF_STRING, 2, "Close App")

        # Create the main application window

        def _window_proc_callback(hwnd, msg, wparam, lparam):

            if msg == WM_CLOSE:
                self.quit()

            elif msg == WM_TIMER:
                self.update_ui()

            elif msg == WM_SIZE:
                width, height = lparam & 0xFFFF, (lparam >> 16) & 0xFFFF
                user32.SetWindowPos(self.hwnd_video_frame, 0, 0, 0, width, height - 70, SWP_NOMOVE)
                user32.SetWindowPos(self.hwnd_button_play, 0, 10, height - 33, 0, 0, SWP_NOSIZE)
                user32.SetWindowPos(self.hwnd_button_stop, 0, 100, height - 33, 0, 0, SWP_NOSIZE)
                user32.SetWindowPos(self.hwnd_trackbar_position, 0, 7, height - 60, width - 14, 23, 0)
                user32.SetWindowPos(self.hwnd_trackbar_volume, 0, width - 107, height - 33, 0, 0, SWP_NOSIZE)

                # Our main window's class has no CS_HREDRAW/CS_VREDRAW class styles,
                # because those would VLC make flicker when the window is resized.
                # Therefor we have to invalidate the non-VLC part of the UI (bottom rect)
                # manually to avoid visual artefacts.
                user32.InvalidateRect(hwnd, byref(RECT(0, height - 70, width, height)), 1)

            elif msg == WM_GETMINMAXINFO:
                mmi = cast(lparam, POINTER(MINMAXINFO)).contents
                mmi.ptMinTrackSize = POINT(320, 128)
                return 0

            elif msg == WM_HSCROLL:
                if lparam == self.hwnd_trackbar_position:
                    lo, hi, = wparam & 0xFFFF, (wparam >> 16) & 0xFFFF
                    if lo == TB_ENDTRACK:
                        return 0
                    if lo in (TB_PAGEDOWN, TB_PAGEUP):  # Click into slider
                        pt = POINT()
                        user32.GetCursorPos(byref(pt))
                        user32.MapWindowPoints(None, self.hwnd_trackbar_position, byref(pt), 1)
                        rc = RECT()
                        user32.GetWindowRect(self.hwnd_trackbar_position, byref(rc))
                        hi = int((pt.x - 10) / (rc.right - rc.left - 20) * 2000)
                        user32.SendMessageW(self.hwnd_trackbar_position, TBM_SETPOS, 1, hi)
                    self.set_position(hi)

                elif lparam == self.hwnd_trackbar_volume:
                    lo, hi, = wparam & 0xFFFF, (wparam >> 16) & 0xFFFF
                    if lo == TB_ENDTRACK:
                        return 0
                    if lo in (TB_PAGEDOWN, TB_PAGEUP):  # Click into slider
                        pt = POINT()
                        user32.GetCursorPos(byref(pt))
                        user32.MapWindowPoints(None, self.hwnd_trackbar_volume, byref(pt), 1)
                        rc = RECT()
                        user32.GetWindowRect(self.hwnd_trackbar_volume, byref(rc))
                        hi = int((pt.x - 10) / (rc.right - rc.left - 20) * 100)
                        user32.SendMessageW(self.hwnd_trackbar_volume, TBM_SETPOS, 1, hi)
                    self.set_volume(hi)

            elif msg == WM_COMMAND:
                command_id = WORD(wparam & 0xFFFF).value  # LOWORD(wparam)
                if lparam == 0:
                    if command_id == 1:
                        self.open_file()
                    elif command_id == 2:
                        self.quit()
                elif lparam == self.hwnd_button_play:
                    if command_id == BN_CLICKED:
                        self.play_pause()
                elif lparam == self.hwnd_button_stop:
                    if command_id == BN_CLICKED:
                        self.stop()

            return user32.DefWindowProcW(hwnd, msg, wparam, lparam)

        self.windowproc = WNDPROC(_window_proc_callback)

        newclass = WNDCLASSEXW()
        newclass.lpfnWndProc = self.windowproc
        newclass.lpszClassName = "MediaPlayer"
        newclass.hbrBackground = COLOR_3DFACE + 1
        newclass.hCursor = user32.LoadCursorW(None, IDC_ARROW)
        user32.RegisterClassExW(byref(newclass))

        hwnd_desktop = user32.GetDesktopWindow()
        rc = RECT()
        user32.GetClientRect(hwnd_desktop, byref(rc))
        cx, cy = 640, 480
        x, y = (rc.right - cx) // 2, (rc.bottom - cy) // 2

        self.hwnd = user32.CreateWindowExW(
            0,
            newclass.lpszClassName,
            "Media Player",
            WS_OVERLAPPEDWINDOW,
            x, y, cx, cy,
            0,
            self.h_menu,
            None, 0
        )

        # Create a basic vlc instance
        self.instance = vlc.Instance(["--quiet", "--no-osd"])

        self.media = None

        # Create an empty vlc media player
        self.mediaplayer = self.instance.media_player_new()

        self.create_ui()

        self.is_paused = False

        # The media player has to be "connected" to our VideoFrame
        self.mediaplayer.set_hwnd(self.hwnd_video_frame)

        user32.ShowWindow(self.hwnd, SW_SHOWNORMAL)

    def run(self):
        msg = MSG()
        while user32.GetMessageW(byref(msg), None, 0, 0):
            if user32.IsDialogMessage(self.hwnd, byref(msg)):
                continue
            user32.TranslateMessage(byref(msg))
            user32.DispatchMessageW(byref(msg))
        return 0

    def quit(self):
        user32.PostQuitMessage(0)

    def timer_start(self):
        user32.SetTimer(self.hwnd, 1, 100, 0)  # 1 is our timer id

    def timer_stop(self):
        user32.KillTimer(self.hwnd, 1)

    def create_ui(self):
        """Set up the user interface"""
        self.dummy_proc = WNDPROC(user32.DefWindowProcW)
        newclass = WNDCLASSEXW()
        newclass.lpfnWndProc = self.dummy_proc
        newclass.lpszClassName = "VideoFrame"
        newclass.hbrBackground = gdi32.CreateSolidBrush(0x000000)
        newclass.hCursor = user32.LoadCursorW(None, IDC_ARROW)
        user32.RegisterClassExW(byref(newclass))

        self.hwnd_video_frame = user32.CreateWindowExW(
            0,
            newclass.lpszClassName,
            "VideoFrame",
            WS_CHILD | WS_VISIBLE,
            0, 0, 0, 0,
            self.hwnd,
            None, None, 0
        )

        h_font_shell = gdi32.CreateFontW(
            -11, 0, 0, 0, FW_DONTCARE, 0, 0, 0, ANSI_CHARSET, OUT_TT_PRECIS,
            CLIP_DEFAULT_PRECIS, DEFAULT_QUALITY, DEFAULT_PITCH | FF_DONTCARE, "Segoe UI"
        )

        self.hwnd_button_play = user32.CreateWindowExW(
            0,
            WC_BUTTON,
            "Play",
            WS_CHILD | WS_VISIBLE,
            0, 0, 80, 23,
            self.hwnd,
            None, None, 0
        )
        user32.SendMessageW(self.hwnd_button_play, WM_SETFONT, h_font_shell, 1)

        self.hwnd_button_stop = user32.CreateWindowExW(
            0,
            WC_BUTTON,
            "Stop",
            WS_CHILD | WS_VISIBLE,
            0, 0, 80, 23,
            self.hwnd,
            None, None, 0
        )
        user32.SendMessageW(self.hwnd_button_stop, WM_SETFONT, h_font_shell, 1)

        self.hwnd_trackbar_position = user32.CreateWindowExW(
            0,
            WC_TRACKBAR,
            "",
            WS_CHILD | WS_VISIBLE | WS_DISABLED,
            0, 0, 0, 0,
            self.hwnd,
            None, None, 0
        )
        user32.SendMessageW(self.hwnd_trackbar_position, TBM_SETRANGEMAX, 0, 2000)
        user32.SendMessageW(self.hwnd_trackbar_position, TBM_SETPAGESIZE, 0, 1)

        self.hwnd_trackbar_volume = user32.CreateWindowExW(
            0,
            WC_TRACKBAR,
            "",
            WS_CHILD | WS_VISIBLE,
            0, 0, 100, 23,
            self.hwnd,
            None, None, 0
        )
        user32.SendMessageW(self.hwnd_trackbar_volume, TBM_SETRANGEMAX, 0, 100)
        user32.SendMessageW(self.hwnd_trackbar_volume, TBM_SETPAGESIZE, 0, 1)
        user32.SendMessageW(self.hwnd_trackbar_volume, TBM_SETPOS, 1, self.mediaplayer.audio_get_volume())

    def play_pause(self):
        """Toggle play/pause status"""
        if self.mediaplayer.is_playing():
            self.mediaplayer.pause()
            user32.SetWindowTextW(self.hwnd_button_play, "Play")
            self.is_paused = True
            self.timer_stop()
        else:
            if self.mediaplayer.play() == -1:
                self.open_file()
                return

            self.mediaplayer.play()
            user32.SetWindowTextW(self.hwnd_button_play, "Pause")
            self.is_paused = False
            self.timer_start()
        user32.EnableWindow(self.hwnd_trackbar_position, 1)

    def stop(self):
        """Stop player"""
        self.mediaplayer.stop()
        user32.SetWindowTextW(self.hwnd_button_play, "Play")
        user32.EnableWindow(self.hwnd_trackbar_position, 0)

    def open_file(self):
        """Open a media file in a MediaPlayer"""
        file_buffer = create_unicode_buffer(MAX_PATH)
        ofn = OPENFILENAMEW()
        ofn.hwndOwner = self.hwnd
        ofn.lpstrTitle = "Choose Media File"
        ofn.lpstrFile = cast(file_buffer, LPWSTR)
        ofn.nMaxFile = MAX_PATH
        ofn.Flags = OFN_ENABLESIZING | OFN_PATHMUSTEXIST
        if not comdlg32.GetOpenFileNameW(byref(ofn)):
            return

        filename = file_buffer[:].split("\0", 1)[0]
        self.media = self.instance.media_new(filename)

        # Put the media in the media player
        self.mediaplayer.set_media(self.media)

        # Parse the metadata of the file
        self.media.parse()

        # Set the title of the track as window title
        user32.SetWindowTextW(self.hwnd, self.media.get_meta(0))

        self.play_pause()

    def set_volume(self, volume):
        """Set the volume"""
        self.mediaplayer.audio_set_volume(volume)

    def set_position(self, pos):
        """Set the movie position according to the position slider"""
        # Set the media position to where the slider was dragged
        self.timer_stop()
        self.mediaplayer.set_position(pos / 2000.0)
        self.timer_start()

    def update_ui(self):
        """Update the user interface"""
        # Set the slider"s position to its corresponding media position
        media_pos = int(self.mediaplayer.get_position() * 2000)
        user32.SendMessageW(self.hwnd_trackbar_position, TBM_SETPOS, 1, media_pos)

        # No need for a timer if nothing is played
        if not self.mediaplayer.is_playing():
            self.timer_stop()

            # After the video finished, the play button stills shows "Pause",
            # which is not the desired behavior of a media player.
            # This fixes that "bug".
            if not self.is_paused:
                self.stop()


def main():
    """Entry point for our simple vlc player"""
    player = Player()
    sys.exit(player.run())

if __name__ == "__main__":
    main()
