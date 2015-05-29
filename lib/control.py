from gi.repository import Gtk, GdkPixbuf


class Control(Gtk.Box):

    '''The main control window for the playlist and playback controls'''

    def __init__(self, player, browser, server):
        self.player = player
        self.server = server
        self.brow = browser

        self.player.image = Gtk.Image()
        self.player.pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
            "/opt/ricochet/images/default_album.jpg", 256, 256)
        self.player.image.set_from_pixbuf(self.player.pixbuf)
        self.player.image.show()
        # FIXME: the multi disc albums look in the directory containing
        # the songs rather than the toplevel album directory.

        Gtk.Box.__init__(self, orientation=1)
        self.pack_start(self.player.image, False, False, 0)

        button_box = Gtk.Box()
        button1 = Gtk.Button()
        pixbuf1 = GdkPixbuf.Pixbuf.new_from_file_at_size(
            'images/prev.png', 20, 20)
        image1 = Gtk.Image().new_from_pixbuf(pixbuf1)
        button1.add(image1)
        button2 = Gtk.Button()
        pixbuf2 = GdkPixbuf.Pixbuf.new_from_file_at_size(
            'images/next.png', 20, 20)
        image2 = Gtk.Image().new_from_pixbuf(pixbuf2)
        button2.add(image2)
        button3 = Gtk.Button()
        pixbuf3 = GdkPixbuf.Pixbuf.new_from_file_at_size(
            'images/play.png', 20, 20)
        image3 = Gtk.Image().new_from_pixbuf(pixbuf3)
        button3.add(image3)
        button4 = Gtk.Button()
        pixbuf4 = GdkPixbuf.Pixbuf.new_from_file_at_size(
            'images/stop.png', 20, 20)
        image4 = Gtk.Image().new_from_pixbuf(pixbuf4)
        button4.add(image4)
        button1.connect("clicked", self.player.skip_prev)
        button2.connect("clicked", self.player.skip_next)
        button3.connect("clicked", self.toggle, button3)
        button4.connect("clicked", self.player.stop)
        button_box.pack_start(button1, True, True, 0)
        button_box.pack_start(button3, True, True, 0)
        button_box.pack_start(button4, True, True, 0)
        button_box.pack_start(button2, True, True, 0)

        self.pack_start(button_box, False, False, 0)

        scroll = Gtk.ScrolledWindow()
        scroll.set_border_width(0)
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.pack_start(scroll, True, True, 0)

        scroll.add(self.player.treeview)
        self.show_all()

    def toggle(self, widget, button):
        self.player.toggle(None)
