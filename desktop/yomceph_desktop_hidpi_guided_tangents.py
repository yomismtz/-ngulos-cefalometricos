import math
import tkinter as tk

import yomceph_desktop as core
import yomceph_desktop_hidpi as ui
import yomceph_desktop_hidpi_brand as brand

APP_VERSION = "0.5.0"

# Puntos ordenados para que la construcción de las tangentes sea pedagógica.
POINTS = [
    ("S", "Sella (S)", "Centro geométrico de la silla turca."),
    ("N", "Nasion (N)", "Punto más anterior de la sutura frontonasal."),
    ("A", "Punto A", "Punto más profundo de la concavidad anterior del maxilar."),
    ("B", "Punto B", "Punto más profundo de la concavidad anterior de la sínfisis mandibular."),
    ("Po", "Porion (Po)", "Punto más superior del borde del conducto auditivo externo utilizado para construir Frankfort."),
    ("Or", "Orbitale (Or)", "Punto más inferior del reborde orbitario."),
    ("Go", "Gonion (Go)", "Punto construido en el ángulo mandibular, sobre la bisectriz entre la tangente de la rama y la del borde inferior mandibular."),
    ("Gn", "Gnathion (Gn)", "Punto más anteroinferior del contorno de la sínfisis mandibular."),

    # Solow/Tallgren: OPT y CVT.
    ("cv2ip", "cv2ip · C2 posteroinferior", "Primero localice C2, justo debajo del odontoides. Marque el punto más posterior e inferior del CUERPO de C2. No marque la punta del odontoides. Este punto será el extremo inferior de OPT."),
    ("cv2tg", "cv2tg · contacto de OPT", "Desde cv2ip imagine una regla apoyada sobre el borde posterior del odontoides. Mueva mentalmente esa regla hasta que TOQUE el contorno posterior sin atravesarlo. Marque el punto exacto de contacto. Al tener cv2ip + cv2tg, la app dibuja automáticamente la tangente OPT."),
    ("cv4ip", "cv4ip · C4 posteroinferior", "Identifique el cuerpo de C4 y marque su punto más posterior e inferior. Al tener cv2tg + cv4ip, la app dibuja automáticamente la tangente CVT. No necesita dibujar la línea manualmente."),

    # Tangentes posteriores cervicales guiadas: dos puntos por cuerpo vertebral.
    ("C2ps", "C2 · posterior superior", "Busque el CUERPO de C2. Siga su borde posterior y marque el extremo superior de ese borde. Este es el PRIMER punto de la tangente posterior de C2."),
    ("C2pi", "C2 · posterior inferior", "En el mismo borde posterior del cuerpo de C2, marque el extremo inferior. Al colocar este segundo punto, la app une C2ps–C2pi y aparece la TANGENTE POSTERIOR DE C2."),
    ("C3ps", "C3 · posterior superior", "Localice el cuerpo de C3. Marque la esquina posterior superior de su cuerpo vertebral. Es el primer punto para la tangente de C3."),
    ("C3pi", "C3 · posterior inferior", "Marque la esquina posterior inferior del cuerpo de C3. Al colocarla, aparece automáticamente la tangente posterior de C3."),
    ("C4ps", "C4 · posterior superior", "Localice el cuerpo de C4. Marque la esquina posterior superior. Es el primer punto de la tangente posterior de C4."),
    ("C4pi", "C4 · posterior inferior", "Marque la esquina posterior inferior de C4. Al colocarla, aparece automáticamente la tangente posterior de C4."),
    ("C5ps", "C5 · posterior superior", "Localice el cuerpo de C5. Marque la esquina posterior superior de su borde posterior."),
    ("C5pi", "C5 · posterior inferior", "Marque la esquina posterior inferior de C5. La app dibujará la tangente de C5 al completar los dos puntos."),
    ("C6ps", "C6 · posterior superior", "Localice el cuerpo de C6. Marque la esquina posterior superior de su borde posterior."),
    ("C6pi", "C6 · posterior inferior", "Marque la esquina posterior inferior de C6. La app dibujará la tangente de C6 al completar los dos puntos."),
    ("C7ps", "C7 · posterior superior", "Localice el cuerpo de C7. Marque la esquina posterior superior de su borde posterior."),
    ("C7pi", "C7 · posterior inferior", "Marque la esquina posterior inferior del cuerpo de C7. Al colocarla se completa la sexta tangente posterior. La app puede entonces calcular el ángulo descriptivo entre las tangentes de C2 y C7."),
    ("PC", "PC · máxima profundidad cervical", "Después de formar la línea de referencia C2–C7, marque el punto del contorno cervical que quede a MAYOR distancia perpendicular de esa línea. Use este punto sólo para la medición de profundidad cervical; requiere calibración para expresarse en milímetros."),
]

