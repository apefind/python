import argparse
import functools
import json
import os
import sys
import yaml
from datetime import datetime

from termcolor import colored as _col

from . import logging as _logging
from .path import expand_path


def _red(*args, **kwargs):
    return _col(*args, **kwargs, color="red")


def _grn(*args, **kwargs):
    return _col(*args, **kwargs, color="green")


def _blu(*args, **kwargs):
    return _col(*args, **kwargs, color="blue")


def _yel(*args, **kwargs):
    return _col(*args, **kwargs, color="yellow")


_ok = _grn("✔")
_nok = _red("✗")


def get_script_name():
    return os.path.splitext(os.path.basename(sys.modules["__main__"].__file__))[0]


def get_logger(name=None, logfile=None, mode="w", color_formatter=_logging.COLOR_FORMATTER):
    if name is None:
        name = get_script_name()
    return _logging.get_logger(name, logfile, mode, color_formatter)


def run(name=None, log=None):
    def _run(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            t0 = datetime.now()
            log.info(f"This is {name}, {t0.strftime('%c')}")
            try:
                return f(*args, **kwargs)
            except Exception as err:
                log.warning("    * an error occurred")
                log.error(f"        => {err}")
                raise
            finally:
                t1 = datetime.now()
                duration = str(t1 - t0).split(".")[0]
                log.info(f"    * terminated at {t1.strftime('%c')}, total duration {duration}")
                log.info("done")

        return wrapper

    if name is None:
        name = get_script_name()
    if log is None:
        log = get_logger(name)
    return _run


class ArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args, fromfile_prefix_chars="@", **kwargs):
        super().__init__(*args, fromfile_prefix_chars=fromfile_prefix_chars, **kwargs)

    def add_commands(self, *args, dest="cmd", **kwargs):
        self.cmds = self.add_subparsers(*args, dest=dest, **kwargs)
        self._cmds = {}

    def add_command(self, name, **kwargs):
        cmd = self.cmds.add_parser(name, **kwargs)
        self._cmds[name] = cmd
        return cmd

    def set_command_defaults(self, name, *args, **kwargs):
        self._cmds[name].set_defaults(*args, **kwargs)

    def parse_args(self, args=None, namespace=None, defaults=None):
        if defaults is not None:
            if isinstance(defaults, str):
                defaults = (defaults,)
            for cfg in defaults:
                self.read_defaults(cfg)
        return super().parse_args(args=args, namespace=namespace)

    def read_defaults(self, cfg):
        try:
            with open(expand_path(cfg), "r") as f:
                defaults = yaml.load(f, Loader=yaml.FullLoader)
        except FileNotFoundError:
            return
        for k, v in defaults.items():
            if not isinstance(v, dict):
                self.set_defaults(**{k: v})
            else:
                self.set_command_defaults(k, **v)  # sub command dict

    def _read_args_from_files(self, arg_strings):
        new_arg_strings = []
        for arg_string in arg_strings:
            if not arg_string or arg_string[0] not in self.fromfile_prefix_chars:
                new_arg_strings.append(arg_string)
            else:
                filepath = arg_string[1:]
                try:
                    if filepath.lower().endswith(".json"):
                        with open(filepath) as f:
                            args = json.load(f)
                            if isinstance(args, dict):
                                for k, v in args.items():
                                    if isinstance(v, bool):
                                        if v:
                                            new_arg_strings.append(k)  # boolean flags
                                    else:
                                        new_arg_strings.append(k)
                                        new_arg_strings.append(str(v))
                            else:
                                for arg in args:
                                    new_arg_strings.append(str(arg))
                    else:
                        with open(filepath) as args_file:
                            arg_strings = []
                            for arg_line in args_file.read().splitlines():
                                for arg in self.convert_arg_line_to_args(arg_line):
                                    arg_strings.append(arg)
                            arg_strings = self._read_args_from_files(arg_strings)
                            new_arg_strings.extend(arg_strings)
                except (OSError, json.JSONDecodeError):
                    err = sys.exc_info()[1]
                    self.error(str(err))
        return new_arg_strings

    def _format_help(self):
        formatter = self._get_formatter()
        formatter.add_usage(self.usage, self._actions, self._mutually_exclusive_groups)
        formatter.add_text(self.description)
        for action_group in self._action_groups:
            formatter.start_section(action_group.title)
            formatter.add_text(action_group.description)
            formatter.add_arguments(action_group._group_actions)
            formatter.end_section()
        args = {}
        for action_group in self._action_groups:
            for action in action_group._group_actions:
                if not action.default == argparse.SUPPRESS and action.option_strings:
                    args[action.option_strings[-1]] = str(action.default)
        formatter.start_section("json default")
        formatter._add_item(lambda t: t, [json.dumps(args, indent=4)])  # for now ...
        formatter.end_section()
        formatter.add_text(self.epilog)
        return formatter.format_help()
