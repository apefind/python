import os

from typing import Tuple


def get_filepath_name(filepath: str) -> str:
    """Return the filename without extension"""
    return os.path.splitext(os.path.basename(filepath))[0]


def get_filepath_ext(filepath: str) -> str:
    """Return the file extension"""
    return os.path.splitext(filepath)[1]


def split_filepath(filepath: str) -> Tuple[str, str, str]:
    """Return directory, filename and extension without leading ."""
    directory, filename = os.path.split(filepath)
    filename, ext = os.path.splitext(filename)
    return directory, filename, ext[1:] if ext else ext


def expand_path(path: str) -> str:
    """Expand variables and ~"""
    return os.path.expanduser(os.path.expandvars(path))
