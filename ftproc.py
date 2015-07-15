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
import numpy as np

# fish_tracker packages
from ftlib import *

# parse the script's arguments
parser = argparse.ArgumentParser()
parser.add_argument("-x", "--xscale", type=float, help="X scale factor",                   default=1.0)
parser.add_argument("-y", "--yscale", type=float, help="Y scale factor",                   default=1.0)
parser.add_argument("-H", "--hshift", type=float, help="Horizontal shift (after scaling)", default=0.0)
parser.add_argument("-V", "--vshift", type=float, help="Vertical shift (after scaling)",   default=0.0)
parser.add_argument("prj",            type=str,   help="project file.")
args = parser.parse_args()

# get the project data
prj = Project(args.prj)

# read the RAW data
raw = read_data(prj.get_raw_fname())

# get the mask coordinates
(mx, my, mw, mh) = prj.get("mask")

XX = mx
YY = my + mh

# process the raw data
raw[:, 2] = ((raw[:, 2] - XX) * args.xscale) + args.hshift   # scale and shift the X coord
raw[:, 4] = ((raw[:, 4] - XX) * args.xscale) + args.hshift   # scale and shift the X coord
raw[:, 6] = ((raw[:, 6] - XX) * args.xscale) + args.hshift   # scale and shift the X coord

raw[:, 3] = ((YY - raw[:, 3]) * args.yscale) + args.vshift   # scale, swap and shift the Y coords
raw[:, 5] = ((YY - raw[:, 5]) * args.yscale) + args.vshift   # scale, swap and shift the Y coords
raw[:, 7] = ((YY - raw[:, 7]) * args.yscale) + args.vshift   # scale, swap and shift the Y coords

# compute the angles
thetas = -np.degrees(np.arctan2(raw[:, 5] - raw[:, 3], raw[:, 4] - raw[:, 2]))

sys.stdout.write("Writing dat file >   0%")
sys.stdout.flush()

fdat = open(prj.get_dat_fname(), "w")
for (i, (row, theta)) in enumerate(zip(raw, thetas)):
    # output something nice to the terminal
    sys.stdout.write("%s%3d%%" % ("\b\b\b\b", int(float(i) / len(raw) * 100)))
    sys.stdout.flush()

    if row[1] == 0:
        # if the row has no data fill up with zeros
        fdat.write("%d\t0\t0\t0\t0\t0\t0\t0\t0\n" % row[0])
    else:
        row1 = map(lambda x: "%d" % int(x), row[:2])
        row2 = map(lambda x: "%5.2f" % x, row[2:])
        fdat.write("%s\t%5.2f\n" % ("\t".join(row1 + row2), theta))
fdat.close()

sys.stdout.write("\b\b\b\b100%\nDONE\n")
