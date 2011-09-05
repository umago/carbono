#!/usr/bin/python
# coding: utf-8

import gtk

class TreeViewDisks(gtk.TreeView):
    
    def __init__(self):
        gtk.TreeView.__init__(self)

        cell = gtk.CellRendererText()
        column_device = gtk.TreeViewColumn("Device", cell, text=0)
        column_device.set_expand(True)

        cell = gtk.CellRendererToggle()
        cell.set_property('activatable', True)
        cell.connect("toggled", self.device_toggled)
        column_selected = gtk.TreeViewColumn("Selected", cell)
        column_selected.add_attribute(cell, "active", 1)
        column_selected.set_expand(True)
    
        cell = gtk.CellRendererText()
        column_fs = gtk.TreeViewColumn("Filesystem", cell, text=2)
        column_fs.set_expand(True)

        cell = gtk.CellRendererText()
        column_size = gtk.TreeViewColumn("Size", cell, text=3)
        column_size.set_expand(True)

        cell = gtk.CellRendererText()
        column_used = gtk.TreeViewColumn("Used", cell, text=4)
        column_used.set_expand(True)

        column_refresh = gtk.TreeViewColumn("Refresh")
        column_refresh.set_clickable(True)
        column_refresh.connect("clicked", self.refresh)
        img = gtk.Image()
        img.set_from_stock(gtk.STOCK_REFRESH, gtk.ICON_SIZE_BUTTON)
        img.show()
        column_refresh.set_widget(img)

        self.treestore = gtk.TreeStore(str, bool, str, str, str)

        it = self.treestore.append(None, ["/dev/sda", False, '', '160 GB', ''])
        self.treestore.append(it, ["/dev/sda1", False, "ext3", "50 GB", "20 GB"])
        self.treestore.append(it, ["/dev/sda2", False, "ext3", "50 GB", "20 GB"])
        self.treestore.append(it, ["/dev/sda3", False, "ext3", "50 GB", "20 GB"])

        it = self.treestore.append(None, ["/dev/sdb", False, '', '160 GB', ''])
        self.treestore.append(it, ["/dev/sdb1", False, "ext3", "50 GB", "20 GB"])
        self.treestore.append(it, ["/dev/sdb2", False, "ext3", "50 GB", "20 GB"])
        self.treestore.append(it, ["/dev/sdb3", False, "ext3", "50 GB", "20 GB"])

        self.append_column(column_device)
        self.append_column(column_selected)
        self.append_column(column_fs)
        self.append_column(column_size)
        self.append_column(column_used)
        self.append_column(column_refresh)
        self.set_model(self.treestore)

        self.connect("row-activated", self.device_toggled)
        self.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_VERTICAL)
        self.set_rules_hint(True)

        self.expand_all()

        self.show_all()

    def refresh(self, widget):
        print "Refreshhh 8D~"

    def clear_tree(self):
        giter = self.treestore.get_iter_first()
        while giter:
            if self.treestore.iter_has_child(giter):
                for i in xrange(self.treestore.iter_n_children(giter)):
                    child = self.treestore.iter_nth_child(giter, i)
                    self.treestore.set_value(child, 1, False)
            self.treestore.set_value(giter, 1, False)
            giter = self.treestore.iter_next(giter)

    def toggle_group(self, parent, value):
        for i in xrange(self.treestore.iter_n_children(parent)):
            child = self.treestore.iter_nth_child(parent, i)
            self.treestore.set_value(child, 1, value)

    def device_toggled(self, widget, path, col=None):
        """Select or unselected the toggled device"""
        self.clear_tree()
        giter = self.treestore.get_iter(path)
        if self.treestore.iter_has_child(giter):
            if not self.treestore[path][1]:
                self.toggle_group(giter, True)
            else:
                self.toggle_group(giter, False)
        else:
            parent = self.treestore.iter_parent(giter)
            self.treestore.set_value(parent, 1, False)
            self.toggle_group(parent, False)

        self.treestore[path][1] = not self.treestore[path][1]

    def get_selected_device(self):
        """Returns the selected row informations"""
        giter = self.treestore.get_iter_first()

        while giter:
            if self.treestore.get_value(giter, 1):
                break
            if self.treestore.iter_has_child(giter):
                for i in xrange(self.treestore.iter_n_children(giter)):
                    child = self.treestore.iter_nth_child(giter, i)
                    if self.treestore.get_value(child, 1):
                        giter = child
                        break
            if self.treestore.get_value(giter, 1):
                break
            giter = self.treestore.iter_next(giter)

        if giter:
            device = self.treestore.get_value(giter, 0)
            return device

        return None


if __name__ == '__main__':
    treeview = TreeViewDisks()
    win = gtk.Window()
    win.add(treeview)
    win.show()
    gtk.main()
