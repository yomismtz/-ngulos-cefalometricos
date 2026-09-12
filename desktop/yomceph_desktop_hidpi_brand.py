import os
import sys
import tkinter as tk

import yomceph_desktop_hidpi as ui

APP_VERSION = "0.4.0"


def resource_path(filename):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, filename)


class BrandedYomCeph(ui.ResponsiveYomCeph):
    def __init__(self):
        super().__init__()
        self.title("YomCeph Desktop · Investigación")
        self._apply_brand_icon()

    def _apply_brand_icon(self):
        ico = resource_path("yomceph.ico")
        png = resource_path("yomceph_logo.png")
        try:
            if os.path.exists(ico):
                self.iconbitmap(ico)
        except Exception:
            pass
        try:
            if os.path.exists(png):
                image = tk.PhotoImage(file=png)
                self._window_icon = image
                self.iconphoto(True, image)
        except Exception:
            pass


if __name__ == "__main__":
    ui.enable_dpi_awareness()
    app = BrandedYomCeph()
    app.mainloop()
