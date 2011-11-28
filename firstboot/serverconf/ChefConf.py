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


class ChefConf():

    def __init__(self):
        self._data = {}
        self._data['chef_server_url'] = ''
        self._data['chef_validation_url'] = ''

    def load_data(self, conf):
        self.set_url(conf['chef_server_url'])
        self.set_pem_url(conf['chef_validation_url'])

    def validate(self):
        valid = len(self._data['chef_server_url']) > 0 \
            and len(self._data['chef_validation_url']) > 0
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
