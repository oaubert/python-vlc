from distribute_setup import use_setuptools
use_setuptools()

import os
import re
from setuptools import setup
import sys

version = None
with open(os.path.join(os.path.dirname(__file__),
                       'generator',
                       'generate.py'), 'r') as f:
    for l in f:
        m = re.search('''__version__\s*=\s*["'](.+)["']''', l)
        if m:
            version = m.group(1)

if not version:
    sys.stderr.write("Cannot determine module version number")
    sys.exit(1)

setup(name='python-vlc-generator',
      version = version,
      author='Olivier Aubert',
      author_email='contact@olivieraubert.net',
      maintainer='Olivier Aubert',
      maintainer_email='contact@olivieraubert.net',
      url='http://wiki.videolan.org/PythonBinding',
      # FIXME: setup.py is not yet complete. There should be the
      # template files, etc.
      py_modules=['generator/generate.py'],
      keywords = [ 'vlc', 'video', 'bindings' ],
      license = "GPL",
      classifiers = [
          "Development Status :: 5 - Production/Stable",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: GNU General Public License v2 or later (LGPLv2+)",
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
          "Topic :: Software Development :: Code Generators"
      ],
      description = "VLC python bindings generator.",
      long_description = """This module provides the bindings generator for the native
      libvlc API (see http://wiki.videolan.org/LibVLC) of the VLC
      video player.
      """)
