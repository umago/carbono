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
                                help="An integer from 1 to 9 controlling "
                                "the level of compression; 1 is fastest and "
                                "produces the least compression, 9 is slowest "
                                "and produces the most. [default: %default]",)
        restore_group.add_option("-t", "--target-device", 
                                 dest="target_device",)
        restore_group.add_option("-i", "--image-folder", 
                                 dest="image_folder",)

        self.parser.add_option_group(create_group)
        self.parser.add_option_group(restore_group)

    def run(self):
        """ """
        options, remainder = self.parser.parse_args()
        if options.source_device is not None:
            if options.output_folder is None:
                self.parser.print_help()
                sys.exit(1)

            ic = ImageCreator(options.image_name,
                              options.source_device,
                              options.output_folder,
                              options.compressor_level)
            ic.create_image()

        elif options.target_device:
            if options.image_folder is None:
                self.parser.print_help()
                sys.exit(1)

            ir = ImageRestorer(options.image_folder, options.target_device)
            ir.restore_image()

if __name__ == '__main__':
    cli = Cli()
    cli.run()

