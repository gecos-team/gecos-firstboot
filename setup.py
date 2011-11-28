#!/usr/bin/env python
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


###################### DO NOT TOUCH THIS (HEAD TO THE SECOND PART) ######################

import os
import sys
import glob

try:
    import DistUtilsExtra.auto
    from distutils.core import setup, Command
    from DistUtilsExtra.command import *
except ImportError:
    print >> sys.stderr, 'To build firstboot you need https://launchpad.net/python-distutils-extra'
    sys.exit(1)
assert DistUtilsExtra.auto.__version__ >= '2.18', 'needs DistUtilsExtra.auto >= 2.18'

def update_config(values={}):

    oldvalues = {}
    try:
        fin = file('firstboot_lib/firstbootconfig.py', 'r')
        fout = file(fin.name + '.new', 'w')

        for line in fin:
            fields = line.split(' = ') # Separate variable from value
            if fields[0] in values:
                oldvalues[fields[0]] = fields[1].strip()
                line = "%s = %s\n" % (fields[0], values[fields[0]])
            fout.write(line)

        fout.flush()
        fout.close()
        fin.close()
        os.rename(fout.name, fin.name)
    except (OSError, IOError), e:
        print ("ERROR: Can't find firstboot_lib/firstbootconfig.py")
        sys.exit(1)
    return oldvalues


def update_desktop_file(datadir):

    try:
        fin = file('firstboot.desktop.in', 'r')
        fout = file(fin.name + '.new', 'w')

        for line in fin:
            if 'Icon=' in line:
                line = "Icon=%s\n" % (datadir + 'media/wizard1.png')
            fout.write(line)
        fout.flush()
        fout.close()
        fin.close()
        os.rename(fout.name, fin.name)
    except (OSError, IOError), e:
        print ("ERROR: Can't find firstboot.desktop.in")
        sys.exit(1)


def copy_pages(pages_path):
    pass


class InstallAndUpdateDataDirectory(DistUtilsExtra.auto.install_auto):
    def run(self):
        values = {'__firstboot_data_directory__': "'%s'" % (self.prefix + '/local/share/firstboot/'),
                  '__version__': "'%s'" % self.distribution.get_version()}
        previous_values = update_config(values)
        update_desktop_file(self.prefix + '/local/share/firstboot/')
        DistUtilsExtra.auto.install_auto.run(self)
        update_config(previous_values)


class Clean(Command):
    description = "custom clean command that forcefully removes dist/build directories and update data directory"
    user_options = []
    def initialize_options(self):
        self.cwd = None
    def finalize_options(self):
        self.cwd = os.getcwd()
    def run(self):
        assert os.getcwd() == self.cwd, 'Must be in package root: %s' % self.cwd
        os.system('rm -rf ./build ./dist')
        update_data_path(prefix, oldvalue)


##################################################################################
###################### YOU SHOULD MODIFY ONLY WHAT IS BELOW ######################
##################################################################################

DistUtilsExtra.auto.setup(
    name='firstboot',
    version='0.3.1',
    license='GPL-2',
    author='Antonio Hernández',
    author_email='ahernandez@emergya.com',
    description='First start assistant for helping to connect a GECOS \
workstation to different services',
    url='https://github.com/ahdiaz/gecos-firstboot',

    keywords=['python', 'gnome'],

    packages=[
        'firstboot',
        'firstboot_lib',
        'firstboot.pages',
        'firstboot.pages.installSoftware',
        'firstboot.pages.linkToServer',
        'firstboot.pages.localUsers',
        'firstboot.pages.network',
        'firstboot.pages.pcLabel',
    ],

    package_dir={
        'firstboot': 'firstboot',
        'firstboot_lib': 'firstboot_lib',
        'firstboot.pages': 'firstboot/pages',
        'firstboot.pages.installSoftware': 'firstboot/pages/installSoftware',
        'firstboot.pages.linkToServer': 'firstboot/pages/linkToServer',
        'firstboot.pages.localUsers': 'firstboot/pages/localUsers',
        'firstboot.pages.network': 'firstboot/pages/network',
        'firstboot.pages.pcLabel': 'firstboot/pages/pcLabel',
        },

    scripts=[
        'bin/firstboot',
        'bin/firstboot-launcher',
        'bin/firstboot-ldapconf.sh',
        'bin/firstboot-chefconf.sh'
        'bin/firstboot-adconf.sh'
    ],

    data_files=[
       ('bin', ['bin/firstboot', 'bin/firstboot-launcher',
            'bin/firstboot-ldapconf.sh', 'bin/firstboot-chefconf.sh',
	    'bin/firstboot-adconf.sh']),
       ('share/firstboot/media', glob.glob('data/media/*')),
       ('share/firstboot/ui', glob.glob('data/ui/*')),
    ],

    cmdclass={
        'install': InstallAndUpdateDataDirectory,
        "build" : build_extra.build_extra,
        "build_i18n" :  build_i18n.build_i18n,
        "clean": [clean_i18n.clean_i18n, Clean],
    }
)
