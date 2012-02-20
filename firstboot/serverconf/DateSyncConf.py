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

import firstboot.validation as validation


class DateSyncConf():

    def __init__(self):
        self._data = {}
        self._data['host'] = ''

    def load_data(self, conf):
        msg = 'DateSyncConf: Key "%s" not found in the configuration file.'
        try:
            self.set_host(conf['host'])
        except KeyError as e:
            print msg % ('host',)

    def validate(self):
        valid = validation.is_qname(self._data['host'])
        return valid

    def get_host(self):
        return self._data['host'].encode('utf-8')

    def set_host(self, host):
        self._data['host'] = host
        return self

