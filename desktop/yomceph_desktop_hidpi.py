import ctypes
import math
import sys
import tkinter as tk
from tkinter import ttk

import yomceph_desktop as core

APP_NAME = "YomCeph Desktop · Investigación"
APP_VERSION = "0.3.0"

C = {
    "purple": "#6E4A9E",
    "purple_dark": "#4E3474",
    "lilac": "#DCCCF2",
    "lilac_soft": "#F3EEFA",
    "mint": "#DDF4EA",
    "mint_deep": "#2F806F",
    "turquoise": "#43B9A8",
    "turquoise_dark": "#247E73",
    "gold": "#D6AD55",
    "gold_dark": "#8F6B1E",
    "paper": "#FBF9FD",
    "panel": "#FFFFFF",
    "text": "#2F2B35",
    "muted": "#6D6576",
    "canvas": "#0B0B10",
    "border": "#E7E0EE",
}


def enable_dpi_awareness():
    """Activa Per-Monitor DPI Awareness antes de crear la ventana de Tk."""
    if sys.platform != "win32":
        return
    try:
        ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
        return
    except Exception:
        pass
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
        return
    except Exception:
        pass
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass


class ResponsiveYomCeph(core.YomCephDesktop):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.configure(bg=C["paper"])
        self._apply_tk_scaling()
        self._fit_window_to_screen()
        self.bind("<F11>", self.toggle_fullscreen)
        self.bind("<Escape>", self.exit_fullscreen)
        self.after(250, self._set_initial_sashes)

    def _apply_tk_scaling(self):
        dpi = 96
        if sys.platform == "win32":
            try:
                dpi = int(ctypes.windll.user32.GetDpiForSystem())
            except Exception:
                pass
        try:
            self.tk.call("tk", "scaling", max(1.0, dpi / 72.0))
        except Exception:
            pass

    def _fit_window_to_screen(self):
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.compact = sw < 1280 or sh < 760
        min_w = min(900, max(720, int(sw * 0.68)))
        min_h = min(600, max(500, int(sh * 0.68)))
        self.minsize(min_w, min_h)
        try:
            if sys.platform == "win32":
                self.state("zoomed")
            else:
                w, h = int(sw * 0.94), int(sh * 0.90)
                self.geometry(f"{w}x{h}+{max(0,(sw-w)//2)}+{max(0,(sh-h)//2)}")
        except Exception:
            self.geometry(f"{int(sw*0.92)}x{int(sh*0.88)}+0+0")

    def _configure_styles(self):
        self.compact = self.winfo_screenwidth() < 1280 or self.winfo_screenheight() < 760
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        small = 9 if self.compact else 10
        style.configure(".", font=("Segoe UI", small), background=C["paper"], foreground=C["text"])
        style.configure("TFrame", background=C["paper"])
        style.configure("Panel.TFrame", background=C["panel"])
        style.configure("TLabel", background=C["paper"], foreground=C["text"])
        style.configure("Panel.TLabel", background=C["panel"], foreground=C["text"])
        style.configure("Section.TLabel", background=C["panel"], foreground=C["purple_dark"], font=("Segoe UI Semibold", small + 1))
        style.configure("Muted.TLabel", background=C["panel"], foreground=C["muted"], font=("Segoe UI", max(8, small - 1)))
        style.configure("Purple.TButton", background=C["purple"], foreground="white", padding=(9, 7), borderwidth=0)
        style.map("Purple.TButton", background=[("active", C["purple_dark"])])
        style.configure("Mint.TButton", background=C["mint"], foreground=C["mint_deep"], padding=(9, 7), borderwidth=0)
        style.map("Mint.TButton", background=[("active", "#C8EBDD")])
        style.configure("Turquoise.TButton", background=C["turquoise"], foreground="white", padding=(9, 7), borderwidth=0)
        style.map("Turquoise.TButton", background=[("active", C["turquoise_dark"])])
        style.configure("Gold.TButton", background=C["gold"], foreground="#2F2616", padding=(9, 7), borderwidth=0, font=("Segoe UI Semibold", small))
        style.map("Gold.TButton", background=[("active", "#C99C3E")])
        style.configure("Soft.TButton", background=C["lilac_soft"], foreground=C["purple_dark"], padding=(9, 7), borderwidth=0)
        style.map("Soft.TButton", background=[("active", C["lilac"])])
        style.configure("TNotebook", background=C["paper"], borderwidth=0)
        style.configure("TNotebook.Tab", background=C["lilac_soft"], foreground=C["purple_dark"], padding=(10, 7), font=("Segoe UI Semibold", small))
        style.map("TNotebook.Tab", background=[("selected", C["mint"])], foreground=[("selected", C["turquoise_dark"])])
        style.configure("TRadiobutton", background=C["panel"], foreground=C["text"])
        style.configure("Horizontal.TProgressbar", troughcolor=C["lilac_soft"], background=C["turquoise"])

    def _build_ui(self):
        self._configure_styles()
        self.compact = self.winfo_screenwidth() < 1280 or self.winfo_screenheight() < 760
        title_size = 18 if self.compact else 22
        body_font = 9 if self.compact else 10

        header = tk.Frame(self, bg=C["purple"], height=72)
        header.pack(side=tk.TOP, fill=tk.X)
        header.pack_propagate(False)
        brand = tk.Frame(header, bg=C["purple"])
        brand.pack(side=tk.LEFT, fill=tk.Y, padx=(18, 8), pady=9)
        tk.Label(brand, text="YomCeph Desktop", bg=C["purple"], fg="white", font=("Segoe UI Semibold", title_size)).pack(anchor="w")
        tk.Label(brand, text="Investigación · Morfología craneofacial y postura cervical", bg=C["purple"], fg=C["lilac_soft"], font=("Segoe UI", max(8, body_font-1))).pack(anchor="w")
        case = tk.Frame(header, bg=C["purple"])
        case.pack(side=tk.RIGHT, padx=18, pady=9)
        tk.Label(case, text="CASO", bg=C["purple"], fg=C["lilac_soft"], font=("Segoe UI Semibold", 8)).pack(anchor="e")
        ttk.Entry(case, textvariable=self.case_id, width=12, font=("Segoe UI Semibold", body_font)).pack(anchor="e", pady=(2, 0))

        toolbar = ttk.Frame(self, padding=(10, 7))
        toolbar.pack(fill=tk.X)
        actions = [
            ("Abrir radiografía", self.open_image, "Purple.TButton"),
            ("Guardar proyecto", self.save_project, "Mint.TButton"),
            ("Abrir proyecto", self.load_project, "Soft.TButton"),
            ("Calibrar mm", self.start_calibration, "Turquoise.TButton"),
            ("Calcular análisis", self.calculate, "Gold.TButton"),
            ("Exportar CSV", self.export_csv, "Mint.TButton"),
            ("Imagen trazada", self.export_annotated, "Soft.TButton"),
            ("Pantalla completa", self.toggle_fullscreen, "Turquoise.TButton"),
        ]
        for col in range(4):
            toolbar.columnconfigure(col, weight=1, uniform="actions")
        for i, (text, cmd, style) in enumerate(actions):
            ttk.Button(toolbar, text=text, command=cmd, style=style).grid(row=i // 4, column=i % 4, sticky="ew", padx=3, pady=3)

        main = ttk.Panedwindow(self, orient=tk.HORIZONTAL)
        main.pack(fill=tk.BOTH, expand=True, padx=9, pady=(0, 6))
        self.body_panes = main
        left = ttk.Frame(main, style="Panel.TFrame", padding=9)
        center = ttk.Frame(main, style="Panel.TFrame", padding=2)
        right = ttk.Frame(main, style="Panel.TFrame", padding=8)
        main.add(left, weight=1)
        main.add(center, weight=5)
        main.add(right, weight=2)

        ttk.Label(left, text="Puntos anatómicos", style="Section.TLabel").pack(anchor="w")
        ttk.Label(left, text="Seleccione un punto y colóquelo sobre la radiografía.", style="Muted.TLabel", wraplength=230).pack(anchor="w", pady=(2, 7))
        list_box = tk.Frame(left, bg=C["panel"])
        list_box.pack(fill=tk.BOTH, expand=True)
        self.point_list = tk.Listbox(list_box, exportselection=False, activestyle="none", relief="flat", bd=0, bg=C["lilac_soft"], fg=C["text"], selectbackground=C["purple"], selectforeground="white", highlightthickness=1, highlightbackground=C["border"], font=("Segoe UI", body_font))
        pscroll = ttk.Scrollbar(list_box, orient="vertical", command=self.point_list.yview)
        self.point_list.configure(yscrollcommand=pscroll.set)
        self.point_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        pscroll.pack(side=tk.RIGHT, fill=tk.Y)
        for key, title, _ in core.POINTS:
            self.point_list.insert(tk.END, f"{key} · {title}")
        self.point_list.selection_set(0)
        self.point_list.bind("<<ListboxSelect>>", self.on_list_select)

        nav = ttk.Frame(left, style="Panel.TFrame")
        nav.pack(fill=tk.X, pady=(7, 0))
        ttk.Button(nav, text="← Anterior", command=self.previous_point, style="Soft.TButton").pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 3))
        ttk.Button(nav, text="Siguiente →", command=self.next_point, style="Turquoise.TButton").pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(3, 0))
        ttk.Button(left, text="Borrar punto seleccionado", command=self.delete_selected, style="Soft.TButton").pack(fill=tk.X, pady=(6, 2))
        ttk.Button(left, text="Borrar todos", command=self.delete_all, style="Soft.TButton").pack(fill=tk.X, pady=2)
        ttk.Button(left, text="Centrar / ajustar", command=self.fit_image, style="Mint.TButton").pack(fill=tk.X, pady=(2, 7))

        self.progress_var = tk.DoubleVar(value=0)
        ttk.Progressbar(left, variable=self.progress_var, maximum=len(core.POINT_ORDER)).pack(fill=tk.X, pady=(3, 2))
        self.progress_label = ttk.Label(left, text=f"0 / {len(core.POINT_ORDER)} puntos", style="Muted.TLabel")
        self.progress_label.pack(anchor="w")
        ttk.Separator(left).pack(fill=tk.X, pady=8)
        ttk.Label(left, text="Orientación del perfil", style="Section.TLabel").pack(anchor="w")
        ttk.Radiobutton(left, text="Mira hacia la derecha", value="right", variable=self.face_direction).pack(anchor="w")
        ttk.Radiobutton(left, text="Mira hacia la izquierda", value="left", variable=self.face_direction).pack(anchor="w")
        self.cal_label = ttk.Label(left, text="Sin calibración", style="Muted.TLabel")
        self.cal_label.pack(anchor="w", pady=(7, 0))

        self.canvas = tk.Canvas(center, background=C["canvas"], highlightthickness=0, cursor="crosshair")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", lambda e: self.redraw())
        self.canvas.bind("<Button-1>", self.canvas_left_down)
        self.canvas.bind("<B1-Motion>", self.canvas_left_drag)
        self.canvas.bind("<ButtonRelease-1>", self.canvas_left_up)
        self.canvas.bind("<Button-3>", self.pan_start)
        self.canvas.bind("<B3-Motion>", self.pan_move)
        self.canvas.bind("<MouseWheel>", self.zoom)

        notebook = ttk.Notebook(right)
        notebook.pack(fill=tk.BOTH, expand=True)
        tab_point = ttk.Frame(notebook, style="Panel.TFrame", padding=11)
        tab_results = ttk.Frame(notebook, style="Panel.TFrame", padding=9)
        tab_vertebral = ttk.Frame(notebook, style="Panel.TFrame", padding=9)
        notebook.add(tab_point, text="Guía")
        notebook.add(tab_results, text="Resultados")
        notebook.add(tab_vertebral, text="Plano vertebral")

        wrap = 300 if self.compact else 350
        self.point_title = ttk.Label(tab_point, text="", style="Section.TLabel", wraplength=wrap)
        self.point_title.pack(anchor="w")
        self.point_desc = ttk.Label(tab_point, text="", style="Panel.TLabel", wraplength=wrap, justify=tk.LEFT)
        self.point_desc.pack(anchor="w", pady=(7, 10))
        self.point_status = ttk.Label(tab_point, text="", style="Panel.TLabel", wraplength=wrap)
        self.point_status.pack(anchor="w")
        ttk.Separator(tab_point).pack(fill=tk.X, pady=11)
        ttk.Label(tab_point, text="La guía ayuda a localizar el landmark; la identificación final corresponde al observador.", style="Muted.TLabel", wraplength=wrap, justify=tk.LEFT).pack(anchor="w")

        self.results_text = tk.Text(tab_results, wrap=tk.WORD, font=("Segoe UI", body_font), state=tk.DISABLED, relief="flat", bd=0, bg=C["panel"], fg=C["text"], padx=7, pady=7)
        self.results_text.pack(fill=tk.BOTH, expand=True)

        ttk.Label(tab_vertebral, text="Análisis del plano vertebral", style="Section.TLabel").pack(anchor="w")
        ttk.Label(tab_vertebral, text="La tangente C2–C7 y el punto PC permiten calcular la profundidad cervical. Con calibración, el resultado se expresa en mm.", style="Muted.TLabel", wraplength=wrap, justify=tk.LEFT).pack(anchor="w", pady=(4, 7))
        self.guide_canvas = tk.Canvas(tab_vertebral, bg="white", highlightthickness=1, highlightbackground=C["border"], height=360)
        self.guide_canvas.pack(fill=tk.BOTH, expand=True)
        self.guide_canvas.bind("<Configure>", lambda e: self.draw_vertebral_guide())

        footer = tk.Frame(self, bg=C["lilac_soft"], height=30)
        footer.pack(side=tk.BOTTOM, fill=tk.X)
        footer.pack_propagate(False)
        self.status = tk.Label(footer, text="Abra una radiografía lateral para comenzar.", bg=C["lilac_soft"], fg=C["muted"], font=("Segoe UI", max(8, body_font-1)))
        self.status.pack(side=tk.LEFT, padx=11)
        tk.Label(footer, text=f"v{APP_VERSION} · Uso educativo y de investigación", bg=C["lilac_soft"], fg=C["purple_dark"], font=("Segoe UI", max(8, body_font-1))).pack(side=tk.RIGHT, padx=11)

        self.update_point_guide()

    def _set_initial_sashes(self):
        try:
            width = self.body_panes.winfo_width()
            if width < 820:
                return
            left_w = max(205, int(width * 0.18))
            right_w = max(270, int(width * 0.25))
            self.body_panes.sashpos(0, left_w)
            self.body_panes.sashpos(1, width - right_w)
        except Exception:
            pass

    def toggle_fullscreen(self, event=None):
        self.attributes("-fullscreen", not bool(self.attributes("-fullscreen")))

    def exit_fullscreen(self, event=None):
        if self.attributes("-fullscreen"):
            self.attributes("-fullscreen", False)

    def update_point_guide(self):
        core.YomCephDesktop.update_point_guide(self)
        if hasattr(self, "progress_var"):
            self.progress_var.set(len(self.points))
            self.progress_label.config(text=f"{len(self.points)} / {len(core.POINT_ORDER)} puntos")

    def redraw(self):
        self.canvas.delete("all")
        if not self.original:
            self.canvas.create_text(self.canvas.winfo_width() / 2, self.canvas.winfo_height() / 2, text="Abra una radiografía lateral de cráneo", fill=C["lilac"], font=("Segoe UI Semibold", 15))
            return
        w = max(1, int(self.original.width * self.scale))
        h = max(1, int(self.original.height * self.scale))
        resized = self.original.resize((w, h), core.Image.Resampling.LANCZOS)
        self.tk_image = core.ImageTk.PhotoImage(resized)
        self.canvas.create_image(self.offset_x, self.offset_y, image=self.tk_image, anchor="nw")
        self._draw_measurement_lines()
        for key, p in self.points.items():
            x, y = self.image_to_canvas(p)
            selected = key == self.selected_point.get()
            r = 6 if selected else 4
            color = C["gold"] if selected else C["turquoise"]
            self.canvas.create_oval(x-r, y-r, x+r, y+r, outline="#161219", fill=color, width=1)
            self.canvas.create_text(x+8, y-8, text=key, fill=color, anchor="sw", font=("Segoe UI Semibold", 9))
        for i, p in enumerate(self.calibration_points):
            x, y = self.image_to_canvas(p)
            self.canvas.create_oval(x-5, y-5, x+5, y+5, fill=C["purple"], outline="white")
            self.canvas.create_text(x+7, y-7, text=f"Cal{i+1}", fill=C["lilac"], anchor="sw", font=("Segoe UI Semibold", 8))

    def _line(self, a_key, b_key, color=C["turquoise"], width=2, dash=None):
        if a_key in self.points and b_key in self.points:
            a = self.image_to_canvas(self.points[a_key])
            b = self.image_to_canvas(self.points[b_key])
            self.canvas.create_line(*a, *b, fill=color, width=width, dash=dash)

    def _draw_measurement_lines(self):
        self._line("S", "N", C["turquoise"])
        self._line("Po", "Or", C["gold"])
        self._line("Go", "Gn", "#C986D8")
        self._line("cv2tg", "cv2ip", "#78D7CB", 3)
        self._line("cv2tg", "cv4ip", "#B896E6", 3)
        self._line("C2ps", "C7pi", C["gold"], 3)
        if self.require("PC", "C2ps", "C7pi"):
            p, a, b = self.points["PC"], self.points["C2ps"], self.points["C7pi"]
            dx, dy = b[0]-a[0], b[1]-a[1]
            den = dx*dx + dy*dy
            if den:
                t = ((p[0]-a[0])*dx + (p[1]-a[1])*dy) / den
                q = (a[0] + t*dx, a[1] + t*dy)
                self.canvas.create_line(*self.image_to_canvas(p), *self.image_to_canvas(q), fill="#F2D184", width=2, dash=(5,3))

    def draw_vertebral_guide(self):
        c = self.guide_canvas
        c.delete("all")
        w, h = max(260, c.winfo_width()), max(300, c.winfo_height())
        c.create_text(14, 14, anchor="nw", text="¿Cómo se ve la tangente?", fill=C["purple_dark"], font=("Segoe UI Semibold", 11))
        c.create_text(14, 40, anchor="nw", width=w-28, text="La línea dorada une la referencia posterior de C2 con C7. PC es el punto de máxima profundidad de la curva respecto a esa línea.", fill=C["muted"], font=("Segoe UI", 9))
        y0 = 112
        x0 = w * 0.28
        c.create_line(x0, y0, x0, h-48, fill=C["gold"], width=4)
        pts = []
        for i in range(42):
            t = i / 41
            y = y0 + t * (h-y0-48)
            x = x0 + 34 * math.sin(math.pi*t)
            pts.extend([x, y])
        c.create_line(*pts, fill=C["purple"], width=4, smooth=True)
        for i, label in enumerate(["C2", "C3", "C4", "C5", "C6", "C7"]):
            y = y0 + 14 + i * max(30, (h-y0-78)/5)
            c.create_rectangle(x0+43, y-10, x0+84, y+10, outline=C["turquoise_dark"], width=2, fill=C["mint"])
            c.create_text(x0+63, y, text=label, fill=C["text"], font=("Segoe UI Semibold", 8))
        py = y0 + (h-y0-48)*0.50
        px = x0 + 34
        c.create_oval(px-5, py-5, px+5, py+5, fill=C["turquoise"], outline=C["purple_dark"])
        c.create_line(x0, py, px, py, fill=C["turquoise"], width=3, dash=(5,3))
        c.create_text(px+9, py, anchor="w", text="PC", fill=C["turquoise_dark"], font=("Segoe UI Semibold", 9))
        c.create_text(w/2, h-20, text="Esquema educativo", fill=C["muted"], font=("Segoe UI", 8))


def main():
    enable_dpi_awareness()
    app = ResponsiveYomCeph()
    app.mainloop()


if __name__ == "__main__":
    main()
