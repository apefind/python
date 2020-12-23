#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys, shutil, glob
import docopt, yaml
from apefind.util import script


log = script.get_logger()


USAGE = """usage:
    sync_app_locations.py [--appdir=<appdir>] [--configuration=<yaml>]
"""


APPLICATIONS = """
    Graphics:
        - Gimp
    Multimedia:
        - VLC
        - Vox
    Network:
        - FileZilla
        - Firefox
        - Thunderbird
        - TorBrowser
    Office:
        - LibreOffice
    Programming:
        - Atom
        - PyCharm CE
        - Racket v6.5
    Tools:
        - FoundImages
        - iTerm
"""


def sync_app_locations(appdir, applications):
    def get_app_categories(applications):
        D = {}
        for category, apps in applications.items():
            for app in apps:
                D[app] = category
        return D

    def get_app_and_category(filename):
        app = os.path.basename(os.path.splitext(path)[0])
        return app, categories.get(app)

    def move_app(app, category):
        path = appdir + os.sep + category + os.sep + app + ".app"
        if os.path.islink(path):
            os.remove(path)
        elif os.path.exists(path):
            shutil.rmtree(path)
        path, location = (
            appdir + os.sep + app + ".app",
            appdir + os.sep + categories[app],
        )
        os.makedirs(location, exist_ok=True)
        shutil.move(path, appdir + os.sep + categories[app])

    log.info("    * syncing app locations")
    categories = get_app_categories(applications)
    for path in glob.glob(appdir + os.sep + "*.app"):
        app, category = get_app_and_category(path)
        if category is not None:
            log.info("        %s -> %s" % (app, category))
            move_app(app, category)
        else:
            log.info("        %s -> no category found" % (app,))


@script.run()
def run_script(args):
    appdir, conf = args.get("--appdir"), args.get("--configuration")
    if appdir is None:
        appdir = os.environ["HOME"] + os.sep + "Applications"
    if conf is not None:
        with open(conf, "r") as f:
            applications = yaml.load(f, Loader=yaml.FullLoader)
    else:
        applications = yaml.load(APPLICATIONS, Loader=yaml.FullLoader)
    sync_app_locations(appdir, applications)


if __name__ == "__main__":
    run_script(docopt.docopt(USAGE, argv=sys.argv[1:]))
