#!/usr/bin/env python

from setuptools import setup

config = {
    'description': 'An album oriented MPD client',
    'author': 'judgedreads',
    'url': 'github.com/judgedreads/ricochet',
    'version': '0.3.6',
    'license': 'GPLv3',
    'install_requires': [
        'python-mpd2',
        'Pillow',
        'pygobject',
        'requests',
    ],
    'packages': ['ricochet'],
    'scripts': ['bin/ricochet'],
    'name': 'ricochet',
}

setup(**config)
