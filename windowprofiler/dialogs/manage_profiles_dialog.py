import gi
import os
import sys

gi.require_version('Gtk', '3.0')
gi.require_version('Wnck', '3.0')

from gi.repository import Gtk, Gdk
# pylint: disable=no-name-in-module
from gi.repository import Wnck
# pylint: enable=no-name-in-module
# pylint: disable=import-error
from config import Config
from models.window import Window
from models.window_profile import WindowProfile
from dialogs.message_dialog import MessageDialog
from dialogs.input_dialog import InputDialog
from dialogs.confirm_dialog import ConfirmDialog
# pylint: enable=import-error


class ManageProfilesDialog(Gtk.Window):
    """
    we call this dialog because the word window is already ambiguous in this project...
    """

    def __init__(
        self,
        config: Config,
        window: Wnck.Window,
    ):
        super().__init__(title = f"Manage profiles for '{ window.get_class_group_name() } - { window.get_class_instance_name() }'")
        self.__config: Config = config
        self.__wnck_window = window
        self.__window = Window.from_file(self.__wnck_window, config = self.__config)
        self.__current_profile: WindowProfile = None
        self.__build_ui()
        self.__clear_ui()
        self.__build_profile_combo(self.__window.find_profile(self.__wnck_window))
        self.__wnck_window.connect("geometry-changed", self.__window_geometry_changed)
        self.__wnck_window.connect("state-changed", self.__window_state_changed)


    def show(self):
        self.show_all()     # pylint: disable=no-member
        Gtk.main()


    def __clear_ui(self):
        screen = Wnck.Screen.get_default()
        self.__cmb_workspace.set_active(-1)
        self.__chk_fallback.set_active(False)
        self.__txt_resolution.set_text("")
        self.__chk_auto_apply.set_active(False)
        self.__chk_restore_pos.set_active(True)
        self.__chk_restore_size.set_active(True)
        self.__chk_restore_state.set_active(True)
        self.__btn_minimized.set_active(False)
        self.__btn_fullscreen.set_active(False)
        self.__btn_max_horizontal.set_active(False)
        self.__btn_max_vertical.set_active(False)
        self.__spn_windowcount.set_value(0)
        self.__chk_namematch.set_active(False)
        self.__chk_regex.set_active(False)
        self.__txt_name.set_text("")
        self.__spn_height.set_value(0)
        self.__spn_width.set_value(0)
        self.__spn_x.set_value(0)
        self.__spn_y.set_value(0)
        self.__txt_cmd.set_text("")
        self.__chk_cmd_on_focus.set_active(False)
        self.__chk_cmd_on_start.set_active(False)
        if not screen is None:
            self.__txt_resolution.set_text(f"{ screen.get_width() }x{ screen.get_height() }")
        else:
            self.__txt_resolution.set_text("")


    def __apply_profile_to_ui(self, profile: WindowProfile):
        if profile is None:
            self.__clear_ui()
            return

        if profile.workspace is None:
            self.__cmb_workspace.set_sensitive(False)
            self.__chk_fallback.set_active(True)
        else:
            self.__cmb_workspace.set_active(profile.workspace)
            self.__chk_fallback.set_active(False)

        self.__chk_auto_apply.set_active(profile.auto_apply)
        self.__chk_restore_size.set_active(profile.restore_size)
        self.__chk_restore_pos.set_active(profile.restore_position)
        self.__chk_restore_state.set_active(profile.restore_state)
        self.__spn_windowcount.set_value(profile.window_count)
        self.__chk_namematch.set_active(profile.match_name)
        self.__chk_regex.set_active(profile.match_regex)
        self.__txt_name.set_text(profile.name)
        self.__spn_width.set_value(profile.geometry[2])
        self.__spn_height.set_value(profile.geometry[3])
        self.__spn_x.set_value(profile.geometry[0])
        self.__spn_y.set_value(profile.geometry[1])
        self.__txt_resolution.set_text(", ".join(map(lambda x: "{}x{}".format(x[0], x[1]), profile.resolutions)))
        self.__btn_minimized.set_active(profile.state & Wnck.WindowState.MINIMIZED)
        self.__btn_max_horizontal.set_active(profile.state & Wnck.WindowState.MAXIMIZED_HORIZONTALLY)
        self.__btn_max_vertical.set_active(profile.state & Wnck.WindowState.MAXIMIZED_VERTICALLY)
        self.__btn_fullscreen.set_active(profile.state & Wnck.WindowState.FULLSCREEN)
        self.__txt_cmd.set_text(profile.runcmd)
        self.__chk_cmd_on_focus.set_active(profile.runcmd_on_focus)
        self.__chk_cmd_on_start.set_active(profile.runcmd_on_start)


    def __apply_ui_to_profile(self, profile: WindowProfile):
        profile.auto_apply = self.__chk_auto_apply.get_active()
        profile.geometry = [
            self.__spn_x.get_value(),
            self.__spn_y.get_value(),
            self.__spn_width.get_value(),
            self.__spn_height.get_value(),
        ]
        profile.match_name = self.__chk_namematch.get_active()
        profile.match_regex = self.__chk_regex.get_active()
        profile.name = self.__txt_name.get_text()
        profile.resolutions = list(map(lambda x: tuple(map(lambda y: int(y), str(x).split("x"))), str(self.__txt_resolution.get_text()).split(",")))
        profile.restore_position = self.__chk_restore_pos.get_active()
        profile.restore_size = self.__chk_restore_size.get_active()
        profile.restore_state = self.__chk_restore_state.get_active()
        profile.window_count = self.__spn_windowcount.get_value()
        profile.workspace = self.__cmb_workspace.get_active() if not self.__chk_fallback.get_active() else None
        profile.runcmd = self.__txt_cmd.get_text()
        profile.runcmd_on_start = self.__chk_cmd_on_start.get_active()
        profile.runcmd_on_focus = self.__chk_cmd_on_focus.get_active()

        if self.__btn_minimized.get_active():
            profile.state |= Wnck.WindowState.MINIMIZED
        else:
            profile.state &=~ Wnck.WindowState.MINIMIZED

        if self.__btn_max_horizontal.get_active():
            profile.state |= Wnck.WindowState.MAXIMIZED_HORIZONTALLY
        else:
            profile.state &=~ Wnck.WindowState.MAXIMIZED_HORIZONTALLY

        if self.__btn_max_vertical.get_active():
            profile.state |= Wnck.WindowState.MAXIMIZED_VERTICALLY
        else:
            profile.state &=~ Wnck.WindowState.MAXIMIZED_VERTICALLY

        if self.__btn_fullscreen.get_active():
            profile.state |= Wnck.WindowState.FULLSCREEN
        else:
            profile.state &=~ Wnck.WindowState.FULLSCREEN


    def __get_selected_profile(self):
        if self.__cmb_profile.get_active() != -1:
            return self.__window.get_profile(
                self.__cmb_profile.get_model()[self.__cmb_profile.get_active()][0],
            )
        return None


    #region UI Events

    def __window_geometry_changed(self, wnck_window: Wnck.Window):
        geometry = wnck_window.get_geometry()
        self.__spn_x.set_value(geometry[0])
        self.__spn_y.set_value(geometry[1])
        self.__spn_width.set_value(geometry[2])
        self.__spn_height.set_value(geometry[3])


    def __window_state_changed(self, wnck_window: Wnck.Window, changed_mask, new_state):
        self.__btn_minimized.set_active(new_state & Wnck.WindowState.MINIMIZED)
        self.__btn_max_horizontal.set_active(new_state & Wnck.WindowState.MAXIMIZED_HORIZONTALLY)
        self.__btn_max_vertical.set_active(new_state & Wnck.WindowState.MAXIMIZED_VERTICALLY)
        self.__btn_fullscreen.set_active(new_state & Wnck.WindowState.FULLSCREEN)


    def __window_onkeypress(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.close()
        elif event.keyval == Gdk.KEY_Return:
            self.__ok()


    def __window_onblur(self, widget, event):
        self.close()


    def __ok(self):
        if not self.__current_profile is None:
            self.__apply_ui_to_profile(self.__current_profile)
        if self.__window:
            self.__window.save_to_file(config = self.__config)
        self.close()


    def __on_btn_add_profile_clicked(self):
        while True:
            dialog = InputDialog("Add Profile", "Insert a name for the window profile", None, self)
            response = dialog.run()

            if response == Gtk.ResponseType.OK and dialog.get_value():
                profile = WindowProfile.from_window(self.__wnck_window)

                try:
                    self.__window.add_profile(
                        dialog.get_value(),
                        profile,
                    )
                except FileExistsError as ex:
                    dialog.destroy()
                    MessageDialog(ex, self)
                    continue

                self.__build_profile_combo(dialog.get_value())
                self.__apply_profile_to_ui(profile)

            dialog.destroy()
            break


    def __on_btn_edit_profile_clicked(self):
        if not self.__current_profile is None:
            old_profile_name: str = self.__cmb_profile.get_model()[self.__cmb_profile.get_active()][0]

            while True:
                dialog = InputDialog("Edit Profile", "Insert a new name for the window profile", old_profile_name, self)
                response = dialog.run()

                if response == Gtk.ResponseType.OK and dialog.get_value():
                    new_profile_name: str = dialog.get_value().strip() if dialog.get_value() else ""

                    if new_profile_name != old_profile_name:
                        if new_profile_name == "":
                            dialog.destroy()
                            continue

                        existing_profile = self.__window.get_profile(new_profile_name)
                        if existing_profile:
                            dialog.destroy()
                            MessageDialog("A profile with that name already exists. Choose another name.", self)
                            continue

                        self.__window.remove_profile(profile=self.__current_profile)
                        self.__window.add_profile(new_profile_name, self.__current_profile)
                        self.__build_profile_combo(new_profile_name)

                dialog.destroy()
                break



    def __on_btn_del_profile_clicked(self):
        if not self.__current_profile is None:
            profile_name: str = self.__cmb_profile.get_model()[self.__cmb_profile.get_active()][0]
            dialog = ConfirmDialog(f"Delete profile '{ profile_name }'", self)
            if dialog.run() == Gtk.ResponseType.YES:
                self.__window.remove_profile(profile = self.__current_profile)
                self.__build_profile_combo(self.__window.find_profile(self.__wnck_window))
            dialog.destroy()


    def __on_profile_combo_changed(self, combo):
        self.__btn_edit_profile.set_sensitive(combo.get_active() != -1)
        self.__btn_del_profile.set_sensitive(combo.get_active() != -1)
        self.__resolution_frame.set_sensitive(combo.get_active() != -1)
        self.__workspace_frame.set_sensitive(combo.get_active() != -1)
        self.__restore_frame.set_sensitive(combo.get_active() != -1)
        self.__name_frame.set_sensitive(combo.get_active() != -1)

        if not self.__current_profile is None:
            self.__apply_ui_to_profile(self.__current_profile)
        if combo.get_active() != -1:
            self.__current_profile = self.__get_selected_profile()
        else:
            self.__current_profile = None
        self.__apply_profile_to_ui(self.__current_profile)


    #endregion

    #region UI


    def __build_profile_combo(self, selected_profile: str = None):
        self.__profile_store.clear()

        idx: int = 0
        selected_index: int = None

        for key in self.__window.profiles:
            if key == selected_profile:
                selected_index = idx
            self.__profile_store.append([key])
            idx += 1

        if not selected_profile is None and not selected_index is None:
            self.__cmb_profile.set_active(selected_index)


    def __build_ui(self):
        # pylint: disable=no-member

        screen = Wnck.Screen.get_default()

        # todo: most vars can be local

        self.__grid = Gtk.Grid()

        self.connect("destroy", lambda q: Gtk.main_quit())
        self.connect('key-press-event', self.__window_onkeypress)
        # self.connect("focus-out-event", self.__window_onblur)
        self.set_name("window-properties-dialog")
        self.set_title(f"Manage profiles for '{ self.__wnck_window.get_class_group_name() } - { self.__wnck_window.get_class_instance_name() }'")
        self.set_skip_pager_hint(0)
        self.set_skip_taskbar_hint(1)
        self.set_urgency_hint(1)
        self.set_accept_focus(1)
        self.set_type_hint(1)
        self.set_keep_above(1)
        self.stick()
        self.set_focus()
        self.add(self.__grid)

        self.__grid.set_halign(Gtk.Align.CENTER)
        self.__grid.set_valign(Gtk.Align.START)
        self.__grid.set_row_spacing(10)
        self.__grid.set_margin_left(20)
        self.__grid.set_margin_right(20)
        self.__grid.set_margin_top(20)
        self.__grid.set_margin_bottom(20)

        self.__prop_box = Gtk.Box(spacing=6, orientation=Gtk.Orientation.VERTICAL)
        self.__grid.attach(self.__prop_box, 1, 2, 1, 1)

        self.__btn_box = Gtk.Box(spacing=6, orientation=Gtk.Orientation.HORIZONTAL)
        self.__grid.attach(self.__btn_box, 1, 3, 1, 1)


        # profile
        self.__profile_frame = Gtk.Frame.new("Profile")
        self.__prop_box.pack_start(self.__profile_frame, True, True, 0)

        self.__profile_box = Gtk.Box(spacing=6, orientation=Gtk.Orientation.HORIZONTAL)
        self.__profile_box.set_margin_start(10)
        self.__profile_box.set_margin_end(10)
        self.__profile_box.set_margin_top(10)
        self.__profile_box.set_margin_bottom(10)
        self.__profile_frame.add(self.__profile_box)

        profile_text_renderer = Gtk.CellRendererText()
        self.__profile_store = Gtk.ListStore(str)

        self.__cmb_profile = Gtk.ComboBox()
        self.__cmb_profile.set_model(self.__profile_store)
        self.__cmb_profile.pack_start(profile_text_renderer, True)
        self.__cmb_profile.add_attribute(profile_text_renderer, "text", 0)
        self.__cmb_profile.connect("changed", self.__on_profile_combo_changed)
        self.__profile_box.pack_start(self.__cmb_profile, True, True, 0)

        icon_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "../../icons"))
        icon_edit = Gtk.Image()
        icon_add = Gtk.Image()
        icon_del = Gtk.Image()
        icon_edit.set_from_file(os.path.join(icon_path, "edit.png"))
        icon_add.set_from_file(os.path.join(icon_path, "add.png"))
        icon_del.set_from_file(os.path.join(icon_path, "remove.png"))

        self.__btn_edit_profile = Gtk.Button()
        self.__btn_edit_profile.connect("clicked", lambda x: self.__on_btn_edit_profile_clicked())
        self.__btn_edit_profile.set_size_request(30, 30)
        self.__btn_edit_profile.set_image(icon_edit)
        self.__profile_box.pack_start(self.__btn_edit_profile, False, False, 0)

        self.__btn_add_profile = Gtk.Button.new_from_icon_name("add", Gtk.IconSize.LARGE_TOOLBAR)
        self.__btn_add_profile.connect("clicked", lambda x: self.__on_btn_add_profile_clicked())
        self.__btn_add_profile.set_size_request(30, 30)
        self.__btn_add_profile.set_image(icon_add)
        self.__profile_box.pack_start(self.__btn_add_profile, False, False, 0)

        self.__btn_del_profile = Gtk.Button.new_from_icon_name("remove", Gtk.IconSize.LARGE_TOOLBAR)
        self.__btn_del_profile.connect("clicked", lambda x: self.__on_btn_del_profile_clicked())
        self.__btn_del_profile.set_size_request(30, 30)
        self.__btn_del_profile.set_sensitive(False)
        self.__btn_del_profile.set_image(icon_del)
        self.__profile_box.pack_start(self.__btn_del_profile, False, False, 0)


        # resolution
        self.__resolution_frame = Gtk.Frame.new("Resolutions")
        self.__resolution_frame.set_sensitive(False)
        self.__prop_box.pack_start(self.__resolution_frame, True, True, 0)

        self.__resolution_box = Gtk.Box(spacing=6, orientation=Gtk.Orientation.VERTICAL)
        self.__resolution_box.set_margin_start(10)
        self.__resolution_box.set_margin_end(10)
        self.__resolution_box.set_margin_top(10)
        self.__resolution_box.set_margin_bottom(10)
        self.__resolution_frame.add(self.__resolution_box)

        self.__txt_resolution = Gtk.Entry()
        self.__resolution_box.pack_start(self.__txt_resolution, True, True, 0)

        self.__lbl_resolution = Gtk.Label(f"Comma seperated list of resolutions the profile applies to.\nThis is the combined resolution of all connected displays.\nCurrent combined resolution is { screen.get_width() }x{ screen.get_height() }.")
        self.__lbl_resolution.set_lines(3)
        self.__lbl_resolution.set_xalign(0)
        self.__resolution_box.pack_start(self.__lbl_resolution, True, True, 0)


        # workspace
        self.__workspace_frame = Gtk.Frame.new("Workspace")
        self.__workspace_frame.set_sensitive(False)
        self.__prop_box.pack_start(self.__workspace_frame, True, True, 0)

        self.__workspace_box = Gtk.Box(spacing=6, orientation=Gtk.Orientation.VERTICAL)
        self.__workspace_box.set_margin_start(10)
        self.__workspace_box.set_margin_end(10)
        self.__workspace_box.set_margin_top(10)
        self.__workspace_box.set_margin_bottom(10)
        self.__workspace_frame.add(self.__workspace_box)

        workspace_text_renderer = Gtk.CellRendererText()
        workspace_store = Gtk.ListStore(str, str)
        for ws in screen.get_workspaces():
            workspace_store.append([ws.get_name(), str(ws.get_number())])

        self.__cmb_workspace = Gtk.ComboBox()
        self.__cmb_workspace.set_model(workspace_store)
        self.__cmb_workspace.pack_start(workspace_text_renderer, True)
        self.__cmb_workspace.add_attribute(workspace_text_renderer, "text", 0)
        self.__workspace_box.pack_start(self.__cmb_workspace, True, True, 0)

        self.__chk_fallback = Gtk.CheckButton.new_with_mnemonic(label="_Global")
        self.__chk_fallback.set_active(False)
        self.__chk_fallback.connect("toggled", lambda x: self.__cmb_workspace.set_sensitive(not x.get_active()))
        self.__workspace_box.pack_start(self.__chk_fallback, True, True, 0)


        # restore options
        self.__restore_frame = Gtk.Frame.new("Restore-Options")
        self.__restore_frame.set_sensitive(False)
        self.__prop_box.pack_start(self.__restore_frame, True, True, 0)

        self.__restore_box = Gtk.Box(spacing=6, orientation=Gtk.Orientation.VERTICAL)
        self.__restore_box.set_margin_start(10)
        self.__restore_box.set_margin_end(10)
        self.__restore_box.set_margin_top(10)
        self.__restore_box.set_margin_bottom(10)
        self.__restore_frame.add(self.__restore_box)

        self.__chk_auto_apply = Gtk.CheckButton.new_with_mnemonic(label="_Auto apply on new windows")
        self.__chk_auto_apply.set_active(False)
        # self.__chk_auto_apply.connect("toggled", self.__on_auto_apply_toggled)
        self.__restore_box.pack_start(self.__chk_auto_apply, True, True, 0)


        # size
        self.__size_box = Gtk.Box(spacing=6, orientation=Gtk.Orientation.HORIZONTAL)
        self.__restore_box.pack_start(self.__size_box, True, True, 0)

        self.__chk_restore_size = Gtk.CheckButton.new_with_mnemonic(label="Restore Si_ze")
        self.__chk_restore_size.set_active(True)
        self.__chk_restore_size.connect(
            "toggled",
            lambda x: self.__spn_width.set_sensitive(x.get_active()) or self.__spn_height.set_sensitive(x.get_active())
        )
        self.__size_box.pack_start(self.__chk_restore_size, True, True, 0)

        self.__spn_width = Gtk.SpinButton.new_with_range(0, 99999, 1)
        self.__size_box.pack_start(self.__spn_width, True, True, 0)

        self.__lbl_size = Gtk.Label("x")
        self.__size_box.pack_start(self.__lbl_size, True, True, 0)

        self.__spn_height = Gtk.SpinButton.new_with_range(0, 99999, 1)
        self.__size_box.pack_start(self.__spn_height, True, True, 0)


        # position
        self.__pos_box = Gtk.Box(spacing=6, orientation=Gtk.Orientation.HORIZONTAL)
        self.__restore_box.pack_start(self.__pos_box, True, True, 0)

        self.__chk_restore_pos = Gtk.CheckButton.new_with_mnemonic(label="Restore _Position")
        self.__chk_restore_pos.set_active(True)
        self.__chk_restore_pos.connect(
            "toggled",
            lambda x: self.__spn_x.set_sensitive(x.get_active()) or self.__spn_y.set_sensitive(x.get_active())
        )
        self.__pos_box.pack_start(self.__chk_restore_pos, True, True, 0)

        self.__spn_x = Gtk.SpinButton.new_with_range(0, 99999, 1)
        self.__pos_box.pack_start(self.__spn_x, True, True, 0)

        self.__lbl_pos = Gtk.Label("x")
        self.__pos_box.pack_start(self.__lbl_pos, True, True, 0)

        self.__spn_y = Gtk.SpinButton.new_with_range(0, 99999, 1)
        self.__pos_box.pack_start(self.__spn_y, True, True, 0)


        # state
        state_grid = Gtk.Grid()
        state_grid.set_halign(Gtk.Align.START)
        state_grid.set_valign(Gtk.Align.START)
        state_grid.set_column_spacing(20)
        self.__restore_box.pack_start(state_grid, True, True, 0)

        self.__chk_restore_state = Gtk.CheckButton.new_with_mnemonic(label="Restore _State")
        self.__chk_restore_state.set_active(True)
        self.__chk_restore_state.connect("toggled", lambda x: self.__state_button_box.set_sensitive(x.get_active()))
        state_grid.attach(self.__chk_restore_state, 0, 0, 1, 1)

        self.__state_button_box = Gtk.FlowBox()
        self.__state_button_box.set_valign(Gtk.Align.START)
        self.__state_button_box.set_halign(Gtk.Align.START)
        self.__state_button_box.set_max_children_per_line(2)
        self.__state_button_box.set_min_children_per_line(2)
        self.__state_button_box.set_selection_mode(Gtk.SelectionMode.NONE)
        state_grid.attach(self.__state_button_box, 1, 0, 1, 1)

        self.__btn_minimized = Gtk.ToggleButton(label="Minimized")
        self.__state_button_box.add(self.__btn_minimized)
        self.__btn_max_horizontal = Gtk.ToggleButton(label="Maximized Horizontally")
        self.__state_button_box.add(self.__btn_max_horizontal)
        self.__btn_fullscreen = Gtk.ToggleButton(label="Fullscreen")
        self.__state_button_box.add(self.__btn_fullscreen)
        self.__btn_max_vertical = Gtk.ToggleButton(label="Maximized Vertically")
        self.__state_button_box.add(self.__btn_max_vertical)


        # window count
        self.__spinner_grid = Gtk.Grid()
        self.__spinner_grid.set_halign(Gtk.Align.END)
        self.__spinner_grid.set_valign(Gtk.Align.START)
        self.__spinner_grid.set_column_spacing(10)
        self.__restore_box.pack_start(self.__spinner_grid, True, True, 0)

        self.__lbl_windowcount = Gtk.Label("Apply only on the nth window (0 = all windows)")
        self.__lbl_windowcount.set_xalign(0)
        self.__lbl_windowcount.set_justify(Gtk.Justification.LEFT)
        self.__spinner_grid.attach(self.__lbl_windowcount, 0, 1, 1, 1)

        self.__spn_windowcount = Gtk.SpinButton.new_with_range(0, 255, 1)
        self.__spinner_grid.attach(self.__spn_windowcount, 1, 1, 1, 1)


        # name match
        self.__name_frame = Gtk.Frame.new("Additional-Options")
        self.__name_frame.set_sensitive(False)
        self.__prop_box.pack_start(self.__name_frame, True, True, 0)

        self.__name_box = Gtk.Box(spacing=6, orientation=Gtk.Orientation.VERTICAL)
        self.__name_box.set_margin_start(10)
        self.__name_box.set_margin_end(10)
        self.__name_box.set_margin_top(10)
        self.__name_box.set_margin_bottom(10)
        self.__name_frame.add(self.__name_box)

        self.__chk_namematch = Gtk.CheckButton.new_with_mnemonic(label="_Match window title")
        self.__chk_namematch.set_active(False)
        self.__chk_namematch.connect("toggled", lambda x: self.__chk_regex.set_sensitive(x.get_active()) or self.__txt_name.set_sensitive(x.get_active()))
        self.__name_box.pack_start(self.__chk_namematch, True, True, 0)

        self.__chk_regex = Gtk.CheckButton.new_with_mnemonic(label="Use _Regex")
        self.__chk_regex.set_active(False)
        self.__chk_regex.set_sensitive(False)
        self.__name_box.pack_start(self.__chk_regex, True, True, 0)

        self.__txt_name = Gtk.Entry()
        self.__txt_name.set_sensitive(False)
        self.__name_box.pack_start(self.__txt_name, True, True, 0)


        # run cmd
        self.__cmd_frame = Gtk.Frame.new("Run command when window")
        # self.__cmd_frame.set_sensitive(False)
        self.__prop_box.pack_start(self.__cmd_frame, True, True, 0)

        self.__cmd_box = Gtk.Box(spacing=6, orientation=Gtk.Orientation.VERTICAL)
        self.__cmd_box.set_margin_start(10)
        self.__cmd_box.set_margin_end(10)
        self.__cmd_box.set_margin_top(10)
        self.__cmd_box.set_margin_bottom(10)
        self.__cmd_frame.add(self.__cmd_box)

        self.__chk_cmd_on_start = Gtk.CheckButton.new_with_mnemonic(label="is _opened")
        self.__chk_cmd_on_start.set_active(False)
        self.__chk_cmd_on_start.connect("toggled", lambda x: self.__txt_cmd.set_sensitive(x.get_active() or self.__chk_cmd_on_focus.get_active()))
        self.__cmd_box.pack_start(self.__chk_cmd_on_start, True, True, 0)

        self.__chk_cmd_on_focus = Gtk.CheckButton.new_with_mnemonic(label="gains _focus")
        self.__chk_cmd_on_focus.set_active(False)
        self.__chk_cmd_on_focus.connect("toggled", lambda x: self.__txt_cmd.set_sensitive(x.get_active() or self.__chk_cmd_on_start.get_active()))
        self.__cmd_box.pack_start(self.__chk_cmd_on_focus, True, True, 0)

        self.__txt_cmd = Gtk.Entry()
        self.__txt_cmd.set_sensitive(False)
        self.__cmd_box.pack_start(self.__txt_cmd, True, True, 0)


        # buttons
        self.__btn_ok = Gtk.Button.new_with_mnemonic(label="O_k")
        self.__btn_ok.connect("clicked", lambda x: self.__ok())
        self.__btn_ok.set_size_request(120, 30)
        self.__btn_box.pack_start(self.__btn_ok, True, True, 0)

        self.__btn_cancel = Gtk.Button.new_with_mnemonic(label="_Cancel")
        self.__btn_cancel.connect("clicked", lambda x: self.close())
        self.__btn_cancel.set_size_request(120, 30)
        self.__btn_box.pack_start(self.__btn_cancel, True, True, 0)


    #endregion
