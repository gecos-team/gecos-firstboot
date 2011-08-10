
import os
import gtk
import subprocess
import shlex
import urllib2
import json
import urlparse
import ldapconf
from firstboot_lib.Builder import Builder

import gettext
from gettext import gettext as _
gettext.textdomain('firstboot')

__REQUIRED__ = False

__TITLE__ = _('Link workstation to a server')

__CONFIG_FILE_VERSION__ = '1.0'

__URLOPEN_TIMEOUT__ = 5
__LDAP_BAK_FILE__ = '/etc/ldap.conf.firstboot.bak'

__STATUS_TEST_PASSED__ = 0
__STATUS_CONFIG_CHANGED__ = 1
__STATUS_CONNECTING__ = 2
__STATUS_ERROR__ = 3


def get_page():

    page = LinkToServerPage()
    return page

class LinkToServerPage(gtk.Window):
    __gtype_name__ = "LinkToServerPage"

    # To construct a new instance of this method, the following notable 
    # methods are called in this order:
    # __new__(cls)
    # __init__(self)
    # finish_initializing(self, builder)
    # __init__(self)
    #
    # For this reason, it's recommended you leave __init__ empty and put
    # your initialization code in finish_initializing

    def __new__(cls):
        """Special static method that's automatically called by Python when 
        constructing a new instance of this class.
        
        Returns a fully instantiated BaseFirstbootWindow object.
        """

        ui_filename = os.path.join(os.path.dirname(__file__), 'LinkToServerPage.glade')

        builder = Builder()
        builder.set_translation_domain('firstboot')
        builder.add_from_file(ui_filename)

        new_object = builder.get_object("ContainerWindow")
        new_object.finish_initializing(builder)

        return new_object

    def finish_initializing(self, builder):
        """Called while initializing this instance in __new__

        finish_initializing should be called after parsing the UI definition
        and creating a FirstbootWindow object with it in order to finish
        initializing the start of the new FirstbootWindow instance.
        """
        # Get a reference to the builder and set up the signals.
        self.builder = builder
        self.ui = builder.get_ui(self, True)

        self.lblDescription = builder.get_object('lblDescription')
        self.lblUrl = builder.get_object('lblUrl')
        self.txtUrl = builder.get_object('txtUrl')
        self.imgStatus = builder.get_object('imgStatus')
        self.lblStatus = builder.get_object('lblStatus')
        self.btnLinkToServer = builder.get_object('btnLinkToServer')
        self.btnTest = builder.get_object('btnTest')

        self.show_status()

        self.txtUrl.set_text('file:///home/ahernandez/dev/guadalinex/firstboot/gecos/src/firstboot/data/response.txt')

        container = builder.get_object('ContainerWindow')
        page = builder.get_object('LinkToServerPage')
        container.remove(page)
        self.page = page

        self.translate()

    def is_associated(self):
        return os.path.exists(__LDAP_BAK_FILE__)

    def translate(self):
        self.lblDescription.set_text(_('Write the server information'))
        self.btnTest.set_label(_('Test'))

        if self.is_associated():
            self.btnLinkToServer.set_label(_('Disassociate'))
        else:
            self.btnLinkToServer.set_label(_('Associate'))

    def get_widget(self):
        return self.page

    def on_txtUrl_changed(self, entry):
        url = entry.get_text()
        #parsed_url = urlparse.urlparse(url)

    def on_btnTest_Clicked(self, button):

        self.show_status()

        try:
            conf = self.get_conf_from_server()
            self.show_status(__STATUS_TEST_PASSED__)

        except LinkToServerException as e:
            self.show_status(__STATUS_ERROR__, e)

        except Exception as e:
            print e

    def on_btnLinkToServer_Clicked(self, button):

        self.show_status()

        if self.is_associated():
            self.dissasociate_from_server()

        else:
            self.associate_to_server()


    def associate_to_server(self):

        try:

            conf = self.get_conf_from_server()

            script = os.path.join(os.path.dirname(__file__), 'ldapconf.sh')
            cmd = 'gksu "%s %s %s %s"' % (script, str(conf['uri']), str(conf['port']), str(conf['base']))
            args = shlex.split(cmd)

            process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            exit_code = os.waitpid(process.pid, 0)
            output = process.communicate()[0]

            if exit_code[1] == 0:
                self.show_status(__STATUS_CONFIG_CHANGED__)
                self.btnLinkToServer.set_label(_('Disassociate'))

            else:
                self.show_status(__STATUS_ERROR__, Exception(_('An error occurred') + ': ' + output))

        except LinkToServerException as e:
            self.show_status(__STATUS_ERROR__, e)

        except Exception as e:
            self.show_status(__STATUS_ERROR__, Exception(_('An error occurred')))
            print e

    def dissasociate_from_server(self):

        try:

            script = os.path.join(os.path.dirname(__file__), 'ldapconf.sh')
            cmd = 'gksu "%s --restore"' % (script,)
            args = shlex.split(cmd)

            process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            exit_code = os.waitpid(process.pid, 0)
            output = process.communicate()[0]

            if exit_code[1] == 0:
                self.show_status(__STATUS_CONFIG_CHANGED__)
                self.btnLinkToServer.set_label(_('Associate'))

            else:
                self.show_status(__STATUS_ERROR__, Exception(_('An error occurred') + ': ' + output))

        except Exception as e:
            self.show_status(__STATUS_ERROR__, Exception(_('An error occurred')))
            print e

    def get_conf_from_server(self):

        self.show_status(__STATUS_CONNECTING__)

        try:

