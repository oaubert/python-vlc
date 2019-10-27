
class Instance:
    """Create a new Instance instance.

    It may take as parameter either:
      - a string
      - a list of strings as first parameters
      - the parameters given as the constructor parameters (must be strings)
    """
    def __new__(cls, *args):
        if len(args) == 1:
            # Only 1 arg. It is either a C pointer, or an arg string,
            # or a tuple.
            i = args[0]
            if isinstance(i, _Ints):
                return _Constructor(cls, i)
            elif isinstance(i, basestring):
                args = i.strip().split()
            elif isinstance(i, _Seqs):
                args = list(i)
            else:
                raise VLCException('Instance %r' % (args,))
        else:
            args = list(args)

        if not args:  # no parameters passed
            args = ['vlc']
        elif args[0] != 'vlc':
            args.insert(0, 'vlc')

        if plugin_path is not None:
            # set plugin_path if detected, win32 and MacOS,
            # if the user did not specify it itself.
            os.environ.setdefault('VLC_PLUGIN_PATH', plugin_path)

        if PYTHON3:
            args = [ str_to_bytes(a) for a in args ]
        return libvlc_new(len(args), args)

    def media_player_new(self, uri=None):
        """Create a new MediaPlayer instance.

        @param uri: an optional URI to play in the player as a str, bytes or PathLike object.
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

        If mrl contains a colon (:) preceded by more than 1 letter, it
        will be treated as a URL. Else, it will be considered as a
        local path. If you need more control, directly use
        media_new_location/media_new_path methods.

        Options can be specified as supplementary string parameters,
        but note that many options cannot be set at the media level,
        and rather at the Instance level. For instance, the marquee
        filter must be specified when creating the vlc.Instance or
        vlc.MediaPlayer.

        Alternatively, options can be added to the media using the
        Media.add_options method (with the same limitation).

        @param mrl: A str, bytes or PathLike object
        @param options: optional media option=value strings
        """
        mrl = try_fspath(mrl)
        if ':' in mrl and mrl.index(':') > 1:
            # Assume it is a URL
            m = libvlc_media_new_location(self, str_to_bytes(mrl))
        else:
            # Else it should be a local path.
            m = libvlc_media_new_path(self, str_to_bytes(os.path.normpath(mrl)))
        for o in options:
            libvlc_media_add_option(m, str_to_bytes(o))
        m._instance = self
        return m

    def media_new_path(self, path):
        """Create a media for a certain file path.
        See L{media_release}.
        @param path: A str, byte, or PathLike object representing a local filesystem path.
        @return: the newly created media or None on error.
        """
        path = try_fspath(path)
        return libvlc_media_new_path(self, str_to_bytes(path))

    def media_list_new(self, mrls=None):
        """Create a new MediaList instance.
        @param mrls: optional list of MRL strings, bytes, or PathLike objects.
        """
        l = libvlc_media_list_new(self)
        # We should take the lock, but since we did not leak the
        # reference, nobody else can access it.
        if mrls:
            for m in mrls:
                l.add_media(m)
        l._instance = self
        return l

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
                r.append({'name': i.name, 'description': i.description})
                i = i.next
            libvlc_audio_output_list_release(head)
        return r

    def audio_filter_list_get(self):
        """Returns a list of available audio filters.

        """
        return module_description_list(libvlc_audio_filter_list_get(self))

    def video_filter_list_get(self):
        """Returns a list of available video filters.

        """
        return module_description_list(libvlc_video_filter_list_get(self))

class Media:
    """Create a new Media instance.

    Usage: Media(MRL, *options)

    See vlc.Instance.media_new documentation for details.
    """
    def __new__(cls, *args):
        if args:
            i = args[0]
            if isinstance(i, _Ints):
                return _Constructor(cls, i)
            if isinstance(i, Instance):
                return i.media_new(*args[1:])

        o = get_default_instance().media_new(*args)
        return o

    def get_instance(self):
        return getattr(self, '_instance', None)

    def add_options(self, *options):
        """Add a list of options to the media.

        Options must be written without the double-dash. Warning: most
        audio and video options, such as text renderer, have no
        effects on an individual media. These options must be set at
        the vlc.Instance or vlc.MediaPlayer instanciation.

        @param options: optional media option=value strings
        """
        for o in options:
            self.add_option(o)

    def tracks_get(self):
        """Get media descriptor's elementary streams description
        Note, you need to call L{parse}() or play the media at least once
        before calling this function.
        Not doing this will result in an empty array.
        The result must be freed with L{tracks_release}.
        @version: LibVLC 2.1.0 and later.
        """
        mediaTrack_pp = ctypes.POINTER(MediaTrack)()
        n = libvlc_media_tracks_get(self, ctypes.byref(mediaTrack_pp))
        info = ctypes.cast(mediaTrack_pp, ctypes.POINTER(ctypes.POINTER(MediaTrack) * n))
        try:
            contents = info.contents
        except ValueError:
            # Media not parsed, no info.
            return None
        tracks = ( contents[i].contents for i in range(len(contents)) )
        # libvlc_media_tracks_release(mediaTrack_pp, n)
        return tracks

