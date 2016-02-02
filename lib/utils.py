import re
import os
import json
import requests
from io import BytesIO
from PIL import Image
import multiprocessing as mp


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
        'cover_names': ["cover.jpg", "cover.png", "front.jpg", "front.png"],
        'symbolic_icons': False
    }

    if os.path.isfile(path):
        with open(path) as f:
            overrides = json.load(f)
        settings.update(overrides)
    else:
        print('No file found at %s - using defaults.' % path)

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


def get_cover_path(album, music_root=None):
    music_root = get_default_music_root(music_root)
    path = '%s/%s/cover.jpg' % (music_root, album)
    if not os.path.exists(path):
        path = '/opt/ricochet/images/default_album.png'
    return path
