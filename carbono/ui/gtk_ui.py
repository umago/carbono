#!/usr/bin/python
#
# Carbono gtk gui
#
# encoding: utf-8

import os
import sys
import urllib
import urllib2
import time
import traceback

import pygtk
import gtk
import gobject
import pango
import glob

from threading import Thread
from multiprocessing import Queue

import gettext
import __builtin__
__builtin__._ = gettext.gettext

class Gtk_UI:
    (COLUMN_DEVICE, COLUMN_FS, COLUMN_SIZE, COLUMN_USED) = range(4)
    def __init__(self, backend=None):
        """Initializes web UI for carbono"""
        self.backend = backend
        self.window = gtk.Window()
        self.window.set_title(_("Carbono client"))
        self.window.set_default_size(640, 480)
        self.window.connect('destroy', self.quit)

        self.main_vbox = gtk.VBox()
        self.window.add(self.main_vbox)

        # for talking with threads
        self.events = Queue()
        gobject.timeout_add(500, self.check_events)

        self.notebook = gtk.Notebook()
        self.main_vbox.pack_start(self.notebook)

        self.notebook.append_page(self.create_carbono(), gtk.Label(_("Create an image")))

        self.window.show_all()

        # status bar
        self.statusbar = gtk.Statusbar()
        self.main_vbox.pack_start(self.statusbar, False, False)
        self.messages = []

        self.update(_("Ready for action"))

    def update(self, text):
        """Updates status message"""
        for id in self.messages:
            self.statusbar.pop(id)
            self.messages.remove(id)
        id = self.statusbar.push(int(time.time()), text)
        self.messages.append(id)

    def check_events(self):
        """Checks for pending events"""
        while not self.events.empty():
            event, params = self.events.get()
            print "received event %s" % event
        gobject.timeout_add(500, self.check_events)

    def quit(self, widget):
        gtk.main_quit()

    def build_value_pair(self, sizegroup, text, value_text=None, value_sizegroup=None, editable=True):
        """Builds a value pair"""
        hbox = gtk.HBox(spacing=10)
        name = gtk.Label(text)
        name.set_property("xalign", 0.0)
        hbox.pack_start(name, False, False)
        value = gtk.Entry()
        if value_text:
            value.set_text(value_text)
        if not editable:
            value.set_editable(False)
        hbox.pack_start(value, False, False)
        if sizegroup:
            sizegroup.add_widget(name)
        if value_sizegroup:
            value_sizegroup.add_widget(value)
        return hbox, value

    def create_carbono(self):
        """Creates a view for individual bug"""
        vbox = gtk.VBox()

        label = gtk.Label(_("Create image"))
        vbox.pack_start(label, False, False)

        # create the list of bugs view
        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)

        # list of levels
        lstore = gtk.ListStore(
                gobject.TYPE_STRING,
                gobject.TYPE_STRING,
                gobject.TYPE_STRING,
                gobject.TYPE_STRING,
                gobject.TYPE_STRING)

        # bugs treeview
        treeview = gtk.TreeView(lstore)
        treeview.set_rules_hint(True)
        treeview.set_search_column(self.COLUMN_DEVICE)
        treeview.connect('row-activated', self.partition_selected, lstore)

        renderer = gtk.CellRendererText()

        # column for device
        column = gtk.TreeViewColumn(_("Device"), renderer, text=self.COLUMN_DEVICE)
        column.set_sort_column_id(self.COLUMN_DEVICE)
        column.set_resizable(True)
        column.set_expand(False)
        treeview.append_column(column)

        # column for filesystem
        column = gtk.TreeViewColumn(_("File system"), renderer, text=self.COLUMN_FS)
        column.set_sort_column_id(self.COLUMN_FS)
        column.set_resizable(True)
        column.set_expand(False)
        treeview.append_column(column)

        # column for size
        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn(_("Size"), renderer, text=self.COLUMN_SIZE)
        column.set_sort_column_id(self.COLUMN_SIZE)
        column.set_resizable(False)
        column.set_expand(True)
        treeview.append_column(column)

        # column for used size
        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn(_("Used"), renderer, text=self.COLUMN_USED)
        column.set_sort_column_id(self.COLUMN_USED)
        column.set_resizable(False)
        column.set_expand(True)
        treeview.append_column(column)

        sw.add(treeview)

        vbox.pack_start(sw)

        sizegroup1 = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)
        sizegroup2 = gtk.SizeGroup(gtk.SIZE_GROUP_HORIZONTAL)

        hbox, image_hd = self.build_value_pair(sizegroup1, _("Hard-disk image to save"), "image.img", value_sizegroup=sizegroup2)
        vbox.pack_start(hbox, False, False)

        hbox, image_net = self.build_value_pair(sizegroup1, _("Network address to save"), "224.51.105.100", value_sizegroup=sizegroup2)
        vbox.pack_start(hbox, False, False)

        return vbox

    def partition_selected(self, treeview, path, col, model):
        """A partition was selected"""
        iter = model.get_iter(path)
        partition = model.get_value(iter, self.COLUMN_DEVICE)
        print partition

    def populate_partitions(self, bugs):
        """Updates list of partitions"""
        # update bugs view
        lstore = self.bugs_lstore
        lstore.clear()
        for id, status, desc in bugs:
            iter = lstore.append()
            lstore.set(iter,
                    self.COLUMN_ID, id,
                    self.COLUMN_GLPI, 0,
                    self.COLUMN_STATUS, status,
                    self.COLUMN_DESCR, desc
                    )
