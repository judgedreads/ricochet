import mpd
from gi.repository import GLib


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

        self.settings = settings

        # TODO do this outside of init
        try:
            self.client.connect(self.host, self.port)
        except mpd.ConnectionError:
            print("Could not connect to %s on port %d." %
                  (self.host, self.port))
            print("Check that mpd is running correctly.")

        VERSION = self.client.mpd_version
        print("Using MPD v%s" % VERSION)

        self.track = 1

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
    def get_playlist(self):
        return self.client.playlistinfo()

    @connect
    def get_status(self):
        return self.client.status()

    @connect
    def get_play_state(self):
        return self.client.status()['state']

    @connect
    def get_currentsong(self):
        return self.client.currentsong()

    @connect
    def toggle(self):
        '''toggle between playing and paused'''
        if self.client.status()['state'] == 'stop':
            self.client.play()
        else:
            self.client.pause()

    @connect
    def play(self, songs):
        '''method to play now, i.e. replace playlist and play it'''
        self.client.clear()
        self._queue(songs)
        self.client.play()

    @connect
    def queue(self, songs):
        '''add songs to the current playlist'''
        self._queue(songs)

    def _queue(self, songs):
        for s in songs:
            self.client.add(s['file'])

    @connect
    def remove(self, songid):
        self.client.deleteid(songid)

    @connect
    def select_song(self, songid):
        self.client.playid(songid)

    @connect
    def stop(self, clear_playlist=True):
        '''Stop playback, optionally clear the playlist'''
        self.client.stop()
        self.track = 1
        if clear_playlist is True:
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

    @connect
    def get_lib(self):
        return self.client.listallinfo()

    def iterlib(self):
        lib = self.get_lib()
        for item in lib:
            if 'directory' in item or 'playlist' in item:
                continue
            yield item

    @connect
    def get_songs_for_album(self, tags):
        songs = self.client.find('album', tags['album'],
                                 'albumartist', tags['artist'],
                                 'date', tags['date'],
                                 'disc', tags['disc'])
        if not songs:
            songs = self.client.find('album', tags['album'],
                                     'artist', tags['artist'],
                                     'date', tags['date'],
                                     'disc', tags['disc'])
        if songs:
            return songs
