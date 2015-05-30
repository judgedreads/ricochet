#!/usr/bin/env python3

import requests


def _get_image_url(html):
    for line in html.split('\n'):
        if 'class="album-cover"' not in line:
            continue
        for item in line.split():
            if 'src' in item:
                url = item.split('"')[1]
                if url:
                    return url
    return None


def fetch_album_art(name, musicdir):
    try:
        r = requests.get(
            'http://www.last.fm/music/%s' % name.replace(' ', '+')
        )
    except requests.exceptions.RequestException as e:
        print(e)
        return 1
    image_url = _get_image_url(r.text)
    if image_url is None:
        return 1
    path = '%s%s/cover.jpg' % (musicdir, name)
    print(path)
    f = open(path, 'wb')
    try:
        r = requests.get(image_url)
    except requests.exceptions.RequestException as e:
        print(e)
        return 1
    f.write(r.content)
    f.close()
    return 0
