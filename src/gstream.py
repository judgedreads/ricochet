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


from gi.repository import Gst, Gtk
import os
import subprocess

import settings


class Player(object):

    # callback for activation on playlist tree
    def on_activate(self, tree, path, column):
        song = self.liststore[path][0]
        i = 0
        for track in self.playlist:
            if track.find(song) != -1:
                self.track = i
            else:
                i += 1

        self.on_eos(None, None)

    def __init__(self, playlist):
        # Option to load a playlist on init
        print("Ricochet v0.3")
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

# keep track of play state
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


# info queries
# should make more functions use this to reduce code duplication
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


# handle playlist changes
    def change_playlist(self, widget):

        self.liststore.clear()

        for item in self.playlist:
            song = item.split('/')[-1]
            self.liststore.append([song])

        self.treeview.set_model(self.liststore)


# toggle play state
    def toggle(self, widget):
        if self.current_state == "PAUSED":
            #self.set_title(self.playlist[self.track - 1].split('/')[-1])
            self.pipeline.set_state(Gst.State.PLAYING)
            self.current_state = "PLAYING"
        elif self.current_state == "PLAYING":
            self.pipeline.set_state(Gst.State.PAUSED)
            self.current_state = "PAUSED"


# method to play now, i.e. replace playlist and play it
    def play(self, widget, data):

        # empty the playlist
        self.playlist = []

# need to set current music (if any) to stop before playing more
        self.pipeline.set_state(Gst.State.NULL)
        self.current_state = "PAUSED"

        # queue the new songs
        self.queue(None, data)
        self.playbin.set_property('uri', self.playlist[0])
        self.track = 1

        # play the playlist
        self.toggle(None)

        self.notify(None, 0)


# add music to current playlist
    def queue(self, widget, data):
        # check if directory or file
        if os.path.isdir("/home/judgedreads/Music/" + data):
            songs = os.listdir("/home/judgedreads/Music/" + data)
            songs.sort()
            for song in songs:
                # handle file types: wma doesn't work with gst for some reason
                ext = song.split('.')[-1]
                if ext in ['mp3', 'ogg', 'm4a', 'mp4', 'flac', 'mpc']:
                    temp = "file:///home/judgedreads/Music/" + \
                        data + "/" + song
                    self.playlist.append(temp)
        else:
            # no need to handle file types here as they are already handled
            # in the browser.
            song = "file:///home/judgedreads/Music/" + data
            self.playlist.append(song)

        self.change_playlist(None)


# unload the player
    def quit(self, widget, event):
        self.pipeline.set_state(Gst.State.NULL)

    def skip_next(self, widget):
        # unload player
        self.pipeline.set_state(Gst.State.NULL)
        i = self.track
        if i < len(self.playlist):
            # load next song and play
            self.playbin.set_property('uri', self.playlist[i])
            self.pipeline.set_state(Gst.State.PLAYING)
            self.track += 1

            self.notify(None, i)

    def skip_prev(self, widget):
        # unload player
        self.pipeline.set_state(Gst.State.NULL)
        i = self.track - 1
        if i > 0:
            # load previous song and play
            self.playbin.set_property('uri', self.playlist[i - 1])
            self.pipeline.set_state(Gst.State.PLAYING)
            self.track -= 1

            self.notify(None, i - 1)


# optional notifications using libnotify
    def notify(self, widget, index):
        if settings.settings['notifications'] == 'True':
            i = index
            print(self.playlist[i])
            song = self.playlist[i].split('/')[-1]
            album = self.playlist[i].split('/')[-2]
            artist = self.playlist[i].split('/')[-3]
            cover = "/home/judgedreads/Music/" + \
                artist + '/' + album + '/' + 'cover.jpg'

# There seems to be a bug in notify send where '&' can't be in
# subheading, even when quoted...
            subprocess.call(["notify-send", "-i", cover, song, artist])


# callback for when the end of a song is reached
    def on_eos(self, bus, msg):
        i = self.track
        # unload the player
        self.pipeline.set_state(Gst.State.NULL)
        if i < len(self.playlist):
            # load next song and play
            self.playbin.set_property('uri', self.playlist[i])
            self.pipeline.set_state(Gst.State.PLAYING)
            # advance the track counter
            self.track += 1

            self.notify(None, i)
        else:
            # stop when the last song is done
            self.pipeline.set_state(Gst.State.NULL)
