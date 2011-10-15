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

from carbono.image_reader.generic import GenericReader
from carbono.image_reader.compressed import CompressedReader

class ImageReaderFactory:

    def __init__(self, image_path, pattern, volumes,
                 compressor_level, notify_status):
        if compressor_level:
            self._reader = CompressedReader(image_path, pattern, volumes,
                                            compressor_level, notify_status)
        else:
            self._reader = GenericReader(image_path, pattern,
                                         volumes, notify_status)

    def read_block(self):
        return self._reader.read_block()

    def open(self):
        self._reader.open()
