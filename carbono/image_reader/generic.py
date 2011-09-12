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

import os

from carbono.config import *
from carbono.utils import *

class GenericReader:

    def __init__(self, image_path, pattern, volumes, notify_status):
        self.image_path = image_path
        self.pattern = pattern
        self.volumes = volumes
        self.current_volume = 1
        self.notify_callback = notify_status
        self._fd = None
        self.open()

    def _check_fd(self):
        return self._fd is None or self._fd.closed

    def open(self):
        if self._check_fd():
            file_pattern = self.pattern.format(volume=self.current_volume)

            # Loop untill find the the next slice or
            # cancel the operation
            while True:
                file_path = self.image_path + file_pattern
                if os.path.exists(file_path):
                    self._fd = open(file_path, 'rb')
                else:
                    self.image_path = self.notify_callback("file_not_found",
                    {"path": self.image_path, "file": file_pattern})

                    if self.image_path:
                        self.image_path = adjust_path(self.image_path)
                        continue
                    else:
                        self.notify_callback("canceled",
                                            {"operation": "Restoring image"})
                break

    def close(self):
        if not self._check_fd():
            self._fd.close()

    def read_block(self):
        if not self._check_fd():
            data = self._fd.read(BLOCK_SIZE)
            if not len(data):
                self.close()
                if self.current_volume < self.volumes:
                    self.current_volume += 1
                    self.open()
                    data = self.read_block()
                else:
                    return None
            return data
