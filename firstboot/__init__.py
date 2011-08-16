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
import optparse

import gettext
from gettext import gettext as _
gettext.bindtextdomain('firstboot', '/usr/local/share/locale')

import gtk

from firstboot import FirstbootWindow

from firstboot_lib import set_up_logging, get_version

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

    # Run the application.    
    window = FirstbootWindow.FirstbootWindow()
    window.show()
    gtk.main()
