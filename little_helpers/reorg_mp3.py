#!/usr/bin/env python

import pathlib
import sys


def fix_name(name):
    for _ in range(3):
        name = name.replace("  ", " ")
    return name.strip()


def get_artist_and_album(p, artist=None):
    name = fix_name(p.name)
    if artist is not None and " - " not in name:
        return "", name
    S = name.split(" - ")
    artist = S[0]
    album = " - ".join(S[1:])
    return fix_name(artist), fix_name(album)


def get_full_album_name(artist, album):
    return f"{artist} - {album}"


def reorganize_artist(root, artist):
    print(f"{artist} ✔")
    for p in sorted(root.iterdir()):
        if not p.is_dir():
            continue
        artist_, album = get_artist_and_album(p, artist=artist)
        if artist == artist_:
            continue
        full_album = get_full_album_name(artist, album)
        if p.name == full_album:
            continue
        print(f"    {album} → {full_album} ✔")
        p.rename(root / full_album)


def reorganize_album(root, artist, album):
    full_album = get_full_album_name(artist, album)
    print(f"{artist} - {album} → {artist}/{full_album}")
    p = root.parent / artist
    p.mkdir(exist_ok=True)
    root.rename(p / full_album)


def reorganize_genre(root):
    for p in sorted(root.iterdir()):
        if not p.is_dir():
            continue
        artist, album = get_artist_and_album(p)
        if artist == p.name:
            reorganize_artist(p, artist)
        else:
            reorganize_album(p, artist, album)


if __name__ == "__main__":
    for p in sys.argv[1:]:
        reorganize_genre(pathlib.Path(p))
