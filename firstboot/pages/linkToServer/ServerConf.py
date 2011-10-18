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
import subprocess
import shlex
import urllib
import urllib2
import json
import urlparse
import tempfile

from firstboot_lib import firstbootconfig

import gettext
from gettext import gettext as _
gettext.textdomain('firstboot')


__CONFIG_FILE_VERSION__ = '1.1'

__URLOPEN_TIMEOUT__ = 15
__BIN_PATH__ = firstbootconfig.get_bin_path()
__LDAP_CONF_SCRIPT__ = 'firstboot-ldapconf.sh'
__CHEF_CONF_SCRIPT__ = 'firstboot-chef.sh'


def parse_url(url):
    parsed_url = list(urlparse.urlparse(url))
    if parsed_url[0] in ('http', 'https'):
        query = urlparse.parse_qsl(parsed_url[4])
        query.append(('v', __CONFIG_FILE_VERSION__))
        query = urllib.urlencode(query)
        parsed_url[4] = query
    url = urlparse.urlunparse(parsed_url)
    return url

def get_server_conf(url):

    try:

        url = parse_url(url)
        fp = urllib2.urlopen(url, timeout=__URLOPEN_TIMEOUT__)
        content = fp.read()
        conf = json.loads(content)

        if 'version' in conf:
            version = conf['version']
            if version != __CONFIG_FILE_VERSION__:
                raise Exception(_('Incorrect version of the configuration file.'))

            server_conf = ServerConf(conf)
            return server_conf

        raise ValueError()

    except urllib2.URLError as e:
        raise ServerConfException(e)

    except ValueError as e:
        raise ServerConfException(_('Configuration file is not valid.'))

def get_chef_pem(url):

    try:

        url = parse_url(url)
        fp = urllib2.urlopen(url, timeout=__URLOPEN_TIMEOUT__)
        content = fp.read()

        (fd, filepath) = tempfile.mkstemp(dir='/tmp') # [suffix=''[, prefix='tmp'[, dir=None[, text=False]]]])
        fp = os.fdopen(fd, "w+b")
        if fp:
            fp.write(content)
            fp.close()

        return filepath

    except urllib2.URLError as e:
        raise ServerConfException(e)

def get_chef_hostnames(chef_conf):

    chef_url = chef_conf.get_url()
    pem_url = chef_conf.get_pem_url()
    pem_file_path = get_chef_pem(pem_url)

    cmd = 'knife node list -u chef-validator -k %s -s %s' % (pem_file_path, chef_url)
    args = shlex.split(cmd)

    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    exit_code = os.waitpid(process.pid, 0)
    output = process.communicate()[0]
    output = output.strip()

    names = []
    if exit_code[1] != 0:
        raise ServerConf.ServerConfException(_('Couldn\t retrieve the host names list') + ': ' + output)

    else:
        try:
            names = json.loads(output)
        except ValueError as e:
            names = output.split('\n')

    hostnames = []
    for name in names:
        name = name.strip()
        if name.startswith('WARNING') or name.startswith('ERROR'):
            continue
        hostnames.append(name)

    os.remove(pem_file_path)
    return hostnames

def ldap_is_configured():
    try:

        script = os.path.join(__BIN_PATH__, __LDAP_CONF_SCRIPT__)
        if not os.path.exists(script):
            raise LinkToLDAPException(_("The LDAP configuration script couldn't be found") + ': ' + script)

        cmd = '"%s" "--query"' % (script,)
        args = shlex.split(cmd)

        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        exit_code = os.waitpid(process.pid, 0)
        output = process.communicate()[0]
        output = output.strip()

        if exit_code[1] == 0:
            ret = bool(int(output))
            return ret

        else:
            raise LinkToLDAPException(_('LDAP setup error') + ': ' + output)


    except Exception as e:
        raise e

def chef_is_configured():
    try:

        script = os.path.join(__BIN_PATH__, __CHEF_CONF_SCRIPT__)
        if not os.path.exists(script):
            raise LinkToChefException(_("The Chef configuration script couldn't be found") + ': ' + script)

        cmd = '"%s" "--query"' % (script,)
        args = shlex.split(cmd)

        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        exit_code = os.waitpid(process.pid, 0)
        output = process.communicate()[0]
        output = output.strip()

        if exit_code[1] == 0:
            ret = bool(int(output))
            return ret

        else:
            raise LinkToChefException(_('Chef setup error') + ': ' + output)


    except Exception as e:
        raise e


