import fnmatch
import os
import re


def get_filepath_name(filepath):
    """Return the filename without extension"""
    return os.path.splitext(os.path.basename(filepath))[0]


def get_filepath_ext(filepath):
    """Return the file extension"""
    return os.path.splitext(filepath)[1]


def split_filepath(filepath):
    """Return directory, filename and extension without leading ."""
    directory, filename = os.path.split(filepath)
    filename, ext = os.path.splitext(filename)
    return directory, filename, ext[1:] if ext else ext


def expand_path(path):
    """Expand variables and ~"""
    return os.path.expanduser(os.path.expandvars(path))


def find_files(directory, pattern="*"):
    """Use filename patterns to find files"""
    F, r = [], re.compile(fnmatch.translate(pattern))
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if r.match(filename):
                F.append(os.path.abspath(root + os.sep + filename))
    return F
