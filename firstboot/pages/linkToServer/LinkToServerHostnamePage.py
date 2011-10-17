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
from gi.repository import Gtk, Gdk
import subprocess
import shlex
import json
import ServerConf

import LinkToServerConfEditorPage, LinkToServerResultsPage
from firstboot_lib import PageWindow

import gettext
from gettext import gettext as _
gettext.textdomain('firstboot')


__REQUIRED__ = False

__TITLE__ = _('Describe this workstation')


def get_page(main_window):

    page = LinkToServerHostnamePage(main_window)
    return page

class LinkToServerHostnamePage(PageWindow.PageWindow):
    __gtype_name__ = "LinkToServerHostnamePage"

    def finish_initializing(self):
        self.ui.imgStatus.set_visible(False)
        self.ui.lblStatus.set_visible(False)
        self.main_window.btnNext.set_sensitive(False)

        self.hostnames = []

    def translate(self):
        desc = _('This workstation is going to be linked to a Chef server, \
therefore it must be given a host name. That name will be used for \
uniquely identify this workstation.')

        self.ui.lblDescription.set_text(desc)
        self.ui.lblHostname.set_label(_('Hostname'))

    def load_page(self, params=None):

        # NOTE: The boolean values in the dict object become tuples
        # after the assignment ???
        # The workaround is to reassign the first element of the tuple.

        self.link_ldap = params['link_ldap'],
        self.link_ldap = self.link_ldap[0]
        self.unlink_ldap = params['unlink_ldap'],
        self.unlink_ldap = self.unlink_ldap[0]
        self.link_chef = params['link_chef'],
        self.link_chef = self.link_chef[0]
        self.unlink_chef = params['unlink_chef']
        #self.unlink_chef = self.unlink_chef[0]
        self.hostnames = params['used_hostnames']

        self.server_conf = params['server_conf']

    def on_txtHostname_changed(self, entry):
        text = self.ui.txtHostname.get_text()
        for name in self.hostnames:
            if name == text:
                #self.txtHostname.modify_text(Gtk.StateFlags.NORMAL, Gdk.Color(255, 0, 0))
                self.show_error(_('The host name is in use.'))
                self.main_window.btnNext.set_sensitive(False)
                return

        self.show_error()
        self.main_window.btnNext.set_sensitive(True)

    def previous_page(self, load_page_callback):
        load_page_callback(LinkToServerConfEditorPage, {
            'server_conf': self.server_conf
        })
        #~ self.emit('subpage-changed', 'linkToServer',
                  #~ 'LinkToServerConfEditorPage', {'server_conf': self.server_conf})

    def next_page(self, load_page_callback):

        hostname = self.ui.txtHostname.get_text()

        if len(hostname) == 0:
            self.show_error(_('The host name cannot be empty.'))
            return

        elif hostname in self.hostnames:
            self.show_error(_('The host name already exists in the Chef server.'))
            return

        self.server_conf.get_chef_conf().set_hostname(hostname)

        result, messages = ServerConf.setup_server(
            server_conf=self.server_conf,
            link_ldap=self.link_ldap,
            unlink_ldap=self.unlink_ldap,
            link_chef=self.link_chef,
            unlink_chef=self.unlink_chef
        )

        load_page_callback(LinkToServerResultsPage, {
            'server_conf': self.server_conf,
            'result': result,
            'messages': messages
        })

        #~ self.emit('subpage-changed', 'linkToServer',
                  #~ 'LinkToServerResultsPage',
                  #~ {'result': result, 'server_conf': self.server_conf,
                   #~ 'messages': messages})

    def show_error(self, message=None):
        if message is None:
            self.ui.imgStatus.set_visible(False)
            self.ui.lblStatus.set_visible(False)
            return

        self.ui.imgStatus.set_from_stock(Gtk.STOCK_DIALOG_ERROR, Gtk.IconSize.BUTTON)
        self.ui.lblStatus.set_label(message)
        self.ui.imgStatus.set_visible(True)
        self.ui.lblStatus.set_visible(True)
