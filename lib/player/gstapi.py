from gi.repository import Gst
import os


class Player(object):

    def __init__(self, settings, playlist=None):
        '''Optionally load a playlist on init'''
        VERSION = '.'.join(map(str, Gst.version()[0:3]))
        if playlist is None:
            playlist = []
        print("Using Gstreamer v%s" % VERSION)
        self.settings = settings
        self.MUSIC_DIR = settings['music_dir']

        # keep track of playlist and current track
        self.playlist = playlist
        self.track = 1
        self.current_state = "STOPPED"

        # set up gstreamer elements
        self.pipeline = Gst.Pipeline()
        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        # about-to-finish signal for gapless
        self.playbin = Gst.ElementFactory.make('playbin', None)
        self.pipeline.add(self.playbin)

    def get_info(self, widget, data):
        i = self.track
        if data == "pos":
            pos = self.pipeline.query_position(Gst.Format.TIME)[1]
            pos = round(pos / 1000000000)
            pos_min = int(pos / 60)
            pos_sec = int(pos) % 60
            dur = self.pipeline.query_duration(Gst.Format.TIME)[1]
            dur = round(dur / 1000000000)
            dur_min = int(dur / 60)
            dur_sec = int(dur) % 60
            return pos_min, pos_sec, dur_min, dur_sec
        elif data == "song":
            song = self.playlist[i - 1].split('/')[-1]
            return song
        elif data == "album":
            album = self.playlist[i - 1].split('/')[-2]
            return album
        elif data == "artist":
            artist = self.playlist[i - 1].split('/')[-3]
            return artist

    def change_playlist(self, widget=None):
        '''handle playlist changes'''
        for i, item in enumerate(self.playlist):
            segs = item.split('/')[-1].split('.')[:-1]
            song = '.'.join(segs)
            if i == self.track - 1:
                if self.current_state == 'PLAYING':
                    song = '\u25B6 ' + song
                elif self.current_state == 'PAUSED':
                    song = '\u25AE\u25AE ' + song
            yield song

    def toggle(self, widget=None):
        '''toggle play state'''
        if self.current_state == "PAUSED":
            self.pipeline.set_state(Gst.State.PLAYING)
            self.current_state = "PLAYING"
        elif self.current_state == "PLAYING":
            self.pipeline.set_state(Gst.State.PAUSED)
            self.current_state = "PAUSED"
        elif self.current_state == "STOPPED":
            if self.playlist == []:
                return
            self.playbin.set_property('uri', self.playlist[0])
            self.pipeline.set_state(Gst.State.PLAYING)
            self.current_state = "PLAYING"
        print(self.pipeline.get_state(Gst.State.NULL))

    def play(self, widget=None, files=None):
        '''method to play now, i.e. replace playlist and play it'''

        self.stop()
        self.queue(files=files)
        self.toggle()

    def queue(self, widget=None, files=None):
        '''add music to current playlist'''

        if os.path.isdir(os.path.join(self.MUSIC_DIR, files)):
            discs = []
            for item in os.listdir(os.path.join(self.MUSIC_DIR, files)):
                if item.startswith('.'):
                    continue
                if os.path.isdir(os.path.join(self.MUSIC_DIR, files, item)):
                    discs.append(os.path.join(files, item))
            if discs == []:
                discs.append(files)
            songs = []
            discs.sort()
            for disc in discs:
                songs = os.listdir(os.path.join(self.MUSIC_DIR, disc))
                songs.sort()
                for song in songs:
                    # handle file types: wma doesn't work with gst for some
                    # reason
                    if song.endswith(('mp3', 'ogg', 'm4a',
                                      'mp4', 'flac', 'mpc')):
                        temp = "file://%s" % os.path.join(
                            self.MUSIC_DIR, disc, song)
                        self.playlist.append(temp)
        else:
            song = "file://%s/%s" % (self.MUSIC_DIR, files)
            self.playlist.append(song)

        self.change_playlist()

    def select_song(self, song):
        '''
        Temporary function for handling selecting song from playlist. May become
        permanent or refactored.
        '''
        for num, name in enumerate(self.player.playlist):
            name = os.path.basename(name)
            if name.split('.')[0] == song:
                self.pipeline.set_state(Gst.State.NULL)
                self.playbin.set_property('uri', self.player.playlist[num])
                self.track = num + 1
                break
        self.pipeline.set_state(Gst.State.PLAYING)
        self.current_state = "PLAYING"

    def quit(self, widget, event):
        self.pipeline.set_state(Gst.State.NULL)

    def stop(self, widget=None, clear_playlist=True):
        '''Stop playback, optionally clear the playlist'''
        self.pipeline.set_state(Gst.State.NULL)
        self.current_state = 'STOPPED'
        self.track = 1
        if clear_playlist is True:
            self.playlist = []
        print(self.pipeline.get_state(Gst.State.NULL))

    def skip_next(self, widget=None):
        self.pipeline.set_state(Gst.State.NULL)
        i = self.track
        if i < len(self.playlist):
            self.playbin.set_property('uri', self.playlist[i])
            self.pipeline.set_state(Gst.State.PLAYING)
            self.current_state = "PLAYING"
            self.track += 1
        else:
            self.stop(clear_playlist=False)

    def skip_prev(self, widget=None):
        i = self.track - 1
        if i <= 0:
            return
        self.pipeline.set_state(Gst.State.NULL)
        self.playbin.set_property('uri', self.playlist[i - 1])
        self.pipeline.set_state(Gst.State.PLAYING)
        self.current_state = "PLAYING"
        self.track -= 1
