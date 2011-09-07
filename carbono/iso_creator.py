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

from carbono.utils import *

import errno

class IsoCreator:
    def __init__(self, target_path, slices,
                       notify_callback=None,
                       delete_files=True):
        """ @delete_files = Delete data files after create the iso """
        self.target_path = adjust_path(target_path)
        self.slices = slices
        self.notify_callback = notify_callback
        self.delete_files = delete_files
        self.timer = Timer(self.notify_percent)
        self.process = None

    def notify_percent(self):
        if self.process is not None:
            if self.process.stderr is not None:
                line = self.process.stderr.readline()
                line = line.split()
                try:
                    if not line[2]=="estimate":
                        return None
                except IndexError:
                    return None

                try:
                    percent = int(line[0].split('.')[0])
                    self.notify_callback("progress", {"percent": percent})
                except IndexError:
                    return None

    def run(self):
        volumes = self.slices.keys()
        volumes.sort()
        self.timer.start()
        for volume in volumes:
            self.notify_callback("iso", {"volume": volume,
                                         "total": len(volumes)})

            slist = ' '.join(self.slices[volume])
            cmd = "mkisofs -J -R -o {0}iso{1}.iso {2}".format(self.target_path,
                                                              volume,
                                                              slist)

            self.process = RunCmd(cmd)
            self.process.run()
            r = self.process.wait()

            if self.delete_files:
                cmd = "rm {0}".format(slist)
                self.process = RunCmd(cmd)
                self.process.run()
                r = self.process.wait()

            self.process = None

        self.stop()

    def stop(self):
        self.timer.stop()
        if self.process is not None:
            self.process.stop()


