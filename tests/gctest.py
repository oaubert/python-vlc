#! /usr/bin/python

"""Script checking for garbage collection issues with event handlers.

See https://github.com/oaubert/python-vlc/issues/2

This currently should exhibit the reported issue.
"""

import sys
import vlc
import time
import gc

i = vlc.Instance()
p = vlc.MediaPlayer()

def poschanged(foo):
    print "poschanged"

for n in range(10):
    p.stop()
    p.set_media(i.media_new(sys.argv[1]))
    em = p.event_manager()
    em.event_attach(vlc.EventType.MediaPlayerPositionChanged, poschanged)
    p.play()
    time.sleep(.5)
    p.pause()
    gc.collect()
    p.pause()
    time.sleep(.5)
