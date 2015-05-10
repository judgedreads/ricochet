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
        icon = '/opt/ricochet/images/ricochet.png'

        title = ''.join(song.split('.')[0:-1])
        body = 'by %s\non %s' % (artist, album)

        Playing = Notify.Notification.new(title, body, icon)
        Playing.add_action('action', 'Next', self.notif_skip, 'next')
        image = GdkPixbuf.Pixbuf.new_from_file(cover)
        Playing.set_image_from_pixbuf(image)
        Playing.show()

        # TODO: make dict for each song (probably in browser), where key should
        # be readable name and val should be dict of info containing file path,
        # album, cover art, artist, etc. Then can put name on treeview and then
        # pass corresponding dict through to everything. Need to have some
        # cleanup methods to get rid of this stuff when it's done.

    def notif_skip(self, notif, action, data):
        if data == 'next':
            self.skip_next(None)
        elif data == 'prev':
            self.skip_prev(None)
