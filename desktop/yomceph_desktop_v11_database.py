import csv
import json
import math
import os
import re
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageOps

import yomceph_desktop as core
import yomceph_desktop_hidpi as ui
import yomceph_desktop_hidpi_guided_tangents as guided
import yomceph_desktop_v06_extended as v06
import yomceph_desktop_v07_powell as v07
import yomceph_desktop_v08_clinical as v08
import yomceph_desktop_v09_clean_workflow as v09
import yomceph_desktop_v10_visual_help as v10

APP_VERSION = "0.11.0"
TARGET_CASES = 103

# -----------------------------------------------------------------------------
# Puntos adicionales del protocolo cefalométrico proporcionado por la
# investigadora. Los puntos ya existentes se conservan y no se duplican.
# -----------------------------------------------------------------------------
NEW_POINTS = [
    ("ANS", "ENA / ANS · espina nasal anterior",
     "Marque la punta más anterior de la espina nasal anterior. Junto con PNS/ENP forma el plano palatino SPP."),
    ("D", "Punto D · centro de la sínfisis",
     "Marque el centro geométrico de la sínfisis mandibular basal. Se utiliza con S y N para el ángulo SND."),
    ("Pg", "Pogonion óseo (Pg)",
     "Marque el punto más anterior del contorno óseo de la sínfisis. Se usa para SL y Pg–NB."),
    ("CI", "Contorno posterior del cóndilo (CI)",
     "Marque el punto más posterior del contorno del cóndilo mandibular. Su proyección perpendicular sobre SN define E para el segmento SE."),
    ("Ar", "Articulare (Ar)",
     "Marque la intersección radiográfica entre el borde posterior de la rama mandibular y la base craneal posterior. Se usa para el ángulo goníaco Ar–Go–Me."),
    ("Me", "Menton óseo (Me)",
     "Marque el punto más inferior del contorno óseo de la sínfisis mandibular. Se usa con Ar y Go para el ángulo goníaco."),
    ("OcA", "Plano oclusal · punto anterior",
     "Marque el punto medio del contacto/solapamiento incisal que represente la zona anterior del plano oclusal funcional."),
    ("OcP", "Plano oclusal · punto posterior",
     "Marque un punto posterior representativo del plano oclusal, preferentemente en la zona de intercuspidación molar claramente identificable. OcA–OcP forma el plano oclusal."),
    ("Ssoft", "Punto S de tejido blando para línea S",
     "Marque el punto medio de la curvatura en S entre el borde inferior de la nariz y el labio superior usado por Steiner. Junto con Pg' forma la línea S."),
    ("Ls", "Labio superior (Ls)",
     "Marque el punto más anterior del contorno del labio superior. La distancia perpendicular a la línea S se expresa en mm."),
    ("Li", "Labio inferior (Li)",
     "Marque el punto más anterior del contorno del labio inferior. La distancia perpendicular a la línea S se expresa en mm."),
]

MASTER_POINTS = []
_seen = set()
for p in v09.POINTS + NEW_POINTS:
    if p[0] not in _seen:
        MASTER_POINTS.append(p)
        _seen.add(p[0])
MASTER_ORDER = [p[0] for p in MASTER_POINTS]
MASTER_INFO = {p[0]: (p[1], p[2]) for p in MASTER_POINTS}

STEINER_POINTS = [
    "S", "N", "A", "B", "Po", "Or", "ANS", "PNS", "D", "Pg", "CI",
    "Ar", "Go", "Me", "Gn", "U1a", "U1i", "L1a", "L1i", "OcA", "OcP",
    "Ssoft", "Pgsoft", "Ls", "Li",
]
POSTURE_POINTS = [
    "S", "N", "cv2ip", "cv2tg", "cv4ip",
    "C2ps", "C2pi", "C3ps", "C3pi", "C4ps", "C4pi",
    "C5ps", "C5pi", "C6ps", "C6pi", "C7ps", "C7pi", "PC",
    "PNS", "C0", "Ops", "Opi",
    "Gsoft", "Nsoft", "Dn", "Prn", "Pgsoft", "Mesoft", "Csoft",
]

