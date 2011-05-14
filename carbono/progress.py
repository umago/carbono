#!/usr/bin/python
# coding: utf-8
# Copyright (C) 2010 Lucas Alvares Gomes <lucasagomes@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

import sys
import time
from threading import Thread

class Progress(Thread):
    def __init__(self, max):
        Thread.__init__(self)
        self.max = max
        self.current = 0
        self.percent = 0
        self.active = False

    def run(self):
        """ """
        self.active = True
        print "\nprocessing ..."
        while self.active:
            sys.stdout.write("%d%%\n\x1b[1A" % self.percent)
            time.sleep(0.5)

    def stop(self):
        """ """
        self.active = False

    def increment(self, amount):
        """ """
        self.current += amount
        self.percent = (self.current/float(self.max)) * 100

