import os, sys, shutil, datetime
from lxml import etree as xml
from .core import *


def get_youtube_annotation_url(url):
    return YOUTUBE_ANNOTATION_URL % get_youtube_video_id(url)


def get_youtube_annotations(url):
    request = urllib.request.Request(get_youtube_annotation_url(url))
    with urllib.request.urlopen(request) as f:
        return xml.ElementTree(xml.fromstring(f.read()))


def get_youtube_subtitles(url):
    return get_subtitles_from_annotations(get_youtube_annotations(url))


def get_subtitles_from_file(filename):
    return get_subtitles_from_annotations(xml.parse(filename))


def get_subtitles_from_annotations(doc):
    def timestamp(h, m, s, ms):
        return datetime.time(hour=h, minute=m, second=s, microsecond=1000 * ms)

    def format_timestamp(t):
        return "%02d:%02d:%02d,%03d" % (t.hour, t.minute, t.second, t.microsecond / 1000)

    def intersect_intervals(I, J):
        if J[0] < I[0]:
            I, J = J, I
        (a0, b0, t0), (a1, b1, t1) = I, J
        if not a1 < b0:
            return []
        K = [(a0, a1, t0), (a1, min(b0, b1), t0 + "\n" + t1), (min(b0, b1), max(b0, b1), t1)]
        return [(a, b, t) for a, b, t in K if not a == b]

    def postprocess_subtitles(A):
        i, n = 0, len(A)
        while i < n - 1:
            j, K = i + 1, []
            while j < len(A):
                K = intersect_intervals(A[i], A[j])
                if K:
                    del A[i], A[j - 1]
                    A.extend(K)
                    n += len(K) - 2
                    break
                j += 1
            if not K:
                i += 1
        return sorted(A)

    def get_subtitles(doc):
        A = []
        for a in doc.getroot().xpath("annotations/annotation"):
            text, times = None, []
            for b in a:
                if b.tag == "TEXT":
                    text = "\n".join([t for t in b.text.strip().split("\n") if t.strip()])
                elif b.tag == "segment":
                    for c in b.xpath("movingRegion/rectRegion"):
                        S = c.get("t").split(".")
                        T, ms = S[0].split(":"), int(S[1])
                        h, m, s = int(T[0]) if len(T) == 3 else 0, int(T[-2]), int(T[-1])
                        times.append(timestamp(h, m, s, ms))
            if text and times:
                A.append((times[0], times[1], text))
        return postprocess_subtitles(A)

    for i, (starttime, stoptime, text) in enumerate(get_subtitles(doc)):
        yield "%d\n" % i
        yield "%s --> %s\n" % (format_timestamp(starttime), format_timestamp(stoptime))
        yield "%s\n" % (text)
        yield "\n"


def create_subtitles_from_annotations(annotations, subtitles):
    with open(subtitles, "w") as f:
        for l in get_subtitles_from_file(annotations):
            f.write(l)
