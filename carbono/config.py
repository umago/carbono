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

FILE_PATTERN = "{name}-{partition}-{volume}.data"
BLOCK_SIZE = 1048576 # 1MB
BASE_SYSTEM_SIZE = 0 #TODO (in bytes)
LOG_FILE = "/var/tmp/carbono.log"
EOF = -1
VERSION = (0, 1, 0, "alpha", 0)

def get_version():
    version = "%s.%s" % (VERSION[0], VERSION[1])
    if VERSION[2]:
        version = "%s.%s" % (version, VERSION[2])
    if VERSION[3] != "final":
            version = "%s-%s-%s" % (version, VERSION[3], VERSION[4])
    return version