class MediaList:
    """Create a new MediaList instance.

    Usage: MediaList(list_of_MRLs)

    See vlc.Instance.media_list_new documentation for details.
    """
    def __new__(cls, *args):
        if args:
            i = args[0]
            if isinstance(i, _Ints):
                return _Constructor(cls, i)
            if isinstance(i, Instance):
                return i.media_list_new(*args[1:])

        o = get_default_instance().media_list_new(*args)
        return o

    def get_instance(self):
        return getattr(self, '_instance', None)

    def add_media(self, mrl):
        """Add media instance to media list.

        The L{lock} should be held upon entering this function.
        @param mrl: a media instance or a MRL.
        @return: 0 on success, -1 if the media list is read-only.
        """
        mrl = try_fspath(mrl)
        if isinstance(mrl, basestring):
            mrl = (self.get_instance() or get_default_instance()).media_new(mrl)
        return libvlc_media_list_add_media(self, mrl)

class MediaPlayer:  #PYCHOK expected (comment is lost)
    """Create a new MediaPlayer instance.

    It may take as parameter either:
      - a string (media URI), options... In this case, a vlc.Instance will be created.
      - a vlc.Instance, a string (media URI), options...
    """
    def __new__(cls, *args):
        if len(args) == 1 and isinstance(args[0], _Ints):
            return _Constructor(cls, args[0])

        if args and isinstance(args[0], Instance):
            instance = args[0]
            args = args[1:]
        else:
            instance = get_default_instance()

        o = instance.media_player_new()
        if args:
            o.set_media(instance.media_new(*args))
        return o

    def get_instance(self):
        """Return the associated Instance.
        """
        return self._instance  #PYCHOK expected

    def set_mrl(self, mrl, *options):
        """Set the MRL to play.

        Warning: most audio and video options, such as text renderer,
        have no effects on an individual media. These options must be
        set at the vlc.Instance or vlc.MediaPlayer instanciation.

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

    def video_get_track_description(self):
        """Get the description of available video tracks.
        """
        return track_description_list(libvlc_video_get_track_description(self))

    def audio_get_track_description(self):
        """Get the description of available audio tracks.
        """
        return track_description_list(libvlc_audio_get_track_description(self))

    def get_full_title_descriptions(self):
        '''Get the full description of available titles.
        @return: the titles list
        @version: LibVLC 3.0.0 and later.
        '''
        titleDescription_pp = ctypes.POINTER(TitleDescription)()
        n = libvlc_media_player_get_full_title_descriptions(self, ctypes.byref(titleDescription_pp))
        info = ctypes.cast(titleDescription_pp, ctypes.POINTER(ctypes.POINTER(TitleDescription) * n))
        try:
            contents = info.contents
        except ValueError:
            # Media not parsed, no info.
            return None
        descr = ( contents[i].contents for i in range(len(contents)) )
        return descr

    def get_full_chapter_descriptions(self, i_chapters_of_title):
        '''Get the full description of available chapters.
        @param i_chapters_of_title: index of the title to query for chapters (uses current title if set to -1).
        @return: the chapters list
        @version: LibVLC 3.0.0 and later.
        '''
        chapterDescription_pp = ctypes.POINTER(ChapterDescription)()
        n = libvlc_media_player_get_full_chapter_descriptions(self, ctypes.byref(chapterDescription_pp))
        info = ctypes.cast(chapterDescription_pp, ctypes.POINTER(ctypes.POINTER(ChapterDescription) * n))
        try:
            contents = info.contents
        except ValueError:
            # Media not parsed, no info.
            return None
        descr = ( contents[i].contents for i in range(len(contents)) )
        return descr

    def video_get_size(self, num=0):
        """Get the video size in pixels as 2-tuple (width, height).

        @param num: video number (default 0).
        """
        r = libvlc_video_get_size(self, num)
        if isinstance(r, tuple) and len(r) == 2:
            return r
        else:
            raise VLCException('invalid video number (%s)' % (num,))

    def set_hwnd(self, drawable):
        """Set a Win32/Win64 API window handle (HWND).

        Specify where the media player should render its video
        output. If LibVLC was built without Win32/Win64 API output
        support, then this has no effects.

        @param drawable: windows handle of the drawable.
        """
        if not isinstance(drawable, ctypes.c_void_p):
            drawable = ctypes.c_void_p(int(drawable))
        libvlc_media_player_set_hwnd(self, drawable)

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

    def video_get_cursor(self, num=0):
        """Get the mouse pointer coordinates over a video as 2-tuple (x, y).

        Coordinates are expressed in terms of the decoded video resolution,
        B{not} in terms of pixels on the screen/viewport.  To get the
        latter, you must query your windowing system directly.

        Either coordinate may be negative or larger than the corresponding
        size of the video, if the cursor is outside the rendering area.

        @warning: The coordinates may be out-of-date if the pointer is not
        located on the video rendering area.  LibVLC does not track the
        mouse pointer if the latter is outside the video widget.

        @note: LibVLC does not support multiple mouse pointers (but does
        support multiple input devices sharing the same pointer).

        @param num: video number (default 0).
        """
        r = libvlc_video_get_cursor(self, num)
        if isinstance(r, tuple) and len(r) == 2:
            return r
        raise VLCException('invalid video number (%s)' % (num,))

class MediaListPlayer:
    """Create a new MediaListPlayer instance.

    It may take as parameter either:
      - a vlc.Instance
      - nothing
    """
    def __new__(cls, arg=None):
        if arg is None:
            i = get_default_instance()
        elif isinstance(arg, Instance):
            i = arg
        elif isinstance(arg, _Ints):
            return _Constructor(cls, arg)
        else:
            raise TypeError('MediaListPlayer %r' % (arg,))

        return i.media_list_player_new()

    def get_instance(self):
        """Return the associated Instance.
        """
        return self._instance  #PYCHOK expected

class LogIterator:
    """Create a new VLC log iterator.
    """
    def __iter__(self):
        return self

    def next(self):
        if self.has_next():
            b = LogMessage()
            i = libvlc_log_iterator_next(self, b)
            return i.contents
        raise StopIteration

    def __next__(self):
        return self.next()

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
    _callback_handler = None
    _callbacks = {}

    def __new__(cls, ptr=_internal_guard):
        if ptr == _internal_guard:
            raise VLCException("(INTERNAL) ctypes class.\nYou should get a reference to EventManager through the MediaPlayer.event_manager() method.")
        return _Constructor(cls, ptr)

    def event_attach(self, eventtype, callback, *args, **kwds):
        """Register an event notification.

        @param eventtype: the desired event type to be notified about.
        @param callback: the function to call when the event occurs.
        @param args: optional positional arguments for the callback.
        @param kwds: optional keyword arguments for the callback.
        @return: 0 on success, ENOMEM on error.

        @note: The callback function must have at least one argument,
        an Event instance.  Any other, optional positional and keyword
        arguments are in B{addition} to the first one. Warning: libvlc
        is not reentrant, i.e. you cannot call libvlc functions from
        an event handler. They must be called from the main
        application thread.
        """
        if not isinstance(eventtype, EventType):
            raise VLCException("%s required: %r" % ('EventType', eventtype))
        if not hasattr(callback, '__call__'):  # callable()
            raise VLCException("%s required: %r" % ('callable', callback))
         # check that the callback expects arguments
        if not any(getargspec(callback)[:2]):  # list(...)
            raise VLCException("%s required: %r" % ('argument', callback))

        if self._callback_handler is None:
            _called_from_ctypes = ctypes.CFUNCTYPE(None, ctypes.POINTER(Event), ctypes.c_void_p)
            @_called_from_ctypes
            def _callback_handler(event, k):
                """(INTERNAL) handle callback call from ctypes.

                @note: We cannot simply make this an EventManager
                method since ctypes does not prepend self as the
                first parameter, hence this closure.
                """
                try: # retrieve Python callback and arguments
                    call, args, kwds = self._callbacks[k]
                except KeyError:  # detached?
                    pass
                else:
                    # deref event.contents to simplify callback code
                    call(event.contents, *args, **kwds)
            self._callback_handler = _callback_handler
            self._callbacks = {}

        k = eventtype.value
        r = libvlc_event_attach(self, k, self._callback_handler, k)
        if not r:
            self._callbacks[k] = (callback, args, kwds)
        return r

    def event_detach(self, eventtype):
        """Unregister an event notification.

        @param eventtype: the event type notification to be removed.
        """
        if not isinstance(eventtype, EventType):
            raise VLCException("%s required: %r" % ('EventType', eventtype))

        k = eventtype.value
        if k in self._callbacks:
            del self._callbacks[k] # remove, regardless of libvlc return value
            libvlc_event_detach(self, k, self._callback_handler, k)

class AudioEqualizer:
    """Create a new default equalizer, with all frequency values zeroed.

    The new equalizer can subsequently be applied to a media player by invoking
    L{MediaPlayer.set_equalizer}.
    The returned handle should be freed via libvlc_audio_equalizer_release() when
    it is no longer needed."""
    def __new__(cls, *args):
        if len(args) == 1 and isinstance(args[0], _Ints):
            return _Constructor(cls, args[0])
        return libvlc_audio_equalizer_new()
