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
import os

from carbono.device import Device
from carbono.disk import Disk
from carbono.mbr import Mbr
from carbono.disk_layout_manager import DiskLayoutManager
from carbono.information import Information
from carbono.compressor import Compressor
from carbono.buffer_manager import BufferManagerFactory
from carbono.iso_creator import IsoCreator
from carbono.exception import *
from carbono.utils import *
from carbono.config import *

from carbono.log import log

class ImageCreator:

    def __init__(self, source_device, output_folder,
                 status_callback, image_name="image", compressor_level=6,
                 raw=False, split_size=0, create_iso=False,
                 fill_with_zeros=False):

        assert check_if_root(), "You need to run this application as root"
        assert os.path.isdir(output_folder), "{0} folder is invalid".\
                                             format(output_folder)

        self.image_name = image_name
        self.device_path = source_device
        self.target_path = adjust_path(output_folder)
        self.notify_status = status_callback
        self.compressor_level = compressor_level
        self.raw = raw
        self.split_size = split_size
        self.create_iso = create_iso
        self.fill_with_zeros = fill_with_zeros

        self.timer = Timer(self.notify_percent)
        self.total_blocks = 0
        self.processed_blocks = 0
        self.current_percent = -1
        self.active = False
        self.canceled = False

    def notify_percent(self):
        percent = (self.processed_blocks/float(self.total_blocks)) * 100
        if percent > self.current_percent:
            self.current_percent = percent
            self.notify_status("progress", {"percent": percent})

    def create_image(self):
        """ """
        if is_mounted(self.device_path):
            raise DeviceIsMounted("Please umount first")

        self.active = True
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
                log.info("Checking filesystem of {0}".format(part.get_path()))
                self.notify_status("checking_filesystem",
                                   {"device": part.get_path()})
                if not part.filesystem.check():
                    log.error("{0} Filesystem is not clean".\
                              format(part.get_path()))
                    raise ErrorCreatingImage("{0} Filesystem is not clean".\
                                             format(part.get_path()))

        # fill partitions with zeroes
        if self.raw and self.fill_with_zeros:
            for part in partition_list:
                log.info("{0} Filling with zeros".format(part.get_path()))
                self.notify_status("filling_with_zeros", {"device":
                                                          part.get_path()})
                part.filesystem.fill_with_zeros()

        # get total size
        total_bytes = 0
        for part in partition_list:
            total_bytes += part.filesystem.get_used_size()
       
        self.total_blocks = long(math.ceil(total_bytes/float(BLOCK_SIZE)))

        information = Information(self.target_path)
        information.set_image_is_disk(device.is_disk())
        information.set_image_name(self.image_name)
        information.set_image_compressor_level(self.compressor_level)

        # TODO: Abstract this whole part, when creating isos,
        # splitting in files, etc...

        self.timer.start()
        remaining_size = self.split_size
        if self.create_iso:
            remaining_size -= BASE_SYSTEM_SIZE
        slices = dict()                  # Used when creating iso
        iso_volume = 1                   # Used when creating iso
        for part in partition_list:
            if not self.active: break

            log.info("Creating image of {0}".format(part.get_path()))
            number = part.get_number()
            uuid = part.filesystem.uuid()
            label = part.filesystem.read_label()
            type = part.filesystem.type

            part.filesystem.open_to_read()

            compact_callback = None
            if self.compressor_level:
                compressor = Compressor(self.compressor_level)
                compact_callback = compressor.compact

            self.buffer_manager = BufferManagerFactory(
                                  part.filesystem.read_block,
                                  compact_callback)
            self.buffer_manager.start()

            buffer = self.buffer_manager.output_buffer 
            volumes = 1
            while self.active:
                total_written = 0 # Used to help splitting the file
                pattern = FILE_PATTERN.format(name=self.image_name,
                                              partition=number,
                                              volume=volumes)
                file_path = self.target_path + pattern
                fd = open(file_path, "wb")

                next_partition = False
                while self.active:
                    try:
                        data = buffer.get()
                    except IOError, e:
                        if e.errno == errno.EINTR:
                            self.cancel()
                            break

                    if data == EOF:
                        next_partition = True
                        if self.create_iso:
                            remaining_size -= total_written
                            if not slices.has_key(iso_volume):
                                slices[iso_volume] = list()
                            slices[iso_volume].append(file_path)
                        break

                    fd.write(data)
                    self.processed_blocks += 1

                    if self.split_size:
                        bytes_written = len(data)
                        total_written += bytes_written

                        if (total_written + bytes_written) >= remaining_size:
                            volumes += 1
                            remaining_size = self.split_size
                            if self.create_iso:
                                if not slices.has_key(iso_volume):
                                    slices[iso_volume] = list()
                                slices[iso_volume].append(file_path)
                                iso_volume += 1
                            break

                fd.close()
                if next_partition: break

            self.buffer_manager.join()
            part.filesystem.close()
            information.add_partition(number, type, volumes,
                                      part.filesystem.get_used_size(),
                                      uuid, label)

        # We dont need to save the data of the swap partition
        # we just copy the informations and re-create when
        # restoring
        swap = disk.get_swap_partition()
        if swap is not None:
            log.info("Swap path {0}".format(swap.get_path()))
            number = swap.get_number()
            uuid = swap.filesystem.uuid()
            type = swap.filesystem.type
            information.add_partition(number, type, 0, 0, uuid)

        information.save()
        self.stop()

        if self.create_iso:
            log.info("Starting create ISO operation")
            iso_creator = IsoCreator(self.target_path, slices,
                                     self.image_name,
                                     self.notify_status,
                                     device.is_disk())
            iso_creator.run()

        if self.canceled:
            self.notify_status("canceled", {"operation": 
                                            "Create image"})
        else:
            self.notify_status("finish")
        log.info("Creation finished")

    def stop(self):
        if self.active:
            if hasattr(self, "buffer_manager"):
                self.buffer_manager.stop()
        self.active = False
        self.timer.stop() 
        log.info("Create image stopped")

    def cancel(self):
        if not self.canceled:
            log.info("Create image canceled")
            self.canceled = True
            self.stop()
