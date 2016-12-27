from gi.repository import Gtk, GdkPixbuf, Notify, GLib
from ricochet import utils
import os


class Control(Gtk.Box):

    '''
    The GUI component of the player. All interaction with the backend playback
    of music is done through this module, including handling of signals.
    '''

    def __init__(self, player, status):
        self.player = player
        self.player.listen(self.event_callback)
        self.track = 1
        self.status = status
        self.status.update()

        self.image = Gtk.Image()
        self.update_image()

        Gtk.Box.__init__(self, orientation=1)
        self.pack_start(self.image, False, False, 0)

        button_box = self.make_buttons()
        self.pack_start(button_box, False, False, 0)

        scroll = Gtk.ScrolledWindow()
        scroll.set_border_width(0)
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.pack_start(scroll, True, True, 0)

        # create playlist tree widget
        self.liststore = Gtk.ListStore(str, str)
        self.treeview = Gtk.TreeView()
        self.treeview.set_enable_search(False)
        self.treeview.set_property("headers-visible", False)
        selection = self.treeview.get_selection()
        selection.set_mode(Gtk.SelectionMode.MULTIPLE)

        renderer = Gtk.CellRendererText()
        renderer.set_property("ellipsize", 3)
        column = Gtk.TreeViewColumn("Playlist", renderer, text=0)
        self.treeview.append_column(column)

        self.treeview.connect("row-activated", self.on_activate)
        self.treeview.connect("key_press_event", self.on_key_press)

        scroll.add(self.treeview)

        self.pl_stats = Gtk.Label()
        self.pl_stats.set_xalign(0)

        self.pack_start(self.pl_stats, False, False, 0)
        self.change_playlist()

        self.show_all()

    def event_callback(self, *args, **kwargs):
        self.change_playlist()
        self.update_tgl_btn()
        self.status.update()

    def make_buttons(self):
        buttons = [
            ('media-skip-backward', self.skip_prev),
            ('media-playback-start', self.toggle),
            ('media-playback-stop', self.stop),
            ('media-skip-forward', self.skip_next)
        ]
        button_box = Gtk.Box()
        for icon, method in buttons:
            if utils.SETTINGS['symbolic_icons'] is True:
                icon += '-symbolic'
            button = Gtk.Button.new_from_icon_name(icon, 1)
            if method == self.toggle:
                self.tgl_btn = button
                self.update_tgl_btn()
            button.connect("clicked", method)
            button.set_focus_on_click(False)
            button_box.pack_start(button, True, True, 0)
        return button_box

    def update_tgl_btn(self):
        state = self.player.get_play_state()
        # TODO: store these vars somewhere, they don't change often.
        # could probs just set them up in settings dict.
        play = 'media-playback-start'
        pause = 'media-playback-pause'
        if utils.SETTINGS['symbolic_icons'] is True:
            pause += '-symbolic'
            play += '-symbolic'
        im = self.tgl_btn.get_image()
        icon = im.get_icon_name()
        if state == 'play':
            im.set_from_icon_name(pause, icon[1])
        else:
            im.set_from_icon_name(play, icon[1])

    def change_playlist(self, widget=None):
        '''handle playlist changes'''
        pl = self.player.get_playlist()
        # self.player.change_playlist()
        self.liststore.clear()
        status = self.player.get_status()
        for song in pl:
            if status['state'] == 'stop':
                self.liststore.append([song['title'], song['id']])
                continue
            if song['id'] == status['songid']:
                if status['state'] == 'play':
                    self.liststore.append(
                        ['\u25B6 ' + song['title'], song['id']])
                elif status['state'] == 'pause':
                    self.liststore.append(
                        ['\u25AE\u25AE ' + song['title'], song['id']])
            else:
                self.liststore.append([song['title'], song['id']])
        self.treeview.set_model(self.liststore)
        ttime = sum(int(t['time']) for t in pl)
        mins = ttime // 60
        secs = ttime % 60
        pl_stats = ' %d tracks totalling %d:%02d  ' % (len(pl), mins, secs)
        self.pl_stats.set_text(pl_stats)
        # FIXME: this stuff probably shouldn't be done here...
        if status.get('song') != self.track:
            self.track = status.get('song')
            self.update_image()
            self.notify()

    def on_key_press(self, widget, event):
        if event.hardware_keycode == 119:
            selection = widget.get_selection()
            songs = selection.get_selected_rows()[1]
            for song in songs:
                self.player.remove(self.liststore[song][1])

    def on_activate(self, tree, path, column):
        '''callback for activation on playlist tree'''
        songid = self.liststore[path][1]
        self.player.select_song(songid)

    def skip_prev(self, *args, **kwargs):
        self.player.skip_prev()

    def skip_next(self, *args, **kwargs):
        self.player.skip_next()

    def toggle(self, widget=None):
        '''toggle play state'''
        self.player.toggle()

    def stop(self, widget=None):
        self.player.stop()
        self.track = 1
        self.update_image()

    def play(self, *args, **kwargs):
        self.player.play(*args, **kwargs)
        self.update_image()

    def queue(self, *args, **kwargs):
        self.player.queue(*args, **kwargs)

    def update_image(self):
        f = self.player.get_currentsong().get('file', '')
        cover = utils.get_cover_path(os.path.dirname(f))
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(cover, 256, 256)
        self.image.set_from_pixbuf(pixbuf)
        self.image.show()

    def notify(self):
        if utils.SETTINGS['notifications'] != "True":
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


