import re
import os


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
    # IDEA: store a hash of the full path so that instead I can
    # avoid recreating dicts I already have.
    music_root = get_default_music_root(music_root)
    songs = []
    for i, f in enumerate(files):
        # FIXME: make this gst and mpd compatible, ie need to strip file:// and
        # file
        f = f[6:]
        if not check_filetype(f):
            continue
        segs = f.split('/')
        song = {
            'artist': segs[0],
            'album': segs[1],
            'path': music_root + f,
            'cover': get_cover_path('/'.join(segs[0:-1])),
            'playing': False
        }
        num, name = parse_song(segs[-1])
        if num is None:
            num = i
        song['name'] = name
        song['track'] = num
        songs.append(song)
    return songs


def remove_ext(filename):
    return '.'.join(filename.split('.')[0:-1])


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
    print(path)
    if not os.path.exists(path):
        path = '/opt/ricochet/images/default_album.png'
    return path
