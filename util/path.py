# -*- coding: utf-8 -*-
"""Some stuff for the handling of files, directories and path
"""

import os, re, fnmatch


def get_filename_from_path(path):
    """Return the filename without extension"""
    return os.path.splitext(os.path.basename(path))[0]


def get_extension_from_path(path):
    """Return the file extension"""
    return os.path.splitext(path)[1]


def split_path(path):
    """Return directory, filename and extension (without leading .)"""
    directory, filename = os.path.split(path)
    filename, extension = os.path.splitext(filename)
    return directory, filename, extension[1:] if extension else extension


def get_expanded_path(path):
    """Expand variables and ~"""
    return os.path.expanduser(os.path.expandvars(path))


def find_files(directory, pattern='*'):
    """Use filename patterns to find files"""
    F, r = [], re.compile(fnmatch.translate(pattern))
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if r.match(filename):
                F.append(os.path.abspath(root + os.sep + filename))
    return F
    
