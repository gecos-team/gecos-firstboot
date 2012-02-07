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


import LinkToChefHostnamePage
import LinkToChefResultsPage
import firstboot.pages.linkToChef
from firstboot_lib import PageWindow
from firstboot import serverconf
import firstboot.validation as validation

import gettext
from gettext import gettext as _
gettext.textdomain('firstboot')

__REQUIRED__ = False

__DEFAULT_ROLE__ = 'default_group'

def get_page(main_window):

    page = LinkToChefConfEditorPage(main_window)
    return page


class LinkToChefConfEditorPage(PageWindow.PageWindow):
    __gtype_name__ = "LinkToChefConfEditorPage"

    def finish_initializing(self):

        self.update_server_conf = False
        self.chef_is_configured = False
        self.unlink_from_chef = False

    def load_page(self, params=None):

        if 'server_conf' in params:
            self.server_conf = params['server_conf']
            if not self.server_conf is None:
                self.ui.lblVersionValue.set_label(self.server_conf.get_version())
                self.ui.lblOrganizationValue.set_label(self.server_conf.get_organization())
                self.ui.lblNotesValue.set_label(self.server_conf.get_notes())
                self.ui.txtUrlChef.set_text(self.server_conf.get_chef_conf().get_url())
                self.ui.txtUrlChefCert.set_text(self.server_conf.get_chef_conf().get_pem_url())
                self.ui.txtHostname.set_text(self.server_conf.get_chef_conf().get_hostname())
                self.ui.txtDefaultRole.set_text(self.server_conf.get_chef_conf().get_default_role())

        if self.server_conf is None:
            self.server_conf = serverconf.ServerConf()

        if len(self.ui.txtDefaultRole.get_text()) == 0:
            self.ui.txtDefaultRole.set_text(__DEFAULT_ROLE__)

        self.update_server_conf = True
        self.chef_is_configured = params['chef_is_configured']
        self.unlink_from_chef = params['unlink_from_chef']

#        if self.chef_is_configured and self.unlink_from_chef:
#            self.ui.chkChef.get_child().set_markup(self._bold(_('This \
#workstation is going to be unlinked from the Chef server.')))

    def _bold(self, str):
        return '<b>%s</b>' % str

    def translate(self):
        desc = _('These are the parameters you need to configure to join this workstation to \
a Chef server. The "Chef URL" is the URL this workstation will use to comunicate with the server. \
The "Chef Certificate" parameter is the URL from which this assistant will download a required \
certificate for joining to the Chef server. The "Node Name" parameter must be an unique name \
for this wokstation. \n\n The "Default Group" parameter is the default group for this workstation \
in the Chef server, you may not modify this parameter unless you really know what you are doing.')

        self.ui.lblDescription.set_text(desc)

        self.ui.lblVersion.set_label(_('Version'))
        self.ui.lblOrganization.set_label(_('Organization'))
        self.ui.lblNotes.set_label(_('Notes'))
        self.ui.lblUrlChef.set_label('Chef URL')
        self.ui.lblUrlChefCert.set_label(_('Certificate URL'))
        self.ui.lblHostname.set_label(_('Node Name'))
        self.ui.lblDefaultRole.set_label(_('Default Group'))

    def previous_page(self, load_page_callback):
        load_page_callback(firstboot.pages.linkToChef)

    def next_page(self, load_page_callback):

        if not self.unlink_from_chef:

            result, messages = self.validate_conf()

            if result == True:
                result, messages = serverconf.setup_server(
                    server_conf=self.server_conf,
                    link_ldap=False,
                    unlink_ldap=False,
                    link_chef=not self.unlink_from_chef,
                    unlink_chef=self.unlink_from_chef
                )

            load_page_callback(LinkToChefResultsPage, {
                'server_conf': self.server_conf,
                'result': result,
                'messages': messages
            })

        else:
            result, messages = serverconf.setup_server(
                server_conf=self.server_conf,
                link_chef=not self.unlink_from_chef,
                unlink_chef=self.unlink_from_chef
            )

            load_page_callback(LinkToChefResultsPage, {
                'result': result,
                'server_conf': self.server_conf,
                'messages': messages
            })

    def on_serverConf_changed(self, entry):
        if not self.update_server_conf:
            return
        self.server_conf.get_chef_conf().set_url(self.ui.txtUrlChef.get_text())
        self.server_conf.get_chef_conf().set_pem_url(self.ui.txtUrlChefCert.get_text())
        self.server_conf.get_chef_conf().set_default_role(self.ui.txtDefaultRole.get_text())
        self.server_conf.get_chef_conf().set_hostname(self.ui.txtHostname.get_text())

    def validate_conf(self):

        valid = True
        messages = []

        if not self.server_conf.get_chef_conf().validate():
            valid = False
            messages.append({'type': 'error', 'message': _('Chef and Chef Cert URLs must be well formed URLs.')})

        hostname = self.server_conf.get_chef_conf().get_hostname()

        if not validation.is_qname(hostname):
            valid = False
            messages.append({'type': 'error', 'message': _('The host name is empty or contains invalid characters.')})

        try:
            used_hostnames = serverconf.get_chef_hostnames(self.server_conf.get_chef_conf())

        except:
            used_hostnames = []
            valid = False
            messages.append({'type': 'error', 'message': _('Please check the Chef Cert URL, it seems to be wrong.')})

        if hostname in used_hostnames:
            valid = False
            messages.append({'type': 'error', 'message': _('The host name already exists in the Chef server. Choose a different one.')})

        return valid, messages
