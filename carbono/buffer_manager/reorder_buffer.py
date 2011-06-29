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

import ctypes
from multiprocessing import Lock, Manager

class ReoderBuffer(object):
    def __init__(self, out_buffer, size=10):
        self.out_buffer = out_buffer
        self.size = size
        self._array = Manager().list(range(self.size))
        self._lock = Lock()
        self._min = 0
        self._max = self.size
        self._count = 0
        self.update_control()

    def update_control(self):
        self._control = dict()
        for e, i in enumerate(xrange(self._min, self._max)):
            self._control.update({i: e})

    def put(self, block_num, data):
        self._lock.acquire()
        if block_num not in self._control.keys():
            self._lock.release()
            raise IndexError
        self._array[self._control[block_num]] = data
        self._count += 1
        if self._count == self.size: self.sync()
        self._lock.release()

    def sync(self):
        for i in xrange(self._count):
            data = self._array[i]
            self.out_buffer.put(data)
        self._min += self._count
        self._max += self._count
        self._count = 0
        self.update_control()

