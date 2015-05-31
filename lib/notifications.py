from gi.repository import Notify, GdkPixbuf
import os


class Notifier(object):

    '''Class to handle all notifications'''

    def __init__(self, player):
        self.notif = Notify.Notification()
        self.notif.set_category('x-gnome.music')
        self.notif.set_timeout(3)
        self.player = player
        self.MUSIC_DIR = player.MUSIC_DIR

    def notify(self, i):
        song = self.player.playlist[i].split('/')[-1]
        album = self.player.playlist[i].split('/')[-2]
        artist = self.player.playlist[i].split('/')[-3]
        cover = self.MUSIC_DIR + artist + '/' + album + '/' + 'cover.jpg'
        if not os.path.exists(cover):
            cover = '/opt/ricochet/images/default_album.jpg'
        icon = '/opt/ricochet/images/ricochet.png'

        title = ''.join(song.split('.')[0:-1])
        body = 'by %s\non %s' % (artist, album)

        self.notif.clear_actions()
        self.notif.add_action('action', 'Next', self.notif_skip, None)
        self.notif.update(title, body, icon)
        image = GdkPixbuf.Pixbuf.new_from_file(cover)
        self.notif.set_image_from_pixbuf(image)
        self.notif.show()

    def notif_skip(self, notification, action, data, ignore=None):
        notification.close()
        self.player.skip_next(None)
