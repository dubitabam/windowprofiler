import os
import gi

gi.require_version('Wnck', '3.0')

from gi.repository import Wnck
# pylint: disable=import-error
from config import Config
from logger import Logger
from models.window import Window
# pylint: enable=import-error


class Watcher:

    def __init__(self, config: Config):
        self.__config = config
        self.__screen = Wnck.Screen.get_default()
        self.__screen.connect("window-opened", self.__window_opened)
        self.__screen.connect("active-window-changed", self.__window_activated)
        Logger.info("demon started")


    def __window_opened(self, screen, wnck_window):
        try:
            window = Window.from_file(wnck_window, config=self.__config, create_new=False)
            Logger.debug(f"new window opened '{ wnck_window.get_class_instance_name() } { wnck_window.get_name() }'")

            if not window is None:
                profile_id = window.find_profile(wnck_window, True)
                if not profile_id is None:
                    profile = window.get_profile(profile_id)
                    if not profile is None:
                        Logger.info(f"restoring profile '{ profile_id }' for '{ wnck_window.get_class_instance_name() } { wnck_window.get_name() }'")
                        profile.restore(wnck_window)

                        if profile.runcmd_on_start and profile.runcmd:
                            os.system(profile.runcmd)
                            Logger.info(f"running cmd '{ profile.runcmd }' in profile '{ profile_id }' for '{ wnck_window.get_class_instance_name() } { wnck_window.get_name() }'")

                        return

            Logger.debug(f"no profile found for '{ wnck_window.get_class_instance_name() } { wnck_window.get_name() }'")

        except Exception as e:
            Logger.error(e)


    def __window_activated(self, screen, previously_active_window):
        try:
            wnck_window = self.__screen.get_active_window()
            if not wnck_window is None:
                window = Window.from_file(wnck_window, config=self.__config, create_new=False)
                Logger.debug(f"window gained focus '{ wnck_window.get_class_instance_name() } { wnck_window.get_name() }'")

                if not window is None:
                    profile_id = window.find_profile(wnck_window, False)
                    if not profile_id is None:
                        profile = window.get_profile(profile_id)
                        if not profile is None:
                            if profile.runcmd_on_focus and profile.runcmd:
                                Logger.info(f"running cmd '{ profile.runcmd }' in profile '{ profile_id }' for '{ wnck_window.get_class_instance_name() } { wnck_window.get_name() }'")
                                # os.system(profile.runcmd)
                                output = os.popen(profile.runcmd).read()
                                Logger.info(f"cmd output: { output }")
                        return

                Logger.debug(f"no profile found for '{ wnck_window.get_class_instance_name() } { wnck_window.get_name() }'")

        except Exception as e:
            Logger.error(e)
