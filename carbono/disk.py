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
from carbono.partition import Partition

class Disk(parted.Disk):

    def _instance_partition(self, p):
        """ """
        path = None
        if self.device.is_disk():
            path = p.path
        else:
            path = self.device.path

        partition = Partition(disk=p.disk,
                              fs=p.fileSystem,
                              type=p.type,
                              geometry=p.geometry,
                              path=path,
                              number=p.number)
        return partition


    def get_partition_by_number(self, number, fs_type):
        """ """
        for p in self.partitions:
            if p.number == number:
                if fs_type == "generic":
                    p.fileSystem = None
                else:
                    fs = parted.FileSystem(fs_type, p.geometry)
                    p.fileSystem = fs
                partition = self._instance_partition(p)
                return partition
        return None

    def get_partition_by_path(self, path, fs_type):
        """ """
        p = self.getPartitionByPath(path)
        if fs_type == "generic":
            p.fileSystem = None
        else:
            fs = parted.FileSystem(fs_type, p.geometry)
            p.fileSystem = fs
        partition = self._instance_partition(p)
        return partition

    def get_valid_partitions(self, force_generic=False):
        """Return a list of valid partitions"""
        plist = list()
        for p in self.partitions:
            if p.type == parted.PARTITION_SWAP or \
               p.type == parted.PARTITION_PROTECTED or \
               p.type == parted.PARTITION_METADATA or \
               p.type == parted.PARTITION_FREESPACE: continue

            # Check if its contain a filesystem
            # or its not a swap filesystem
            if not p.fileSystem or \
               p.fileSystem.type.find("swap") > -1:
                continue

            if force_generic:
                p.fileSystem = None

            partition = self._instance_partition(p)
            plist.append(partition)

        return plist

    def get_last_partition(self, force_generic=False):
        """ """
        try:
            part = self.partitions[-1]
        except IndexError:
            return None

        if force_generic:
            part.fileSystem = None

        partition = self._instance_partition(part)
        return partition

    def get_swap_partition(self):
        """ """
        for p in self.partitions:
            if p.fileSystem:
                if p.fileSystem.type.find("swap") > -1:
                    partition = self._instance_partition(p)
                    return partition
        return None
