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

import optparse
import os
import sys

from carbono.image_restorer import ImageRestorer
from carbono.image_creator import ImageCreator

class Cli:

    def __init__(self):
        self.parser = optparse.OptionParser()
        self._set_options()

    def _set_options(self):
        """ """
        create_group = optparse.OptionGroup(self.parser,
                                "Creating Image Options",)
        restore_group = optparse.OptionGroup(self.parser,
                                 "Restoring Image Options",)

        create_group.add_option("-s", "--source-device", 
                                dest="source_device",)
        create_group.add_option("-o", "--output-folder", 
                                dest="output_folder",)
        create_group.add_option("-n", "--image-name", 
                                dest="image_name", 
                                default="image",
                                help="[default: %default]",)
        create_group.add_option("-c", "--compressor-level", 
                                dest="compressor_level",
                                type="int",
                                default=6,
                                help="An integer from 0 to 9 controlling "
                                "the level of compression; 0 for no compression, "
                                "1 is fastest and produces the least compression, "
                                "9 is slowest and produces the most. "
                                "[default: %default]",)
        create_group.add_option("-r", "--raw", 
                                dest="raw", 
                                action="store_true",
                                default=False,
                                help="Create raw images.",)
        create_group.add_option("-m", "--iso", 
                                dest="iso", 
                                action="store_true",
                                default=False,
                                help="Create iso(s) from file(s).",)
        create_group.add_option("-z", "--fill-with-zeros", 
                                dest="fill_with_zeros", 
                                action="store_true",
                                default=False,
                                help="Fill the filesystem with zeros. Because Raw image "
                                "copies every block of the filesystem this will aid "
                                "compression of the image (If compression is enabled).",)
        create_group.add_option("-p", "--split", 
                                dest="split_size",
                                type="string",
                                help="Split the image file into smaller chunks "
                                "of required size (in MB).",)
        restore_group.add_option("-t", "--target-device", 
                                 dest="target_device",)
        restore_group.add_option("-i", "--image-folder", 
                                 dest="image_folder",)

        self.parser.add_option_group(create_group)
        self.parser.add_option_group(restore_group)

    def status(self, action, dict={}):
        """ """
        if action == "progress":
            sys.stdout.write("%d%%\r" % dict["percent"])
        elif action == "finish":
            sys.stdout.write("finished.\n")
        elif action == "checking_filesystem":
            sys.stdout.write("Checking filesystem of %s...\n" % dict["device"])
        elif action == "filling_with_zeros":
            sys.stdout.write("Zeroing filesystem of %s...\n" % dict["device"])

        sys.stdout.flush()

    def run(self):
        """ """
        opt, remainder = self.parser.parse_args()
        if opt.source_device is not None:
            if opt.output_folder is None:
                self.parser.print_help()
                sys.exit(1)

            split_size = 0
            if opt.split_size:
                l = opt.split_size[-1]
                if l.isdigit():
                    split_size = int(opt.split_size)
                else:
                    l = l.upper()
                    if l == 'M':
                        split_size = int(opt.split_size[:-1]) * 1024 * 1024
                    elif l == 'G':
                        split_size = int(opt.split_size[:-1]) * 1024 * 1024 * 1024
                    else:
                        raise Exception("Cannt determine split size")

            ic = ImageCreator(opt.source_device, opt.output_folder, \
                              opt.image_name, opt.compressor_level, \
                              opt.raw, split_size, opt.iso, opt.fill_with_zeros)
            ic.connect_status_callback(self.status)
            ic.create_image()

        elif opt.target_device:
            if opt.image_folder is None:
                self.parser.print_help()
                sys.exit(1)

            ir = ImageRestorer(opt.image_folder, opt.target_device)
            ir.connect_status_callback(self.status)
            ir.restore_image()

if __name__ == '__main__':
    cli = Cli()
    cli.run()