# Normas exactas de la tabla entregada por la investigadora. Se mantienen como
# "protocolo de investigación" porque algunas difieren de tablas clásicas de
# Steiner publicadas en otras fuentes.
# clave: (media, DE, unidad, disminuye, norma, aumenta)
STEINER_PROTOCOL = {
    "SNA": (82.0, 2.0, "°", "Retrognatismo maxilar.", "Posición maxilar normal.", "Prognatismo maxilar."),
    "SN–PoOr": (7.0, 3.0, "°", "Tendencia a patrón horizontal o braquifacial.", "Relación craneal normal entre la base craneal anterior y el plano de Frankfort.", "Tendencia a patrón vertical o dolicofacial."),
    "Frankfort–SPP": (5.0, 2.0, "°", "Tendencia a mordida abierta o rotación posterior del maxilar.", "Relación normal entre el plano de Frankfort y el plano palatino.", "Tendencia a mordida profunda o rotación anterior del maxilar."),
    "SNB": (80.0, 2.0, "°", "Retrogenismo / retroposición mandibular.", "Mandíbula en posición normal.", "Prognatismo mandibular."),
    "SND": (77.0, 2.0, "°", "Retrogenismo de la sínfisis mandibular.", "Sínfisis en posición normal.", "Progenismo de la sínfisis mandibular."),
    "SL": (51.0, 2.0, "mm", "Mandíbula corta o retruida.", "Longitud/posición mandibular dentro de la referencia del protocolo.", "Mandíbula larga o adelantada."),
    "SE": (23.0, 2.0, "mm", "Posición adelantada del cóndilo.", "Cóndilo en posición de referencia.", "Posición retrasada del cóndilo."),
    "Ar–Go–Me": (125.0, 2.0, "°", "Crecimiento horizontal con tendencia a rotación antihoraria.", "Patrón mesofacial según el protocolo.", "Crecimiento vertical con tendencia a rotación horaria."),
    "SN–GoGn": (32.0, 5.0, "°", "Crecimiento horizontal, rotación antihoraria y tendencia a mordida profunda.", "Patrón mesofacial / normodivergente.", "Crecimiento vertical, rotación horaria y tendencia a mordida abierta."),
    "ANB": (2.0, 1.0, "°", "Relación sagital compatible con Clase III esquelética.", "Relación sagital compatible con Clase I esquelética.", "Relación sagital compatible con Clase II esquelética."),
    "AB–GoGn": (74.0, 2.0, "°", "Tendencia a mordida abierta según la tabla del protocolo.", "Relación vertical maxilomandibular normal.", "Tendencia a mordida profunda según la tabla del protocolo."),
    "IS–SN": (104.0, 2.0, "°", "Retroinclinación del incisivo superior.", "Incisivo superior con inclinación de referencia.", "Proinclinación del incisivo superior."),
    "IS–NA (°)": (22.0, 2.0, "°", "Palatinización / retroinclinación del incisivo superior.", "Incisivo superior en norma angular.", "Vestibularización / proinclinación del incisivo superior."),
    "IS–NA (mm)": (4.0, 1.0, "mm", "Linguogresión / retrusión del incisivo superior.", "Posición lineal del incisivo superior en norma.", "Vestibulogresión / protrusión del incisivo superior."),
    "II–NB (°)": (16.0, 1.0, "°", "Lingualización / retroinclinación del incisivo inferior.", "Incisivo inferior en norma angular del protocolo.", "Vestibularización / proinclinación del incisivo inferior."),
    "II–NB (mm)": (4.0, 1.0, "mm", "Linguogresión / retrusión del incisivo inferior.", "Posición lineal del incisivo inferior en norma.", "Vestibulogresión / protrusión del incisivo inferior."),
    "Plano oclusal–SN": (16.0, 1.0, "°", "Plano oclusal cerrado.", "Inclinación del plano oclusal dentro de la referencia.", "Plano oclusal abierto."),
    "Ángulo interincisal": (135.0, 4.0, "°", "Relación incisiva disminuida; en la tabla del protocolo se asocia con tendencia a mordida abierta.", "Relación incisiva normal según el protocolo.", "Relación incisiva aumentada; en la tabla del protocolo se asocia con tendencia a mordida profunda."),
    "Línea S · labio superior": (0.0, 2.0, "mm", "Retrusión labial superior.", "Labio superior ortognático respecto a la línea S.", "Protrusión labial superior."),
    "Línea S · labio inferior": (0.0, 2.0, "mm", "Retrusión labial inferior.", "Labio inferior ortognático respecto a la línea S.", "Protrusión labial inferior."),
    "Pg–NB": (4.0, 1.0, "mm", "Retrogenismo: mentón óseo relativamente retraído.", "Mentón dentro de la referencia del protocolo.", "Progenismo: mentón óseo relativamente prominente."),
}

STEINER_ORDER = list(STEINER_PROTOCOL.keys())
POSTURE_ORDER = [
    "SN–OPT", "SN–CVT", "OPT–CVT", "Tangente posterior C2–C7",
    "MGP–OP", "MGP–CVT", "Powell Nasofrontal", "Powell Nasofacial",
    "Powell Nasomental", "Powell Mentocervical", "Profundidad cervical (mm)",
]


def _project_to_line(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    den = dx * dx + dy * dy
    if den <= 1e-12:
        return a
    t = ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / den
    return (a[0] + t * dx, a[1] + t * dy)


def _line_side(a, b, p):
    return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])


def _sanitize_case_id(value):
    value = re.sub(r"[^A-Za-z0-9._-]+", "_", str(value).strip())
    return value or "caso"


