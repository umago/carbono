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

import os
import errno

from carbono.utils import *
from carbono.exception import *
from carbono.config import *

CARBONO_FILES = ("initram.gz", "vmlinuz")

class IsoCreator:
    def __init__(self, target_path, slices,
                       name = "image",
                       notify_callback=None,
                       is_disk=False):
        self.target_path = adjust_path(target_path)
        self.slices = slices
        self.name = name
        self.notify_callback = notify_callback
        self.is_disk = is_disk
        self.timer = Timer(self.notify_percent)
        self.process = None
        self.mount_point = None

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

    def mount_device(self, device):
        tmpd = make_temp_dir()
        ret = run_simple_command("mount {0} {1}".\
              format(device, tmpd))
        if ret is not 0:
            raise ErrorMountingFilesystem
        return tmpd        

    def find_carbono_files(self, path):
        dev_files = os.listdir(path)
        ret = True
        if filter(lambda x: not x in dev_files,
                      CARBONO_FILES):
            ret = False
        return ret

    def make_cfg(self):
        path = "/tmp/isolinux.cfg"
        template = "prompt 0\n\tdefault 1\nlabel 1\n\tkernel " + \
                   "vmlinuz\n\tappend initrd=initram.gz " + \
                   "rdinit=/sbin/init ramdisk_size=512000"
        with open(path, 'w') as f:
            f.write(template)
        return path

    def run(self):
        volumes = self.slices.keys()
        volumes.sort()
        self.timer.start()
        first_volume = True
        for volume in volumes:
            extra_params = ''
            self.notify_callback("iso", {"volume": volume,
                                         "total": len(volumes)})

            if first_volume:
                device = get_cdrom_device()
                while True:
                    error = False

                    try:
                        self.mount_point = self.mount_device(device)
                    except ErrorMountingFilesystem:
                        error = True

                    if error or not self.find_carbono_files(self.mount_point):
                        if not error:
                            run_simple_command("umount {0}".\
                                               format(self.mount_point))
                            error = True

                    if error:
                        device = self.notify_callback("base_files_not_found",
                                                     {"device": device})
                        if not device:
                            self.notify_callback("canceled",
                                                {"operation": "Creating ISO"})
                            self.stop()
                            return
                        continue

                    break

                # Add carbono files  
                map(lambda x: self.slices[volume].\
                    append(self.mount_point + x), CARBONO_FILES)

                # Bootloader
                self.slices[volume].append("/usr/lib/syslinux/isolinux.bin")
                self.slices[volume].append(self.make_cfg())

                if self.is_disk:
                    # Add the rest of files needed to
                    # restore the image
                    map(lambda x: self.slices[volume].\
                        append(self.target_path + x),
                        ("mbr.bin", "disk.dl","image.info"))
                        
            if first_volume:
                extra_params = "-joliet-long -b " + \
                "isolinux.bin -c " + \
                "boot.cat -no-emul-boot " + \
                "-boot-load-size 4 -boot-info-table"

            slist = ' '.join(self.slices[volume])
            cmd = "{0} -R -J -o {1}{2}{3}.iso {4} {5}".format(
                                                       which("mkisofs"),
                                                       self.target_path,
                                                       self.name,
                                                       volume,
                                                       extra_params,
                                                       slist)

            self.process = RunCmd(cmd)
            self.process.run()
            # TODO: check output of wait, in case
            # of no space left on device
            self.process.wait()

            self.process = None
            if first_volume:
                run_simple_command("umount {0}".format(self.mount_point))
                first_volume = False

        self.stop()

    def stop(self):
        self.timer.stop()
        if self.process is not None:
            self.process.stop()

