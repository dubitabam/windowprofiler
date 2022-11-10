import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class InputDialog(Gtk.Dialog):

    def __init__(
        self,
        title: str,
        prompt: str = None,
        value: str = None,
        parent = None,
    ):
        super().__init__(
            title           = title,
            transient_for   = parent,
            flags           = 0
        )

        self.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OK, Gtk.ResponseType.OK,
        )

        self.set_default_size(150, 100)

        box = self.get_content_area()
        box.set_spacing(10)
        box.set_margin_start(10)
        box.set_margin_end(10)
        box.set_margin_top(10)
        box.set_margin_bottom(10)

        if not prompt is None:
            self.__label = Gtk.Label(label = prompt)
            self.__label.set_xalign(0)
            box.add(self.__label)

        self.__textbox = Gtk.Entry()
        if not value is None:
            self.__textbox.set_text(value)
        box.add(self.__textbox)

        self.show_all()


    def get_value(self) -> str:
        return self.__textbox.get_text()
