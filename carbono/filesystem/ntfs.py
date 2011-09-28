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
        cmd = "{0} --force --save-image -o - {1} 2> /dev/null".\
              format(which("ntfsclone"), self.path)
        try:
            self.process = RunCmd(cmd)
            self.process.run()
            self._fd = self.process.stdout
        except:
            raise ErrorOpenToRead("Cannot open {0} to read".format(self.path))

    def open_to_write(self):
        """ """
        cmd = "{0} --force --restore-image --overwrite {1} - > /dev/null".\
              format(which("ntfsclone"), self.path)
        try:
            self.process = RunCmd(cmd)
            self.process.run()
            self._fd = self.process.stdin
        except:
            raise ErrorOpenToWrite("Cannot open {0} to write".format(self.path))

    def get_size(self):
        """ """
        proc = subprocess.Popen("{0} -i {1} -f".format(which("ntfsresize"), self.path),
                                shell=True, stdout=subprocess.PIPE)
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
        proc = subprocess.Popen("{0} -i {1} -f".format(which("ntfsresize"), self.path),
                                shell=True, stdout=subprocess.PIPE)
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
        self.process = RunCmd("{0} -P -i -f -v {1}".\
                       format(which("ntfsresize"), self.path))
        self.process.run()
        return not self.process.wait()

    def resize(self):
        if self.check():
            ret = run_simple_command("ntfsresize -f {0}".format(self.path))
            if ret == 0:
                return True
        return False

    def read_label(self):
        proc = subprocess.Popen([which("ntfslabel"), "--force", self.path],
                                stdout=subprocess.PIPE)
        output = proc.stdout.read()
        output = output.strip()
        if output:
            return output
        return None

    def write_label(self, label):
        ret = run_simple_command('{0} --force {1} "{2}"'. \
              format(which("ntfslabel"), self.path, label))
        if ret == 0:
            return True
        return False
