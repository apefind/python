#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import docopt
from apefind.util.script import get_script_logger, script_logging
from apefind.youtube.cookinginrussia.downloader import *


SCRIPT_NAME = 'cookinginrussia'

log = get_script_logger(name=SCRIPT_NAME)
script_logging = script_logging(log, name=SCRIPT_NAME)


USAGE = """usage:
    {script_name} download [--flags=<flags>] [--output=<output>] <url>...

options:
    --flags FLAGS    comma separated options [default: {default_flags}]
    --output OUTPUT  output directory [default: .]
""".format(script_name=SCRIPT_NAME, default_flags=DEFAULT_FLAGS)


def download_video_files(urls, output, flags):

    def download_files(url):
        log.info('    * processing ' + url)
        downloader.get_info(url)
        log.info('        ' + downloader.info['title'])
        if DOWNLOAD_VIDEO in downloader.flags:
            log.info('    * downloading video')
            downloader.download_video(url)
        if CREATE_META_INFO in downloader.flags:
            log.info('    * creating meta info')
            downloader.create_meta_info(url)
        if DOWNLOAD_ANNOTATIONS in downloader.flags:
            log.info('    * downloading annotations')
            downloader.download_annotations(url)
        if DOWNLOAD_THUMBNAIL in downloader.flags:
            log.info('    * downloading thumbnail')
            downloader.download_thumbnail(url)
        if CREATE_SUBTITLES in downloader.flags:
            log.info('    * creating subtitles')
            downloader.create_subtitles(url)

    downloader = CookingInRussiaDL(output=output, flags=flags)
    for url in urls:
        download_files(get_youtube_url(url))


@script_logging
def run_script(args):
    if args['download']:
        download_video_files(args['<url>'], args['--output'], flags=args['--flags'])


if __name__ == '__main__':
    run_script(docopt.docopt(USAGE, argv=sys.argv[1:]))
