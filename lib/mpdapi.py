import mpd
from gi.repository import GLib
from . import utils


def is_connected(client):
    if isinstance(client._wfile, mpd._NotConnected):
        return False
    else:
        return True


def connect(func):
    '''safety measure to handle connection errors before commands'''
    def new_func(*args, **kwargs):
        if not is_connected(args[0].client):
            args[0].client.connect(args[0].host, args[0].port)
        ret = func(*args, **kwargs)
        args[0].client.disconnect()
        return ret
    return new_func


class Player(object):

    def __init__(self, settings, playlist=None):

        self.client = mpd.MPDClient()
        self.host = settings['mpd_host']
        self.port = settings['mpd_port']

        try:
            self.client.connect(self.host, self.port)
        except mpd.ConnectionError:
            print("Could not connect to %s on port %d." %
                  (self.host, self.port))
            print("Check that mpd is running correctly.")
            # TODO raise a custom exception here

        VERSION = self.client.mpd_version
        print("Using MPD v%s" % VERSION)

        self.track = 1
        self.playlist = utils.parse_files(self.client.playlist())

        self.watcher = mpd.MPDClient()

    def listen(self, func):
        if not is_connected(self.watcher):
            self.watcher.connect(self.host, self.port)
        self.watcher.send_idle()

        def new_func(*args, **kwargs):
            changes = self.watcher.fetch_idle()
            if changes:
                func(*args, **kwargs)
            self.watcher.send_idle()
            return True
        GLib.io_add_watch(self.watcher, GLib.IO_IN, new_func)
        # GLib.MainLoop().run()

    @connect
    def change_playlist(self):
        '''handle reloading of the playlist widget upon changes'''

        for i, item in enumerate(self.playlist):
            if str(i) == self.client.currentsong().get('pos', '0'):
                self.track = i + 1
                if self.client.status()['state'] == 'play':
                    item['playing'] = 'playing'
                elif self.client.status()['state'] == 'pause':
                    item['playing'] = 'paused'
            else:
                item['playing'] = False

    @connect
    def toggle(self):
        '''toggle between playing and paused'''
        if self.client.status()['state'] == 'stop':
            self.client.play()
        else:
            self.client.pause()

    @connect
    def play(self, files=None):
        '''method to play now, i.e. replace playlist and play it'''
        self.client.clear()
        self.playlist = []
        self._queue(files=files)
        self.client.play()

    @connect
    def queue(self, files=None):
        '''add songs to the current playlist'''
        self._queue(files=files)

    def _queue(self, files=None):
        self.client.add(files)
        self.playlist.extend(utils.parse_files(files))

    @connect
    def remove(self, ind):
        self.client.delete(ind)
        del self.playlist[ind]

    @connect
    def select_song(self, song):
        for num, track in enumerate(self.playlist):
            if track['name'] == song:
                self.client.play(num)
                self.track = num + 1
                break

    @connect
    def stop(self, clear_playlist=True):
        '''Stop playback, optionally clear the playlist'''
        self.client.stop()
        self.track = 1
        if clear_playlist is True:
            self.playlist = []
            self.client.clear()

    @connect
    def quit(self, event=None):
        '''close connections to mpd'''
        self.client.disconnect()
        self.client.close()

    @connect
    def skip_next(self):
        self.client.next()

    @connect
    def skip_prev(self):
        self.client.previous()
