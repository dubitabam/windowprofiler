import os
import json
import gi
import re

gi.require_version('Wnck', '3.0')

from gi.repository import Wnck
from types import SimpleNamespace
# pylint: disable=import-error
from models.window_profile import WindowProfile
from config import Config
# pylint: enable=import-error


class Window:

    def __init__(
        self,
        class_name: str = None,
        class_group_name: str = None,
        application: str = None,
        role: str = None,
        window_type: int = None,
    ):
        self.class_name: str = class_name
        self.class_group_name: str = class_group_name
        self.application: str = application
        self.role: str = role
        self.window_type: int = window_type
        self.profiles: set[WindowProfile] = {}


    @classmethod
    def from_window(cls, window: Wnck.Window):
        if not isinstance(window, Wnck.Window):
            raise Exception("paramter window is not of type Wnck.Window")

        return cls(
            window.get_class_instance_name(),
            window.get_class_group_name(),
            window.get_application().get_name() if window.get_application() else None,
            window.get_role(),
            window.get_window_type(),
        )


    @classmethod
    def from_file(
        cls,
        window: Wnck.Window,
        config: Config = None,
        profile_dir: str = None,
        create_new: bool = True
    ):
        """
        creates a window object from a json file.
        basically the same as from_json() but build the path etc.

        if no file for the window exists and create_new is True,
        a default window object is created.
        """
        if not isinstance(window, Wnck.Window):
            raise Exception("parameter window is not of type Wnck.Window")

        if isinstance(config, Config):
            path = config.profile_path
        elif not profile_dir is None:
            path = profile_dir
        else:
            raise Exception("keyword parameter 'config' or 'profile_dir' is required")

        filename = cls.get_window_filename(window)
        # path = "/home/d/projects/python/window-profiler/profiles"

        if os.path.isfile(f"{ path }/{ filename }"):
            with open(os.path.expanduser(f"{ path }/{ filename }")) as fd:
                return Window.from_json(fd)

        return Window.from_window(window) if create_new else None


    @classmethod
    def from_json_path(cls, path: str):
        with open(os.path.expanduser(path)) as fd:
            return cls.from_json(fd)


    @classmethod
    def from_json(cls, fd):
        simple_object = json.load(fd, object_hook=lambda d: SimpleNamespace(**d))

        if not hasattr(simple_object, "class_name") \
           or not hasattr(simple_object, "class_group_name") \
           or not hasattr(simple_object, "application") \
           or not hasattr(simple_object, "role") \
           or not hasattr(simple_object, "window_type"):
            raise Exception("invalid json file")

        window = cls(
            simple_object.class_name,
            simple_object.class_group_name,
            simple_object.application,
            simple_object.role,
            simple_object.window_type,
        )

        if hasattr(simple_object, "profiles"):
            for key in simple_object.profiles.__dict__:
                window.add_profile(
                    key,
                    WindowProfile.from_json(json.dumps(simple_object.profiles.__dict__[key].__dict__)),
                )

        return window


    @staticmethod
    def window_is_handleable(wnck_window: Wnck.Window):
        return isinstance(wnck_window, Wnck.Window) \
                and (wnck_window.get_state() & Wnck.WindowState.HIDDEN == 0 or wnck_window.get_state() & Wnck.WindowState.MINIMIZED) \
                and wnck_window.get_window_type() == Wnck.WindowType.NORMAL \
                and wnck_window.get_workspace()


    @staticmethod
    def get_window_filename(window: Wnck.Window) -> str:
        """ returns the json filename for the window, including file extension """
        if not isinstance(window, Wnck.Window):
            raise Exception("paramter window is not of type Wnck.Window")
        return f"{ window.get_class_group_name() }_{ window.get_class_instance_name() }.json"


    @staticmethod
    def get_active_wnck_window() -> Wnck.Window:
        screen = Wnck.Screen.get_default()
        try:
            screen.force_update()
        except:
            pass
        return screen.get_active_window()


    @staticmethod
    def unlink_window_file(
        window: Wnck.Window,
        config: Config = None,
        profile_dir: str = None,
    ):
        """ deletes the json file for the window """

        if not isinstance(window, Wnck.Window):
            raise Exception("parameter window is not of type Wnck.Window")

        if isinstance(config, Config):
            path = config.profile_path
        elif not profile_dir is None:
            path = profile_dir
        else:
            raise Exception("keyword parameter 'config' or 'profile_dir' is required")

        path += f"/{ Window.get_window_filename(window) }"

        if os.path.isfile(path):
            os.unlink(path)


    def to_json(self) -> str:
        return json.dumps(
            self.__dict__,
            skipkeys    = True,
            default     = self.__json_filter,
            indent      = 2,
        )


    def save_to_file(
        self,
        config: Config = None,
        profile_dir: str = None,
    ):
        if isinstance(config, Config):
            path = config.profile_path
        elif not profile_dir is None:
            path = profile_dir
        else:
            raise Exception("keyword parameter 'config' or 'profile_dir' is required")

        # path = "/home/d/projects/python/window-profiler/profiles"
        filename = f"{ self.class_group_name }_{ self.class_name }.json"

        if len(self.profiles.keys()) == 0:
            if os.path.isfile(f"{path}/{filename}"):
                os.unlink(f"{path}/{filename}")
            return

        os.makedirs(path, exist_ok = True)
        with open(f"{ path }/{ filename }", "w") as fd:
            fd.write(self.to_json())


    def get_profile(self, profile_id: str) -> WindowProfile:
        if profile_id in self.profiles and isinstance(self.profiles[profile_id], WindowProfile):
            return self.profiles[profile_id]
        return None


    def get_profile_id(self, profile: WindowProfile) -> str:
        if profile is None:
            return None

        profile_id = [key for key, value in self.profiles.items() if value == profile]
        if len(profile_id) < 1:
            return None

        return profile_id[0]


    def add_profile(self, profile_id: str, profile: WindowProfile):
        if not self.get_profile(profile_id) is None:
            raise FileExistsError("A profile with this name already exists")
        self.profiles[profile_id] = profile


    def remove_profile(self, profile_id: str = None, profile: WindowProfile = None) -> WindowProfile:
        if profile is None and profile_id is None:
            raise Exception("missing keyword argument 'profile' or 'profile_id'")

        if profile is None:
            profile = self.get_profile(profile_id)
        else:
            profile_id = [key for key, value in self.profiles.items() if value == profile]
            if len(profile_id) < 1:
                return None
            profile_id = profile_id[0]

        if not profile is None:
            del self.profiles[profile_id]

        return profile


    def find_similar_windows(
        self,
        window: Wnck.Window,
    ):
        if not isinstance(window, Wnck.Window):
            raise Exception("parameter window is not of type Wnck.Window")

        screen: Wnck.Screen = Wnck.Screen.get_default()
        windows: list[Wnck.Window] = []

        try:
            screen.force_update()
        except:
            pass

        for win in screen.get_windows():
            if Window.window_is_handleable(win) and \
                win.get_workspace().get_number() == window.get_workspace().get_number() and \
                win.get_class_group_name() == window.get_class_group_name() and \
                win.get_class_instance_name() == window.get_class_instance_name():
                windows.append(win)

        return windows


    def find_matching_windows(self, profile: WindowProfile) -> list[Wnck.Window]:

        screen: Wnck.Screen = Wnck.Screen.get_default()
        res: tuple[int, int] = tuple([screen.get_width(), screen.get_height()])

        try:
            screen.force_update()
        except:
            pass

        if not next(filter(lambda x: x[0] == res[0] and x[1] == res[1], profile.resolutions), False):
            return []

        def filter_func(window: Wnck.Window):
            name_lower: str = window.get_name().lower().strip()
            return (
                        (window.get_workspace() and profile.workspace == window.get_workspace().get_number())
                        or
                        profile.workspace is None
                    ) \
                    and \
                    (
                        window.get_class_instance_name() == self.class_name
                        and
                        window.get_class_group_name() == self.class_group_name
                    ) \
                    and \
                    (
                        not profile.match_name or not profile.name
                        or
                        (not profile.match_regex and name_lower == profile.name.lower().strip())
                        or
                        (profile.match_regex and re.search(profile.name.strip(), name_lower, re.IGNORECASE))
                    )

        return list(filter(filter_func, screen.get_windows()))


    def find_profile(
        self,
        window: Wnck.Window,
        auto_apply_only: bool = False,
        ignore_window_count: bool = False,
    ) -> str:

        screen = window.get_screen()
        res: tuple[int, int] = tuple([screen.get_width(), screen.get_height()])
        name_lower: str = window.get_name().lower().strip()

        def filter_func(key):
            window_count: int = len(self.find_matching_windows(self.profiles[key]))
            return (
                        (window.get_workspace() and self.profiles[key].workspace == window.get_workspace().get_number())
                        or
                        self.profiles[key].workspace is None
                    ) \
                    and \
                    (
                        self.profiles[key].resolutions is None
                        or
                        next(filter(lambda x: x[0] == res[0] and x[1] == res[1], self.profiles[key].resolutions), False)
                    ) \
                    and \
                    (
                        not self.profiles[key].match_name or not self.profiles[key].name
                        or
                        (not self.profiles[key].match_regex and name_lower == self.profiles[key].name.lower().strip())
                        or
                        (self.profiles[key].match_regex and re.search(self.profiles[key].name.strip(), name_lower, re.IGNORECASE))
                    ) \
                    and \
                    (
                        ignore_window_count or
                        self.profiles[key].window_count == 0 or self.profiles[key].window_count is None
                        or
                        window_count == self.profiles[key].window_count
                    ) \
                    and \
                    (
                        not auto_apply_only
                        or
                        (auto_apply_only and self.profiles[key].auto_apply)
                    )

        return next(filter(filter_func, self.profiles), None)


    def __json_filter(self, o):
        return o.__dict__ if isinstance(o, WindowProfile) else None
