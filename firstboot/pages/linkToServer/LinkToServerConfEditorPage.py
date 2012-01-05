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


import LinkToServerResultsPage
import firstboot.pages.linkToServer
from firstboot_lib import PageWindow
from firstboot import serverconf
import os
import gettext
from gettext import gettext as _
gettext.textdomain('firstboot')

__REQUIRED__ = False


def get_page(main_window):

    page = LinkToServerConfEditorPage(main_window)
    return page


class LinkToServerConfEditorPage(PageWindow.PageWindow):
    __gtype_name__ = "LinkToServerConfEditorPage"

    def finish_initializing(self):

        self.update_server_conf = False
        self.link_ldap = False
        self.link_ad = False

    def load_page(self, params=None):
        if 'server_conf' in params:
            self.server_conf = params['server_conf']
            if not self.server_conf is None:
                self.ui.lblVersionValue.set_label(self.server_conf.get_version())
                self.ui.lblOrganizationValue.set_label(self.server_conf.get_organization())
                self.ui.txtUrlLDAP.set_text(self.server_conf.get_ldap_conf().get_url())
                self.ui.txtBaseDN.set_text(self.server_conf.get_ldap_conf().get_basedn())
                self.ui.txtBindDN.set_text(self.server_conf.get_ldap_conf().get_binddn())
                self.ui.txtPassword.set_text(self.server_conf.get_ldap_conf().get_password())
                self.ui.txtFqdnAD.set_text(self.server_conf.get_ad_conf().get_fqdn())
                self.ui.txtDnsDomain.set_text(self.server_conf.get_ad_conf().get_dns_domain())

        if not 'server_conf' in params or self.server_conf is None:
            self.ui.lblOrganization.set_visible(False)
            self.ui.lblNotes.set_visible(False)
            self.ui.lblNotesValue.set_visible(False)
            self.ui.lblOrganizationValue.set_visible(False)
            self.server_conf = serverconf.ServerConf()
        self.update_server_conf = True
        self.method = params['auth_method']
        if self.method == 'ldap':
            self.ui.adBox.set_visible(False)
            self.ui.ldapBox.set_visible(True)
            self.link_ldap = True
        else:
            os.system('DEBCONF_PRIORITY=critical DEBIAN_FRONTEND=noninteractive dpkg-reconfigure resolvconf')
            self.ui.ldapBox.set_visible(False)
            self.ui.adBox.set_visible(True)
            self.link_ad = True

        if params['ldap_is_configured'] or params['ad_is_configured']:
            self.ui.lblDescription.set_visible(False)

    def _bold(self, str):
        return '<b>%s</b>' % str

    def translate(self):
        desc = _('Insert your authentication configuration')

        self.ui.lblDescription.set_text(desc)

        self.ui.lblVersion.set_label(_('Version'))
        self.ui.lblOrganization.set_label(_('Organization'))
        self.ui.lblNotes.set_label(_('Notes'))
        self.ui.lblUrlLDAP.set_label('URL')
        self.ui.lblBaseDN.set_label('Base DN')
        self.ui.lblBindDN.set_label('Bind DN')
        self.ui.lblPassword.set_label(_('Password'))
        self.ui.lblFqdnAD.set_label('FQDN')
        self.ui.lblDnsDomain.set_label(_('Domain DNS'))

    def previous_page(self, load_page_callback):
        load_page_callback(firstboot.pages.linkToServer)

    def next_page(self, load_page_callback):
        if self.method == 'ad':
            retval = serverconf.auth_dialog(_('Authentication Required'),
                    _('You need enter Administrator credentials of Active Directory'))
            self.server_conf.get_ad_conf().set_user(retval[0])
            self.server_conf.get_ad_conf().set_passwd(retval[1])

        messages = []

        if self.method == 'ad':
            if not self.server_conf.get_ad_conf().validate():
                messages.append({'type': 'error', 'message': 'Please, check the Active Directory parameters.'})

        else:
            if not self.server_conf.get_ldap_conf().validate():
                messages.append({'type': 'error', 'message': 'Please, check the LDAP parameters.'})

        result = len(messages) == 0
        if result == True:
            result, messages = serverconf.setup_server(
                server_conf=self.server_conf,
                link_ldap=self.link_ldap,
                link_ad=self.link_ad
            )

        load_page_callback(LinkToServerResultsPage, {
            'result': result,
            'server_conf': self.server_conf,
            'messages': messages
         })

    def on_serverConf_changed(self, entry):
        if not self.update_server_conf:
            return
        if self.method == 'ldap':
            self.server_conf.get_ldap_conf().set_url(self.ui.txtUrlLDAP.get_text())
            self.server_conf.get_ldap_conf().set_basedn(self.ui.txtBaseDN.get_text())
            self.server_conf.get_ldap_conf().set_binddn(self.ui.txtBindDN.get_text())
            self.server_conf.get_ldap_conf().set_password(self.ui.txtPassword.get_text())
        else:
            self.server_conf.get_ad_conf().set_fqdn(self.ui.txtFqdnAD.get_text())
            self.server_conf.get_ad_conf().set_dns_domain(self.ui.txtDnsDomain.get_text())
