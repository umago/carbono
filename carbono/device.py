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
import subprocess

from carbono.utils import *

class Device(parted.Device):
    
    def get_size(self):
        """Returns the size in bytes"""
        return int(self.getSize('b'))

    def is_disk(self):
        """Check if the device is a disk or partition"""
        try:
            int(self.path[-1])
        except ValueError:
            return True
        return False

    def fix_disk_label(self):
        """Workaround to fix the disk label"""
        if self.is_disk():
            proc = subprocess.Popen("fdisk %s" %(self.path),
                                    shell=True,
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            proc.stdin.write('%s\n' % 'o')
            proc.stdin.write('%s\n' % 'w')
            proc.communicate()
        else:
            run_simple_command("mkntfs -f %s" % self.path)
