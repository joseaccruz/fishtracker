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
import os
import sys

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.ticker import NullFormatter

from ftlib import *

WND_SIZE = 1
WND_WEIGHT = 1

SURF_WIDTH = 100
SURF_HEIGHT = 100


def shiftZero_old(data):
    return data - np.min(data)


def normalize(data, scale=1.0):
    min_data = float(np.min(data))
    max_data = float(np.max(data))

    return((data - min_data) / (max_data - min_data)  * float(scale))


def polar(data, show, fname):
    angs = data[:, 8]

    step = np.pi / 180.0
    theta = np.arange(0, 2 * np.pi + step, step)
    theta_hist = np.zeros(361)

    for a in angs:
        if(a < 0):
            a = 360 + a
        theta_hist[a] += 1

    # force square figure and square axes looks better for polar, IMO
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8], polar=True)
    ax.set_theta_zero_location("W")
    ax.set_theta_direction(-1)
    ax.plot(theta, theta_hist)
    fig.savefig(fname)

    if show:
        plt.show()


def surface(xs, ys):
    xsize = np.max(xs) - np.min(xs)
    ysize = np.max(ys) - np.min(ys)

    img_size = max(xsize, ysize) + 1  # we want the surface to be square (!!)

    img = np.zeros((img_size, img_size), dtype=np.float64)

    for (x, y) in zip(xs, ys):
        if(WND_SIZE > 0):
            img[y - WND_SIZE:y + WND_SIZE, x - WND_SIZE:x + WND_SIZE] += WND_WEIGHT
        else:
            img[y, x] += WND_WEIGHT

    return(normalize(img, scale=255.0))


def scatter(xs, ys, show, fname):
    img = surface(xs, ys)

    nullfmt   = NullFormatter()         # no labels

    # definitions for the axes
    left, width = 0.1, 0.65
    bottom, height = 0.1, 0.65
    bottom_h = left_h = left + width + 0.02

    rect_scatter = [left, bottom, width, height]
    rect_histx = [left, bottom_h, width, 0.2]
    rect_histy = [left_h, bottom, 0.2, height]

    # start with a square Figure
    fig = plt.figure(figsize=(8, 8))

    axScatter = plt.axes(rect_scatter)
    axHistx = plt.axes(rect_histx)
    axHisty = plt.axes(rect_histy)

    # no labels
    axHistx.xaxis.set_major_formatter(nullfmt)
    axHisty.yaxis.set_major_formatter(nullfmt)

    # the scatter plot:
    axScatter.imshow(img, cmap=cm.jet)

    # now determine nice limits by hand:
    binwidth = 5

    axScatter.set_xlim((1.0, np.size(img, 0)))
    axScatter.set_ylim((1.0, np.size(img, 1)))

    axHistx.hist(xs, bins=np.arange(np.min(xs), np.max(xs) + binwidth, binwidth))
    axHisty.hist(ys, bins=np.arange(np.min(ys), np.max(ys) + binwidth, binwidth), orientation='horizontal')

    axHistx.set_xlim(axScatter.get_xlim())
    axHisty.set_ylim(axScatter.get_ylim())
    fig.savefig(fname)

    if show:
        plt.show()


#
# Main
#

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--show", action="store_true", help="Do not show the graphics while saving.")
parser.add_argument("prj",            type=str, help="project file.")
args = parser.parse_args()

# get the project data
prj = Project(args.prj)

# read data
dat = read_data(prj.get_dat_fname())

count_rows = float(len(dat))

dat = np.array(filter(lambda d: d[1] == 1, dat), dtype=np.float64)
count_valid = float(len(dat))

sys.stdout.write("Total rows in file: %d.\n" % count_rows)
sys.stdout.write("Valid rows in file: %d (%.1f%%).\n" % (count_valid, (count_valid / count_rows) * 100.0))

(xs, ys) = (dat[:, 4], dat[:, 5])

fscatter = args.prj + ".plt_heat.svg"
fpolar   = args.prj + ".plt_polar.svg"

scatter(xs, ys, args.show, fscatter)
polar(dat, args.show, fpolar)
