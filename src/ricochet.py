#!/usr/bin/env python3

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


from gi.repository import Gst, Gtk, GObject, Notify
from socket import socket, AF_UNIX, SOCK_DGRAM
import os
import subprocess

import browser
import settings
from control import Control


if settings.settings['backend'] == "gstreamer":
    import gstream as backend
    Gst.init()
elif settings.settings['backend'] == "mpd":
    import mpdbind as backend
else:
    print("Invalid backend: should be 'mpd' or 'gstreamer'")




# callback for tray to show/hide windows
def show_hide(widget, event):
    if event.button == 1:
        if control.get_visible():
            control.hide()
        else:
            control.show()
    elif event.button == 3:
        if brow.get_visible():
            brow.hide()
        else:
            brow.show()

# TODO: pass this shit through as args to __init__
player  = backend.Player()
browser.player = player

# the main music directory
music = settings.settings['music_dir']
browser.music = music

artists = os.listdir(music)

albums = []

for artist in artists:
    # list all items(albums) in the artist directory
    albumlist = os.listdir(music + artist)
    for i in range(0, len(albumlist)):
        albumlist[i] = artist + "/" + albumlist[i]
    # need extend method as append only joins one item i.e. treats whole
    # extra array as one item
    albums.extend(albumlist)


# listdir accesses files the way they are indexed in the filesystem
# so need to sort them. list.sort() alters current list, sorted returns
# a new one. Don't need the old one and .sort is more efficient.
albums.sort()


# instantiate the browser
brow = browser.Browser(albums)

control = Control()
control.show_all()

# show the window and run the main method
brow.show_all()
brow.connect("delete-event", brow.quit)

# optionally create system tray icon
if settings.settings['system_tray'] == 'True':
    tray = Gtk.StatusIcon.new_from_file("images/ricochet.png")
    tray.connect("button-press-event", show_hide)


# callback for the socket communication
def handle_connection(source, condition):
    # receive data and decode it from bytes to str
    data = server.recv(1024).decode('UTF-8')
    sock = socket(AF_UNIX, SOCK_DGRAM)
    sock.connect('/tmp/ricochetctl')
    if data == "toggle":
        player.toggle(None)
        message = "toggle"
    elif data == "next":
        player.skip_next(None)
        message = "next"
    elif data == "prev":
        player.skip_prev(None)
        message = "prev"
    elif data == "pos":
        pos_min, pos_sec, dur_min, dur_sec = player.get_info(
            None, data)
        message = "%d:%d/%d:%d" % (pos_min, pos_sec, dur_min, dur_sec)
    elif data == "artist":
        message = player.get_info(None, data)
    elif data == "album":
        message = player.get_info(None, data)
    elif data == "song":
        message = player.get_info(None, data)

    info = bytes(message, 'UTF-8')
    sock.sendall(info)
# by returning True, the io watcher remains
    return True

# create a named pipe for communication
server = socket(AF_UNIX, SOCK_DGRAM)
try:
    server.bind('/tmp/ricochet')
except OSError:
    subprocess.call(['rm', '/tmp/ricochet'])
    server.bind('/tmp/ricochet')
GObject.io_add_watch(server, GObject.IO_IN, handle_connection)

Notify.init('ricochet')

# main loop
Gtk.main()