class StatusLine(Gtk.Box):

    def __init__(self, player):
        Gtk.Box.__init__(self)
        self.player = player
        self.stats = Gtk.Label()
        stats = self.player.get_stats()
        text = '    {albums} albums featuring {artists} artists containing '\
               '{songs} songs '.format(**stats)
        self.stats.set_text(text)
        self.stats.set_xalign(1)

        self.audio = Gtk.Label()
        self.audio.set_xalign(0)

        self.slider = Gtk.Scale()
        self.slider.set_draw_value(False)
        self.slider.set_increments(1, 10)
        self.slider.set_min_slider_size(200)
        self.slider_handler_id = self.slider.connect(
            "value-changed", self.on_slide)
        self.sync_slider()

        self.pack_start(self.audio, False, False, 0)
        self.pack_start(self.slider, True, True, 0)
        self.pack_start(self.stats, False, False, 0)

        self.playing = False

    def on_slide(self, widget):
        if not self.playing:
            return
        t = self.slider.get_value()
        self.player.seek(t)

    def sync_slider(self, s=None):
        if s is None:
            s = self.player.get_status()
        t = s.get('time', '0:100').split(':')
        self.slider.handler_block(self.slider_handler_id)
        self.slider.set_value(int(t[0]))
        self.slider.set_range(0, int(t[1]))
        self.slider.handler_unblock(self.slider_handler_id)

    def increment_slider(self):
        if not self.playing:
            self.sync_slider()
            return False
        self.slider.handler_block(self.slider_handler_id)
        self.slider.set_value(self.slider.get_value() + 1)
        self.slider.handler_unblock(self.slider_handler_id)
        return True

    def update_audio_info(self, s):
        if 'audio' not in s:
            self.audio.set_text('')
            return
        done, tot = map(int, s['time'].split(':'))
        tprog = '%2d:%02d/%2d:%02d' % (done // 60, done % 60, tot // 60, tot % 60)
        freq, bit, chan = s['audio'].split(':')
        text = '  %sHz | %2s bit | %s channel | %4skbps | %s    '
        self.audio.set_text(text % (freq, bit, chan, s['bitrate'], tprog))

    def on_timeout(self):
        if not self.playing:
            return False
        s = self.player.get_status()
        self.sync_slider(s)
        self.update_audio_info(s)
        return True

    def update(self):
        s = self.player.get_status()
        if s['state'] == 'play':
            if not self.playing:
                self.playing = True
                GLib.timeout_add(1000, self.on_timeout)
        else:
            self.playing = False
        self.update_audio_info(s)
        self.sync_slider(s)
