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


import ServerConf, LinkToServerHostnamePage, LinkToServerResultsPage
import firstboot.pages.linkToServer
from firstboot_lib import PageWindow

import gettext
from gettext import gettext as _
gettext.textdomain('firstboot')

__REQUIRED__ = False

__TITLE__ = _('Link workstation to a server')


def get_page(main_window):

    page = LinkToServerConfEditorPage(main_window)
    return page

class LinkToServerConfEditorPage(PageWindow.PageWindow):
    __gtype_name__ = "LinkToServerConfEditorPage"

    def finish_initializing(self):

        self.update_server_conf = False
        self.unlink_from_ldap = False
        self.unlink_from_chef = False

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
                self.ui.txtUrlChef.set_text(self.server_conf.get_chef_conf().get_url())
                self.ui.txtUrlChefCert.set_text(self.server_conf.get_chef_conf().get_pem_url())

        if self.server_conf is None:
            self.server_conf = ServerConf.ServerConf()

        self.update_server_conf = True

        self.unlink_from_ldap = params['unlink_from_ldap']
        self.unlink_from_chef = params['unlink_from_chef']

        if params['ldap_is_configured']:
            self.ui.chkLDAP.set_active(False)
            self.ui.chkLDAP.set_sensitive(False)

        if params['chef_is_configured']:
            self.ui.chkChef.set_active(False)
            self.ui.chkChef.set_sensitive(False)

        if params['ldap_is_configured'] and params['chef_is_configured']:
            self.ui.lblDescription.set_visible(False)

        if self.unlink_from_ldap:
            self.ui.chkLDAP.get_child().set_markup(self._bold(_('This \
workstation is going to be unlinked from the LDAP server.')))

        if self.unlink_from_chef:
            self.ui.chkChef.get_child().set_markup(self._bold(_('This \
workstation is going to be unlinked from the Chef server.')))

    def _bold(self, str):
        return '<b>%s</b>' % str

    def translate(self):
        desc = _('Remember you can disable the sections you don\'t want to configure.')

        self.ui.lblDescription.set_text(desc)

        self.ui.lblVersion.set_label(_('Version'))
        self.ui.lblOrganization.set_label(_('Organization'))
        self.ui.lblNotes.set_label(_('Notes'))
        self.ui.lblUrlLDAP.set_label('URL')
        self.ui.lblBaseDN.set_label('Base DN')
        self.ui.lblBindDN.set_label('Bind DN')
        self.ui.lblPassword.set_label(_('Password'))
        self.ui.lblUrlChef.set_label('URL')
        self.ui.lblUrlChefCert.set_label(_('Certificate URL'))

        self.ui.chkLDAP.get_child().set_markup(self._bold(_('Configure LDAP')))
        self.ui.chkChef.get_child().set_markup(self._bold(_('Configure Chef')))

    def on_chkLDAP_toggle(self, button):
        active = self.ui.chkLDAP.get_active()

        self.ui.txtUrlLDAP.set_sensitive(active)
        self.ui.txtBaseDN.set_sensitive(active)
        self.ui.txtBindDN.set_sensitive(active)
        self.ui.txtPassword.set_sensitive(active)

        active = active \
            | self.ui.chkChef.get_active() \
            | self.unlink_from_ldap \
            | self.unlink_from_chef

        self.main_window.btnNext.set_sensitive(active)

    def on_chkChef_toggle(self, button):
        active = self.ui.chkChef.get_active()

        self.ui.txtUrlChef.set_sensitive(active)
        self.ui.txtUrlChefCert.set_sensitive(active)

        active = active \
            | self.ui.chkLDAP.get_active() \
            | self.unlink_from_ldap \
            | self.unlink_from_chef

        self.main_window.btnNext.set_sensitive(active)

    def previous_page(self, load_page_callback):
        load_page_callback(firstboot.pages.linkToServer)

    def next_page(self, load_page_callback):

        if not self.unlink_from_chef and self.ui.chkChef.get_active():
            # The unique host name for Chef is mandatory, so we need
            # to ask for it before the setup.

            try:
                used_hostnames = ServerConf.get_chef_hostnames(self.server_conf.get_chef_conf())

                load_page_callback(LinkToServerHostnamePage, {
                    'server_conf': self.server_conf,
                    'link_ldap': self.ui.chkLDAP.get_active(),
                    'unlink_ldap': self.unlink_from_ldap,
                    'link_chef': self.ui.chkChef.get_active(),
                    'unlink_chef': self.unlink_from_chef,
                    'used_hostnames': used_hostnames
                })

            except ServerConf.ServerConfException as e:
                messages = [{'type': 'error', 'message': str(e)}]

                load_page_callback(LinkToServerResultsPage, {
                    'result': False,
                    'server_conf': self.server_conf,
                    'messages': messages
                })

        else:
            result, messages = ServerConf.setup_server(
                server_conf=self.server_conf,
                link_ldap=self.ui.chkLDAP.get_active(),
                unlink_ldap=self.unlink_from_ldap,
                link_chef=self.ui.chkChef.get_active(),
                unlink_chef=self.unlink_from_chef
            )

            load_page_callback(LinkToServerResultsPage, {
                'result': result,
                'server_conf': self.server_conf,
                'messages': messages
            })

    def on_serverConf_changed(self, entry):
        if not self.update_server_conf:
            return
        self.server_conf.get_ldap_conf().set_url(self.ui.txtUrlLDAP.get_text())
        self.server_conf.get_ldap_conf().set_basedn(self.ui.txtBaseDN.get_text())
        self.server_conf.get_ldap_conf().set_binddn(self.ui.txtBindDN.get_text())
        self.server_conf.get_ldap_conf().set_password(self.ui.txtPassword.get_text())
        self.server_conf.get_chef_conf().set_url(self.ui.txtUrlChef.get_text())
        self.server_conf.get_chef_conf().set_pem_url(self.ui.txtUrlChefCert.get_text())
