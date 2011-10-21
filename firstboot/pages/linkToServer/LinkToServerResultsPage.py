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


from gi.repository import Gtk

import firstboot.pages
from firstboot_lib import PageWindow

import gettext
from gettext import gettext as _
gettext.textdomain('firstboot')


__REQUIRED__ = False

__TITLE__ = _('Link workstation to a server')


def get_page(main_window):

    page = LinkToServerResultsPage(main_window)
    return page

class LinkToServerResultsPage(PageWindow.PageWindow):
    __gtype_name__ = "LinkToServerResultsPage"

    def finish_initializing(self):
        self.result = False

    def translate(self):
        self.ui.lblDescription.set_text('')

    def load_page(self, params=None):

        if 'server_conf' in params:
            self.server_conf = params['server_conf']

        if 'result' in params:
            self.result = params['result']

        if 'messages' in params:
            for m in params['messages']:
                if m['type'] == 'error':
                    icon = Gtk.STOCK_DIALOG_ERROR
                else:
                    icon = Gtk.STOCK_YES
                box = self.new_message(m['message'], icon)
                self.ui.boxMessageContainer.pack_start(box, False, False, 0)

        if self.result == True:
            self.ui.lblDescription.set_text(_('The configuration was \
updated successfully.'))
            self.emit('status-changed', 'linkToServer', True)

        else:
            self.ui.lblDescription.set_text(_('There are some errors you may fix.'))
            self.emit('status-changed', 'linkToServer', False)

    def new_message(self, message, icon):
        box = Gtk.HBox()
        img = Gtk.Image()
        img.set_from_stock(icon, Gtk.IconSize.MENU)
        img.show()
        lbl = Gtk.Label()
        lbl.set_text(message)
        lbl.show()
        box.pack_start(img, False, True, 0)
        box.pack_start(lbl, False, True, 0)
        box.set_spacing(10)
        box.show()
        return box

    def previous_page(self, load_page_callback):
        load_page_callback(firstboot.pages.linkToServer)

    def next_page(self, load_page_callback):
        load_page_callback(firstboot.pages.localUsers)
