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

from carbono.config import *

class GenericReader:

    def __init__(self, path):
        self.path = path
        self._fd = None

    def __iter__(self):
        return self

    def _check_fd(self):
        return self._fd is None or self._fd.closed

    def open(self):
        if self._check_fd():
            self._fd = open(self.path, 'rb')

    def close(self):
        if not self._check_fd():
            self._fd.close()

    def next(self):
        self.open()
        if not self._check_fd():
            data = self._fd.read(BLOCK_SIZE)
            if not len(data):
                self.close()
                raise StopIteration
            return data
