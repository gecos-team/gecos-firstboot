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

import math
import shlex
import subprocess
import os
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Pango
from gi.repository import Gio
from gi.repository import GdkPixbuf
from gi.repository import GObject
import logging
logger = logging.getLogger('firstboot')

from firstboot_lib import Window, firstbootconfig, FirstbootEntry
import pages
import dbus
from dbus.mainloop.glib import DBusGMainLoop


__DESKTOP_FILE__ = '/etc/xdg/autostart/firstboot.desktop'

NM_DBUS_SERVICE = 'org.freedesktop.NetworkManager'
NM_DBUS_OBJECT_PATH = '/org/freedesktop/NetworkManager'

NM_STATE_UNKNOWN = 0    # Networking state is unknown.
NM_STATE_ASLEEP = 10    # Networking is inactive and all devices are disabled.
NM_STATE_DISCONNECTED = 20    # There is no active network connection.
NM_STATE_DISCONNECTING = 30    # Network connections are being cleaned up.
NM_STATE_CONNECTING = 40    # A network device is connecting to a network and there is no other available network connection.
NM_STATE_CONNECTED_LOCAL = 50    # A network device is connected, but there is only link-local connectivity.
NM_STATE_CONNECTED_SITE = 60    # A network device is connected, but there is only site-local connectivity.
NM_STATE_CONNECTED_GLOBAL = 70    # A network device is connected, with global network connectivity.


