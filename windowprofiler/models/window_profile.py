import time
import json
import gi
gi.require_version('Wnck', '3.0')
from gi.repository import Wnck
from types import SimpleNamespace


class WindowProfile:
    def __init__(
        self,
        resolutions: list[tuple[int, int]] = None,
        workspace: int = None,
        name: str = None,
        match_name: bool = False,
        match_regex: bool = False,
        auto_apply: bool = True,
        window_count: int = 0,
        restore_size: bool = True,
        restore_position: bool = True,
        restore_state: bool = True,
        state = None,
        geometry = None,
    ):
        self.resolutions: list[tuple[int, int]] = resolutions
        self.workspace: int = workspace
        self.name: str = name
        self.match_name: bool = match_name
        self.match_regex: bool = match_regex
        self.auto_apply: bool = auto_apply
        self.window_count: int = window_count
        self.restore_size: bool = restore_size
        self.restore_position: bool = restore_position
        self.restore_state: bool = restore_state
        self.state: int = state
        self.geometry = geometry


    @classmethod
    def from_window(cls, window: Wnck.Window):
        """
        creates a default profile for the given wnck window
        """
        if not isinstance(window, Wnck.Window):
            raise Exception("parameter window is not of type Wnck.Window")

        screen = window.get_screen()
        if screen is None:
            raise Exception("can't get screen from window")

        return cls(
            resolutions = [(screen.get_width(), screen.get_height())],
            workspace = window.get_workspace().get_number() if not window.get_workspace() is None else None,
            name = window.get_name(),
            geometry = window.get_geometry(),
            state = window.get_state(),
        )


    @classmethod
    def from_json(cls, json_data: str):
        """
        creates a profile from a json string
        """
        simple_object = json.loads(json_data, object_hook=lambda d: SimpleNamespace(**d))
        return cls(
            list(map(lambda x: tuple(x), simple_object.resolutions)) if hasattr(simple_object, "resolutions") else None,
            simple_object.workspace if hasattr(simple_object, "workspace") else None,
            simple_object.name if hasattr(simple_object, "name") else None,
            simple_object.match_name if hasattr(simple_object, "match_name") else False,
            simple_object.match_regex if hasattr(simple_object, "match_regex") else False,
            simple_object.auto_apply if hasattr(simple_object, "auto_apply") else False,
            simple_object.window_count if hasattr(simple_object, "window_count") else 0,
            simple_object.restore_size if hasattr(simple_object, "restore_size") else True,
            simple_object.restore_position if hasattr(simple_object, "restore_position") else True,
            simple_object.restore_state if hasattr(simple_object, "restore_state") else True,
            simple_object.state if hasattr(simple_object, "state") else None,
            simple_object.geometry if hasattr(simple_object, "geometry") else None,
        )


    def restore(
        self,
        window: Wnck.Window,
    ):
        """
        restores a profile by changing the window size, position & state
        """
        if self.restore_state:
            if self.state & Wnck.WindowState.MAXIMIZED_HORIZONTALLY:
                window.maximize_horizontally()
            elif window.is_maximized_horizontally():
                window.unmaximize_horizontally()

            if self.state & Wnck.WindowState.MAXIMIZED_VERTICALLY:
                window.maximize_vertically()
            elif window.is_maximized_vertically():
                window.unmaximize_vertically()

            if self.state & Wnck.WindowState.FULLSCREEN:
                window.set_fullscreen(True)
            elif window.is_fullscreen():
                window.set_fullscreen(False)

            if self.state & Wnck.WindowState.MINIMIZED:
                window.minimize()
            elif window.is_minimized():
                window.unminimize(time.time())

        geometry_mask = 0
        if self.restore_position:
            geometry_mask = geometry_mask | Wnck.WindowMoveResizeMask.X
            geometry_mask = geometry_mask | Wnck.WindowMoveResizeMask.Y
        if self.restore_size:
            geometry_mask = geometry_mask | Wnck.WindowMoveResizeMask.WIDTH
            geometry_mask = geometry_mask | Wnck.WindowMoveResizeMask.HEIGHT

        window.set_geometry(
            Wnck.WindowGravity.STATIC,
            Wnck.WindowMoveResizeMask(geometry_mask),
            self.geometry[0],
            self.geometry[1],
            self.geometry[2],
            self.geometry[3],
        )
