"""
Example of how to use the ANT module
"""
import sys

from psychopy import visual, core, event, monitors, tools
import pyglet
import time
import numpy as np
import random as random
from ant import ANTExp
import threading

################################
### Main program starts here

# Prepare the window and stimulus
winsize = [1440, 900]

mon = monitors.Monitor('testMonitor', distance=60, width=28.5)
mon.setDistance(60)
mon.setWidth(28.5)
mon.setSizePix(winsize)

win = visual.Window(winsize, waitBlanking=True, winType='pyglet', fullscr=True, 
        color='white', units='deg', monitor=mon)
pw = visual.TextStim(win, alignHoriz='center', wrapWidth=12, height=0.01, color='black', 
        text="Please wait (checking screen timing)...")
pw.autoDraw = True
pw.draw()
win.flip()
refresh = win.getActualFrameRate(nIdentical=50, nMaxFrames=900, nWarmUpFrames=100, threshold=1)
pw.autoDraw = False

halted = False

win.flip()
globalClock = core.Clock()
startTime = time.time()
now = globalClock.getTime()
if now > 0.001:
    sys.stderr.write("WARNING: Your machine seems a little slow; just looking at the watch takes more than 1 mS (%.3f)!\n" % t0)
else:
    print("Internal initial timing offset is not to worry about (only %0.6f s)" % now)

endExperiment = False
exp = ANTExp(mon, win, winsize, refresh, globalClock, startTime)

noPractice = exp.displayInstructions()

allData = None
if noPractice:
    sys.stderr.write("Skipped practice block on user's request\n")
else:
    exp.displayText("Starting practice block in 2 seconds", noWait=True, showLine=False, time=2)
    if not exp.practiceBlock():
        sys.stderr.write("Shortened practice block on user's request\n")

for r in range(6):
    if r%2 == 0:
        if exp.displayText("Starting experimental block %d of 3\nHit any key when ready to start." % (r/2+1), showLine=False):
            break
        core.wait(1)
    block = exp.fullExperiment()

    if block == None:
        break
    if allData == None:
        allData = block
    else:
        allData = np.concatenate((allData, block))

# do something with allData here!

endTime = time.time()
now = globalClock.getTime()
print("Real time was %0.3f and global clock counted %0.3f (compare %0.6f to initial timing offset to determine drift)" % 
        (endTime-startTime, now, now - (endTime-startTime)))

win.close()
core.quit()
