Ricochet
========

Requirements:
-------------
  - mpd or gstreamer >1.0
  - python 3
  - gtk3
  - python bindings for gstreamer1.0 and gtk3 (gst-python and python-gobject in Arch repos, names may differ for other distros)

... I think that's all.


Usage:
------

  - There is partial configuration in the settings.py file

  - Just run src/ricochet.py from main ricochet directory, make sure executable bit is set (chmod +x ricochet.py)

  - make sure mpd is running (unless using gstreamer)

  - A simple install script (run: ./setup install) will put the files in /opt and an executable in /usr/bin; needs to be run as root. Then you can just run 'ricochet' anywhere. use ./setup remove to uninstall.


Controls:
---------

Main browser: 
  - Left click on an album brings up the album window with song list, right click an album for context menu with queue option, middle click to play album. 
  - Keyboard controls: arrows: navigate, p/enter: play album, q: queue album, o: open album, space: play/pause.

Detailed album view:
  - double-click the songs to play, right click to queue songs.
  - Can also play selection with 'enter' or 'p', and queue selection with 'q'. 'space' will toggle play/pause.

Control window:
  - Buttons control playback and double-clicking a song in the playlist will play that song.


Some assumptions about this program:
------------------------------------

  - This is a work in progress and a learning exercise

  - This is not a finished application nor is it under full-time maintainance.

  - This program assumes you are running a Linux distribution

  - You may need to change the top line of the python file (cover-browser) depending on your distribution (e.g. /usr/bin/env python) but you can always run it with python: python ricochet.py

  - Some assumptions about the structure of the music collection is made, again because this was a gui exercise initially (using a database would be more portable). The music is expected to be structured as follows: Music_Dir/Artist/Album/song.ext e.g. mine is ~/Music/Artist/Album/song.ext.

  - Cover art is expected to be called cover.jpg and located in the album directory to which it corresponds. 


Planned Features:
-----------------

  - Incorporate album art look-up (art look up has been written but not yet implemented.)
  - More advanced gui with an artist filter side bar?
  - Improve the capabilities of the backends
  - More playlist control
  - Save settings such as window geometry and playlist in config directory
  - Pandora integration
  - Porting some/all code to C/C++ with a plugin architecture


Changelog:
----------

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

If you have any advice I would appreciate it :) and feature requests are
welcome (although no promises about me implementing them). I'd love to
know if anyone does anything cool with it too - contact: 
pearce@millerdedmon.com


Enjoy!

  --judgedreads