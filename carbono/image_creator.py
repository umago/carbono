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

import math
from os.path import realpath

from carbono.device import Device
from carbono.disk import Disk
from carbono.progress import Progress
from carbono.mbr import Mbr
from carbono.compressor import Compressor
from carbono.disk_layout_manager import DiskLayoutManager
from carbono.information import Information
from carbono.options import Options
from carbono.exception import *
from carbono.utils import *
from carbono.config import *

class ImageCreator:

    def __init__(self):

        self.options = Options()
        self.image_name = self.options.image_name
        self.device_path = self.options.source_device
        self.target_path = adjust_path(realpath(self.options.output_folder))
        self.compressor_level = self.options.compressor_level

    def _print_informations(self, total_bytes):
        """ """
        print "Total Bytes: %s" % total_bytes
        print "Name: %s" % self.image_name
        print "Compressor Level: %s" % self.compressor_level
        print "Source Device: %s" % self.device_path
        print "Target Path: %s" % self.target_path

    def create_image(self):
        """ """
        device = Device(self.device_path)
        disk = Disk(device)

        if device.is_disk():
            mbr = Mbr(self.target_path)
            mbr.save_to_file(self.device_path)
            dlm = DiskLayoutManager(self.target_path)
            dlm.save_to_file(disk)
        
        partition_list = disk.get_valid_partitions()
        
        total_bytes = 0
        for p in partition_list:
            total_bytes += p.filesystem.get_used_size()
       
        total_blocks = long(math.ceil(total_bytes/float(BLOCK_SIZE)))
        self._print_informations(total_bytes)

        information = Information(self.target_path)
        information.set_image_is_disk(device.is_disk())
        information.set_image_name(self.image_name)
        information.set_image_total_bytes(total_bytes)
        information.set_image_compressor_level(self.compressor_level)

        compressor = Compressor(self.compressor_level)
        progress = Progress(total_blocks)
        progress.start()
        for p in partition_list:
            number = p.get_number()
            uuid = p.filesystem.uuid()
            type = p.filesystem.type
            information.add_partition(number, uuid, type)

            p.filesystem.open_to_read()

            file_name = FILE_PATTERN % (self.image_name, number)
            with open(self.target_path + file_name, 'wb') as f:
                # TODO: Work with parallelism
                while True: # Ugly
                    data = p.filesystem.read(BLOCK_SIZE)
                    if not len(data):
                        break
                    cdata = compressor.compact(data)
                    f.write(cdata)
                    progress.increment(1)
            p.filesystem.close()

        swap = disk.get_swap_partition()
        if swap is not None:
            number = swap.get_number()
            uuid = swap.filesystem.uuid()
            type = swap.filesystem.type
            information.add_partition(number, uuid, type)

        information.save()
        progress.stop()
        print "completed."


