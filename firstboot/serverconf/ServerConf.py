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


import firstboot.serverconf
from LdapConf import LdapConf
from ChefConf import ChefConf
from ActiveDirectoryConf import ActiveDirectoryConf

class ServerConf():

    def __init__(self):
        self._data = {}
        self._data['version'] = firstboot.serverconf.__CONFIG_FILE_VERSION__
        self._data['organization'] = ''
        self._data['notes'] = ''
        self._ldap_conf = LdapConf()
        self._chef_conf = ChefConf()
        self._ad_conf = ActiveDirectoryConf()

    def load_data(self, conf):
        self.set_organization(conf['organization'])
        self.set_notes(conf['notes'])
        self._ldap_conf.load_data(conf['pamldap'])
        self._chef_conf.load_data(conf['chef'])
        self._ad_conf.load_data(conf['ad'])

    def validate(self):
        valid = len(self._data['version']) > 0 \
            and self._ldap_conf.validate() \
            and self._chef_conf.validate()
        return valid;

    def get_version(self):
        return self._data['version'].encode('utf-8')

    def set_version(self, version):
        self._data['version'] = version
        return self

    def get_organization(self):
        return self._data['organization'].encode('utf-8')

    def set_organization(self, organization):
        self._data['organization'] = organization
        return self

    def get_notes(self):
        return self._data['notes'].encode('utf-8')

    def set_notes(self, notes):
        self._data['notes'] = notes
        return self

    def get_ad_conf(self):
        return self._ad_conf

    def get_ldap_conf(self):
        return self._ldap_conf

    def get_chef_conf(self):
        return self._chef_conf
