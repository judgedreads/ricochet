# Ricochet: A different angle on music.
# Copyright (C) 2013-2014 Pearce Dedmon

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from gi.repository import Gtk, Gdk, GdkPixbuf
import os

from . import settings
from . import albumart


class Cover(Gtk.Button):

    '''The class structure for each album in the main browser'''

    def __init__(self, name):
        Gtk.Button.__init__(self)
        self.name = name
        self.directory = music + self.name

        self.image = Gtk.Image()
        self.set_album_art()
        self.add(self.image)

        # set up menu and its items
        self.menu = Gtk.Menu()
        menu_item_open = Gtk.MenuItem("Open")
        self.menu.append(menu_item_open)
        menu_item_open.connect("activate", self.album_detail)
        menu_item_open.show()
        menu_item_queue = Gtk.MenuItem("Queue")
        self.menu.append(menu_item_queue)
        menu_item_queue.connect("activate", player.queue, self.name)
        menu_item_queue.show()
        menu_item_play = Gtk.MenuItem("Play")
        self.menu.append(menu_item_play)
        menu_item_play.connect("activate", player.play, self.name)
        menu_item_play.show()
        menu_item_cover = Gtk.MenuItem("Get Cover")
        self.menu.append(menu_item_cover)
        menu_item_cover.connect("activate", self.fetch_album_art)
        menu_item_cover.show()

        self.connect("button-press-event", self.on_button_press)

        self.set_tooltip_text(self.name)

        self.show()

    def set_album_art(self):
        size = int(settings.settings['grid_icon_size'])
        if os.path.exists(self.directory + "/cover.jpg"):
            self.pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
                self.directory + "/cover.jpg", size, size)
        else:
            self.pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
                "/opt/ricochet/images/music_note.png", size, size)
        self.image.set_from_pixbuf(self.pixbuf)
        self.image.show()

    def album_detail(self, widget):
        '''launch the detailed album view'''
        album = Album(self.name)

    def fetch_album_art(self, widget):
        code = albumart.fetch_album_art(self.name)
        if code == 0:
            self.set_album_art()

    def on_button_press(self, widget, event):
        '''Callback function for clicking on album'''
        if event.button == 1:
            self.album_detail(self)
        elif event.button == 2:
            player.play(None, self.name)
        elif event.button == 3:
            self.menu.popup(
                None, None, None, self.name, event.button, event.time)


class Browser(Gtk.Window):

    '''The main window displaying all covers'''

    def __init__(self, albums):
        Gtk.Window.__init__(self, title="Cover Browser")

        self.albums = albums

        self.set_border_width(0)
        self.set_icon_from_file("/opt/ricochet/images/ricochet.png")
        self.set_default_size(950, 500)

        # scrolled window for the albums
        self.scroll = Gtk.ScrolledWindow()
        self.scroll.set_border_width(0)
        self.scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scroll.show()
        self.add(self.scroll)

        # flowbox to hold the albums for dynamic window resizing and row
        # organising
        self.flowbox = Gtk.FlowBox()
        self.flowbox.set_valign(Gtk.Align.START)
        self.flowbox.set_max_children_per_line(20)
        # allows selection of items with keyboard
        self.flowbox.set_selection_mode(Gtk.SelectionMode.BROWSE)
        self.flowbox.connect("key-press-event", self.on_key_press)
        self.scroll.add(self.flowbox)

        # a loop to create a Cover class for each album found
        for album in albums:
            temp = Cover(album)
            self.flowbox.add(temp)

    def on_key_press(self, widget, event):
        '''handle keyboard controls'''
        # print(event.hardware_keycode)
        child = self.get_focus()
        index = child.get_index()
        if event.hardware_keycode == 36 or event.hardware_keycode == 32:
            Album(self.albums[index])
        elif event.hardware_keycode == 33:
            player.play(None, self.albums[index])
        elif event.hardware_keycode == 24:
            player.queue(None, self.albums[index])
        elif event.hardware_keycode == 65:
            player.toggle(None)

    def quit(self, widget, event):
        self.hide()
        # make sure it doesn't delete
        return True


class Album(Gtk.Window):

    '''The class for the detailed album view'''

    def __init__(self, name):
        Gtk.Window.__init__(self, title=name)
        self.set_default_size(256, 512)

        self.name = name

        if os.path.exists(music + name + "/cover.jpg"):
            self.pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
                music + name + "/cover.jpg", 256, 256)
            self.set_icon_from_file(music + name + "/cover.jpg")
        else:
            self.pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
                "/opt/ricochet/images/music_note.png", 256, 256)
            self.set_icon_from_file("/opt/ricochet/images/music_note.png")

        self.image = Gtk.Image()
        self.image.set_from_pixbuf(self.pixbuf)

        # orientation defaults to 0 (horiz)
        self.vbox = Gtk.Box(orientation=1, spacing=0)
        self.add(self.vbox)
        # make sure image doesn't expand or fill but the scroll window
        # does.
        self.vbox.pack_start(self.image, False, False, 0)

        # scrolled area for the songs
        self.scroll = Gtk.ScrolledWindow()
        self.scroll.set_border_width(0)
        self.scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.vbox.pack_start(self.scroll, True, True, 0)

        songs = os.listdir(music + name)
        songs.sort()

        # set up the song treeview
        self.liststore = Gtk.ListStore(str)

        for song in songs:
            if song.endswith(("mp3", "mpc", "ogg", "wma", "m4a", "mp4", "flac")):
                self.liststore.append([song])

        treeview = Gtk.TreeView(model=self.liststore)

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

        treeview.connect("button-press-event", self.on_button_press)
        treeview.connect("key-press-event", self.on_key_press)

        self.scroll.add(treeview)

        self.show_all()

    def on_button_press(self, widget, event):
        # print(event.type)
        select = widget.get_selection()
        model, treeiter = select.get_selected_rows()
        if event.button == 3:
            for path in treeiter:
                player.queue(None, self.name + '/' + model[path][0])
        elif event.button == 2:
            player.play(None, self.name + '/' + model[treeiter][0])
            for i in range(1, len(treeiter)):
                player.queue(None, self.name + '/' + model[i][0])
        elif event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS:
            player.play(None, self.name + '/' + model[treeiter][0])

    # TODO: Could also make the backend capable of handling lists ^^

    def on_key_press(self, widget, event):
        # print(event.hardware_keycode)
        select = widget.get_selection()
        model, treeiter = select.get_selected_rows()

        if event.hardware_keycode == 36 or event.hardware_keycode == 33:
            player.play(None, self.name + '/' + model[treeiter][0])
            for i in range(1, len(treeiter)):
                player.queue(None, self.name + '/' + model[i][0])
        elif event.hardware_keycode == 24:
            for path in treeiter:
                player.queue(None, self.name + '/' + model[path][0])
        elif event.hardware_keycode == 65:
            player.toggle(None)
