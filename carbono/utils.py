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

from os.path import realpath

def run_command(cmd):
    """  """
    p = subprocess.Popen(cmd, shell=True,
                         stdout=subprocess.PIPE,
                         stdin=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    p.wait()
    return p.returncode

def make_temp_dir():
    """ """
    return tempfile.mkdtemp()

def adjust_path(path):
    """ """
    path = realpath(path)
    if not path[-1] == '/':
        path += '/'
    return path

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

def get_available_processors():
    return multiprocessing.cpu_count()

