import os
import argparse
from xdg.BaseDirectory import xdg_config_home


class ArgParser:

    def __init__(self):
        self.__argparser = argparse.ArgumentParser(
            description = "Create and restore geometry profiles for application windows."
        )

        self.__argparser.add_argument(
            "-m", "--manage",
            help="opens a dialog to manage the profiles of the currently active window",
            dest="MANAGE",
            action="store_true",
            default=False,
        )

        self.__argparser.add_argument(
            "-r", "--restore",
            help="restores the geometry profile of the currently active window, if a saved profile exists",
            dest="RESTORE_WINDOW",
            action="store_true",
            default=False,
        )

        self.__argparser.add_argument(
            "-a", "--restore-all",
            help="restores the geometry profile for all windows on the current workspace. only works for workspace specific profiles",
            dest="RESTORE_ALL",
            action="store_true",
            default=False,
        )

        self.__argparser.add_argument(
            "-p", "--purge",
            help="deletes all saved profiles of the currently active window",
            dest="PURGE",
            action="store_true",
            default=False,
        )

        self.__argparser.add_argument(
            "-d", "--demon",
            help="run as demon and watch for newly opened windows",
            dest="DEMON",
            action="store_true",
            default=False,
        )

        self.__argparser.add_argument(
            "--profile-path",
            help=f"base path to the profile directory. default is { os.path.join(xdg_config_home, 'windowprofiler/profiles') }",
            dest="PROFILE_PATH",
            metavar="PATH",
        )

        self.__argparser.add_argument(
            "--log-file",
            help="path to the log-file. no log will be written if omitted",
            dest="LOG_FILE",
            metavar="PATH",
        )

        self.__argparser.add_argument(
            "--log-console",
            help="print log messages to console",
            dest="LOG_CONSOLE",
            action="store_true",
            default=True,
        )

        self.__argparser.add_argument(
            "--log-level",
            help="what should be logged. valid values: CRITICAL, ERROR, WARNING, INFO, DEBUG",
            dest="LOG_LEVEL",
            metavar="LEVEL",
            default="INFO",
        )

        self.args = self.__argparser.parse_args()
