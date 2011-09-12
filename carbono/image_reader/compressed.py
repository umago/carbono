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

from carbono.compressor import Compressor
from carbono.image_reader.generic import GenericReader

class CompressedReader(GenericReader):

    def __init__(self, image_path, pattern, volumes,
                 compressor_level, notify_status):
        GenericReader.__init__(self, image_path, pattern,
                               volumes, notify_status)
        self.compressor = Compressor(compressor_level)

    def read_block(self):
        header_size = self.compressor.get_header_size()
        if not self._check_fd():
            header = self._fd.read(header_size)
            if not len(header):
                self.close()
                if self.current_volume < self.volumes:
                    self.current_volume += 1
                    self.open()
                    data = self.read_block()
                    return data
                else:
                    return None
            size = self.compressor.read_block_header(header)
            data = self._fd.read(size)
            return data
