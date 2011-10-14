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


import gettext
from gettext import gettext as _
gettext.textdomain('firstboot')

import shlex
import subprocess
import os
from gi.repository import Gtk
from gi.repository import Pango
from gi.repository import Gio
from gi.repository import GdkPixbuf
import logging
logger = logging.getLogger('firstboot')

from firstboot_lib import Window, firstbootconfig, FirstbootEntry

import pages

__DESKTOP_FILE__ = '/etc/xdg/autostart/firstboot.desktop'

# See firstboot_lib.Window.py for more details about how this class works
class FirstbootWindow(Window):
    __gtype_name__ = "FirstbootWindow"

    def finish_initializing(self, builder, options=None): # pylint: disable=E1002
        """Set up the main window"""
        super(FirstbootWindow, self).finish_initializing(builder)
        self.connect("delete_event", self.on_delete_event)

        self.cmd_options = options
        self.fbe = FirstbootEntry.FirstbootEntry()

        iconfile = firstbootconfig.get_data_file('media', '%s' % ('wizard1.png',))
        self.set_icon_from_file(iconfile)


        self.lblDescription = builder.get_object('lblDescription')
        self.boxContent = builder.get_object('boxContent')
        self.swContent = builder.get_object('swContent')
        self.boxIndex = builder.get_object('boxIndex')
        self.boxApplications = builder.get_object('boxApplications')
        #self.btnClose = builder.get_object('btnClose')
        self.btnPrev = builder.get_object('btnPrev')
        self.btnNext = builder.get_object('btnNext')

        self.pages = {}
        self.buttons = {}
        self.current_page = None

        self.translate()
        self.build_index()

        self.set_current_page(pages.get_first_page())
        self.on_link_status(None, False)
        self.show_applications()

        self.set_focus(self.btnNext)

    def translate(self):
        self.set_title(_('First Boot Assistant'))
        self.lblDescription.set_text('')
        #self.btnClose.set_label(_('Close'))
        self.btnPrev.set_label(_('Previous'))
        self.btnNext.set_label(_('Next'))

    def on_btnClose_Clicked(self, button):
        self.destroy()

    def on_delete_event(self, widget, data=None):

        return False

        dialog = Gtk.MessageDialog(self,
            Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
            Gtk.MessageType.INFO, Gtk.ButtonsType.YES_NO,
            _("Are you sure you have fully configured this workstation?"))

        result = dialog.run()
        dialog.destroy()
        retval = True

        if result == Gtk.ResponseType.YES:

            if os.path.exists(__DESKTOP_FILE__):
                os.rename(__DESKTOP_FILE__, '/tmp/firstboot.desktop');

            retval = False

        return retval


    def on_btnIndex_Clicked(self, button, page_name, module):
        self.set_current_page(page_name)

    def on_btnPrev_Clicked(self, button):
        self.current_page.previous_page(self.set_current_page)

    def on_btnNext_Clicked(self, button):
        self.current_page.next_page(self.set_current_page)

    def build_index(self):

        self.pages = {}
        self.buttons = {}

        children = self.boxIndex.get_children()
        for child in children:
            self.boxIndex.remove(child)

        for page_name in pages.pages:
            try:
                module = __import__('firstboot.pages.%s' % page_name, fromlist=['firstboot.pages'])
                button = self.new_index_button(module.__TITLE__, page_name, module)
                self.pages[page_name] = {
                    'id': page_name,
                    'button': button,
                    'module': module,
                    'enabled': True,
                    'instance': None
                }
                self.buttons[page_name] = button

            except ImportError, e:
                print e

    def new_index_button(self, page_title, page_name, module):

        button = Gtk.Button()
        button.set_relief(Gtk.ReliefStyle.NONE)
        button.set_property('focus-on-click', False)
        button.set_property('xalign', 0)

        label = Gtk.Label()
        label.set_text(page_title)
        label.show()
        button.add(label)

        self.boxIndex.pack_start(button, False, True, 0)
        button.connect('clicked', self.on_btnIndex_Clicked, page_name, module)
        button.show()

        return button


    def set_current_page(self, module, params=None):

        try:
            self.current_page.unload_page(self, params)
        except Exception as e:
            pass

        self.current_page = module.get_page(self.cmd_options)

        try:
            self.current_page.load_page(self, params)
        except Exception as e:
            pass

        try:
            self.current_page.connect('link-status', self.on_link_status)
        except Exception as e:
            pass

        try:
            self.current_page.connect('page-changed', self.on_page_changed)
        except Exception as e:
            pass


        for button_name in self.buttons:
            self.button_set_inactive(self.buttons[button_name])

        #self.button_set_active(button)

        for child in self.swContent.get_children():
            self.swContent.remove(child)

        self.swContent.add_with_viewport(self.current_page.get_widget())

    def on_page_changed(self, sender, module, params):
        self.set_current_page(module, params)

    def button_set_active(self, button):
        label = button.get_children()[0]
        label.set_markup('<b>%s</b>' % (label.get_text(),))

    def button_set_inactive(self, button):
        label = button.get_children()[0]
        label.set_markup(label.get_text())

    def on_link_status(self, sender, status):
        for button_name in self.buttons:
            if button_name in ['linkToServer', 'installSoftware']:
                self.buttons[button_name].set_sensitive(status)
                self.pages[button_name]['enabled'] = status

    def show_applications(self):

        filter = ['firefox', 'firefox-firma', 'gnome-terminal']
        app_list = Gio.app_info_get_all()

        for app in app_list:
            if app.get_executable() in filter:

                icon = app.get_icon()
                pixbuf = None

                try:
                    if isinstance(icon, Gio.FileIcon):
                        pixbuf = GdkPixbuf.Pixbuf.new_from_file(icon.get_file().get_path())

                    elif isinstance(icon, Gio.ThemedIcon):
                        theme = Gtk.IconTheme.get_default()
                        pixbuf = theme.load_icon(icon.get_names()[0], 24, Gtk.IconLookupFlags.USE_BUILTIN)

                    pixbuf = pixbuf.scale_simple(24, 24, GdkPixbuf.InterpType.BILINEAR)

                except Exception, e:
                    print "Error loading icon pixbuf: " + e.message;

                btn = Gtk.Button()
                btn.set_relief(Gtk.ReliefStyle.NONE)
                btn.set_property('focus-on-click', False)
                btn.set_property('xalign', 0)

                img = Gtk.Image.new_from_pixbuf(pixbuf)

                lbl = Gtk.Label()
                lbl.set_text(app.get_name())

                box = Gtk.HBox()
                box.set_spacing(10)
                box.pack_start(img, False, True, 0)
                box.pack_start(lbl, False, True, 0)
                btn.add(box)

                self.boxApplications.add(btn)
                box.show()
                btn.show()
                img.show()
                lbl.show()

                btn.connect('clicked', self.on_btnApplication_Clicked, app)

    def on_btnApplication_Clicked(self, button, app):
        app.launch([], None)
