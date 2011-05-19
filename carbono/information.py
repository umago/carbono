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

import libxml2

from carbono.exception import *
from carbono.utils import *

class Information:

    def __init__(self, target_path):
        self._doc = libxml2.newDoc("1.0")
        self._doc.newChild(None, "image", None)
        self.target_path = adjust_path(target_path)
        self.file_path = self.target_path + "info.xml"

    def set_image_name(self, name):
        """ """
        root = self._doc.getRootElement()
        root.setProp("name", name)

    def set_image_compressor_level(self, level):
        """ """
        root = self._doc.getRootElement()
        root.setProp("compressor_level", str(level))

    def set_image_total_bytes(self, total_bytes):
        """ """
        root = self._doc.getRootElement()
        root.setProp("total_bytes", str(total_bytes))

    def set_image_is_disk(self, is_disk):
        """ """
        root = self._doc.getRootElement()
        root.setProp("is_disk", str(is_disk))

    def add_partition(self, number, uuid, type, volumes):
        """ """
        root = self._doc.getRootElement()
        partition = root.newChild(None, "partition", None)

        partition.setProp("number", str(number))
        partition.setProp("type", type)

        if uuid is not None:
            partition.setProp("uuid", uuid)
        if volumes > 1:
            partition.setProp("volumes", str(volumes))


    def get_image_name(self):
        """ """
        root = self._doc.getRootElement()
        name = root.xpathEval2("@name")[0].content
        return name
    
    def get_image_compressor_level(self):
        """ """
        root = self._doc.getRootElement()
        level = int(root.xpathEval2("@compressor_level")[0].content)
        return level

    def get_image_total_bytes(self):
        """ """
        root = self._doc.getRootElement()
        total_bytes = long(root.xpathEval2("@total_bytes")[0].content)
        return total_bytes

    def get_image_is_disk(self):
        """ """
        root = self._doc.getRootElement()
        is_disk = eval(root.xpathEval2("@is_disk")[0].content)
        return is_disk

    def get_partitions(self):
        """ """
        root = self._doc.getRootElement()
        partitions = list()
        for p in root.xpathEval2("partition"):
            number = int(p.xpathEval2("@number")[0].content)
            type_ = p.xpathEval2("@type")[0].content

            part_dict = dict()
            part_dict.update({"number": number, "type": type_})

            if p.xpathEval2("@uuid"):
                uuid = p.xpathEval2("@uuid")[0].content
                part_dict.update({"uuid": uuid})

            if p.xpathEval2("@volumes"):
                volumes = int(p.xpathEval2("@volumes")[0].content)
                part_dict.update({"volumes": volumes})

            partition = type("Partition",
                             (object,),
                             part_dict)
            partitions.append(partition)
        return partitions

    def save(self):
        """ """
        self._doc.saveFileEnc(self.file_path, "utf-8")

    def load(self):
        """ """
        self._doc = libxml2.parseFile(self.file_path)

