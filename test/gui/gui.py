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

import gtk
import gettext
_ = gettext.gettext

from treeview_disks import TreeViewDisks

class Gui:

    def __init__(self):
        """  """
        self.builder = gtk.Builder()
        self.builder.add_from_file("carbono.glade")
        self.builder.connect_signals(self)

    def run(self):
        """  """
        self._init_widgets()
        self._setup_widgets()

        self.window_main.show()
        gtk.main()

    def _init_widgets(self):
        """  """
        self.window_main = self.builder.get_object("window_main")
        self.notebook = self.builder.get_object("notebook_main")
        self.dialog_create_advanced = self.builder.get_object("dialog_create_advanced")
        self.dialog_about = self.builder.get_object("dialog_about")
        self.dialog_harddisk = self.builder.get_object("dialog_harddisk")
        self.dialog_network = self.builder.get_object("dialog_network")

    def _setup_widgets(self):
        """  """
        self.window_main.set_resizable(False)
        self.window_main.set_size_request(600, 500)

        # About dialog
        self.dialog_about.set_name("carbono")

        # Painting
        self.window_main.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#f7f6f5"))
        self.dialog_create_advanced.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#f7f6f5"))
        self.dialog_harddisk.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#f7f6f5"))
        self.dialog_network.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#f7f6f5"))
        
        eventbox_menu = self.builder.get_object("eventbox_menu")
        eventbox_progress = self.builder.get_object("eventbox_progress")
        eventbox_progressbar = self.builder.get_object("eventbox_progressbar")
        eventbox_create_image = self.builder.get_object("eventbox_create_image")
        eventbox_create_advanced = self.builder.get_object("eventbox_create_advanced")
        eventbox_harddisk = self.builder.get_object("eventbox_harddisk")
        eventbox_network = self.builder.get_object("eventbox_network")

        eventbox_menu.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#3c3b37"))
        eventbox_progress.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#3c3b37"))
        eventbox_progressbar.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#3c3b37"))
        eventbox_create_image.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#3c3b37"))
        eventbox_create_advanced.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#3c3b37"))
        eventbox_harddisk.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#3c3b37"))
        eventbox_network.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#3c3b37"))

        # Attach the treeview
        scrolledwindow_new_disks = self.builder.get_object("scrolledwindow_new_disks")
        scrolledwindow_new_disks.add(TreeViewDisks())

    def about(self, widget):
        """Show about dialog"""
        self.dialog_about.run()
        self.dialog_about.hide()

    def menu(self, widget):
        """Go to menu screen"""
        self.notebook.set_current_page(0)

    def create_image(self, widget):
        """Go to create image screen"""
        self.notebook.set_current_page(2)

    def create_advanced(self, widget):
        """Show advanced dialog"""
        self.dialog_create_advanced.run()
        self.dialog_create_advanced.hide()

    def create_harddisk(self, widget):
        """Show harddisk dialog"""
        self.dialog_harddisk.run()
        self.dialog_harddisk.hide()

    def create_network(self, widget):
        """Show hnetwork dialog"""
        self.dialog_network.run()
        self.dialog_network.hide()

if __name__ == '__main__':
    gui = Gui()
    gui.run()
