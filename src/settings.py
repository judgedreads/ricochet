import os

# set up defaults
settings = {'backend': 'gstreamer', 'mpd_host': 'localhost', 'mpd_port': 6600, 'music_dir': '/home/judgedreads/Music/',
            'grid_icon_size': 128, 'detail_icon_size': 256, 'notifications': 'True', 'system_tray': 'True'}

home = os.environ['HOME']
path = home + '/.config/ricochet/ricochetrc'

try:
    f = open(path, 'r')
    print('Reading ricochetrc settings.')
    for line in f:
        if line[0] != '#' and line != '\n':
            key = line.strip().split('=')[0]
            value = line.strip().split('=')[1]
            settings[key] = value

    f.close()
except FileNotFoundError:
    print('No ricochetrc file - using defaults.')
