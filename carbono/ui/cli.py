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
import errno
import sys
import signal
from threading import Lock

from carbono.image_restorer import ImageRestorer
from carbono.image_creator import ImageCreator
from carbono.information import Information
from carbono.utils import *
from carbono.config import *

class Cli:

    def __init__(self):
        self.parser = optparse.OptionParser(usage=self.usage(),
                                            version=get_version())
        self.lock = Lock()
        self._set_options()
        self._register_signals()
        self.operation = None

    def _register_signals(self):
        signal.signal(signal.SIGINT, self.cancel_operation)
        signal.signal(signal.SIGUSR1, self.cancel_operation)

    def cancel_operation(self, signal=None, frame=None):
        if self.operation is not None:
            self.operation.cancel()

    def usage(self):
        usage = "usage: %prog [options]\n"
        usage += "\nCreating: \n"
        usage += "\t%prog -s /dev/sda -o /media/external_hd\n"
        usage += "\t%prog -s /dev/sda1 -o /media/external_hd -r -z -c 0\n"
        usage += "\t%prog -s /dev/sda -o /media/external_hd -p 4G -m\n"
        usage += "\nRestoring: \n"
        usage += "\t%prog -t /dev/sda -i /media/external_hd\n"
        usage += "\t%prog -t /dev/sda -i /media/external_hd -x 1,3 -e\n"
        return usage

    def _set_options(self):
        """ """
        create_group = optparse.OptionGroup(self.parser,
                                "Creating Image Options",)
        restore_group = optparse.OptionGroup(self.parser,
                                 "Restoring Image Options",)
        information_group = optparse.OptionGroup(self.parser,
                                 "Image Information Options",)

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
                                "the level of compression; 0 for no "
                                "compression, 1 is fastest and produces "
                                "the least compression, 9 is slowest and "
                                "produces the most. "
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
                                help="Fill the filesystem with zeros. "
                                "Because Raw image copies every block of "
                                "the filesystem this will aid compression "
                                "of the image (If compression is enabled).",)
        create_group.add_option("-p", "--split", 
                                dest="split_size",
                                type="string",
                                help="Split the image file into smaller "
                                "chunks of required size.",)
        restore_group.add_option("-t", "--target-device", 
                                 dest="target_device",)
        restore_group.add_option("-i", "--image-folder", 
                                 dest="image_folder",)
        restore_group.add_option("-x", "--image-partitions", 
                                dest="partition_numbers",
                                help="Restore only the given "
                                "partition number(s) (Comma separated). "
                                "ONLY FOR DISK RECOVERIES. "
                                "[Ex: 1,2,3]",)
        restore_group.add_option("-e", "--expand", 
                                dest="expand", 
                                action="store_true",
                                default=False,
                                help="If possible resize the last partition "
                                "until it fills the whole disk. "
                                "ONLY FOR DISK RECOVERIES.",)
        information_group.add_option("-q", "--image-information", 
                                dest="image_folder",
                                help="Show the information about the image.",)

        self.parser.add_option_group(create_group)
        self.parser.add_option_group(restore_group)
        self.parser.add_option_group(information_group)

    def status(self, action, dict={}):
        """ """
        self.lock.acquire()
        response = None
        if action == "progress":
            sys.stdout.write("%d%%\r" % dict["percent"])

        elif action == "finish":
            sys.stdout.write("Finished.\r\n")

        elif action == "checking_filesystem":
            sys.stdout.write("Checking filesystem of %s...\n" %
                             dict["device"])

        elif action == "expand":
            sys.stdout.write("Expanding filesystem of %s...\n" %
                             dict["device"])

        elif action == "filling_with_zeros":
            sys.stdout.write("Zeroing filesystem of %s...\n" %
                             dict["device"])

        elif action == "iso":
            sys.stdout.write("Creating ISO %d of %d...\n" %
                            (dict["volume"], dict["total"]))

        elif action == "canceled":
            sys.stdout.write("\r%s operation canceled!\n" % 
                             dict["operation"])

        elif action == "base_files_not_found":
            sys.stdout.write("\nCarbono files cannt be found in %s.\n" \
                             % dict["device"])
            response = raw_input("Please type another device " + \
                                 "(or leave blank to cancel): ")

        elif action == "file_not_found":
            sys.stdout.write("\nThe file %s cannot be found at %s.\n" \
                             % (dict["file"], dict["path"]))
            response = raw_input("Type the file location " + \
                                 "(or leave blank to cancel): ")
        
        sys.stdout.flush()
        self.lock.release()
        return response

    def run(self):
        """ """
        opt, remainder = self.parser.parse_args()
        if opt.source_device is not None:
            if opt.output_folder is None:
                self.parser.print_help()
                sys.exit(1)

            if not check_if_root():
                sys.stderr.write("You need to run this option as root.\n")
                sys.exit(1)

            split_size = 0
            if opt.split_size:
                l = opt.split_size[-1]
                if l.isdigit():
                    split_size = float(opt.split_size)
                else:
                    try:
                        split_size = float(opt.split_size[:-1])
                    except ValueError:
                        raise Exception("Invalid split size")

                    l = l.upper()
                    if l == 'M':
                        split_size = int(split_size *1024**2)
                    elif l == 'G':
                        split_size = int(split_size *1024**3)
                    else:
                        raise Exception("Cannot determine split size")

            self.operation = ImageCreator(opt.source_device, opt.output_folder,
                              self.status, opt.image_name,
                              opt.compressor_level, opt.raw, split_size,
                              opt.iso, opt.fill_with_zeros)
            self.operation.create_image()

        elif opt.target_device is not None:
            if opt.image_folder is None:
                self.parser.print_help()
                sys.exit(1)

            if not check_if_root():
                sys.stderr.write("You need to run this option as root.\n")
                sys.exit(1)

            partitions = None
            if opt.partition_numbers is not None:
                if not opt.partition_numbers.find(','):
                    partitions = list()
                    partitions.append(int(opt.partition_numbers))
                else:
                    plist = opt.partition_numbers.split(',')
                    partitions = map(lambda x: int(x), plist)

            self.operation = ImageRestorer(opt.image_folder, opt.target_device,
                               self.status, partitions, opt.expand)
            try:
                self.operation.restore_image()
            except OSError, e:
                if e.errno == errno.ECHILD:
                    pass

        elif opt.image_folder is not None:
            image_path = adjust_path(opt.image_folder)
            inf = Information(image_path)
            inf.load()
            sys.stdout.write("Name:\t\t\t%s\n" % inf.get_image_name())
            sys.stdout.write("Is disk:\t\t%s\n" % inf.get_image_is_disk())
            sys.stdout.write("Compressor level:\t%d\n\n" %
                             inf.get_image_compressor_level())
            sys.stdout.write("Partitions:\n")
            sys.stdout.write("%-10s %-15s %-15s %-16s %-36s\n" %
                            ("Number", "Type", "Size", "Label", "UUID"))
            for part in inf.get_partitions():
                uuid = ''
                label = ''
                if hasattr(part, "uuid"):
                    uuid = part.uuid
                if hasattr(part, "label"):
                    label = part.label
                sys.stdout.write("%-10d %-15s %-15d %-16s %-36s\n" %
                                (part.number, part.type, part.size,
                                 label, uuid))
            sys.stdout.flush()

        else:
            self.parser.print_help()

if __name__ == '__main__':
    cli = Cli()
    cli.run()

