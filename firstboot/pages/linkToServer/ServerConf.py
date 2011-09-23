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
import gtk
import subprocess
import shlex
import urllib
import urllib2
import json
import urlparse
import gobject

import gettext
from gettext import gettext as _
gettext.textdomain('firstboot')


__CONFIG_FILE_VERSION__ = '1.1'

__URLOPEN_TIMEOUT__ = 5
__LDAP_BAK_FILE__ = '/etc/ldap.conf.firstboot.bak'
__LDAP_CONF_SCRIPT__ = 'firstboot-ldapconf.sh'


def get_server_conf(self):

    try:

        fp = urllib2.urlopen(self.get_url(), timeout=__URLOPEN_TIMEOUT__)
        #print fp.url(), fp.info()
        content = fp.read()
        conf = json.loads(content)

        if 'version' in conf and 'uri' in conf and 'port' in conf and 'base' in conf:
            version = conf['version']
            if version != __CONFIG_FILE_VERSION__:
                raise Exception(_('Incorrect version of the configuration file.'))

            server_conf = ServerConf(conf)
            return server_conf

        raise ValueError()

    except urllib2.URLError as e:
        raise LinkToServerException(e.args[0])

    except ValueError as e:
        raise LinkToServerException(_('Configuration file is not valid.'))

    except Exception as e:
        raise Exception(e.args[0])

def apply_conf(server_conf):
    pass

class LinkToServerException(Exception):

    def __init__(self, msg):
        Exception.__init__(self, msg)

class ServerConf():

    def __init__(self, json_conf):
        self._data = json_conf
        self._validate()
        self._ldap_conf = LdapConf(self._data['pamldap'])
        self._chef_conf = ChefConf(self._data['chef'])

    def _validate(self):
        pass

    def get_version(self):
        return self._data['version']

    def get_organization(self):
        return self._data['organization']

    def get_ldap_conf(self):
        return self._ldap_conf

    def get_chef_conf(self):
        return self._chef_conf

class LdapConf():

    def __init__(self, json_conf):
        self._data = json_conf
        self._validate()

    def _validate(self):
        pass

    def get_url(self):
        return self._data['url']

    def get_basedn(self):
        return self._data['basedn']

    def get_binddn(self):
        return self._data['binddn']

    def get_password(self):
        return self._data['password']

class ChefConf():

    def __init__(self, json_conf):
        self._data = json_conf
        self._validate()

    def _validate(self):
        pass

    def get_url(self):
        return self._data['url']

    def get_pem_url(self):
        return self._data['pemurl']
