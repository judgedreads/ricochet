import mpd


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

        VERSION = self.client.mpd_version
        print("Using MPD v%s" % VERSION)

    def get_info(self, widget, data):
        if data == "pos":
            self.check_connected()
            pos = self.client.status()['elapsed']
            pos = float(pos)
            pos_min = int(pos / 60)
            pos_sec = int(pos) % 60
            dur = self.client.currentsong()['time']
            dur = float(dur)
            dur_min = int(dur / 60)
            dur_sec = int(dur) % 60
            return pos_min, pos_sec, dur_min, dur_sec
        elif data == "song":
            song = self.client.currentsong()['title']
            return song
        elif data == "album":
            album = self.client.currentsong()['album']
            return album
        elif data == "artist":
            artist = self.client.currentsong()['artist']
            return artist

    def change_playlist(self, widget=None):
        '''handle reloading of the playlist widget upon changes'''
        self.check_connected()

        self.playlist = self.client.playlist()

        for i, item in enumerate(self.playlist):
            segs = item.split('/')[-1].split('.')[:-1]
            song = '.'.join(segs)
            self.track = i + 1
            if str(i) == self.client.currentsong()['pos']:
                print(self.client.status())
                if self.client.status()['state'] == 'play':
                    song = '\u25B6 ' + song
                elif self.client.status()['state'] == 'pause':
                    song = '\u25AE\u25AE ' + song
            yield song

    def toggle(self, widget=None):
        '''toggle between playing and paused'''
        self.check_connected()
        self.client.pause()

    def play(self, widget=None, files=None):
        '''method to play now, i.e. replace playlist and play it'''
        self.check_connected()
        self.client.clear()
        self.client.add(files)
        self.client.play()

    def queue(self, widget=None, files=None):
        '''add songs to the current playlist'''
        self.check_connected()
        self.client.add(files)

    def quit(self, widget=None, event=None):
        '''close connections to mpd'''
        self.check_connected()
        self.client.close()
        self.client.disconnect()

    def skip_next(self, widget=None):
        self.check_connected()
        self.client.next()

    def skip_prev(self, widget=None):
        self.check_connected()
        self.client.previous()

    def check_connected(self):
        '''safety measure to handle connection errors before commands'''
        try:
            self.client.ping()
        except mpd.ConnectionError:
            self.client.connect(self.host, self.port)
