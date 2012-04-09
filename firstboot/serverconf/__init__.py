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

from gi.repository import Gtk
from firstboot_lib import firstbootconfig
from ServerConf import ServerConf
from gi.repository import Gtk
import gettext
from gettext import gettext as _
gettext.textdomain('firstboot')


__URLOPEN_TIMEOUT__ = 15
__JSON_CACHE__ = '/tmp/json_cached'
__BIN_PATH__ = firstbootconfig.get_bin_path()
__LDAP_CONF_SCRIPT__ = 'firstboot-ldapconf.sh'
__CHEF_CONF_SCRIPT__ = 'firstboot-chefconf.sh'
__AD_CONF_SCRIPT__ = 'firstboot-adconf.sh'

CREDENTIAL_CACHED = {}


def _install_opener(url, user, password, url_based_auth=True):
    if not url_based_auth:
        # Domain based auth
        parsed_url = list(urlparse.urlparse(url))
        top_level_url = '%s://%s' % (parsed_url[0], parsed_url[1])

    else:
        # URL based auth
        top_level_url = url

    pwmgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    pwmgr.add_password(None, top_level_url, user, password)
    handler = urllib2.HTTPBasicAuthHandler(pwmgr)
    opener = urllib2.build_opener(handler)
    opener.open(url)
    urllib2.install_opener(opener)


def parse_url(url):
    parsed_url = list(urlparse.urlparse(url))
    if parsed_url[0] in ('http', 'https'):
        query = urlparse.parse_qsl(parsed_url[4])
        query.append(('v', ServerConf.VERSION))
        query = urllib.urlencode(query)
        parsed_url[4] = query
    url = urlparse.urlunparse(parsed_url)
    return url


def validate_credentials(url):
    global CREDENTIAL_CACHED
    url_parsed = urlparse.urlparse(url)
    user = ''
    password = ''
    hostname = ''
    if url_parsed.scheme == '':
        if url_parsed.path == '':
            hostname = url_parsed.hostname
        else:
            hostname = url_parsed.path
    else:
        hostname = url_parsed.hostname

    if hostname in CREDENTIAL_CACHED:
        validate_credentials = False
        credentials = CREDENTIAL_CACHED[hostname]
        for cred in credentials:
            try:
                _install_opener(url, cred[0], cred[1])
                validate = True
                user, password = cred[0], cred[1]
                break
            except urllib2.URLError as e:
                print e
                if hasattr(e, 'code') and e.code == 401 and e.msg == 'basic auth failed':
                    continue
        if not validate:
            user, password = auth_dialog(_('Authentication Required'),
                    _('You need to enter your credentials to access the requested resource.'))
            _install_opener(url, user, password)
            credentials = CREDENTIAL_CACHED[hostname]
            credentials.append([user, password])
    else:
        user, password = auth_dialog(_('Authentication Required'),
                _('You need to enter your credentials to access the requested resource.'))
        _install_opener(url, user, password)
        CREDENTIAL_CACHED[hostname] = [[user, password]]
    return user, password

def json_is_cached():
    return os.path.exists(__JSON_CACHE__)

def clean_json_cached():
    return os.remove(__JSON_CACHE__)

def get_server_conf(url):

    is_cached = json_is_cached()

    try:
        if is_cached:
            fp = open(__JSON_CACHE__, 'r')

        else:
            try:
                url = parse_url(url)
                user, password = validate_credentials(url)
                fp = urllib2.urlopen(url, timeout=__URLOPEN_TIMEOUT__)

            except urllib2.URLError as e:
                if hasattr(e, 'code') and e.code == 401:
                    user, password = validate_credentials(url)
                    fp = urllib2.urlopen(url, timeout=__URLOPEN_TIMEOUT__)

                else:
                    raise e

            fp_cached = open(__JSON_CACHE__, 'w')
            for line in fp:
                fp_cached.write(line)

            fp_cached.close()
            fp.close()
            fp = open(__JSON_CACHE__, 'r')

        content = fp.read()
        fp.close()
        conf = json.loads(content)

        server_conf = ServerConf()
        server_conf.load_data(conf)
        return server_conf

    except urllib2.URLError as e:
        raise ServerConfException(e)

    except ValueError as e:
        raise ServerConfException(_('Configuration file is not valid.'))


