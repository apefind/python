#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys, errno
import docopt, yaml
from apefind.util.script import get_script_logger, script_logging


log = get_script_logger()
script_logging = script_logging(log)


USAGE = """usage:
    sync_symlinks.py install --configuration=<yaml> <key>...
    sync_symlinks.py uninstall --configuration=<yaml> <key>...
"""


def get_symlinks(symlinks, key):
    config = symlinks.get(key, {})
    return config.get('site', ''), config.get('symlinks', {}),


def get_symlink_paths(site, target, source):
    return os.path.abspath(os.path.expandvars(site + os.sep + target)), \
           os.path.abspath(os.path.expandvars(site + os.sep + source))


def create_symlink(target, source):
    if not os.path.isfile(source):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), source)
    if os.path.islink(target):
        os.remove(target)
    os.symlink(source, target)


def remove_symlink(target, source):
    if os.path.islink(target):
        os.remove(target)


def install_symlinks(site, symlinks):
    log.info('    * creating symbolic links in %s' % site)
    for target, source in sorted(symlinks.items()):
        log.info('        %s -> %s' % (target, source))
        try:
            create_symlink(*get_symlink_paths(site, target, source))
        except Exception as e:
            log.warning('            => %s' % e)


def uninstall_symlinks(site, symlinks):
    log.info('    * removing symbolic links in %s' % site)
    for target, source in sorted(symlinks.items()):
        log.info('        %s -> %s' % (target, source))
        try:
            remove_symlink(*get_symlink_paths(site, target, source))
        except Exception as e:
            log.warning('            => %s' % e)


@script_logging
def run_script(args):
    conf, keys = args.get('--configuration'), args['<key>']
    try:
        with open(conf, 'r') as f:
            symlinks = yaml.load(f)
    except:
        symlinks = conf
    if args['install']:
        for key in keys:
            install_symlinks(*get_symlinks(symlinks, key))
    elif args['uninstall']:
        for key in keys:
            uninstall_symlinks(*get_symlinks(symlinks, key))


if __name__ == '__main__':
    run_script(docopt.docopt(USAGE, argv=sys.argv[1:]))
