# -*- coding: utf-8 -*-

from .core import *


class CookingInRussiaDL(YoutubeDL):

    def __init__(self, params=None, auto_init=True, output=None, flags=DEFAULT_FLAGS):

        class Logger:
            def debug(self, msg): pass
            def warning(self, msg): pass
            def error(self, msg): pass

        self.output, self.flags = output, flags
        if params is None:
            params = {}
        params['logger'] = Logger()
        params['outtmpl'] = output + os.sep + '%(title)s.%(ext)s'
        super().__init__(params=params, auto_init=auto_init)
        self.add_default_info_extractors()

    def get_info(self, url):
        self.info = self.extract_info(url, download=False)

    def download_video(self, url):
        super().download([url])

    def create_meta_info(self, url):
        filename = self.get_filename('.yaml')
        with open(filename, 'w') as f:
            f.write(yaml.dump(self.info, default_flow_style=False, indent=4))
        self.set_stat(filename)

    def download_annotations(self, url):
        filename, annotations = self.get_filename('.xml'), get_youtube_annotations(url)
        with open(filename, 'wb') as f:
            f.write(xml.tostring(annotations.getroot(), pretty_print=True))
        self.set_stat(filename)

    def download_thumbnail(self, url):
        url = self.info.get('thumbnail')
        if url is not None:
            filename = self.get_filename(os.path.splitext(url)[1])
            download_youtube_thumbnail(url, filename)
            self.set_stat(filename)

    def create_subtitles(self, url):
        filename, annotations = self.get_filename('.srt'), get_youtube_annotations(url)
        with open(filename, 'w') as f:
            for l in get_subtitles_from_annotations(annotations):
                f.write(l)
        self.set_stat(filename)

    def get_filename(self, ext):
        return os.path.splitext(self.prepare_filename(self.info))[0] + ext

    def get_video_filename(self):
        for ext in ['.mp4', '.mkv', ]:
            filename = self.get_filename(ext)
            if os.path.isfile(filename):
                return filename
        return self.prepare_filename(self.info)  # not always correct!?

    def set_stat(self, filename):
        if COPY_STAT in self.flags:
            video = self.get_video_filename()
            if video is not None and os.path.isfile(video):
                shutil.copystat(video, filename)
