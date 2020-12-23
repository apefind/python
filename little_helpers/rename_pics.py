#!/usr/bin/env python

import argparse
import mimetypes
import os
import pathlib

from apefind.util import script

log = script.get_logger()


def get_parser():
    parser = script.ArgumentParser()
    parser.add_argument("-start", type=int)
    parser.add_argument("-template", default="Pic_{n:06d}{suffix}")
    parser.add_argument("-config", default="~/.config/lastpic")
    parser.add_argument("paths", nargs=argparse.REMAINDER)
    return parser


def is_pic(filename):
    mtype, _ = mimetypes.guess_type(filename)
    return mtype is not None and mtype.startswith("image")


def get_counter(n, config):
    if n is not None:
        return n
    try:
        with open(config, "r") as f:
            return int(f.read())
    except:
        return 0


def save_counter(n, config):
    with open(config, "w") as f:
        f.write(str(n))


def rename_pictures(p, n, template):
    for e in p.rglob(f"*.*"):
        if not is_pic(e):
            continue
        suffix = e.suffix
        filename = template.format(**locals())
        log.info(f"        {e.parent.name}/{e.name} -> {filename}")
        e.rename(e.parent / filename)
        n += 1
    return n


@script.run()
def run_script(args):
    if not args.paths:
        paths = [pathlib.Path.cwd()]
    else:
        paths = [pathlib.Path(p) for p in args.paths]
    log.info("    * renaming pictures")
    config = os.path.expanduser(args.config)
    n = get_counter(args.start, config)
    for p in paths:
        if not p.is_dir():
            continue
        n = rename_pictures(p, n, args.template)
    save_counter(n, config)


if __name__ == "__main__":
    run_script(get_parser().parse_args())
