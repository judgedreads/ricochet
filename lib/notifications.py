from gi.repository import Notify, GdkPixbuf


class NullNotifier(object):

    '''Dummy notifier for when notifications are disabled'''

    def __init__(self, player):
        self.player = player

    def notify(self, i):
        pass


class Notifier(object):

    '''Class to handle all notifications'''

    def __init__(self, player):
        self.notif = Notify.Notification()
        self.notif.set_category('x-gnome.music')
        self.notif.set_timeout(3)
        self.player = player

    def notify(self, i):
        print(self.player.playlist[i])
        song = self.player.playlist[i].split('/')[-1]
        album = self.player.playlist[i].split('/')[-2]
        artist = self.player.playlist[i].split('/')[-3]
        cover = "/home/judgedreads/Music/" + \
            artist + '/' + album + '/' + 'cover.jpg'
        icon = '/opt/ricochet/images/ricochet.png'

        title = ''.join(song.split('.')[0:-1])
        body = 'by %s\non %s' % (artist, album)

        self.notif.clear_actions()
        self.notif.add_action('action', 'Next', self.notif_skip, None)
        self.notif.update(title, body, icon)
        image = GdkPixbuf.Pixbuf.new_from_file(cover)
        self.notif.set_image_from_pixbuf(image)
        self.notif.show()

        # TODO: make dict for each song (probably in browser), where key should
        # be readable name and val should be dict of info containing file path,
        # album, cover art, artist, etc. Then can put name on treeview and then
        # pass corresponding dict through to everything. Need to have some
        # cleanup methods to get rid of this stuff when it's done.

    def notif_skip(self, notification, action, data, ignore=None):
        notification.close()
        self.player.skip_next(None)
