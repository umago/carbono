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

from carbono.writer.generic import GenericWriter
from carbono.writer.compressed import CompressedWriter

class WriterFactory:

    def __init__(self, path, compressor_level):
        if compressor_level:
            self._writer = CompressedWriter(path, compressor_level)
        else:
            self._writer = GenericWriter(path)

    def open(self):
        self._writer.open()

    def close(self):
        self._writer.open()

    def write(self, data):
        self._writer.write(data)
