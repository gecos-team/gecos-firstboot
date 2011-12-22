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


import re


def is_empty(value):
    ret = not(len(value) > 0)
    #print '> %s :: %s' % (ret, value)
    return ret


def is_qname(value):
    m = re.search('^[a-zA-Z][\w-]+$', value)
    #print '> %s :: %s' % (m != None, value)
    return m != None


def is_url(value):
    m = re.search('^(http|https|ftp|ftps|file|ldap)://(.+)', value)
    #print '> %s :: %s' % (m != None, value)
    return m != None


def is_password(value):
    """ Maybe not necesary """
    return True
