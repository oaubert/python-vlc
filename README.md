Python ctypes-based bindings for libvlc
=======================================

This file documents the bindings generator, not the bindings
themselves. For the bindings documentation, see the README.module
file.


The bindings generator generates ctypes-bindings from the include
files defining the public API. The same generated module should be
compatible with various versions of libvlc 2.* and 3.*. However, there
may be incompatible changes between major versions. Versioned bindings
for 2.2 and 3.0 are provided in the repository.

License
-------

The module generator is licensed under the GNU General Public License
version 2 or later.  The generated module is licensed, like libvlc,
under the GNU Lesser General Public License 2.1 or later.

Building from source
--------------------

You can get the latest version of the code generator from
<https://github.com/oaubert/python-vlc/> or
<http://git.videolan.org/?p=vlc/bindings/python.git>.

The code expects to be placed inside a VLC source tree, in
vlc/bindings/python, so that it finds the development include files,
or to find the installed include files in /usr/include (on Debian,
install libvlc-dev).

To generate the vlc.py module and its documentation, for both the
development version and the installed VLC version, use

    make

If you want to generate the bindings from an installed version of the
VLC includes (which are expected to be in /usr/include/vlc), use the
'installed' target:

    make installed

To install it for development purposes (add a symlink to your Python
library) simply do

    python setup.py develop

preferably inside a virtualenv. You can uninstall it later with

    python setup.py develop --uninstall

Documentation building needs epydoc. An online build is available at
<http://olivieraubert.net/vlc/python-ctypes/>

Packaging
---------

The generated module version number is built from the VLC version
number and the generator version number:

vlc_major.vlc_minor.(1000 * vlc_micro + 100 * generator_major + generator_minor)

so that it shared it major.minor with the corresponding VLC.

To generate the reference PyPI module (including setup.py, examples
and metadata files), use

    make dist

LibVLC Discord
-----------------
[![Join the chat at https://discord.gg/3h3K3JF](https://img.shields.io/discord/716939396464508958?label=discord)](https://discord.gg/3h3K3JF)

python-vlc is part of the LibVLC Discord Community server. Feel free to come say hi!

How to contribute
-----------------

There are short-terms contributions (reporting and fixing bugs,
contributing unit tests, contributing examples). A number of libvlc
functions are currently blacklisted (search for `_blacklist` in the
generator code), mostly because of their signature complexity. They
would benefit some work.

Longer terms goals include the rewriting of the generator to use a
proper parser for the C-syntax (for the moment, the parser relies on
regexp-based expression, which works thanks to the coding style
applied in the code, but remains very fragile).
