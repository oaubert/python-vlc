### Start of footer.py ###

def callbackmethod(f):
    """Backward compatibility with the now useless @callbackmethod decorator.
    
    This method will be removed after a transition period.
    """
    return f

# Example callback, useful for debugging
def debug_callback(event, *args, **kwds):
    l = ["event %s" % (event.type,)]
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
        print "End of media stream (event %s)" % event.type
        sys.exit(0)

    echo_position = False
    def pos_callback(event, player):
        if echo_position:
            print "%s to %.2f%% (%.2f%%)\r" % (event.type,
                   event.u.new_position * 100,
                   player.get_position() * 100)

    def print_version():
        """Print libvlc version.
        """
        try:
            print "LibVLC version", libvlc_get_version()
        except:
            print "Error:", sys.exc_info()[1]

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
            try:
                print_version()
                media = player.get_media()
                print "State:", player.get_state()
                print "Media:", media.get_mrl()
                print "Track:", player.video_get_track(), "/", player.video_get_track_count()
                print "Current time:", player.get_time(), "/", media.get_duration()
                print "Position:", player.get_position()
                print "FPS:", player.get_fps()
                print "Rate:", player.get_rate()
                print "Video size: (%d, %d)" % player.video_get_size()
                print "Scale:", player.video_get_scale()
                print "Aspect ratio:", player.video_get_aspect_ratio()
            except Exception:
                print "Error:", sys.exc_info()[1]

        def forward():
            """Go forward 1s"""
            player.set_time(player.get_time() + 1000)

        def backward():
            """Go backward 1s"""
            player.set_time(player.get_time() - 1000)

        def one_frame_forward():
            """Go forward one frame"""
            player.set_time(player.get_time() + long(1000 / (player.get_fps() or 25)))

        def one_frame_backward():
            """Go backward one frame"""
            player.set_time(player.get_time() - long(1000 / (player.get_fps() or 25)))

        def print_help():
            """Print help
            """
            print "Single-character commands:"
            for k, m in keybindings.iteritems():
                print "  %s: %s" % (k, (m.__doc__ or m.__name__).splitlines()[0].rstrip("."))
            print " 1-9: go to the given fraction of the movie"

        def quit_app():
            """Exit."""
            sys.exit(0)

        def toggle_echo_position():
            """Toggle echoing of media position"""
            global echo_position
            echo_position = not echo_position

        keybindings={
            ' ': player.pause,
            '+': forward,
            '-': backward,
            '.': one_frame_forward,
            ',': one_frame_backward,
            '?': print_help,
            'f': player.toggle_fullscreen,
            'i': print_info,
            'p': toggle_echo_position,
            'q': quit_app,
            }

        print "Press q to quit, ? to get help."
        print
        while True:
            k = getch()
            print ">", k
            if k in keybindings:
                keybindings[k]()
            elif k.isdigit():
                # Numeric value. Jump to a fraction of the movie.
                player.set_position(float('0.'+k))
    else:
        print "Syntax: %s <movie_filename>" % sys.argv[0]
        print "Once launched, type ? to get help."
        print_version()




