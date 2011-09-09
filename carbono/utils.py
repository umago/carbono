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

import subprocess
import tempfile
import multiprocessing
import random

from threading import Thread, Event
from os.path import realpath

class Timer(Thread):
    def __init__(self, callback, timeout=2):
        Thread.__init__(self)
        self.callback = callback
        self.timeout = timeout
        self.event = Event()

    def run(self):
        while not self.event.is_set():
            self.callback()
            self.event.wait(self.timeout)

    def stop(self):
        self.event.set()


class RunCmd:
    def __init__(self, cmd):
        self.cmd = cmd
        self.stdout = None
        self.stdin = None
        self.stderr = None

    def run(self):
        self.process = subprocess.Popen(self.cmd, shell=True,
                                        stdout=subprocess.PIPE,
                                        stdin=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
        self.stdout = self.process.stdout
        self.stdin = self.process.stdin
        self.stderr = self.process.stderr

    def wait(self):
        if hasattr(self, "process"):
            self.process.wait()
            return self.process.returncode

    def stop(self):
        if hasattr(self, "process"):
            try:
                self.process.kill()
            except OSError, e:
                if e.errno == errno.ESRCH:
                    pass


def run_simple_command(cmd):
    """  """
    p = subprocess.Popen(cmd, shell=True,
                         stdout=subprocess.PIPE,
                         stdin=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    p.wait()
    return p.returncode

def random_string(length=5):
    return ''.join([random.choice(tempfile._RandomNameSequence.characters) for i in range(length)])

def adjust_path(path):
    """ """
    path = realpath(path)
    if not path[-1] == '/':
        path += '/'
    return path

def make_temp_dir():
    """ """
    return adjust_path(tempfile.mkdtemp())

def get_parent_path(path):
    num = -1
    while True:
        try:
            int(path[num])
            num -= 1
        except ValueError:
            return path[:num+1]

def singleton(cls):
    instance_list = list()
    def getinstance():
        if not len(instance_list):
            instance_list.append(cls())
        return instance_list[0]
    return getinstance

def available_processors():
    return multiprocessing.cpu_count()

def available_memory(percent=100):
    free = 0
    with open("/proc/meminfo", 'r') as f:
        for line in f:
            if line.startswith("MemFree:"):
                free = int(line.split()[1]) * 1024
                break

    if percent < 100:
        free = (free * percent) / 100

    return free

def get_cdrom_device():
    device = None
    with open("/proc/sys/dev/cdrom/info", 'r') as f:
        for line in f:
            if line.startswith("drive name:"):
                try:
                    device = "/dev/" + line.split()[2]
                except IndexError:
                    break
    return device

