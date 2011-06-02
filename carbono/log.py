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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

import logging

from carbono.utils import *

__all__ = ["log"]

@singleton
class Logger(logging.Logger):
    def __init__(self, name="carbono", logfile="/var/tmp/carbono.log"):
        logging.Logger.__init__(self, name)
        hdlr = logging.FileHandler(logfile)
        formatter = logging.Formatter("%(asctime)s %(levelname)s [%(filename)s " \
                                      "-> %(funcName)s] %(message)s", "%H:%M:%S")
        hdlr.setFormatter(formatter)
        self.addHandler(hdlr) 
        self.setLevel(logging.DEBUG)

log = Logger()
