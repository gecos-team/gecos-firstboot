
import os
import gtk
import gobject
from firstboot_lib.Builder import Builder

import gettext
from gettext import gettext as _
gettext.textdomain('firstboot')

from interface import localifs, internet_on

__REQUIRED__ = True

__TITLE__ = _('Configure the network')

def get_page():

    page = NetworkPage()
    return page

class NetworkPage(gtk.Window):
    __gtype_name__ = "NetworkPage"

    __gsignals__ = {
        'link-status': (gobject.SIGNAL_ACTION, gobject.TYPE_NONE, (gobject.TYPE_BOOLEAN,))
    }

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

        ui_filename = os.path.join(os.path.dirname(__file__), 'NetworkPage.glade')

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
        page = builder.get_object('NetworkPage')
        container.remove(page)
        self.page = page

        self.btnNetworkDialog = builder.get_object('btnNetworkDialog')

        self.lblDescription = builder.get_object('lblDescription')
        self.treeviewInterfaces = builder.get_object('treeviewInterfaces')

        self.timer_ret = True

        self.translate()
        self.init_treeviewInterfaces()

    def translate(self):
        self.btnNetworkDialog.set_label(_('Configure the network'))
        self.lblDescription.set_text(_('You need to be connected to the network for linking this workstation to a GECOS server and for installing software.'))

    def load_page(self, assistant):
        self.timer_ret = True
        gobject.timeout_add_seconds(1, self.load_treeviewInterfaces)

    def unload_page(self):
        self.timer_ret = False

    def get_widget(self):
        return self.page

    def on_btnNetworkDialog_Clicked(self, button):
        cmd = 'nm-connection-editor'
        os.spawnlp(os.P_NOWAIT, cmd, cmd)

    def show_ifs_information(self):

        def _format_text(info):
            return '<b>%s</b>:\t%s\n' % info

        text = ''
        ifs = localifs()

        for _if in ifs:
            if _if[0] != 'lo':
                text += _format_text(_if)

        print text
        self.lblDescription.set_markup(text)

        connected = internet_on()
        print connected

    def init_treeviewInterfaces(self):

        tvcolumn = gtk.TreeViewColumn(_('Name'))
        cell = gtk.CellRendererText()
        tvcolumn.pack_start(cell, True)
        tvcolumn.set_cell_data_func(cell, self._render_column_name)
        self.treeviewInterfaces.append_column(tvcolumn)

        tvcolumn = gtk.TreeViewColumn(_('IP'))
        cell = gtk.CellRendererText()
        tvcolumn.pack_start(cell, True)
        tvcolumn.set_cell_data_func(cell, self._render_column_ip)
        self.treeviewInterfaces.append_column(tvcolumn)

        selection = self.treeviewInterfaces.get_selection()
        selection.set_mode(gtk.SELECTION_NONE)

        self.load_treeviewInterfaces()

    def load_treeviewInterfaces(self):

        n_ifaces = 0

        store = self.treeviewInterfaces.get_model()
        store.clear()

        ifs = localifs()
        #print ifs

        for _if in ifs:
            store.append([_if[0], _if[1]])
            if _if[0] != 'lo' and len(_if[1]) > 0:
                n_ifaces += 1

        self.emit('link-status', n_ifaces > 0)
        self.treeviewInterfaces.set_model(store)

        return self.timer_ret

    def _render_column_name(self, column, cell, model, iter):

        value = model.get_value(iter, 0)
        text = '<b>%s</b>' % (value,)
        cell.set_property('markup', text)
        cell.set_property('width', 80)

    def _render_column_ip(self, column, cell, model, iter):

        value = model.get_value(iter, 1)
        cell.set_property('text', value)

