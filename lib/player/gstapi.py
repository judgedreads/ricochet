from gi.repository import Gst
import os
from .. import utils


class Player(object):

    def __init__(self, settings, playlist=None):
        VERSION = '.'.join(map(str, Gst.version()[0:3]))
        print("Using Gstreamer v%s" % VERSION)
        # Optionally load a playlist on init
        if playlist is None:
            playlist = []
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
        self.playbin = Gst.ElementFactory.make('playbin', None)
        self.pipeline.add(self.playbin)

    def listen(self, func):
        def new_func(*args, **kwargs):
            self.skip_next(gapless=True)
            func(*args, **kwargs)
            return True
        # self.bus.connect('message::eos', new_func)
        # might still be worth using eos message to handle reaching the end of
        # the playlist, some other messages might be worthwhile too.

        # gapless playback - needs to pass gapless=True to skip_next or make
        # separate function
        self.playbin.connect('about-to-finish', new_func)

    def change_playlist(self, widget=None):
        '''handle playlist changes'''
        for i, item in enumerate(self.playlist):
            if i == self.track - 1:
                if self.current_state == 'PLAYING':
                    item['playing'] = 'playing'
                elif self.current_state == 'PAUSED':
                    item['playing'] = 'paused'
            else:
                item['playing'] = False

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
            self.playbin.set_property('uri', 'file://'+self.playlist[0]['path'])
            self.pipeline.set_state(Gst.State.PLAYING)
            self.current_state = "PLAYING"

    def play(self, widget=None, files=None):
        '''method to play now, i.e. replace playlist and play it'''

        self.stop()
        self.queue(files=files)
        self.toggle()

    def xqueue(self, widget=None, files=None):
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

    def queue(self, widget=None, files=None):
        self.playlist.extend(utils.parse_files(files))

    def remove(self, ind):
        del self.playlist[ind]

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

    def skip_next(self, widget=None, gapless=False):
        if gapless is False:
            self.pipeline.set_state(Gst.State.NULL)
        i = self.track
        if i < len(self.playlist):
            self.playbin.set_property('uri', 'file://'+self.playlist[i]['path'])
            self.pipeline.set_state(Gst.State.PLAYING)
            self.current_state = "PLAYING"
            self.track += 1
        else:
            self.stop(clear_playlist=False)

    def skip_prev(self, widget=None):
        # TODO: CD style skip (make optional)
        i = self.track - 1
        if i <= 0:
            return
        self.pipeline.set_state(Gst.State.NULL)
        self.playbin.set_property('uri', 'file://'+self.playlist[i-1]['path'])
        self.pipeline.set_state(Gst.State.PLAYING)
        self.current_state = "PLAYING"
        self.track -= 1
