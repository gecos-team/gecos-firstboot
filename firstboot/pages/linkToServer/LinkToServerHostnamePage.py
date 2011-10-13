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

from firstboot_lib import PageWindow, FirstbootEntry

import gettext
from gettext import gettext as _
gettext.textdomain('firstboot')


__REQUIRED__ = False

__TITLE__ = _('Describe this workstation')


def get_page(options=None):

    page = LinkToServerHostnamePage(options)
    return page

class LinkToServerHostnamePage(PageWindow.PageWindow):
    __gtype_name__ = "LinkToServerHostnamePage"

    # To construct a new instance of this method, the following notable
    # methods are called in this order:
    # __new__(cls)
    # __init__(self)
    # finish_initializing(self, builder)
    # __init__(self)
    #
    # For this reason, it's recommended you leave __init__ empty and put
    # your initialization code in finish_initializing

    def finish_initializing(self, builder, options=None):
        """Called while initializing this instance in __new__

        finish_initializing should be called after parsing the UI definition
        and creating a FirstbootWindow object with it in order to finish
        initializing the start of the new FirstbootWindow instance.
        """

        # Get a reference to the builder and set up the signals.
        self.builder = builder
        self.ui = builder.get_ui(self, True)

        self.lblDescription = builder.get_object('lblDescription')
        self.imgStatus = builder.get_object('imgStatus')
        self.lblStatus = builder.get_object('lblStatus')
        self.lblHostname = builder.get_object('lblHostname')
        self.txtHostname = builder.get_object('txtHostname')
        self.btnBack = builder.get_object('btnBack')
        self.btnAccept = builder.get_object('btnAccept')

        container = builder.get_object(self.__page_container__)
        page = builder.get_object(self.__gtype_name__)
        container.remove(page)
        self.page = page

        self.translate()
        self.imgStatus.set_visible(False)
        self.lblStatus.set_visible(False)

        self.cmd_options = options
        self.fbe = FirstbootEntry.FirstbootEntry()

        self.hostnames = []

    def translate(self):
        desc = _('This workstation is going to be linked to a Chef server, \
therefore it must be given a host name. That name will be used for \
uniquely identify this workstation.')

        self.lblDescription.set_text(desc)
        self.lblHostname.set_label(_('Hostname'))
        self.btnBack.set_label(_('Back'))
        self.btnAccept.set_label(_('Aceptar'))

    def set_params(self, params):

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

    def get_widget(self):
        return self.page

    def on_txtHostname_changed(self, entry):
        text = self.txtHostname.get_text()
        for name in self.hostnames:
            if name == text:
                #self.txtHostname.modify_text(Gtk.StateFlags.NORMAL, Gdk.Color(255, 0, 0))
                self.show_error(_('The host name is in use.'))
                self.btnAccept.set_sensitive(False)
                return

        self.show_error()
        self.btnAccept.set_sensitive(True)

    def on_btnAccept_Clicked(self, button):

        hostname = self.txtHostname.get_text()

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

        self.emit('subpage-changed', 'linkToServer',
                  'LinkToServerResultsPage',
                  {'result': result, 'server_conf': self.server_conf,
                   'messages': messages})

    def on_btnBack_clicked(self, button):
        self.emit('subpage-changed', 'linkToServer',
                  'LinkToServerConfEditorPage', {'server_conf': self.server_conf})

    def show_error(self, message=None):
        if message is None:
            self.imgStatus.set_visible(False)
            self.lblStatus.set_visible(False)
            return

        self.imgStatus.set_from_stock(Gtk.STOCK_DIALOG_ERROR, Gtk.IconSize.BUTTON)
        self.lblStatus.set_label(message)
        self.imgStatus.set_visible(True)
        self.lblStatus.set_visible(True)
