from gi.repository import Gtk, GdkPixbuf
import os

from . import utils
from .album import Album


class Cover(Gtk.EventBox):

    '''The class structure for each album in the main browser'''

    def __init__(self, name, player, pixbuf):
        Gtk.EventBox.__init__(self)
        self.name = name
        self.player = player

        self.image = Gtk.Image()
        self.image.set_from_file(pixbuf)

        # self.set_album_art()
        self.add(self.image)

        # set up menu and its items
        self.menu = Gtk.Menu()
        menu_item_open = Gtk.MenuItem("Open")
        self.menu.append(menu_item_open)
        menu_item_open.connect("activate", self.album_detail)
        menu_item_open.show()
        menu_item_queue = Gtk.MenuItem("Queue")
        self.menu.append(menu_item_queue)
        menu_item_queue.connect("activate", self.queue)
        menu_item_queue.show()
        menu_item_play = Gtk.MenuItem("Play")
        self.menu.append(menu_item_play)
        menu_item_play.connect("activate", self.play)
        menu_item_play.show()
        menu_item_cover = Gtk.MenuItem("Get Cover")
        self.menu.append(menu_item_cover)
        menu_item_cover.connect("activate", self.fetch_album_art)
        menu_item_cover.show()

        self.connect("button-press-event", self.on_button_press)

        self.set_tooltip_text(self.name)

        self.show_all()

    def set_album_art(self):
        path = os.path.join(self.player.MUSIC_DIR, self.name, 'cover.jpg')
        if not os.path.exists(path):
            path = '/usr/share/ricochet/default_album.png'
        size = int(self.player.settings['grid_icon_size'])
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(path, size, size)
        self.image.set_from_pixbuf(pixbuf)
        self.image.show()

    def queue(self, *args, **kwargs):
        # TODO create file list from name on this end
        self.player.queue(files=self.name)

    def play(self, *args, **kwargs):
        # TODO create file list from name on this end
        self.player.play(files=self.name)

    def album_detail(self, widget):
        '''launch the detailed album view'''
        return Album(self.name, self.player)

    def fetch_album_art(self, widget):
        code = utils.fetch_album_art(self.name, self.player.MUSIC_DIR)
        if code == 0:
            self.set_album_art()

    def on_button_press(self, widget, event):
        '''Callback function for clicking on album'''
        if event.button == 1:
            self.album_detail(self)
        elif event.button == 2:
            self.player.play(files=self.name)
        elif event.button == 3:
            self.menu.popup(
                None, None, None, self.name, event.button, event.time)


class Browser(Gtk.ScrolledWindow):

    '''The main window displaying all covers'''

    def __init__(self, player):
        Gtk.ScrolledWindow.__init__(self)
        self.set_border_width(0)
        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self.albums = []
        self.player = player

        self.search_bar = Gtk.SearchBar()
        self.entry = Gtk.Entry()
        self.query = self.entry.get_buffer()
        self.query.connect("inserted-text", self.search_changed)
        self.query.connect("deleted-text", self.search_changed)
        self.search_bar.add(self.entry)

        self.flowbox = Gtk.FlowBox()
        self.flowbox.set_valign(Gtk.Align.START)
        self.flowbox.set_max_children_per_line(20)
        self.flowbox.set_selection_mode(Gtk.SelectionMode.BROWSE)
        self.flowbox.connect("key-press-event", self.on_key_press)
        # self.flowbox.connect(
        #    "selected-children-changed", self.on_selection_changed)
        self.flowbox.set_filter_func(self.filter_func)

        vbox = Gtk.Box(orientation=1, spacing=0)
        self.add(vbox)
        vbox.pack_start(self.search_bar, False, False, 0)
        vbox.pack_start(self.flowbox, False, False, 0)

        self.show_all()

    def filter_func(self, child):
        return (self.entry.get_text().upper()
                in self.albums[child.get_index()].upper())

    def search_changed(self, *args):
        self.flowbox.invalidate_filter()

    def add_album(self, album, pixbuf):
        self.albums.append(album)
        cover = Cover(album, self.player, pixbuf)
        self.flowbox.add(cover)

    def on_selection_changed(self, box):
        child = box.get_selected_children()[0]
        print(self.albums[child.get_index()])

    def on_key_press(self, flowbox, event):
        '''handle keyboard controls'''
        child = flowbox.get_selected_children()[0]
        index = child.get_index()
        if event.hardware_keycode == 36 or event.hardware_keycode == 32:
            Album(self.albums[index], self.player)
        elif event.hardware_keycode == 33:
            self.player.play(files=self.albums[index])
        elif event.hardware_keycode == 24:
            self.player.queue(files=self.albums[index])
        elif event.hardware_keycode == 43:
            event.hardware_keycode = 113
            self.event(event)
        elif event.hardware_keycode == 44:
            event.hardware_keycode = 116
            self.event(event)
        elif event.hardware_keycode == 45:
            event.hardware_keycode = 111
            self.event(event)
        elif event.hardware_keycode == 46:
            event.hardware_keycode = 114
            self.event(event)
        elif event.hardware_keycode == 61:
            self.search_bar.set_search_mode(True)