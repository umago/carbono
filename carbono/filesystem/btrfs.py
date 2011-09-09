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

class Btrfs(Generic):
    MOUNT_OPTIONS = "-t btrfs"

    def get_used_size(self):
        """  """
        p = subprocess.Popen("btrfs-show %s" % self.path,
                             shell=True,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)

        lines = p.stdout.readlines()

        size = 0
        for l in lines:
            if l.startswith("\tTotal devices"):
                size = l.split()[-1]
                unit = size[-2:].upper()
                size = float(size[:-2])
                if unit == "KB":
                    size = long(size * 1024)
                elif unit == "MB":
                    size = long(size * 1024 * 1024)
                elif unit == "GB":
                    size = long(size * 1024 * 1024 * 1024)
                break

        return size

    def open_to_read(self):
        """ """
        cmd = "partclone.btrfs -c -s {0} -o -".format(self.path)
        try:
            self.process = RunCmd(cmd)
            self.process.run()
            self._fd = self.process.stdout
        except:
            raise ErrorOpenToRead("Cannot open %s to read" % self.path)

    def open_to_write(self, uuid=None):
        """ """
        cmd = "partclone.btrfs -r -o {0} -s - ".format(self.path)
        try:
            self.process = RunCmd(cmd)
            self.process.run()
            self._fd = self.process.stdin
        except:
            raise ErrorOpenToWrite("Cannot open %s to read" % self.path)

    def uuid(self):
        """ """
        p = subprocess.Popen("btrfs-show %s" % self.path,
                             shell=True,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)

        lines = p.stdout.readlines()

        uuid = None
        for l in lines:
            seek = l.find("uuid: ")
            if seek != -1:
                uuid = l[seek+6:].strip()

        return uuid

    def close(self):
        """  """
        if self._fd is None or \
           self._fd.closed:
            return

        self._fd.close()

    def check(self):
        """ """
        return not run_simple_command("btrfsck %s" % self.path)

