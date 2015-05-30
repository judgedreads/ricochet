from gi.repository import Gtk, Gdk, GdkPixbuf
import os

from . import settings


class Album(Gtk.Window):

    '''The class for the detailed album view'''

    def __init__(self, name, player):
        Gtk.Window.__init__(self, title=name)
        self.set_default_size(300, 600)

        self.name = name
        self.player = player

        path = ''.join([self.player.MUSIC_DIR, self.name, '/cover.jpg'])
        if not os.path.exists(path):
            path = '/opt/ricochet/images/default_album.jpg'
        size = int(self.player.settings['detail_icon_size'])
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(path, size, size)
        image = Gtk.Image()
        image.set_from_pixbuf(pixbuf)

        vbox = Gtk.Box(orientation=1, spacing=0)
        self.add(vbox)
        # make sure image doesn't expand or fill
        vbox.pack_start(image, False, False, 0)

        discs = []
        for item in os.listdir(self.player.MUSIC_DIR + name):
            if item.startswith('.'):
                continue
            if os.path.isdir(os.path.join(self.player.MUSIC_DIR, name, item)):
                discs.append(os.path.join(name, item))
        if discs == []:
            tracklist = self.get_tracklist(name)
        else:
            tracklist = self.multi_disc(discs)

        vbox.pack_start(tracklist, True, True, 0)

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
        liststore = Gtk.ListStore(str)
        songs = os.listdir(self.player.MUSIC_DIR + disc)
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

        return scroll

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
