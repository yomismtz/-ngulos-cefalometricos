import csv
import json
import math
import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
from PIL import Image, ImageDraw, ImageOps, ImageTk

APP_NAME = "YomCeph Desktop · Investigación"
APP_VERSION = "0.1.0"

POINTS = [
    ("S", "Sella (S)", "Centro geométrico de la silla turca."),
    ("N", "Nasion (N)", "Punto más anterior de la sutura frontonasal."),
    ("A", "Punto A", "Punto más profundo de la concavidad anterior del maxilar, entre la espina nasal anterior y el proceso alveolar."),
    ("B", "Punto B", "Punto más profundo de la concavidad anterior de la sínfisis mandibular."),
    ("Po", "Porion (Po)", "Punto más superior del borde del conducto auditivo externo utilizado para construir el plano de Frankfort."),
    ("Or", "Orbitale (Or)", "Punto más inferior del reborde orbitario."),
    ("Go", "Gonion (Go)", "Punto construido en el ángulo mandibular, sobre la bisectriz entre la tangente al borde posterior de la rama y la tangente al borde inferior mandibular."),
    ("Gn", "Gnathion (Gn)", "Punto más anteroinferior del contorno de la sínfisis mandibular."),
    ("cv2tg", "cv2tg", "Punto de tangencia en el contorno posterior de C2 usado para construir las tangentes OPT y CVT."),
    ("cv2ip", "cv2ip", "Punto posteroinferior del cuerpo de C2. Junto con cv2tg define la tangente OPT."),
    ("cv4ip", "cv4ip", "Punto posteroinferior del cuerpo de C4. Junto con cv2tg define la tangente CVT."),
    ("C2ps", "C2 posterior superior", "Punto posterior superior de C2 usado como extremo superior de la tangente cervical para valorar profundidad de la curva."),
    ("C7pi", "C7 posterior inferior", "Punto posterior inferior de C7 usado como extremo inferior de la tangente cervical para valorar profundidad de la curva."),
    ("PC", "Profundidad cervical", "Punto de máxima profundidad de la curvatura cervical respecto a la tangente C2–C7."),
]
POINT_ORDER = [p[0] for p in POINTS]
POINT_INFO = {p[0]: (p[1], p[2]) for p in POINTS}

MEASUREMENT_INFO = {
    "SNA": (80, 84, "82° ± 2°", "Posición maxilar relativamente posterior respecto a SN.", "Posición maxilar dentro del rango de referencia adoptado.", "Posición maxilar relativamente anterior respecto a SN."),
    "SNB": (78, 82, "80° ± 2°", "Posición mandibular relativamente posterior respecto a SN.", "Posición mandibular dentro del rango de referencia adoptado.", "Posición mandibular relativamente anterior respecto a SN."),
    "ANB": (0, 4, "2° ± 2°", "Relación sagital compatible con tendencia esquelética Clase III; corroborar con el resto del análisis.", "Relación sagital dentro del rango de referencia para Clase I.", "Relación sagital compatible con tendencia esquelética Clase II; corroborar con el resto del análisis."),
    "SN–PoOr": (4, 10, "7° ± 3°", "Ángulo SN–Frankfort por debajo del rango adoptado.", "Ángulo SN–Frankfort dentro del rango adoptado.", "Ángulo SN–Frankfort por encima del rango adoptado."),
    "SN–GoGn": (27, 37, "32° ± 5°", "Patrón mandibular relativamente hipodivergente / rotación anterior.", "Inclinación mandibular dentro del rango de referencia adoptado.", "Patrón mandibular relativamente hiperdivergente / rotación posterior."),
    "SN–OPT": (94, 100, "94°–100° · rango del protocolo", "Valor menor al rango del protocolo para la relación SN–OPT.", "Valor dentro del rango del protocolo para la relación SN–OPT.", "Valor mayor al rango del protocolo para la relación SN–OPT."),
    "SN–CVT": (96, 102, "96°–102° · rango del protocolo", "Valor menor al rango del protocolo para la relación SN–CVT.", "Valor dentro del rango del protocolo para la relación SN–CVT.", "Valor mayor al rango del protocolo para la relación SN–CVT."),
}

