"""
ANT (Attention Network Test) implemented in PsychoPy2

Created by Per Baekgaard / pgba@dtu.dk / baekgaard@b4net.dk, September 2015

Licensed under the MIT License:

    Copyright (c) 2015,2016 Per Baekgaard, Technical University of Denmark, DTU Informatics, Cognitive Systems Section

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without
limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the
Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE
OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""
__author__ = "Per Baekgaard"
__copyright__ = \
            "Copyright (c) 2015, Per Baekgaard, Technical University of Denmark, DTU Informatics, Cognitive Systems Section"
__license__ = "MIT"
__version__ = "1.0"
__email__ = "pgba@dtu.dk"
__status__ = "Beta"

import sys

from psychopy import visual, core, event, monitors, tools
import pyglet
import time
import numpy as np
import random as random

class Bunch(object):
    def __init__(self, **kwds):
        self.__dict__.update(kwds)

# Experimental setup
class ANTExp:
    """This class implements the ANT (Attention Network Test) in PsychoPy2

    To use this class, do something like the following:


        # Create the ANT Experimental class
        exp = ANTExp(mon, win, winsize, refresh, globalClock, startTime, alog)

        # Show the instructions to the user
        noPractice = exp.displayInstructions()

        # Run the practice block
        exp.practiceBlock():

        # Run the real experiment as 3*2 runs
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

        # do something with allData


    For a full description of the original experiment, see:
        Jin Fan, Bruce D. McCandliss, Tobias Sommer, Amir Raz, and Michael I. Posner:
        "Testing the Efficiency and Independence of Attentional Networks"
        Journal of Cognitive Neuroscience 14:3, pp. 340-347 (2002)
    """

    def _fixStim(self):
        """Returns a fixation cross '+' (as a visual) to be drawn later"""
        a = self.cueSize/2.
        vertices = [[0,0], [0,a], [0,-a], [0,0], [-a,0], [a,0], [0,0]]

        return visual.ShapeStim(self.win, fillColor=None, lineColor='black', 
                lineWidth=self.allWidthPix, units='deg', vertices=vertices)

    def _cueStim(self):
        """Returns a cue '*' (as a visual) to be drawn later"""
        a = self.cueSize/2.
        w = self.cueSize/20.
        c1 = a*0.9511
        s1 = a*0.3090
        c2 = a*0.5878
        s2 = a*0.8090

        vertices = [[0,0], [0,a], [0,0], [c1, s1], [0,0], [c2, -s2], [0,0], [-c2, -s2], [0,0], [-c1, s1], [0,0]]

        return visual.ShapeStim(self.win, fillColor=None, lineColor='black', 
                lineWidth=self.allWidthPix, units='deg', vertices=vertices)

    def _drawLine(self, pos, sz, pw, short, tdir):
        """Return a tdir (left or right) line of width pw at pos of given sz, 
        making it possibly short (to make room for arrow heads)
        """
        a = sz/2.
        if short and tdir=='left':
            vertices = [[a, pw], [-a/3.0, pw], [-a/3.0, -pw], [a, -pw]]
        elif short and tdir=='right':
            vertices = [[-a, pw], [a/3.0, pw], [a/3.0, -pw], [-a, -pw]]
        else:
            vertices = [[-a, pw], [a, pw], [a, -pw], [-a, -pw]]
        return visual.ShapeStim(self.win, pos=pos, lineColor=None, fillColor='black', units='deg', vertices=vertices)

    def _drawHead(self, pos, sz, pw, tdir):
        """Return an arrowhead (left or right, depending on tdir) fitting with a short line"""
        a = sz/2.
        if tdir=='left':
            vertices = [[-a/3.0, a/3.0], [-a, 0], [-a/3.0, -a/3.0]]
        elif tdir=='right':
            vertices = [[a/3.0, a/3.0], [a, 0], [a/3.0, -a/3.0]]
        return visual.ShapeStim(self.win, pos=pos, lineColor=None, fillColor='black', units='deg', vertices=vertices)


    def _targetStim(self, tloc, tdir, flank):
        """Return a complete buffer of specified target at position tloc (top or down) 
        with flankers (congruent, neutral, or incongruent) in direction tdir (left or right)
        ready to flip
        """
        sz = self.arrowSize
        pw = self.allWidthDeg
        p = self.arrowSize + self.arrowSep
        y = self.targetDist if tloc=='top' else -self.targetDist
        if self.runDummy:
            lines = [ self._drawLine((x, y), sz, pw, False, None) for x in (-2*p, -p, 0, p, 2*p) ]
            heads = []
        elif flank=='neutral':
            lines = [ self._drawLine((x, y), sz, pw, False, None) for x in (-2*p, -p, p, 2*p) ]

            lines = lines + [self._drawLine((0, y), sz, pw, True, tdir)]
            heads = [ self._drawHead((0, y), sz, pw, tdir) ]
        elif flank=='congruent':
            lines = [ self._drawLine((x, y), sz, pw, True, tdir) for x in (-2*p, -p, 0, p, 2*p) ]
            heads = [ self._drawHead((x, y), sz, pw, tdir) for x in (-2*p, -p, 0, p, 2*p) ]
        elif flank=='incongruent':
            rdir = 'left' if tdir=='right' else 'right'
            lines = [ self._drawLine((x, y), sz, pw, True, rdir) for x in (-2*p, -p, p, 2*p) ]
            heads = [ self._drawHead((x, y), sz, pw, rdir) for x in (-2*p, -p, p, 2*p) ]

            lines = lines + [ self._drawLine((0, y), sz, pw, True, tdir) ]
            heads = heads + [ self._drawHead((0, y), sz, pw, tdir) ]

        return visual.BufferImageStim(self.win, stim=(lines + heads))

    def __init__(self, mon, win, winsize, refreshRate, clock, startTime, logfile=None, runDummy=False, original=True):
        """Create an ANTExp class at the specified monitor/window of given size and refreshrate

        mon -- the (PsychoPy) monitor spec; needed to determine correct scale
        win -- the (PsychoPy) window visual on which you will run the experiment (should be full screen)
        winsize -- (width, height) of the monitor in pixels
        refreshRate -- the monitor refresh rate in frames pr second; needed to calculate proper frame timing
        clock -- the (PsycoPy) clock which you use for measuring time within this experiment
        startTime -- the walltime (epoch; seconds since Jan 1st 1970 00:00) that corresponds to clock==0.0
        logFile -- an open file that is used for printing results to (if not given, then stdout is used)
        runDummy -- removes arrowheads; can be used when no response is solicited from the user
        original -- can be set to False to remove fixation crosses after the user has replied

        """
        self.mon = mon
        self.win = win
        self.winsize = winsize
        self.refreshRate = refreshRate
        self.frameTime = 1.0 / refreshRate
        self.clock = clock
        self.startTime = startTime
        self.logfile = logfile
        self.runDummy = runDummy
        self.original = original

        if logfile:
            logfile.write("wallt;t0;warning;position;direction;congruency;d1;ct;d2;rt;tf;response\n")
        else:
            print("wallt;t0;warning;position;direction;congruency;d1;ct;d2;rt;tf;response")


        ### BEGIN Semi-configurable values
        # Timings for each 'procedure'
        self.tD1min = 400                   # Min initial fixation time
        self.tD1max = 1600                  # Max initial fixation time
        self.tCue   = 100                   # Cue time
        self.tNoCue = 400                   # Time after cue before target
        self.tOut   = 1700                  # Target timeout
        self.tDummy = 700                   # TIme to show target when running dummy
        self.tExp   = 4000                  # Total procedure time

        # Visual setup
        self.arrowSize  = 0.55              # Size of an arrow (visual angle)
        self.arrowSep   = 0.06              # Separation between arrows (visual angle)
        self.cueSize    = 0.35              # Size of the fixation and the cue (size from opensesame implementation)
        self.allWidthDeg  = 0.04            # Linewidth of stimuli (visual angle)
        self.allWidthPix  = tools.monitorunittools.deg2pix(self.allWidthDeg, mon) # Linewidth of stimuli (in pixels!)

        self.targetDist = 1.06              # Vertical distance from fixation center to target center
        ### END (Semi-)configurable options

        # Set up the experimental combinations, creating a list of all combinations of cue, location, direction and flankers
        self.procedures = [Bunch()] * 48
        i = 0
        for cue in ('no', 'spatial', 'center', 'double'):
            for tloc in ('top', 'bottom'):
                for tdir in ('left', 'right'):
                    for flank in ('incongruent', 'neutral', 'congruent'):
                        self.procedures[i] = Bunch(cue=cue, tloc=tloc, tdir=tdir, flank=flank)
                        i += 1

        # Create visual stimuli to be used (fixation cross and cues and all targets)
        self.visFix = self._fixStim()
        self.visCue = self._cueStim()

        self.visTarget ={}
        for tloc in ('top', 'bottom'):
            for tdir in ('left', 'right'):
                for flank in ('incongruent', 'neutral', 'congruent'):
                    self.visTarget[tloc+tdir+flank] = self._targetStim(tloc, tdir, flank)


    def _oneProcedure(self, condition, short=False):
        """Presents one complete 'procedure' of (initial fixation, cue, wait, target and response and final delay)

        Returns the timing for said procedure, using the clock set up initially or None if the user halted!

        Expects to be called with "some time" before next flip, and returns immediately after the final flip
        so it can be called repeatedly with no delays, and will then run the experiment at the expected timing

        Overall procedure is like this -- for each stimuli to be show:

            Draw stimuli to backbuffer
            Wait until previous stimuli is done
            Flip window and wait until retrace
            (Repeat for next stimuli)

        condition -- the condition requested (cue, tloc, pos)
        short -- can be used to shorten the waiting time after the user has replied;
                 this can be helpful in the practice rounds (but was likely not present in the original experiment).

        """

        def waitAndFlip(t):
            """Wait until next flip after time t (offset to self.clock) has passed, then flip (once only!)

            Returns time of flip (also offset to self.clock)
            """

            core.wait(t - self.clock.getTime() - self.frameTime, self.frameTime/2.0)

            self.win.flip()

            return self.clock.getTime()

        quit = False

        # Draw initial fixation cross and get start-time from the global clock (no previous stimuli)
        self.visFix.draw()
        self.win.flip()
        t0 = self.clock.getTime()

        # Pull a random waiting time
        r = random.randrange(self.tD1min, self.tD1max, 10)

        # Draw cue (if any)
        if condition.cue != 'no':
            if condition.cue == 'double' or (condition.cue == 'spatial' and condition.tloc == 'top'):
                if self.original:
                    self.visFix.draw()
                self.visCue.pos = (0,  self.targetDist)
                self.visCue.draw()
            if condition.cue == 'double' or (condition.cue == 'spatial' and condition.tloc == 'bottom'):
                if self.original:
                    self.visFix.draw()
                self.visCue.pos = (0, -self.targetDist)
                self.visCue.draw()
            if condition.cue == 'center':
                self.visCue.pos = (0, 0)
                self.visCue.draw()
        else:
            self.visFix.draw()

        # Wait random time and Present cue when ready
        d1 = waitAndFlip(t0 + r/1000.0) - t0

        # Draw fixation cross again
        self.visFix.draw()

        # Wait for cue time and present fixation cross again when ready
        ct = waitAndFlip(t0 + d1 + 0.1) - t0 - d1

        # Draw target
        self.visTarget[condition.tloc+condition.tdir+condition.flank].draw()
        if self.original:
            self.visFix.draw()

        # Wait for 2nd fixation time and Present target when ready
        d2 = waitAndFlip(t0 + d1 + 0.1 + 0.4) - t0 - d1 - ct

        # Discard any buffered events (we don't accept extremely fast reaction times here!)
        event.clearEvents(eventType='keyboard')

        # Wait for user response or timeout
        if self.runDummy:
            keys = event.waitKeys(maxWait = self.tDummy/1000.0-self.frameTime, timeStamped=self.clock)
        else:
            keys = event.waitKeys(maxWait = self.tOut/1000.0-self.frameTime, timeStamped=self.clock)
        if keys is not None:
            print("Got %s at %s expecting %s" % (keys[0][0], keys[0][1], condition.tdir))
            if keys[0][0] == 'escape':
                quit = True
                resp = 'QUIT'
            elif keys[0][0] == '0':
                core.wait(100)
            elif ((keys[0][0] == ('%s' % condition.tdir)) or
                  (keys[0][0] in ['f', 'a', 'z', 'q'] and condition.tdir=='left') or
                  (keys[0][0] in ['j', 'm', 'l', 'p'] and condition.tdir=='right')):
                resp = 'OK'
            else:
                resp = 'NOK'
        else:
            print("TIMEOUT")
            resp = None
        rt = self.clock.getTime() - t0 - d2 - ct - d1

        # 'Blank' the screen and wait until we're done with this trial (minus one final flip)
        if self.original:
            self.visFix.draw()
        self.win.flip()
        if self.original:
            self.visFix.draw()
        if not short:
            tf = waitAndFlip(t0 + 4.0) - t0
        else:
            tf = self.clock.getTime() - t0

        # print("At %0.3f/%0.3f [%s, %s, %s, %s]: d1=%0.3f, ct=%0.3f, d2=%0.3f, rt=%0.3f, tf=%0.3f, resp=%s" % 
        #         (self.startTime+t0, t0, condition.cue, condition.tloc, condition.tdir, condition.flank, d1, ct, d2, rt, tf, resp))

        if quit:
            return None
        else:
            return (Bunch(condition=condition, wt=self.startTime+t0, t0=t0, d1=d1, ct=ct, d2=d2, rt=rt, tf=tf, resp=resp))

    def practiceBlock(self, maxrun=24):
        """Run a practice block with maxrun=24 (no more than 48!) procedures"""
        for i in random.sample(xrange(len(self.procedures)), len(self.procedures)):
            res = self._oneProcedure(self.procedures[i], True)  # True is probably not as original experiment

            if res is None:
                return False

            self.win.flip()
            if res.resp=='OK':
                visual.TextStim(self.win, color='black', text="Correct reply (%0.3fs)" % (res.rt)).draw()
            elif res.resp=='NOK':
                visual.TextStim(self.win, color='red', text="Incorrect reply (%0.3fs)" % (res.rt)).draw()
            else:
                visual.TextStim(self.win, color='orange', text="No timely response recorded").draw()
            self.win.flip()
            core.wait(2)

            maxrun -= 1
            if maxrun==0:
                return True

    def fullExperiment(self, maxrun=None):
        """Run half of a real experiment in a random sequence (in total 48 target presentation)

        Use maxrun to limit the number of runs (mainly useful for testing)

        Returns a numpy array of (completed) procedures -- not in the order executed -- each row containing

            * the (clock referenced) starting time t0, 
            * the index of the experiment, 
            * the warning type [0-3] (none, center, double or spatial), 
            * the congruency [0-2] (congruent, incongruent, neutral),
            * the d1 timing (random waiting time before the cue, relative to t0)
            * the cue timing (should be around 100ms)
            * the time from cue to target (should be around 400ms)
            * the users response time (max 1.7s)
            * the total time until ready for next proceudre (should be around 4.0s)
            * 1 if the user replied correctly, 0 otherwise
            * 1 indicating a completed experiment; should always be 1 in the returned array

        """
        expData = np.zeros((len(self.procedures), 11))

        def c2s(condition, sep=';'):
            return "%s%s%s%s%s%s%s" % (condition.cue, sep, condition.tloc, sep, condition.tdir, sep, condition.flank)

        for i in random.sample(xrange(len(self.procedures)), len(self.procedures)):
            res = self._oneProcedure(self.procedures[i])
            if res is None:
                return None

            if self.logfile:
                self.logfile.write("%0.3f;%0.3f;%s;%0.3f;%0.3f;%0.3f;%0.3f;%0.3f;%s\n" %
                    (res.wt, res.t0, c2s(res.condition), res.d1, res.ct, res.d2, res.rt, res.tf, res.resp))
            else:
                print("%0.3f;%0.3f;%s;%0.3f;%0.3f;%0.3f;%0.3f;%0.3f;%s" %
                    (res.wt, res.t0, c2s(res.condition), res.d1, res.ct, res.d2, res.rt, res.tf, res.resp))

            cond = self.procedures[i]

            if cond.cue=='no':
                warningType = 0
            elif cond.cue=='center':
                warningType = 1
            elif cond.cue=='double':
                warningType = 2
            elif cond.cue=='spatial':
                warningType = 3
            else:
                sys.stderr.write("ERROR: Unknown cue '%s' in experiment. Programming error. Halting execution.\n" % cond.cue)

            if cond.flank=='congruent':
                congruency = 0
            elif cond.flank=='incongruent':
                congruency = 1
            elif cond.flank=='neutral':
                congruency = 2
            else:
                sys.stderr.write("ERROR: Unknown flank '%s' in experiment. Programming error. Halting execution.\n" % cond.flank)

            expData[i] = (res.t0, i, warningType, congruency, res.d1, res.ct, res.d2, res.rt, res.tf, 1 if res.resp=='OK' else 0, 1)

            if maxrun is not None:
                maxrun -= 1
                if maxrun==0:
                    break

        return expData[expData[:,10]==1]

    # The following text is adapted from the original (Visual Basic?) experiment
    # For the validity of the rule of thumb, see
    #    Robert P O'Shea: "Thumb's rule tested: visual angle of thumb's width is about 2 deg."
    #    Perception June 1991 vol. 20 no. 3 415-418 (doi: 10.1068/p200415)

    _instructions1 = 'This is an experiment investigating attention.  You will be shown ' + \
        'an arrow on the screen pointing either to the left or to the right, ' + \
        'for example -> or <- .  On some trials, the arrow will be flanked ' + \
        'by two arrows to the left and two arrows to the right. Examples might be:\n' + \
        '\n' + \
        '                                           ->->->->->\n' + \
        '\n' + \
        '                                           ->-><-->->\n' + \
        '\n' + \
        'Your task is to respond to the direction of the CENTRAL arrow.  You ' + \
        'should press either "z", "a", "q", "f" or the left arrow your left finger if the ' + \
        'central arrow points to the left or press the "m", "l", "p", "j" or right arrow ' + \
        'with your right finger if the central arrow points to the right. Place ' + \
        'your fingers on the keys you decide to use and keep them in position.\n' + \
        '\n' + \
        'Please place your eyes approx 60 cm from the screen. ' + \
        'The line to the right should be approx 2.1 cm long and appear as 2 deg of visual angle ' + \
        '(often the width of your thumb at an arms length is be 2 deg wide).\n' + \
        '\n' + \
        'Please make your response as quickly and accurately as possible. ' + \
        'Your reaction time and accuracy will be recorded.\n' + \
        '\n' + \
        'There will be a cross + in the center of the screen and the arrows ' + \
        'will appear either above or below the cross.  You should try to ' + \
        'fixate on the cross throughout the experiment.\n' + \
        '\n' + \
        'On some trials there will be asterisk cues indicating when or where ' + \
        'the arrow will occur.  If the cue is at the center or both above ' + \
        'and below fixation it indicates that the arrow will appear shortly. ' + \
        'If the cue is only above or below fixation it indicates both that ' + \
        'the trial will occur shortly and where it will occur.  Try to ' + \
        'maintain fixation at all times.  However, you may attend when and ' + \
        'where indicated by the cues.\n' + \
        '\n' + \
        'Press any key to go to the next page.'

    _instructions2 = 'The experiment contains four blocks. The first block is for practice ' + \
        'and takes about two minutes. ' + \
        '\n' + \
        'The other three blocks are experimental blocks and each takes about ' + \
        'five minutes.  After each block there will be a message "take a ' + \
        'break" and you may take a short rest.  After it, you can press the ' + \
        'space bar to begin the next block.\n' + \
        '\n' + \
        'The whole experiment takes about twenty minutes.\n' + \
        '\n' + \
        'Hitting the "escape" key will abort the experiment.\n' + \
        '\n' + \
        'If you have any question, please ask the experimenter.\n' + \
        '\n' + \
        'Press any key to start the practice session or hit the "escape" key to go directly to the experiment.'

    def displayText(self, text, showLine=True, noWait=False, time=2):
        """Display some text and wait for the user to hit a key

        noWait can be True, in which case the text is displayed for time seconds
        showLine can be False if you don't want the 2 deg line next to the text

        Returns True if the user hit 'escape' (presumably to abort/interrupt the run)
        """
        self.win.flip()
        visual.TextStim(self.win, alignHoriz='center', wrapWidth=12, height=0.01, color='black', text=text).draw()
        if showLine:
            visual.Line(self.win, start=(-7,-1), end=(-7,1), lineColor='black').draw()
            visual.Line(self.win, start=(-7.1,-1), end=(-6.9,-1), lineColor='black').draw()
            visual.Line(self.win, start=(-7.1,1), end=(-6.9,1), lineColor='black').draw()
        self.win.flip()
        if noWait:
            core.wait(time)
            self.win.flip()
            return False
        else:
            keys = event.waitKeys()
            self.win.flip()
            return keys[0]=='escape'

    def displayInstructions(self):
        """Show instructions and wait for the user to be ready

        The 2 deg line next to the instructions can be used as a rough rule-of-thumb calibration

        Returns True if the user wishes to skip the practice session
        """
        if not self.displayText(self._instructions1):
            noPractice = self.displayText(self._instructions2)
        else:
            noPractice = True

        return noPractice
