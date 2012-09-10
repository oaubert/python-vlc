
# Start of footer.py #

# Backward compatibility
def callbackmethod(callback):
    """Now obsolete @callbackmethod decorator."""
    return callback

# libvlc_free is not present in some versions of libvlc. If it is not
# in the library, then emulate it by calling libc.free
if not hasattr(dll, 'libvlc_free'):
    # need to find the free function in the C runtime. This is
    # platform specific.
    # For Linux and MacOSX
    libc_path = find_library('c')
    if libc_path:
        libc = ctypes.CDLL(libc_path)
        libvlc_free = libc.free
    else:
        # On win32, it is impossible to guess the proper lib to call
        # (msvcrt, mingw...). Just ignore the call: it will memleak,
        # but not prevent to run the application.
        def libvlc_free(p):
            pass

    # ensure argtypes is right, because default type of int won't work
    # on 64-bit systems
    libvlc_free.argtypes = [ ctypes.c_void_p ]

# Version functions
def _dot2int(v):
    '''(INTERNAL) Convert 'i.i.i[.i]' str to int.
    '''
    t = [int(i) for i in v.split('.')]
    if len(t) == 3:
        t.append(0)
    elif len(t) != 4:
        raise ValueError('"i.i.i[.i]": %r' % (v,))
    if min(t) < 0 or max(t) > 255:
        raise ValueError('[0..255]: %r' % (v,))
    i = t.pop(0)
    while t:
        i = (i << 8) + t.pop(0)
    return i

def hex_version():
    """Return the version of these bindings in hex or 0 if unavailable.
    """
    try:
        return _dot2int(__version__.split('-')[-1])
    except (NameError, ValueError):
        return 0

def libvlc_hex_version():
    """Return the libvlc version in hex or 0 if unavailable.
    """
    try:
        return _dot2int(libvlc_get_version().split()[0])
    except ValueError:
        return 0


def debug_callback(event, *args, **kwds):
    '''Example callback, useful for debugging.
    '''
    l = ['event %s' % (event.type,)]
    if args:
        l.extend(map(str, args))
    if kwds:
        l.extend(sorted('%s=%s' % t for t in kwds.items()))
    print('Debug callback (%s)' % ', '.join(l))