def get_chef_pem(chef_conf):
    global CREDENTIAL_CACHED
    url = chef_conf.get_pem_url()
    user = ''
    password = ''
    try:
        try:
            url = parse_url(url)
            user, password = validate_credentials(url)
            chef_conf.set_user(user)
            chef_conf.set_password(password)
            fp = urllib2.urlopen(url, timeout=__URLOPEN_TIMEOUT__)

        except urllib2.URLError as e:
            if hasattr(e, 'code') and e.code == 401:
                user, password = validate_credentials(url)
                fp = urllib2.urlopen(url, timeout=__URLOPEN_TIMEOUT__)

                chef_conf.set_user(user)
                chef_conf.set_password(password)

            else:
                raise e

        content = fp.read()

        (fd, filepath) = tempfile.mkstemp(dir='/tmp')  # [suffix=''[, prefix='tmp'[, dir=None[, text=False]]]])
        fp = os.fdopen(fd, "w+b")
        if fp:
            fp.write(content)
            fp.close()

        return filepath

    except urllib2.URLError as e:
        raise ServerConfException(e)


def get_chef_hostnames(chef_conf):

    chef_url = chef_conf.get_url()
    pem_file_path = get_chef_pem(chef_conf)

    cmd = 'knife node list -u chef-validator -k %s -s %s' % (pem_file_path, chef_url)
    args = shlex.split(cmd)

    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    exit_code = os.waitpid(process.pid, 0)
    output = process.communicate()[0]
    output = output.strip()

    names = []
    if exit_code[1] != 0:
        raise ServerConfException(_('Couldn\'t retrieve the host names list') + ': ' + output)

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


def ad_is_configured():
    try:
        script = os.path.join(__BIN_PATH__, __AD_CONF_SCRIPT__)
        if not os.path.exists(script):
            raise LinkToADException(_("The Active Directory configuration script couldn't be found") + ': ' + script)
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
            raise LinkToADException(_('Active Directory setup error') + ': ' + output)

    except Exception as e:
        raise e


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
                link_chef=False, unlink_chef=False, link_ad=False, unlink_ad=False):

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

    if unlink_ad == True:
        try:
            ret = unlink_from_ad()
            if ret == True:
                messages.append({'type': 'info', 'message': _('Workstation has been unlinked from the Active Directory.')})
            else:
                messages += ret
        except Exception as e:
            messages.append({'type': 'error', 'message': str(e)})

    elif link_ad == True:
        try:
            ret = link_to_ad(server_conf.get_ad_conf())
            if ret == True:
                messages.append({'type': 'info', 'message': _('The Active Directory has been configured successfully.')})
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
    basedngroup = ldap_conf.get_basedngroup()
    binddn = ldap_conf.get_binddn()
    password = ldap_conf.get_password()
    anonymous = ldap_conf.get_anonymous()
    if anonymous == True:
        anonymous = 1
    else:
        anonymous = 0
    errors = []

    if len(url) == 0:
        errors.append({'type': 'error', 'message': _('The LDAP URL cannot be empty.')})

    if len(basedn) == 0:
        errors.append({'type': 'error', 'message': _('The LDAP BaseDN cannot be empty.')})

    if len(errors) > 0:
        return errors

    try:

        script = os.path.join(__BIN_PATH__, __LDAP_CONF_SCRIPT__)
        if not os.path.exists(script):
            raise LinkToLDAPException(_("The LDAP configuration script couldn't be found") + ': ' + script)

        cmd = '"%s" "%s" "%s" "%s" "%s" "%s" "%s"' % (script, url, basedn, basedngroup, anonymous, binddn, password)
        args = shlex.split(cmd)

        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        exit_code = os.waitpid(process.pid, 0)
        output = process.communicate()[0]

        if exit_code[1] != 0:
            raise LinkToLDAPException(_('LDAP setup error') + ': ' + output)

    except Exception as e:
        raise e

    return True


