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
import gtk
import subprocess
import shlex
import urllib
import urllib2
import json
import urlparse
import gobject

import ServerConf
from firstboot_lib import PageWindow, FirstbootEntry

import gettext
from gettext import gettext as _
gettext.textdomain('firstboot')

__REQUIRED__ = False

__TITLE__ = _('Link workstation to a server')

__CONFIG_FILE_VERSION__ = '1.0'

__URLOPEN_TIMEOUT__ = 5
__LDAP_BAK_FILE__ = '/etc/ldap.conf.firstboot.bak'
__LDAP_CONF_SCRIPT__ = 'firstboot-ldapconf.sh'

__STATUS_TEST_PASSED__ = 0
__STATUS_CONFIG_CHANGED__ = 1
__STATUS_CONNECTING__ = 2
__STATUS_ERROR__ = 3


def get_page(options=None):

    page = LinkToServerConfEditorPage(options)
    return page

class LinkToServerConfEditorPage(PageWindow.PageWindow):
    __gtype_name__ = "LinkToServerConfEditorPage"

    __gsignals__ = {
        'page-changed': (
            gobject.SIGNAL_RUN_LAST,
            gobject.TYPE_NONE,
            (gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_PYOBJECT)
        )
    }

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

        self.lblDescription = self.builder.get_object('lblDescription')
        self.lblVersionValue = self.builder.get_object('lblVersionValue')
        self.txtOrganization = self.builder.get_object('txtOrganization')
        self.txtUrlLDAP = self.builder.get_object('txtUrlLDAP')
        self.txtBaseDN = self.builder.get_object('txtBaseDN')
        self.txtBindDN = self.builder.get_object('txtBindDN')
        self.txtPassword = self.builder.get_object('txtPassword')
        self.txtUrlChef = self.builder.get_object('txtUrlChef')
        self.txtUrlChefCert = self.builder.get_object('txtUrlChefCert')
        self.btnCancel = self.builder.get_object('btnCancel')
        self.btnApply = self.builder.get_object('btnApply')

        self.translate()

        container = builder.get_object('ContainerWindow')
        page = builder.get_object('LinkToServerConfEditorPage')
        container.remove(page)
        self.page = page

        self.cmd_options = options
        self.fbe = FirstbootEntry.FirstbootEntry()

    def set_params(self, params):
        if 'server_conf' in params:
            self.server_conf = params['server_conf']
            if not self.server_conf is None:
                self.lblVersionValue.set_label(self.server_conf.get_version())
                self.txtOrganization.set_text(self.server_conf.get_organization())
                self.txtUrlLDAP.set_text(self.server_conf.get_ldap_conf().get_url())
                self.txtBaseDN.set_text(self.server_conf.get_ldap_conf().get_basedn())
                self.txtBindDN.set_text(self.server_conf.get_ldap_conf().get_binddn())
                self.txtPassword.set_text(self.server_conf.get_ldap_conf().get_password())
                self.txtUrlChef.set_text(self.server_conf.get_chef_conf().get_url())
                self.txtUrlChefCert.set_text(self.server_conf.get_chef_conf().get_pem_url())

        else:
            self.server_conf = ServerConf.ServerConf()

    def is_associated(self):
        return os.path.exists(__LDAP_BAK_FILE__)

    def _bold(self, str):
        return '<b>%s</b>' % str

    def translate(self):
        desc = _('When a workstation is linked to a GECOS server it can be \
managed remotely and existing users in the server can login into \
the workstation.\n\n')

        if not self.is_associated():
            desc_detail = _('For linking this workstation, type the URL where the \
configuration resides and click on "Link".')
        else:
            desc_detail = _('This workstation is currently linked to a GECOS \
server. If you want to unlink it click on "Unlink".')

        self.builder.get_object('lblDescription').set_text(desc + desc_detail)

        self.builder.get_object('lblVersion').set_label(_('Version'))
        self.builder.get_object('lblOrganization').set_label(_('Organization'))
        self.builder.get_object('lblLDAPInfo').set_markup(self._bold(_('LDAP Information')))
        self.builder.get_object('lblUrlLDAP').set_label('URL')
        self.builder.get_object('lblBaseDN').set_label('Base DN')
        self.builder.get_object('lblBindDN').set_label('Bind DN')
        self.builder.get_object('lblPassword').set_label(_('Password'))
        self.builder.get_object('lblChefInfo').set_markup(self._bold(_('Chef information')))
        self.builder.get_object('lblUrlChef').set_label('URL')
        self.builder.get_object('lblUrlChefCert').set_label(_('Certificate URL'))

        self.builder.get_object('btnCancel').set_label(_('Cancel'))
        self.builder.get_object('btnApply').set_label(_('Apply'))

    def get_widget(self):
        return self.page

    def on_btnCancel_Clicked(self, button):
        self.emit('page-changed', 'linkToServer', 'LinkToServer', {})

    def on_btnApply_Clicked(self, button):

        self.show_status()

        if self.is_associated():
            self.unlink_from_server()

        else:
            self.link_to_server()

    def show_status(self, status=None, exception=None):

        icon_size = gtk.ICON_SIZE_BUTTON

        if status == None:
            self.imgStatus.set_visible(False)
            self.lblStatus.set_visible(False)

        elif status == __STATUS_TEST_PASSED__:
            self.imgStatus.set_from_stock(gtk.STOCK_APPLY, icon_size)
            self.imgStatus.set_visible(True)
            self.lblStatus.set_label(_('The configuration file is valid'))
            self.lblStatus.set_visible(True)

        elif status == __STATUS_CONFIG_CHANGED__:
            self.imgStatus.set_from_stock(gtk.STOCK_APPLY, icon_size)
            self.imgStatus.set_visible(True)
            self.lblStatus.set_label(_('The configuration was updated successfully'))
            self.lblStatus.set_visible(True)

        elif status == __STATUS_ERROR__:
            self.imgStatus.set_from_stock(gtk.STOCK_DIALOG_ERROR, icon_size)
            self.imgStatus.set_visible(True)
            self.lblStatus.set_label(str(exception.args[0]))
            self.lblStatus.set_visible(True)

        elif status == __STATUS_CONNECTING__:
            self.imgStatus.set_from_stock(gtk.STOCK_CONNECT, icon_size)
            self.imgStatus.set_visible(True)
            self.lblStatus.set_label(_('Trying to connect...'))
            self.lblStatus.set_visible(True)
