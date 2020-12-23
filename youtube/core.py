import os, sys, urllib, shutil
import urllib.request, urllib.parse
from lxml import etree as xml
from youtube_dl import YoutubeDL


YOUTUBE_ANNOTATION_URL = "https://www.youtube.com/annotations_invideo?features=0&legacy=1&video_id=%s"


def get_youtube_url(url):
    if url.startswith("www.youtube.com/watch?v="):
        return "https://" + url
    if not url.startswith("https://www.youtube.com/watch?v="):
        return "https://www.youtube.com/watch?v=" + url
    return url


def get_youtube_video_id(url):
    data = urllib.parse.urlparse(url)
    query = urllib.parse.parse_qs(data.query)
    return query["v"][0]


def download_youtube_thumbnail(url, filename):
    request = urllib.request.Request(url)
    with urllib.request.urlopen(request) as f:
        with open(filename, "wb") as g:
            g.write(f.read())
