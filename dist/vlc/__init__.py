# A Python package, what a surprise!

# VLC and Python Version checker.
#
# Author:  Ben McGinnes <ben@adversary.org>
# GPG Key:  0x321E4E2373590E5D
#
# This library is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation; either version 2.1 of the
# License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston MA 02110-1301 USA

import os
import os.path
import subprocess
import sys
import inspect

# Just in case people are using Python 3, sets VLC module path:

inspector = inspect.getfile(inspect.currentframe())
cmd_folder = os.path.realpath(os.path.abspath(os.path.split(inspector)[0]))
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)


if sys.platform == "darwin":
    vlcx = "VLC"
    topdir = os.path.abspath("/Applications/")
elif sys.platform == "win32" or "cygwin":
    vlcx = "vlc.exe"
    topdir = os.path.abspath("C:\\Program Files\\")
elif sys.platform == "linux" or "linux2":
    topdir = os.path.abspath("/")
    vlcx = "vlc"
else:
    vlcx = "vlc"  # probably (includes Solaris, SunOS and assorted BSDs)
    topdir = os.path.abspath("/")


def vlcpath(vlcx, topdir):
    for root, dirs, files in os.walk(topdir, topdown=False):
        if vlcx in files:
            return os.path.join(root, vlcx)


vlcexec = vlcpath(vlcx, topdir)
vlcepath = vlcexec[0:(len(vlcexec) - len(vlcx))]

vlc_ver = subprocess.Popen([vlcexec, "--version"],
                           stdout=subprocess.PIPE).communicate()[0]
vlcver = vlc_ver.split(" ")[2]


if vlcver.startswith(b"1.0"):
    from vlc_100 import *
elif vlcver.startswith(b"1.1"):
    from vlc_110 import *
elif vlcver.startswith(b"2.0"):
    from vlc_200 import *
elif vlcver.startswith(b"2.1"):
    from vlc_210 import *
else:
    from vlc_current import *
