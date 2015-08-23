import mpd
from gi.repository import GLib


def idle(func):
    def new_func(*args, **kwargs):
        try:
            ret = func(*args, **kwargs)
        except mpd.PendingCommandError:
            changes = args[0].client.fetch_idle()
            print(changes)
            ret = func(*args, **kwargs)
        finally:
            args[0].client.send_idle()
            return ret
    return new_func


class Player(object):

    def __init__(self, settings, playlist=None):

        self.client = mpd.MPDClient()
        self.host = settings['mpd_host']
        self.port = settings['mpd_port']
        if playlist is None:
            playlist = []
        self.playlist = playlist
        self.track = 1

        # catch connection errors
        try:
            self.client.connect(self.host, self.port)
        except mpd.ConnectionError:
            print("Could not connect to %s on port %d." %
                  (self.host, self.port))
            print("Check that mpd is running correctly.")
            # TODO: put this in a function and do a sys.exit

        VERSION = self.client.mpd_version
        print("Using MPD v%s" % VERSION)

        self.playlist = self.client.playlist()

    def event_callback(self, *args, **kwargs):
        '''
        This function is not implemented by default so should be done so by
        whatever ends up using this. This function is connected to the mpd
        client via a GLib IO watcher, returning True will keep the IO watcher
        connected, returning False or None will remove the watcher.
        '''
        # need to ignore most stuff here, mostly just want to update playlist
        # and notify when a song changes, the tricky thing is not notifying when
        # toggling playback. This check could be implemented in the
        # update/notify stage to see if the song has changed.
        # This will need to be implemented by control.
        raise NotImplementedError

    def _event_callback(self, *args, **kwargs):
        changes = self.client.fetch_idle()
        print(changes)
        # yeah I think decorators are the way to go,
        # should fetch_idle before function then send_idle after

    def wait(self):
        # make this into a decorator for use with most methods?
        # or maybe decorate methods so they try to fetch_idle, then
        # run, then call wait when they are done.
        self.check_connected()
        self.client.send_idle()
        GLib.io_add_watch(self.client, GLib.IO_IN, self.event_callback)
        # GLib.MainLoop().run()

    @idle
    def change_playlist(self, widget=None):
        '''handle reloading of the playlist widget upon changes'''

        # TODO: should make playlist a list of dicts
        # keys can be: file_path, artist, album, track_num, title, etc
        # this should simplify a lot of things and reduce the need for
        # parsing

        self.playlist = []
        for i, item in enumerate(self.client.playlist()):
            segs = item.split('/')[-1].split('.')[:-1]
            song = '.'.join(segs)
            print(song)
            if str(i) == self.client.currentsong()['pos']:
                self.track = i + 1
                if self.client.status()['state'] == 'play':
                    song = '\u25B6 ' + song
                elif self.client.status()['state'] == 'pause':
                    song = '\u25AE\u25AE ' + song
            self.playlist.append(song)

    @idle
    def toggle(self, widget=None):
        '''toggle between playing and paused'''
        self.client.pause()

    @idle
    def play(self, widget=None, files=None):
        '''method to play now, i.e. replace playlist and play it'''
        self.client.clear()
        self.client.add(files)
        self.client.play()

    @idle
    def queue(self, widget=None, files=None):
        '''add songs to the current playlist'''
        self.client.add(files)

    @idle
    def quit(self, widget=None, event=None):
        '''close connections to mpd'''
        self.client.close()
        self.client.disconnect()

    @idle
    def skip_next(self, widget=None):
        self.client.next()

    @idle
    def skip_prev(self, widget=None):
        self.client.previous()

    def check_connected(self):
        '''safety measure to handle connection errors before commands'''
        try:
            self.client.ping()
        except mpd.ConnectionError:
            self.client.connect(self.host, self.port)
