from gi.repository import Gtk, GdkPixbuf
import os
from ..notifications import Notifier

# TODO: Make this be the connection between gui and backend by using the backend
# as an API. Will need API endpoints to skip, toggle, set states etc.


class Control(Gtk.Box):

    '''
    The GUI component of the player. All interaction with the backend playback
    of music is done through this module, including handling of signals.
    '''

    def __init__(self, player, server):
        self.player = player
        self.player.bus.connect('message::eos', self.on_eos)
        self.server = server

        self.image = Gtk.Image()
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
            "/opt/ricochet/images/default_album.png", 256, 256)
        self.image.set_from_pixbuf(pixbuf)
        self.image.show()
        # FIXME: the multi disc albums look in the directory containing
        # the songs rather than the toplevel album directory.

        Gtk.Box.__init__(self, orientation=1)
        self.pack_start(self.image, False, False, 0)

        buttons = [
            ('\u25AE\u25C0', self.skip_prev),
            ('\u25B6\u25AE\u25AE', self.toggle),
            ('\u25FC', self.stop),
            ('\u25B6\u25AE', self.skip_next)
        ]
        button_box = Gtk.Box()
        for label, method in buttons:
            button = Gtk.Button(label=label)
            button.connect("clicked", method)
            button.set_focus_on_click(False)
            button_box.pack_start(button, True, True, 0)
        self.pack_start(button_box, False, False, 0)

        scroll = Gtk.ScrolledWindow()
        scroll.set_border_width(0)
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.pack_start(scroll, True, True, 0)

        # create playlist tree widget
        self.liststore = Gtk.ListStore(str)
        self.treeview = Gtk.TreeView()
        self.treeview.set_enable_search(False)
        selection = self.treeview.get_selection()
        selection.set_mode(Gtk.SelectionMode.MULTIPLE)

        self.change_playlist()

        renderer = Gtk.CellRendererText()
        renderer.set_property("ellipsize", 3)
        column = Gtk.TreeViewColumn("Playlist", renderer, text=0)
        self.treeview.append_column(column)

        self.treeview.connect("row-activated", self.on_activate)
        self.treeview.connect("key_press_event", self.on_key_press)

        scroll.add(self.treeview)
        self.show_all()

    def on_eos(self, bus, msg):
        '''callback for when the end of a song is reached'''
        self.skip_next()

    def change_playlist(self, widget=None):
        '''handle playlist changes'''
        self.liststore.clear()
        for song in self.player.change_playlist():
            self.liststore.append([song])
        self.treeview.set_model(self.liststore)

    def on_key_press(self, widget, event):
        if event.hardware_keycode == 119:
            selection = widget.get_selection()
            songs = selection.get_selected_rows()[1]
            for song in songs:
                for track in self.player.playlist:
                    if self.liststore[song][0] in track:
                        self.player.playlist.remove(track)
            self.change_playlist(None)

    def on_activate(self, tree, path, column):
        '''callback for activation on playlist tree'''
        song = self.liststore[path][0]
        song = song.replace('\u25B6 ', '')
        song = song.replace('\u25AE\u25AE ', '')
        self.player.select_song(song)
        self.notify()
        self.update_image()
        self.change_playlist()

    def skip_prev(self, widget=None):
        self.player.skip_prev()
        self.notify()
        self.update_image()
        self.change_playlist()

    def skip_next(self, widget=None):
        self.player.skip_next()
        self.notify()
        self.update_image()
        self.change_playlist()

    def toggle(self, widget=None):
        '''toggle play state'''
        self.player.toggle()
        self.update_image()
        self.change_playlist()

    def stop(self, widget=None):
        self.player.stop()
        self.update_image()
        self.change_playlist()

    def update_image(self):
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
            "/opt/ricochet/images/default_album.png", 256, 256)
        if self.player.playlist:
            segs = self.player.playlist[self.player.track - 1].split('/')
            path = '/'.join(segs[2:-1]) + '/cover.jpg'
            if os.path.exists(path):
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
                    path, 256, 256)
        self.image.set_from_pixbuf(pixbuf)
        self.image.show()

    def notify(self):
        n = Notifier(self)
        if self.settings['notifications'] == "True":
            n.notify(self.player.track - 1)