POINT_ORDER = [p[0] for p in POINTS]
POINT_INFO = {p[0]: (p[1], p[2]) for p in POINTS}

OPT_SEQUENCE = ["cv2ip", "cv2tg", "cv4ip"]
POSTERIOR_SEQUENCE = [
    "C2ps", "C2pi", "C3ps", "C3pi", "C4ps", "C4pi",
    "C5ps", "C5pi", "C6ps", "C6pi", "C7ps", "C7pi",
]
VERTEBRA_PAIRS = [
    ("C2ps", "C2pi", "C2"),
    ("C3ps", "C3pi", "C3"),
    ("C4ps", "C4pi", "C4"),
    ("C5ps", "C5pi", "C5"),
    ("C6ps", "C6pi", "C6"),
    ("C7ps", "C7pi", "C7"),
]

TANGENT_HELP = {
    "cv2ip": "PASO 1/3 · OPT/CVT\nMarque cv2ip. Todavía NO aparece OPT: falta el punto de contacto cv2tg.",
    "cv2tg": "PASO 2/3 · OPT/CVT\nMarque dónde la regla imaginaria que parte de cv2ip toca el borde posterior del odontoides. Al hacer clic, OPT aparecerá automáticamente.",
    "cv4ip": "PASO 3/3 · OPT/CVT\nMarque el punto posteroinferior de C4. Al hacerlo, aparecerá CVT automáticamente.",
}
for i, key in enumerate(POSTERIOR_SEQUENCE):
    vertebra = key[:2]
    if key.endswith("ps"):
        TANGENT_HELP[key] = f"PASO {i+1}/12 · TANGENTES POSTERIORES\n{vertebra}: marque primero el extremo posterior SUPERIOR. Falta un segundo punto para formar su tangente."
    else:
        TANGENT_HELP[key] = f"PASO {i+1}/12 · TANGENTES POSTERIORES\n{vertebra}: marque ahora el extremo posterior INFERIOR. Al hacer clic, la tangente de {vertebra} se dibuja automáticamente."


