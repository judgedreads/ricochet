from gi.repository import Gtk, GdkPixbuf


class Control(Gtk.Box):

    '''The side panel for the playlist and playback controls'''

    def __init__(self, player, server):
        self.player = player
        self.server = server

        self.player.image = Gtk.Image()
        self.player.pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
            "/opt/ricochet/images/default_album.jpg", 256, 256)
        self.player.image.set_from_pixbuf(self.player.pixbuf)
        self.player.image.show()
        # FIXME: the multi disc albums look in the directory containing
        # the songs rather than the toplevel album directory.

        Gtk.Box.__init__(self, orientation=1)
        self.pack_start(self.player.image, False, False, 0)

        buttons = [
            ('prev', self.player.skip_prev),
            ('play', self.player.toggle),
            ('stop', self.player.stop),
            ('next', self.player.skip_next)
        ]
        button_box = Gtk.Box()
        for name, method in buttons:
            button = Gtk.Button()
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
                '/opt/ricochet/images/%s.png' % name, 20, 20)
            image = Gtk.Image().new_from_pixbuf(pixbuf)
            button.add(image)
            button.connect("clicked", method)
            button_box.pack_start(button, True, True, 0)
        self.pack_start(button_box, False, False, 0)

        scroll = Gtk.ScrolledWindow()
        scroll.set_border_width(0)
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.pack_start(scroll, True, True, 0)

        scroll.add(self.player.treeview)
        self.show_all()
