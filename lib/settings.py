import os

# set up defaults
settings = {
    'backend': 'gstreamer',
    'mpd_host': 'localhost',
    'mpd_port': 6600,
    'music_dir': '%s/Music/' % os.environ['HOME'],
    'grid_icon_size': 128,
    'detail_icon_size': 256,
    'notifications': 'True',
    'system_tray': 'False'
}

home = os.environ['HOME']
path = home + '/.config/ricochet/ricochetrc'

try:
    f = open(path, 'r')
    for line in f:
        if line[0] != '#' and line != '\n':
            key = line.strip().split('=')[0]
            value = line.strip().split('=')[1]
            if value:
                settings[key] = value

    f.close()
except FileNotFoundError:
    print('No ricochetrc file - using defaults.')
