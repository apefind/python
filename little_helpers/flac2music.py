#!/usr/bin/env python3

import os
import pathlib
import shutil
import subprocess
import zipfile
from typing import Tuple

import PIL.Image
import PIL.ImageFile
import PIL.ImageFilter
import eyed3
import rarfile

from apefind.util import script

log = script.get_logger()


def parse_args(args=None, namespace=None):
    parser = script.ArgumentParser()
    parser.add_commands(required=True)
    cmd = parser.add_command("unpack")
    cmd.add_argument("-downloads", default="~/Downloads", help="download folder")
    cmd.add_argument("-music", default=os.getcwd(), help="music folder")
    cmd.add_argument("-trash", default="~/Desktop", help="trash folder")
    cmd.add_argument("-passwords", type=tuple, default=(), help="password list for encrypted archives")
    cmd.add_argument("-cleanup", action="store_true", help="delete archives after unpacking")
    cmd = parser.add_command("convert")
    cmd.add_argument("-album", default=os.getcwd(), help="album directory")
    cmd.add_argument("-flacdir", help="target directory for flac files")
    cmd.add_argument("-mp3dir", help="target directory for mp3 files")
    cmd.add_argument("-scale", type=int, default=2, help="scaling factor for mp3 conversion")
    return parser.parse_args(args=args, namespace=namespace, defaults=f"~/.config/{script.get_script_name()}.yaml")


def unpack_music(downloads: pathlib.Path, music: pathlib.Path, trash: pathlib.Path, passwords: Tuple[str],
                 cleanup: bool = False):
    def is_music_archive(ar):
        for filepath in ar.namelist():
            if pathlib.PurePath(filepath).suffix.lower() in (".mp3", ".flac", ".wma", ".ape", ".m4a", ".cue"):
                return True
        return False

    def get_archive_dir(ar):
        names = ar.namelist()
        p = pathlib.PurePath(names[0]).parts[0]
        if all(pathlib.PurePath(name).parts[0] == p for name in names):
            return p

    def move_to_trash(archive):
        if cleanup:
            archive.unlink()
        else:
            shutil.move(str(archive), str(trash))

    def unrar(archive, pwd=None):
        with rarfile.RarFile(archive) as ar:
            if pwd is None:
                if ar.needs_password():
                    raise rarfile.PasswordRequired("no password provided")
            else:
                ar.setpassword(pwd)
            if not is_music_archive(ar):
                raise AssertionError("not a music archive")
            p = get_archive_dir(ar)
            if p is None:
                target = music / archive.stem
                target.mkdir(parents=True)
                unrar.target = target
                ar.extractall(target)
            else:
                target = music / p
                unrar.target = target
                if target.exists():
                    raise AssertionError(f"{p} already exists")
                ar.extractall(music)
        return target

    def unzip(archive, pwd=None):
        with zipfile.ZipFile(archive) as ar:
            if pwd is not None:
                ar.setpassword(bytes(pwd, 'utf-8'))
            if not is_music_archive(ar):
                raise AssertionError("not a music archive")
            p = get_archive_dir(ar)
            if p is None:
                target = music / archive.stem
                unzip.target = target
                target.mkdir(parents=True)
                ar.extractall(target)
            else:
                target = music / p
                unzip.target = target
                if target.exists():
                    raise AssertionError(f"{p} already exists")
                ar.extractall(music)
        return target

    def fix_permissions(target):
        target.touch()
        target.chmod(0o755)
        for p in target.rglob("*"):
            if p.is_dir():
                p.chmod(0o755)
            elif p.is_file():
                p.chmod(0o644)

    def unpack(archive, unar=unrar):
        err = None
        for pwd in passwords:
            unrar.target = None
            try:
                target = unar(archive, pwd=pwd)
                fix_permissions(target)
                move_to_trash(archive)
                return
            except rarfile.BadRarFile as err_:
                if unrar.target is not None:
                    shutil.rmtree(unrar.target)
                err = err_
            except (AssertionError, rarfile.PasswordRequired, rarfile.NeedFirstVolume) as err_:
                err = err_
        if err:
            raise err

    log.info(f"    * extracting archives")
    for archive in sorted(downloads.glob("*.rar")):
        log.info(f"        {archive.name}")
        try:
            unpack(archive, unar=unrar)
        except Exception as err:
            log.warning(f"            {err}")
    for archive in sorted(downloads.glob("*.zip")):
        log.info(f"        {archive.name}")
        try:
            unpack(archive, unar=unzip)
        except Exception as err:
            log.warning(f"            {err}")


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
        if not p.is_file():
            continue
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

    def get_audio_and_cue():
        audio, cues = list(album.rglob("*.flac")), list(album.rglob("*.cue"))
        if not audio:
            audio = list(album.rglob("*.ape"))
        assert len(audio) == len(cues) == 1
        return audio[0], cue_to_utf8(cues[0])

    def split_audio(audio, cue):
        cmd = f'shnsplit -d "{flacdir}" -f "{cue}" -t "{title}" -o flac "{audio}"'
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
    audio, cue = get_audio_and_cue()
    log.info(f"    * splitting {audio.name}")
    flacs = split_audio(audio, cue)
    for f in flacs:
        log.info(f"        {f.name}")
    log.info(f"    * tagging flac files")
    tag_flacs(flacs, cue)


def convert_flac(album, flacdir, mp3dir, scale=2):
    log.info(f"    * converting to mp3")
    for flac in sorted(flacdir.glob("*.flac")):
        mp3 = mp3dir / flac.with_suffix(".mp3").name
        log.info(f"        {mp3.name}")
        if mp3.exists():
            continue
        cmd = f'ffmpeg -i "{flac}" -codec:a libmp3lame -qscale:a {scale} "{mp3}"'
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
    if args.cmd == "unpack":
        downloads, music = pathlib.Path(args.downloads).expanduser(), pathlib.Path(args.music).expanduser()
        trash = pathlib.Path(args.trash).expanduser()
        unpack_music(downloads, music, trash, (None,) + tuple(args.passwords), args.cleanup)
    elif args.cmd == "convert":
        album, flacdir, mp3dir = get_album_dirs(args.album, args.flacdir, args.mp3dir)
        mp3dir.mkdir(parents=True, exist_ok=True)
        if splitting_required(album):
            flacdir.mkdir(parents=True, exist_ok=True)
            split_flac(album, flacdir)
            convert_flac(album, flacdir, mp3dir, args.scale)
        else:
            convert_flac(album, album, mp3dir, args.scale)


if __name__ == "__main__":
    run_script(parse_args())
