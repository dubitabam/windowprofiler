#!/usr/bin/env python
from __future__ import print_function
import os
import sys
import signal
import gi

gi.require_version('Gtk', '3.0')
gi.require_version('Wnck', '3.0')

from gi.repository import Gtk
from gi.repository import Wnck
# pylint: disable=import-error
from args import ArgParser
from config import Config
from logger import Logger
from watcher import Watcher
from dialogs.manage_profiles_dialog import ManageProfilesDialog
from models.window import Window
# pylint: enable=import-error


class WindowProfiler:

    def __init__(self):

        self.__agparser = ArgParser()
        self.__config = Config(self.__agparser)
        self.__screen = Wnck.Screen.get_default()
        self.__screen.force_update()

        try:
            Logger.configure(self.__config)
        except ValueError as ex:
            self.__eprint(ex)
            exit(1)


        signal.signal(signal.SIGINT, self.__signal_handler)
        signal.signal(signal.SIGTERM, self.__signal_handler)

        if self.__config.run_as_demon:
            Watcher(self.__config)
            Gtk.main()

        elif self.__config.manage_mode:
            window = Window.get_active_wnck_window()
            dialog = ManageProfilesDialog(self.__config, window)
            dialog.show()
            dialog.destroy()

        elif self.__config.restore_window:
            window = Window.from_file(Window.get_active_wnck_window(), config=self.__config, create_new=False)
            if window:
                wnck_window: Wnck.Window = Window.get_active_wnck_window()
                if wnck_window:
                    profile_id: str = window.find_profile(wnck_window)
                    if profile_id:
                        profile = window.get_profile(profile_id)
                        if profile:
                            Logger.info(f"restoring profile '{ profile_id }' for '{ wnck_window.get_class_instance_name() } { wnck_window.get_name() }'")
                            profile.restore(wnck_window)

        elif self.__config.restore_all:
            self.__restore_all_windows()
            pass

        elif self.__config.purge_window:
            Window.unlink_window_file(
                Window.get_active_wnck_window(),
                config=self.__config,
            )
            pass

        else:
            self.__eprint(
                "no argument given. exiting...\n"
                f"use '{os.path.basename(sys.argv[0])} --help' for more help"
            )
            exit(1)


    @staticmethod
    def __eprint(*args, **kwargs):
        print(*args, file=sys.stderr, **kwargs)


    def __signal_handler(self, sig, frame):
        Gtk.main_quit()
        sys.exit(0)


    def __restore_all_windows(self):
        current_workspace = self.__screen.get_active_workspace().get_number()
        window_count = {}

        windows_on_workspace = list(
            filter(
                lambda x: Window.window_is_handleable(x) and x.get_workspace().get_number() == current_workspace,
                self.__screen.get_windows(),
            )
        )

        for wnck_window in windows_on_workspace:
            window: Window = Window.from_file(wnck_window, config=self.__config, create_new=False)
            if window:
                profile_id = window.find_profile(wnck_window, False, True)
                if profile_id:
                    profile = window.get_profile(profile_id)
                    if profile:
                        Logger.debug(f"found profile '{ profile_id }' for '{ wnck_window.get_class_instance_name() } { wnck_window.get_name() }'")
                        counter_key: str = f"{ window.class_group_name }_{ window.class_name }_{ profile_id }"

                        if not counter_key in window_count:
                            window_count[counter_key] = 0
                        window_count[counter_key] += 1

                        if profile.window_count == 0 or profile.window_count == window_count[counter_key]:
                            Logger.info(f"restoring profile '{ profile_id }' for '{ wnck_window.get_class_instance_name() } { wnck_window.get_name() }'")
                            profile.restore(wnck_window)

WindowProfiler()
