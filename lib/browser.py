from gi.repository import Gtk, Gdk, GdkPixbuf
import os

from . import settings
from . import albumart


music = settings.settings['music_dir']


class Cover(Gtk.EventBox):

    '''The class structure for each album in the main browser'''

    def __init__(self, name, player):
        Gtk.EventBox.__init__(self)
        self.name = name
        self.player = player

        self.image = Gtk.Image()
        self.set_album_art()
        self.add(self.image)

        # set up menu and its items
        self.menu = Gtk.Menu()
        menu_item_open = Gtk.MenuItem("Open")
        self.menu.append(menu_item_open)
        menu_item_open.connect("activate", self.album_detail)
        menu_item_open.show()
        menu_item_queue = Gtk.MenuItem("Queue")
        self.menu.append(menu_item_queue)
        menu_item_queue.connect("activate", self.player.queue, self.name)
        menu_item_queue.show()
        menu_item_play = Gtk.MenuItem("Play")
        self.menu.append(menu_item_play)
        menu_item_play.connect("activate", self.player.play, self.name)
        menu_item_play.show()
        menu_item_cover = Gtk.MenuItem("Get Cover")
        self.menu.append(menu_item_cover)
        menu_item_cover.connect("activate", self.fetch_album_art)
        menu_item_cover.show()

        self.connect("button-press-event", self.on_button_press)

        self.set_tooltip_text(self.name)

        self.show_all()

    def set_album_art(self):
        path = ''.join([music, self.name, '/cover.jpg'])
        if not os.path.exists(path):
            path = '/opt/ricochet/images/default_album.jpg'
        size = int(settings.settings['grid_icon_size'])
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(path, size, size)
        self.image.set_from_pixbuf(pixbuf)
        self.image.show()

    def album_detail(self, widget):
        '''launch the detailed album view'''
        album = Album(self.name, self.player)

    def fetch_album_art(self, widget):
        code = albumart.fetch_album_art(self.name)
        if code == 0:
            self.set_album_art()

    def on_button_press(self, widget, event):
        '''Callback function for clicking on album'''
        if event.button == 1:
            self.album_detail(self)
        elif event.button == 2:
            self.player.play(None, self.name)
        elif event.button == 3:
            self.menu.popup(
                None, None, None, self.name, event.button, event.time)


class Browser(Gtk.ScrolledWindow):

    '''The main window displaying all covers'''

    def __init__(self, albums, player):
        Gtk.ScrolledWindow.__init__(self)
        self.set_border_width(0)
        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self.albums = albums
        self.player = player

        # flowbox to hold the albums for dynamic window resizing and row
        # organising
        flowbox = Gtk.FlowBox()
        flowbox.set_valign(Gtk.Align.START)
        flowbox.set_max_children_per_line(20)
        # allows selection of items with keyboard
        flowbox.set_selection_mode(Gtk.SelectionMode.BROWSE)
        flowbox.connect("key-press-event", self.on_key_press)
        self.add(flowbox)

        # a loop to create a Cover class for each album found
        for album in albums:
            temp = Cover(album, self.player)
            flowbox.add(temp)

        self.show_all()

    def on_key_press(self, widget, event):
        '''handle keyboard controls'''
        children = widget.get_selected_children()
        for child in children:
            index = child.get_index()
            if event.hardware_keycode == 36 or event.hardware_keycode == 32:
                Album(self.albums[index], self.player)
            elif event.hardware_keycode == 33:
                self.player.play(None, self.albums[index])
            elif event.hardware_keycode == 24:
                self.player.queue(None, self.albums[index])
            elif event.hardware_keycode == 65:
                self.player.toggle(None)


class Album(Gtk.Window):

    '''The class for the detailed album view'''

    def __init__(self, name, player):
        Gtk.Window.__init__(self, title=name)
        self.set_default_size(256, 512)

        self.name = name
        self.player = player

        path = ''.join([music, self.name, '/cover.jpg'])
        if not os.path.exists(path):
            path = '/opt/ricochet/images/default_album.jpg'
        size = int(settings.settings['detail_icon_size'])
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(path, size, size)
        image = Gtk.Image()
        image.set_from_pixbuf(pixbuf)

        vbox = Gtk.Box(orientation=1, spacing=0)
        self.add(vbox)
        # make sure image doesn't expand or fill but the scroll window
        # does.
        vbox.pack_start(image, False, False, 0)

        discs = []
        for item in os.listdir(music + name):
            if item.startswith('.'):
                continue
            if os.path.isdir(os.path.join(music, name, item)):
                discs.append(os.path.join(name, item))
        if discs == []:
            discs.append(name)

        discs.sort()
        tabbed = Gtk.Notebook()
        tabbed.set_scrollable(True)
        for disc in discs:

            # scrolled area for the songs
            scroll = Gtk.ScrolledWindow()
            scroll.set_border_width(0)
            scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

            # set up the song treeview
            liststore = Gtk.ListStore(str)
            songs = os.listdir(music + disc)
            songs.sort()
            for song in songs:
                if song.endswith(("mp3", "mpc", "ogg", "wma", "m4a", "mp4", "flac")):
                    liststore.append([song])
            treeview = Gtk.TreeView(model=liststore)
            renderer = Gtk.CellRendererText()
            # option is PangoEllipsizeMode numbered 0,1,2,3 for none, start,
            # middle, end (True becomes 1=start)
            renderer.set_property("ellipsize", 3)
            column = Gtk.TreeViewColumn("Track", renderer, text=0)
            treeview.append_column(column)
            treeview.set_property("headers-visible", False)
            # disable search grabbing keyboard input
            treeview.set_enable_search(False)

            # allow selection of multiple rows. get_selection won't work
            # now so use get_selected_rows instead (on selection object)
            Gtk.TreeSelection.set_mode(
                treeview.get_selection(), Gtk.SelectionMode.MULTIPLE)

            treeview.connect("button-press-event", self.on_button_press, disc)
            treeview.connect("key-press-event", self.on_key_press, disc)

            scroll.add(treeview)
            tabbed.append_page(scroll, None)
            tabbed.set_tab_label_text(scroll, os.path.basename(disc))

        vbox.pack_start(tabbed, True, True, 0)

        self.show_all()

    def on_button_press(self, widget, event, disc):
        # print(event.type)
        select = widget.get_selection()
        model, treeiter = select.get_selected_rows()
        if event.button == 3:
            for path in treeiter:
                self.player.queue(None, disc + '/' + model[path][0])
        elif event.button == 2:
            self.player.play(None, disc + '/' + model[treeiter][0])
            for i in range(1, len(treeiter)):
                self.player.queue(None, disc + '/' + model[i][0])
        elif event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS:
            self.player.play(None, disc + '/' + model[treeiter][0])

    # TODO: Could also make the backend capable of handling lists ^^

    def on_key_press(self, widget, event, disc):
        # print(event.hardware_keycode)
        select = widget.get_selection()
        model, treeiter = select.get_selected_rows()

        if event.hardware_keycode == 36 or event.hardware_keycode == 33:
            self.player.play(None, disc + '/' + model[treeiter][0])
            for i in range(1, len(treeiter)):
                self.player.queue(None, disc + '/' + model[i][0])
        elif event.hardware_keycode == 24:
            for path in treeiter:
                self.player.queue(None, disc + '/' + model[path][0])
        elif event.hardware_keycode == 65:
            self.player.toggle(None)
