# -*- coding: utf-8 -*-

import os, sys, functools
from datetime import datetime
from apefind.util.logging import expand_logfile_path, get_logger, COLOR_FORMATTER


def get_script_name():
    return os.path.splitext(os.path.basename(sys.modules['__main__'].__file__))[0]


def get_script_logger(name=None, logfile=None, mode='w', color_formatter=COLOR_FORMATTER):
    if name is None:
        name = get_script_name()
    if logfile is None:
        logfile = expand_logfile_path('~/.' + name + '.log')
    return get_logger(name, logfile, mode, color_formatter)


def script_logging(log, name=None):

    def _logging(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            t0 = datetime.now()
            log.info('This is %s, %s' % (get_script_name() if name is None else name, t0.strftime('%c')))
            try:
                return f(*args, **kwargs)
            except Exception as e:
                log.warning('    * an error occurred')
                log.error('        => ' + str(e))
                raise
            finally:
                t1 = datetime.now()
                log.info('    * terminated at ' + t1.strftime('%c') + ', total duration ' + str(t1 - t0).split('.')[0])
                log.info('done')
        return wrapper

    return _logging
