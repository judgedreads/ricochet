#!/usr/bin/env python

from distutils.core import setup

config = {
    'description': 'An album oriented MPD client',
    'author': 'judgedreads',
    'url': 'github.com/judgedreads/ricochet',
    'version': '0.3.6',
    'install_requires': ['python-mpd2', 'Pillow', 'pygobject', 'requests'],
    'packages': ['ricochet'],
    'scripts': ['bin/ricochet'],
    'name': 'ricochet',
    'data_files': [('/usr/share/applications', ['misc/ricochet.desktop']),
                   ('/etc/ricochet/settings.json', ['misc/settings.json']),
                   ('/usr/share/ricochet', ['images/default_album.png']),
                   ('/usr/share/icons/hicolor/512x512/apps',
                    ['images/ricochet.png'])]
}

setup(**config)
