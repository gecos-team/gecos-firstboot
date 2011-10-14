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
from gi.repository import Gtk

import ServerConf
from ServerConf import ServerConfException, LinkToLDAPException, LinkToChefException
from firstboot_lib import PageWindow, FirstbootEntry

import gettext
from gettext import gettext as _
gettext.textdomain('firstboot')


__REQUIRED__ = False

__TITLE__ = _('Link workstation to a server')

__STATUS_TEST_PASSED__ = 0
__STATUS_CONFIG_CHANGED__ = 1
__STATUS_CONNECTING__ = 2
__STATUS_ERROR__ = 3


def get_page(options=None):

    page = LinkToServerPage(options)
    return page

class LinkToServerPage(PageWindow.PageWindow):
    __gtype_name__ = "LinkToServerPage"

    def finish_initializing(self, builder, options=None):
        self.lblDescription = builder.get_object('lblDescription')
        self.chkUnlinkLDAP = builder.get_object('chkUnlinkLDAP')
        self.chkUnlinkChef = builder.get_object('chkUnlinkChef')
        self.radioManual = builder.get_object('radioManual')
        self.radioAuto = builder.get_object('radioAuto')
        self.lblUrl = builder.get_object('lblUrl')
        self.txtUrl = builder.get_object('txtUrl')
        self.imgStatus = builder.get_object('imgStatus')
        self.lblStatus = builder.get_object('lblStatus')
        self.btnLinkToServer = builder.get_object('btnLinkToServer')

        self.show_status()

        self.ldap_is_configured = ServerConf.ldap_is_configured()
        self.chef_is_configured = ServerConf.chef_is_configured()

        if self.ldap_is_configured and self.chef_is_configured:
            self.btnLinkToServer.set_sensitive(False)


        show_conf_fields = not (self.ldap_is_configured & self.chef_is_configured)
        if not show_conf_fields:
            self.radioManual.set_visible(False)
            self.radioAuto.set_visible(False)
            self.lblUrl.set_visible(False)
            self.txtUrl.set_visible(False)
            #~ self.btnLinkToServer.set_sensitive(True)

        self.chkUnlinkLDAP.set_visible(self.ldap_is_configured)
        self.chkUnlinkChef.set_visible(self.chef_is_configured)

        url_config = self.fbe.get_url()
        url = self.cmd_options.url

        if url == None or len(url) == 0:
            url = url_config

        if url == None or len(url) == 0:
            url = ''

        self.txtUrl.set_text(url)

    def translate(self):
        desc = _('When a workstation is linked to a GECOS server it can be \
managed remotely and existing users in the server can login into \
this workstation.\n\n')

        desc_detail = ''
        if not self.ldap_is_configured and not self.chef_is_configured:
            desc_detail = _('You can type the options manually or download \
a default configuration from the server.')

        elif self.ldap_is_configured and self.chef_is_configured:
            desc_detail = _('This workstation is currently linked to a GECOS \
server.')

        self.lblDescription.set_text(desc + desc_detail)
        self.chkUnlinkLDAP.set_label(_('Unlink from LDAP'))
        self.chkUnlinkChef.set_label(_('Unlink from Chef'))
        self.radioManual.set_label(_('Manual'))
        self.radioAuto.set_label(_('Automatic'))
        self.btnLinkToServer.set_label(_('Configure'))

    def on_chkUnlinkLDAP_toggle(self, button):
        if self.ldap_is_configured & self.chef_is_configured:
            active = button.get_active() | self.chkUnlinkChef.get_active()
            self.btnLinkToServer.set_sensitive(active)

    def on_chkUnlinkChef_toggle(self, button):
        if self.ldap_is_configured & self.chef_is_configured:
            active = button.get_active() | self.chkUnlinkLDAP.get_active()
            self.btnLinkToServer.set_sensitive(active)

    def on_radioManual_toggled(self, button):
        self.lblUrl.set_visible(False)
        self.txtUrl.set_visible(False)
        self.show_status()

    def on_radioAutomatic_toggled(self, button):
        self.lblUrl.set_visible(True)
        self.txtUrl.set_visible(True)
        self.show_status()

    def on_btnLinkToServer_Clicked(self, button):

        self.show_status()

        try:
            server_conf = None
            if self.radioAuto.get_active():
                url = self.txtUrl.get_text()
                server_conf = ServerConf.get_server_conf(url)

            self.emit(
                'subpage-changed',
                'linkToServer',
                'LinkToServerConfEditorPage',
                {
                    'server_conf': server_conf,
                    'ldap_is_configured': self.ldap_is_configured,
                    'unlink_from_ldap': self.chkUnlinkLDAP.get_active(),
                    'chef_is_configured': self.chef_is_configured,
                    'unlink_from_chef': self.chkUnlinkChef.get_active()
                }
            )

        except ServerConfException as e:
            self.show_status(__STATUS_ERROR__, e)

        except Exception as e:
            self.show_status(__STATUS_ERROR__, e)

    def show_status(self, status=None, exception=None):

        icon_size = Gtk.IconSize.BUTTON

        if status == None:
            self.imgStatus.set_visible(False)
            self.lblStatus.set_visible(False)

        elif status == __STATUS_TEST_PASSED__:
            self.imgStatus.set_from_stock(Gtk.STOCK_APPLY, icon_size)
            self.imgStatus.set_visible(True)
            self.lblStatus.set_label(_('The configuration file is valid.'))
            self.lblStatus.set_visible(True)

        elif status == __STATUS_CONFIG_CHANGED__:
            self.imgStatus.set_from_stock(Gtk.STOCK_APPLY, icon_size)
            self.imgStatus.set_visible(True)
            self.lblStatus.set_label(_('The configuration was updated successfully.'))
            self.lblStatus.set_visible(True)

        elif status == __STATUS_ERROR__:
            self.imgStatus.set_from_stock(Gtk.STOCK_DIALOG_ERROR, icon_size)
            self.imgStatus.set_visible(True)
            self.lblStatus.set_label(str(exception))
            self.lblStatus.set_visible(True)

        elif status == __STATUS_CONNECTING__:
            self.imgStatus.set_from_stock(Gtk.STOCK_CONNECT, icon_size)
            self.imgStatus.set_visible(True)
            self.lblStatus.set_label(_('Trying to connect...'))
            self.lblStatus.set_visible(True)
