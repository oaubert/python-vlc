Python ctypes-based bindings for libvlc
=======================================

The bindings use ctypes to directly call the libvlc dynamic lib, and
the code is generated from the include files defining the public
API. The same module is compatible with various versions of libvlc
2.*.

License
-------

The generated module is licensed, like libvlc, under the GNU Lesser
General Public License 2.1 or later. The module generator itself is
licensed under the GNU General Public License version 2 or later.

Building from source
--------------------

You can get the latest version of the code generator from
<https://github.com/oaubert/python-vlc/>

To generate the vlc.py module and its documentation, use

    make

To install it for development purposes (add a symlink to your Python
library) simply do

    python setup.py develop

preferably inside a virtualenv. You can uninstall it later with

    python setup.py develop --uninstall

Documentation building needs epydoc. An online build is available at
<http://olivieraubert.net/vlc/python-ctypes/>

Layout
------

The module offers two ways of accessing the API - a raw access to all
exported methods, and more convenient wrapper classes :

- Raw access: methods are available as attributes of the vlc
  module. Use their docstring (any introspective shell like ipython is
  your friends) to explore them.

- Wrapper classes: most major structures of the libvlc API (Instance,
  Media, MediaPlayer, etc) are wrapped as classes, with shorter method
  names.

Using the module
----------------

On win32, the simplest way is to put the ``vlc.py`` file in the same
directory as the libvlc.dll file (standard location:
``c:\Program Files\VideoLAN\VLC``).

- Using raw access:

    >>> import vlc
    >>> vlc.libvlc_get_version()
    '1.0.0 Goldeneye'
    >>> e=vlc.VLCException()
    >>> i=vlc.libvlc_new(0, [], e)
    >>> i
    <vlc.Instance object at 0x8384a4c>
    >>> vlc.libvlc_audio_get_volume(i,e)
    50

- Using wrapper classes:

   >>> import vlc
   >>> i=vlc.Instance('--no-audio', '--fullscreen')
   >>> i.audio_get_volume()
   50
   >>> p=i.media_player_new()
   >>> m=i.media_new('file:///tmp/foo.avi')
   >>> m.get_mrl()
   'file:///tmp/foo.avi'
   >>> p.set_media(m)
   >>> p.play()

or shorter:

   >>> import vlc
   >>> p=vlc.MediaPlayer('file:///tmp/foo.avi')
   >>> p.play()

In this latter case, a default ``vlc.Instance`` will be instanciated and
stored in ``vlc._default_instance``. It will be used to instanciate the
various classes (``Media``, ``MediaList``, ``MediaPlayer``, etc).
