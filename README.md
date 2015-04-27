#Ricochet

##Requirements:

  - mpd or gstreamer >1.0
  - python 3
  - GTK+ >3.12
  - python bindings for gstreamer1.0 and gtk3 (gst-python and python-gobject in Arch repos, names may differ for other distros)

... I think that's all.


##Usage:

  - This program assumes you are running a Linux distribution

  - The music is expected to be structured as follows: _MusicDir/Artist/Album/song_ e.g. mine is _~/Music/Artist/Album/song_

  - Cover art is expected to be called cover.jpg and located in the album directory to which it corresponds. 

  - A simple install script (run: `./setup install`) will put the files in /opt and an executable in /usr/bin; needs to be run as root. Then you can just run `ricochet` anywhere. Use `./setup remove` to uninstall.

  - Ricochet can also be run from the program directory: `./ricochet`

  - Settings should be configured in ~/.config/ricochet/ricochetrc file (a sample is included)

  - `ricochetctl` allows control over the main program, possible commands are: `ricochetctl toggle`, `ricochetctl next`, and `ricochetctl prev`. These can be bound to keys in the preferred way.

  - If using mpd, make sure it is running before launching Ricochet


###Controls:

**Main browser:**
  - Left click on an album brings up the album window with song list, right click an album for context menu with queue option, middle click to play album. 
  - Keyboard controls: arrows: navigate, p/enter: play album, q: queue album, o: open album, space: play/pause.

**Detailed album view:**
  - double-click the songs to play, right click to queue songs.
  - Can also play selection with 'enter' or 'p', and queue selection with 'q'. 'space' will toggle play/pause.

**Control window:**
  - Buttons control playback and double-clicking a song in the playlist will play that song.


##Planned Features:

  - Incorporate album art look-up
  - More advanced gui e.g. artist filter side bar
  - Save settings such as window geometry and playlist
  - Pandora integration
  - Porting some/all code to Vala/C/C++ with a python plugin architecture


##Changelog:

v0.1:
  - Basic implementation using pygtk (gtk2) and python2
  - Crude mpd backend using mpc

v0.2:
  - Ported to GTK3 and Python3, using more advanced and feature rich widgets
  - Made the code more modular to support multiple backends and settings
  - Developed basic mpd and gstreamer backends using python bindings
  - Temporary simple install/uninstall script

v0.2.1:
  - Improved the Album window with treeview widgets
  - Added album icon for Album window
  - Replaced full image paths with relative ones
  - Fixed mpd timeout bug
  - Improved and aligned mpd and gstreamer backends

v0.2.2:
  - Added notifications to gstreamer backend (libnotify)
  - Added support for tray icon

v0.3:
  - New name! Also a new icon and general structural improvements in the code.
  - A few new control features like playlist management and keyboard control
  - Added a .desktop file

v0.3.1:
  - Bug fixes
  - Basic socket control implemented

v0.3.2:
  - Improved the settings so that they can be read from an rc file
  - Improved the socket control for hotkey/conky integration
