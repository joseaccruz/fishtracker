#!/usr/bin/env python

#
# Fish Tracker
#
# Copyright (c) 2015, Rodrigo Abreu, Jose Cruz & Rui Oliveira
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

import argparse
import sys
import os

import cv2

from ftlib import *


#
# MAIN
#

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--delay", type=int, help="set the delay between frames (ms)", default=1)
parser.add_argument("-j", "--jump",  type=int, help="Jump to a specific frame", default=0)
parser.add_argument("prj",           type=str, help="project file.")
args = parser.parse_args()


# get the project data
prj = Project(args.prj)

#
# checks the presence of all needed files
#
if not os.path.isfile(prj.get("video")):
    sys.stderr.write("\nVideo file '%s' not found.\n" % prj.get("video"))
    sys.exit(1)

# read data
raw = read_data(prj.get_raw_fname())
dat = read_data(prj.get_dat_fname())

if(len(raw) != len(dat)):
    sys.stderr.write("\nRaw and processed data have different lengths.\n")
    sys.exit(1)

# get the mask coordinates
(mx, my, mw, mh) = prj.get("mask")

# start capture
capture = cv2.VideoCapture(prj.get("video"))
frame_height  = int(capture.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))

if args.jump > 0:
    capture.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, args.jump)

lifo = []

f = args.jump
while f < len(raw):
    draw = raw[f]
    ddat = dat[f]

    f += 1

    (ret, frame) = capture.read()

    #K = 200.0
    #for i in xrange(int(K)):
    #    if f - i <= 0:
    #        break
    #
    #    praw = map(int, data_raw[f - i])

    if(f == 1):
        sys.stderr.write("\nPress 'Q' or 'q' to terminate.\n")

    if(int(draw[1]) == 1):
        draw = map(int,   draw)
        ddat = map(float, ddat)

        # compute theta
        cv2.circle(frame, tuple(draw[2:4]), 3, (0, 0, 255), -1)
        cv2.circle(frame, tuple(draw[4:6]), 3, (0, 255, 0), -1)
        cv2.circle(frame, tuple(draw[6:8]), 3, (255, 0, 0), -1)
        cv2.line(frame, tuple(draw[2:4]), tuple(draw[4:6]), (255, 255, 255), 1)
        cv2.line(frame, tuple(draw[4:6]), tuple(draw[6:8]), (255, 255, 255), 1)

        cv2.putText(frame, "%5.2f" % ddat[8], tuple(draw[2:4]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0))
        cv2.putText(frame, "raw: %3d x %3d"     % (draw[4], draw[5]), (mx, my+20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255))
        cv2.putText(frame, "dat: %5.2f x %5.2f" % (ddat[4], ddat[5]), (mx, my+40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255))
    else:
        cv2.putText(frame, "NO FISH", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 0, 0))

    cv2.putText(frame, "%d" % f, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255))

    cv2.line(frame, (mx, my), (mx + mw, my), (255, 0, 255), 2)
    cv2.line(frame, (mx + mw, my), (mx + mw, my + mh), (255, 0, 255), 2)
    cv2.line(frame, (mx + mw, my + mh), (mx, my + mh), (255, 0, 255), 2)
    cv2.line(frame, (mx, my + mh), (mx, my), (255, 0, 255), 2)

    cv2.imshow("Analyse", frame)
    key = cv2.waitKey(args.delay)

    if key in [113, 65617]:
        sys.stderr.write("\nTerminated by the user...\n")
        break

sys.stderr.write("\nDONE\n")
