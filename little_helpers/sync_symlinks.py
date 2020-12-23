#!/usr/bin/env python3
"""Example symlinks.yaml::

    work:
        basedir:                            $WORK
        symlinks:
            bin/annotations2srt:            python/apefind/youtube/script/annotations2srt.py
            bin/bolt:                       go/bin/bolt
            bin/charm:                      shell/script/macos/charm
            bin/clean_up:                   shell/script/clean_up
            bin/cookinginrussia:            shell/script/cookinginrussia.sh
            ...
"""

import os

import yaml

from apefind.util import script
from apefind.util.path import expand_path
from apefind.util.script import _ok, _nok

log = script.get_logger()


def parse_args(args=None, namespace=None):
    parser = script.ArgumentParser()
    parser.add_argument("-config")
    parser.add_commands(required=True)
    for command in "install", "uninstall", "check":
        cmd = parser.add_command(command)
        cmd.add_argument("-site", nargs="*")
    return parser.parse_args(
        args=args,
        namespace=namespace,
        defaults=f"~/.config/{script.get_script_name()}.yaml",
    )


def get_symlinks(conf, site):
    site_cfg = conf.get(site, {})
    return (
        site_cfg.get("basedir", ""),
        site_cfg.get("symlinks", {}),
    )


def get_symlink_paths(basedir, target, source):
    return (
        expand_path(basedir + os.sep + target),
        expand_path(basedir + os.sep + source),
    )


def create_symlink(target, source):
    if not os.path.exists(source):
        raise OSError(f"{source} does not exist")
    if os.path.islink(target):
        os.remove(target)
    os.symlink(source, target)


def remove_symlink(target):
    if os.path.islink(target):
        os.remove(target)


def check_symlink(target, source):
    if not os.path.exists(source):
        raise OSError(f"{source} does not exist")
    if not os.path.exists(target):
        raise OSError(f"{target} does not exist")
    if not os.path.islink(target):
        raise OSError(f"{target} is not a symlink")
    if not os.path.realpath(target) == os.path.realpath(source):
        raise OSError(f"linked to {os.readlink(target)}")


def install_symlinks(basedir, symlinks):
    log.info(f"    * creating symbolic links in {basedir}")
    for target, source in sorted(symlinks.items()):
        try:
            create_symlink(*get_symlink_paths(basedir, target, source))
            log.info(f"        {target} -> {source} {_ok}")
        except Exception as err:
            log.warning(f"        {target} -> {source}: {err} {_nok}")


def uninstall_symlinks(basedir, symlinks):
    log.info(f"    * removing symbolic links in {basedir}")
    for target, source in sorted(symlinks.items()):
        try:
            remove_symlink(get_symlink_paths(basedir, target, source)[0])
            log.info(f"        {target} -> {source} {_ok}")
        except Exception as err:
            log.warning(f"        {target} -> {source}: {err} {_nok}")


def check_symlinks(basedir, symlinks):
    log.info(f"    * checking symbolic links in {basedir}")
    for target, source in sorted(symlinks.items()):
        try:
            check_symlink(*get_symlink_paths(basedir, target, source))
            log.info(f"        {target} -> {source} {_ok}")
        except Exception as err:
            log.warning(f"        {target} -> {source}: {err} {_nok}")


@script.run()
def run_script(args):
    with open(expand_path(args.config), "r") as f:
        conf = yaml.load(f, Loader=yaml.FullLoader)
    if args.site is None:
        args.site = conf.keys()
    if args.cmd == "install":
        for site in args.site:
            install_symlinks(*get_symlinks(conf, site))
    elif args.cmd == "uninstall":
        for site in args.site:
            uninstall_symlinks(*get_symlinks(conf, site))
    elif args.cmd == "check":
        for site in args.site:
            check_symlinks(*get_symlinks(conf, site))


if __name__ == "__main__":
    run_script(parse_args())
