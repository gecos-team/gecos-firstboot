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


def parse_url(url):
    parsed_url = list(urlparse.urlparse(url))
    if parsed_url[0] in ('http', 'https'):
        query = urlparse.parse_qsl(parsed_url[4])
        query.append(('v', ServerConf.__CONFIG_FILE_VERSION__))
        query = urllib.urlencode(query)
        parsed_url[4] = query
    url = urlparse.urlunparse(parsed_url)
    return url

def get_server_conf(url):

    try:

        url = parse_url(url)
        #print url
        fp = urllib2.urlopen(url, timeout=__URLOPEN_TIMEOUT__)
        #print fp.url(), fp.info()
        content = fp.read()
        conf = json.loads(content)
        #print conf

        if 'version' in conf:
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

def link_to_server():

    try:

        conf = self.get_conf_from_server()

        script = os.path.join('/usr/local/bin', __LDAP_CONF_SCRIPT__)
        if not os.path.exists(script):
            raise LinkToServerException("The file could not be found: " + script)

        cmd = 'gksu "%s %s %s %s"' % (script, str(conf['uri']), str(conf['port']), str(conf['base']))
        args = shlex.split(cmd)

        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        exit_code = os.waitpid(process.pid, 0)
        output = process.communicate()[0]

        if exit_code[1] == 0:
            self.show_status(__STATUS_CONFIG_CHANGED__)

        else:
            self.show_status(__STATUS_ERROR__, Exception(_('An error has occurred') + ': ' + output))

    except LinkToServerException as e:
        self.show_status(__STATUS_ERROR__, e)

    except Exception as e:
        self.show_status(__STATUS_ERROR__, Exception(_('An error has occurred')))
        print e

    self.translate()

def unlink_from_server():

    try:

        script = os.path.join('/usr/local/bin', __LDAP_CONF_SCRIPT__)
        if not os.path.exists(script):
            raise LinkToServerException("The file could not be found: " + script)

        cmd = 'gksu "%s --restore"' % (script,)
        args = shlex.split(cmd)

        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        exit_code = os.waitpid(process.pid, 0)
        output = process.communicate()[0]

        if exit_code[1] == 0:
            self.show_status(__STATUS_CONFIG_CHANGED__)

        else:
            self.show_status(__STATUS_ERROR__, Exception(_('An error has occurred') + ': ' + output))

    except Exception as e:
        self.show_status(__STATUS_ERROR__, Exception(_('An error has occurred')))
        print e

    self.translate()

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
        return str(self._data['version'])

    def set_version(self, version):
        self._data['version'] = version
        return self

    def get_organization(self):
        return str(self._data['organization'])

    def set_organization(self, organization):
        self._data['organization'] = organization
        return self

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
        return str(self._data['url'])

    def set_url(self, url):
        self._data['url'] = url
        return self

    def get_basedn(self):
        return str(self._data['basedn'])

    def set_basedn(self, basedn):
        self._data['basedn'] = basedn
        return self

    def get_binddn(self):
        return str(self._data['binddn'])

    def set_binddn(self, binddn):
        self._data['binddn'] = binddn
        return self

    def get_password(self):
        return str(self._data['password'])

    def set_password(self, password):
        self._data['password'] = password
        return self

class ChefConf():

    def __init__(self, json_conf):
        self._data = json_conf
        self._validate()

    def _validate(self):
        pass

    def get_url(self):
        return str(self._data['url'])

    def set_url(self, url):
        self._data['url'] = url
        return self

    def get_pem_url(self):
        return str(self._data['pemurl'])

    def set_pem_url(self, pem_url):
        self._data['pemurl'] = pem_url
        return self
