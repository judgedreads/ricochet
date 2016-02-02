#!/usr/bin/env python3

import requests
from io import BytesIO
from PIL import Image
import multiprocessing as mp
import os


def _get_image_url(html):
    for line in html.split('\n'):
        if 'class="artist_pic"' not in line:
            continue
        for item in line.split():
            if 'src' in item:
                url = item.split('"')[1]
                if url:
                    return url
    return None


def fetch_album_art(name, musicdir):
    # use notifications here or at least log stuff
    artist, album = name.split('/')
    artist = artist.replace(' ', '_')
    print(artist)
    try:
        r = requests.get(
            'http://musicdatabase.co/artist/%s/album/%s' % (artist, album)
        )
        print(r.status_code)
    except requests.exceptions.RequestException as e:
        print(e)
        return 1
    image_url = _get_image_url(r.text)
    if image_url is None:
        return 1
    ext = image_url.split('.')[-1]
    path = '%s/%s/cover.%s' % (musicdir, name, ext)
    print(path)
    try:
        r = requests.get(image_url)
    except requests.exceptions.RequestException as e:
        print(e)
        return 1
    im = Image.open(BytesIO(r.content))
    path = '%s/%s/cover.%s' % (musicdir, name, im.format.lower())
    cache = '/home/judgedreads/.cache/ricochet/%s__%s' % (artist, album)
    im.save(path, im.format)
    im.save(cache, im.format)
    return 0


def _cache_image(args):
    im = Image.open(args[0])
    im.thumbnail((args[2], args[2]))
    im.save(args[1], im.format)


def update_cache(settings):
    # TODO: need to run this when settings change
    # could have covers dir in cache and also have a file to store previous
    # geometry info etc

    cache = settings['cache']
    music = settings['music_dir']
    p = mp.Pool()
    srcs = []
    dests = []
    for artist in sorted(os.listdir(music)):
        for album in os.listdir(os.path.join(music, artist)):
            for name in settings['cover_names']:
                src = os.path.join(music, artist, album, name)
                if os.path.exists(src):
                    break
            if not os.path.exists(src):
                src = '/opt/ricochet/images/default_album.png'
            srcs.append(src)
            dests.append('%s/%s__%s' % (cache, artist, album))
    size = [int(settings['grid_icon_size'])] * len(srcs)
    args = zip(srcs, dests, size)
    p.map(_cache_image, args)
