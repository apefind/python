#!/usr/bin/env python

import argparse
import pathlib

from apefind.util import script
from apefind.util.script import _ok

log = script.get_logger()


def parse_args():
    parser = script.ArgumentParser()
    parser.add_argument("path", nargs=argparse.REMAINDER)
    return parser.parse_args()


def fix_name(name):
    for _ in range(3):
        name = name.replace("  ", " ")
    return name.strip()


def get_author_and_book(p):
    if " - " not in p.name:
        return p.parent.name, p.name
    S = p.name.split("-")
    author = S[0]
    book = "-".join(S[1:])
    return fix_name(author), fix_name(book)


def get_full_book_title(author, book):
    return f"{author} - {book}"


def reorganize_author(root):
    log.info(f"        {root} {_ok}")
    for p in sorted(root.iterdir()):
        if not p.is_file():
            continue
        author, book = get_author_and_book(p)
        full_title = get_full_book_title(author, book)
        if p.name == full_title:
            continue
        log.info(f"            {book} → {full_title} {_ok}")
        p.rename(root / full_title)


def reorganize_genre(root):
    for p in sorted(root.iterdir()):
        if p.is_dir():
            reorganize_author(p)


@script.run()
def run_script(args):
    log.info(f"    * reorganizing books")
    for p in args.path:
        reorganize_genre(pathlib.Path(p))


if __name__ == "__main__":
    run_script(parse_args())
