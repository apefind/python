#!/usr/bin/env python3

import sys

import docopt

from apefind.util import script
from apefind.youtube import cookinginrussia

log = script.get_logger()

USAGE = """usage:
    {script_name} download [--flags=<flags>] [--output=<output>] <url>...

options:
    --flags FLAGS    comma separated options [default: {default_flags}]
    --output OUTPUT  output directory [default: .]
""".format(
    script_name=script.get_script_name(), default_flags=cookinginrussia.DEFAULT_FLAGS
)


def download_video_files(urls, output, flags):
    def download_files(url):
        log.info("    * processing " + url)
        downloader.get_info(url)
        log.info("        " + downloader.info["title"])
        if cookinginrussia.DOWNLOAD_VIDEO in downloader.flags:
            log.info("    * downloading video")
            downloader.download_video(url)
        if cookinginrussia.CREATE_META_INFO in downloader.flags:
            log.info("    * creating meta info")
            downloader.create_meta_info(url)
        if cookinginrussia.DOWNLOAD_ANNOTATIONS in downloader.flags:
            log.info("    * downloading annotations")
            downloader.download_annotations(url)
        if cookinginrussia.DOWNLOAD_THUMBNAIL in downloader.flags:
            log.info("    * downloading thumbnail")
            downloader.download_thumbnail(url)
        if cookinginrussia.CREATE_SUBTITLES in downloader.flags:
            log.info("    * creating subtitles")
            downloader.create_subtitles(url)

    downloader = cookinginrussia.CookingInRussiaDL(output=output, flags=flags)
    for url in urls:
        download_files(cookinginrussia.get_youtube_url(url))


@script.run()
def run_script(args):
    if args["download"]:
        download_video_files(args["<url>"], args["--output"], flags=args["--flags"])


if __name__ == "__main__":
    run_script(docopt.docopt(USAGE, argv=sys.argv[1:]))
