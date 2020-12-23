#!/usr/bin/env python3

import os
import shutil
import sys

import docopt

from apefind.util import script
from apefind.util.path import get_filepath_name
from apefind.youtube.annotations import create_subtitles_from_annotations

log = script.get_logger()

USAGE = """usage:
    annotations2srt.py [--copy-stat] [--output=<output>] <annotation>...
"""


def create_subtitles(annotations, subtitles, copy_stat=False):
    create_subtitles_from_annotations(annotations, subtitles)
    if copy_stat:
        shutil.copystat(annotations, subtitles)


def convert_annotations(annotations, output, copy_stat=False):
    def get_srt_filename(annotation, output):
        filename = get_filepath_name(annotation)
        if not output:
            return filename + ".srt"
        if os.path.isdir(output):
            return output + os.sep + filename + ".srt"
        return output

    log.info("    * converting annotations to subtitles")
    for annotation in annotations:
        log.info("         " + annotation)
        subtitles = get_srt_filename(annotation, output)
        with open(subtitles, "w") as f:
            log.info("             => " + subtitles)
            create_subtitles(annotation, subtitles, copy_stat)


@script.run()
def run_script(args):
    convert_annotations(args["<annotation>"], args["--output"], args["--copy-stat"])


if __name__ == "__main__":
    run_script(docopt.docopt(USAGE, argv=sys.argv[1:]))
