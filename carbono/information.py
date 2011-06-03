#!/usr/bin/python
# coding: utf-8
# Copyright (C) 2011 Lucas Alvares Gomes <lucasagomes@gmail.com>
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

import json

from carbono.utils import *

class Information:

    def __init__(self, target_path):
        self._doc = dict()
        self.target_path = adjust_path(target_path)
        self.file_path = self.target_path + "image.info"

    def set_image_name(self, name):
        """ """
        self._doc.update({"name": name})

    def set_image_compressor_level(self, level):
        """ """
        self._doc.update({"compressor_level": level})

    def set_image_total_bytes(self, total_bytes):
        """ """
        self._doc.update({"total_bytes": total_bytes})

    def set_image_is_disk(self, is_disk):
        """ """
        self._doc.update({"is_disk": is_disk})

    def add_partition(self, number, uuid, type, volumes):
        """ """
        part_dict = dict()
        part_dict.update({"number": number,
                          "type": type})

        if uuid is not None:
            part_dict.update({"uuid": uuid})
        if volumes > 1:
            part_dict.update({"volumes": volumes})

        if not self._doc.has_key("partitions"):
            self._doc.update({"partitions": list()})

        self._doc["partitions"].append(part_dict)

    def get_image_name(self):
        """ """
        return self._doc["name"]
    
    def get_image_compressor_level(self):
        """ """
        return self._doc["compressor_level"]

    def get_image_total_bytes(self):
        """ """
        return self._doc["total_bytes"]

    def get_image_is_disk(self):
        """ """
        return self._doc["is_disk"]

    def get_partitions(self):
        """ """
        partitions = self._doc["partitions"]
        parts = list()
        for part in partitions:
            partition = type("Partition",
                             (object,),
                             part)
            parts.append(partition)
        return parts

    def save(self):
        with open(self.file_path, mode='w') as f:
            json.dump(self._doc, f, indent=4)

    def load(self):
        with open(self.file_path, 'r') as f:
            self._doc = json.load(f)

