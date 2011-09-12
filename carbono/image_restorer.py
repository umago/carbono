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
from carbono.image_reader import ImageReaderFactory
from carbono.compressor import Compressor
from carbono.buffer_manager import BufferManagerFactory
from carbono.exception import *
from carbono.utils import *
from carbono.config import *

from carbono.log import log

class ImageRestorer:

    def __init__(self, image_folder, target_device, status_callback):
        self.image_path = adjust_path(image_folder)
        self.target_device = target_device
        self.notify_status = status_callback
 
        self.timer = Timer(self.notify_percent)
        self.total_blocks = 0
        self.processed_blocks = 0
        self.current_percent = -1
        self.active = False

    def notify_percent(self):
        percent = (self.processed_blocks/float(self.total_blocks)) * 100
        if self.current_percent != percent:
            self.current_percent = percent
            self.notify_status("progress", {"percent": self.current_percent})

    def restore_image(self):
        """ """
        self.active = True
        information = Information(self.image_path)
        information.load()
        image_name = information.get_image_name()
        compressor_level = information.get_image_compressor_level()
        total_bytes = information.get_image_total_bytes()
        self.total_blocks = long(math.ceil(total_bytes/float(BLOCK_SIZE)))

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

        self.timer.start()
        partitions = information.get_partitions()
        for part in partitions:
            if not self.active: break
            
            if information.get_image_is_disk():
                partition = disk.get_partition_by_number(part.number,
                                                         part.type)
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

            pattern = FILE_PATTERN.format(name=image_name,
                                          partition=part.number,
                                          volume="{volume}")
            volumes = 1
            if hasattr(part, "volumes"):
                volumes = part.volumes

            image_reader = ImageReaderFactory(self.image_path, pattern,
                                              volumes, compressor_level,
                                              self.notify_status)

            extract_callback = None
            if compressor_level:
                compressor = Compressor(compressor_level)
                extract_callback = compressor.extract

            self.buffer_manager = BufferManagerFactory(image_reader.read_block,
                                                       extract_callback)
            self.buffer_manager.start()

            buffer = self.buffer_manager.output_buffer
            while self.active:
                data = buffer.get()
                if data == EOF:
                    break
                partition.filesystem.write_block(data)
                self.processed_blocks += 1

            self.buffer_manager.join()
            partition.filesystem.close()

        self.stop()
        self.notify_status("finish")
        log.info("Restoration finished")

    def stop(self):
        if self.active:
            self.buffer_manager.stop()
        self.active = False
        self.timer.stop()        

