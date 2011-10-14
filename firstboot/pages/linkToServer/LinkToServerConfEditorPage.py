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


def get_page(options=None):

    page = LinkToServerConfEditorPage(options)
    return page

class LinkToServerConfEditorPage(PageWindow.PageWindow):
    __gtype_name__ = "LinkToServerConfEditorPage"

    def finish_initializing(self, builder, options=None):
        self.lblDescription = self.builder.get_object('lblDescription')
        self.lblVersionValue = self.builder.get_object('lblVersionValue')
        self.lblOrganizationValue = self.builder.get_object('lblOrganizationValue')
        self.txtUrlLDAP = self.builder.get_object('txtUrlLDAP')
        self.txtBaseDN = self.builder.get_object('txtBaseDN')
        self.txtBindDN = self.builder.get_object('txtBindDN')
        self.txtPassword = self.builder.get_object('txtPassword')
        self.txtUrlChef = self.builder.get_object('txtUrlChef')
        self.txtUrlChefCert = self.builder.get_object('txtUrlChefCert')
        self.chkLDAP = self.builder.get_object('chkLDAP')
        self.chkChef = self.builder.get_object('chkChef')

        self.update_server_conf = False
        self.unlink_from_ldap = False
        self.unlink_from_chef = False

    def load_page(self, main_window, params=None):

        if 'server_conf' in params:
            self.server_conf = params['server_conf']
            if not self.server_conf is None:
                self.lblVersionValue.set_label(self.server_conf.get_version())
                self.lblOrganizationValue.set_label(self.server_conf.get_organization())
                self.txtUrlLDAP.set_text(self.server_conf.get_ldap_conf().get_url())
                self.txtBaseDN.set_text(self.server_conf.get_ldap_conf().get_basedn())
                self.txtBindDN.set_text(self.server_conf.get_ldap_conf().get_binddn())
                self.txtPassword.set_text(self.server_conf.get_ldap_conf().get_password())
                self.txtUrlChef.set_text(self.server_conf.get_chef_conf().get_url())
                self.txtUrlChefCert.set_text(self.server_conf.get_chef_conf().get_pem_url())

        if self.server_conf is None:
            self.server_conf = ServerConf.ServerConf()

        self.update_server_conf = True

        self.unlink_from_ldap = params['unlink_from_ldap']
        self.unlink_from_chef = params['unlink_from_chef']

        if params['ldap_is_configured']:
            self.chkLDAP.set_active(False)
            self.chkLDAP.set_sensitive(False)

        if params['chef_is_configured']:
            self.chkChef.set_active(False)
            self.chkChef.set_sensitive(False)

        if self.unlink_from_ldap:
            self.chkLDAP.get_child().set_markup(self._bold(_('This \
workstation is going to be unlinked from the LDAP server.')))

        if self.unlink_from_chef:
            self.chkChef.get_child().set_markup(self._bold(_('This \
workstation is going to be unlinked from the Chef server.')))

    def _bold(self, str):
        return '<b>%s</b>' % str

    def translate(self):
        desc = _('Remember you can disable the sections you don\'t want to configure.')

        self.builder.get_object('lblDescription').set_text(desc)

        self.builder.get_object('lblVersion').set_label(_('Version'))
        self.builder.get_object('lblOrganization').set_label(_('Organization'))
        self.builder.get_object('lblNotes').set_label(_('Notes'))
        self.builder.get_object('lblUrlLDAP').set_label('URL')
        self.builder.get_object('lblBaseDN').set_label('Base DN')
        self.builder.get_object('lblBindDN').set_label('Bind DN')
        self.builder.get_object('lblPassword').set_label(_('Password'))
        self.builder.get_object('lblUrlChef').set_label('URL')
        self.builder.get_object('lblUrlChefCert').set_label(_('Certificate URL'))

        self.chkLDAP.get_child().set_markup(self._bold(_('Configure LDAP')))
        self.chkChef.get_child().set_markup(self._bold(_('Configure Chef')))

    def on_chkLDAP_toggle(self, button):
        active = self.chkLDAP.get_active()

        self.txtUrlLDAP.set_sensitive(active)
        self.txtBaseDN.set_sensitive(active)
        self.txtBindDN.set_sensitive(active)
        self.txtPassword.set_sensitive(active)

        active = active \
            | self.chkChef.get_active() \
            | self.unlink_from_ldap \
            | self.unlink_from_chef

        #~ self.btnApply.set_sensitive(active)

    def on_chkChef_toggle(self, button):
        active = self.chkChef.get_active()

        self.txtUrlChef.set_sensitive(active)
        self.txtUrlChefCert.set_sensitive(active)

        active = active \
            | self.chkLDAP.get_active() \
            | self.unlink_from_ldap \
            | self.unlink_from_chef

        #~ self.btnApply.set_sensitive(active)

    def previous_page(self, load_page_callback):
        load_page_callback(firstboot.pages.linkToServer)

    def next_page(self, load_page_callback):

        if not self.unlink_from_chef and self.chkChef.get_active():
            # The unique host name for Chef is mandatory, so we need
            # to ask for it before the setup.

            try:
                used_hostnames = ServerConf.get_chef_hostnames(self.server_conf.get_chef_conf())
                #print used_hostnames

                load_page_callback(LinkToServerHostnamePage, {
                    'server_conf': self.server_conf,
                    'link_ldap': self.chkLDAP.get_active(),
                    'unlink_ldap': self.unlink_from_ldap,
                    'link_chef': self.chkChef.get_active(),
                    'unlink_chef': self.unlink_from_chef,
                    'used_hostnames': used_hostnames
                })

                #~ self.emit('subpage-changed', 'linkToServer', 'LinkToServerHostnamePage',
                    #~ {'server_conf': self.server_conf,
                    #~ 'link_ldap': self.chkLDAP.get_active(),
                    #~ 'unlink_ldap': self.unlink_from_ldap,
                    #~ 'link_chef': self.chkChef.get_active(),
                    #~ 'unlink_chef': self.unlink_from_chef,
                    #~ 'used_hostnames': used_hostnames})

            except ServerConf.ServerConfException as e:
                messages = [{'type': 'error', 'message': str(e)}]

                load_page_callback(LinkToServerResultsPage, {
                    'result': False,
                    'server_conf': self.server_conf,
                    'messages': messages
                })

                #~ self.emit('subpage-changed', 'linkToServer',
                          #~ 'LinkToServerResultsPage',
                          #~ {'result': False, 'server_conf': self.server_conf,
                           #~ 'messages': messages})

        else:
            result, messages = ServerConf.setup_server(
                server_conf=self.server_conf,
                link_ldap=self.chkLDAP.get_active(),
                unlink_ldap=self.unlink_from_ldap,
                link_chef=self.chkChef.get_active(),
                unlink_chef=self.unlink_from_chef
            )

            load_page_callback(LinkToServerResultsPage, {
                'result': result,
                'server_conf': self.server_conf,
                'messages': messages
            })

            #~ self.emit('subpage-changed', 'linkToServer',
                      #~ 'LinkToServerResultsPage',
                      #~ {'result': result, 'server_conf': self.server_conf,
                       #~ 'messages': messages})

    def on_serverConf_changed(self, entry):
        if not self.update_server_conf:
            return
        self.server_conf.get_ldap_conf().set_url(self.txtUrlLDAP.get_text())
        self.server_conf.get_ldap_conf().set_basedn(self.txtBaseDN.get_text())
        self.server_conf.get_ldap_conf().set_binddn(self.txtBindDN.get_text())
        self.server_conf.get_ldap_conf().set_password(self.txtPassword.get_text())
        self.server_conf.get_chef_conf().set_url(self.txtUrlChef.get_text())
        self.server_conf.get_chef_conf().set_pem_url(self.txtUrlChefCert.get_text())
