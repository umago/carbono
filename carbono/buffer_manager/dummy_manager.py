#!/usr/bin/python
# coding: utf-8
# Copyright (C) 2011 Lucas Alvares Gomes <lucasagomes@gmail.com>
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

from threading import Thread
from multiprocessing import Queue

from carbono.utils import *
from carbono.config import *

class DummyManager(Thread):

    def __init__(self, read_callback):
        Thread.__init__(self)
        self.read_block = read_callback
        self.active = False
        self._setup()

    def _setup(self):
        free_phy_mem = available_memory(percent=70)
        maxsize = int(free_phy_mem / BLOCK_SIZE) 
        self.output_buffer = Queue(maxsize)

    def put(self, data):
        self.output_buffer.put(data)

    def run(self):
        self.active = True
        while self.active:
            try:
                data = self.read_block()
            except ErrorReadingFromDevice, e:
                self.stop()
                raise e

            if not data:
                self.stop()
                break
            self.put(data)
        
    def stop(self):
        self.output_buffer.put(EOF)
        self.active = False

