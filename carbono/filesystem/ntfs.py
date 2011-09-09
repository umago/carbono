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

import subprocess
from carbono.filesystem.generic import Generic
from carbono.exception import *
from carbono.utils import *

class Ntfs(Generic):
    MOUNT_OPTIONS = "-t ntfs"

    def open_to_read(self):
        """ """
        cmd = "ntfsclone --force --save-image -o - {0} 2> /dev/null".\
              format(self.path)
        try:
            self.process = RunCmd(cmd)
            self.process.run()
            self._fd = self.process.stdout
        except:
            raise ErrorOpenToRead("Cannot open %s to read" % self.path)

    def open_to_write(self):
        """ """
        cmd = "ntfsclone --force --restore-image --overwrite {0} - > /dev/null".\
              format(self.path)
        try:
            self.process = RunCmd(cmd)
            self.process.run()
            self._fd = self.process.stdin
        except:
            raise ErrorOpenToWrite("Cannot open %s to write" % self.path)

    def get_size(self):
        """ """
        proc = subprocess.Popen(["ntfsresize", "-i" , self.path, "-f"], stdout=subprocess.PIPE)
        lines = proc.stdout.readlines()

        size = None
        for l in lines:
            if l.startswith("Current volume size"):
                try:
                    size = long(l.split()[3])
                except ValueError:
                    raise ErrorGettingSize
        
        if size is None:
            raise ErrorGettingSize

        return size
            
    def get_used_size(self):
        """ """
        proc = subprocess.Popen(["ntfsresize", "-i" , self.path, "-f"], stdout=subprocess.PIPE)
        lines = proc.stdout.readlines()

        size = None
        for l in lines:
            if l.startswith("You might resize at"):
                try:
                    size = long(l.split()[4])
                except ValueError:
                    raise ErrorGettingUsedSize
        
        if size is None:
            raise ErrorGettingUsedSize

        return size

    def check(self):
        """  """
        self.process = RunCmd("ntfsresize -P -i -f -v {0}".format(self.path))
        self.process.run()
        return not self.process.wait()
