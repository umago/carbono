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
from carbono.filesystem import FilesystemFactory
from carbono.utils import *

class Partition(parted.Partition):
    
    def __init__(self, disk, fs, type, geometry, path, number):
        parted.Partition.__init__(self, disk, type, fs, geometry)
        self._number = number
        self._path = path
        if fs is None: # treat as generic
            fs_type = "generic"
        else:
            fs_type = fs.type
            
        self.filesystem = FilesystemFactory(path,
                                            fs_type,
                                            geometry)

    def get_number(self):
        """ """
        return self._number

    def get_path(self):
        """ """
        return self._path
