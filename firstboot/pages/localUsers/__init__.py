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
import firstboot.pages
from firstboot_lib import PageWindow

import gettext
from gettext import gettext as _
gettext.textdomain('firstboot')

__REQUIRED__ = False

__TITLE__ = _('Create local users')

def get_page(options=None):

    page = LocalUsersPage(options)
    return page

class LocalUsersPage(PageWindow.PageWindow):
    __gtype_name__ = "LocalUsersPage"

    def finish_initializing(self, builder, options=None):
        self.btnLocalUsers = builder.get_object('btnLocalUsers')
        self.lblDescription = builder.get_object('lblDescription')

    def translate(self):
        self.btnLocalUsers.set_label(_('Create local users'))
        self.lblDescription.set_text(_('If you need to manage local users on this \
workstation click the button below. Note that if this workstation \
is linked to a GECOS server, it\'s likely you don\'t need to create \
local users.'))

    def on_btnLocalUsers_Clicked(self, button):
        cmd = 'gnome-control-center'
        param = 'user-accounts'
        os.spawnlp(os.P_NOWAIT, cmd, cmd, param)

    def previous_page(self, load_page_callback):
        load_page_callback(firstboot.pages.linkToServer)

    def next_page(self, load_page_callback):
        load_page_callback(firstboot.pages.installSoftware)
