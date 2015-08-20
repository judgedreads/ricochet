import mpd

# TODO: need to separate all gui and backend stuff so that maintaining two
# backends is easy. Make it more like an api where the gui can query stuff like
# current artist or song or album art etc.


class Player(object):

    def __init__(self, settings, playlist=None):

        self.client = mpd.MPDClient()
        VERSION = self.client.mpd_version
        self.host = settings['mpd_host']
        self.port = settings['mpd_port']
        if playlist is None:
            playlist = []

        # catch connection errors
        try:
            self.client.connect(self.host, self.port)
        except mpd.ConnectionError:
            print("Could not connect to %s on port %d." %
                  (self.host, self.port))
            print("Check that mpd is running correctly.")

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

    # handle reloading of the playlist widget upon changes
    def change_playlist(self, widget):
        self.check_connected()

        playlist = self.client.playlist()

        for i, item in enumerate(playlist):
            song = item.split('/')[-1]
            if i == self.track - 1:
                if self.current_state == 'PLAYING':
                    song = '\u25B6 ' + song
                elif self.current_state == 'PAUSED':
                    song = '\u25AE\u25AE ' + song

    # toggle between playing and paused
    def toggle(self, widget):
        self.check_connected()
        self.client.pause()


# method to play now, i.e. replace playlist and play it
    def play(self, widget, data):
        self.check_connected()
        self.client.clear()
        self.client.add(data)
        self.client.play()


# add songs to the current playlist
    def queue(self, widget, data):
        self.check_connected()
        self.client.add(data)


# close connections to mpd
    def quit(self, widget, event):
        self.check_connected()
        self.client.close()
        self.client.disconnect()

    def skip_next(self, widget):
        self.check_connected()
        self.client.next()

    def skip_prev(self, widget):
        self.check_connected()
        self.client.previous()


# safety measure to handle connection errors before commands
    def check_connected(self):
        try:
            self.client.ping()
        except mpd.ConnectionError:
            self.client.connect(self.host, self.port)
