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

from carbono.buffer_manager.work_manager import WorkManager
from carbono.buffer_manager.simple_manager import SimpleManager
from carbono.buffer_manager.dummy_manager import DummyManager

from carbono.utils import *

class BufferManagerFactory:

    def __init__(self, read_callback, job_callback=None):
        if job_callback:
            if available_processors() <= 2 and is_hyperthreading():
                self._manager = SimpleManager(read_callback, job_callback)
            else:
                self._manager = WorkManager(read_callback, job_callback)
        else:
            self._manager = DummyManager(read_callback)

    def start(self):
        self._manager.start()

    def join(self):
        self._manager.join()

    def put(self, data):
        self._manager.put(data)

    def stop(self):
        self._manager.stop()

    @property
    def output_buffer(self):
        return self._manager.output_buffer
