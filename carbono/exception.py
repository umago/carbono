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

class ErrorOpenToRead(Exception):
    pass

class ErrorOpenToWrite(Exception):
    pass

class ErrorReadingFromDevice(Exception):
    pass

class ErrorWritingToDevice(Exception):
    pass

class ErrorGettingSize(Exception):
    pass

class ErrorGettingUsedSize(Exception):
    pass

class ErrorSavingDiskLayout(Exception):
    pass

class ErrorRestoringDiskLayout(Exception):
    pass

class ErrorRestoringImage(Exception):
    pass

class ErrorCreatingImage(Exception):
    pass

class InvalidCompressorLevel(Exception):
    pass

class ErrorMountingFilesystem(Exception):
    pass

class ImageNotFound(Exception):
    pass

class CommandNotFound(Exception):
    pass

class PartitionNotFound(Exception):
    pass

class ExpandingPartitionError(Exception):
    pass

class DeviceIsMounted(Exception):
    pass

