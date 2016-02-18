import re
import os
import json
import requests
from io import BytesIO
from PIL import Image
import multiprocessing as mp
import taglib
import hashlib


def get_tags(path):
    if not os.path.isfile(path):
        return
    try:
        d = taglib.File(path)
    except OSError:
        return
    print(d.tags)
    if 'TRACKNUMBER' in d.tags:
        track = d.tags['TRACKNUMBER'][0].split('/')[0]
    else:
        track = '00'
    # make sure track numbers are padded
    track = track.zfill(2)
    if 'TITLE' in d.tags:
        title = d.tags['TITLE'][0]
    else:
        title = 'Unknown Song'
    if 'ARTIST' in d.tags:
        artist = d.tags['ARTIST'][0]
    else:
        artist = 'Unknown Artist'
    kbps = str(d.bitrate)
    return [track, title, artist, kbps, path]


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


def fetch_album_art(name, musicdir, settings):
    # use notifications here or at least log stuff
    artist, album = name.split('/')
    artist = artist.replace(' ', '_')
    try:
        r = requests.get(
            'http://musicdatabase.co/artist/%s/album/%s' % (artist, album)
        )
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
    im = Image.open(BytesIO(r.content))
    path = '%s/%s/cover.%s' % (musicdir, name, im.format.lower())
    im.save(path, im.format)
    cache = '/home/judgedreads/.cache/ricochet/%s' % name.replace('/', '__')
    size = int(settings['grid_icon_size'])
    im.thumbnail((size, size))
    im.save(cache, im.format)
    return cache


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


def check_filetype(f):
    valid = ('mp3', 'm4a', 'flac', 'mp4', 'ogg', 'mpc', 'oga')
    return f.endswith(valid)


def get_default_music_root(music_root=None):
    if music_root is None:
        return os.path.join(os.environ.get('HOME', ''), 'Music')
    return os.path.abspath(music_root)


def parse_files(files, music_root=None):
    '''
    returns a list of dicts containing information about the songs in the
    playlist
    '''
    # I think that this should be done by the browser so that the player can be
    # handed a list of file paths instead of a directory or filename.
    music_root = get_default_music_root(music_root)
    songs = []
    if not isinstance(files, list):
        absfiles = music_root+'/'+files
        if os.path.isfile(absfiles):
            files = [files]
        elif os.path.isdir(absfiles):
            files = [os.path.join(files, f) for f in os.listdir(absfiles)]
            files.sort()
    for i, f in enumerate(files):
        f = trim_prefix(f, 'file://')
        f = trim_prefix(f, 'file: ')
        if not check_filetype(f):
            continue
        segs = f.split('/')
        song = {
            'artist': segs[0],
            'album': segs[1],
            'path': os.path.join(music_root, f),
            # TODO: cover path should be passed through from initial browser,
            # maybe even reuse the pixbuf?
            'cover': get_cover_path('/'.join(segs[0:2])),
            'playing': False
        }
        num, name = parse_song(segs[-1])
        if num is None:
            num = i
        song['name'] = name
        song['track'] = num
        songs.append(song)
    return songs


def trim_prefix(s, prefix):
    # could make this take tuples of prefixes
    if s.startswith(prefix):
        return s[len(prefix):]
    else:
        return s


def trim_suffix(s, suffix):
    if s.endswith(suffix):
        return s[:len(suffix)]
    else:
        return s


def remove_ext(filename):
    return '.'.join(filename.split('.')[:-1])


def parse_song(filename):
    song = remove_ext(filename)
    for sep in ('.', '-', '_', ' '):
        segs = song.split(sep)
        if re.match('[0-9][0-9]$', segs[0].strip()):
            tracknum = int(segs[0].strip())
            trackname = sep.join(segs[1:]).strip()
            return tracknum, trackname
    return None, song


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
