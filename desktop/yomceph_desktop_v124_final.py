"""Cierre visual de YomCeph Desktop v0.12.4.

Completa la personalización de la candidata v0.12.4 para controles ttk y hace
compatible el modo de alto contraste con la paleta elegida por el usuario.
"""

import tkinter as tk
from tkinter import ttk

import yomceph_desktop_hidpi as ui
from yomceph_desktop_v124_personalization import APP_VERSION, YomCephV124Personalization


class YomCephV124Final(YomCephV124Personalization):
    def _configure_personalization_styles(self, prefs):
        super()._configure_personalization_styles(prefs)
        c = ui.C
        family = prefs["font_family"]
        size = prefs["font_size"]
        style = ttk.Style(self)

        style.configure(
            "Treeview",
            background=c["panel"],
            fieldbackground=c["panel"],
            foreground=c["text"],
            font=(family, size),
            bordercolor=c["border"],
            lightcolor=c["border"],
            darkcolor=c["border"],
        )
        style.map(
            "Treeview",
            background=[("selected", c["purple"])],
            foreground=[("selected", "white")],
        )
        style.configure(
            "Treeview.Heading",
            background=c["lilac_soft"],
            foreground=c["purple_dark"],
            font=(family, size, "bold"),
            relief="flat",
        )
        style.map("Treeview.Heading", background=[("active", c["lilac"])])

        for style_name in ("TEntry", "TCombobox", "TSpinbox"):
            style.configure(
                style_name,
                fieldbackground=c["panel"],
                background=c["panel"],
                foreground=c["text"],
                insertcolor=c["text"],
                font=(family, size),
            )
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", c["panel"])],
            foreground=[("readonly", c["text"])],
            selectbackground=[("readonly", c["purple"])],
            selectforeground=[("readonly", "white")],
        )
        style.configure(
            "TLabelframe",
            background=c["panel"],
            bordercolor=c["border"],
            lightcolor=c["border"],
            darkcolor=c["border"],
        )
        style.configure(
            "TLabelframe.Label",
            background=c["panel"],
            foreground=c["purple_dark"],
            font=(family, size, "bold"),
        )

    def _apply_high_contrast(self):
        enabled = bool(self.high_contrast_var.get())
        try:
            self.canvas.configure(background="#000000" if enabled else ui.C["canvas"])
            base = int(self._personalization.get("font_size", 10))
            family = self._personalization.get("font_family", "Segoe UI")
            self.case_state_label.configure(
                font=(family, base + 1 if enabled else max(8, base), "bold")
            )
        except Exception:
            pass
        self.status.config(
            text=(
                "Alto contraste activado."
                if enabled
                else f"Alto contraste desactivado · paleta {self._personalization.get('palette', 'YomCeph violeta')}."
            )
        )

    def load_case_from_database(self, storage_id):
        result = super().load_case_from_database(storage_id)
        try:
            self.title(f"YomCeph Desktop · v{APP_VERSION}")
        except tk.TclError:
            pass
        return result


if __name__ == "__main__":
    ui.enable_dpi_awareness()
    app = YomCephV124Final()
    app.mainloop()
