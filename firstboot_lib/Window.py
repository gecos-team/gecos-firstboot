# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
### BEGIN LICENSE
# This file is in the public domain
### END LICENSE

import gtk
import logging
logger = logging.getLogger('firstboot_lib')

from . helpers import get_builder, show_uri, get_help_uri
from . preferences import preferences

# This class is meant to be subclassed by FirstbootWindow.  It provides
# common functions and some boilerplate.
class Window(gtk.Window):
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

    def __new__(cls):
        """Special static method that's automatically called by Python when 
        constructing a new instance of this class.
        
        Returns a fully instantiated BaseFirstbootWindow object.
        """
        builder = get_builder('FirstbootWindow')
        new_object = builder.get_object("FirstbootWindow")
        new_object.finish_initializing(builder)
        return new_object

    def finish_initializing(self, builder):
        """Called while initializing this instance in __new__

        finish_initializing should be called after parsing the UI definition
        and creating a FirstbootWindow object with it in order to finish
        initializing the start of the new FirstbootWindow instance.
        """
        # Get a reference to the builder and set up the signals.
        self.builder = builder
        self.ui = builder.get_ui(self, True)

        preferences.connect('changed', self.on_preferences_changed)

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
        gtk.main_quit()

    def on_preferences_changed(self, widget, data=None):
        logger.debug('main window received preferences changed')
        for key in data:
            logger.debug('preference changed: %s = %s' % (key, preferences[key]))
