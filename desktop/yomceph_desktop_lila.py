import tkinter as tk
from tkinter import ttk

import yomceph_desktop as core

core.APP_NAME = "YomCeph Desktop · Investigación"
core.APP_VERSION = "0.2.0"


class YomCephDesktopStyled(core.YomCephDesktop):
    """Capa visual para YomCeph Desktop sin modificar el motor de medición."""

    COLORS = {
        "bg": "#F7F3FB",
        "surface": "#FFFFFF",
        "surface_alt": "#F2EAFB",
        "purple": "#6E4A9E",
        "purple_dark": "#493067",
        "lilac": "#DCCCF2",
        "lilac_soft": "#EEE5F8",
        "mint": "#DDF4EA",
        "mint_dark": "#2F806B",
        "turquoise": "#43B9A8",
        "turquoise_dark": "#217B70",
        "gold": "#D6AD55",
        "gold_dark": "#8B681D",
        "text": "#30283A",
        "muted": "#726A7D",
        "canvas": "#15121B",
        "line": "#E6DDF0",
    }

    def _build_ui(self):
        self._configure_visual_theme()
        super()._build_ui()
        self._polish_existing_widgets()

    def _configure_visual_theme(self):
        c = self.COLORS
        self.configure(background=c["bg"])
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("TFrame", background=c["bg"])
        style.configure("TLabel", background=c["bg"], foreground=c["text"], font=("Segoe UI", 10))
        style.configure("TEntry", fieldbackground=c["surface"], foreground=c["text"], padding=7, borderwidth=1)
        style.map("TEntry", bordercolor=[("focus", c["turquoise"])])

        style.configure(
            "TButton",
            background=c["lilac_soft"],
            foreground=c["purple_dark"],
            borderwidth=0,
            focusthickness=0,
            focuscolor=c["lilac_soft"],
            padding=(12, 8),
            font=("Segoe UI", 9, "bold"),
        )
        style.map("TButton", background=[("active", c["lilac"]), ("pressed", c["purple"])], foreground=[("pressed", "#FFFFFF")])

        style.configure("Purple.TButton", background=c["purple"], foreground="#FFFFFF", padding=(14, 8), font=("Segoe UI", 9, "bold"))
        style.map("Purple.TButton", background=[("active", c["purple_dark"]), ("pressed", c["purple_dark"])])

        style.configure("Turquoise.TButton", background=c["turquoise"], foreground="#FFFFFF", padding=(14, 8), font=("Segoe UI", 9, "bold"))
        style.map("Turquoise.TButton", background=[("active", c["turquoise_dark"]), ("pressed", c["turquoise_dark"])])

        style.configure("Mint.TButton", background=c["mint"], foreground=c["mint_dark"], padding=(12, 8), font=("Segoe UI", 9, "bold"))
        style.map("Mint.TButton", background=[("active", "#CBECDD"), ("pressed", c["mint_dark"])], foreground=[("pressed", "#FFFFFF")])

        style.configure("Gold.TButton", background=c["gold"], foreground="#FFFFFF", padding=(16, 9), font=("Segoe UI", 10, "bold"))
        style.map("Gold.TButton", background=[("active", c["gold_dark"]), ("pressed", c["gold_dark"])])

        style.configure("TRadiobutton", background=c["bg"], foreground=c["text"], font=("Segoe UI", 9))
        style.map("TRadiobutton", indicatorcolor=[("selected", c["turquoise"])])
        style.configure("TSeparator", background=c["line"])

        style.configure("TNotebook", background=c["bg"], borderwidth=0, tabmargins=(4, 6, 4, 0))
        style.configure("TNotebook.Tab", background=c["lilac_soft"], foreground=c["purple_dark"], padding=(14, 9), font=("Segoe UI", 9, "bold"), borderwidth=0)
        style.map("TNotebook.Tab", background=[("selected", c["purple"]), ("active", c["lilac"])], foreground=[("selected", "#FFFFFF")])

        style.configure("TPanedwindow", background=c["bg"])

    def _polish_existing_widgets(self):
        c = self.COLORS
        self.title("YomCeph Desktop · Investigación · v0.2")

        # Panel de landmarks con apariencia de tarjeta.
        self.point_list.configure(
            background=c["surface"],
            foreground=c["text"],
            selectbackground=c["purple"],
            selectforeground="#FFFFFF",
            activestyle="none",
            relief="flat",
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=c["lilac"],
            highlightcolor=c["turquoise"],
            font=("Segoe UI", 10),
        )

        # Zona radiográfica oscura para aumentar contraste visual.
        self.canvas.configure(background=c["canvas"], highlightthickness=2, highlightbackground=c["purple_dark"])

        # Resultados legibles como una ficha clínica/académica.
        self.results_text.configure(
            background="#FFFDF8",
            foreground=c["text"],
            selectbackground=c["lilac"],
            selectforeground=c["purple_dark"],
            insertbackground=c["purple"],
            relief="flat",
            borderwidth=0,
            padx=14,
            pady=14,
            font=("Segoe UI", 10),
        )

        self.guide_canvas.configure(
            background="#FFFDF9",
            highlightthickness=1,
            highlightbackground=c["gold"],
        )

        # Colores de estado.
        self.cal_label.configure(foreground=c["turquoise_dark"])
        self.status.configure(foreground=c["purple_dark"])
        self.point_title.configure(foreground=c["purple_dark"])
        self.point_desc.configure(foreground=c["text"])
        self.point_status.configure(foreground=c["mint_dark"])

        # Botones semánticos: acción principal, archivo, calibración y exportación.
        self._style_buttons_recursively(self)

    def _style_buttons_recursively(self, widget):
        for child in widget.winfo_children():
            if isinstance(child, ttk.Button):
                text = str(child.cget("text")).strip().lower()
                if "calcular" in text:
                    child.configure(style="Gold.TButton")
                elif "abrir radiografía" in text:
                    child.configure(style="Purple.TButton")
                elif "calibrar" in text:
                    child.configure(style="Turquoise.TButton")
                elif "guardar" in text or "exportar" in text or "imagen trazada" in text:
                    child.configure(style="Mint.TButton")
                elif "siguiente" in text:
                    child.configure(style="Turquoise.TButton")
            self._style_buttons_recursively(child)

    def redraw(self):
        # Conserva todas las mediciones del motor y mejora la lectura de los trazos.
        super().redraw()
        if not self.original:
            return
        # Borde sutil de la imagen para separarla del fondo negro.
        try:
            x1 = self.offset_x
            y1 = self.offset_y
            x2 = self.offset_x + self.original.width * self.scale
            y2 = self.offset_y + self.original.height * self.scale
            self.canvas.create_rectangle(x1, y1, x2, y2, outline=self.COLORS["lilac"], width=1)
        except Exception:
            pass


if __name__ == "__main__":
    app = YomCephDesktopStyled()
    app.mainloop()
