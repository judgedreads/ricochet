from gi.repository import Gtk, Gdk, GdkPixbuf
import os


class Album(Gtk.Window):

    '''The class for the detailed album view'''

    def __init__(self, info, player, app):
        name = ' - '.join([info['artist'], info['title']])
        Gtk.Window.__init__(self, title=name)
        size = player.settings['detail_icon_size']
        windows = app.get_windows()
        self.set_transient_for(windows[0])
        self.set_modal(True)
        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)

        self.player = player

        self.tracks = info['tracks']

        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
            info['cover'], size, size)
        image = Gtk.Image()
        image.set_from_pixbuf(pixbuf)

        hbox = Gtk.Box(orientation=0, spacing=0)
        self.add(hbox)
        hbox.pack_start(image, False, False, 0)

        tracklist = self.make_tracklist()
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

    def make_tracklist(self):
        scroll = Gtk.ScrolledWindow()
        scroll.set_border_width(0)
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        liststore = Gtk.ListStore(str, str, str, str, str)
        for t in self.tracks:
            track_num = t['track'].split('/')[0].zfill(2)
            secs = int(t['time'])
            mins = secs // 60
            rem = secs % 60
            time = '%02d:%02d' % (mins, rem)
            row = [track_num, t['title'], t['artist'], time, t['file']]
            liststore.append(row)
        treeview = Gtk.TreeView(model=liststore)
        treeview.set_enable_search(False)
        track_renderer = Gtk.CellRendererText()
        track_column = Gtk.TreeViewColumn("Track", track_renderer, text=0)
        treeview.append_column(track_column)

        title_renderer = Gtk.CellRendererText()
        title_column = Gtk.TreeViewColumn("Title", title_renderer, text=1)
        treeview.append_column(title_column)

        artist_renderer = Gtk.CellRendererText()
        artist_column = Gtk.TreeViewColumn("Artist", artist_renderer, text=2)
        treeview.append_column(artist_column)

        length_renderer = Gtk.CellRendererText()
        length_column = Gtk.TreeViewColumn("Length", length_renderer, text=3)
        treeview.append_column(length_column)

        Gtk.TreeSelection.set_mode(
            treeview.get_selection(), Gtk.SelectionMode.MULTIPLE)

        treeview.connect("button-press-event", self.on_button_press)
        treeview.connect("key-press-event", self.on_key_press)

        scroll.add(treeview)

        return scroll

    def on_button_press(self, widget, event):
        # print(event.type)
        select = widget.get_selection()
        model, treeiter = select.get_selected_rows()
        songs = []
        for path in treeiter:
            f = model[path][4]
            for t in self.tracks:
                if t['file'] == f:
                    songs.append(t)
                    break
        if event.button == 3:
            self.player.queue(songs)
        elif event.button == 2:
            self.player.play(songs)
        elif event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS:
            songs = []
            f = model[treeiter][4]
            for t in self.tracks:
                if t['file'] == f:
                    songs.append(t)
                    break
            self.player.play(songs)

    def on_key_press(self, widget, event):
        select = widget.get_selection()
        model, treeiter = select.get_selected_rows()
        songs = []
        for path in treeiter:
            f = model[path][4]
            for t in self.tracks:
                if t['file'] == f:
                    songs.append(t)
                    break
        # TODO shift+P to play all, shift+Q to queue all
        if event.hardware_keycode == 36 or event.hardware_keycode == 33:
            self.player.play(songs)
        elif event.hardware_keycode == 24:
            self.player.queue(songs)
        elif event.hardware_keycode == 65:
            self.player.toggle()