def dist(a, b):
    return math.hypot(b[0]-a[0], b[1]-a[1])

def angle3(a, b, c):
    v1 = (a[0]-b[0], a[1]-b[1])
    v2 = (c[0]-b[0], c[1]-b[1])
    n1 = math.hypot(*v1); n2 = math.hypot(*v2)
    if n1 == 0 or n2 == 0:
        return float("nan")
    x = max(-1.0, min(1.0, (v1[0]*v2[0] + v1[1]*v2[1])/(n1*n2)))
    return math.degrees(math.acos(x))

def angle_lines(a, b, c, d):
    v1 = (b[0]-a[0], b[1]-a[1])
    v2 = (d[0]-c[0], d[1]-c[1])
    n1 = math.hypot(*v1); n2 = math.hypot(*v2)
    if n1 == 0 or n2 == 0:
        return float("nan")
    x = max(-1.0, min(1.0, (v1[0]*v2[0] + v1[1]*v2[1])/(n1*n2)))
    return math.degrees(math.acos(x))

def closest_supplement(theta, target):
    if math.isnan(theta):
        return theta
    other = 180.0 - theta
    return theta if abs(theta-target) <= abs(other-target) else other

def point_line_distance(p, a, b):
    dx, dy = b[0]-a[0], b[1]-a[1]
    den = math.hypot(dx, dy)
    if den == 0:
        return float("nan")
    return abs(dy*p[0] - dx*p[1] + b[0]*a[1] - b[1]*a[0]) / den

def x_on_line_at_y(a, b, y):
    if abs(b[1]-a[1]) < 1e-9:
        return (a[0]+b[0])/2
    t = (y-a[1])/(b[1]-a[1])
    return a[0] + t*(b[0]-a[0])

