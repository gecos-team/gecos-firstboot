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


class ChefConf():

    def __init__(self):
        self._data = {}
        self._data['chef_server_url'] = ''
        self._data['chef_validation_url'] = ''
        self._data['chef_default_role'] = ''

    def load_data(self, conf):
        msg = 'ServerConf: Key "%s" not found in the configuration file.'
        try:
            self.set_url(conf['chef_server_url'])
        except KeyError as e:
            print msg % ('chef_server_url',)
        try:
            self.set_pem_url(conf['chef_validation_url'])
        except KeyError as e:
            print msg % ('chef_validation_url',)
        try:
            self.set_default_role(conf['chef_default_role'])
        except KeyError as e:
            print msg % ('chef_default_role',)

    def validate(self):
        valid = validation.is_url(self._data['chef_server_url']) \
            and validation.is_url(self._data['chef_validation_url']) \
            and validation.is_qname(self._data['chef_default_role'])
        return valid

    def get_url(self):
        return self._data['chef_server_url'].encode('utf-8')

    def set_url(self, url):
        self._data['chef_server_url'] = url
        return self

    def get_pem_url(self):
        return self._data['chef_validation_url'].encode('utf-8')

    def set_pem_url(self, pem_url):
        self._data['chef_validation_url'] = pem_url
        return self

    def get_default_role(self):
        return self._data['chef_default_role'].encode('utf-8')

    def set_default_role(self, default_role):
        self._data['chef_default_role'] = default_role
        return self

    # --- Next fields are not present in the JSON file but are
    # setted on runtime by Firstboot ---

    def get_hostname(self):
        if not 'hostname' in self._data:
            self._data['hostname'] = ''
        return self._data['hostname'].encode('utf-8')

    def set_hostname(self, hostname):
        self._data['hostname'] = hostname
        return self

    def get_user(self):
        if not 'user' in self._data:
            self._data['user'] = ''
        return self._data['user'].encode('utf-8')

    def set_user(self, user):
        self._data['user'] = user
        return self

    def get_password(self):
        if not 'password' in self._data:
            self._data['password'] = ''
        return self._data['password'].encode('utf-8')

    def set_password(self, password):
        self._data['password'] = password
        return self
