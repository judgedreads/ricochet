#Ricochet

##Requirements:

  - mpd
  - python 3
  - GTK+ >3.12
  - python bindings for gtk+ 3.0 (probably packaged with python gobject)
  - [python mpd bindings](https://github.com/Mic92/python-mpd2): `pip3 install python-mpd2`
  - Pillow (for image manipulation): `pip install Pillow`


##Usage:

###Running:

  - This program assumes you are running a Linux distribution

  - The music is expected to be structured as follows:
    _MusicDir/Artist/Album/song_ e.g. mine is
    _~/Music/Artist/Album/song_

  - Cover art is expected to be called cover.jpg and located in the
    album directory to which it corresponds. 

  - A simple install script (run: `./setup install`) will put the data
    in _/opt/ricochet/_ and executables in _/usr/bin_; needs to be run
    as root. Then you can just run `ricochet` anywhere. Use `./setup
    remove` to uninstall.

  - Ricochet can also be run from the program directory: `./ricochet`

  - Settings should be configured in _~/.config/ricochet/ricochetrc_ (a
    sample config is included)

  - Make sure mpd is running before launching Ricochet

###Controls:

**Main browser:**
  - Left click on an album brings up the album window with song list,
    right click an album for context menu with queue option, middle
    click to play album. 
  - Keyboard controls: arrows/hjkl: navigate, p: play album, q: queue
    album, o/enter: open album, space: play/pause.

**Detailed album view:**
  - Double-click the songs to play, right click to queue songs.
  - Can also play selection with 'enter' or 'p', and queue selection
    with 'q'. 'space' will toggle play/pause.

**Playlist/control centre:**
  - Buttons control playback and double-clicking a song in the playlist
    will play that song.
  - Press delete on a selection of tracks to remove them from the
    playlist.
  - Space to toggle playback

##Non Goals

As a simple, album-oriented frontend to mpd, ricochet will not provide
external control/integrations such as global hotkeys or MPRIS (dbus)
support. These features are already very well implemented by other tools
such as mpc and mpdris2.
