import os
import json
from PIL import Image
import multiprocessing as mp
import hashlib
from gi.repository import Gtk, GObject
import threading
import pkg_resources


SETTINGS = {
    'mpd_host': 'localhost',
    'mpd_port': '6600',
    'music_dir': os.path.expandvars('$HOME/Music'),
    'grid_icon_size': 150,
    'detail_icon_size': 300,
    'notifications': 'True',
    'cache': '%s/.cache/ricochet' % os.environ['HOME'],
    'cover_names': ["cover.jpg", "cover.png", "front.jpg", "front.png"],
    'symbolic_icons': False,
}


def get_version():
    return pkg_resources.require("ricochet")[0].version


def progress(func, *args, **kwargs):
    win = Gtk.Window(default_height=50, default_width=300)
    win.connect("delete-event", Gtk.main_quit)
    win.set_position(Gtk.WindowPosition.CENTER_ALWAYS)

    progress = Gtk.ProgressBar(show_text=True)
    progress.set_text('updating cache...')
    win.add(progress)

    def update_progress():
        progress.pulse()
        return True

    def target():
        try:
            func(*args, **kwargs)
        finally:
            win.close()

    win.show_all()

    GObject.timeout_add(100, update_progress)
    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()
    Gtk.main()


def get_album_tags(item):
    a = {
        'artist': item.get('albumartist', item.get('artist', 'Unknown Artist')),
        'title': item.get('album', 'Unknown Album'),
        'date': item.get('date', ''),
        'genre': item.get('genre', ''),
        'cover': get_cover_path(os.path.dirname(item['file'])),
    }
    return {k: delistify_tag(v) for k, v in a.items()}


def get_song_tags(item):
    s = {
        'title': item.get('title', 'Unknown Song'),
        'track': item.get('track', '00'),
        'artist': item.get('artist', 'Unknown Artist'),
        'file': item['file'],
        'time': item['time'],
        'disc': item.get('disc', ''),
    }
    return {k: delistify_tag(v) for k, v in s.items()}


def delistify_tag(tag):
    if not isinstance(tag, list):
        return tag
    return ', '.join(sorted(set(tag)))


def need_update():
    # TODO: maybe I should parse mpd.conf to get common mpd vars?
    lib = os.path.join(SETTINGS['cache'], 'lib.json')
    if not os.path.exists(lib):
        return True
    paths = [
        os.path.expandvars('$HOME/.mpd/database'),
        os.path.expandvars('$HOME/.config/ricochet/settings.json'),
        '/etc/ricochet/settings.json',
    ]
    for p in paths:
        if not os.path.exists(p):
            continue
        if os.path.getmtime(p) > os.path.getmtime(lib):
            return True


def update_cached_album(album):
    h = make_album_hash(album)
    with open(os.path.join(SETTINGS['cache'], 'lib.json'), 'r') as f:
        lib = json.load(f)
    lib[h] = album
    with open(os.path.join(SETTINGS['cache'], 'lib.json'), 'w') as f:
        json.dump(lib, f)


def _cache_image(args):
    src, dst, sz = args
    im = Image.open(src)
    im.thumbnail((sz, sz))
    im.save(dst, im.format)


def update_cache(player):
    cache_dir = SETTINGS['cache']
    if not os.path.exists(os.path.join(cache_dir, 'covers')):
        os.makedirs(os.path.join(cache_dir, 'covers'))
    p = mp.Pool()
    lib = {}
    args = []
    size = int(SETTINGS['grid_icon_size'])
    for item in player.iterlib():
        a = get_album_tags(item)
        s = get_song_tags(item)
        h = make_album_hash(a)
        if h in lib:
            lib[h]['tracks'].append(s)
        else:
            a['tracks'] = [s]
            a['thumb'] = os.path.join(cache_dir, 'covers', h)
            args.append((a['cover'], a['thumb'], size))
            lib[h] = a
    p.map(_cache_image, args)

    with open(os.path.join(cache_dir, 'lib.json'), 'w') as f:
        json.dump(lib, f)


def make_album_hash(a):
    s = a['artist'] + a['title'] + a['date']
    return hashlib.md5(s.encode()).hexdigest()


def update_settings():
    paths = [os.path.expandvars('$HOME/.config/ricochet/settings.json'),
             '/etc/ricochet/settings.json']
    for path in paths:
        if os.path.isfile(path):
            with open(path) as f:
                overrides = json.load(f)
            SETTINGS.update(overrides)
            break


def get_cover_path(dirname):
    if not dirname:
        return '/usr/share/ricochet/default_album.png'
    dirname = os.path.join(SETTINGS['music_dir'], dirname)
    for name in SETTINGS['cover_names']:
        path = os.path.join(dirname, name)
        if os.path.exists(path):
            break
    if not os.path.exists(path):
        path = '/usr/share/ricochet/default_album.png'
    return path
