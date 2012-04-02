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

__author__ = "David Amian <damian@emergya.com>"
__copyright__ = "Copyright (C) 2011, Junta de Andalucía <devmaster@guadalinex.org>"
__license__ = "GPL-2"


import os
import shlex
import subprocess
from gi.repository import Gtk
from firstboot_lib import PageWindow
from firstboot import serverconf

import gettext
from gettext import gettext as _
gettext.textdomain('firstboot')

import firstboot.pages


__REQUIRED__ = False

__TITLE__ = _('Auto Configuration')


def get_page(main_window):

    page = AutoConfigPage(main_window)
    return page


class AutoConfigPage(PageWindow.PageWindow):
    __gtype_name__ = "AutoConfigPage"

    def finish_initializing(self):
        self.set_status(None)

    def load_page(self, params=None):
        self.emit('status-changed', 'autoConfig', not __REQUIRED__)
        

        self.ui.chkAutoconf.set_visible(False)
        url_config = self.fbe.get_url()
        url = self.cmd_options.url

        if url == None or len(url) == 0:
            url = url_config

        if url == None or len(url) == 0:
            url = ''

        self.ui.txtAutoconf.set_text(url)
        if serverconf.json_is_cached():
            self.ui.boxCheckAutoconf.set_visible(True)
            self.ui.chkAutoconf.set_visible(True)
            self.ui.txtAutoconf.set_sensitive(False)
            self.serverconf = serverconf.get_server_conf(None)

    def translate(self):
        desc = _('Parameters can be filled automatically if an autoconfiguration file is available in your GECOS server.')

        self.ui.lblDescription.set_text(desc)
        self.ui.chkAutoconf.set_label(_('Download a new file with default configuration parameters.'))
        self.ui.lblAutoconf.set_label(_('Autoconfig file URL'))

    def on_chkAutoconf_toggled(self, widget):
        self.ui.txtAutoconf.set_sensitive(self.ui.chkAutoconf.get_active())

    def set_status(self, code, description=''):

        self.ui.imgStatus.set_visible(code != None)
        self.ui.lblStatus.set_visible(code != None)

        if code == None:
            return

        if code == 0:
            icon = Gtk.STOCK_YES

        else:
            icon = Gtk.STOCK_DIALOG_ERROR

        self.ui.imgStatus.set_from_stock(icon, Gtk.IconSize.MENU)
        self.ui.lblStatus.set_label(description)

    def previous_page(self, load_page_callback):
  
        load_page_callback(firstboot.pages.network)

    def next_page(self, load_page_callback):
        if not serverconf.json_is_cached() or (serverconf.json_is_cached() and self.ui.chkAutoconf.get_active()):
           url = self.ui.txtAutoconf.get_text()
           if url != '' and url != None:
               try:
                   if serverconf.json_is_cached():
                       serverconf.clean_json_cached()
                   self.serverconf = serverconf.get_server_conf(url)

               except Exception as e:
                    self.set_status(1, str(e))
                    return
           
 
        load_page_callback(firstboot.pages.dateSync)
