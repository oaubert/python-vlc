#! /usr/bin/python

"""Script checking for garbage collection issues with event handlers.

See https://github.com/oaubert/python-vlc/issues/2

This currently does not exhibit the reported issue.
"""

import sys
import vlc
import time
import gc

p = vlc.MediaPlayer(sys.argv[1])
def endreached(foo):
    print "EndReached"
em = p.event_manager()
em.event_attach(vlc.EventType.MediaPlayerEndReached, endreached) 
p.play()
time.sleep(.5)
for n in range(10):
    print "Try", n
    p.pause()
    gc.collect()
    p.pause()
    time.sleep(.5)
