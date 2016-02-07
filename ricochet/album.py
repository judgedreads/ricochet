from gi.repository import Gtk, Gdk, GdkPixbuf
import os
from . import utils


class Album(Gtk.Window):

    '''The class for the detailed album view'''

    def __init__(self, name, player):
        Gtk.Window.__init__(self, title=name)
        size = player.settings['detail_icon_size']
        # self.set_default_size(size, 2 * size)

        self.name = name
        self.player = player

        path = os.path.join(self.player.MUSIC_DIR, self.name, 'cover.jpg')
        if not os.path.exists(path):
            path = '/usr/share/ricochet/default_album.png'
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(path, size, size)
        image = Gtk.Image()
        image.set_from_pixbuf(pixbuf)

        hbox = Gtk.Box(orientation=0, spacing=0)
        self.add(hbox)
        hbox.pack_start(image, False, False, 0)

        discs = []
        for item in os.listdir(os.path.join(self.player.MUSIC_DIR, name)):
            if item.startswith('.'):
                continue
            if os.path.isdir(os.path.join(self.player.MUSIC_DIR, name, item)):
                discs.append(os.path.join(name, item))
        if discs == []:
            tracklist = self.get_tracklist(name)
        else:
            tracklist = self.multi_disc(discs)

        hbox.pack_start(tracklist, True, True, 0)

        self.show_all()

    def multi_disc(self, discs):
        discs.sort()
        tabbed = Gtk.Notebook()
        tabbed.set_scrollable(True)
        for disc in discs:
            scroll = self.get_tracklist(disc)
            tabbed.append_page(scroll, None)
            tabbed.set_tab_label_text(scroll, os.path.basename(disc))

        return tabbed

    def get_tracklist(self, disc):
        # scrolled area for the songs
        scroll = Gtk.ScrolledWindow()
        scroll.set_border_width(0)
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        # set up the song treeview
        liststore = Gtk.ListStore(str, str, str, str)
        songs = os.listdir(os.path.join(self.player.MUSIC_DIR, disc))
        tracklist = []
        for song in songs:
            path = os.path.join(self.player.MUSIC_DIR, disc, song)
            tags = utils.get_tags(path)
            if tags:
                tracklist.append(tags)
        tracklist.sort(key=lambda t: t[0])
        print(tracklist)
        [liststore.append(t) for t in tracklist]
        treeview = Gtk.TreeView(model=liststore)
        #treeview.set_property("headers-visible", False)
        treeview.set_enable_search(False)
        track_renderer = Gtk.CellRendererText()
        # option is PangoEllipsizeMode numbered 0,1,2,3 for none, start,
        # middle, end (True becomes 1=start)
        #track_renderer.set_property("ellipsize", 3)
        track_column = Gtk.TreeViewColumn("Track", track_renderer, text=0)
        treeview.append_column(track_column)

        title_renderer = Gtk.CellRendererText()
        #title_renderer.set_property("ellipsize", 3)
        title_column = Gtk.TreeViewColumn("Title", title_renderer, text=1)
        treeview.append_column(title_column)

        artist_renderer = Gtk.CellRendererText()
        #track_renderer.set_property("ellipsize", 3)
        artist_column = Gtk.TreeViewColumn("Artist", artist_renderer, text=2)
        treeview.append_column(artist_column)

        Gtk.TreeSelection.set_mode(
            treeview.get_selection(), Gtk.SelectionMode.MULTIPLE)

        treeview.connect("button-press-event", self.on_button_press, disc)
        treeview.connect("key-press-event", self.on_key_press, disc)

        scroll.add(treeview)

        return scroll

    def on_button_press(self, widget, event, disc):
        # print(event.type)
        select = widget.get_selection()
        model, treeiter = select.get_selected_rows()
        if event.button == 3:
            for path in treeiter:
                print(model[path][3])
                song = os.path.basename(model[path][3])
                self.player.queue(files=disc + '/' + song)
        elif event.button == 2:
            song = os.path.basename(model[treeiter][3])
            self.player.play(files=disc + '/' + song)
            for i in range(1, len(treeiter)):
                song = os.path.basename(model[i][3])
                self.player.queue(files=disc + '/' + song)
        elif event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS:
            song = os.path.basename(model[treeiter][3])
            self.player.play(files=disc + '/' + song)

    def on_key_press(self, widget, event, disc):
        select = widget.get_selection()
        model, treeiter = select.get_selected_rows()

        # TODO shift+P to play all, shift+Q to queue all
        if event.hardware_keycode == 36 or event.hardware_keycode == 33:
            for i, path in enumerate(treeiter):
                song = os.path.basename(model[path][3])
                if i == 0:
                    self.player.play(files=disc + '/' + song)
                else:
                    self.player.queue(files=disc + '/' + song)
        elif event.hardware_keycode == 24:
            for path in treeiter:
                song = os.path.basename(model[path][3])
                self.player.queue(files=disc + '/' + song)
        elif event.hardware_keycode == 65:
            self.player.toggle()
