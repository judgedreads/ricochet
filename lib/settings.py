import os
import json


def get_settings():

    path = '%s/.config/ricochet/settings.json' % os.environ['HOME']

    # set up defaults
    settings = {
        'mpd_host': 'localhost',
        'mpd_port': '6600',
        'music_dir': '%s/Music/' % os.environ['HOME'],
        'grid_icon_size': 150,
        'detail_icon_size': 300,
        'notifications': 'True',
        'cache': '%s/.cache/ricochet' % os.environ['HOME'],
        'cover_names': ["cover.jpg", "cover.png", "front.jpg", "front.png"]
    }

    if os.path.isfile(path):
        with open(path) as f:
            overrides = json.load(f)
    else:
        print('No file found at %s - using defaults.' % path)
    settings.update(overrides)

    settings['music_dir'] = os.path.normpath(settings['music_dir'])

    return settings
