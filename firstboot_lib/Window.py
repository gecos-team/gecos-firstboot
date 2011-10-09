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
from gi.repository import GObject
import logging
logger = logging.getLogger('firstboot_lib')

from . helpers import get_builder, show_uri, get_help_uri

# This class is meant to be subclassed by FirstbootWindow.  It provides
# common functions and some boilerplate.
class Window(Gtk.Window):
    __gtype_name__ = "Window"

    # To construct a new instance of this method, the following notable
    # methods are called in this order:
    # __new__(cls)
    # __init__(self)
    # finish_initializing(self, builder)
    # __init__(self)
    #
    # For this reason, it's recommended you leave __init__ empty and put
    # your initialization code in finish_initializing

    def __init__(self, options=None):
        GObject.GObject.__init__(self)

    def __new__(cls, options=None):
        """Special static method that's automatically called by Python when
        constructing a new instance of this class.

        Returns a fully instantiated BaseFirstbootWindow object.
        """
        builder = get_builder('FirstbootWindow')
        new_object = builder.get_object("FirstbootWindow")
        new_object.finish_initializing(builder, options)
        return new_object

    def finish_initializing(self, builder, options=None):
        """Called while initializing this instance in __new__

        finish_initializing should be called after parsing the UI definition
        and creating a FirstbootWindow object with it in order to finish
        initializing the start of the new FirstbootWindow instance.
        """

        self.cmd_options = options

        # Get a reference to the builder and set up the signals.
        self.builder = builder
        self.ui = builder.get_ui(self, True)

        # Optional Launchpad integration
        # This shouldn't crash if not found as it is simply used for bug reporting.
        # See https://wiki.ubuntu.com/UbuntuDevelopment/Internationalisation/Coding
        # for more information about Launchpad integration.
        #try:
        #    import LaunchpadIntegration
        #    LaunchpadIntegration.add_items(self.ui.helpMenu, 1, True, True)
        #    LaunchpadIntegration.set_sourcepackagename('firstboot')
        #except ImportError:
        #    pass
        #except Exception:
        #    pass

        # Optional application indicator support
        # Run 'quickly add indicator' to get started.
        # More information:
        #  http://owaislone.org/quickly-add-indicator/
        #  https://wiki.ubuntu.com/DesktopExperienceTeam/ApplicationIndicators
        try:
            from firstboot import indicator
            # self is passed so methods of this class can be called from indicator.py
            # Comment this next line out to disable appindicator
            self.indicator = indicator.new_application_indicator(self)
        except ImportError:
            pass

    def on_destroy(self, widget, data=None):
        """Called when the FirstbootWindow is closed."""
        # Clean up code for saving application state should be added here.
        Gtk.main_quit()
