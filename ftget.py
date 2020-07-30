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

# python standard library
import argparse
import sys

# 3rd party packages
import cv2
import numpy as np

# fish_tracker packages
from ftlib import *

# parse the script's arguments
parser = argparse.ArgumentParser()
parser.add_argument("-s", "--show",  action="store_true", help="show the video while processing.")
parser.add_argument("-d", "--delay", type=int,            help="set the delay between frames (ms)", default=1)
parser.add_argument("video",         type=str,            help="input video file")
parser.add_argument("prj",           type=str,            help="project info file")
parser.add_argument("mask",          type=str,            help="mask coords (<left>x<top>:<width>x<height>)")
parser.add_argument("lumth",         type=int,            help="Luminosity threshold (ex. 200)")
args = parser.parse_args()

# open the video file
capture = cv2.VideoCapture(args.video)
frame_height = capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
frame_width  = capture.get(cv2.CAP_PROP_FRAME_WIDTH)
frame_count  = capture.get(cv2.CAP_PROP_FRAME_COUNT)

# create the square mask
(mx, my, mw, mh) = parse_mask(args.mask)
mask = np.uint8(np.zeros((int(frame_height), int(frame_width))))
mask[my:my + mh, mx:mx + mw] = 255

# create the project file
prj = Project()
prj.set("video", args.video)
prj.set("mask", (mx, my, mw, mh))
prj.set("lumth", args.lumth)
prj.save(args.prj)

# open the raw data file
fraw = open(prj.get_raw_fname(), "w")

# start the counter
tcount = TimeCount(frame_count)

if args.show:
    sys.stderr.write("\nPress 'Q' or 'q' to terminate.\n")

last_head = None
last_tail = None

f = -1
while True:
    f += 1

    (ret, frame) = capture.read()

    if(not ret):
        break

    if(f % 100 == 0):
        tcount.show(f)

    hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
    [hue, sat, lum] = cv2.split(hsv)

    (ret, lum_bin) = cv2.threshold(lum, args.lumth, 255, cv2.THRESH_BINARY_INV)

    lum_bin = np.bitwise_and(lum_bin, mask)

    if args.show:
        cv2.imshow("binary", lum_bin)

    (blobs, dummy) = cv2.findContours(lum_bin, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    blobs = sorted(blobs, key=lambda x: -len(x))

    body_length = 0
    txt = ""

    if (len(blobs) > 0) and (np.size(blobs[0]) > 100):
        blob = blobs[0]

        small_mask = np.uint8(np.ones(np.shape(frame)[:2])) * 0
        cv2.fillConvexPoly(small_mask, blob, 255)

        moments = cv2.moments(small_mask)
        centroid = (int(moments['m10'] / moments['m00']), int(moments['m01'] / moments['m00']))

        dists = list(map(lambda p: lindist(p[0], centroid), blob))
        tail = tuple(blob[dists.index(max(dists))][0])

        dists = list(map(lambda p: lindist(p[0], tail), blob))
        head = tuple(blob[dists.index(max(dists))][0])

        # doesn't consider when the fish touches the limits
        if(check_inside(head[0], mx, mw) and check_inside(head[1], my, mh) and check_inside(tail[0], mx, mw) and check_inside(tail[1], my, mh)):
            body_angle = angle(head, centroid, tail)

            # swap the head and the tail when needed
            if (last_head is not None) and (lindist(head, last_head) > lindist(head, last_tail)) and (body_angle > 20):
                (head, tail) = (tail, head)

        txt = "%d\t1\t%d\t%d\t%d\t%d\t%d\t%d\n" % (f, head[0], head[1], centroid[0], centroid[1], tail[0], tail[1])

        # store the head and tail for the next frame
        last_head = head
        last_tail = tail

    if args.show:
        cv2.putText(frame, "%d" % f, (0, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255))
        cv2.rectangle(frame, (mx, my), (mx + mw, my + mh), (0, 0, 255), 1)
        cv2.putText(frame, "%dx%d:%dx%d (%d)" % (mx, my, mw, mh, args.lumth), (mx, my+20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255))

        if(txt == ""):
            cv2.line(frame, (mx, my), (mx + mw, my + mh), (0, 255, 0), 1)
            cv2.line(frame, (mx, my + mh), (mx + mw, my), (0, 255, 0), 1)
        else:
            cv2.circle(frame, centroid, 2, (0, 255, 0), -1)
            cv2.circle(frame, tail, 2, (255, 0, 0), -1)
            cv2.circle(frame, head, 2, (0, 0, 255), -1)
            cv2.line(frame, centroid, head, (0, 255, 0), 1)

    if txt == "":
        last_head = None
        last_tail = None
        txt = "%d\t0\t0\t0\t0\t0\t0\t0\n" % f

    fraw.write(txt)
    fraw.flush()

    if args.show:
        cv2.imshow("video", frame)
        key = cv2.waitKey(args.delay)

        if key > 0:
            if key in QUIT_KEYS:
                sys.stderr.write("\n\nFinal parameters: %dx%d:%dx%d %d\n" % (mx, my, mw, mh, args.lumth))
                break

            if key in [LUMTH_UP, LUMTH_DOWN]:
                args.lumth = max(0, args.lumth - 1) if key == LUMTH_DOWN else min(args.lumth + 1, 255)

            if key in MOVE_SQUARE_KEYS.keys():
                mx += MOVE_SQUARE_KEYS[key][0]
                my += MOVE_SQUARE_KEYS[key][1]
                mw += MOVE_SQUARE_KEYS[key][2]
                mh += MOVE_SQUARE_KEYS[key][3]

                mask[:, :] = 0
                mask[my:my + mh, mx:mx + mw] = 255

fraw.close()
sys.stderr.write("\nDONE\n")
