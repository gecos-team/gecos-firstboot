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

__TITLE__ = _('Install software')


def get_page(main_window):

    page = InstallSoftwarePage(main_window)
    return page


class InstallSoftwarePage(PageWindow.PageWindow):
    __gtype_name__ = "InstallSoftwarePage"

    def load_page(self, params=None):
        self.emit('status-changed', 'localUsers', not __REQUIRED__)
        self.main_window.btnNext.set_label(_('Close'))

    def translate(self):
        self.ui.btnInstallSoftware.set_label(_('Install software'))
        self.ui.lblDescription.set_text(_('Install software packages from a safe repository.\
\n\nYou can skip this step if this workstation will be managed from your GECOS server.'))

    def on_btnInstallSoftware_Clicked(self, button):
        cmd = '/usr/sbin/synaptic'
        param = '/usr/sbin/synaptic'
        os.spawnlp(os.P_NOWAIT, cmd, cmd)

    def previous_page(self, load_page_callback):
        load_page_callback(firstboot.pages.localUsers)
