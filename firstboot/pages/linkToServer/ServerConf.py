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
        raise ServerConfException(e.args[0])

    except ValueError as e:
        raise ServerConfException(_('Configuration file is not valid.'))

    except Exception as e:
        raise Exception(e.args[0])

def update_organization(server_conf):
    print server_conf.get_organization()
    return True

def link_to_ldap(ldap_conf):

    url = ldap_conf.get_url()
    basedn = ldap_conf.get_basedn()
    binddn = ldap_conf.get_binddn()
    password = ldap_conf.get_password()
    errors = []

    if len(url) == 0:
        errors.append(_('The LDAP URL cannot be empty.'))

    if len(basedn) == 0:
        errors.append(_('The LDAP BaseDN cannot be empty.'))

    if len(binddn) == 0:
        errors.append(_('The LDAP BindDN cannot be empty.'))

    if len(errors) > 0:
        return errors

    try:

        script = os.path.join('/usr/local/bin', __LDAP_CONF_SCRIPT__)
        if not os.path.exists(script):
            raise LinkToLDAPException(_("The LDAP configuration script couldn't be found") + ': ' + script)

        cmd = 'gksu "%s %s %s %s %s"' % (script, url, basedn, binddn, password)
        args = shlex.split(cmd)

        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        exit_code = os.waitpid(process.pid, 0)
        output = process.communicate()[0]

        if exit_code[1] == 0:
            #self.show_status(__STATUS_CONFIG_CHANGED__)
            pass

        else:
            #self.show_status(__STATUS_ERROR__, Exception(_('An error has occurred') + ': ' + output))
            raise LinkToLDAPException(_('LDAP setup error') + ': ' + output)


    except Exception as e:
        #self.show_status(__STATUS_ERROR__, Exception(_('An error has occurred')))
        raise e

    return True
    #self.translate()

def unlink_from_ldap():

    try:

        script = os.path.join('/usr/local/bin', __LDAP_CONF_SCRIPT__)
        if not os.path.exists(script):
            raise LinkToLDAPException("The file could not be found: " + script)

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
        self.show_status(__STATUS_ERROR__, Exception(_('An error has occurred.')))
        print e

    self.translate()

def link_to_chef(chef_conf):

    url = chef_conf.get_url()
    pemurl = chef_conf.get_pem_url()
    errors = []

    if len(url) == 0:
        errors.append(_('The Chef URL cannot be empty.'))

    if len(pemurl) == 0:
        errors.append(_('The Chef certificate URL cannot be empty.'))

    if len(errors) > 0:
        return errors

    try:
        pass

    except Exception as e:
        raise e

    return True

def unlink_from_chef():
    pass

class ServerConf():

    def __init__(self, json_conf=None):
        self._data = json_conf
        self._validate()
        self._ldap_conf = LdapConf(self._data['pamldap'])
        self._chef_conf = ChefConf(self._data['chef'])

    def _validate(self):
        if self._data is None:
            self._data = {}
            self._data['version'] = __CONFIG_FILE_VERSION__
            self._data['organization'] = ''
            self._data['pamldap'] = None
            self._data['chef'] = None

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

    def __init__(self, json_conf=None):
        self._data = json_conf
        self._validate()

    def _validate(self):
        if self._data is None:
            self._data = {}
            self._data['url'] = ''
            self._data['basedn'] = ''
            self._data['binddn'] = ''
            self._data['password'] = ''

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

    def __init__(self, json_conf=None):
        self._data = json_conf
        self._validate()

    def _validate(self):
        if self._data is None:
            self._data = {}
            self._data['url'] = ''
            self._data['pemurl'] = ''

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


class ServerConfException(Exception):
    '''
    Raised when there are errors retrieving the remote configuration.
    '''

    def __init__(self, msg):
        Exception.__init__(self, msg)

class LinkToLDAPException(Exception):
    '''
    Raised when there are errors trying to link the client to a LDAP server. 
    '''

    def __init__(self, msg):
        Exception.__init__(self, msg)

class LinkToChefException(Exception):
    '''
    Raised when there are errors trying to link the client to a Chef server. 
    '''

    def __init__(self, msg):
        Exception.__init__(self, msg)
