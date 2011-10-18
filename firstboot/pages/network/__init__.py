# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-

# This file is part of Guadalinex
#
# This software is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this package; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA

__author__ = "Antonio Hernández <ahernandez@emergya.com>"
__copyright__ = "Copyright (C) 2011, Junta de Andalucía <devmaster@guadalinex.org>"
__license__ = "GPL-2"


import os
from gi.repository import GObject, Gtk
from firstboot_lib import PageWindow

import gettext
from gettext import gettext as _
gettext.textdomain('firstboot')

import firstboot.pages
from interface import localifs, internet_on

__REQUIRED__ = True

__TITLE__ = _('Configure the network')

def get_page(main_window):

    page = NetworkPage(main_window)
    return page

class NetworkPage(PageWindow.PageWindow):
    __gtype_name__ = "NetworkPage"

    __gsignals__ = {
        'link-status': (GObject.SignalFlags.ACTION, None, (GObject.TYPE_BOOLEAN,))
    }

    def finish_initializing(self):
        self.timer_ret = True
        self.init_treeviewInterfaces()
        self.main_window.btnPrev.set_sensitive(False)

    def translate(self):
        self.ui.btnNetworkDialog.set_label(_('Configure the network'))
        self.ui.lblDescription.set_text(_('You need to be connected to the network \
for linking this workstation to a GECOS server and for installing software.'))
        self.ui.lblDescription1.set_text(_('Below are shown the current \
detected interfaces.'))

    def load_page(self, params=None):
        self.timer_ret = True
        GObject.timeout_add_seconds(1, self.load_treeviewInterfaces)

    def unload_page(self, params=None):
        self.timer_ret = False

    def on_btnNetworkDialog_Clicked(self, button):
        cmd = 'nm-connection-editor'
        os.spawnlp(os.P_NOWAIT, cmd, cmd)
        self.emit('status-changed', 'network', True)

    def init_treeviewInterfaces(self):

        tvcolumn = Gtk.TreeViewColumn(_('Interface'))
        cell = Gtk.CellRendererText()
        tvcolumn.pack_start(cell, True)
        tvcolumn.set_cell_data_func(cell, self._render_column_name)
        self.ui.treeviewInterfaces.append_column(tvcolumn)

        tvcolumn = Gtk.TreeViewColumn(_('IP'))
        cell = Gtk.CellRendererText()
        tvcolumn.pack_start(cell, True)
        tvcolumn.set_cell_data_func(cell, self._render_column_ip)
        self.ui.treeviewInterfaces.append_column(tvcolumn)

        selection = self.ui.treeviewInterfaces.get_selection()
        selection.set_mode(Gtk.SelectionMode.NONE)

        self.load_treeviewInterfaces()

    def load_treeviewInterfaces(self):

        n_ifaces = 0

        store = self.ui.treeviewInterfaces.get_model()
        store.clear()

        ifs = localifs()
        #print ifs

        for _if in ifs:
            store.append([_if[0], _if[1]])
            if _if[0] != 'lo' and len(_if[1]) > 0:
                n_ifaces += 1

        self.emit('link-status', n_ifaces > 0)
        self.emit('status-changed', 'network', bool(n_ifaces > 0))
        self.ui.treeviewInterfaces.set_model(store)

        return self.timer_ret

    def _render_column_name(self, column, cell, model, iter, user_param):

        value = model.get_value(iter, 0)
        text = '<b>%s</b>' % (value,)
        cell.set_property('markup', text)
        cell.set_property('width', 80)

    def _render_column_ip(self, column, cell, model, iter, user_param):

        value = model.get_value(iter, 1)
        cell.set_property('text', value)

    def next_page(self, load_page_callback):
        load_page_callback(firstboot.pages.pcLabel)