# See firstboot_lib.Window.py for more details about how this class works
class FirstbootWindow(Window):
    __gtype_name__ = "FirstbootWindow"

    __gsignals__ = {
        'link-status': (GObject.SignalFlags.ACTION, None, (GObject.TYPE_BOOLEAN,))
    }

    def finish_initializing(self, builder, options=None):   # pylint: disable=E1002
        """Set up the main window"""
        super(FirstbootWindow, self).finish_initializing(builder)
        self.connect("delete_event", self.on_delete_event)

        screen = Gdk.Screen.get_default()
        sw = math.floor(screen.width() - screen.width() / 6)
        sh = math.floor(screen.height() - screen.height() / 6)
        self.resize(sw, sh)

        self.btnPrev = self.ui.btnPrev
        self.btnNext = self.ui.btnNext

        self.cmd_options = options
        self.fbe = FirstbootEntry.FirstbootEntry()

        iconfile = firstbootconfig.get_data_file('media', '%s' % ('wizard1.png',))
        self.set_icon_from_file(iconfile)

        self.pages = {}
        self.buttons = {}
        self.current_page = None
        self.is_last_page = False
        self.fully_configured = False

        self.translate()
        self.build_index()

        first_page = self.pages[pages.pages[0]]
        self.set_current_page(first_page['module'])
        self.show_applications()

        self.set_focus(self.ui.btnNext)

        # Register changes on NetworkManager so we will
        # know the connection state.
        DBusGMainLoop(set_as_default=True)

        self.system_bus = dbus.SystemBus()
        self.nm = self.system_bus.get_object(NM_DBUS_SERVICE, NM_DBUS_OBJECT_PATH)
        self.nm.connect_to_signal('StateChanged', self.on_nm_state_changed)

        # Read the connection state now since it's posible we don't
        # get any signals at that point.
        i = dbus.Interface(self.nm, 'org.freedesktop.DBus.Properties')
        state = i.Get(NM_DBUS_SERVICE, 'State')
        self.on_nm_state_changed(state)

    def translate(self):
        self.set_title(_('First Boot Assistant'))
        self.ui.lblDescription.set_text('')
        self.ui.btnPrev.set_label(_('Previous'))
        self.ui.btnNext.set_label(_('Next'))

    def on_btnClose_Clicked(self, button):
        self.destroy()

    def on_delete_event(self, widget, data=None):
        return self.confirm_exit()

    def confirm_exit(self):

        if self.fully_configured == True:
            if os.path.exists(__DESKTOP_FILE__):
                os.rename(__DESKTOP_FILE__, '/tmp/firstboot.desktop')
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
                os.rename(__DESKTOP_FILE__, '/tmp/firstboot.desktop')
            retval = False

        return retval

    def on_btnIndex_Clicked(self, button, page_name, module=None):
        self.set_current_page(self.pages[page_name]['module'])

    def on_btnPrev_Clicked(self, button):
        self.current_page.previous_page(self.set_current_page)

    def on_btnNext_Clicked(self, button):
        if self.is_last_page == True:
            if not self.confirm_exit():
                self.destroy()
            return
        self.current_page.next_page(self.set_current_page)

    def build_index(self):

        self.pages = {}
        self.buttons = {}

        children = self.ui.boxIndex.get_children()
        for child in children:
            self.ui.boxIndex.remove(child)

        for page_name in pages.pages:
            try:
                module = __import__('firstboot.pages.%s' % page_name, fromlist=['firstboot.pages'])
                button = self.new_index_button(module.__TITLE__, page_name)
                self.pages[page_name] = {
                    'id': page_name,
                    'button': button,
                    'module': module,
                    'enabled': True,
                    'instance': None,
                    'configured': not module.__REQUIRED__
                }
                self.buttons[page_name] = button

            except ImportError, e:
                print e

    def new_index_button(self, page_title, page_name):

        button = Gtk.Button()
        button.set_relief(Gtk.ReliefStyle.NONE)
        button.set_property('focus-on-click', False)
        button.set_property('xalign', 0)

        image_file = firstbootconfig.get_data_file('media', '%s' % ('arrow_right_32.png',))
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(image_file, 8, 8)
        image = Gtk.Image.new_from_pixbuf(pixbuf)
        image.hide()

        #~ image = Gtk.Arrow()
        #~ image.set(Gtk.ArrowType.RIGHT, Gtk.ShadowType.NONE)

        label = Gtk.Label()
        label.set_text(page_title)
        label.show()

        hbox = Gtk.HBox()
        hbox.set_spacing(3)
        hbox.pack_start(image, False, True, 0)
        hbox.pack_start(label, False, True, 0)
        hbox.show()

        button.add(hbox)

        self.ui.boxIndex.pack_start(button, False, True, 0)
        button.connect('clicked', self.on_btnIndex_Clicked, page_name)
        button.show()

        return button

    def set_current_page(self, module, params=None):

        self.ui.btnPrev.set_sensitive(True)
        self.ui.btnNext.set_sensitive(True)
        self.translate()

        try:
            self.current_page.unload_page(params)
        except Exception as e:
            pass

        self.current_page = module.get_page(self)

        try:
            self.current_page.connect('page-changed', self.on_page_changed)
        except Exception as e:
            pass

        try:
            self.current_page.connect('status-changed', self.on_page_status_changed)
        except Exception as e:
            pass

        page_name = module.__name__.split('.')[-1]
        self.is_last_page = (page_name == pages.pages[-1])

        if page_name in self.buttons:
            for button_name in self.buttons:
                self.button_set_inactive(self.buttons[button_name])
            button = self.buttons[page_name]
            self.button_set_active(button)

        for child in self.ui.swContent.get_children():
            self.ui.swContent.remove(child)

        self.ui.swContent.add_with_viewport(self.current_page.get_widget())

        try:
            self.current_page.load_page(params)
        except Exception as e:
            pass

    def on_page_changed(self, sender, module, params):
        self.set_current_page(module, params)

    def on_page_status_changed(self, sender, page_name, configured):
        if page_name in self.pages:
            self.pages[page_name]['configured'] = configured
        self.fully_configured = self.check_fully_configured()

    def check_fully_configured(self):
        configured = True
        for page in self.pages:
            if self.pages[page]['configured'] == False:
                configured = False
                break
        return configured

    def button_set_active(self, button):
        hbox = button.get_children()[0]
        image = hbox.get_children()[0]
        image.show()
        label = hbox.get_children()[1]
        label.set_padding(0, 0)
        label.set_markup('<b>%s</b>' % (label.get_text(),))

    def button_set_inactive(self, button):
        hbox = button.get_children()[0]
        image = hbox.get_children()[0]
        image.hide()
        label = hbox.get_children()[1]
        label.set_padding(10, 0)
        label.set_markup(label.get_text())

    def on_nm_state_changed(self, state):
        ''' Handle the NetworkManager state changed signal. If we have
        global network connectivity then try to connect to the resources.
        We launch a new thread for each resource.
        '''

        linked = state == NM_STATE_CONNECTED_GLOBAL

        for button_name in self.buttons:
            if button_name in ['linkToServer', 'linkToChef', 'installSoftware']:
                self.buttons[button_name].set_sensitive(linked)
                self.pages[button_name]['enabled'] = linked

        self.emit('link-status', linked)

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
                    print "Error loading icon pixbuf: " + e.message

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

                self.ui.boxApplications.add(btn)
                box.show()
                btn.show()
                img.show()
                lbl.show()

                btn.connect('clicked', self.on_btnApplication_Clicked, app)

    def on_btnApplication_Clicked(self, button, app):
        app.launch([], None)