class GuidedTangentsYomCeph(brand.BrandedYomCeph):
    def __init__(self):
        # La clase base consulta estas constantes durante la creación de la interfaz.
        core.POINTS = POINTS
        core.POINT_ORDER = POINT_ORDER
        core.POINT_INFO = POINT_INFO
        self.guided_mode = None
        self.guided_sequence = []
        super().__init__()
        self.title("YomCeph Desktop · Tangentes guiadas")
        self._install_guided_menu()
        self.bind("<F6>", lambda e: self.start_opt_guide())
        self.bind("<F7>", lambda e: self.start_posterior_guide())
        self.bind("<F8>", lambda e: self.stop_guide())
        self.status.config(text="Listo. F6: guía OPT/CVT · F7: tangentes C2–C7 · F8: salir de guía")

    def _install_guided_menu(self):
        menubar = tk.Menu(self)
        guide = tk.Menu(menubar, tearoff=False)
        guide.add_command(label="1. Guiarme para formar OPT y CVT (3 puntos)", command=self.start_opt_guide, accelerator="F6")
        guide.add_command(label="2. Guiarme para tangentes posteriores C2–C7 (12 puntos)", command=self.start_posterior_guide, accelerator="F7")
        guide.add_command(label="3. Ir a profundidad cervical (PC)", command=lambda: self._select_key("PC"))
        guide.add_separator()
        guide.add_command(label="Salir del modo guiado", command=self.stop_guide, accelerator="F8")
        menubar.add_cascade(label="TRAZADO CERVICAL PASO A PASO", menu=guide)
        self.config(menu=menubar)

    def start_opt_guide(self):
        self.guided_mode = "OPT/CVT"
        self.guided_sequence = OPT_SEQUENCE[:]
        self._select_first_missing()
        self.status.config(text="Guía OPT/CVT activada: coloque 3 puntos; la app dibuja las líneas por usted.")
        self.redraw()

    def start_posterior_guide(self):
        self.guided_mode = "Tangentes C2–C7"
        self.guided_sequence = POSTERIOR_SEQUENCE[:]
        self._select_first_missing()
        self.status.config(text="Guía C2–C7 activada: 2 puntos por vértebra. Cada tangente aparecerá al completar su segundo punto.")
        self.redraw()

    def stop_guide(self):
        self.guided_mode = None
        self.guided_sequence = []
        self.status.config(text="Modo guiado desactivado. Puede seleccionar cualquier punto manualmente.")
        self.redraw()

    def _select_key(self, key):
        if key in core.POINT_ORDER:
            self.select_index(core.POINT_ORDER.index(key))

    def _select_first_missing(self):
        for key in self.guided_sequence:
            if key not in self.points:
                self._select_key(key)
                return
        if self.guided_sequence:
            self._select_key(self.guided_sequence[-1])

    def _advance_guide(self, placed_key):
        if not self.guided_sequence or placed_key not in self.guided_sequence:
            return
        idx = self.guided_sequence.index(placed_key)
        for key in self.guided_sequence[idx + 1:]:
            if key not in self.points:
                self._select_key(key)
                return
        # Si ya están todos, no cambia de punto; muestra estado de finalización.
        if all(k in self.points for k in self.guided_sequence):
            self.status.config(text=f"✓ {self.guided_mode} completado. Las líneas ya están formadas. Puede revisar y luego calcular.")

    def canvas_left_up(self, event):
        placed = self.selected_point.get()
        was_dragging = self._dragging_point
        super().canvas_left_up(event)
        if was_dragging and placed in self.points and self.guided_mode:
            self.after(80, lambda: self._advance_guide(placed))

    def update_point_guide(self):
        super().update_point_guide()
        key = self.selected_point.get()
        if hasattr(self, "point_desc") and key in TANGENT_HELP:
            title, desc = POINT_INFO[key]
            extra = TANGENT_HELP[key]
            self.point_desc.config(text=f"{extra}\n\nDÓNDE MARCAR:\n{desc}\n\n¿QUÉ ES UNA TANGENTE?\nEs una línea recta que sigue la dirección del borde posterior. En esta app usted NO dibuja la línea: coloca los puntos y la línea aparece automáticamente.")
        if hasattr(self, "progress_label"):
            completed = sum(1 for a, b, _ in VERTEBRA_PAIRS if a in self.points and b in self.points)
            self.progress_label.config(text=f"{len(self.points)} / {len(core.POINT_ORDER)} puntos · tangentes C2–C7: {completed}/6")
        self._refresh_point_list_marks()

    def _refresh_point_list_marks(self):
        if not hasattr(self, "point_list"):
            return
        current = self.selected_point.get()
        try:
            self.point_list.delete(0, tk.END)
            selected_index = 0
            for i, (key, title, _) in enumerate(POINTS):
                mark = "✓" if key in self.points else "○"
                self.point_list.insert(tk.END, f"{mark} {key} · {title}")
                if key == current:
                    selected_index = i
            self.point_list.selection_set(selected_index)
            self.point_list.see(selected_index)
        except Exception:
            pass

    def redraw(self):
        super().redraw()
        if not hasattr(self, "canvas"):
            return
        self._draw_extended_tangents()
        self._draw_guide_overlay()

    def _extended_line(self, a_key, b_key, color, label, extent=28, width=3):
        if not self.require(a_key, b_key):
            return
        a = self.image_to_canvas(self.points[a_key])
        b = self.image_to_canvas(self.points[b_key])
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(dx, dy)
        if length < 1:
            return
        ux, uy = dx / length, dy / length
        x1, y1 = a[0] - ux * extent, a[1] - uy * extent
        x2, y2 = b[0] + ux * extent, b[1] + uy * extent
        self.canvas.create_line(x1, y1, x2, y2, fill=color, width=width)
        self.canvas.create_text(x2 + 5, y2, text=label, fill=color, anchor="w", font=("Segoe UI Semibold", 9))

    def _draw_extended_tangents(self):
        if not self.original:
            return
        # OPT y CVT se extienden para que visualmente se entiendan como tangentes y no sólo segmentos.
        self._extended_line("cv2ip", "cv2tg", ui.C["turquoise"], "OPT", extent=36, width=3)
        self._extended_line("cv4ip", "cv2tg", ui.C["purple"], "CVT", extent=36, width=3)
        colors = [ui.C["gold"], "#C986D8", ui.C["turquoise"], "#B896E6", "#74C7B8", "#E2B85E"]
        for (a, b, label), color in zip(VERTEBRA_PAIRS, colors):
            self._extended_line(a, b, color, f"Tangente {label}", extent=20, width=3)

    def _draw_guide_overlay(self):
        if not self.guided_mode or not self.original:
            return
        key = self.selected_point.get()
        text = TANGENT_HELP.get(key, f"Modo guiado: {self.guided_mode}\nColoque el punto {key}.")
        w = min(520, max(330, self.canvas.winfo_width() - 40))
        self.canvas.create_rectangle(14, 14, 14 + w, 96, fill=ui.C["purple_dark"], outline=ui.C["gold"], width=2)
        self.canvas.create_text(28, 26, anchor="nw", width=w - 28, text=text, fill="white", font=("Segoe UI Semibold", 10))

    def _draw_measurement_lines(self):
        # Mantiene trazos craneofaciales y la referencia de profundidad del programa base.
        super()._draw_measurement_lines()

    def calculate_values(self):
        r = super().calculate_values()
        complete = sum(1 for a, b, _ in VERTEBRA_PAIRS if self.require(a, b))
        r["_posterior_tangents_complete"] = complete
        if self.require("C2ps", "C2pi", "C7ps", "C7pi"):
            angle = core.angle_lines(self.points["C2ps"], self.points["C2pi"], self.points["C7ps"], self.points["C7pi"])
            r["Tangente posterior C2–C7"] = min(angle, 180.0 - angle)
        return r

    def calculate(self):
        super().calculate()
        r = self.results_cache
        extra = ["", "TANGENTES POSTERIORES CERVICALES"]
        complete = r.get("_posterior_tangents_complete", 0)
        extra.append(f"Tangentes construidas: {complete}/6")
        if "Tangente posterior C2–C7" in r:
            extra.append(f"Ángulo entre tangentes posteriores C2 y C7: {r['Tangente posterior C2–C7']:.2f}°")
            extra.append("Interpretación: medida angular descriptiva de la relación entre las tangentes posteriores de C2 y C7. No se clasifica automáticamente como normal o anormal.")
        else:
            extra.append("Para calcular C2–C7 complete al menos C2ps, C2pi, C7ps y C7pi. Para ver todo el trazado complete las 6 tangentes.")
        try:
            self.results_text.config(state=tk.NORMAL)
            self.results_text.insert(tk.END, "\n" + "\n".join(extra))
            self.results_text.config(state=tk.DISABLED)
        except Exception:
            pass

    def draw_vertebral_guide(self):
        c = self.guide_canvas
        c.delete("all")
        w, h = max(280, c.winfo_width()), max(330, c.winfo_height())
        c.create_text(14, 12, anchor="nw", text="Cómo formar las tangentes C2–C7", fill=ui.C["purple_dark"], font=("Segoe UI Semibold", 11))
        c.create_text(14, 38, anchor="nw", width=w-28,
                      text="Regla simple: cada vértebra necesita DOS puntos sobre el borde posterior: uno superior (PS) y uno inferior (PI). Al colocar el segundo punto, YomCeph dibuja la tangente automáticamente.",
                      fill=ui.C["muted"], font=("Segoe UI", 9))
        top = 112
        row_h = max(34, (h - top - 55) / 6)
        for i, (_, _, label) in enumerate(VERTEBRA_PAIRS):
            y = top + i * row_h
            x = w * 0.43
            c.create_rectangle(x, y, x + 72, y + 24, fill=ui.C["lilac_soft"], outline=ui.C["turquoise_dark"], width=2)
            px = x - 8
            c.create_oval(px-3, y-2, px+3, y+4, fill=ui.C["gold"], outline="")
            c.create_oval(px-3, y+20, px+3, y+26, fill=ui.C["turquoise"], outline="")
            c.create_line(px, y-13, px, y+37, fill=ui.C["purple"], width=3)
            c.create_text(px-10, y+1, anchor="e", text="PS", fill=ui.C["gold_dark"], font=("Segoe UI Semibold", 8))
            c.create_text(px-10, y+23, anchor="e", text="PI", fill=ui.C["turquoise_dark"], font=("Segoe UI Semibold", 8))
            c.create_text(x+36, y+12, text=label, fill=ui.C["purple_dark"], font=("Segoe UI Semibold", 9))
        c.create_text(14, h-38, anchor="nw", width=w-28,
                      text="OPT/CVT son diferentes: OPT se forma con cv2ip + cv2tg; CVT con cv4ip + cv2tg. Use F6 para que la app lo guíe punto por punto.",
                      fill=ui.C["purple_dark"], font=("Segoe UI Semibold", 8))


if __name__ == "__main__":
    ui.enable_dpi_awareness()
    app = GuidedTangentsYomCeph()
    app.mainloop()
