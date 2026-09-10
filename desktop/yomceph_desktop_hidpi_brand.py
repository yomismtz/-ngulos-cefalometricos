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
        self._add_brand_badge()

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

    def _add_brand_badge(self):
        # Badge discreto superpuesto al encabezado; no altera el espacio de trabajo.
        png = resource_path("yomceph_logo.png")
        if not os.path.exists(png):
            return
        try:
            img = tk.PhotoImage(file=png)
            # Downsample natively so the logo remains crisp at normal DPI.
            factor = max(1, img.width() // 52)
            if factor > 1:
                img = img.subsample(factor, factor)
            self._brand_badge_image = img
            badge = tk.Label(self, image=img, bd=0, bg=ui.C["purple"], highlightthickness=0)
            badge.place(x=8, y=8, width=48, height=48)
        except Exception:
            pass


if __name__ == "__main__":
    ui.enable_dpi_awareness()
    app = BrandedYomCeph()
    app.mainloop()
