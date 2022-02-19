import os
import sys
from logging import *

try:
    from colorlog import ColoredFormatter

    COLOR_FORMATTER = ColoredFormatter(
        "%(log_color)s%(message)s%(reset)s",
        log_colors={
            "DEBUG": "black,bg_white",
            "WARNING": "cyan",
            "ERROR": "bold_red",
            "CRITICAL": "white,bg_red",
        },
    )
except ImportError:
    COLOR_FORMATTER = None


def expand_logfile_path(logfile):
    filepath = os.path.abspath(os.path.expandvars(os.path.expanduser(logfile)))
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    return filepath


def get_logger(name, logfile=None, mode="w", color_formatter=None):
    logger = getLogger(name)
    if not hasattr(logger, "console"):
        logger.console = StreamHandler(sys.stdout)
        if color_formatter:
            try:
                if logger.console.stream.isatty():
                    logger.console.setFormatter(color_formatter)
            except:
                pass
        logger.addHandler(logger.console)
        logger.setLevel(DEBUG)
        logger.console.setLevel(INFO)
    if not hasattr(logger, "logfile"):
        if logfile is not None:
            logger.file = FileHandler(logfile, mode)
            logger.file.filepath = logfile
            logger.addHandler(logger.file)
            logger.file.setLevel(DEBUG)
    return logger


def get_console_logger(name, color_formatter=COLOR_FORMATTER):
    return get_logger(name, color_formatter=color_formatter)
