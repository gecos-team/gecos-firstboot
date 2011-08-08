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
from firstboot.AboutFirstbootDialog import AboutFirstbootDialog
from firstboot.PreferencesFirstbootDialog import PreferencesFirstbootDialog

# See firstboot_lib.Window.py for more details about how this class works
class FirstbootWindow(Window):
    __gtype_name__ = "FirstbootWindow"
    
    def finish_initializing(self, builder): # pylint: disable=E1002
        """Set up the main window"""
        super(FirstbootWindow, self).finish_initializing(builder)

        self.AboutDialog = AboutFirstbootDialog
        self.PreferencesDialog = PreferencesFirstbootDialog

        # Code for other initialization actions should be added here.

