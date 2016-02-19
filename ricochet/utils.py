import os
import json
import requests
from io import BytesIO
from PIL import Image
import multiprocessing as mp
import hashlib


def get_album_tags(item):
    a = {}
    a['artist'] = item.get('albumartist', item.get('artist', 'Unknown Artist'))
    a['title'] = item.get('album', 'Unknown Album')
    a['date'] = item.get('date', '')
    a['genre'] = item.get('genre', '')
    a['disc'] = item.get('disc', '')
    for k, v in a.items():
        a[k] = delistify_tag(v)
    a['cover'] = get_cover_path(os.path.dirname(item['file']))
    return a


def get_song_tags(item):
    s = {}
    s['title'] = item.get('title', 'Unknown Song')
    s['track'] = item.get('track', '00')
    s['artist'] = item.get('artist', 'Unknown Artist')
    s['file'] = item['file']
    s['time'] = item['time']
    for k, v in s.items():
        s[k] = delistify_tag(v)
    return s


def delistify_tag(tag):
    if not isinstance(tag, list):
        return tag
    s = sorted(set(tag))
    return ', '.join(s)


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


def fetch_album_art(album):
    # use notifications here or at least log stuff
    settings = get_settings()
    url = 'http://musicdatabase.co/artist/%s/album/%s' % (
        album['artist'], album['title'])
    try:
        r = requests.get(url)
        print(r.status_code)
    except requests.exceptions.RequestException as e:
        print(e)
        return
    image_url = _get_image_url(r.text)
    if image_url is None:
        return
    try:
        r = requests.get(image_url)
    except requests.exceptions.RequestException as e:
        print(e)
        return
    dirname = os.path.dirname(album['tracks'][0]['file'])
    im = Image.open(BytesIO(r.content))
    path = os.path.join(settings['music_dir'], dirname, im.format.lower())
    im.save(path, im.format)
    album['cover'] = path
    cache = os.path.join(settings['cache'], 'covers', make_album_hash(album))
    size = int(settings['grid_icon_size'])
    im.thumbnail((size, size))
    im.save(cache, im.format)
    album['thumb'] = cache
    update_cached_album(album)
    return True


def need_update():
    # TODO: maybe I should parse mpd.conf to get common mpd vars?
    settings = get_settings()
    mpddb = os.path.expanduser('~/.mpd/database')
    lib = os.path.join(settings['cache'], 'lib.json')
    return os.path.getmtime(mpddb) > os.path.getmtime(lib)


def update_cached_album(album):
    settings = get_settings()
    h = make_album_hash(album)
    with open(os.path.join(settings['cache'], 'lib.json'), 'r') as f:
        lib = json.load(f)
    lib[h] = album
    with open(os.path.join(settings['cache'], 'lib.json'), 'w') as f:
        json.dump(lib, f)


def _cache_image(args):
    im = Image.open(args[0])
    im.thumbnail((args[2], args[2]))
    im.save(args[1], im.format)


def update_cache(player):
    cache_dir = player.settings['cache']
    p = mp.Pool()
    lib = {}
    args = []
    size = int(player.settings['grid_icon_size'])
    for item in player.iterlib():
        a = get_album_tags(item)
        s = get_song_tags(item)
        a['tracks'] = [s]
        h = make_album_hash(a)
        if h in lib:
            lib[h]['tracks'].append(s)
        else:
            a['thumb'] = os.path.join(cache_dir, 'covers', h)
            args.append((a['cover'], a['thumb'], size))
            lib[h] = a
    p.map(_cache_image, args)

    with open(os.path.join(cache_dir, 'lib.json'), 'w') as f:
        json.dump(lib, f)


def make_album_hash(a):
    s = a['artist'] + a['title'] + a['date'] + a['disc']
    return hashlib.md5(s.encode()).hexdigest()


def get_settings():

    paths = ['%s/.config/ricochet/settings.json' % os.environ['HOME'],
             '/etc/ricochet/settings.json']

    # set up defaults
    settings = {
        'mpd_host': 'localhost',
        'mpd_port': '6600',
        'music_dir': '%s/Music/' % os.environ['HOME'],
        'grid_icon_size': 150,
        'detail_icon_size': 300,
        'notifications': 'True',
        'cache': '%s/.cache/ricochet' % os.environ['HOME'],
        'cover_names': ["cover.jpg", "cover.png", "front.jpg", "front.png"],
        'symbolic_icons': False
    }

    for path in paths:
        if os.path.isfile(path):
            with open(path) as f:
                overrides = json.load(f)
            settings.update(overrides)
            break

    settings['music_dir'] = os.path.normpath(settings['music_dir'])

    return settings


def get_cover_path(dirname):
    settings = get_settings()
    dirname = os.path.join(settings['music_dir'], dirname)
    for name in settings['cover_names']:
        path = os.path.join(dirname, name)
        if os.path.exists(path):
            break
    if not os.path.exists(path):
        path = '/usr/share/ricochet/default_album.png'
    return path
