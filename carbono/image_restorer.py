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
import _ped

from carbono.device import Device
from carbono.disk import Disk
from carbono.progress import Progress
from carbono.mbr import Mbr
from carbono.disk_layout_manager import DiskLayoutManager
from carbono.information import Information
from carbono.reader import ReaderFactory
from carbono.exception import *
from carbono.utils import *
from carbono.config import *

class ImageRestorer:

    def __init__(self, image_folder, target_device):
        self.image_path = adjust_path(image_folder)
        self.target_device = target_device

    def _print_informations(self, total_bytes, image_name):
        """ """
        print "Total Bytes: %s" % total_bytes
        print "Name: %s" % image_name
        print "Target Device: %s" % self.target_device

    def restore_image(self):
        """ """
        information = Information(self.image_path)
        information.load()
        image_name = information.get_image_name()
        compressor_level = information.get_image_compressor_level()
        total_bytes = information.get_image_total_bytes()
        total_blocks = long(math.ceil(total_bytes/float(BLOCK_SIZE)))

        device = Device(self.target_device)

        if device.is_disk() != \
           information.get_image_is_disk():
            raise ErrorRestoringImage("Invalid target dispositive")

        try:
            disk = Disk(device)
        except _ped.DiskLabelException:
            try:
                device.fix_disk_label()
                disk = Disk(device)
            except:
                raise ErrorRestoringImage("Unrecognized disk label")

        if information.get_image_is_disk():
            mbr = Mbr(self.image_path)
            mbr.restore_from_file(self.target_device)
            dlm = DiskLayoutManager(self.image_path)
            dlm.restore_from_file(disk)

        self._print_informations(total_bytes, image_name)
        progress = Progress(total_blocks)
        progress.start()
        partitions = information.get_partitions()
        for p in partitions:
            if information.get_image_is_disk():
                partition = disk.get_partition_by_number(p.number, p.type)
            else:
                parent_path = get_parent_path(self.target_device)
                parent_device = Device(parent_path)
                parent_disk = Disk(parent_device)
                partition = parent_disk.get_partition_by_path(
                                            self.target_device,
                                            p.type)

            if partition is None:
                raise ErrorRestoringImage("No valid partitions found")

            if p.uuid is not None:
                partition.filesystem.open_to_write(p.uuid)
            else:
                partition.filesystem.open_to_write()

            if partition.filesystem.is_swap():
                continue

            file_name = FILE_PATTERN % (image_name, p.number)
            file_path = self.image_path + file_name

            reader = ReaderFactory(file_path, compressor_level)

            for data in reader:
                partition.filesystem.write(data)
                progress.increment(1)

            partition.filesystem.close()

        progress.stop()
        print "completed."
