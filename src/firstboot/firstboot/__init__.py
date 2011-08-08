# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
### BEGIN LICENSE
# This file is in the public domain
### END LICENSE

import os
import optparse

import gettext
from gettext import gettext as _
gettext.textdomain('firstboot')

import gtk

from firstboot import FirstbootWindow

from firstboot_lib import set_up_logging, preferences, get_version

def parse_options():
    """Support for command line options"""
    parser = optparse.OptionParser(version="%%prog %s" % get_version())
    parser.add_option(
        "-v", "--verbose", action="count", dest="verbose",
        help=_("Show debug messages (-vv debugs firstboot_lib also)"))
    parser.add_option(
        "-d", "--debug", action="store_true", dest="debug",
        help=_("Debug mode. Force run the application after the first start"))
    (options, args) = parser.parse_args()

    set_up_logging(options)
    return options

def is_first_start(debug):

    config_path = os.path.join(os.getenv('HOME'), '.config/firstboot')
    config_file = os.path.join(config_path, 'firstboot.conf')

    if not debug and os.path.exists(config_file):
        return False

    if not os.path.exists(config_path):
        os.mkdir(config_path)

    if not os.path.exists(config_file):
        fd = open(config_file, 'w')
        if fd != None:
            fd.write('[firstboot]')
            fd.close()

    return True

def main():
    'constructor for your class instances'
    options = parse_options()

    if not is_first_start(options.debug):
        return

    # preferences
    # set some values for our first session
    # TODO: replace defaults with your own values
    default_preferences = {
    'example_entry': 'I remember stuff',
    }
    preferences.update(default_preferences)
    # user's stored preferences are used for 2nd and subsequent sessions
    preferences.db_connect()
    preferences.load()

    # Run the application.    
    window = FirstbootWindow.FirstbootWindow()
    window.show()
    gtk.main()

    preferences.save()
