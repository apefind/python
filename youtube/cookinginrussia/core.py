# -*- coding: utf-8 -*-

import os, sys, urllib, shutil
import urllib.request, urllib.parse
from lxml import etree as xml
import yaml
from youtube_dl import YoutubeDL
from apefind.util.path import get_filepath_name
from apefind.youtube.core import *
from apefind.youtube.annotations import *


DOWNLOAD_VIDEO = "video"
CREATE_META_INFO = "meta_info"
DOWNLOAD_ANNOTATIONS = "annotations"
DOWNLOAD_THUMBNAIL = "thumbnail"
CREATE_SUBTITLES = "subtitles"
COPY_STAT = "stat"
DEFAULT_FLAGS = ",".join(
    [DOWNLOAD_VIDEO, CREATE_META_INFO, DOWNLOAD_ANNOTATIONS, DOWNLOAD_THUMBNAIL, CREATE_SUBTITLES, COPY_STAT]
)
