### Start of footer.py ###

class MediaEvent(ctypes.Structure):
    _fields_ = [
        ('media_name', ctypes.c_char_p),
        ('instance_name', ctypes.c_char_p),
        ]

class EventUnion(ctypes.Union):
    _fields_ = [
        ('meta_type', ctypes.c_uint),
        ('new_child', ctypes.c_uint),
        ('new_duration', ctypes.c_longlong),
        ('new_status', ctypes.c_int),
        ('media', ctypes.c_void_p),
        ('new_state', ctypes.c_uint),
        # Media instance
        ('new_position', ctypes.c_float),
        ('new_time', ctypes.c_longlong),
        ('new_title', ctypes.c_int),
        ('new_seekable', ctypes.c_longlong),
        ('new_pausable', ctypes.c_longlong),
        # FIXME: Skipped MediaList and MediaListView...
        ('filename', ctypes.c_char_p),
        ('new_length', ctypes.c_longlong),
        ('media_event', MediaEvent),
        ]

class Event(ctypes.Structure):
    _fields_ = [
        ('type', EventType),
        ('object', ctypes.c_void_p),
        ('u', EventUnion),
        ]

_EventManagers = {}

# FIXME: the EventManager global dict could be removed if
# _callback_handler was made a method of EventManager.
_called_from_ctypes = ctypes.CFUNCTYPE(None, ctypes.POINTER(Event), ctypes.c_void_p)
@_called_from_ctypes
def _callback_handler(event, key):
    '''(INTERNAL) handle callback call from ctypes.
    '''
    try: # retrieve Python callback and arguments
        call, args, kwds = _EventManagers[key]._callbacks_[event.contents.type.value]
        # FIXME: event could be dereferenced here to event.contents,
        # this would simplify the callback code.
        call(event, *args, **kwds)
    except KeyError:  # detached?
        pass

def callbackmethod(f):
    """Backward compatibility with the now useless @callbackmethod decorator.
    
    This method will be removed after a transition period.
    """
    return f

# Example callback, useful for debugging
def debug_callback(event, *args, **kwds):
    l = ["event %s" % (event.contents.type,)]
    if args:
       l.extend(map(str, args))
    if kwds:
       l.extend(sorted( "%s=%s" % t for t in kwds.iteritems() ))
    print "Debug callback (%s)" % ", ".join(l)

if __name__ == '__main__':
    try:
        from msvcrt import getch
    except ImportError:
        def getch():
            import tty
            import termios
            fd=sys.stdin.fileno()
            old_settings=termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                ch=sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch

    def end_callback(event):
        print "End of stream"
        sys.exit(0)

    echo_position = False
    def pos_callback(event, player):
        if echo_position:
            print "%s to %.2f%% (%.2f%%)" % (event.contents.type,
                   event.contents.u.new_position * 100,
                   player.get_position() * 100)

    if sys.argv[1:]:
        instance=Instance()
        media=instance.media_new(sys.argv[1])
        player=instance.media_player_new()
        player.set_media(media)
        player.play()

         # Some event manager examples.  Note, the callback can be any Python
         # callable and does not need to be decorated.  Optionally, specify
         # any number of positional and/or keyword arguments to be passed
         # to the callback (in addition to the first one, an Event instance).
        event_manager = player.event_manager()
        event_manager.event_attach(EventType.MediaPlayerEndReached, end_callback)
        event_manager.event_attach(EventType.MediaPlayerPositionChanged, pos_callback, player)

        def print_info():
            """Print information about the media."""
            media = player.get_media()
            print "State:", player.get_state()
            print "Media:", media.get_mrl()
            try:
                print "Current time:", player.get_time(), "/", media.get_duration()
                print "Position:", player.get_position()
                print "FPS:", player.get_fps()
                print "Rate:", player.get_rate()
                print "Video size: (%d, %d)" % (player.video_get_width(), player.video_get_height())
            except Exception:
                pass

        def forward():
            """Go forward 1s"""
            player.set_time(player.get_time() + 1000)

        def one_frame_forward():
            """Go forward one frame"""
            player.set_time(player.get_time() + long(1000 / (player.get_fps() or 25)))

        def one_frame_backward():
            """Go backward one frame"""
            player.set_time(player.get_time() - long(1000 / (player.get_fps() or 25)))

        def backward():
            """Go backward 1s"""
            player.set_time(player.get_time() - 1000)

        def print_help():
            """Print help
            """
            print "Commands:"
            for k, m in keybindings.iteritems():
                print "  %s: %s" % (k, (m.__doc__ or m.__name__).splitlines()[0])
            print " 1-9: go to the given fraction of the movie"

        def quit_app():
            """Exit."""
            sys.exit(0)

        def toggle_echo_position():
            """Toggle echoing of media position"""
            global echo_position
            echo_position = not echo_position

        keybindings={
            'f': player.toggle_fullscreen,
            ' ': player.pause,
            '+': forward,
            '-': backward,
            '.': one_frame_forward,
            ',': one_frame_backward,
            '?': print_help,
            'i': print_info,
            'p': toggle_echo_position,
            'q': quit_app,
            }

        print "Press q to quit, ? to get help."
        while True:
            k=getch()
            o=ord(k)
            method=keybindings.get(k, None)
            if method is not None:
                method()
            elif o >= 49 and o <= 57:
                # Numeric value. Jump to a fraction of the movie.
                v=0.1*(o-48)
                player.set_position(v)
    else:
        print "Syntax: %s movie_filename" % sys.argv[0]
        print "Once launched, type ? to get commands."



