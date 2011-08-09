
import os
import gtk
from firstboot_lib.Builder import Builder

import gettext
from gettext import gettext as _
gettext.textdomain('firstboot')

__REQUIRED__ = False

__TITLE__ = _('Create local users')

def get_page():

    page = LocalUsersPage()
    return page

class LocalUsersPage(gtk.Window):
    __gtype_name__ = "LocalUsersPage"

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

        ui_filename = os.path.join(os.path.dirname(__file__), 'LocalUsersPage.glade')

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

        container = builder.get_object('ContainerWindow')
        page = builder.get_object('LocalUsersPage')
        container.remove(page)
        self.page = page

        self.btnLocalUsers = builder.get_object('btnLocalUsers')
        self.btnLocalUsers.set_label(_('Create local users'))

    def get_widget(self):
        return self.page

    def on_btnLocalUsers_Clicked(self, button):
        cmd = 'gnome-control-center'
        param = 'user-accounts'
        os.spawnlp(os.P_NOWAIT, cmd, cmd, param)
