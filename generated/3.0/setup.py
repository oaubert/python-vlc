from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup

setup(name='python-vlc',
      version = '3.0.0102',
      author='Olivier Aubert',
      author_email='contact@olivieraubert.net',
      maintainer='Olivier Aubert',
      maintainer_email='contact@olivieraubert.net',
      url='http://wiki.videolan.org/PythonBinding',
      py_modules=['vlc'],
      keywords = [ 'vlc', 'video' ],
      license = "GPL",
      classifiers = [
          "Development Status :: 5 - Production/Stable",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)",
          "Operating System :: MacOS :: MacOS X",
          "Operating System :: Microsoft :: Windows",
          "Operating System :: POSIX :: Linux",
          "Operating System :: POSIX :: Other",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2",
          "Programming Language :: Python :: 3",
          "Topic :: Multimedia",
          "Topic :: Multimedia :: Sound/Audio",
          "Topic :: Multimedia :: Video",
      ],
      description = "VLC bindings for python.",
      long_description = """This module provides ctypes-based bindings (see
      http://wiki.videolan.org/PythonBinding) for the native libvlc
      API (see http://wiki.videolan.org/LibVLC) of the VLC video
      player. Note that it relies on an already present install of VLC.

      It has been automatically generated from the include files of
      vlc 3.0.0, using generator 1.2.
      """)
