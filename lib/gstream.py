# Ricochet: A different angle on music.
# Copyright (C) 2013-2014 Pearce Dedmon

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from gi.repository import Gst, Gtk, Notify, GdkPixbuf
import os
import subprocess

from . import settings


if settings.settings['notifications'] == "True":
    from .notifications import Notifier
else:
    from .notifications import NullNotifier as Notifier


class Player(object):

    def __init__(self, playlist=None):
        '''Optionally load a playlist on init'''
        if playlist is None:
            playlist = []
        self.version = 'v' + \
            str(Gst.version()[0]) + '.' + \
            str(Gst.version()[1]) + '.' + str(Gst.version()[2])
        print("Using Gstreamer " + self.version)

        # keep track of playlist and current track
        self.playlist = playlist
        self.track = 1

        # set up gstreamer elements
        self.pipeline = Gst.Pipeline()

        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect('message::eos', self.on_eos)

        self.playbin = Gst.ElementFactory.make('playbin', None)

        self.pipeline.add(self.playbin)

        self.current_state = "PAUSED"

        # create playlist tree widget
        self.liststore = Gtk.ListStore(str)
        self.treeview = Gtk.TreeView()

        self.change_playlist(None)

        renderer = Gtk.CellRendererText()
        renderer.set_property("ellipsize", 3)
        column = Gtk.TreeViewColumn("Playlist", renderer, text=0)
        self.treeview.append_column(column)

        self.treeview.connect("row-activated", self.on_activate)

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
                "/opt/ricochet/images/music_note.png", 256, 256)
        self.image.set_from_pixbuf(self.pixbuf)
        self.image.show()

    def change_playlist(self, widget):
        '''handle playlist changes'''

        self.liststore.clear()

        for item in self.playlist:
            song = item.split('/')[-1]
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

    def queue(self, widget, data):
        '''add music to current playlist'''

        if os.path.isdir("/home/judgedreads/Music/" + data):
            songs = os.listdir("/home/judgedreads/Music/" + data)
            songs.sort()
            for song in songs:
                # handle file types: wma doesn't work with gst for some reason
                if song.endswith(('mp3', 'ogg', 'm4a', 'mp4', 'flac', 'mpc')):
                    temp = "file:///home/judgedreads/Music/" + \
                        data + "/" + song
                    self.playlist.append(temp)
        else:
            song = "file:///home/judgedreads/Music/" + data
            self.playlist.append(song)

        self.change_playlist(None)

    def quit(self, widget, event):
        self.pipeline.set_state(Gst.State.NULL)

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

    def skip_prev(self, widget):
        self.pipeline.set_state(Gst.State.NULL)
        i = self.track - 1
        if i > 0:
            self.playbin.set_property('uri', self.playlist[i - 1])
            self.pipeline.set_state(Gst.State.PLAYING)
            self.track -= 1

            self.notify(i - 1)
            self.update_image()

    def notify(self, i):
        n = Notifier(self.playlist)
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
        else:
            self.pipeline.set_state(Gst.State.NULL)
