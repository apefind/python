#!/usr/bin/env python3

import os
import pathlib
import shutil
import subprocess

import eyed3
import PIL.Image
import PIL.ImageFile
import PIL.ImageFilter

from apefind.util import script

log = script.get_logger()


def parse_args(args=None, namespace=None):
    parser = script.ArgumentParser()
    parser.add_argument("-album", default=os.getcwd())
    parser.add_argument("-flacdir")
    parser.add_argument("-mp3dir")
    return parser.parse_args(args=args, namespace=namespace, defaults=f"~/.config/{script.get_script_name()}.yaml")


def get_album_dirs(album, flacdir, mp3dir):
    album = pathlib.Path(album).expanduser()
    if flacdir is None:
        flacdir = album / "flac" / album.name
    else:
        flacdir = pathlib.Path(flacdir).expanduser() / album.name
    if mp3dir is None:
        mp3dir = album / "mp3" / album.name
    else:
        mp3dir = pathlib.Path(mp3dir).expanduser() / album.name
    return album, flacdir, mp3dir


def copy_cover(album, target):
    def resize_cover(filepath, size=640):
        cover = PIL.Image.open(filepath)
        cover = cover.resize((size, size), PIL.Image.LANCZOS)
        cover = cover.filter(PIL.ImageFilter.UnsharpMask(radius=1.5, percent=70, threshold=5))
        cover.save(filepath)

    for p in album.glob("**/*"):
        if any(t in p.name.lower() for t in ("cover", "front", "folder")):
            cover = target / "Cover.jpg"
            resize_cover(shutil.copy(p, cover))
            return cover


def add_cover_art(cover, mp3dir):
    for mp3 in sorted(mp3dir.glob("*.mp3")):
        audio = eyed3.load(mp3)
        if audio.tag is None:
            audio.initTag()
        with open(cover, "rb") as f:
            audio.tag.images.set(3, f.read(), 'image/jpeg')
        audio.tag.save()


def splitting_required(album):
    return len(list(album.rglob("*.cue"))) > 0


def split_flac(album, flacdir, title="%n %t"):
    def cue_to_utf8(cue):
        try:
            with open(cue, "r") as f:
                data = f.read()
        except UnicodeDecodeError:
            with open(cue, "r", encoding="latin-1") as f:
                data = f.read()
        cue = flacdir / cue.name
        with open(cue, "w", encoding="utf-8") as f:
            f.write(data)
        return cue

    def get_flac_and_cue():
        flacs, cues = list(album.rglob("*.flac")), list(album.rglob("*.cue"))
        assert len(flacs) == len(cues) == 1
        return flacs[0], cue_to_utf8(cues[0])

    def split_flac(flac, cue):
        cmd = f'shnsplit -d "{flacdir}" -f "{cue}" -t "{title}" -o flac "{flac}"'
        # cmd = "ls"
        status, stdout = subprocess.getstatusoutput(cmd)
        if status:
            raise OSError(stdout)
        for f in flacdir.glob("*.flac"):
            if "pregap" in f.name:
                f.unlink()
        return sorted(flacdir.rglob("*.flac"))

    def tag_flacs(flacs, cue):
        args = " ".join(f'"{f}"' for f in flacs)
        cmd = f'cuetag.sh "{cue}" {args}'
        status, stdout = subprocess.getstatusoutput(cmd)
        if status or any(t in stdout for t in ("error", "warning")):
            raise OSError(stdout)

    log.info(f"    * converting {album.name}")
    flac, cue = get_flac_and_cue()
    log.info(f"    * splitting {flac.name}")
    flacs = split_flac(flac, cue)
    for f in flacs:
        log.info(f"        {f.name}")
    log.info(f"    * tagging flac files")
    tag_flacs(flacs, cue)


def convert_flac(album, flacdir, mp3dir):
    log.info(f"    * converting to mp3")
    for flac in sorted(flacdir.glob("*.flac")):
        mp3 = mp3dir / flac.with_suffix(".mp3").name
        log.info(f"        {mp3.name}")
        if mp3.exists():
            continue
        cmd = f'ffmpeg -i "{flac}" -codec:a libmp3lame -qscale:a 2 "{mp3}"'
        status, stdout = subprocess.getstatusoutput(cmd)
        if status:
            raise OSError(stdout)
    log.info(f"    * copying cover")
    cover = copy_cover(album, mp3dir)
    if cover is not None:
        log.info(f"    * adding cover art")
        add_cover_art(cover, mp3dir)


@script.run()
def run_script(args):
    album, flacdir, mp3dir = get_album_dirs(args.album, args.flacdir, args.mp3dir)
    if splitting_required(album):
        flacdir.mkdir(parents=True, exist_ok=True)
        mp3dir.mkdir(parents=True, exist_ok=True)
        split_flac(album, flacdir)
        convert_flac(album, flacdir, mp3dir)
    else:
        mp3dir.mkdir(parents=True, exist_ok=True)
        convert_flac(album, album, mp3dir)


if __name__ == "__main__":
    run_script(parse_args())
