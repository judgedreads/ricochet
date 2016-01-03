import os


def get_settings():

    path = '%s/.config/ricochet/ricochetrc' % os.environ['HOME']

    # set up defaults
    settings = {
        'mpd_host': 'localhost',
        'mpd_port': '6600',
        'music_dir': '%s/Music/' % os.environ['HOME'],
        'grid_icon_size': 128,
        'detail_icon_size': 256,
        'notifications': 'True',
    }

    if os.path.isfile(path):
        f = open(path, 'r')
        for line in f:
            if line[0] != '#' and line != '\n':
                key = line.strip().split('=')[0]
                value = line.strip().split('=')[1]
                if value:
                    settings[key] = value
        f.close()
    else:
        print('No file found at %s - using defaults.' % path)

    settings['grid_icon_size'] = int(settings['grid_icon_size'])
    settings['detail_icon_size'] = int(settings['detail_icon_size'])
    settings['music_dir'] = os.path.normpath(settings['music_dir'])

    return settings
