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

import parted
import subprocess
from carbono.config import *
from carbono.exception import *

class Generic(parted.FileSystem):

    def __init__(self, path, type, geometry):
        parted.FileSystem.__init__(self, type, geometry)
        self.path = path
        self._fd = None

    def get_size(self):
        """ """
        return long(self.getSize('b'))

    def get_used_size(self):
        """ """
        return self.get_size()

    def open_to_read(self):
        """ """
        cmd = "dd if=%s bs=%s" % (self.path, DD_BLOCK_SIZE)
        try:
            self._fd = subprocess.Popen(cmd, shell=True,
                                        stdin=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        stdout=subprocess.PIPE).stdout
        except:
            raise ErrorOpenToRead("Cannot open %s to read" % self.path)

    def open_to_write(self):
        """ """
        cmd = "dd of=%s bs=%s" % (self.path, DD_BLOCK_SIZE)
        try:
            self._fd = subprocess.Popen(cmd, shell=True,
                                        stdin=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        stdout=subprocess.PIPE).stdin
        except:
            raise ErrorOpenToWrite("Cannot open %s to read" % self.path)

    def read(self, size):
        """ """
        if self._fd is None or \
           self._fd.closed:
            raise ErrorReadingFromDevice 
            
        return self._fd.read(size)

    def write(self, data):
        """  """
        if self._fd is None or \
           self._fd.closed:
            raise ErrorWritingToDevice

        self._fd.write(data)

    def close(self):
        """  """
        if self._fd is None or \
           self._fd.closed:
            return

        self._fd.close()

    def uuid(self):
        """  """
        return None

    def get_type(self):
        """ """
        return self.type

    def is_swap(self):
        """  """
        return False