class YomCephDesktop(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("1500x900")
        self.minsize(1100, 700)
        self.image_path = None
        self.original = None
        self.tk_image = None
        self.scale = 1.0
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.points = {}
        self.selected_point = tk.StringVar(value=POINT_ORDER[0])
        self.case_id = tk.StringVar(value="")
        self.face_direction = tk.StringVar(value="right")
        self.mm_per_pixel = None
        self.calibration_points = []
        self.calibrating = False
        self._pan_last = None
        self._dragging_point = False
        self.results_cache = {}
        self._build_ui()
        self.after(200, self._fit_if_possible)

    def _build_ui(self):
        top = ttk.Frame(self, padding=8)
        top.pack(side=tk.TOP, fill=tk.X)
        ttk.Label(top, text=APP_NAME, font=("Segoe UI", 17, "bold")).pack(side=tk.LEFT, padx=(0, 20))
        ttk.Label(top, text="Caso:").pack(side=tk.LEFT)
        ttk.Entry(top, textvariable=self.case_id, width=12).pack(side=tk.LEFT, padx=(4, 12))
        ttk.Button(top, text="Abrir radiografía", command=self.open_image).pack(side=tk.LEFT, padx=3)
        ttk.Button(top, text="Guardar proyecto", command=self.save_project).pack(side=tk.LEFT, padx=3)
        ttk.Button(top, text="Abrir proyecto", command=self.load_project).pack(side=tk.LEFT, padx=3)
        ttk.Button(top, text="Calibrar mm", command=self.start_calibration).pack(side=tk.LEFT, padx=3)
        ttk.Button(top, text="Calcular", command=self.calculate).pack(side=tk.LEFT, padx=3)
        ttk.Button(top, text="Exportar CSV", command=self.export_csv).pack(side=tk.LEFT, padx=3)
        ttk.Button(top, text="Imagen trazada", command=self.export_annotated).pack(side=tk.LEFT, padx=3)

        main = ttk.Panedwindow(self, orient=tk.HORIZONTAL)
        main.pack(fill=tk.BOTH, expand=True)
        left = ttk.Frame(main, padding=8, width=280)
        center = ttk.Frame(main)
        right = ttk.Frame(main, padding=8, width=390)
        main.add(left, weight=0); main.add(center, weight=4); main.add(right, weight=0)

        ttk.Label(left, text="Puntos anatómicos", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        self.point_list = tk.Listbox(left, height=22, exportselection=False)
        for key, title, _ in POINTS:
            self.point_list.insert(tk.END, f"{key} · {title}")
        self.point_list.selection_set(0)
        self.point_list.bind("<<ListboxSelect>>", self.on_list_select)
        self.point_list.pack(fill=tk.BOTH, expand=True, pady=(6, 8))
        nav = ttk.Frame(left); nav.pack(fill=tk.X)
        ttk.Button(nav, text="← Anterior", command=self.previous_point).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 2))
        ttk.Button(nav, text="Siguiente →", command=self.next_point).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(2, 0))
        ttk.Button(left, text="Borrar punto seleccionado", command=self.delete_selected).pack(fill=tk.X, pady=(6, 0))
        ttk.Button(left, text="Borrar todos", command=self.delete_all).pack(fill=tk.X, pady=(4, 0))
        ttk.Separator(left).pack(fill=tk.X, pady=10)
        ttk.Label(left, text="Orientación del perfil", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        ttk.Radiobutton(left, text="Paciente mira hacia la derecha", value="right", variable=self.face_direction).pack(anchor="w")
        ttk.Radiobutton(left, text="Paciente mira hacia la izquierda", value="left", variable=self.face_direction).pack(anchor="w")
        ttk.Label(left, text="Controles de imagen", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(10, 2))
        ttk.Label(left, text="Rueda: zoom\nBotón derecho + arrastrar: mover\nClic izquierdo: colocar punto\nMantener clic: ajustar punto").pack(anchor="w")
        ttk.Button(left, text="Centrar / ajustar", command=self.fit_image).pack(fill=tk.X, pady=(8, 0))
        self.cal_label = ttk.Label(left, text="Sin calibración", foreground="#555"); self.cal_label.pack(anchor="w", pady=(8, 0))

        self.canvas = tk.Canvas(center, background="#101010", highlightthickness=0, cursor="crosshair")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", lambda e: self.redraw())
        self.canvas.bind("<Button-1>", self.canvas_left_down)
        self.canvas.bind("<B1-Motion>", self.canvas_left_drag)
        self.canvas.bind("<ButtonRelease-1>", self.canvas_left_up)
        self.canvas.bind("<Button-3>", self.pan_start)
        self.canvas.bind("<B3-Motion>", self.pan_move)
        self.canvas.bind("<MouseWheel>", self.zoom)

        notebook = ttk.Notebook(right); notebook.pack(fill=tk.BOTH, expand=True)
        tab_point = ttk.Frame(notebook, padding=10); tab_results = ttk.Frame(notebook, padding=10); tab_vertebral = ttk.Frame(notebook, padding=10)
        notebook.add(tab_point, text="Guía del punto"); notebook.add(tab_results, text="Resultados"); notebook.add(tab_vertebral, text="Plano vertebral")
        self.point_title = ttk.Label(tab_point, text="", font=("Segoe UI", 14, "bold"), wraplength=340); self.point_title.pack(anchor="w")
        self.point_desc = ttk.Label(tab_point, text="", wraplength=340, justify=tk.LEFT); self.point_desc.pack(anchor="w", pady=(8, 12))
        self.point_status = ttk.Label(tab_point, text="", wraplength=340); self.point_status.pack(anchor="w")
        ttk.Separator(tab_point).pack(fill=tk.X, pady=12)
        ttk.Label(tab_point, text="La descripción sirve como guía de localización. La identificación final del landmark corresponde al observador.", wraplength=340, justify=tk.LEFT).pack(anchor="w")
        self.update_point_guide()
        self.results_text = tk.Text(tab_results, wrap=tk.WORD, font=("Consolas", 10), state=tk.DISABLED); self.results_text.pack(fill=tk.BOTH, expand=True)
        ttk.Label(tab_vertebral, text="Análisis del plano vertebral", font=("Segoe UI", 13, "bold")).pack(anchor="w")
        ttk.Label(tab_vertebral, text="La app usa una tangente C2–C7 y el punto de máxima profundidad cervical (PC). Con calibración calcula la profundidad en mm. El intervalo 7–15 mm se muestra como referencia del protocolo aportado por el investigador.", wraplength=340, justify=tk.LEFT).pack(anchor="w", pady=(5, 8))
        self.guide_canvas = tk.Canvas(tab_vertebral, width=340, height=430, background="white", highlightthickness=1); self.guide_canvas.pack(fill=tk.BOTH, expand=True)
        self.guide_canvas.bind("<Configure>", lambda e: self.draw_vertebral_guide())

        status = ttk.Frame(self, padding=(8, 4)); status.pack(side=tk.BOTTOM, fill=tk.X)
        self.status = ttk.Label(status, text="Abra una radiografía lateral para comenzar."); self.status.pack(side=tk.LEFT)
        ttk.Label(status, text=f"v{APP_VERSION} · Uso educativo y de investigación").pack(side=tk.RIGHT)

    def on_list_select(self, _event=None):
        sel = self.point_list.curselection()
        if not sel: return
        self.selected_point.set(POINT_ORDER[sel[0]]); self.update_point_guide(); self.redraw()

    def select_index(self, idx):
        idx = max(0, min(len(POINT_ORDER)-1, idx))
        self.point_list.selection_clear(0, tk.END); self.point_list.selection_set(idx); self.point_list.see(idx)
        self.selected_point.set(POINT_ORDER[idx]); self.update_point_guide(); self.redraw()

    def next_point(self):
        i = POINT_ORDER.index(self.selected_point.get()) if self.selected_point.get() in POINT_ORDER else 0
        self.select_index((i+1) % len(POINT_ORDER))

    def previous_point(self):
        i = POINT_ORDER.index(self.selected_point.get()) if self.selected_point.get() in POINT_ORDER else 0
        self.select_index((i-1) % len(POINT_ORDER))

    def update_point_guide(self):
        key = self.selected_point.get(); title, desc = POINT_INFO[key]
        self.point_title.config(text=f"{key} · {title}"); self.point_desc.config(text=desc)
        self.point_status.config(text="✓ Punto colocado" if key in self.points else "○ Punto pendiente")

    def open_image(self):
        path = filedialog.askopenfilename(title="Seleccionar radiografía lateral", filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.tif *.tiff *.bmp"), ("Todos", "*.*")])
        if not path: return
        try:
            self.original = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
        except Exception as exc:
            messagebox.showerror("Error", f"No se pudo abrir la imagen.\n\n{exc}"); return
        self.image_path = path; self.points.clear(); self.mm_per_pixel = None; self.calibration_points = []
        self.cal_label.config(text="Sin calibración"); self.after(50, self.fit_image); self.status.config(text=os.path.basename(path)); self.update_point_guide()

    def _fit_if_possible(self):
        if self.original: self.fit_image()

    def fit_image(self):
        if not self.original: return
        cw = max(100, self.canvas.winfo_width()); ch = max(100, self.canvas.winfo_height())
        self.scale = min(cw/self.original.width, ch/self.original.height) * 0.97
        self.offset_x = (cw - self.original.width*self.scale)/2; self.offset_y = (ch - self.original.height*self.scale)/2; self.redraw()

    def image_to_canvas(self, p): return (self.offset_x + p[0]*self.scale, self.offset_y + p[1]*self.scale)
    def canvas_to_image(self, x, y):
        if not self.original or self.scale == 0: return None
        ix = max(0.0, min(self.original.width-1.0, (x-self.offset_x)/self.scale)); iy = max(0.0, min(self.original.height-1.0, (y-self.offset_y)/self.scale))
        return (ix, iy)

    def redraw(self):
        self.canvas.delete("all")
        if not self.original:
            self.canvas.create_text(self.canvas.winfo_width()/2, self.canvas.winfo_height()/2, text="Abra una radiografía lateral de cráneo", fill="white", font=("Segoe UI", 16, "bold")); return
        w = max(1, int(self.original.width*self.scale)); h = max(1, int(self.original.height*self.scale))
        resized = self.original.resize((w, h), Image.Resampling.LANCZOS); self.tk_image = ImageTk.PhotoImage(resized)
        self.canvas.create_image(self.offset_x, self.offset_y, image=self.tk_image, anchor="nw"); self._draw_measurement_lines()
        for key, p in self.points.items():
            x, y = self.image_to_canvas(p); r = 6 if key == self.selected_point.get() else 4; color = "#ffd54f" if key == self.selected_point.get() else "#00e5ff"
            self.canvas.create_oval(x-r, y-r, x+r, y+r, outline="black", fill=color, width=1); self.canvas.create_text(x+8, y-8, text=key, fill=color, anchor="sw", font=("Segoe UI", 9, "bold"))
        for i, p in enumerate(self.calibration_points):
            x, y = self.image_to_canvas(p); self.canvas.create_oval(x-5, y-5, x+5, y+5, fill="#ff4081", outline="white"); self.canvas.create_text(x+7, y-7, text=f"Cal{i+1}", fill="#ff4081", anchor="sw")

    def _line(self, a_key, b_key, color="#7CFF6B", width=2, dash=None):
        if a_key in self.points and b_key in self.points:
            a = self.image_to_canvas(self.points[a_key]); b = self.image_to_canvas(self.points[b_key]); self.canvas.create_line(*a, *b, fill=color, width=width, dash=dash)

    def _draw_measurement_lines(self):
        self._line("S","N","#00e5ff"); self._line("Po","Or","#ffd54f"); self._line("Go","Gn","#ff80ab")
        self._line("cv2tg","cv2ip","#80d8ff",3); self._line("cv2tg","cv4ip","#b388ff",3); self._line("C2ps","C7pi","#ff5252",3)
        if "PC" in self.points and "C2ps" in self.points and "C7pi" in self.points:
            p = self.points["PC"]; a=self.points["C2ps"]; b=self.points["C7pi"]; dx,dy=b[0]-a[0],b[1]-a[1]; den=dx*dx+dy*dy
            if den:
                t=((p[0]-a[0])*dx+(p[1]-a[1])*dy)/den; q=(a[0]+t*dx,a[1]+t*dy); ps=self.image_to_canvas(p); qs=self.image_to_canvas(q)
                self.canvas.create_line(*ps,*qs,fill="#ff9800",width=2,dash=(5,3))

    def canvas_left_down(self, event):
        if not self.original: return
        p = self.canvas_to_image(event.x, event.y)
        if p is None: return
        if self.calibrating:
            self.calibration_points.append(p)
            if len(self.calibration_points) == 2: self.finish_calibration()
            self.redraw(); return
        self.points[self.selected_point.get()] = p; self._dragging_point = True; self.update_point_guide(); self.redraw()

    def canvas_left_drag(self, event):
        if not self.original or self.calibrating or not self._dragging_point: return
        p = self.canvas_to_image(event.x, event.y)
        if p: self.points[self.selected_point.get()] = p; self.redraw()

    def canvas_left_up(self, _event):
        if self._dragging_point: self._dragging_point = False; self.update_point_guide()

    def pan_start(self, event): self._pan_last = (event.x, event.y)
    def pan_move(self, event):
        if not self._pan_last: return
        dx = event.x-self._pan_last[0]; dy=event.y-self._pan_last[1]; self.offset_x += dx; self.offset_y += dy; self._pan_last = (event.x,event.y); self.redraw()

    def zoom(self, event): self._zoom_at(event.x, event.y, 1.12 if event.delta > 0 else 1/1.12)
    def _zoom_at(self, x, y, factor):
        if not self.original: return
        before = self.canvas_to_image(x,y); self.scale = max(0.05, min(8.0, self.scale*factor))
        if before: self.offset_x = x-before[0]*self.scale; self.offset_y = y-before[1]*self.scale
        self.redraw()

    def delete_selected(self):
        self.points.pop(self.selected_point.get(), None); self.update_point_guide(); self.redraw()
    def delete_all(self):
        if messagebox.askyesno("Borrar", "¿Borrar todos los puntos colocados?"): self.points.clear(); self.update_point_guide(); self.redraw()

    def start_calibration(self):
        if not self.original: messagebox.showinfo("Calibración", "Primero abra una radiografía."); return
        self.calibration_points = []; self.calibrating = True; self.status.config(text="Calibración: marque dos extremos de una referencia de longitud conocida.")

    def finish_calibration(self):
        self.calibrating = False
        if len(self.calibration_points) != 2: return
        pix = dist(*self.calibration_points)
        if pix < 5: messagebox.showwarning("Calibración", "Los puntos de calibración están demasiado juntos."); self.calibration_points = []; return
        real_mm = simpledialog.askfloat("Calibración", "Longitud real entre los dos puntos (mm):", minvalue=0.1)
        if not real_mm: self.calibration_points = []; return
        self.mm_per_pixel = real_mm/pix; self.cal_label.config(text=f"Calibrado: {self.mm_per_pixel:.5f} mm/píxel"); self.status.config(text=f"Calibración guardada ({real_mm:g} mm)."); self.redraw()

    def require(self, *names): return all(n in self.points for n in names)
    def calculate_values(self):
        r = {}
        if self.require("S","N","A"): r["SNA"] = angle3(self.points["S"],self.points["N"],self.points["A"])
        if self.require("S","N","B"): r["SNB"] = angle3(self.points["S"],self.points["N"],self.points["B"])
        if "SNA" in r and "SNB" in r: r["ANB"] = r["SNA"] - r["SNB"]
        if self.require("S","N","Po","Or"): r["SN–PoOr"] = closest_supplement(angle_lines(self.points["S"],self.points["N"],self.points["Po"],self.points["Or"]),7)
        if self.require("S","N","Go","Gn"): r["SN–GoGn"] = closest_supplement(angle_lines(self.points["S"],self.points["N"],self.points["Go"],self.points["Gn"]),32)
        if self.require("S","N","cv2tg","cv2ip"): r["SN–OPT"] = closest_supplement(angle_lines(self.points["S"],self.points["N"],self.points["cv2tg"],self.points["cv2ip"]),97)
        if self.require("S","N","cv2tg","cv4ip"): r["SN–CVT"] = closest_supplement(angle_lines(self.points["S"],self.points["N"],self.points["cv2tg"],self.points["cv4ip"]),99)
        if self.require("cv2tg","cv2ip","cv4ip"):
            t=angle_lines(self.points["cv2tg"],self.points["cv2ip"],self.points["cv2tg"],self.points["cv4ip"]); r["OPT–CVT"] = min(t,180-t)
        if self.require("C2ps","C7pi","PC"):
            px = point_line_distance(self.points["PC"],self.points["C2ps"],self.points["C7pi"]); r["Profundidad cervical (px)"] = px
            if self.mm_per_pixel:
                r["Profundidad cervical (mm)"] = px*self.mm_per_pixel; xline=x_on_line_at_y(self.points["C2ps"],self.points["C7pi"],self.points["PC"][1]); dx=self.points["PC"][0]-xline; anterior = dx if self.face_direction.get()=="right" else -dx; r["_cervical_anterior_sign"] = 1 if anterior >= 0 else -1
        return r

    def interpret(self, name, value):
        if name not in MEASUREMENT_INFO: return ""
        lo, hi, norm, low, normal, high = MEASUREMENT_INFO[name]; text = low if value < lo else high if value > hi else normal
        return f"Referencia: {norm}\nInterpretación: {text}"

    def cervical_interpretation(self, r):
        if "Profundidad cervical (mm)" not in r: return "Sin clasificación en mm: calibre la imagen con una referencia conocida."
        mm = r["Profundidad cervical (mm)"]; direction = r.get("_cervical_anterior_sign",1)
        if direction < 0: return f"{mm:.2f} mm hacia el lado posterior de la tangente según la orientación seleccionada. Curvatura inversa compatible con patrón cifótico según el esquema aportado; revisar visualmente."
        if mm < 7: return f"{mm:.2f} mm. Profundidad menor a 7 mm: compatible con rectificación / disminución de la curvatura según el protocolo aportado."
        if mm <= 15: return f"{mm:.2f} mm. Dentro del intervalo 7–15 mm mostrado en el protocolo aportado para lordosis cervical."
        return f"{mm:.2f} mm. Profundidad mayor de 15 mm: compatible con curvatura aumentada / hiperlordosis según el protocolo aportado."

    def calculate(self):
        r = self.calculate_values(); self.results_cache = r
        lines = [APP_NAME, f"Caso: {self.case_id.get().strip() or 'sin identificar'}", ""]
        for name in ["SNA","SNB","ANB","SN–PoOr","SN–GoGn","SN–OPT","SN–CVT","OPT–CVT"]:
            if name in r:
                lines.append(f"{name}: {r[name]:.2f}°")
                lines.append("Interpretación: medida descriptiva de la relación entre las tangentes OPT y CVT." if name == "OPT–CVT" else self.interpret(name,r[name])); lines.append("")
            else: lines.append(f"{name}: pendiente (faltan puntos)\n")
        if "Profundidad cervical (px)" in r:
            lines.append(f"Profundidad cervical: {r['Profundidad cervical (px)']:.2f} px")
            if "Profundidad cervical (mm)" in r: lines.append(f"Profundidad cervical: {r['Profundidad cervical (mm)']:.2f} mm")
            lines.append("Interpretación plano vertebral: " + self.cervical_interpretation(r))
        else: lines.append("Plano vertebral: marque C2ps, C7pi y PC para calcular la profundidad cervical.")
        lines += ["", "Nota: resultados para uso educativo y de investigación. Las interpretaciones se realizan respecto a los rangos adoptados en este protocolo y no constituyen diagnóstico clínico."]
        self.results_text.config(state=tk.NORMAL); self.results_text.delete("1.0",tk.END); self.results_text.insert("1.0","\n".join(lines)); self.results_text.config(state=tk.DISABLED); self.status.config(text="Análisis calculado."); self.redraw()

    def save_project(self):
        if not self.original or not self.image_path: messagebox.showinfo("Guardar", "Primero abra una radiografía."); return
        path=filedialog.asksaveasfilename(defaultextension=".yomceph.json", filetypes=[("Proyecto YomCeph","*.yomceph.json"),("JSON","*.json")])
        if not path: return
        data={"version":APP_VERSION,"case_id":self.case_id.get(),"image_path":self.image_path,"points":self.points,"mm_per_pixel":self.mm_per_pixel,"calibration_points":self.calibration_points,"face_direction":self.face_direction.get()}
        with open(path,"w",encoding="utf-8") as f: json.dump(data,f,ensure_ascii=False,indent=2)
        self.status.config(text=f"Proyecto guardado: {os.path.basename(path)}")

    def load_project(self):
        path=filedialog.askopenfilename(filetypes=[("Proyecto YomCeph","*.json"),("Todos","*.*")])
        if not path: return
        try:
            with open(path,"r",encoding="utf-8") as f: d=json.load(f)
            img_path=d["image_path"]; self.original=ImageOps.exif_transpose(Image.open(img_path)).convert("RGB"); self.image_path=img_path
            self.points={k:tuple(v) for k,v in d.get("points",{}).items()}; self.mm_per_pixel=d.get("mm_per_pixel"); self.calibration_points=[tuple(v) for v in d.get("calibration_points",[])]; self.case_id.set(d.get("case_id","")); self.face_direction.set(d.get("face_direction","right"))
            self.cal_label.config(text=(f"Calibrado: {self.mm_per_pixel:.5f} mm/píxel" if self.mm_per_pixel else "Sin calibración")); self.after(50,self.fit_image); self.update_point_guide()
        except Exception as exc: messagebox.showerror("Abrir proyecto",f"No se pudo abrir.\n\n{exc}")

    def export_csv(self):
        if not self.results_cache: self.calculate()
        r=self.results_cache; path=filedialog.asksaveasfilename(defaultextension=".csv",filetypes=[("CSV","*.csv")])
        if not path: return
        headers=["Caso","SNA","SNB","ANB","SN-PoOr","SN-GoGn","SN-OPT","SN-CVT","OPT-CVT","Profundidad cervical mm","Interpretación plano vertebral"]
        values=[self.case_id.get(),r.get("SNA",""),r.get("SNB",""),r.get("ANB",""),r.get("SN–PoOr",""),r.get("SN–GoGn",""),r.get("SN–OPT",""),r.get("SN–CVT",""),r.get("OPT–CVT",""),r.get("Profundidad cervical (mm)",""),self.cervical_interpretation(r)]
        with open(path,"w",newline="",encoding="utf-8-sig") as f: w=csv.writer(f); w.writerow(headers); w.writerow(values)
        self.status.config(text=f"CSV exportado: {os.path.basename(path)}")

    def export_annotated(self):
        if not self.original: return
        path=filedialog.asksaveasfilename(defaultextension=".png",filetypes=[("PNG","*.png")])
        if not path: return
        img=self.original.copy(); draw=ImageDraw.Draw(img); radius=max(3,int(min(img.size)/300))
        for key,p in self.points.items():
            x,y=p; draw.ellipse((x-radius,y-radius,x+radius,y+radius),fill=(0,240,255),outline=(0,0,0)); draw.text((x+radius+2,y-radius-2),key,fill=(255,255,0))
        def dline(a,b,color,width=3):
            if a in self.points and b in self.points: draw.line((self.points[a],self.points[b]),fill=color,width=width)
        dline("S","N",(0,220,255)); dline("Po","Or",(255,220,70)); dline("Go","Gn",(255,100,160)); dline("cv2tg","cv2ip",(100,200,255)); dline("cv2tg","cv4ip",(180,130,255)); dline("C2ps","C7pi",(255,70,70)); img.save(path); self.status.config(text=f"Imagen trazada guardada: {os.path.basename(path)}")

    def draw_vertebral_guide(self):
        c=self.guide_canvas; c.delete("all"); w=max(320,c.winfo_width()); c.create_text(12,10,anchor="nw",text="¿Qué es una tangente?",fill="#0b2b59",font=("Segoe UI",12,"bold"))
        c.create_text(12,36,anchor="nw",width=w-24,text="Es una línea recta de referencia que toca/relaciona puntos del contorno cervical. En este módulo se muestran OPT, CVT y una tangente C2–C7.",fill="#222",font=("Segoe UI",9))
        y0=105; labels=[("Lordosis\n7–15 mm",0),("Rectificación",1),("Cifosis",2),("Hiperlordosis",3)]; boxw=(w-24)/4
        for i,(label,kind) in enumerate(labels):
            x0=12+i*boxw; cx=x0+boxw/2; c.create_line(cx-30,y0,cx-30,y0+210,fill="#ef3b3b",width=2)
            for j,vertebra in enumerate(["C2","C3","C4","C5","C6","C7"]):
                yy=y0+20+j*31; shift=0
                if kind==0: shift=int(15*math.sin(j/5*math.pi))
                elif kind==1: shift=3
                elif kind==2: shift=-int(12*math.sin(j/5*math.pi))
                elif kind==3: shift=int(29*math.sin(j/5*math.pi))
                c.create_rectangle(cx-10+shift,yy,cx+20+shift,yy+20,outline="#1d3557",width=1); c.create_text(cx+5+shift,yy+10,text=vertebra,font=("Segoe UI",7,"bold"))
            c.create_text(cx,y0+225,text=label,fill="#0b2b59",font=("Segoe UI",8,"bold"),justify=tk.CENTER)
        c.create_text(12,y0+270,anchor="nw",width=w-24,text="Para el cálculo: marque C2ps y C7pi para la tangente, y PC en la máxima profundidad de la curva. Calibre la radiografía para obtener milímetros.",fill="#333",font=("Segoe UI",9,"bold"))

if __name__ == "__main__":
    YomCephDesktop().mainloop()