class ResearchDatabaseYomCeph(v10.VisualHelpYomCeph):
    def __init__(self):
        # Propagar el catálogo maestro antes de que las clases padre creen la UI.
        for module in (core, guided, v06, v07, v08, v09):
            module.POINTS = MASTER_POINTS
            module.POINT_ORDER = MASTER_ORDER
            module.POINT_INFO = MASTER_INFO

        self.analysis_mode = "Ambos"
        self.active_point_order = MASTER_ORDER[:]
        self._vertebral_tab = None
        self._vertebral_notebook = None
        self._db_path = None
        self._data_dir = None
        self._case_images_dir = None

        super().__init__()
        self.title("YomCeph Desktop · Investigación · Base de datos · v0.11")

        self._capture_vertebral_tab()
        self._init_database()
        self._install_database_bar()
        self._install_database_menu()
        self._update_db_counter()

        # Elegir el tipo de análisis antes de empezar a colocar puntos.
        self.after(120, lambda: self.choose_analysis_mode(startup=True))

    # ------------------------------------------------------------------
    # Base de datos persistente (fuera de la carpeta de instalación)
    # ------------------------------------------------------------------
    def _init_database(self):
        base = os.getenv("LOCALAPPDATA")
        if base:
            data_dir = Path(base) / "YomCeph" / "ResearchData"
        else:
            data_dir = Path.home() / ".yomceph" / "ResearchData"
        data_dir.mkdir(parents=True, exist_ok=True)
        images = data_dir / "case_images"
        images.mkdir(parents=True, exist_ok=True)
        backups = data_dir / "backups"
        backups.mkdir(parents=True, exist_ok=True)

        self._data_dir = data_dir
        self._case_images_dir = images
        self._db_path = data_dir / "yomceph_research.sqlite3"

        with sqlite3.connect(self._db_path) as con:
            con.execute("PRAGMA foreign_keys=ON")
            con.execute("""
                CREATE TABLE IF NOT EXISTS cases (
                    case_id TEXT PRIMARY KEY,
                    analysis_mode TEXT NOT NULL,
                    image_path TEXT,
                    stored_image_path TEXT,
                    face_direction TEXT,
                    mm_per_pixel REAL,
                    points_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            con.execute("""
                CREATE TABLE IF NOT EXISTS measurements (
                    case_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    value REAL NOT NULL,
                    unit TEXT NOT NULL,
                    norm REAL,
                    sd REAL,
                    difference REAL,
                    diagnosis TEXT,
                    PRIMARY KEY(case_id, name),
                    FOREIGN KEY(case_id) REFERENCES cases(case_id) ON DELETE CASCADE
                )
            """)
            con.commit()

    def _install_database_bar(self):
        bar = ttk.Frame(self, padding=(10, 4))
        try:
            bar.pack(fill=tk.X, before=self.body_panes)
        except Exception:
            bar.pack(fill=tk.X)

        ttk.Label(bar, text="Base de investigación", style="Section.TLabel").pack(side=tk.LEFT, padx=(0, 8))
        self.db_counter = ttk.Label(bar, text="0 / 103 casos", style="Muted.TLabel")
        self.db_counter.pack(side=tk.LEFT, padx=(0, 14))
        self.mode_label = ttk.Label(bar, text="Modo: Ambos", style="Muted.TLabel")
        self.mode_label.pack(side=tk.LEFT, padx=(0, 14))

        ttk.Button(bar, text="✓ Guardar en base", command=self.save_case_to_database, style="Mint.TButton").pack(side=tk.LEFT, padx=3)
        ttk.Button(bar, text="Abrir base", command=self.open_database_browser, style="Soft.TButton").pack(side=tk.LEFT, padx=3)
        ttk.Button(bar, text="Exportar CSV para Excel", command=self.export_database_csv, style="Gold.TButton").pack(side=tk.LEFT, padx=3)
        ttk.Button(bar, text="Nuevo caso / análisis", command=self.new_case, style="Turquoise.TButton").pack(side=tk.LEFT, padx=3)

    def _install_database_menu(self):
        try:
            menu_name = self.cget("menu")
            menubar = self.nametowidget(menu_name) if menu_name else tk.Menu(self)
        except Exception:
            menubar = tk.Menu(self)
            self.config(menu=menubar)
        menu = tk.Menu(menubar, tearoff=False)
        menu.add_command(label="Guardar / actualizar caso en base", command=self.save_case_to_database)
        menu.add_command(label="Abrir casos guardados", command=self.open_database_browser)
        menu.add_command(label="Exportar base completa a CSV", command=self.export_database_csv)
        menu.add_separator()
        menu.add_command(label="Cambiar tipo de análisis", command=self.choose_analysis_mode)
        menu.add_command(label="Nuevo caso", command=self.new_case)
        menubar.add_cascade(label="BASE DE DATOS", menu=menu)

    def _db_case_count(self):
        try:
            with sqlite3.connect(self._db_path) as con:
                return int(con.execute("SELECT COUNT(*) FROM cases").fetchone()[0])
        except Exception:
            return 0

    def _update_db_counter(self):
        n = self._db_case_count()
        if hasattr(self, "db_counter"):
            self.db_counter.config(text=f"{n} / {TARGET_CASES} casos guardados")
        if hasattr(self, "mode_label"):
            self.mode_label.config(text=f"Modo: {self.analysis_mode}")

    def _backup_database(self):
        if not self._db_path or not self._db_path.exists():
            return
        stamp = datetime.now().strftime("%Y-%m-%d")
        target = self._data_dir / "backups" / f"yomceph_research_{stamp}.sqlite3"
        try:
            shutil.copy2(self._db_path, target)
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Selector Steiner / postura / ambos
    # ------------------------------------------------------------------
    def choose_analysis_mode(self, startup=False):
        win = tk.Toplevel(self)
        win.title("Elegir análisis")
        win.transient(self)
        win.grab_set()
        win.resizable(False, False)
        win.configure(bg=ui.C["paper"])

        tk.Label(win, text="¿Qué análisis desea realizar?", bg=ui.C["purple"], fg="white",
                 font=("Segoe UI Semibold", 16), padx=22, pady=14).pack(fill=tk.X)
        tk.Label(win,
                 text="La lista de puntos se adapta automáticamente. En modo Steiner no se muestra la guía del plano vertebral.",
                 bg=ui.C["paper"], fg=ui.C["text"], wraplength=520, justify=tk.LEFT,
                 font=("Segoe UI", 10), padx=18, pady=12).pack(fill=tk.X)

        choice = tk.StringVar(value=self.analysis_mode if self.analysis_mode in ("Steiner", "Postura craneofacial", "Ambos") else "Ambos")
        box = ttk.Frame(win, padding=(18, 0, 18, 12))
        box.pack(fill=tk.BOTH)
        for label, desc in [
            ("Steiner", "Esquelético, vertical, dental, plano oclusal, línea S y medidas lineales del protocolo."),
            ("Postura craneofacial", "OPT/CVT, C2–C7, McGregor/odontoides, profundidad cervical y Powell."),
            ("Ambos", "Activa los dos grupos en el mismo caso."),
        ]:
            row = ttk.Frame(box, style="Panel.TFrame", padding=8)
            row.pack(fill=tk.X, pady=4)
            ttk.Radiobutton(row, text=label, value=label, variable=choice).pack(anchor="w")
            ttk.Label(row, text=desc, style="Muted.TLabel", wraplength=470).pack(anchor="w", padx=(24, 0))

        def accept():
            self.apply_analysis_mode(choice.get())
            win.destroy()

        buttons = ttk.Frame(win, padding=(18, 0, 18, 16))
        buttons.pack(fill=tk.X)
        ttk.Button(buttons, text="Continuar", command=accept, style="Purple.TButton").pack(side=tk.RIGHT)
        if not startup:
            ttk.Button(buttons, text="Cancelar", command=win.destroy, style="Soft.TButton").pack(side=tk.RIGHT, padx=6)
        win.protocol("WM_DELETE_WINDOW", accept if startup else win.destroy)
        win.update_idletasks()
        x = max(0, (self.winfo_screenwidth() - win.winfo_reqwidth()) // 2)
        y = max(0, (self.winfo_screenheight() - win.winfo_reqheight()) // 2)
        win.geometry(f"+{x}+{y}")

    def apply_analysis_mode(self, mode):
        if mode not in ("Steiner", "Postura craneofacial", "Ambos"):
            mode = "Ambos"
        self.analysis_mode = mode
        if mode == "Steiner":
            active_set = set(STEINER_POINTS)
        elif mode == "Postura craneofacial":
            active_set = set(POSTURE_POINTS)
        else:
            active_set = set(STEINER_POINTS) | set(POSTURE_POINTS)
        self.active_point_order = [k for k in MASTER_ORDER if k in active_set]
        self._set_vertebral_visibility(mode != "Steiner")
        self._rebuild_active_point_list()
        self._update_db_counter()
        self.status.config(text=f"Análisis seleccionado: {mode}. Sólo se muestran los puntos necesarios.")

    def _capture_vertebral_tab(self):
        try:
            self._vertebral_tab = self.guide_canvas.master
            self._vertebral_notebook = self._vertebral_tab.master
        except Exception:
            self._vertebral_tab = None
            self._vertebral_notebook = None

    def _set_vertebral_visibility(self, visible):
        if not self._vertebral_tab or not self._vertebral_notebook:
            return
        try:
            tabs = self._vertebral_notebook.tabs()
            tab_name = str(self._vertebral_tab)
            if visible and tab_name not in tabs:
                self._vertebral_notebook.add(self._vertebral_tab, text="Plano vertebral")
            elif not visible and tab_name in tabs:
                self._vertebral_notebook.forget(self._vertebral_tab)
        except Exception:
            pass

    def _rebuild_active_point_list(self):
        if not hasattr(self, "point_list"):
            return
        current = self.selected_point.get()
        self.point_list.delete(0, tk.END)
        for key in self.active_point_order:
            title = MASTER_INFO[key][0]
            placed = key in self.points
            self.point_list.insert(tk.END, f"{'✓' if placed else '○'} {key} · {title}")
            self.point_list.itemconfig(tk.END, foreground=("#238B67" if placed else ui.C["muted"]))
        if not self.active_point_order:
            return
        if current not in self.active_point_order:
            current = next((k for k in self.active_point_order if k not in self.points), self.active_point_order[0])
            self.selected_point.set(current)
        idx = self.active_point_order.index(current)
        self.point_list.selection_set(idx)
        self.point_list.see(idx)
        self.update_point_guide()

    def _refresh_point_list_marks(self):
        # Versión filtrada del sistema de palomitas verdes de v0.9.
        if not hasattr(self, "point_list"):
            return
        current = self.selected_point.get()
        try:
            self.point_list.delete(0, tk.END)
            selected = 0
            for i, key in enumerate(self.active_point_order):
                title = MASTER_INFO[key][0]
                placed = key in self.points
                self.point_list.insert(tk.END, f"{'✓' if placed else '○'} {key} · {title}")
                self.point_list.itemconfig(i, foreground=("#238B67" if placed else ui.C["muted"]))
                if key == current:
                    selected = i
            if self.active_point_order:
                self.point_list.selection_set(selected)
                self.point_list.see(selected)
        except Exception:
            pass

    def on_list_select(self, _event=None):
        sel = self.point_list.curselection()
        if not sel or sel[0] >= len(self.active_point_order):
            return
        self.selected_point.set(self.active_point_order[sel[0]])
        self.update_point_guide()
        self.redraw()

    def select_index(self, idx):
        if not self.active_point_order:
            return
        idx = max(0, min(len(self.active_point_order) - 1, idx))
        self.point_list.selection_clear(0, tk.END)
        self.point_list.selection_set(idx)
        self.point_list.see(idx)
        self.selected_point.set(self.active_point_order[idx])
        self.update_point_guide()
        self.redraw()

    def next_point(self):
        if not self.active_point_order:
            return
        key = self.selected_point.get()
        i = self.active_point_order.index(key) if key in self.active_point_order else 0
        self.select_index((i + 1) % len(self.active_point_order))

    def previous_point(self):
        if not self.active_point_order:
            return
        key = self.selected_point.get()
        i = self.active_point_order.index(key) if key in self.active_point_order else 0
        self.select_index((i - 1) % len(self.active_point_order))

    def _select_key(self, key):
        if key not in self.active_point_order:
            return
        self.select_index(self.active_point_order.index(key))

    # Bloquea recorridos que no corresponden al modo actual.
    def _posture_enabled(self):
        return self.analysis_mode in ("Postura craneofacial", "Ambos")

    def _steiner_enabled(self):
        return self.analysis_mode in ("Steiner", "Ambos")

    def start_opt_guide(self):
        if not self._posture_enabled():
            messagebox.showinfo("Análisis", "OPT/CVT pertenece al módulo de postura craneofacial. Cambie a Postura o Ambos.")
            return
        super().start_opt_guide()

    def start_posterior_guide(self):
        if not self._posture_enabled():
            messagebox.showinfo("Análisis", "Las tangentes C2–C7 pertenecen al módulo de postura craneofacial.")
            return
        super().start_posterior_guide()

    def start_mcgregor_guide(self):
        if not self._posture_enabled():
            messagebox.showinfo("Análisis", "McGregor/odontoides pertenece al módulo de postura craneofacial.")
            return
        super().start_mcgregor_guide()

    def start_powell_guide(self):
        if not self._posture_enabled():
            messagebox.showinfo("Análisis", "Powell está agrupado en el módulo de postura craneofacial/perfil.")
            return
        super().start_powell_guide()

    def start_dental_guide(self):
        if not self._steiner_enabled():
            messagebox.showinfo("Análisis", "Los incisivos del protocolo están en el módulo Steiner. Cambie a Steiner o Ambos.")
            return
        super().start_dental_guide()

    # ------------------------------------------------------------------
    # Nuevas mediciones
    # ------------------------------------------------------------------
    def _mm(self, px):
        if not self.mm_per_pixel:
            return None
        return px * self.mm_per_pixel

    def _signed_s_line_distance(self, point_key):
        if not self.mm_per_pixel or not self.require("Ssoft", "Pgsoft", point_key):
            return None
        a = self.points["Ssoft"]
        b = self.points["Pgsoft"]
        p = self.points[point_key]
        d = core.point_line_distance(p, a, b) * self.mm_per_pixel
        mid = ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)
        face_sign = 1 if self.face_direction.get() == "right" else -1
        anterior_ref = (mid[0] + face_sign * 20.0, mid[1])
        ref_side = _line_side(a, b, anterior_ref)
        p_side = _line_side(a, b, p)
        sign = 1.0 if ref_side == 0 or p_side == 0 or (ref_side > 0) == (p_side > 0) else -1.0
        return sign * d

    def calculate_values(self):
        r = super().calculate_values()

        # Evita duplicar las normas dentales antiguas de versiones anteriores.
        r.pop("U1–NA", None)
        r.pop("L1–NB", None)
        r.pop("Interincisal", None)

        if self._steiner_enabled():
            if self.require("Po", "Or", "ANS", "PNS"):
                raw = core.angle_lines(self.points["Po"], self.points["Or"], self.points["ANS"], self.points["PNS"])
                r["Frankfort–SPP"] = min(raw, 180.0 - raw)
            if self.require("S", "N", "D"):
                r["SND"] = core.angle3(self.points["S"], self.points["N"], self.points["D"])
            if self.mm_per_pixel and self.require("S", "N", "Pg"):
                L = _project_to_line(self.points["Pg"], self.points["S"], self.points["N"])
                r["SL"] = core.dist(self.points["S"], L) * self.mm_per_pixel
            if self.mm_per_pixel and self.require("S", "N", "CI"):
                E = _project_to_line(self.points["CI"], self.points["S"], self.points["N"])
                r["SE"] = core.dist(self.points["S"], E) * self.mm_per_pixel
            if self.require("Ar", "Go", "Me"):
                r["Ar–Go–Me"] = core.angle3(self.points["Ar"], self.points["Go"], self.points["Me"])
            if self.require("A", "B", "Go", "Gn"):
                raw = core.angle_lines(self.points["A"], self.points["B"], self.points["Go"], self.points["Gn"])
                r["AB–GoGn"] = core.closest_supplement(raw, 74.0)
            if self.require("U1a", "U1i", "S", "N"):
                raw = core.angle_lines(self.points["U1a"], self.points["U1i"], self.points["S"], self.points["N"])
                r["IS–SN"] = core.closest_supplement(raw, 104.0)
            if self.require("U1a", "U1i", "N", "A"):
                raw = core.angle_lines(self.points["U1a"], self.points["U1i"], self.points["N"], self.points["A"])
                r["IS–NA (°)"] = min(raw, 180.0 - raw)
            if self.mm_per_pixel and self.require("U1i", "N", "A"):
                r["IS–NA (mm)"] = core.point_line_distance(self.points["U1i"], self.points["N"], self.points["A"]) * self.mm_per_pixel
            if self.require("L1a", "L1i", "N", "B"):
                raw = core.angle_lines(self.points["L1a"], self.points["L1i"], self.points["N"], self.points["B"])
                r["II–NB (°)"] = min(raw, 180.0 - raw)
            if self.mm_per_pixel and self.require("L1i", "N", "B"):
                r["II–NB (mm)"] = core.point_line_distance(self.points["L1i"], self.points["N"], self.points["B"]) * self.mm_per_pixel
            if self.require("OcA", "OcP", "S", "N"):
                raw = core.angle_lines(self.points["OcA"], self.points["OcP"], self.points["S"], self.points["N"])
                r["Plano oclusal–SN"] = min(raw, 180.0 - raw)
            if self.require("U1a", "U1i", "L1a", "L1i"):
                raw = core.angle_lines(self.points["U1a"], self.points["U1i"], self.points["L1a"], self.points["L1i"])
                acute = min(raw, 180.0 - raw)
                r["Ángulo interincisal"] = 180.0 - acute
            d = self._signed_s_line_distance("Ls")
            if d is not None:
                r["Línea S · labio superior"] = d
            d = self._signed_s_line_distance("Li")
            if d is not None:
                r["Línea S · labio inferior"] = d
            if self.mm_per_pixel and self.require("Pg", "N", "B"):
                r["Pg–NB"] = core.point_line_distance(self.points["Pg"], self.points["N"], self.points["B"]) * self.mm_per_pixel

        # Si el usuario eligió únicamente Steiner no se guardan resultados
        # cervicales residuales de un proyecto cargado previamente.
        if self.analysis_mode == "Steiner":
            for key in list(r.keys()):
                if key in POSTURE_ORDER or key.startswith("Powell ") or key == "_posterior_tangents_complete" or key == "_cervical_anterior_sign":
                    r.pop(key, None)
        elif self.analysis_mode == "Postura craneofacial":
            for key in list(r.keys()):
                if key in STEINER_ORDER or key in ("SNA", "SNB", "ANB", "SN–PoOr", "SN–GoGn"):
                    r.pop(key, None)
        return r

    @staticmethod
    def _finite(value):
        return isinstance(value, (int, float)) and math.isfinite(value)

    def _protocol_diagnosis(self, key, value):
        mean, sd, unit, low, normal, high = STEINER_PROTOCOL[key]
        lo, hi = mean - sd, mean + sd
        if value < lo:
            state, dx = "DISMINUIDO", low
        elif value > hi:
            state, dx = "AUMENTADO", high
        else:
            state, dx = "EN NORMA", normal
        difference = value - mean
        return state, dx, difference, mean, sd, unit

    def _measurement_unit(self, key):
        if key in STEINER_PROTOCOL:
            return STEINER_PROTOCOL[key][2]
        if key == "Profundidad cervical (mm)":
            return "mm"
        return "°"

    def _diagnosis_for_result(self, key, value, r):
        if key in STEINER_PROTOCOL:
            state, dx, difference, mean, sd, unit = self._protocol_diagnosis(key, value)
            return f"Diagnóstico cefalométrico: {dx}  Diferencia respecto a la norma: {difference:+.2f}{unit}."
        if key == "Profundidad cervical (mm)":
            return "Interpretación clínica: " + self.cervical_interpretation(r)
        return self._result_interpretation(key, value, r)

    def _active_measure_order(self):
        order = []
        if self._steiner_enabled():
            order.extend(STEINER_ORDER)
        if self._posture_enabled():
            order.extend(POSTURE_ORDER)
        # deduplicación conservando orden
        out = []
        for k in order:
            if k not in out:
                out.append(k)
        return out

    def calculate(self):
        r = self.calculate_values()
        self.results_cache = r
        lines = []
        count = 0
        for key in self._active_measure_order():
            value = r.get(key)
            if not self._finite(value):
                continue
            count += 1
            unit = self._measurement_unit(key)
            display = "Profundidad cervical" if key == "Profundidad cervical (mm)" else key
            lines.append(f"{display}: {value:.2f}{unit}")
            if key in STEINER_PROTOCOL:
                mean, sd, _, _, _, _ = STEINER_PROTOCOL[key]
                lines.append(f"Norma del protocolo: {mean:g}{unit} ± {sd:g}{unit}")
            diagnosis = self._diagnosis_for_result(key, value, r)
            if diagnosis:
                lines.append(diagnosis)
            lines.append("")
        if not lines:
            lines = ["Aún no hay mediciones calculables con los puntos colocados."]
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete("1.0", tk.END)
        self.results_text.insert("1.0", "\n".join(lines).strip())
        self.results_text.config(state=tk.DISABLED)
        self.status.config(text=f"Análisis calculado: {count} mediciones con valor.")
        self.hide_traces()

    # ------------------------------------------------------------------
    # Guardar / abrir / exportar la investigación
    # ------------------------------------------------------------------
    def _copy_case_image(self, case_id):
        if not self.image_path or not os.path.exists(self.image_path):
            return self.image_path or ""
        src = Path(self.image_path)
        suffix = src.suffix.lower() if src.suffix else ".png"
        target = self._case_images_dir / f"{_sanitize_case_id(case_id)}{suffix}"
        try:
            if src.resolve() != target.resolve():
                shutil.copy2(src, target)
            return str(target)
        except Exception:
            return str(src)

    def save_case_to_database(self):
        case_id = self.case_id.get().strip()
        if not case_id:
            messagebox.showwarning("Base de datos", "Escriba primero el número o identificador del caso.")
            return
        if not self.original:
            messagebox.showwarning("Base de datos", "Abra la radiografía del caso antes de guardarlo.")
            return

        r = self.calculate_values()
        now = datetime.now().isoformat(timespec="seconds")
        stored_image = self._copy_case_image(case_id)
        points_json = json.dumps(self.points, ensure_ascii=False)

        with sqlite3.connect(self._db_path) as con:
            exists = con.execute("SELECT 1 FROM cases WHERE case_id=?", (case_id,)).fetchone() is not None
            if exists:
                ok = messagebox.askyesno("Actualizar caso", f"El caso {case_id} ya existe.\n\n¿Desea actualizar sus puntos y resultados?")
                if not ok:
                    return
                created = con.execute("SELECT created_at FROM cases WHERE case_id=?", (case_id,)).fetchone()[0]
            else:
                created = now

            con.execute("""
                INSERT INTO cases(case_id, analysis_mode, image_path, stored_image_path, face_direction, mm_per_pixel, points_json, created_at, updated_at)
                VALUES(?,?,?,?,?,?,?,?,?)
                ON CONFLICT(case_id) DO UPDATE SET
                    analysis_mode=excluded.analysis_mode,
                    image_path=excluded.image_path,
                    stored_image_path=excluded.stored_image_path,
                    face_direction=excluded.face_direction,
                    mm_per_pixel=excluded.mm_per_pixel,
                    points_json=excluded.points_json,
                    updated_at=excluded.updated_at
            """, (case_id, self.analysis_mode, self.image_path or "", stored_image or "", self.face_direction.get(), self.mm_per_pixel, points_json, created, now))
            con.execute("DELETE FROM measurements WHERE case_id=?", (case_id,))

            for key in self._active_measure_order():
                value = r.get(key)
                if not self._finite(value):
                    continue
                unit = self._measurement_unit(key)
                norm = sd = diff = None
                diagnosis = self._diagnosis_for_result(key, value, r)
                if key in STEINER_PROTOCOL:
                    _, dx, diff, norm, sd, unit = self._protocol_diagnosis(key, value)
                    diagnosis = dx
                con.execute("""
                    INSERT INTO measurements(case_id, name, value, unit, norm, sd, difference, diagnosis)
                    VALUES(?,?,?,?,?,?,?,?)
                """, (case_id, key, float(value), unit, norm, sd, diff, diagnosis))
            con.commit()

        self._backup_database()
        self.results_cache = r
        self._update_db_counter()
        self.status.config(text=f"✓ Caso {case_id} guardado permanentemente en la base de investigación.")
        messagebox.showinfo("Base de datos", f"Caso {case_id} guardado.\n\nLa información permanecerá disponible aunque cierre la app o apague la computadora.")

    def open_database_browser(self):
        win = tk.Toplevel(self)
        win.title("YomCeph · Base de investigación")
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        w, h = min(1050, int(sw * 0.86)), min(700, int(sh * 0.82))
        win.geometry(f"{w}x{h}+{max(0,(sw-w)//2)}+{max(0,(sh-h)//2)}")

        header = tk.Frame(win, bg=ui.C["purple"], height=66)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text="Base de datos de la investigación", bg=ui.C["purple"], fg="white",
                 font=("Segoe UI Semibold", 17)).pack(anchor="w", padx=16, pady=(9, 0))
        tk.Label(header, text=f"Archivo persistente: {self._db_path}", bg=ui.C["purple"], fg=ui.C["lilac_soft"],
                 font=("Segoe UI", 8)).pack(anchor="w", padx=16)

        frame = ttk.Frame(win, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        cols = ("case", "mode", "measurements", "updated")
        tree = ttk.Treeview(frame, columns=cols, show="headings")
        tree.heading("case", text="Caso")
        tree.heading("mode", text="Análisis")
        tree.heading("measurements", text="Mediciones guardadas")
        tree.heading("updated", text="Última actualización")
        tree.column("case", width=100, anchor="center")
        tree.column("mode", width=210)
        tree.column("measurements", width=160, anchor="center")
        tree.column("updated", width=210)
        sy = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sy.set)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sy.pack(side=tk.RIGHT, fill=tk.Y)

        with sqlite3.connect(self._db_path) as con:
            rows = con.execute("""
                SELECT c.case_id, c.analysis_mode, COUNT(m.name), c.updated_at
                FROM cases c LEFT JOIN measurements m ON c.case_id=m.case_id
                GROUP BY c.case_id, c.analysis_mode, c.updated_at
                ORDER BY CASE WHEN c.case_id GLOB '[0-9]*' THEN CAST(c.case_id AS INTEGER) ELSE 999999 END, c.case_id
            """).fetchall()
        for row in rows:
            tree.insert("", tk.END, values=row)

        buttons = ttk.Frame(win, padding=(10, 0, 10, 10))
        buttons.pack(fill=tk.X)

        def open_selected():
            sel = tree.selection()
            if not sel:
                return
            case = str(tree.item(sel[0], "values")[0])
            win.destroy()
            self.load_case_from_database(case)

        ttk.Button(buttons, text="Abrir caso seleccionado", command=open_selected, style="Purple.TButton").pack(side=tk.LEFT)
        ttk.Button(buttons, text="Exportar CSV para Excel", command=self.export_database_csv, style="Gold.TButton").pack(side=tk.LEFT, padx=6)
        ttk.Label(buttons, text=f"{len(rows)} / {TARGET_CASES} casos", style="Muted.TLabel").pack(side=tk.RIGHT)
        tree.bind("<Double-1>", lambda e: open_selected())

    def load_case_from_database(self, case_id):
        with sqlite3.connect(self._db_path) as con:
            row = con.execute("""
                SELECT case_id, analysis_mode, image_path, stored_image_path, face_direction, mm_per_pixel, points_json
                FROM cases WHERE case_id=?
            """, (case_id,)).fetchone()
        if not row:
            messagebox.showerror("Base de datos", "No se encontró el caso.")
            return
        _, mode, original_path, stored_path, face, mmpp, points_json = row
        path = stored_path if stored_path and os.path.exists(stored_path) else original_path
        if not path or not os.path.exists(path):
            messagebox.showerror("Radiografía no encontrada", "Los datos del caso existen, pero no se encontró la copia de la radiografía.")
            return
        try:
            self.original = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
        except Exception as exc:
            messagebox.showerror("Error", f"No se pudo abrir la radiografía guardada.\n\n{exc}")
            return

        self.image_path = path
        raw_points = json.loads(points_json or "{}")
        self.points = {k: tuple(v) for k, v in raw_points.items() if isinstance(v, (list, tuple)) and len(v) == 2}
        self.mm_per_pixel = mmpp
        self.face_direction.set(face or "right")
        self.case_id.set(case_id)
        self.calibration_points = []
        self.cal_label.config(text=(f"Calibrado: {mmpp:.5f} mm/píxel" if mmpp else "Sin calibración"))
        self.apply_analysis_mode(mode or "Ambos")
        self.after(40, self.fit_image)
        self.update_point_guide()
        self.status.config(text=f"Caso {case_id} cargado desde la base. Puede corregir cualquier punto y volver a guardar.")

    def export_database_csv(self):
        path = filedialog.asksaveasfilename(
            title="Exportar base para Excel",
            defaultextension=".csv",
            initialfile="YomCeph_base_103_casos.csv",
            filetypes=[("CSV compatible con Excel", "*.csv")],
        )
        if not path:
            return

        all_keys = []
        for k in STEINER_ORDER + POSTURE_ORDER:
            if k not in all_keys:
                all_keys.append(k)

        with sqlite3.connect(self._db_path) as con:
            cases = con.execute("SELECT case_id, analysis_mode, updated_at FROM cases ORDER BY case_id").fetchall()
            data = {}
            for case_id, name, value, diagnosis in con.execute("SELECT case_id, name, value, diagnosis FROM measurements"):
                data.setdefault(case_id, {})[name] = (value, diagnosis or "")

        headers = ["Caso", "Tipo de análisis", "Última actualización"]
        for key in all_keys:
            display = "Profundidad cervical" if key == "Profundidad cervical (mm)" else key
            headers.extend([display, display + " - Diagnóstico"])

        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            for case_id, mode, updated in cases:
                row = [case_id, mode, updated]
                measures = data.get(case_id, {})
                for key in all_keys:
                    if key in measures:
                        value, diagnosis = measures[key]
                        row.extend([value, diagnosis])
                    else:
                        row.extend(["", ""])
                writer.writerow(row)
        self.status.config(text=f"Base completa exportada: {os.path.basename(path)}")
        messagebox.showinfo("Exportación", f"Base exportada correctamente.\n\nCasos: {len(cases)}\nArchivo: {path}")

    def new_case(self):
        if self.points or self.case_id.get().strip():
            if not messagebox.askyesno("Nuevo caso", "¿Iniciar un nuevo caso?\n\nSi hizo cambios en el caso actual, guárdelo primero en la base de datos."):
                return
        self.image_path = None
        self.original = None
        self.points = {}
        self.results_cache = {}
        self.mm_per_pixel = None
        self.calibration_points = []
        self.case_id.set("")
        self.cal_label.config(text="Sin calibración")
        self.redraw()
        self.choose_analysis_mode(startup=False)

    # ------------------------------------------------------------------
    # Ayuda visual actualizada con el protocolo recibido
    # ------------------------------------------------------------------
    def open_measurement_help(self, tab=0):
        win = tk.Toplevel(self)
        win.title("YomCeph · Ayuda visual del protocolo")
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        w, h = min(1540, int(sw * 0.94)), min(860, int(sh * 0.88))
        win.geometry(f"{w}x{h}+{max(0,(sw-w)//2)}+{max(0,(sh-h)//2)}")
        win.configure(bg=ui.C["paper"])

        header = tk.Frame(win, bg=ui.C["purple"], height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text="Ayuda visual · normas del protocolo", bg=ui.C["purple"], fg="white",
                 font=("Segoe UI Semibold", 18)).pack(anchor="w", padx=18, pady=(9, 0))
        tk.Label(header, text="Disminuido · en norma · aumentado · diagnóstico cefalométrico",
                 bg=ui.C["purple"], fg=ui.C["lilac_soft"], font=("Segoe UI", 9)).pack(anchor="w", padx=18)

        note = tk.Label(win,
            text=("Las cifras de la pestaña Steiner corresponden exactamente a la tabla proporcionada para esta investigación. "
                  "Algunas difieren de publicaciones clásicas de Steiner; por eso YomCeph las identifica como NORMAS DEL PROTOCOLO y no como valores universales. "
                  "Las medidas lineales en mm sólo aparecen cuando la radiografía fue calibrada."),
            bg=ui.C["mint"], fg=ui.C["text"], justify=tk.LEFT, wraplength=max(700, w-60),
            font=("Segoe UI", 9), padx=12, pady=9)
        note.pack(fill=tk.X, padx=12, pady=(10, 6))

        nb = ttk.Notebook(win)
        nb.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 10))
        steiner_tab = ttk.Frame(nb, style="Panel.TFrame", padding=6)
        posture_tab = ttk.Frame(nb, style="Panel.TFrame", padding=6)
        nb.add(steiner_tab, text="Steiner · protocolo de investigación")
        nb.add(posture_tab, text="Postura craneofacial / Powell")

        cols = ("medida", "norma", "de", "bajo", "normal", "alto")
        tree = ttk.Treeview(steiner_tab, columns=cols, show="headings", height=21)
        for key, title in [("medida", "Ángulo / línea"), ("norma", "Norma"), ("de", "DE"),
                           ("bajo", "Disminuye"), ("normal", "En norma"), ("alto", "Aumenta")]:
            tree.heading(key, text=title)
        tree.column("medida", width=170)
        tree.column("norma", width=90, anchor="center")
        tree.column("de", width=80, anchor="center")
        tree.column("bajo", width=360)
        tree.column("normal", width=360)
        tree.column("alto", width=360)
        sy = ttk.Scrollbar(steiner_tab, orient="vertical", command=tree.yview)
        sx = ttk.Scrollbar(steiner_tab, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
        tree.grid(row=0, column=0, sticky="nsew")
        sy.grid(row=0, column=1, sticky="ns")
        sx.grid(row=1, column=0, sticky="ew")
        steiner_tab.rowconfigure(0, weight=1)
        steiner_tab.columnconfigure(0, weight=1)
        for key in STEINER_ORDER:
            mean, sd, unit, low, normal, high = STEINER_PROTOCOL[key]
            tree.insert("", tk.END, values=(key, f"{mean:g}{unit}", f"±{sd:g}{unit}", low, normal, high))

        pcols = ("medida", "ref", "bajo", "normal", "alto")
        ptree = ttk.Treeview(posture_tab, columns=pcols, show="headings", height=21)
        for key, title in [("medida", "Medición"), ("ref", "Referencia"), ("bajo", "Disminuye"),
                           ("normal", "En referencia"), ("alto", "Aumenta")]:
            ptree.heading(key, text=title)
        ptree.column("medida", width=190)
        ptree.column("ref", width=210)
        ptree.column("bajo", width=380)
        ptree.column("normal", width=360)
        ptree.column("alto", width=380)
        psy = ttk.Scrollbar(posture_tab, orient="vertical", command=ptree.yview)
        psx = ttk.Scrollbar(posture_tab, orient="horizontal", command=ptree.xview)
        ptree.configure(yscrollcommand=psy.set, xscrollcommand=psx.set)
        ptree.grid(row=0, column=0, sticky="nsew")
        psy.grid(row=0, column=1, sticky="ns")
        psx.grid(row=1, column=0, sticky="ew")
        posture_tab.rowconfigure(0, weight=1)
        posture_tab.columnconfigure(0, weight=1)
        posture_names = {"SN–OPT", "SN–CVT", "OPT–CVT", "Tangente posterior C2–C7", "MGP–OP", "MGP–CVT",
                         "Powell nasofrontal", "Powell nasofacial", "Powell nasomental", "Powell mentocervical", "Profundidad cervical"}
        for row in v10.MEASURE_ROWS:
            if row[0] in posture_names:
                ptree.insert("", tk.END, values=(row[0], row[2], row[3], row[4], row[5]))

        try:
            nb.select(tab)
        except Exception:
            pass


if __name__ == "__main__":
    ui.enable_dpi_awareness()
    app = ResearchDatabaseYomCeph()
    app.mainloop()
