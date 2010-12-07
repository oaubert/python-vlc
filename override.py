
class Instance:
    """Create a new Instance instance.

    It may take as parameter either:
      - a string
      - a list of strings as first parameters
      - the parameters given as the constructor parameters (must be strings)
    """
    def __new__(cls, *args):
        if args:
            i = args[0]
            if i == 0:
                return None
            if isinstance(i, _Ints):
                return _Cobject(cls, ctypes.c_void_p(i))
            if len(args) == 1:
                if isinstance(i, basestring):
                    args = i.strip().split()
                elif isinstance(i, _Seqs):
                    args = i
                else:
                    raise VLCException('Instance %r' % (args,))

        if not args and plugin_path is not None:
             # no parameters passed, for win32 and MacOS,
             # specify the plugin_path if detected earlier
            args = ['vlc', '--plugin-path=' + plugin_path]
        return libvlc_new(len(args), args)

    def media_player_new(self, uri=None):
        """Create a new MediaPlayer instance.

        @param uri: an optional URI to play in the player.
        """
        p = libvlc_media_player_new(self)
        if uri:
            p.set_media(self.media_new(uri))
        p._instance = self
        return p

    def media_list_player_new(self):
        """Create a new MediaListPlayer instance.
        """
        p = libvlc_media_list_player_new(self)
        p._instance = self
        return p

    def media_new(self, mrl, *options):
        """Create a new Media instance.

        Options can be specified as supplementary string parameters, e.g.

        C{m = i.media_new('foo.avi', 'sub-filter=marq{marquee=Hello}', 'vout-filter=invert')}

        Alternatively, the options can be added to the media using the Media.add_options method:

        C{m.add_options('foo.avi', 'sub-filter=marq@test{marquee=Hello}', 'video-filter=invert')}

        @param options: optional media option=value strings
        """
        m = libvlc_media_new_location(self, mrl)
        for o in options:
            libvlc_media_add_option(m, o)
        return m

    def audio_output_enumerate_devices(self):
        """Enumerate the defined audio output devices.

        @return: list of dicts {name:, description:, devices:}
        """
        r = []
        head = libvlc_audio_output_list_get(self)
        if head:
            i = head
            while i:
                i = i.contents
                d = [{'id':       libvlc_audio_output_device_id      (self, i.name, d), 
                      'longname': libvlc_audio_output_device_longname(self, i.name, d)} 
                   for d in range(libvlc_audio_output_device_count   (self, i.name))]
                r.append({'name': i.name, 'description': i.description, 'devices': d})
                i = i.next
            libvlc_audio_output_list_release(head)
        return r

class Media:
    """Create a new Media instance.
    """

    def add_options(self, *options):
        """Add a list of options to the media.

        Options must be written without the double-dash, e.g.:

        C{m.add_options('sub-filter=marq@test{marquee=Hello}', 'video-filter=invert')}

        Alternatively, the options can directly be passed in the Instance.media_new method:

        C{m = instance.media_new('foo.avi', 'sub-filter=marq@test{marquee=Hello}', 'video-filter=invert')}

        @param options: optional media option=value strings
        """
        for o in options:
            self.add_option(o)

class MediaPlayer:  #PYCHOK expected (comment is lost)
    """Create a new MediaPlayer instance.

    It may take as parameter either:
      - a string (media URI). In this case, a vlc.Instance will be created.
      - a vlc.Instance
    """
    def __new__(cls, *args):
        if args:
            i = args[0]
            if i == 0:
                return None
            if isinstance(i, _Ints):
                return _Cobject(cls, ctypes.c_void_p(i))
            if isinstance(i, Instance):
                return i.media_player_new()

        i = Instance()
        o = i.media_player_new()
        if args:
            o.set_media(i.media_new(*args))  # args[0]
        return o

    def get_instance(self):
        """Return the associated Instance.
        """
        return self._instance  #PYCHOK expected

    def set_mrl(self, mrl, *options):
        """Set the MRL to play.

        @param mrl: The MRL
        @param options: optional media option=value strings
        @return: the Media object
        """
        m = self.get_instance().media_new(mrl, *options)
        self.set_media(m)
        return m

    def video_get_spu_description(self):
        """Get the description of available video subtitles.
        """
        return track_description_list(libvlc_video_get_spu_description(self))

    def video_get_title_description(self):
        """Get the description of available titles.
        """
        return track_description_list(libvlc_video_get_title_description(self))

    def video_get_chapter_description(self, title):
        """Get the description of available chapters for specific title.

        @param title: selected title (int)
        """
        return track_description_list(libvlc_video_get_chapter_description(self, title))

    def video_get_track_description(self):
        """Get the description of available video tracks.
        """
        return track_description_list(libvlc_video_get_track_description(self))

    def audio_get_track_description(self):
        """Get the description of available audio tracks.
        """
        return track_description_list(libvlc_audio_get_track_description(self))

    def video_get_width(self, num=0):
        """Get the width of a video in pixels.

        @param num: video number (default 0).
        """
        return self.video_get_size(num)[0]

    def video_get_height(self, num=0):
        """Get the height of a video in pixels.

        @param num: video number (default 0).
        """
        return self.video_get_size(num)[1]

