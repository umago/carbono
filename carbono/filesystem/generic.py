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
from carbono.config import *
from carbono.exception import *
from carbono.utils import *

class Generic:
    MOUNT_OPTIONS = ""

    def __init__(self, path, type, geometry):
        self.path = path
        self.type = type
        self.geometry = geometry
        self._fd = None
        self.process = None

    def get_size(self):
        """ """
        return long(self.geometry.getSize('b'))

    def get_used_size(self):
        """ """
        return self.get_size()

    def open_to_read(self):
        """ """
        cmd = "dd if={0} bs={1}".format(self.path, BLOCK_SIZE)
        try:
            self.process = RunCmd(cmd)
            self.process.run()
            self._fd = self.process.stdout
        except:
            raise ErrorOpenToRead("Cannot open {0} to read".\
                                  format(self.path))

    def open_to_write(self):
        """ """
        cmd = "dd of={0} bs={1}".format(self.path, BLOCK_SIZE)
        try:
            self.process = RunCmd(cmd)
            self.process.run()
            self._fd = self.process.stdin
        except:
            raise ErrorOpenToWrite("Cannot open {0} to write".\
                                   format(self.path))

    def read_block(self):
        """ """
        if self._fd is None or \
           self._fd.closed:
            raise ErrorReadingFromDevice("File descriptor does not " +\
                                         "exist or its closed")
            
        return self._fd.read(BLOCK_SIZE)

    def write_block(self, data):
        """  """
        if self._fd is None or \
           self._fd.closed:
            raise ErrorWritingToDevice("File descriptor does not "+\
                                       "exist or its closed")

        self._fd.write(data)

    def close(self):
        """  """
        if self._fd is None or \
           self._fd.closed:
            return

        self._fd.close()
        sync()

    def uuid(self):
        """  """
        return None

    def get_type(self):
        """ """
        return self.type

    def is_swap(self):
        """  """
        return False

    def check(self):
        """ Check if filesystem is clean. """
        return True

    def mount(self):
        tmpd = make_temp_dir()
        ret = run_simple_command("mount {0} {1} {2}".\
              format(self.MOUNT_OPTIONS, self.path, tmpd))
        if ret is not 0:
            raise ErrorMountingFilesystem
        return tmpd

    def umount(self, dir=None):
        if dir is not None:
            param = dir
        else:
            param = self.path
        ret = run_simple_command("umount {0}".format(param))
        sync()
        return ret

    def fill_with_zeros(self):
        tmpd = self.mount()
        tmpfile = tmpd + '/' + random_string()

        self.process = RunCmd("dd if=/dev/zero of={0} bs={1}".\
                              format(tmpfile, BLOCK_SIZE))
        self.process.run()
        self.process.wait()

        run_simple_command("rm {0}".format(tmpfile))
        self.umount(tmpd)
        return 0

    def stop(self):
        if self.process is not None:
            self.process.stop()
 
    def resize(self):
        return True

    def read_label(self):
        return None

    def write_label(self, label):
        return True

