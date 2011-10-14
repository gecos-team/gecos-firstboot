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
from gi.repository import Gio
from gi.repository import Pango
from firstboot_lib import PageWindow
from gi.repository import GdkPixbuf

import gettext
from gettext import gettext as _
gettext.textdomain('firstboot')

__REQUIRED__ = False

__TITLE__ = _('Run applications')

def get_page(options=None):

    page = RunApplicationsPage(options)
    return page

class RunApplicationsPage(PageWindow.PageWindow):
    __gtype_name__ = "RunApplicationsPage"

    def _finish_initializing(self, builder, options=None):
        self.ivApplications = builder.get_object('ivApplications')
        self.load_iconview()

    def load_iconview(self):

        self.ivApplications.set_selection_mode(Gtk.SelectionMode.SINGLE)

        store = self.ivApplications.get_model()
        store.clear()

        filter = ['firefox', 'gnome-terminal']
        app_list = Gio.app_info_get_all()

        for app in app_list:
            if app.get_executable() in filter:

                icon = app.get_icon()
                pixbuf = None

                try:
                    if isinstance(icon, Gio.FileIcon):
                        pixbuf = GdkPixbuf.Pixbuf.from_file(icon).get_file().get_path()

                    elif isinstance(icon, Gio.ThemedIcon):
                        theme = Gtk.IconTheme.get_default()
                        pixbuf = theme.load_icon(icon.get_names()[0], 96, Gtk.IconLookupFlags.USE_BUILTIN)

                except Exception, e:
                    print "Error loading icon pixbuf: " + e.message;

                store.append([
                    pixbuf, app.get_name(),
                    Pango.ALIGN_CENTER, 140, Pango.WrapMode.WORD,
                    app
                ])

        self.ivApplications.set_model(store)

    def on_ivApplications_buttonReleased(self, iconview, event):
        try:
            path = iconview.get_path_at_pos(int(event.x), int(event.y))
            if path == None:
                raise Exception('No item selected')
            model = iconview.get_model()
            item = model.get_value(model.get_iter(path), 5)

            item.launch()

        except Exception, e:
            print e

    def on_ivApplications_activated(self, iconview):
        try:
            cursor = iconview.get_cursor()
            path = cursor[0]
            model = iconview.get_model()
            item = model.get_value(model.get_iter(path), 5)

            item.launch()

        except Exception, e:
            print e