if __name__ == '__main__':

    try:
        from msvcrt import getch
    except ImportError:
        import termios
        import tty

        def getch():  # getchar(), getc(stdin)  #PYCHOK flake
            fd = sys.stdin.fileno()
            old = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                ch = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old)
            return ch

    def end_callback(event):
        print('End of media stream (event %s)' % event.type)
        sys.exit(0)

    echo_position = False
    def pos_callback(event, player):
        if echo_position:
            sys.stdout.write('\r%s to %.2f%% (%.2f%%)' % (event.type,
                                                          event.u.new_position * 100,
                                                          player.get_position() * 100))
            sys.stdout.flush()

    def print_version():
        """Print libvlc version"""
        try:
            print('Build date: %s (%#x)' % (build_date, hex_version()))
            print('LibVLC version: %s (%#x)' % (libvlc_get_version(), libvlc_hex_version()))
            print('LibVLC compiler: %s' % libvlc_get_compiler())
            if plugin_path:
                print('Plugin path: %s' % plugin_path)
        except:
            print('Error: %s' % sys.exc_info()[1])

    if sys.argv[1:] and sys.argv[1] not in ('-h', '--help'):

        movie = os.path.expanduser(sys.argv[1])
        if not os.access(movie, os.R_OK):
            print('Error: %s file not readable' % movie)
            sys.exit(1)

        instance = Instance()
        try:
            media = instance.media_new(movie, 'sub-filter=marq')  # load marqee option
        except NameError:
            print('NameError: %s (%s vs LibVLC %s)' % (sys.exc_info()[1],
                                                       __version__,
                                                       libvlc_get_version()))
            sys.exit(1)
        player = instance.media_player_new()
        player.set_media(media)
        player.play()

        # Some marquee examples.  Marquee requires 'sub-filter=marq' in the
        # media_new() call above.  See also the Media.add_options method
        # and <http://www.videolan.org/doc/play-howto/en/ch04.html>
        player.video_set_marquee_int(VideoMarqueeOption.Enable, 1)
        player.video_set_marquee_int(VideoMarqueeOption.Size, 24)  # pixels
        player.video_set_marquee_int(VideoMarqueeOption.Position, Position.Bottom)
        if True:  # only one marquee can be specified
            player.video_set_marquee_int(VideoMarqueeOption.Timeout, 5000)  # millisec, 0==forever
            t = media.get_mrl()  # movie
        else:  # update marquee text periodically
            player.video_set_marquee_int(VideoMarqueeOption.Timeout, 0)  # millisec, 0==forever
            player.video_set_marquee_int(VideoMarqueeOption.Refresh, 1000)  # millisec (or sec?)
            ##t = '$L / $D or $P at $T'
            t = '%Y-%m-%d  %H:%M:%S'
        player.video_set_marquee_string(VideoMarqueeOption.Text, t)

        # Some event manager examples.  Note, the callback can be any Python
        # callable and does not need to be decorated.  Optionally, specify
        # any number of positional and/or keyword arguments to be passed
        # to the callback (in addition to the first one, an Event instance).
        event_manager = player.event_manager()
        event_manager.event_attach(EventType.MediaPlayerEndReached,      end_callback)
        event_manager.event_attach(EventType.MediaPlayerPositionChanged, pos_callback, player)

        def mspf():
            """Milliseconds per frame."""
            return int(1000 // (player.get_fps() or 25))

        def print_info():
            """Print information about the media"""
            try:
                print_version()
                media = player.get_media()
                print('State: %s' % player.get_state())
                print('Media: %s' % media.get_mrl())
                print('Track: %s/%s' % (player.video_get_track(), player.video_get_track_count()))
                print('Current time: %s/%s' % (player.get_time(), media.get_duration()))
                print('Position: %s' % player.get_position())
                print('FPS: %s (%d ms)' % (player.get_fps(), mspf()))
                print('Rate: %s' % player.get_rate())
                print('Video size: %s' % str(player.video_get_size(0)))  # num=0
                print('Scale: %s' % player.video_get_scale())
                print('Aspect ratio: %s' % player.video_get_aspect_ratio())
               #print('Window:' % player.get_hwnd()
            except Exception:
                print('Error: %s' % sys.exc_info()[1])

        def sec_forward():
            """Go forward one sec"""
            player.set_time(player.get_time() + 1000)

        def sec_backward():
            """Go backward one sec"""
            player.set_time(player.get_time() - 1000)

        def frame_forward():
            """Go forward one frame"""
            player.set_time(player.get_time() + mspf())

        def frame_backward():
            """Go backward one frame"""
            player.set_time(player.get_time() - mspf())

        def print_help():
            """Print help"""
            print('Single-character commands:')
            for k, m in sorted(keybindings.items()):
                m = (m.__doc__ or m.__name__).splitlines()[0]
                print('  %s: %s.' % (k, m.rstrip('.')))
            print('0-9: go to that fraction of the movie')

        def quit_app():
            """Stop and exit"""
            sys.exit(0)

        def toggle_echo_position():
            """Toggle echoing of media position"""
            global echo_position
            echo_position = not echo_position

        keybindings = {
            ' ': player.pause,
            '+': sec_forward,
            '-': sec_backward,
            '.': frame_forward,
            ',': frame_backward,
            'f': player.toggle_fullscreen,
            'i': print_info,
            'p': toggle_echo_position,
            'q': quit_app,
            '?': print_help,
            }

        print('Press q to quit, ? to get help.%s' % os.linesep)
        while True:
            k = getch()
            print('> %s' % k)
            if k in keybindings:
                keybindings[k]()
            elif k.isdigit():
                 # jump to fraction of the movie.
                player.set_position(float('0.'+k))

    else:
        print('Usage: %s <movie_filename>' % sys.argv[0])
        print('Once launched, type ? for help.')
        print('')
        print_version()
