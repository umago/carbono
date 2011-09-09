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

from carbono.utils import *

class Mbr:

    def __init__(self, target_path):
        self.target_path = adjust_path(target_path)
        self.file_path = self.target_path + "mbr.bin"
    
    def save_to_file(self, device):
        """ """
        fdevice = open(device, 'rb')
        ffile = open(self.file_path, 'wb')
        data = fdevice.read(446)
        ffile.write(data)
        fdevice.close()
        ffile.close()

    def restore_from_file(self, device):
        """ """
        ffile = open(self.file_path, 'rb')
        fdevice = open(device, 'wb')
        data = ffile.read(446)
        fdevice.write(data)
        fdevice.close()
        ffile.close()
        run_simple_command("sfdisk -R %s" % device)
        
            

        