def link_to_ad(ad_conf):

    fqdn = ad_conf.get_fqdn()
    dns_domain = ad_conf.get_dns_domain()
    user = ad_conf.get_user()
    passwd = ad_conf.get_passwd()
    errors = []

    if len(fqdn) == 0:
        errors.append({'type': 'error', 'message': _('The Active Directory URL cannot be empty.')})

    if len(dns_domain) == 0:
        errors.append({'type': 'error', 'message': _('The DNS Domain cannot be empty.')})
    if len(user) == 0:
        errors.append({'type': 'error', 'message': _('The administrator user cannot be empty.')})
    if len(passwd) == 0:
        errors.append({'type': 'error', 'message': _('The administrator password cannot be empty.')})

    if len(errors) > 0:
        return errors

    try:

        script = os.path.join(__BIN_PATH__, __AD_CONF_SCRIPT__)
        if not os.path.exists(script):
            raise LinkToADException(_("The Active Directory configuration script couldn't be found") + ': ' + script)

        cmd = '"%s" "%s" "%s" "%s" "%s"' % (script, fqdn, dns_domain, user, passwd)
        args = shlex.split(cmd)

        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        exit_code = os.waitpid(process.pid, 0)
        output = process.communicate()[0]

        if exit_code[1] != 0:
            raise LinkToADException(_('Active Directory setup error') + ': ' + output)

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


def unlink_from_ad():

    try:

        script = os.path.join(__BIN_PATH__, __AD_CONF_SCRIPT__)
        if not os.path.exists(script):
            raise LinkToADException("The file could not be found: " + script)

        cmd = '"%s" "--restore"' % (script,)
        args = shlex.split(cmd)

        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        exit_code = os.waitpid(process.pid, 0)
        output = process.communicate()[0]

        if exit_code[1] != 0:
            raise LinkToADException(_('An error has ocurred unlinking from Active Directory') + ': ' + output)

    except Exception as e:
        raise e

    return True


def link_to_chef(chef_conf):

    url = chef_conf.get_url()
    pemurl = chef_conf.get_pem_url()
    role = chef_conf.get_default_role()
    hostname = chef_conf.get_hostname()
    user = chef_conf.get_user()
    password = chef_conf.get_password()
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

        cmd = '"%s" "%s" "%s" "%s" "%s" "%s" "%s"' % (script, url, pemurl, hostname, user, password, role)
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


def auth_dialog(title, text):
    dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.INFO,
                                   Gtk.ButtonsType.OK_CANCEL)
    dialog.set_title(title)
    dialog.set_position(Gtk.WindowPosition.CENTER)
    dialog.set_default_response(Gtk.ResponseType.OK)
    dialog.set_icon_name('dialog-password')
    dialog.set_markup(text)

    hboxuser = Gtk.HBox()
    lbluser = Gtk.Label(_('user'))
    lbluser.set_visible(True)
    hboxuser.pack_start(lbluser, False, False, False)
    user = Gtk.Entry()
    user.set_activates_default(True)
    user.show()
    hboxuser.pack_end(user, False, False, False)
    hboxuser.show()

    hboxpwd = Gtk.HBox()
    lblpwd = Gtk.Label(_('password'))
    lblpwd.set_visible(True)
    hboxpwd.pack_start(lblpwd, False, False, False)
    pwd = Gtk.Entry()
    pwd.set_activates_default(True)
    pwd.set_visibility(False)
    pwd.show()
    hboxpwd.pack_end(pwd, False, False, False)
    hboxpwd.show()

    dialog.get_message_area().pack_start(hboxuser, False, False, False)
    dialog.get_message_area().pack_end(hboxpwd, False, False, False)
    result = dialog.run()

    retval = [None, None]
    if result == Gtk.ResponseType.OK:
        retval = [user.get_text(), pwd.get_text()]

    dialog.destroy()
    return retval


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


class LinkToADException(Exception):
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
