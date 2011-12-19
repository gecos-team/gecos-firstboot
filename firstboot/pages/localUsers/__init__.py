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


import pwd
import os, SystemUsers, Dialogs
from gi.repository import Gtk
import firstboot.pages
from firstboot_lib import PageWindow

import gettext
from gettext import gettext as _
gettext.textdomain('firstboot')

__REQUIRED__ = False

__TITLE__ = _('Manage local users')

__DUMMY_PASSWORD__ = '********'

def get_page(main_window):

    page = LocalUsersPage(main_window)
    return page

class LocalUsersPage(PageWindow.PageWindow):
    __gtype_name__ = "LocalUsersPage"

    def load_page(self, params=None):
        self.emit('status-changed', 'localUsers', not __REQUIRED__)
        self.init_treeview()
        self.reload_page()

        self.ui.lblGroups.set_visible(False)
        self.ui.txtGroups.set_visible(False)

    def reload_page(self):
        self._accept_changes = False
        self._active_user = None
        self.ui.btnApply.set_sensitive(False)
        self.ui.btnCancel.set_sensitive(False)
        self.ui.btnAdd.set_sensitive(True)
        self.ui.btnRemove.set_sensitive(False)
        self._accept_changes = False
        self.ui.txtName.set_text('')
        self.ui.txtPassword.set_text('')
        self.ui.txtConfirm.set_text('')
        self.ui.txtGroups.set_text('')
        self._accept_changes = True
        try:
            self.load_users()
        except Exception as e:
            print e

    def translate(self):
        self.ui.lblDescription.set_text(_('You can manage local users on this \
workstation. Note if this workstation is linked to a GECOS server, it\'s \
likely you don\'t need to create local users.'))

        self.ui.lblName.set_text(_('Name'))
        self.ui.lblPassword.set_text(_('Password'))
        self.ui.lblConfirm.set_text(_('Confirm'))
        self.ui.lblGroups.set_text(_('Groups'))
        self.ui.btnAdd.set_label(_('Add'))
        self.ui.btnRemove.set_label(_('Remove'))
        self.ui.btnCancel.set_label(_('Cancel'))
        self.ui.btnApply.set_label(_('Apply'))

#    def on_btnLocalUsers_Clicked(self, button):
#        cmd = 'gnome-control-center'
#        param = 'user-accounts'
#        os.spawnlp(os.P_NOWAIT, cmd, cmd, param)

    def previous_page(self, load_page_callback):
        load_page_callback(firstboot.pages.linkToChef)

    def next_page(self, load_page_callback):
        load_page_callback(firstboot.pages.installSoftware)

    def init_treeview(self):

        tvcolumn = Gtk.TreeViewColumn(_('User'))

        cell = Gtk.CellRendererText()
        tvcolumn.pack_start(cell, False)
        tvcolumn.set_cell_data_func(cell, self._render_user_column)

        self.ui.tvUsers.append_column(tvcolumn)
        self.ui.tvUsers.set_enable_search(True)
        self.ui.tvUsers.set_search_column(1)
        self.ui.tvUsers.set_show_expanders(False)

    def _render_user_column(self, column, cell, model, iter, userdata):
        user = model.get_value(iter, 0)
        property = 'text'
        text = user['login']
        cell.set_property(property, text)

    def load_users(self):

        users = SystemUsers.read_users()
        store = self.ui.tvUsers.get_model()
        store.clear()

        for user in users:
            store.append([user])

        self.ui.tvUsers.set_model(store)

    def _select_user(self):
        self.ui.tvUsers.get_selection().select_path(self._selected_path)
        self.on_tvUsersCursorChanged(self.ui.tvUsers)

    def on_tvUsersCursorChanged(self, widget):
        if self._active_user and self._active_user['updated'] == True:
            return
        store, iter = widget.get_selection().get_selected()
        user = store.get_value(iter, 0)
        self._selected_path = store.get_path(iter)
        self.set_active_user(user)

    def set_active_user(self, user):
        pwd_struct = pwd.getpwnam(os.getlogin())
        is_current_user = int(user['uid']) == int(pwd_struct.pw_uid)
        self._active_user = user
        self._active_user['updated'] = False
        self._accept_changes = False
        self.ui.txtName.set_text(user['name'])
        self.ui.txtPassword.set_text(__DUMMY_PASSWORD__)
        self.ui.txtConfirm.set_text('')
        self.ui.txtGroups.set_text(user['groups'])
        self.ui.btnRemove.set_sensitive(not is_current_user)
        self._accept_changes = True

    def on_userDataChanged(self, widget):
        if self._active_user != None:
            self._active_user['updated'] = self._accept_changes
        self.ui.btnApply.set_sensitive(self._accept_changes)
        self.ui.btnCancel.set_sensitive(self._accept_changes)

    def on_btnApplyClicked(self, widget):

        update_passwd = False

        if self.ui.txtPassword.get_text() != __DUMMY_PASSWORD__:
            update_passwd = True
            if self.ui.txtPassword.get_text() != self.ui.txtConfirm.get_text():
                Dialogs.user_error_dialog(_('The passwords doesn\'t match.'))
                return

        user = {
            'login': self._active_user['login'],
            'name': self.ui.txtName.get_text(),
            'password': self.ui.txtPassword.get_text(),
            'groups': self.ui.txtGroups.get_text()
        }

        try:
            SystemUsers.update_user(user, update_passwd)
            self.reload_page()
            self._select_user()

        except SystemUsers.SystemUserException as e:
            Dialogs.user_error_dialog(e.message)

    def on_btnCancelClicked(self, widget):
        self._accept_changes = False
        self.ui.txtName.set_text(self._active_user['name'])
        self.ui.txtPassword.set_text(__DUMMY_PASSWORD__)
        self.ui.txtConfirm.set_text('')
        self.ui.txtGroups.set_text(self._active_user['groups'])
        self._accept_changes = True

    def on_btnAddClicked(self, widget):
        login_info = Dialogs.new_user_dialog()
        if login_info == False:
            return

        try:
            SystemUsers.add_user(login_info[0], login_info[1])
            self.reload_page()

        except SystemUsers.SystemUserException as e:
            Dialogs.user_error_dialog(e.message)

    def on_btnRemoveClicked(self, widget):
        action = Dialogs.remove_user_dialog(self._active_user)
        if action == False:
            return

        try:
            SystemUsers.remove_user(self._active_user['login'], action[1])
            self.reload_page()

        except SystemUsers.SystemUserException as e:
            Dialogs.user_error_dialog(e.message)
