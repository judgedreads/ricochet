from gi.repository import Gst, Gtk, GdkPixbuf
import os

from . import settings


if settings.settings['notifications'] == "True":
    from .notifications import Notifier
else:
    from .notifications import NullNotifier as Notifier


class Player(object):

    def __init__(self, playlist=None):
        '''Optionally load a playlist on init'''
        VERSION = '.'.join(map(str, Gst.version()[0:3]))
        if playlist is None:
            playlist = []
        print("Using Gstreamer v%s" % VERSION)
        self.MUSIC_DIR = settings.settings['music_dir']

        # keep track of playlist and current track
        self.playlist = playlist
        self.track = 1
        self.current_state = "PAUSED"

        # set up gstreamer elements
        self.pipeline = Gst.Pipeline()
        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect('message::eos', self.on_eos)
        self.playbin = Gst.ElementFactory.make('playbin', None)
        self.pipeline.add(self.playbin)

        # create playlist tree widget
        self.liststore = Gtk.ListStore(str)
        self.treeview = Gtk.TreeView()
        selection = self.treeview.get_selection()
        selection.set_mode(Gtk.SelectionMode.MULTIPLE)

        self.change_playlist(None)

        renderer = Gtk.CellRendererText()
        renderer.set_property("ellipsize", 3)
        column = Gtk.TreeViewColumn("Playlist", renderer, text=0)
        self.treeview.append_column(column)

        self.treeview.connect("row-activated", self.on_activate)
        self.treeview.connect("key_press_event", self.on_key_press)

    def on_activate(self, tree, path, column):
        '''callback for activation on playlist tree'''
        song = self.liststore[path][0]
        i = 0
        for track in self.playlist:
            if track.find(song) != -1:
                self.track = i
            else:
                i += 1
        self.on_eos(None, None)

    def on_key_press(self, widget, event):
        if event.hardware_keycode == 119:
            selection = widget.get_selection()
            songs = selection.get_selected_rows()[1]
            for song in songs:
                for track in self.playlist:
                    if self.liststore[song][0] in track:
                        self.playlist.remove(track)
            self.change_playlist(None)

    def get_info(self, widget, data):
        i = self.track
        if data == "pos":
            pos = self.pipeline.query_position(Gst.Format.TIME)[1]
            pos = round(pos / 1000000000)
            pos_min = int(pos / 60)
            pos_sec = int(pos) % 60
            dur = self.pipeline.query_duration(Gst.Format.TIME)[1]
            dur = round(dur / 1000000000)
            dur_min = int(dur / 60)
            dur_sec = int(dur) % 60
            return pos_min, pos_sec, dur_min, dur_sec
        elif data == "song":
            song = self.playlist[i - 1].split('/')[-1]
            return song
        elif data == "album":
            album = self.playlist[i - 1].split('/')[-2]
            return album
        elif data == "artist":
            artist = self.playlist[i - 1].split('/')[-3]
            return artist

    def update_image(self):
        segs = self.playlist[self.track - 1].split('/')
        path = '/'.join(segs[2:-1]) + '/cover.jpg'
        if os.path.exists(path):
            self.pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
                path, 256, 256)
        else:
            self.pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
                "/opt/ricochet/images/default_album.jpg", 256, 256)
        self.image.set_from_pixbuf(self.pixbuf)
        self.image.show()

    def change_playlist(self, widget):
        '''handle playlist changes'''
        self.liststore.clear()
        for i, item in enumerate(self.playlist):
            segs = item.split('/')[-1].split('.')[:-1]
            song = '.'.join(segs)
            if i == self.track - 1 and self.current_state == 'PLAYING':
                song = '\u25B6 ' + song
            self.liststore.append([song])
        self.treeview.set_model(self.liststore)

    def toggle(self, widget):
        '''toggle play state'''
        if self.current_state == "PAUSED":
            self.pipeline.set_state(Gst.State.PLAYING)
            self.current_state = "PLAYING"
        elif self.current_state == "PLAYING":
            self.pipeline.set_state(Gst.State.PAUSED)
            self.current_state = "PAUSED"
        self.change_playlist(None)

    def play(self, widget, data):
        '''method to play now, i.e. replace playlist and play it'''

        self.playlist = []
        self.pipeline.set_state(Gst.State.NULL)
        self.current_state = "PAUSED"

        # queue the new songs
        self.queue(None, data)
        self.playbin.set_property('uri', self.playlist[0])
        self.track = 1

        # play the playlist
        self.toggle(None)

        self.notify(0)
        self.update_image()
        self.change_playlist(None)

    def queue(self, widget, data):
        '''add music to current playlist'''

        if os.path.isdir(self.MUSIC_DIR + data):
            discs = []
            for item in os.listdir(self.MUSIC_DIR + data):
                if item.startswith('.'):
                    continue
                if os.path.isdir(os.path.join(self.MUSIC_DIR, data, item)):
                    discs.append(os.path.join(data, item))
            if discs == []:
                discs.append(data)
            songs = []
            discs.sort()
            for disc in discs:
                files = os.listdir(self.MUSIC_DIR + disc)
                files.sort()
                songs.extend(files)
            for song in songs:
                # handle file types: wma doesn't work with gst for some reason
                if song.endswith(('mp3', 'ogg', 'm4a', 'mp4', 'flac', 'mpc')):
                    temp = "file://%s%s/%s" % (self.MUSIC_DIR, data, song)
                    self.playlist.append(temp)
        else:
            song = "file://%s%s" % (self.MUSIC_DIR, data)
            self.playlist.append(song)

        self.change_playlist(None)

    def quit(self, widget, event):
        self.pipeline.set_state(Gst.State.NULL)

    def stop(self, widget):
        self.pipeline.set_state(Gst.State.NULL)
        self.current_state = 'PAUSED'
        self.playlist = []
        self.change_playlist(None)

    def skip_next(self, widget):
        print('skipping')
        self.pipeline.set_state(Gst.State.NULL)
        i = self.track
        if i < len(self.playlist):
            self.playbin.set_property('uri', self.playlist[i])
            self.pipeline.set_state(Gst.State.PLAYING)
            self.track += 1
            self.notify(i)
            self.update_image()
            self.change_playlist(None)

    def skip_prev(self, widget):
        self.pipeline.set_state(Gst.State.NULL)
        i = self.track - 1
        if i > 0:
            self.playbin.set_property('uri', self.playlist[i - 1])
            self.pipeline.set_state(Gst.State.PLAYING)
            self.track -= 1
            self.notify(i - 1)
            self.update_image()
            self.change_playlist(None)

    def notify(self, i):
        n = Notifier(self)
        n.notify(i)

    def on_eos(self, bus, msg):
        '''callback for when the end of a song is reached'''
        i = self.track
        self.pipeline.set_state(Gst.State.NULL)
        if i < len(self.playlist):
            self.playbin.set_property('uri', self.playlist[i])
            self.pipeline.set_state(Gst.State.PLAYING)
            self.track += 1
            self.notify(i)
            self.update_image()
            self.change_playlist(None)
        else:
            self.pipeline.set_state(Gst.State.NULL)
