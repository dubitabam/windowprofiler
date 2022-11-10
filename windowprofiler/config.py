import yaml
import os
import sys

from xdg.BaseDirectory import xdg_config_home
# pylint: disable=import-error
from args import ArgParser
# pylint: enable=import-error


class Config:

    __DEFAULTS = {
        "run_as_demon": False,
        "manage_mode": False,
        "restore_window": False,
        "restore_all": False,
        "purge_window": False,
        "profile_path":  os.path.join(xdg_config_home, "windowprofiler/profiles"),
        "log_file": None,
        "log_console": False,
        "log_level": "INFO",
    }


    def __init__(self, argparser: ArgParser = None):
        self.__dict__.update(Config.__DEFAULTS)
        self.__apply_cmdline_args(argparser)


    def get(self, key: str, default = None):
        if hasattr(self, key):
            return self.__getattribute__(key) if self.__getattribute__(key) != None else default
        else:
            return default


    def __read_config_file(self, path):
        if os.path.isfile(path):

            try:
                with open(path) as file:
                    data: dict = yaml.load(file, Loader=yaml.FullLoader)

            except FileNotFoundError as e:
                print(f"error: config file not found ({path}). {e.strerror}", file=sys.stderr)
                exit(1)

            except yaml.scanner.ScannerError as e:
                print(f"error: malformed config file. {e.problem} {e.problem_mark}", file=sys.stderr)
                exit(1)

            if data:
                self.__dict__.update(data)


    def __apply_cmdline_args(self, argparser: ArgParser):
        self.run_as_demon = argparser.args.DEMON
        self.manage_mode = argparser.args.MANAGE
        self.restore_window = argparser.args.RESTORE_WINDOW
        self.restore_all = argparser.args.RESTORE_ALL
        self.purge_window = argparser.args.PURGE
        if argparser and argparser.args and argparser.args.PROFILE_PATH:
            self.profile_path = os.path.realpath(os.path.expandvars(os.path.expanduser(os.path.normpath(argparser.args.PROFILE_PATH))))
        if argparser and argparser.args and argparser.args.LOG_FILE:
            self.log_file = os.path.realpath(os.path.expandvars(os.path.expanduser(os.path.normpath(argparser.args.LOG_FILE))))
        self.log_console = argparser.args.LOG_CONSOLE
        self.log_level =  argparser.args.LOG_LEVEL.upper() if argparser.args.LOG_LEVEL else "INFO"
