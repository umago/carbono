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
import os
import time
import cPickle
from _ped import partition_flag_get_by_name

from carbono.exception import *
from carbono.utils import *

__all__ = ["DiskLayoutManager"]

class PartitionLayout(object):
    def __init__(self, type, start, end, length, flags, fs=None):
        self.type = type
        self.start = start
        self.end = end
        self.length = length
        self.flags = flags
        self.fs = fs

class DiskLayoutManager:

    def __init__(self, target_path):
        self.target_path = adjust_path(target_path)
        self.file_path = self.target_path + "disk.dl"

    def save_to_file(self, disk):
        """  """
        partitions = list()
        for p in disk.partitions:
            fs_type = None
            if p.fileSystem:
                fs_type = p.fileSystem.type

            pinf = PartitionLayout(p.type,
                                   p.geometry.start,
                                   p.geometry.end,
                                   p.geometry.length,
                                   p.getFlagsAsString(),
                                   fs_type)
            partitions.append(pinf)

        with open(self.file_path, 'w') as f:
            cPickle.dump(partitions, f)

    def _wait_devices(self, disk):
        """Wait OS create all device nodes"""
        for p in disk.partitions:
            while not os.path.exists(p.path):
                time.sleep(1)

    def restore_from_file(self, disk):
        """ """
        with open(self.file_path, 'r') as f:
            layout = list()
            partitions = cPickle.load(f)
            for p in partitions:
                geometry = parted.geometry.Geometry(device=disk.device,
                                                    start=p.start,
                                                    length=p.length,
                                                    end=p.end)

                p_fs = None
                if p.fs is not None:
                    p_fs = parted.filesystem.FileSystem(type = p.fs,
                                                        geometry = geometry)

                partition = parted.partition.Partition(disk=disk,
                                                       type=p.type,
                                                       geometry=geometry,
                                                       fs=p_fs)

                if p.flags != "swap" and p.flags != '':
                    partition.setFlag(partition_flag_get_by_name(p.flags))
                layout.append(partition)

            disk.deleteAllPartitions()
            constraint = parted.Constraint(device=disk.device)
            for p in layout:
                disk.addPartition(p, constraint)

            disk.commitToDevice()
            disk.commitToOS()
            self._wait_devices(disk)
