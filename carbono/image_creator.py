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

from carbono.device import Device
from carbono.disk import Disk
from carbono.progress import Progress
from carbono.mbr import Mbr
from carbono.disk_layout_manager import DiskLayoutManager
from carbono.information import Information
from carbono.writer import WriterFactory
from carbono.exception import *
from carbono.utils import *
from carbono.config import *

class ImageCreator:

    def __init__(self, source_device, output_folder, image_name="image", \
                 compressor_level=6, raw=False, split_size=0):

        self.image_name = image_name
        self.device_path = source_device
        self.target_path = adjust_path(output_folder)
        self.compressor_level = compressor_level
        self.raw = raw
        self.split_size = split_size

    def _print_informations(self, total_bytes):
        """ """
        print "Total Bytes: %s" % total_bytes
        print "Name: %s" % self.image_name
        print "Source Device: %s" % self.device_path
        print "Target Path: %s" % self.target_path
        if self.compressor_level:
            print "Compressor Level: %s" % self.compressor_level
        if self.split_size:
            print "Split Size: %d MB" % self.split_size

    def create_image(self):
        """ """
        device = Device(self.device_path)
        disk = Disk(device)

        if device.is_disk():
            mbr = Mbr(self.target_path)
            mbr.save_to_file(self.device_path)
            dlm = DiskLayoutManager(self.target_path)
            dlm.save_to_file(disk)
        
        partition_list = disk.get_valid_partitions(self.raw)

        # check partitions filesystem
        if not self.raw:
            for part in partition_list:
                if not part.filesystem.check():
                    raise ErrorCreatingImage("(%s) Filesystem is not clean" % part.path)       

        # get total size
        total_bytes = 0
        for part in partition_list:
            total_bytes += part.filesystem.get_used_size()
       
        total_blocks = long(math.ceil(total_bytes/float(BLOCK_SIZE)))
        self._print_informations(total_bytes)

        information = Information(self.target_path)
        information.set_image_is_disk(device.is_disk())
        information.set_image_name(self.image_name)
        information.set_image_total_bytes(total_bytes)
        information.set_image_compressor_level(self.compressor_level)

        progress = Progress(total_blocks)
        progress.start()
        for part in partition_list:
            number = part.get_number()
            uuid = part.filesystem.uuid()
            type = part.filesystem.type

            part.filesystem.open_to_read()
            split_volume = 1
            while True:
                file_name = FILE_PATTERN % (self.image_name, number, split_volume)
                file_path = self.target_path + file_name

                writer = WriterFactory(file_path, self.compressor_level)
                writer.open()

                next_partition = False
                total_written = 0
                while True:
                    data = part.filesystem.read(BLOCK_SIZE)
                    if not len(data):
                        next_partition = True
                        break
                    bytes_written = writer.write(data)
                    total_written += bytes_written
                    progress.increment(1)
                    if self.split_size:
                        if (total_written + bytes_written) / 1024 / 1024 >= self.split_size:
                            break

                writer.close()
                if next_partition: break
                split_volume += 1
            part.filesystem.close()
            information.add_partition(number, uuid, type, split_volume)

        swap = disk.get_swap_partition()
        if swap is not None:
            number = swap.get_number()
            uuid = swap.filesystem.uuid()
            type = swap.filesystem.type
            information.add_partition(number, uuid, type, 0)

        information.save()
        progress.stop()
        print "completed."


