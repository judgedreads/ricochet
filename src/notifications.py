from gi.repository import Notify

# TODO need to make everything more modular then set it all up
# from main exe. Pass the backend class around to connect the
# callbacks e.g. notif_skip takes gst player as arg.

class NullNotifier(object):
    def send(self):
        pass


class Notifier(object):
        i = index
        print(self.playlist[i])
        song = self.playlist[i].split('/')[-1]
        album = self.playlist[i].split('/')[-2]
        artist = self.playlist[i].split('/')[-3]
        cover = "/home/judgedreads/Music/" + \
            artist + '/' + album + '/' + 'cover.jpg'

# for actions to work, we need to run a separate Gtk.main()
# but this interferes with closing (2 main methods running).
# Might need to completely separate notification framework.
# also try using GtkApplication class to init stuff like
# Notify.init and connect all windows to this, this seems to
# be the 'proper' way of doing things. Also, the notify docs
# are here: https://developer.gnome.org/libnotify/0.7/ not 
# with Gtk docs.
        #Notify.init("Ricochet")
        Playing = Notify.Notification.new(song, artist, cover)
        Playing.add_action('action', 'Next', self.notif_skip, 'next')
        image = GdkPixbuf.Pixbuf.new_from_file(cover)
        Playing.set_image_from_pixbuf(image)
        Playing.show()

    def notif_skip(self, notif, action, data):
        if data == 'next':
            self.skip_next(None)
        elif data == 'prev':
            self.skip_prev(None)
