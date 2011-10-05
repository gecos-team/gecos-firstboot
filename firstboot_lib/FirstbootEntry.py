
import os
import types
import firstbootconfig
import firstboot.pages
from xdg.IniFile import *

class FirstbootEntry(IniFile):

    default_group = 'Firstboot Entry'

    def __init__(self):

        self.content = dict()

        self.config_path = os.path.join(os.getenv('HOME'), '.config/firstboot')
        self.config_file = os.path.join(self.config_path, 'firstboot.conf')

        if not os.path.exists(self.config_path):
            os.makedirs(self.config_path)

        if not os.path.exists(self.config_file):
            self._create_config_file()

        IniFile.parse(self, self.config_file, [self.default_group])

    def _create_config_file(self):

        fd = open(self.config_file, 'w')
        if fd != None:
            fd.write('[Firstboot Entry]\n')
            fd.write('firststart=0\n')
            fd.write('\n')
            fd.write('[LinkToServer]\n')
            fd.write('url=\n')
            fd.write('\n')
            fd.close()

    def get_firststart(self):
        fs = self.get('firststart').strip()
        fs = bool(int(fs))
        return fs

    def set_firststart(self, value):
        self.set('firststart', value)
        self.write()

    def get_url(self):
        return self.get('url', group='LinkToServer')

    def set_url(self, value):
        self.set('url', value, group='LinkToServer')
        self.write()

#===============================================================================
#    def new(self, filename):
#        self.content = dict()
#        self.addGroup(self.default_group)
#        self.filename = os.path.join(utils.get_actions_path(), filename)
#===============================================================================
