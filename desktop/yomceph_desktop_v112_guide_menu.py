import tkinter as tk
from tkinter import ttk

import yomceph_desktop_hidpi as ui
import yomceph_desktop_v111_mode_ui_fix as v111

APP_VERSION = "0.11.2"


class GuideMenuYomCeph(v111.ModeFilteredYomCeph):
    """v0.11.2: elimina la pestaña lateral Plano vertebral y la mueve al menú TRAZADO GUIADO."""

    def __init__(self):
        super().__init__()
        self.title("YomCeph Desktop · Investigación · Base de datos · v0.11.2")
        self.after(300, self._force_vertebral_tab_hidden)

    # La guía vertebral nunca vuelve a aparecer como pestaña lateral.
    def _set_vertebral_visibility(self, visible):
        self._force_vertebral_tab_hidden()

    def _force_vertebral_tab_hidden(self):
        tab = getattr(self, "_vertebral_tab", None)
        nb = getattr(self, "_vertebral_notebook", None)
        if tab is None or nb is None:
            return
        try:
            if str(nb.select()) == str(tab):
                tabs = list(nb.tabs())
                other = next((t for t in tabs if str(t) != str(tab)), None)
                if other:
                    nb.select(other)
        except Exception:
            pass
        try:
            nb.tab(tab, state="hidden")
            return
        except Exception:
            pass
        try:
            tabs = [str(x) for x in nb.tabs()]
            if str(tab) in tabs:
                nb.forget(tab)
        except Exception:
            pass

    def apply_analysis_mode(self, mode):
        super().apply_analysis_mode(mode)
        self._force_vertebral_tab_hidden()
        self._refresh_guided_menu_for_mode()

    def _refresh_guided_menu_for_mode(self):
        try:
            menu_name = self.cget("menu")
            menubar = self.nametowidget(menu_name)
        except Exception:
            return

        try:
            end = menubar.index("end")
            if end is not None:
                for i in range(end, -1, -1):
                    try:
                        if menubar.entrycget(i, "label") == "TRAZADO GUIADO":
                            menubar.delete(i)
                    except Exception:
                        pass
        except Exception:
            pass

        guide = tk.Menu(menubar, tearoff=False)
        if self.analysis_mode in ("Postura craneofacial", "Ambos"):
            guide.add_command(label="OPT y CVT", command=self.start_opt_guide, accelerator="F6")
            guide.add_command(label="Tangentes posteriores C2–C7", command=self.start_posterior_guide, accelerator="F7")
            guide.add_command(label="McGregor + plano odontoideo OP", command=self.start_mcgregor_guide, accelerator="F9")
            guide.add_command(label="Powell · tejidos blandos", command=self.start_powell_guide, accelerator="F12")
            guide.add_separator()
            guide.add_command(label="Plano vertebral · guía visual", command=self.open_vertebral_guide_window)
            guide.add_command(label="Ir a profundidad cervical (PC)", command=lambda: self._select_key("PC"))

        if self.analysis_mode in ("Steiner", "Ambos"):
            if guide.index("end") is not None:
                guide.add_separator()
            guide.add_command(label="Incisivos e interincisal", command=self.start_dental_guide, accelerator="F10")

        guide.add_separator()
        guide.add_command(label="Salir del modo guiado", command=self.stop_guide, accelerator="F8")
        menubar.add_cascade(label="TRAZADO GUIADO", menu=guide)

    def open_vertebral_guide_window(self):
        if self.analysis_mode == "Steiner":
            return

        win = tk.Toplevel(self)
        win.title("YomCeph · Guía del plano vertebral")
        win.transient(self)
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        w, h = min(760, int(sw * 0.72)), min(760, int(sh * 0.84))
        win.geometry(f"{w}x{h}+{max(0,(sw-w)//2)}+{max(0,(sh-h)//2)}")
        win.minsize(620, 560)
        win.configure(bg=ui.C["paper"])

        header = tk.Frame(win, bg=ui.C["purple"], height=72)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(
            header, text="Plano vertebral · guía visual", bg=ui.C["purple"], fg="white",
            font=("Segoe UI Semibold", 18)
        ).pack(anchor="w", padx=18, pady=(10, 0))
        tk.Label(
            header, text="Esta ayuda se abrió desde TRAZADO GUIADO y ya no ocupa la barra lateral.",
            bg=ui.C["purple"], fg=ui.C["lilac_soft"], font=("Segoe UI", 9)
        ).pack(anchor="w", padx=18)

        body = ttk.Frame(win, padding=14, style="Panel.TFrame")
        body.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(body, text="Cómo usar el análisis vertebral", style="Section.TLabel").pack(anchor="w")
        ttk.Label(
            body,
            text=(
                "1. Use F6 para colocar cv2ip, cv2tg y cv4ip y formar OPT/CVT.\n"
                "2. Use F7 para colocar dos puntos por vértebra (posterior superior e inferior) de C2 a C7.\n"
                "3. La app forma automáticamente cada tangente posterior.\n"
                "4. Si necesita profundidad cervical, calibre primero la radiografía y después marque PC.\n"
                "5. Durante la colocación las líneas permanecen ocultas; puede activarlas sólo para revisión desde VER."
            ),
            style="Panel.TLabel", justify=tk.LEFT, wraplength=max(520, w - 70)
        ).pack(anchor="w", pady=(6, 10))

        ttk.Label(
            body,
            text="Esquema de tangentes posteriores C2–C7",
            style="Section.TLabel"
        ).pack(anchor="w", pady=(2, 5))

        canvas = tk.Canvas(body, bg="white", highlightthickness=1, highlightbackground=ui.C["border"], height=350)
        canvas.pack(fill=tk.BOTH, expand=True)

        def draw(_event=None):
            canvas.delete("all")
            cw = max(560, canvas.winfo_width())
            ch = max(320, canvas.winfo_height())
            x_center = cw * 0.48
            top = 30
            gap = max(43, min(50, (ch - 70) / 6))
            colors = [ui.C["gold"], "#C986D8", ui.C["turquoise"], "#B896E6", "#74C7B8", "#E2B85E"]
            for i, label in enumerate(("C2", "C3", "C4", "C5", "C6", "C7")):
                y = top + i * gap
                x1, x2 = x_center - 70 + i * 4, x_center + 25 + i * 2
                y1, y2 = y, y + 28
                canvas.create_rectangle(x1, y1, x2, y2, outline="#6D6576", width=2)
                px = x1 + 4
                canvas.create_oval(px-4, y1-4, px+4, y1+4, fill=colors[i], outline="")
                canvas.create_oval(px-4, y2-4, px+4, y2+4, fill=colors[i], outline="")
                canvas.create_line(px, y1-14, px, y2+14, fill=colors[i], width=3)
                canvas.create_text(x1 - 18, (y1+y2)/2, text=label, fill=ui.C["purple_dark"], font=("Segoe UI Semibold", 10))
                canvas.create_text(px - 10, y1 - 8, text="PS", anchor="e", fill=colors[i], font=("Segoe UI", 8))
                canvas.create_text(px - 10, y2 + 8, text="PI", anchor="e", fill=colors[i], font=("Segoe UI", 8))

            canvas.create_text(
                cw * 0.69, 65,
                text=("PS = posterior superior\nPI = posterior inferior\n\n"
                      "Dos puntos forman la tangente de cada cuerpo vertebral.\n"
                      "La línea aparece automáticamente; usted no la dibuja manualmente."),
                anchor="nw", width=max(180, cw * 0.27), fill=ui.C["text"], font=("Segoe UI", 9)
            )

        canvas.bind("<Configure>", draw)
        draw()

        buttons = ttk.Frame(body, style="Panel.TFrame")
        buttons.pack(fill=tk.X, pady=(10, 0))
        ttk.Button(buttons, text="Iniciar OPT / CVT", command=lambda: (win.destroy(), self.start_opt_guide()), style="Turquoise.TButton").pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(buttons, text="Iniciar C2–C7", command=lambda: (win.destroy(), self.start_posterior_guide()), style="Purple.TButton").pack(side=tk.LEFT, padx=6)
        ttk.Button(buttons, text="Cerrar", command=win.destroy, style="Soft.TButton").pack(side=tk.RIGHT)


if __name__ == "__main__":
    ui.enable_dpi_awareness()
    app = GuideMenuYomCeph()
    app.mainloop()
