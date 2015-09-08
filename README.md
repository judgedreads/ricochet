#Ricochet

##Requirements:

  - mpd or gstreamer >1.0
  - python 3
  - GTK+ >3.12
  - python bindings for gstreamer1.0 and gtk3 (gst-python and
    python-gobject in Arch repos, names may differ for other distros)
  - [python mpd bindings](https://github.com/Mic92/python-mpd2): `pip3 install python-mpd2`


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

  - If using mpd, make sure it is running before launching Ricochet

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

**ricochetctl:**

  `ricochetctl` can be used to send commands to ricochet externally, the
  commands are:
  - `ricochetctl toggle` to toggle play/pause
  - `ricochetctl next` to skip to the next track
  - `ricochetctl prev` to skip to the previous track

These are intended to be bound to global keys using a WM/DE. If using
mpd, other programs can be used to control playback as well as ricochet.
