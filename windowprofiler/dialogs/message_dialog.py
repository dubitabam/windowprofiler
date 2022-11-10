import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class MessageDialog(Gtk.MessageDialog):

    def __init__(
        self,
        text: str,
        parent = None,
    ):
        super().__init__(
            parent = parent,
            # flags = Gtk.DialogFlags.DESTROY_WITH_PARENT,      # deprecated
            modal = True,
            text = text,
            buttons = Gtk.ButtonsType.OK,
        )

        self.set_default_size(150, 100)
        self.run()
        self.destroy()
