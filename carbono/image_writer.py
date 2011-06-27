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

from carbono.utils import *
from carbono.config import *

class ImageWriter(Thread):
    def __init__(self, buffer, pattern,
                 total_blocks, split_size,
                 notify_callback):
        Thread.__init__(self)
        self.buffer = buffer
        self.pattern = pattern
        self.total_blocks = total_blocks
        self.split_size = split_size
        self.notify_status = notify_callback

        self.timer = Timer(self.notify_percent)
        self.volumes = 1
        self.processed_blocks = 0
        self.current_percent = -1
        self.active = False

    def notify_percent(self):
        percent = (self.processed_blocks/float(self.total_blocks)) * 100
        if percent > self.current_percent:
            self.current_percent = percent
            self.notify_status("progress", {"percent": percent})

    def run(self):
        self.active = True
        self.timer.start()

        total_written = 0
        while self.active:
            file_path = self.pattern.format(volume=self.volumes)

            fd = open(file_path, "wb")

            while self.active:
                data = self.buffer.get()
                if data == EOF:
                    self.stop()
                    break
                fd.write(data)
                bytes_written = len(data)
                total_written += bytes_written
                self.processed_blocks += 1

                if self.split_size:
                    if (total_written + bytes_written) >= self.split_size:
                        self.volumes += 1
                        break

            fd.close()

    def stop(self):
        self.active = False
        self.timer.stop()
