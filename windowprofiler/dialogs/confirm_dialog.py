import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class ConfirmDialog(Gtk.MessageDialog):

    def __init__(
        self,
        text: str,
        parent = None,
    ):
        super().__init__(
            parent = parent,
            modal = True,
            text = text,
            buttons = Gtk.ButtonsType.YES_NO,
        )

        self.set_default_size(150, 100)
