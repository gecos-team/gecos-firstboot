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

    def finish_initializing(self):
        self.init_treeviewInterfaces()
        self.main_window.btnPrev.set_sensitive(False)

    def translate(self):
        self.ui.btnNetworkDialog.set_label(_('Configure a network card'))
        self.ui.lblDescription.set_text(_('This workstation needs a network connection in order to autenticate users, \
link to a GECOS server, and software installation.'))
        self.ui.lblDescription1.set_text(_('Available network cards are listed below:'))

    def load_page(self, params=None):
        self.main_window.connect('link-status', self.on_link_status_changed)

    def unload_page(self, params=None):
        self.main_window.disconnect('link-status')

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

        try:
            store = self.ui.treeviewInterfaces.get_model()
            store.clear()

            ifs = localifs()

            for _if in ifs:
                store.append([_if[0], _if[1]])

            self.ui.treeviewInterfaces.set_model(store)

        except AttributeError as e:
            pass

    def on_link_status_changed(self, sender, status):
        """ If status = True there are global connectivity.
        """
        self.load_treeviewInterfaces()
        self.emit('status-changed', 'network', status)

    def _render_column_name(self, column, cell, model, iter, user_param):

        value = model.get_value(iter, 0)
        text = '<b>%s</b>' % (value,)
        cell.set_property('markup', text)
        cell.set_property('width', 80)

    def _render_column_ip(self, column, cell, model, iter, user_param):

        value = model.get_value(iter, 1)
        cell.set_property('text', value)

    def next_page(self, load_page_callback):
        load_page_callback(firstboot.pages.autoConfig)
