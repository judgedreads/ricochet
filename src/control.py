# The main control window for the playlist and playback controls
class Control(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self)
        self.set_title("Ricochet v0.3")
        self.set_icon_from_file("images/ricochet.png")
        self.connect('delete-event', self.quit)
        self.set_default_size(300, 400)

        self.box = Gtk.Box()
        self.button1 = Gtk.Button(label="Prev")
        self.button2 = Gtk.Button(label="Next")
        self.button3 = Gtk.Button(label="Play/Pause")
        self.button1.connect("clicked", browser.player.skip_prev)
        self.button2.connect("clicked", browser.player.skip_next)
        self.button3.connect("clicked", browser.player.toggle)
        self.box.pack_start(self.button1, True, True, 0)
        self.box.pack_start(self.button3, True, True, 0)
        self.box.pack_start(self.button2, True, True, 0)

        self.vbox = Gtk.Box(orientation=1)
        self.add(self.vbox)
        self.vbox.pack_start(self.box, False, False, 0)

        self.browser_button = Gtk.Button(label="Cover Browser")
        self.browser_button.connect("clicked", self.show_brow)
        self.vbox.pack_start(self.browser_button, False, False, 0)

        self.scroll = Gtk.ScrolledWindow()
        self.scroll.set_border_width(0)
        self.scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.vbox.pack_start(self.scroll, True, True, 0)

        self.scroll.add(browser.player.treeview)


# close the backend and browser and then Gtk
    def quit(self, widget, event):
        server.close()
        brow.quit(None, None)
        browser.player.quit(None, None)
        print("Next time, punk.")
        Gtk.main_quit()

    def show_brow(self, widget):
        brow.show()
