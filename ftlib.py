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

import json
import os
import re
import sys
import time

import numpy as np


MOVE_SQUARE_KEYS = {
    65363:   (1, 0, 0, 0),      # move square left (arrow left)
    2555904: (1, 0, 0, 0),
    65361:   (-1, 0, 0, 0),     # move square right (arrow right)
    2424832: (-1, 0, 0, 0),
    65364:   (0, 1, 0, 0),      # move square up (arrow up)
    2621440: (0, 1, 0, 0),
    65362:   (0, -1, 0, 0),     # move square down (arrow down)
    2490368: (0, -1, 0, 0),
    119:     (0, 0, 1, 0),      # increase square width ("w" key)
    327507:  (0, 0, 1, 0),      # increase square width (CTRL + arrow right)
    65623:   (0, 0, -1, 0),     # increase square width (SHIFT + "w" key)
    327505:  (0, 0, -1, 0),     # decrease square width (CTRL + arrow left)
    104:     (0, 0, 0, 1),      # increase square height ("h" key)
    327508:  (0, 0, 0, 1),      # increase square height (CTRL + arrow down)
    65608:   (0, 0, 0, -1),     # decrease square height (SHIFT + "h" key)
    327506:  (0, 0, 0, -1)      # decrease square height (CTRL + arrow up)
}

QUIT_KEYS = [113, 65617]

LUMTH_UP = 108
LUMTH_DOWN = 65612

class TimeCount(object):
    def __init__(self, total):
        self._total = total
        self._start = time.time()

    def show(self, count):
        if count == 0:
            count += 1

        deltat = time.time() - self._start
        stept = deltat / float(count)
        finalt = float(self._total - count) * stept

        back = "\b" * 75

        deltats = time.strftime("%H:%M:%S", time.gmtime(deltat))
        finalts = time.strftime("%H:%M:%S", time.gmtime(finalt))

        sys.stderr.write("%sFrame: %5d/%5d (%5.2f%%), Ellap: %s, Expec: %s" % (back, count, self._total, (float(count) / float(self._total)) * 100.0, deltats, finalts))
        sys.stderr.flush()


class Project(object):
    def __init__(self, fname=None):
        if fname is None:
            self._fname = ""
            self._data = {}
        else:
            self.load(fname)

    def set(self, key, value):
        self._data[key] = value

    def get(self, key):
        return self._data.get(key, None)

    def get_raw_fname(self):
        return self._fname + ".raw"

    def get_dat_fname(self):
        return self._fname + ".dat"

    def save(self, fname):
        self._fname = fname

        open(fname, "w").write(json.dumps(self._data, indent=4))

    def load(self, fname):
        try:
            self._fname = fname
            self._data = json.loads(open(fname).read())

        except ValueError:
            sys.stderr.write("ERROR: Bad JSON file '%s'." % fname)
            sys.exit(1)

        except IOError:
            sys.stderr.write("ERROR: File not found '%s'." % fname)
            sys.exit(1)


def angle(p1, p2, p3):
    (u, v, w) = np.array(p1), np.array(p2), np.array(p3)

    u1 = (v - u) / np.linalg.norm(v - u)
    v1 = (w - v) / np.linalg.norm(w - v)
    return np.degrees(np.arccos(np.dot(u1, v1)))


def check_inside(c, f, t):
    return((c - f > 1) and (c - f < (t - 1)))


def lindist(p1, p2):
    return np.linalg.norm((p1[0] - p2[0], p1[1] - p2[1]))


def parse_mask(mask):
    pat = "^(\d+)x(\d+):(\d+)x(\d+)$"

    m = re.match(pat, mask)

    if m is None:
        sys.stderr.write("Invalid mask: '%s'\n" % mask)
        quit()

    return map(int, m.groups())


def read_data(fname):
    try:
        ret = np.array(map(lambda s: map(float, s.split("\t")), open(fname).read().strip().split("\n")))
    except IOError:
        sys.stderr.write("ERROR: File not found '%s'." % fname)
        sys.exit(1)

    return ret
