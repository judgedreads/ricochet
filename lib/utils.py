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
