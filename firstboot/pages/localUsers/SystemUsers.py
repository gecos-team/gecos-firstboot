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


import os, shlex, subprocess, crypt

import gettext
from gettext import gettext as _
gettext.textdomain('firstboot')

def read_users(min_uid=1000):

    users = []

    f = open('/etc/passwd')
    try:
        for line in f:
            line = line.strip()
            tokens = line.split(':')
            if int(tokens[2]) >= min_uid:
                cmd = 'groups %s' % (tokens[0],)
                pid, exit_code, output = _run_command(cmd)
                groups = output.split(':')
                groups = groups[1].strip()

                user = {
                    'login': tokens[0],
                    'uid': tokens[2],
                    'gid': tokens[3],
                    'name': tokens[4].split(',')[0],
                    'home': tokens[5],
                    'shell': tokens[6],
                    'groups': groups
                }
                users.append(user)

    finally:
        f.close()

    return users

def update_user(user, update_passwd=False):
    # Modifies an user:
    #    -c Comment line, GECOS info.
    #    -G  A list of supplementary groups which the user is also a member of.
    #        If the user is currently a member of a group which is not listed,
    #        the user will be removed from the group.
    #    -p The encrypted password, as returned by crypt(3).

    groups = user['groups'].strip()
    groups = groups.split(' ')
    groups = filter(len, groups)
    groups = ','.join(groups)
    groups = groups.replace(' ', '')

    cmd = 'usermod -c "%s" -G %s %s' % (user['name'], groups, user['login'])
    pid, exit_code, output = _run_command(cmd)

    if exit_code == 0:
        if update_passwd == True:
            return set_password(user['login'], user['password'])
        else:
            return True

    else:
        raise SystemUserException(_('The user couldn\'t be updated. Please check the parameters.'))

def set_password(login, plain_passwd):
    # Modifies an user:
    #    -c Comment line, GECOS info.
    #    -G  A list of supplementary groups which the user is also a member of.
    #        If the user is currently a member of a group which is not listed,
    #        the user will be removed from the group.
    #    -p The encrypted password, as returned by crypt(3).

    passwd = crypt.crypt(plain_passwd, 'salt')
    cmd = 'usermod -p %s %s' % (passwd, login)
    pid, exit_code, output = _run_command(cmd)

    if exit_code == 0:
        return True

    else:
        raise SystemUserException(_('The password couldn\'t be changed.'))

def add_user(login, passwd):

    cmd = 'adduser --add_extra_groups --disabled-login --gecos "" %s' % (login,)
    pid, exit_code, output = _run_command(cmd)

    if exit_code == 0:
        return set_password(login, passwd);

    else:
        raise SystemUserException(_('The user couldn\'t be created. Please check the parameters.'))

def remove_user(login, remove_home=False):

    if remove_home == True:
        r = '--remove-home'
    else:
        r = ''

    cmd = 'deluser %s %s' % (r, login)
    pid, exit_code, output = _run_command(cmd)

    if exit_code == 0:
        return True

    elif exit_code == 1:
        raise SystemUserException(_('The user to delete was not a system account.'))

    elif exit_code == 2:
        raise SystemUserException(_('There is no such user.'))

    elif exit_code == 3:
        raise SystemUserException(_('There is no such group.'))

    elif exit_code == 4:
        raise SystemUserException(_('Internal error. No action was performed.'))

    elif exit_code == 5:
        raise SystemUserException(_('The group to delete is not empty.'))

    elif exit_code == 6:
        raise SystemUserException(_('The user does not belong to the specified group.'))

    elif exit_code == 7:
        raise SystemUserException(_('You cannot remove a user from its primary group.'))

    elif exit_code == 8:
        raise SystemUserException(_('The required perl-package \'perl modules\' is not installed. This package is required to perform the requested actions.'))

    elif exit_code == 9:
        raise SystemUserException(_('For removing the root account the parameter "--force" is required.'))

    else:
        raise SystemUserException(_('Unknown error, the user couldn\'t be removed for some reason.'))

def _run_command(cmd):
    args = shlex.split(cmd)
    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    exit_code = os.waitpid(process.pid, 0)
    output = process.communicate()[0]
    output = output.strip()

    #print cmd, exit_code
    #if exit_code[1] != 0:
    #    raise Exception(output)

    # PID, exit code, output
    return (exit_code[0], exit_code[1], output)

class SystemUserException(Exception):

    def __init__(self, msg):
        Exception.__init__(self, msg)
