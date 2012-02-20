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
from DateSyncConf import DateSyncConf


class ServerConf():

    # Version of the configuration JSON file
    VERSION = '1.3'

    def __init__(self):
        self._data = {}
        self._data['version'] = ServerConf.VERSION
        self._data['organization'] = ''
        self._data['notes'] = ''
        self._ldap_conf = LdapConf()
        self._chef_conf = ChefConf()
        self._ad_conf = ActiveDirectoryConf()
        self._ntp_conf = DateSyncConf()

    def load_data(self, conf):
        msg = 'ServerConf: Key "%s" not found in the configuration file.'
        try:
            v = conf['version']
            if v != ServerConf.VERSION:
                print 'WARNING: ServerConf and AUTOCONFIG_JSON version mismatch!'
        except KeyError as e:
            print msg % ('version',)
        try:
            self.set_organization(conf['organization'])
        except KeyError as e:
            print msg % ('organization',)
        try:
            self.set_notes(conf['notes'])
        except KeyError as e:
            print msg % ('notes',)
        try:
            self._ldap_conf.load_data(conf['pamldap'])
        except KeyError as e:
            print msg % ('pamldap',)
        try:
            self._chef_conf.load_data(conf['chef'])
        except KeyError as e:
            print msg % ('chef',)
        try:
            self._ad_conf.load_data(conf['ad'])
        except KeyError as e:
            print msg % ('ad',)
        try:
            self._ntp_conf.load_data(conf['ntp'])
        except KeyError as e:
            print msg % ('ntp',)

    def validate(self):
        valid = len(self._data['version']) > 0 \
            and self._ldap_conf.validate() \
            and self._chef_conf.validate() \
            and self._ad_conf.validate() \
            and self._ntp_conf.validate()
        return valid

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

    def get_ntp_conf(self):
        return self._ntp_conf

