#!/usr/bin/env python

from setuptools import setup

with open('VERSION') as f:
    ver = f.read().strip()

config = {
    'description': 'An album oriented MPD client',
    'author': 'judgedreads',
    'url': 'github.com/judgedreads/ricochet',
    'version': ver,
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
