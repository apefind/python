#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys, shutil, glob
import docopt, yaml
from apefind.util.script import get_script_logger, script_logging


log = get_script_logger()
script_logging = script_logging(log)


USAGE = """usage:
    clean_brew_casks.py [--simulate]
"""


def get_cask_directories(caskroom):
    return [e.path for e in os.scandir(caskroom) if e.is_dir()]


def get_cask_versions(caskdir):
    versions = []
    for e in os.scandir(caskdir):
        if not e.is_dir():
            continue
        if e.name[0] == '.':
            continue
        if e.name == 'latest':
            continue
        versions.append(e.path)
    return versions


def get_old_cask_versions(caskdir):
    return sorted(get_cask_versions(caskdir))[:-1]


def clean_brew_casks(caskroom, simulate=False):
    log.info('    * removing old brew casks')
    for caskdir in get_cask_directories(caskroom):
        log.info('        ' + os.path.basename(caskdir))
        for version in get_old_cask_versions(caskdir):
            log.info('            ' + os.path.basename(version))
            if not simulate:
                shutil.rmtree(version)


@script_logging
def run_script(args):
    clean_brew_casks('/usr/local/Caskroom', args['--simulate'])


if __name__ == '__main__':
    run_script(docopt.docopt(USAGE, argv=sys.argv[1:]))
