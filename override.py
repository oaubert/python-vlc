class Instance:
    """Create a new Instance instance.

    It may take as parameter either:
      - a string
      - a list of strings as first parameters
      - the parameters given as the constructor parameters (must be strings)
    """
    def __new__(cls, *p):
        if p and p[0] == 0:
            return None
        elif p and isinstance(p[0], (int, long)):
            # instance creation from ctypes
            o=object.__new__(cls)
            o._as_parameter_=ctypes.c_void_p(p[0])
            return o
        elif len(p) == 1 and isinstance(p[0], basestring):
            # Only 1 string parameter: should be a parameter line
            p=p[0].split(' ')
        elif len(p) == 1 and isinstance(p[0], (tuple, list)):
            p=p[0]

        if not p and detected_plugin_path is not None:
            # No parameters passed. Under win32 and MacOS, specify
            # the detected_plugin_path if present.
            p=[ 'vlc', '--plugin-path='+ detected_plugin_path ]
        return libvlc_new(len(p), p)

    def media_player_new(self, uri=None):
        """Create a new Media Player object.

        @param uri: an optional URI to play in the player.
        """
        p=libvlc_media_player_new(self)
        if uri:
            p.set_media(self.media_new(uri))
        p._instance=self
        return p

    def media_list_player_new(self):
        """Create an empty Media Player object
        """
        p=libvlc_media_list_player_new(self)
        p._instance=self
        return p

    def media_new(self, mrl, *options):
        """Create an empty Media Player object

        Options can be specified as supplementary string parameters, e.g.
        m=i.media_new('foo.avi', 'sub-filter=marq{marquee=Hello}', 'vout-filter=invert')
        """
        m=libvlc_media_new_location(self, mrl)
        for o in options:
            libvlc_media_add_option(m, o)
        return m

class Media:
    def add_options(self, *list_of_options):
        """Add a list of options to the media.

        Options must be written without the double-dash, e.g.:
        m.add_options('sub-filter=marq@test{marquee=Hello}', 'video-filter=invert')

        Note that you also can directly pass these options in the Instance.media_new method:
        m=instance.media_new( 'foo.avi', 'sub-filter=marq@test{marquee=Hello}', 'video-filter=invert')
        """
        for o in list_of_options:
            self.add_option(o)

class MediaPlayer:
    """Create a new MediaPlayer instance.

    It may take as parameter either:
      - a string (media URI). In this case, a vlc.Instance will be created.
      - a vlc.Instance
    """
    def __new__(cls, *p):
        if p and p[0] == 0:
            return None
        elif p and isinstance(p[0], (int, long)):
            # instance creation from ctypes
            o=object.__new__(cls)
            o._as_parameter_=ctypes.c_void_p(p[0])
            return o

        if p and isinstance(p[0], Instance):
            return p[0].media_player_new()
        else:
            i=Instance()
            o=i.media_player_new()
            if p:
                o.set_media(i.media_new(p[0]))
            return o

    def get_instance(self):
        """Return the associated vlc.Instance.
        """
        return self._instance

class MediaListPlayer:
    """Create a new MediaPlayer instance.

    It may take as parameter either:
      - a vlc.Instance
      - nothing
    """
    def __new__(cls, *p):
        if p and p[0] == 0:
            return None
        elif p and isinstance(p[0], (int, long)):
            # instance creation from ctypes
            o=object.__new__(cls)
            o._as_parameter_=ctypes.c_void_p(p[0])
            return o
        elif len(p) == 1 and isinstance(p[0], (tuple, list)):
            p=p[0]

        if p and isinstance(p[0], Instance):
            return p[0].media_list_player_new()
        else:
            i=Instance()
            o=i.media_list_player_new()
            return o

    def get_instance(self):
        """Return the associated vlc.Instance.
        """
        return self._instance

class LogIterator:
    def __iter__(self):
        return self

    def next(self):
        if not self.has_next():
            raise StopIteration
        buf=LogMessage()
        ret=libvlc_log_iterator_next(self, buf)
        return ret.contents

class Log:
    def __iter__(self):
        return self.get_iterator()

    def dump(self):
        return [ str(m) for m in self ]
