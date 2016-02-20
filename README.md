#Ricochet

##Requirements:

  - mpd
  - python 3
  - GTK+ >3.12
  - libnotify (optional)
  - Python dependencies can be installed with package manager or pip.
    Any that are missing will be installed with make.
    - pygobject
    - [python-mpd2](https://github.com/Mic92/python-mpd2)
    - Pillow
    - requests


##Running:

  - This program assumes you are running a Linux distribution

  - install/uninstall with make

  - Make sure mpd is running before launching Ricochet

##Settings

Settings should be configured in _~/.config/ricochet/settings.json_ or
_/etc/ricochet/settings.json_ (defaults are installed to the latter).
Most settings should be self-explanatory.

**cover_names**  
A list of paths (relative to the song files) that ricochet will check
for cover images. Albums are expected to be grouped toogether as the
first track's cover will be used for the others.

**symbolic_icons**  
Specifies whether to use symbolic alternatives in the icon theme for the
buttons etc.

**notifications**  
Whether or not to use libnotify to send a notification when the song
changes, with actions to skip back and forwards.


##Controls:

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
