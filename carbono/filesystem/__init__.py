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

import errno

from carbono.filesystem.generic import Generic
from carbono.filesystem.ext import Ext
from carbono.filesystem.ntfs import Ntfs
from carbono.filesystem.btrfs import Btrfs
from carbono.filesystem.linux_swap import LinuxSwap
from carbono.exception import *

class FilesystemFactory:
    
    def __init__(self, path, type, geometry):
        self.type = type
        self.geometry = geometry
        self.path = path
        self._fs = self._get_filesystem_instance()

    def _get_filesystem_instance(self):
        """  """
        if self.type.startswith("ext"):
            fs_instance = Ext(self.path, self.type, self.geometry)

        elif self.type == "ntfs":
            fs_instance = Ntfs(self.path, self.type, self.geometry)

        elif self.type == "btrfs":
            fs_instance = Btrfs(self.path, self.type, self.geometry)

        elif self.type.startswith("linux-swap"):
            fs_instance = LinuxSwap(self.path, self.type, self.geometry)

        else:
            fs_instance = Generic(self.path, self.type, self.geometry)

        return fs_instance

    def open_to_read(self):
        self._fs.open_to_read()
    
    def open_to_write(self, uuid=None):
        if uuid is not None:
            self._fs.open_to_write(uuid)
        else:
            self._fs.open_to_write()

    def get_size(self):
        return self._fs.get_size()

    def get_used_size(self):
        return self._fs.get_used_size()

    def read_block(self):
        try:
            return self._fs.read_block()
        except IOError, e:
            if e.errno == errno.EPIPE:
                msg = "The application crashed when " +\
                       "reading from {0}".format(self.path)

            msg = self._append_debug(msg, e)
            raise ErrorReadingFromDevice(msg)

    def write_block(self, data):
        try:
            self._fs.write_block(data)
        except IOError, e:
            if e.errno == errno.EPIPE:
                msg = "The application crashed when " +\
                       "writing in {0}".format(self.path)

            msg = self._append_debug(msg, e)
            raise ErrorWritingToDevice(msg)

    def close(self):
        self._fs.close()

    def uuid(self):
        return self._fs.uuid()

    def is_swap(self):
        return self._fs.is_swap()

    def check(self):
        return self._fs.check()
        
    def mount(self):
        return self._fs.mount()

    def umount(self, dir=None):
        return self._fs.umount(dir)

    def fill_with_zeros(self):
        return self._fs.fill_with_zeros()

    def resize(self):
        return self._fs.resize()

    def stop(self):
        self._fs.stop()

    def read_label(self):
        return self._fs.read_label()

    def write_label(self, label):
        return self._fs.write_label(label)

    def _append_debug(self, msg, e):
        msg += "\n\n[DEBUG]"
        msg += "\nFilesystem type: {0}".format(self.type)
        msg += "\nDevice: {0}".format(self.path)
        msg += "\nOriginal error: {0}".format(e)
        return msg
