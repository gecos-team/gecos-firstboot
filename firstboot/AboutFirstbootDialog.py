# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
### BEGIN LICENSE
# This file is in the public domain
### END LICENSE

import gettext
from gettext import gettext as _
gettext.textdomain('firstboot')

import logging
logger = logging.getLogger('firstboot')

from firstboot_lib.AboutDialog import AboutDialog

# See firstboot_lib.AboutDialog.py for more details about how this class works.
class AboutFirstbootDialog(AboutDialog):
    __gtype_name__ = "AboutFirstbootDialog"
    
    def finish_initializing(self, builder): # pylint: disable=E1002
        """Set up the about dialog"""
        super(AboutFirstbootDialog, self).finish_initializing(builder)

        # Code for other initialization actions should be added here.

