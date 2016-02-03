from gi.repository import Gtk, GdkPixbuf, Notify


class Control(Gtk.Box):

    '''
    The GUI component of the player. All interaction with the backend playback
    of music is done through this module, including handling of signals.
    '''

    def __init__(self, player, settings):
        self.player = player
        self.player.listen(self.event_callback)
        self.track = 1

        self.settings = settings

        self.image = Gtk.Image()
        self.update_image()

        Gtk.Box.__init__(self, orientation=1)
        self.pack_start(self.image, False, False, 0)

        # TODO: it would be cool to have the toggle button change icon
        if settings['symbolic_icons'] == True:
            buttons = [
                ('media-skip-backward-symbolic', self.skip_prev),
                ('media-playback-start-symbolic', self.toggle),
                ('media-playback-stop-symbolic', self.stop),
                ('media-skip-forward-symbolic', self.skip_next)
            ]
        else:
            buttons = [
                ('media-skip-backward', self.skip_prev),
                ('media-playback-start', self.toggle),
                ('media-playback-stop', self.stop),
                ('media-skip-forward', self.skip_next)
            ]
        button_box = Gtk.Box()
        for icon, method in buttons:
            button = Gtk.Button.new_from_icon_name(icon, 1)
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

    def event_callback(self, *args, **kwargs):
        self.change_playlist()

    def change_playlist(self, widget=None):
        '''handle playlist changes'''
        self.player.change_playlist()
        self.liststore.clear()
        for song in self.player.playlist:
            if song['playing'] == 'playing':
                self.liststore.append(['\u25B6 ' + song['name']])
            elif song['playing'] == 'paused':
                self.liststore.append(['\u25AE\u25AE ' + song['name']])
            else:
                self.liststore.append([song['name']])
        self.treeview.set_model(self.liststore)
        if self.player.track != self.track:
            self.track = self.player.track
            self.update_image()
            self.notify()

    def on_key_press(self, widget, event):
        if event.hardware_keycode == 119:
            selection = widget.get_selection()
            songs = selection.get_selected_rows()[1]
            rm = []
            for song in songs:
                # don't remove play/pause char as we want this song to be
                # unremovable
                for i, track in enumerate(self.player.playlist):
                    if self.liststore[song][0] == track['name']:
                        rm.append(i)
            for x, i in enumerate(rm):
                self.player.remove(i-x)
            self.change_playlist()

    def on_activate(self, tree, path, column):
        '''callback for activation on playlist tree'''
        song = self.liststore[path][0]
        song = song.replace('\u25B6 ', '')
        song = song.replace('\u25AE\u25AE ', '')
        self.player.select_song(song)
        self.change_playlist()

    def skip_prev(self, *args, **kwargs):
        self.player.skip_prev()
        self.change_playlist()

    def skip_next(self, *args, **kwargs):
        self.player.skip_next()
        self.change_playlist()

    def toggle(self, widget=None):
        '''toggle play state'''
        self.player.toggle()
        self.change_playlist()

    def stop(self, widget=None):
        self.player.stop()
        self.track = 1
        self.update_image()
        self.change_playlist()

    def play(self, *args, **kwargs):
        self.player.play(*args, **kwargs)
        self.change_playlist()
        self.update_image()

    def queue(self, *args, **kwargs):
        self.player.queue(*args, **kwargs)
        self.change_playlist()

    def update_image(self):
        # FIXME: the multi disc albums look in the directory containing
        # the songs rather than the toplevel album directory.
        cover = "/usr/share/ricochet/default_album.png"
        if self.player.playlist:
            song = self.player.playlist[self.player.track - 1]
            cover = song['cover']
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(cover, 256, 256)
        self.image.set_from_pixbuf(pixbuf)
        self.image.show()

    def notify(self):
        if self.settings['notifications'] != "True":
            return
        song = self.player.playlist[self.player.track - 1]
        cover = song['cover']
        icon = 'ricochet'
        title = song['name']
        body = 'by %s\non %s' % (song['artist'], song['album'])

        n = Notifier(self)
        n.notify(title, body, icon, cover)


class Notifier(object):

    '''Class to handle all notifications'''

    def __init__(self, player):
        self.notif = Notify.Notification()
        self.notif.set_category('x-gnome.music')
        self.notif.set_timeout(3)
        self.player = player

    def notify(self, title, body, icon, cover):
        self.notif.clear_actions()
        self.notif.add_action('skip_next', '\u25AE\u25C0',
                              self.notif_skip, 'prev')
        self.notif.add_action('skip_prev', '\u25B6\u25AE',
                              self.notif_skip, 'next')
        self.notif.update(title, body, icon)
        image = GdkPixbuf.Pixbuf.new_from_file(cover)
        self.notif.set_image_from_pixbuf(image)
        self.notif.show()

    def notif_skip(self, notification, action, data, ignore=None):
        notification.close()
        if data == 'next':
            self.player.skip_next()
        elif data == 'prev':
            self.player.skip_prev()