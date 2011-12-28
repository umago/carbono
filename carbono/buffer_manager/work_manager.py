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

import time
import Queue
from multiprocessing import Process, Manager, Event
from multiprocessing.managers import BaseManager
from threading import Thread
from copy import deepcopy

from carbono.buffer_manager.reorder_buffer import ReoderBuffer
from carbono.utils import *
from carbono.config import *
from carbono.exception import *

class Worker(Process):
    def __init__(self, buffer, reorder_buffer, job):
        Process.__init__(self)
        self.buffer = buffer
        self.reorder_buffer = reorder_buffer
        self.job = job
        self.event = Event()

    def run(self):
        self.event.set()
        while self.event.is_set():
            try:
                block_number, data = self.buffer.get()
            except IOError, e:
                if e.errno == errno.EINTR:
                    data = EOF

            if data == EOF:
                self.stop()
                break
            worked_data = self.job(data)

            while self.event.is_set():
                try:
                    self.reorder_buffer.put(block_number, worked_data)
                    break
                except IndexError:
                    # Block num bigger than expected,
                    # wait untill ReorderBuffer start
                    # processing blocks in this range
                    time.sleep(0.1)
                except IOError, e:
                    if e.errno == errno.EINTR:
                        self.stop()

    def stop(self):
        self.event.clear()
        try:
            self.terminate()
        except AttributeError:
            pass


class WorkManager(Thread):
    def __init__(self, read_callback, job_callback):
        Thread.__init__(self)
        self.read_block = read_callback
        self.job = job_callback

        self.manager = Manager()
        self.num_cores = available_processors()
        self._block_number = 0
        self._worker_list = list()
        self.active = False

        self._setup()
        self._start_workers()

    def _setup(self):
        free_phy_mem = available_memory(percent=35)
        maxsize = int(free_phy_mem / BLOCK_SIZE)
        self._input_buffer = self.manager.Queue(maxsize)
        self.output_buffer = self.manager.Queue(maxsize)

        BaseManager.register("ReoderBuffer", ReoderBuffer)
        bm = BaseManager()
        bm.start()
        self.reorder_buffer = bm.ReoderBuffer(self.output_buffer, 50)

    def _start_workers(self):
        for cpu in xrange(self.num_cores):
            worker = Worker(self._input_buffer, 
                            self.reorder_buffer,
                            self.job)
            worker.start()
            self._worker_list.append(worker)

    def run(self):
        self.active = True
        while self.active:
            try:
                data = self.read_block()
            except ErrorReadingFromDevice, e:
                self.stop()
                raise e
                
            if not data:
                self._finish()
                break
            self.put(data)

    def put(self, data):
        while self.active:
            try:
                self._input_buffer.put((deepcopy(self._block_number), data),
                                       timeout=1)
            except Queue.Full:
                continue
            self._block_number += 1
            break

    def _finish(self):
        self.active = False

        for worker in self._worker_list:
            self._input_buffer.put((EOF, EOF))

        for worker in self._worker_list:
            try:
                worker.join()
            except AssertionError:
                pass

        self.reorder_buffer.sync()
        self.output_buffer.put(EOF)
        
    def stop(self):
        self.active = False

        for worker in self._worker_list:
            worker.stop()

        for worker in self._worker_list:
            try:
                worker.join()
            except AssertionError:
                pass
