
import os
import gtk
import urllib2
import json
import urlparse
from firstboot_lib.Builder import Builder

import gettext
from gettext import gettext as _
gettext.textdomain('firstboot')

__REQUIRED__ = False

__TITLE__ = _('Link workstation to a server')

__CONFIG_FILE_VERSION__ = '1.0'

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

        self.show_status()

        self.txtUrl.set_text('file:///home/ahernandez/dev/guadalinex/firstboot/gecos/src/firstboot/data/response.txt')

        container = builder.get_object('ContainerWindow')
        page = builder.get_object('LinkToServerPage')
        container.remove(page)
        self.page = page

    def translate(self):
        self.lblDescription.set_text(_('Write the server information'))
        self.btnTest.set_text(_('Test'))
        self.btnLinkToServer.set_text(_('Associate'))

    def get_widget(self):
        return self.page

    def on_txtUrl_changed(self, entry):
        url = entry.get_text()
        #parsed_url = urlparse.urlparse(url)

    def on_btnTest_Clicked(self, button):

        #self.show_status(gtk.STOCK_CONNECT)
        self.show_status()

        try:
            conf = self.get_conf_from_server()
            self.show_status(gtk.STOCK_APPLY)

        except Exception as e:
            self.show_status(gtk.STOCK_DIALOG_ERROR, e)

    def on_btnLinkToServer_Clicked(self, button):
        print button

    def get_conf_from_server(self):

        url = self.txtUrl.get_text()
        #parsed_url = urlparse.urlparse(url)
        # TODO: Algorithm for version controll

        try:
            fp = urllib2.urlopen(url, timeout=20)
            #print fp.url(), fp.info()
            content = fp.read()
            conf = json.loads(content)

            if 'version' in conf and 'host' in conf and 'port' in conf:
                version = conf['version']
                if version != __CONFIG_FILE_VERSION__:
                    raise Exception(_('Incorrect version of the configuration file.'))

                return conf

            raise ValueError()

        except urllib2.URLError as e:
            raise Exception(e.args[0])

        except ValueError as e:
            raise Exception(_('Configuration file is not valid.'))

        except Exception as e:
            raise Exception(e.args[0])

    def show_status(self, status=None, exception=None):

        icon_size = gtk.ICON_SIZE_BUTTON

        if status == None:
            self.imgStatus.set_visible(False)
            self.lblStatus.set_visible(False)

        elif status == gtk.STOCK_APPLY:
            self.imgStatus.set_from_stock(status, icon_size)
            self.imgStatus.set_visible(True)
            self.lblStatus.set_label(_('The configuration file is valid'))
            self.lblStatus.set_visible(True)

        elif status == gtk.STOCK_DIALOG_ERROR:
            self.imgStatus.set_from_stock(status, icon_size)
            self.imgStatus.set_visible(True)
            self.lblStatus.set_label(str(exception.args[0]))
            self.lblStatus.set_visible(True)

        elif status == gtk.STOCK_CONNECT:
            self.imgStatus.set_from_stock(status, icon_size)
            self.imgStatus.set_visible(True)
            self.lblStatus.set_label(_('Trying to connect...'))
            self.lblStatus.set_visible(True)

