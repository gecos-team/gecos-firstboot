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
        self.btnAccept = builder.get_object('btnAccept')
        self.tvNames = builder.get_object('tvNames')

        container = builder.get_object(self.__page_container__)
        page = builder.get_object(self.__gtype_name__)
        container.remove(page)
        self.page = page

        self.translate()
        self.imgStatus.set_visible(False)
        self.lblStatus.set_visible(False)

        self.cmd_options = options
        self.fbe = FirstbootEntry.FirstbootEntry()

        self._init_treeview()

    def translate(self):
        desc = _('This workstation is going to be linked to a Chef server, \
therefore it must be given a host name. The host name will be used for \
uniquely identify this workstation.\n\n The list below shows the current \
host names found in the Chef server, you must avoid to use any of them.')

        self.lblDescription.set_text(desc)
        self.lblHostname.set_label(_('Hostname'))
        self.btnAccept.set_label(_('Accept'))

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

        self.server_conf = params['server_conf']
        self.pem_file_path = None

        chef_conf = self.server_conf.get_chef_conf()
        pem_url = chef_conf.get_pem_url()

        try:
            self.pem_file_path = ServerConf.get_chef_pem(pem_url)
        except Exception as e:
            self.show_error(_('The Chef certificate couldn\'t be found.'))
            return

        self._load_hostnames()

    def get_widget(self):
        return self.page

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

    def _init_treeview(self):

        tvcolumn = gtk.TreeViewColumn(_('Host names in use'))

        cell = gtk.CellRendererText()
        tvcolumn.set_sort_column_id(0)
        tvcolumn.pack_start(cell, True)
        tvcolumn.set_cell_data_func(cell, self._render_column_text)

        self.tvNames.append_column(tvcolumn)
        self.tvNames.set_enable_search(True)
        self.tvNames.set_search_column(0)

    def _load_hostnames(self):

        try:

            chef_conf = self.server_conf.get_chef_conf()
            chef_url = chef_conf.get_url()

            cmd = 'knife node list -u chef-validator -k %s -s %s' % (self.pem_file_path, chef_url)
            args = shlex.split(cmd)

            process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            exit_code = os.waitpid(process.pid, 0)
            output = process.communicate()[0]
            output = output.strip()

            names = []
            if exit_code[1] == 0:
                names = json.loads(output)

            self.hostnames = []
            model = self.tvNames.get_model()
            for name in names:
                self.hostnames.append(name)
                model.append([name])

            os.remove(self.pem_file_path)
            self.pem_file_path = None

        except Exception as e:
            self.show_error(str(e))

    def _render_column_text(self, column, cell, model, iter):

        hostname = model.get_value(iter, 0)
        cell.set_property('text', hostname)

    def on_tvNames_row_activated(self, treeview, path, view_column):
        pass

    def on_tvNames_cursor_changed(self, treeview):
        pass
        #~ selection = self.tvNames.get_selection()
        #~ (model, iter) = selection.get_selected()
        #~ hostname = model.get_value(iter, 0)
        #~ self.txtHostname.set_text(hostname)

    def show_error(self, message):
        self.imgStatus.set_from_stock(gtk.STOCK_DIALOG_ERROR, gtk.ICON_SIZE_BUTTON)
        self.lblStatus.set_label(message)
        self.imgStatus.set_visible(True)
        self.lblStatus.set_visible(True)
