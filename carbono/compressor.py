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

import struct
import zlib

from carbono.exception import *

class Compressor:

    def __init__(self, level=6):
        if level < 1 or level > 9:
            raise InvalidCompressorLevel("Invalid range, " + \
                    "the range must be an integer from 1 to 9")

        self.level = level
        self.header = "<I"

    def get_header_size(self):
        return struct.calcsize(self.header)

    def compact(self, data):
        compressed_data = zlib.compress(data, self.level)
        header = struct.pack(self.header, len(compressed_data))
        final_data = header + compressed_data
        return final_data
    
    def extract(self, data):
        return zlib.decompress(data)
    
    def read_block_header(self, data):
        length = struct.unpack(self.header, data)[0]
        return length
