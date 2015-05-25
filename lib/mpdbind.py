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


from gi.repository import Gtk
import mpd

from . import settings


class Player(object):

    # callback for activation on playlist tree
    def on_activate(self, tree, path, column):
        song = self.liststore[path][0]
        i = 0
        for track in self.client.playlist():
            if track.find(song) != -1:
                self.track = i
                break
            else:
                i += 1
        self.client.play(self.track)

    def __init__(self, playlist):
        # option to load a playlist on init

        self.client = mpd.MPDClient()
        VERSION = self.client.mpd_version
        self.host = settings.settings['mpd_host']
        self.port = settings.settings['mpd_port']

        # catch connection errors
        try:
            self.client.connect(self.host, self.port)
        except mpd.ConnectionError:
            print("Could not connect to %s on port %d." %
                  (self.host, self.port))
            print("Check that mpd is running correctly.")

        print("Using MPD v%s" % VERSION)

        # create playlist widget
        self.liststore = Gtk.ListStore(str)
        self.treeview = Gtk.TreeView()

        # initialize the playlist
        self.change_playlist(None)

        renderer = Gtk.CellRendererText()
        renderer.set_property("ellipsize", 3)
        column = Gtk.TreeViewColumn("Playlist", renderer, text=0)
        self.treeview.append_column(column)
        self.treeview.connect("row_activated", self.on_activate)

    def get_info(self, widget, data):
        if data == "pos":
            self.check_connected()
            pos = self.client.status()['elapsed']
            pos = float(pos)
            pos_min = int(pos / 60)
            pos_sec = int(pos) % 60
            dur = self.client.currentsong()['time']
            dur = float(dur)
            dur_min = int(dur / 60)
            dur_sec = int(dur) % 60
            return pos_min, pos_sec, dur_min, dur_sec
        elif data == "song":
            song = self.client.currentsong()['title']
            return song
        elif data == "album":
            album = self.client.currentsong()['album']
            return album
        elif data == "artist":
            artist = self.client.currentsong()['artist']
            return artist


# handle reloading of the playlist widget upon changes
    def change_playlist(self, widget):
        self.check_connected()

        self.liststore.clear()
        playlist = self.client.playlist()

        for item in playlist:
            song = item.split('/')[-1]
            self.liststore.append([song])

        self.treeview.set_model(self.liststore)


# toggle between playing and paused
    def toggle(self, widget):
        self.check_connected()

        self.client.pause()


# method to play now, i.e. replace playlist and play it
    def play(self, widget, data):
        self.check_connected()

        self.client.clear()
        self.client.add(data)
        self.client.play()

        self.change_playlist(None)


# add songs to the current playlist
    def queue(self, widget, data):
        self.check_connected()

        self.client.add(data)

        self.change_playlist(None)


# close connections to mpd
    def quit(self, widget, event):
        self.check_connected()

        self.client.close()
        self.client.disconnect()

    def skip_next(self, widget):
        self.check_connected()

        self.client.next()

    def skip_prev(self, widget):
        self.check_connected()

        self.client.previous()


# safety measure to handle connection errors before commands
    def check_connected(self):
        try:
            self.client.ping()
        except mpd.ConnectionError:
            self.client.connect(self.host, self.port)
