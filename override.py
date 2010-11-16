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
        """Create a new MediaPlayer instance.

        @param uri: an optional URI to play in the player.
        """
        p=libvlc_media_player_new(self)
        if uri:
            p.set_media(self.media_new(uri))
        p._instance=self
        return p

    def media_list_player_new(self):
        """Create a new MediaListPlayer instance.
        """
        p=libvlc_media_list_player_new(self)
        p._instance=self
        return p

    def media_new(self, mrl, *options):
        """Create a new Media instance.

        Options can be specified as supplementary string parameters, e.g.
        m=i.media_new('foo.avi', 'sub-filter=marq{marquee=Hello}', 'vout-filter=invert')
        """
        m=libvlc_media_new_location(self, mrl)
        for o in options:
            libvlc_media_add_option(m, o)
        return m

    def audio_output_enumerate_devices(self):
        """Enumerate the defined audio output devices.

        The result is a list of dict (name, description)
        """
        l = []
        head = ao = libvlc_audio_output_list_get(self)
        while ao:
            l.append( { 'name': ao.contents.name,
                        'description': ao.contents.description,
                        'devices': [ { 'id': libvlc_audio_output_device_id(self, ao.contents.name, i),
                                       'longname': libvlc_audio_output_device_longname(self, ao.contents.name, i) }
                                     for i in range(libvlc_audio_output_device_count(self, ao.contents.name) ) ] } )
            ao = ao.contents.next
        libvlc_audio_output_list_release(head)
        return l

class Media:
    """Create a new Media instance.
    """

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

    def set_mrl(self, mrl, *options):
        """Set the MRL to play.

        @param mrl: The MRL
        @param options: a list of options
        @return The Media object
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
        @param i_title selected title (int)
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

    def video_get_size(self, num=0):
        """Get the size of a video in pixels as 2-tuple (width, height).

        @param num: video number (default 0)
        """
        x, y = ctypes.c_ulong(), ctypes.c_ulong()  # or c_uint?
        if libvlc_video_get_size(self, num, ctypes.byref(x), ctypes.byref(y)):
            raise LibVLCException('invalid video number (%s)' % (num,))
        return int(x.value), int(y.value)

    def video_get_width(self, num=0):
        """Get the width of a video in pixels.

        @param num: video number (default 0)
        """
        return self.video_get_size(num)[0]

    def video_get_height(self, num=0):
        """Get the height of a video in pixels.

        @param num: video number (default 0)
        """
        return self.video_get_size(num)[1]

    def video_get_cursor(self, num=0):
        """Get the mouse pointer coordinates over a video as 2-tuple (x, y).

        Coordinates are expressed in terms of the decoded video resolution,
        <b>not</b> in terms of pixels on the screen/viewport.  To get the
        latter, you must query your windowing system directly.

        Either coordinate may be negative or larger than the corresponding
        size of the video, if the cursor is outside the rendering area.

        @warning The coordinates may be out-of-date if the pointer is not
        located on the video rendering area.  LibVLC does not track the
        mouse pointer if it is outside the video widget.

        @note LibVLC does not support multiple mouse pointers (but does
        support multiple input devices sharing the same pointer).

        @param num: video number (default 0)
        """
        x, y = ctypes.c_long(), ctypes.c_long()  # or c_int?
        if libvlc_video_get_cursor(self, num, ctypes.byref(x), ctypes.byref(y)):
            raise LibVLCException('invalid video number (%s)' % (num,))
        return int(x.value), int(y.value)

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
    """Create an event manager and handler.

       This class interposes the registration and handling of
       event notifications in order to (a) allow any number of
       positional and/or keyword arguments to the callback (in
       addition to the Event instance), (b) preserve the Python
       argument objects and (c) remove the need for decorating
       each callback with decorator '@callbackmethod'.

       Calls from ctypes to Python callbacks are handled by
       function _callback_handler.

       A side benefit of this scheme is that the callback and
       all argument objects remain alive (i.e. are not garbage
       collected) until *after* the event notification has
       been unregistered.

       NOTE: only a single notification can be registered for
       each event type in an EventManager instance.
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
            def _callback_handler(event, data):
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
