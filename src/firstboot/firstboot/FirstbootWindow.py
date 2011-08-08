# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
### BEGIN LICENSE
# This file is in the public domain
### END LICENSE

import gettext
from gettext import gettext as _
gettext.textdomain('firstboot')

import gtk
import logging
logger = logging.getLogger('firstboot')

from firstboot_lib import Window

import pages

# See firstboot_lib.Window.py for more details about how this class works
class FirstbootWindow(Window):
    __gtype_name__ = "FirstbootWindow"

    def finish_initializing(self, builder): # pylint: disable=E1002
        """Set up the main window"""
        super(FirstbootWindow, self).finish_initializing(builder)

        self.lblDescription = builder.get_object('lblDescription')
        self.boxContent = builder.get_object('boxContent')
        self.swContent = builder.get_object('swContent')
        self.boxIndex = builder.get_object('boxIndex')
        #self.btnClose = builder.get_object('btnClose')
        self.btnPrev = builder.get_object('btnPrev')
        self.btnNext = builder.get_object('btnNext')

        self.pages = {}
        self.buttons = {}
        self.current_page = None

        self.translate()
        self.build_index()

        self.set_current_page(pages.pages[0])
        self.on_link_status(None, False)

    def translate(self):
        self.set_title(_('First Boot Assistant'))
        self.lblDescription.set_text(_(''))
        #self.btnClose.set_label(_('Close'))
        self.btnPrev.set_label(_('Previous'))
        self.btnNext.set_label(_('Next'))

    def on_btnClose_Clicked(self, button):
        self.destroy()

    def on_btnIndex_Clicked(self, button, page_name, module):
        self.set_current_page(page_name)

    def on_btnPrev_Clicked(self, button):

        index = pages.pages.index(self.current_page['id'])

        if index <= 0:
            index = 0
            return

        enabled = False
        while not enabled and index >= 0:
            index -= 1
            prev_page_name = pages.pages[index]
            enabled = self.pages[prev_page_name]['enabled']

        if enabled:
            self.set_current_page(prev_page_name)

    def on_btnNext_Clicked(self, button):

        index = pages.pages.index(self.current_page['id'])

        if index >= len(pages.pages) - 1:
            index = len(pages.pages) - 1
            return

        enabled = False
        while not enabled and index < len(pages.pages):
            index += 1
            next_page_name = pages.pages[index]
            enabled = self.pages[next_page_name]['enabled']

        if enabled:
            self.set_current_page(next_page_name)

    def build_index(self):

        self.pages = {}
        self.buttons = {}

        children = self.boxIndex.get_children()
        for child in children:
            self.boxIndex.remove(child)

        for page_name in pages.pages:
            try:
                module = __import__('firstboot.pages.%s' % page_name, fromlist=['firstboot.pages'])

                button = gtk.Button(module.__TITLE__)
                button.set_relief(gtk.RELIEF_NONE)
                button.set_property('xalign', 0)
                self.boxIndex.pack_start(button, False, True)
                button.connect('clicked', self.on_btnIndex_Clicked, page_name, module)
                button.show()

                self.pages[page_name] = {'id': page_name, 'button': button, 'module': module, 'enabled': True}
                self.buttons[page_name] = button

            except ImportError, e:
                print e

    def set_current_page(self, page_name):

        try:
            self.current_page['page'].unload_page()
        except Exception as e:
            pass

        self.current_page = self.pages[page_name]
        button = self.pages[page_name]['button']
        module = self.pages[page_name]['module']

        self.current_page['page'] = module.get_page()

        try:
            self.current_page['page'].load_page(self)
        except Exception as e:
            pass

        try:
            self.current_page['page'].connect('link-status', self.on_link_status)
        except Exception as e:
            pass


        #for btn in self.buttons:
        #    self.button_set_inactive(btn)

        #self.button_set_active(button)

        for child in self.swContent.get_children():
            self.swContent.remove(child)

        self.swContent.add_with_viewport(self.current_page['page'].get_widget())

    def button_set_active(self, button):
        pass

    def button_set_inactive(self, button):
        pass

    def on_link_status(self, sender, status):
        for button_name in self.buttons:
            if button_name in ['linkToServer', 'installSoftware']:
                self.buttons[button_name].set_sensitive(status)
                self.pages[button_name]['enabled'] = status