#            ldapconf.get_config_file(
#                self.txtUrl.get_text(),
#                self.on_get_conf_ok,
#                self.on_get_conf_error
#            )

            fp = urllib2.urlopen(self.txtUrl.get_text(), timeout=__URLOPEN_TIMEOUT__)
            #print fp.url(), fp.info()
            content = fp.read()
            conf = json.loads(content)

            if 'version' in conf and 'uri' in conf and 'port' in conf and 'base' in conf:
                version = conf['version']
                if version != __CONFIG_FILE_VERSION__:
                    raise Exception(_('Incorrect version of the configuration file.'))

                return conf

            raise ValueError()

        except urllib2.URLError as e:
            raise LinkToServerException(e.args[0])

        except ValueError as e:
            raise LinkToServerException(_('Configuration file is not valid.'))

        except Exception as e:
            raise Exception(e.args[0])

    def show_status(self, status=None, exception=None):

        icon_size = gtk.ICON_SIZE_BUTTON

        if status == None:
            self.imgStatus.set_visible(False)
            self.lblStatus.set_visible(False)

        elif status == __STATUS_TEST_PASSED__:
            self.imgStatus.set_from_stock(gtk.STOCK_APPLY, icon_size)
            self.imgStatus.set_visible(True)
            self.lblStatus.set_label(_('The configuration file is valid'))
            self.lblStatus.set_visible(True)

        elif status == __STATUS_CONFIG_CHANGED__:
            self.imgStatus.set_from_stock(gtk.STOCK_APPLY, icon_size)
            self.imgStatus.set_visible(True)
            self.lblStatus.set_label(_('The configuration was updated successfully'))
            self.lblStatus.set_visible(True)

        elif status == __STATUS_ERROR__:
            self.imgStatus.set_from_stock(gtk.STOCK_DIALOG_ERROR, icon_size)
            self.imgStatus.set_visible(True)
            self.lblStatus.set_label(str(exception.args[0]))
            self.lblStatus.set_visible(True)

        elif status == __STATUS_CONNECTING__:
            self.imgStatus.set_from_stock(gtk.STOCK_CONNECT, icon_size)
            self.imgStatus.set_visible(True)
            self.lblStatus.set_label(_('Trying to connect...'))
            self.lblStatus.set_visible(True)


class LinkToServerException(Exception):

    def __init__(self, msg):
        Exception.__init__(self, msg)
