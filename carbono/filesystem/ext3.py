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
import os
import time
import re
from carbono.filesystem.generic import Generic
from carbono.exception import *
from carbono.utils import *

class Ext3(Generic):
    MOUNT_OPTIONS = "-t ext3"

    def __init__(self, path, type, geometry):
        Generic.__init__(self, path, type, geometry)
        self._tmpfs = make_temp_dir()

    def _mount_tmpfs(self):
        """  """
        # FIXME: Ret code inst reliable
        if not os.path.ismount(self._tmpfs):
            ret = run_command("mount -t tmpfs -o size=100M tmpfs %s" % self._tmpfs)
            if ret is not 0:
                return False

        return True
    
    def _umount_tmpfs(self):
        """  """
        # FIXME: Ret code inst reliable
        if os.path.ismount(self._tmpfs):
            ret = run_command("umount %s" % self._tmpfs)
            if ret is not 0:
                return False

        return True

    def _make_filesystem(self, uuid=None):
        """ """
        param = ''
        if uuid is not None:
            param = "-U %s" % uuid

        ret = run_command("mkfs.ext3 %s %s" % (param, self.path))
        return ret

    def get_used_size(self):
        """  """
        tmpd = self.mount()

        try:
            out = os.popen("df -k | grep %s" % tmpd).read()
            size = long(out.split()[2]) * 1024
        except Exception:
            raise ErrorGettingUsedSize

        self.umount(tmpd)
        return size

    def open_to_read(self):
        """ """
        cmd = "dump -0 -q -f - %s 2> /dev/null" % self.path
        try:
            self._fd = subprocess.Popen(cmd, shell=True,
                                        stdin=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        stdout=subprocess.PIPE).stdout
        except:
            raise ErrorOpenToRead("Cannot open %s to read" % self.path)

    def open_to_write(self, uuid=None):
        """ """
        run_command("umount %s" % self.path)

        ret = self._make_filesystem(uuid)
        if ret is not 0:
            raise ErrorOpenToWrite

        tmpd = self.mount()
        if self._mount_tmpfs():
            os.chdir(tmpd)
            cmd = "restore -u -y -r -T %s -f -" % self._tmpfs
            try:
                self._fd = subprocess.Popen(cmd, shell=True,
                                            stdin=subprocess.PIPE,
                                            stderr=subprocess.PIPE,
                                            stdout=subprocess.PIPE).stdin
            except:
                raise ErrorOpenToWrite("Cannot open %s to read" % self.path)
        else:
            raise ErrorOpenToWrite("Unable to mount a tmpfs filesystem")

    def uuid(self):
        """ """
        proc = subprocess.Popen(["blkid", self.path], stdout=subprocess.PIPE)
        output = proc.stdout.read()

        uuid = None

        if not len(output):
            return uuid
        
        try:
            uuid = re.search('(?<=UUID=")\w+-\w+-\w+-\w+-\w+', output).group(0)
        except AttributeError:
            pass

        return uuid

    def close(self):
        """  """
        if self._fd is None or \
           self._fd.closed:
            return

        self._fd.close()
        #FIXME: Ugly timing, but it works :~
        time.sleep(2)
        os.chdir('/')
        run_command("sync")
        self._umount_tmpfs()
        run_command("umount %s" % self.path)

    def check(self):
        ret = run_command("e2fsck -f -y -v %s" % self.path)
        if ret in(0, 1, 2, 256):
            return True
        return False

