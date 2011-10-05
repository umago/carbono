#!/usr/bin/python
# coding: utf-8
# Copyright (C) 2011 Lucas Alvares Gomes <lucasagomes@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

from distutils.core import setup
from carbono.config import get_version

DEPENDS = "python2.7, partclone, ntfsprogs, btrfs-tools, e2fsprogs, genisoimage"
DESC = "A hard disk imaging and recovery application"

setup(name = "carbono",
      version = get_version(),
      author = "Lucas Alvares Gomes",
      author_email = "lucasagomes@gmail.com",
      url = "http://umago.info/carbono",
      description = DESC,
      license = "GNU GPLv2",
      packages = ["carbono","carbono.buffer_manager",
                  "carbono.filesystem", "carbono.ui",
                  "carbono.image_reader"],
      scripts = ["scripts/carbono"],
      )

