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

from carbono.filesystem.generic import Generic
from carbono.filesystem.ext3 import Ext3
from carbono.filesystem.ntfs import Ntfs
from carbono.filesystem.linux_swap import LinuxSwap

class FilesystemManager:
    
    def __init__(self, path, type, geometry):
        self.type = type
        self.geometry = geometry
        self.path = path
        self._fs = self._get_filesystem_instance()

    def _get_filesystem_instance(self):
        """  """
        if self.type == "ext3":
            fs_instance = Ext3(self.path, self.type, self.geometry)
        elif self.type == "ntfs":
            fs_instance = Ntfs(self.path, self.type, self.geometry)
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

    def read(self, size):
        return self._fs.read(size)

    def write(self, data):
        self._fs.write(data)

    def close(self):
        self._fs.close()

    def uuid(self):
        return self._fs.uuid()

    def is_swap(self):
        return self._fs.is_swap()