class MediaListPlayer:
    """Create a new MediaListPlayer instance.

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
    """Create a new VLC log iterator.
    """
    def __iter__(self):
        return self

    def next(self):
        if not self.has_next():
            raise StopIteration
        buf=LogMessage()
        ret=libvlc_log_iterator_next(self, buf)
        return ret.contents

class Log:
    """Create a new VLC log instance.
    """
    def __iter__(self):
        return self.get_iterator()

    def dump(self):
        return [ str(m) for m in self ]

class EventManager:
    """Create an event manager with callback handler.

    This class interposes the registration and handling of
    event notifications in order to (a) remove the need for
    decorating each callback functions with the decorator
    '@callbackmethod', (b) allow any number of positional
    and/or keyword arguments to the callback (in addition
    to the Event instance) and (c) to preserve the Python
    objects such that the callback and argument objects
    remain alive (i.e. are not garbage collected) until
    B{after} the notification has been unregistered.

    @note: Only a single notification can be registered
    for each event type in an EventManager instance.
    """
    def __new__(cls, ptr=None):
        if ptr is None:
            raise LibVLCException("(INTERNAL) ctypes class.")
        if ptr == 0:
            return None
        o = object.__new__(cls)
        o._as_parameter_ = ptr  # was ctypes.c_void_p(ptr)
        o._callbacks_ = {}  # 3-tuples of Python objs
        o._callback_handler = None
        return o

    def event_attach(self, eventtype, callback, *args, **kwds):
        """Register an event notification.

        @param eventtype: the desired event type to be notified about
        @param callback: the function to call when the event occurs
        @param args: optional positional arguments for the callback
        @param kwds: optional keyword arguments for the callback
        @return: 0 on success, ENOMEM on error

        NOTE: The callback must have at least one argument, the Event
        instance.  The optional positional and keyword arguments are
        in addition to the first one.
        """
        if not isinstance(eventtype, EventType):
            raise LibVLCException("%s required: %r" % ('EventType', eventtype))
        if not hasattr(callback, '__call__'):  # callable()
            raise LibVLCException("%s required: %r" % ('callable', callback))

        if self._callback_handler is None:
            _called_from_ctypes = ctypes.CFUNCTYPE(None, ctypes.POINTER(Event), ctypes.c_void_p)
            @_called_from_ctypes
            def _callback_handler(event, unused):
                """(INTERNAL) handle callback call from ctypes.

                Note: we cannot simply make this an instance method of
                EventManager since ctypes callback does not append
                self as first parameter. Hence we use a closure.
                """
                try: # retrieve Python callback and arguments
                    call, args, kwds = self._callbacks_[event.contents.type.value]
                    # We dereference event.contents here to simplify callback code.
                    call(event.contents, *args, **kwds)
                except KeyError:  # detached?
                    pass
            self._callback_handler = _callback_handler

        r = libvlc_event_attach(self, eventtype, self._callback_handler, None)
        if not r:
            self._callbacks_[eventtype.value] = (callback, args, kwds)
        return r

    def event_detach(self, eventtype):
        """Unregister an event notification.

        @param eventtype: the event type notification to be removed
        """
        if not isinstance(eventtype, EventType):
            raise LibVLCException("%s required: %r" % ('EventType', eventtype))

        t = eventtype.value
        if t in self._callbacks_:
            del self._callbacks_[t] # remove, regardless of libvlc return value
            libvlc_event_detach(self, eventtype, self._callback_handler, None)
