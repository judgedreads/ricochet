from gi.repository import Gtk, GdkPixbuf


class Control(Gtk.Box):

    '''The main control window for the playlist and playback controls'''

    def __init__(self, player, browser, server):
        self.player = player
        self.server = server
        self.brow = browser

        self.player.image = Gtk.Image()
        self.player.pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
            "/opt/ricochet/images/music_note.png", 256, 256)
        self.player.image.set_from_pixbuf(self.player.pixbuf)
        self.player.image.show()

        Gtk.Box.__init__(self, orientation=1)
        self.pack_start(self.player.image, False, False, 0)

        self.box = Gtk.Box()
        self.button1 = Gtk.Button(label="Prev")
        self.button2 = Gtk.Button(label="Next")
        self.button3 = Gtk.Button(label="Play/Pause")
        self.button1.connect("clicked", self.player.skip_prev)
        self.button2.connect("clicked", self.player.skip_next)
        self.button3.connect("clicked", self.player.toggle)
        self.box.pack_start(self.button1, True, True, 0)
        self.box.pack_start(self.button3, True, True, 0)
        self.box.pack_start(self.button2, True, True, 0)

        self.pack_start(self.box, False, False, 0)

        self.scroll = Gtk.ScrolledWindow()
        self.scroll.set_border_width(0)
        self.scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.pack_start(self.scroll, True, True, 0)

        self.scroll.add(self.player.treeview)
