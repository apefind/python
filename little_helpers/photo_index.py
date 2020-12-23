#!/usr/bin/env python

import argparse
import mimetypes
import os

from apefind.util import script

log = script.get_logger()


def get_parser():
    parser = script.ArgumentParser()
    parser.add_argument("path", nargs=argparse.REMAINDER)
    return parser


def get_subdirectories(path):
    return sorted(
        [
            path + os.sep + f
            for f in os.listdir(path)
            if os.path.isdir(path + os.sep + f)
        ]
    )


def get_year_photos(path):
    L = []
    for d in get_subdirectories(path):
        description = d + os.sep + "DESCRIPTION.txt"
        if os.path.isfile(description):
            with open(description, "r") as f:
                date, content = get_description_content(f.readlines())
            n = len([f for f in os.listdir(d) if is_picture(f)])
        else:
            date, content = "", []
        n = len([f for f in os.listdir(d) if is_picture(f)])
        L.append((d, date, content, n))
    return L


def is_picture(filename):
    type, _ = mimetypes.guess_type(filename)
    return type is not None and type[:5] == "image"


def get_description_content(description):
    date = description[0][5:].strip()
    content = [clear_description(s) for s in " ".join(description[1:]).split(",")]
    return date, content


def clear_description(s):
    s = s.replace("Description:", "").replace("\n", " ").strip()
    while s.find("  ") >= 0:
        s = s.replace("  ", " ")
    return s


def print_index(path):
    for y in get_subdirectories(path):
        title = os.path.basename(y)
        log.info("")
        log.info(title)
        log.info(len(title) * "=")
        for m, date, content, n in get_year_photos(y):
            title = f"{os.path.basename(m)} ({date}, {n} Photos)"
            log.info("")
            log.info(title)
            log.info(len(title) * "-")
            for s in content:
                log.info("    - " + s.title())


def run_script(args):
    title = "Photo Index"
    log.info(title)
    log.info(len(title) * "*")
    for p in args.path:
        print_index(p)


if __name__ == "__main__":
    run_script(get_parser().parse_args())
