# -*- coding: utf-8 -*-

import os, sys, time
from logging import *
from logging import handlers
try:
    from colorlog import ColoredFormatter
    COLOR_FORMATTER = ColoredFormatter('%(log_color)s%(message)s%(reset)s', log_colors={
        'DEBUG': 'cyan',
        'WARNING': 'yellow',
        'ERROR': 'bold_red',
        'CRITICAL': 'bold_red',
    })
except ImportError as e:
    COLOR_FORMATTER = None


def expand_logfile_path(logfile):
    filename = os.path.abspath(os.path.expandvars(os.path.expanduser(logfile)))
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    return filename


def get_logger(name, logfile, mode='w', color_formatter=None):
    logger = getLogger(name)
    logger.console = StreamHandler(sys.stdout)
    if color_formatter:
        try:
            if logger.console.stream.isatty():
                logger.console.setFormatter(color_formatter)
        except Exception as e:
            pass
    logger.file = FileHandler(logfile, mode)
    logger.file.filename = logfile
    logger.addHandler(logger.console)
    logger.addHandler(logger.file)
    logger.setLevel(DEBUG)
    logger.console.setLevel(INFO)
    logger.file.setLevel(DEBUG)
    return logger
