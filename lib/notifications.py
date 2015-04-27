from gi.repository import Notify, GdkPixbuf


class NullNotifier(object):
    '''Dummy notifier for when notifications are disabled'''

    def __init__(self, playlist):
        self.playlist = playlist

    def notify(self, i):
        pass


class Notifier(object):
    '''Class to handle all notifications'''

    def __init__(self, playlist):
        self.playlist = playlist

    def notify(self, i):
        print(self.playlist[i])
        song = self.playlist[i].split('/')[-1]
        album = self.playlist[i].split('/')[-2]
        artist = self.playlist[i].split('/')[-3]
        cover = "/home/judgedreads/Music/" + \
            artist + '/' + album + '/' + 'cover.jpg'

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
