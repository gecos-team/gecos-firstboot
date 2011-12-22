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

__author__ = "David Amian Valle <damian@emergya.com>"
__copyright__ = "Copyright (C) 2011, Junta de Andalucía <devmaster@guadalinex.org>"
__license__ = "GPL-2"

import firstboot.validation as validation


class ActiveDirectoryConf():

    def __init__(self):
        self._data = {}
        self._data['fqdn'] = ''
        self._data['dns_domain'] = ''
        self._data['user'] = ''
        self._data['passwd'] = ''

    def load_data(self, conf):
        self.set_fqdn(conf['fqdn'])
        self.set_dns_domain(conf['dns'])

    def validate(self):
        valid = not validation.is_empty(self._data['fqdn']) \
            and not validation.is_empty(self._data['dns_domain'])
        return valid

    def get_fqdn(self):
        return self._data['fqdn'].encode('utf-8')

    def set_fqdn(self, fqdn):
        self._data['fqdn'] = fqdn
        return self

    def get_dns_domain(self):
        return self._data['dns_domain'].encode('utf-8')

    def set_dns_domain(self, dns_domain):
        self._data['dns_domain'] = dns_domain
        return self

    def get_user(self):
        return self._data['user'].encode('utf-8')

    def set_user(self, user):
        self._data['user'] = user
        return self

    def get_passwd(self):
        return self._data['passwd'].encode('utf-8')

    def set_passwd(self, passwd):
        self._data['passwd'] = passwd
        return self

    def __str__(self):
        return str(self._data)