def setup_server(server_conf, link_ldap=False, unlink_ldap=False,
                link_chef=False, unlink_chef=False):

    result = True
    messages = []

    if unlink_ldap == True:
        try:
            ret = unlink_from_ldap()
            if ret == True:
                messages.append({'type': 'info', 'message': _('Workstation has been unlinked from LDAP.')})
            else:
                messages += ret
        except Exception as e:
            messages.append({'type': 'error', 'message': str(e)})

    elif link_ldap == True:
        try:
            ret = link_to_ldap(server_conf.get_ldap_conf())
            if ret == True:
                messages.append({'type': 'info', 'message': _('The LDAP has been configured successfully.')})
            else:
                messages += ret
        except Exception as e:
            messages.append({'type': 'error', 'message': str(e)})

    if unlink_chef == True:
        try:
            ret = unlink_from_chef()
            if ret == True:
                messages.append({'type': 'info', 'message': _('Workstation has been unlinked from Chef.')})
            else:
                messages += ret
        except Exception as e:
            messages.append({'type': 'error', 'message': str(e)})

    elif link_chef == True:
        try:
            ret = link_to_chef(server_conf.get_chef_conf())
            if ret == True:
                messages.append({'type': 'info', 'message': _('The Chef client has been configured successfully.')})
            else:
                messages += ret
        except Exception as e:
            messages.append({'type': 'error', 'message': str(e)})

    for msg in messages:
        if msg['type'] == 'error':
            result = False
            break

    return result, messages

def link_to_ldap(ldap_conf):

    url = ldap_conf.get_url()
    basedn = ldap_conf.get_basedn()
    binddn = ldap_conf.get_binddn()
    password = ldap_conf.get_password()
    errors = []

    if len(url) == 0:
        errors.append({'type': 'error', 'message': _('The LDAP URL cannot be empty.')})

    if len(basedn) == 0:
        errors.append({'type': 'error', 'message': _('The LDAP BaseDN cannot be empty.')})

    if len(binddn) == 0:
        errors.append({'type': 'error', 'message': _('The LDAP BindDN cannot be empty.')})

    if len(errors) > 0:
        return errors

    try:

        script = os.path.join(__BIN_PATH__, __LDAP_CONF_SCRIPT__)
        if not os.path.exists(script):
            raise LinkToLDAPException(_("The LDAP configuration script couldn't be found") + ': ' + script)

        cmd = '"%s" "%s" "%s" "%s" "%s"' % (script, url, basedn, binddn, password)
        args = shlex.split(cmd)

        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        exit_code = os.waitpid(process.pid, 0)
        output = process.communicate()[0]

        if exit_code[1] != 0:
            raise LinkToLDAPException(_('LDAP setup error') + ': ' + output)

    except Exception as e:
        raise e

    return True

def unlink_from_ldap():

    try:

        script = os.path.join(__BIN_PATH__, __LDAP_CONF_SCRIPT__)
        if not os.path.exists(script):
            raise LinkToLDAPException("The file could not be found: " + script)

        cmd = '"%s" "--restore"' % (script,)
        args = shlex.split(cmd)

        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        exit_code = os.waitpid(process.pid, 0)
        output = process.communicate()[0]

        if exit_code[1] != 0:
            raise LinkToLDAPException(_('An error has ocurred unlinking from LDAP') + ': ' + output)

    except Exception as e:
        raise e

    return True

def link_to_chef(chef_conf):

    url = chef_conf.get_url()
    pemurl = chef_conf.get_pem_url()
    hostname = chef_conf.get_hostname()
    errors = []

    if len(url) == 0:
        errors.append({'type': 'error', 'message': _('The Chef URL cannot be empty.')})

    if len(pemurl) == 0:
        errors.append({'type': 'error', 'message': _('The Chef certificate URL cannot be empty.')})

    if len(hostname) == 0:
        errors.append({'type': 'error', 'message': _('The Chef host name cannot be empty.')})

    if len(errors) > 0:
        return errors

    try:

        script = os.path.join(__BIN_PATH__, __CHEF_CONF_SCRIPT__)
        if not os.path.exists(script):
            raise LinkToChefException(_("The Chef configuration script couldn't be found") + ': ' + script)

        cmd = '"%s" "%s" "%s" "%s" "%s" "%s"' % (script, url, pemurl, hostname, 'user', 'passwd')
        args = shlex.split(cmd)

        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        exit_code = os.waitpid(process.pid, 0)
        output = process.communicate()[0]

        if exit_code[1] != 0:
            raise LinkToChefException(_('Chef setup error') + ': ' + output)

    except Exception as e:
        raise e

    return True

def unlink_from_chef():

    try:

        script = os.path.join(__BIN_PATH__, __CHEF_CONF_SCRIPT__)
        if not os.path.exists(script):
            raise LinkToChefException("The file could not be found: " + script)

        cmd = '"%s" "--restore"' % (script,)
        args = shlex.split(cmd)

        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        exit_code = os.waitpid(process.pid, 0)
        output = process.communicate()[0]

        if exit_code[1] != 0:
            raise LinkToChefException(_('An error has ocurred unlinking from Chef') + ': ' + output)

    except Exception as e:
        raise e

    return True

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
            self._data['notes'] = ''
            self._data['pamldap'] = None
            self._data['chef'] = None

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
            self._data['uri'] = ''
            self._data['base'] = ''
            self._data['binddn'] = ''
            self._data['bindpw'] = ''

    def get_url(self):
        return self._data['uri'].encode('utf-8')

    def set_url(self, url):
        self._data['uri'] = url
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

class ChefConf():

    def __init__(self, json_conf=None):
        self._data = json_conf
        self._validate()

    def _validate(self):
        if self._data is None:
            self._data = {}
            self._data['chef_server_url'] = ''
            self._data['chef_validation_url'] = ''

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
