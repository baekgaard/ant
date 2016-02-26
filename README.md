# ANT (Attention Network Test) 

This module implements the ANT (Attention Network Test) in PsychoPy2

## Use

To use this class, do something like the following:


    from ant import ANTExp # or some such

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

    # do something with allData (or use the logfiles, that log ;-separated experimental data)

There is a working example in the testant.py file.


For a full description of the original experiment, see:

    Jin Fan, Bruce D. McCandliss, Tobias Sommer, Amir Raz, and Michael I. Posner:
    "Testing the Efficiency and Independence of Attentional Networks"
    Journal of Cognitive Neuroscience 14:3, pp. 340-347 (2002)

## Quoting

If you use this for your research, I would appreciate either a citation to this article:

    Bækgaard, Per, Michael Kai Petersen, and Jakob Eg Larsen.
    "Assessing Levels of Attention using Low Cost Eye Tracking"
    (To appear in proceedings from the Human Computer Interaction International 2016 by Springer).

which is currently available as a preprint:

    Bækgaard, Per, Michael Kai Petersen, and Jakob Eg Larsen. 
    "Assessing Levels of Attention using Low Cost Eye Tracking." 
    arXiv preprint arXiv:1512.05497 (2015).

or a reference to the GitHub repository

    https://github.com/baekgaard/ant


## Licence

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
