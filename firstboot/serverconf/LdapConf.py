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


class LdapConf():

    def __init__(self):
        self._data = {}
        self._data['uri'] = ''
        self._data['base'] = ''
        self._data['basegroup'] = ''
        self._data['binddn'] = ''
        self._data['bindpw'] = ''
        self._data['anonymous'] = ''

    def load_data(self, conf):
        msg = 'ServerConf: Key "%s" not found in the configuration file.'
        try:
            self.set_url(conf['uri'])
        except KeyError as e:
            print msg % ('uri',)
        try:
            self.set_basedn(conf['base'])
        except KeyError as e:
            print msg % ('base',)
        try:
            self.set_basedngroup(conf['basegroup'])
        except KeyError as e:
            print msg % ('basegroup',)
        try:
            self.set_binddn(conf['binddn'])
        except KeyError as e:
            print msg % ('binddn',)
        try:
            self.set_password(conf['bindpw'])
        except KeyError as e:
            print msg % ('bindpw',)
        try:
            self.set_anonymous(conf['anonymous'])
        except KeyError as e:
            print msg % ('anonymous',)

    def validate(self):
        valid = validation.is_url(self._data['uri']) \
            and not validation.is_empty(self._data['base']) 
        return valid

    def get_url(self):
        return self._data['uri'].encode('utf-8')

    def set_url(self, url):
        self._data['uri'] = url
        return self

    def get_basedngroup(self):
        return self._data['basegroup'].encode('utf-8')

    def set_basedngroup(self, basedngroup):
        self._data['basegroup'] = basedngroup
        return self

    def get_basedn(self):
        return self._data['base'].encode('utf-8')

    def set_basedn(self, basedn):
        self._data['base'] = basedn
        return self

    def get_binddn(self):
        return self._data['binddn'].encode('utf-8')

    def set_binddn(self, binddn):
        self._data['binddn'] = binddn
        return self

    def get_password(self):
        return self._data['bindpw'].encode('utf-8')

    def set_password(self, password):
        self._data['bindpw'] = password
        return self

    def get_anonymous(self):
        return self._data['anonymous']

    def __str__(self):
        return str(self._data)

    def set_anonymous(self, anonymous):
        self._data['anonymous'] = anonymous
        return self
