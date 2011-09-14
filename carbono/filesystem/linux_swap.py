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
import re
from carbono.filesystem.generic import Generic
from carbono.utils import *

class LinuxSwap(Generic):

    def _make_filesystem(self, uuid=None):
        """ """
        param = ''
        if uuid is not None:
            param = "-U %s" % uuid

        ret = run_simple_command("{0} {1} {2}".\
                                format(which("mkswap"),
                                param, self.path))
        return ret

    def open_to_write(self, uuid=None):
        """ """
        ret = self._make_filesystem(uuid)
        if ret is not 0:
            raise ErrorOpenToWrite

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

    def is_swap(self):
        """  """
        return True
