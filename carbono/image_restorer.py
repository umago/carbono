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
from carbono.mbr import Mbr
from carbono.disk_layout_manager import DiskLayoutManager
from carbono.information import Information
from carbono.reader import ReaderFactory
from carbono.exception import *
from carbono.utils import *
from carbono.config import *

from carbono.log import log

class ImageRestorer:

    def __init__(self, image_folder, target_device):
        self.image_path = adjust_path(image_folder)
        self.target_device = target_device

    def connect_status_callback(self, callback):
        """ """
        self.status_callback = callback

    def notify_status(self, action, dict={}):
        """Notify interfaces about the current progress"""
        if hasattr(self, "status_callback"):
            self.status_callback(action, dict) 

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
            log.error("Invalid target device %s" % device.path)
            raise ErrorRestoringImage("Invalid target device")

        try:
            disk = Disk(device)
        except _ped.DiskLabelException:
            try:
                device.fix_disk_label()
                disk = Disk(device)
            except:
                log.error("Unrecognized disk label")
                raise ErrorRestoringImage("Unrecognized disk label")

        if information.get_image_is_disk():
            log.info("Restoring MBR and Disk Layout")
            mbr = Mbr(self.image_path)
            mbr.restore_from_file(self.target_device)
            dlm = DiskLayoutManager(self.image_path)
            dlm.restore_from_file(disk)

        partitions = information.get_partitions()
        for part in partitions:
            if information.get_image_is_disk():
                partition = disk.get_partition_by_number(part.number, part.type)
            else:
                parent_path = get_parent_path(self.target_device)
                parent_device = Device(parent_path)
                parent_disk = Disk(parent_device)
                partition = parent_disk.get_partition_by_path(
                                            self.target_device,
                                            part.type)

            log.info("Restoring partition %s" % partition.path)

            if partition is None:
                raise ErrorRestoringImage("No valid partitions found")

            if hasattr(part, "uuid"):
                partition.filesystem.open_to_write(part.uuid)
            else:
                partition.filesystem.open_to_write()

            if partition.filesystem.is_swap():
                continue

            processed_blocks = 0
            current_percent = -1

            current_volume = 1
            while True:
                file_name = FILE_PATTERN % (image_name, part.number, current_volume)
                file_path = self.image_path + file_name

                reader = ReaderFactory(file_path, compressor_level)

                for data in reader:
                    partition.filesystem.write(data)

                    processed_blocks += 1
                    percent = (processed_blocks/float(total_blocks)) * 100
                    if current_percent != percent:
                        current_percent = percent
                        self.notify_status("progress", {"percent": current_percent})

                if hasattr(part, "volumes"):
                    if current_volume < part.volumes:
                        current_volume += 1
                        continue
                break

            partition.filesystem.close()

        self.notify_status("finish")
        log.info("Restoration finished")
