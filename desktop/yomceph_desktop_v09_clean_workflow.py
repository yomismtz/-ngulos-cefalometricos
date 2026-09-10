import math
import tkinter as tk
from tkinter import ttk

import yomceph_desktop as core
import yomceph_desktop_hidpi as ui
import yomceph_desktop_hidpi_guided_tangents as guided
import yomceph_desktop_v06_extended as v06
import yomceph_desktop_v07_powell as v07
import yomceph_desktop_v08_clinical as v08

APP_VERSION = "0.9.0"

# Mantiene la corrección de Powell: Prn es la punta nasal y Dn define la
# dirección/tangencia del dorso. La v0.8 clínica se extiende sin perderla.
DN_POINT = (
    "Dn",
    "Dn · punto de tangencia del dorso nasal",
    "Sobre el dorso nasal marque un segundo punto que, junto con N', represente la dirección de la tangente dorsonasal. No es necesariamente Prn."
)

POINTS = []
_seen = set()
for p in v07.POINTS:
    if p[0] not in _seen:
        POINTS.append(p)
        _seen.add(p[0])
    if p[0] == "Nsoft" and "Dn" not in _seen:
        POINTS.append(DN_POINT)
        _seen.add("Dn")
POINT_ORDER = [p[0] for p in POINTS]
POINT_INFO = {p[0]: (p[1], p[2]) for p in POINTS}
POWELL_SEQUENCE = ["Gsoft", "Nsoft", "Dn", "Prn", "Pgsoft", "Mesoft", "Csoft"]
POWELL_HELP = dict(v07.POWELL_HELP)
POWELL_HELP.update({
    "Gsoft": "PASO 1/7 · POWELL\nMarque G': punto más prominente de la frente blanda.",
    "Nsoft": "PASO 2/7 · POWELL\nMarque N': depresión más profunda de la raíz nasal.",
    "Dn": "PASO 3/7 · TANGENTE DORSONASAL\nMarque un segundo punto sobre el dorso para definir su dirección. N' + Dn forman la tangente; Prn se marcará después.",
    "Prn": "PASO 4/7 · POWELL\nMarque Prn: punto más anterior de la punta nasal. No sustituye a Dn.",
    "Pgsoft": "PASO 5/7 · POWELL\nMarque Pg': punto más anterior del mentón blando.",
    "Mesoft": "PASO 6/7 · POWELL\nMarque Me': punto más inferior del mentón blando.",
    "Csoft": "PASO 7/7 · POWELL\nMarque C: punto más profundo de la unión submandibular-cuello."
})


class CleanWorkflowYomCeph(v08.ClinicalYomCeph):
    def __init__(self):
        # Estas constantes son consultadas por las capas base durante la creación
        # de la interfaz, por eso se propagan antes de llamar a super().__init__().
        v07.POINTS = POINTS
        v07.POINT_ORDER = POINT_ORDER
        v07.POINT_INFO = POINT_INFO
        v07.POWELL_SEQUENCE = POWELL_SEQUENCE
        v07.POWELL_HELP = POWELL_HELP
        v06.POINTS = POINTS
        v06.POINT_ORDER = POINT_ORDER
        v06.POINT_INFO = POINT_INFO
        guided.POINTS = POINTS
        guided.POINT_ORDER = POINT_ORDER
        guided.POINT_INFO = POINT_INFO
        core.POINTS = POINTS
        core.POINT_ORDER = POINT_ORDER
        core.POINT_INFO = POINT_INFO

        # Por defecto se muestran puntos, NO líneas. Las líneas pueden activarse
        # sólo para revisión final desde el menú Ver.
        self._show_traces = False
        super().__init__()
        self.title("YomCeph Desktop · Flujo limpio · v0.9")
        self.status.config(text="v0.9 · Puntos limpios · primer clic = zoom · rueda = acercar/alejar · barras = desplazar")

        self.show_traces_var = tk.BooleanVar(master=self, value=False)
        self._install_view_menu()
        self._install_canvas_scrollbars()
        self.after(120, self._update_scrollbars)

    # ------------------------------------------------------------------
    # Interfaz: trazos ocultos mientras se marcan puntos
    # ------------------------------------------------------------------
    def _install_view_menu(self):
        try:
            menu_name = self.cget("menu")
            menubar = self.nametowidget(menu_name) if menu_name else tk.Menu(self)
        except Exception:
            menubar = tk.Menu(self)
            self.config(menu=menubar)
        view = tk.Menu(menubar, tearoff=False)
        view.add_checkbutton(
            label="Mostrar líneas de trazado (sólo para revisar)",
            variable=self.show_traces_var,
            command=self.toggle_traces,
        )
        view.add_command(label="Ocultar líneas y dejar sólo puntos", command=self.hide_traces)
        view.add_separator()
        view.add_command(label="Ajustar radiografía a la ventana", command=self.fit_image)
        menubar.add_cascade(label="VER", menu=view)

    def toggle_traces(self):
        self._show_traces = bool(self.show_traces_var.get())
        self.redraw()

    def hide_traces(self):
        self._show_traces = False
        if hasattr(self, "show_traces_var"):
            self.show_traces_var.set(False)
        self.redraw()

    def _draw_measurement_lines(self):
        if self._show_traces:
            super()._draw_measurement_lines()

    def _extended_line(self, a_key, b_key, color, label, extent=28, width=3):
        if not self._show_traces:
            return
        # Evita la antigua simplificación N'–Prn como tangente dorsonasal.
        if a_key == "Nsoft" and b_key == "Prn" and "dorso" in label.lower():
            return
        return super()._extended_line(a_key, b_key, color, label, extent, width)

    def redraw(self):
        super().redraw()
        # Si el usuario activó trazos para revisar, añade la tangente dorsonasal
        # corregida N'–Dn. Durante la colocación queda oculta como las demás.
        if self.original and self._show_traces:
            super()._extended_line("Nsoft", "Dn", ui.C["turquoise"], "Tangente dorsonasal", extent=26, width=3)
        self._update_scrollbars()

    # ------------------------------------------------------------------
    # Lista: palomita verde y edición fácil
    # ------------------------------------------------------------------
    def _refresh_point_list_marks(self):
        if not hasattr(self, "point_list"):
            return
        current = self.selected_point.get()
        try:
            self.point_list.delete(0, tk.END)
            selected_index = 0
            for i, (key, title, _) in enumerate(POINTS):
                placed = key in self.points
                mark = "✓" if placed else "○"
                self.point_list.insert(tk.END, f"{mark} {key} · {title}")
                self.point_list.itemconfig(i, foreground=("#238B67" if placed else ui.C["muted"]))
                if key == current:
                    selected_index = i
            self.point_list.selection_set(selected_index)
            self.point_list.see(selected_index)
        except Exception:
            pass

    def update_point_guide(self):
        super().update_point_guide()
        key = self.selected_point.get()
        if hasattr(self, "point_status"):
            if key in self.points:
                self.point_status.config(
                    text="✓ Punto colocado. Para corregirlo, selecciónelo y arrástrelo sobre la radiografía, o haga clic cerca del punto y muévalo.",
                    foreground="#238B67",
                )
            else:
                self.point_status.config(
                    text="○ Punto pendiente. Haga clic aproximadamente sobre el sitio anatómico; el primer clic hará zoom automático para facilitar el ajuste.",
                    foreground=ui.C["muted"],
                )
        self._refresh_point_list_marks()

    def _hit_test_point(self, x, y, radius=13):
        best = None
        best_d = radius
        for key, p in self.points.items():
            cx, cy = self.image_to_canvas(p)
            d = math.hypot(cx - x, cy - y)
            if d <= best_d:
                best = key
                best_d = d
        return best

    def canvas_left_down(self, event):
        if not self.original:
            return

        # Calibración conserva el comportamiento original.
        if self.calibrating:
            return core.YomCephDesktop.canvas_left_down(self, event)

        # En cuanto se vuelve a editar/marcar, se ocultan las líneas para que no
        # tapen anatomía ni dificulten la colocación del siguiente landmark.
        if self._show_traces:
            self.hide_traces()

        # Si se hace clic cerca de una palomita ya colocada, se selecciona ese
        # landmark y puede arrastrarse directamente, aunque otro estuviera activo.
        hit = self._hit_test_point(event.x, event.y)
        if hit:
            try:
                self._select_key(hit)
            except Exception:
                if hit in core.POINT_ORDER:
                    self.select_index(core.POINT_ORDER.index(hit))
            self._dragging_point = True
            self.status.config(text=f"Editando {hit}: mantenga el clic y arrastre hasta la posición correcta.")
            return

        p = self.canvas_to_image(event.x, event.y)
        if p is None:
            return
        key = self.selected_point.get()
        is_first_placement = key not in self.points
        self.points[key] = p
        self._dragging_point = True
        self.update_point_guide()

        if is_first_placement:
            self._auto_zoom_to_point(p)
            self.status.config(text=f"✓ {key} colocado · zoom automático. Ajuste arrastrando si es necesario; la rueda controla el zoom.")
        else:
            self.redraw()
            self.status.config(text=f"{key} recolocado. Puede seguir arrastrando mientras mantenga presionado el botón.")

    def _auto_zoom_to_point(self, image_point):
        if not self.original:
            return
        cw = max(1, self.canvas.winfo_width())
        ch = max(1, self.canvas.winfo_height())
        # Objetivo estable: aproximadamente 2.5 veces el ajuste a ventana. No se
        # acumula indefinidamente con cada punto nuevo.
        fit_scale = min(cw / max(1, self.original.width), ch / max(1, self.original.height))
        target = min(6.0, max(self.scale, fit_scale * 2.5))
        self.scale = max(0.05, target)
        self.offset_x = cw / 2.0 - image_point[0] * self.scale
        self.offset_y = ch / 2.0 - image_point[1] * self.scale
        self._clamp_offsets()
        self.redraw()

    # ------------------------------------------------------------------
    # Zoom y barras horizontal/vertical
    # ------------------------------------------------------------------
    def _install_canvas_scrollbars(self):
        parent = self.canvas.master
        try:
            self.canvas.pack_forget()
        except Exception:
            pass
        parent.rowconfigure(0, weight=1)
        parent.columnconfigure(0, weight=1)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.vscroll = ttk.Scrollbar(parent, orient="vertical", command=self._scroll_y)
        self.hscroll = ttk.Scrollbar(parent, orient="horizontal", command=self._scroll_x)
        self.vscroll.grid(row=0, column=1, sticky="ns")
        self.hscroll.grid(row=1, column=0, sticky="ew")
        corner = ttk.Frame(parent, width=14, height=14, style="Panel.TFrame")
        corner.grid(row=1, column=1, sticky="nsew")

    def _clamp_offsets(self):
        if not self.original or not hasattr(self, "canvas"):
            return
        cw = max(1, self.canvas.winfo_width())
        ch = max(1, self.canvas.winfo_height())
        iw = self.original.width * self.scale
        ih = self.original.height * self.scale
        if iw <= cw:
            self.offset_x = (cw - iw) / 2.0
        else:
            self.offset_x = min(0.0, max(cw - iw, self.offset_x))
        if ih <= ch:
            self.offset_y = (ch - ih) / 2.0
        else:
            self.offset_y = min(0.0, max(ch - ih, self.offset_y))

    def _update_scrollbars(self):
        if not hasattr(self, "hscroll") or not hasattr(self, "vscroll"):
            return
        if not self.original:
            self.hscroll.set(0.0, 1.0)
            self.vscroll.set(0.0, 1.0)
            return
        cw = max(1, self.canvas.winfo_width())
        ch = max(1, self.canvas.winfo_height())
        iw = max(1.0, self.original.width * self.scale)
        ih = max(1.0, self.original.height * self.scale)
        if iw <= cw:
            self.hscroll.set(0.0, 1.0)
        else:
            first = max(0.0, min(1.0, -self.offset_x / iw))
            last = max(first, min(1.0, (cw - self.offset_x) / iw))
            self.hscroll.set(first, last)
        if ih <= ch:
            self.vscroll.set(0.0, 1.0)
        else:
            first = max(0.0, min(1.0, -self.offset_y / ih))
            last = max(first, min(1.0, (ch - self.offset_y) / ih))
            self.vscroll.set(first, last)

    def _scroll_x(self, *args):
        if not self.original:
            return
        cw = max(1, self.canvas.winfo_width())
        iw = self.original.width * self.scale
        if iw <= cw:
            return
        if args[0] == "moveto":
            fraction = float(args[1])
            max_first = max(0.0, 1.0 - cw / iw)
            fraction = max(0.0, min(max_first, fraction))
            self.offset_x = -fraction * iw
        elif args[0] == "scroll":
            amount = int(args[1])
            step = 42 if args[2] == "units" else int(cw * 0.82)
            self.offset_x -= amount * step
        self._clamp_offsets()
        self.redraw()

    def _scroll_y(self, *args):
        if not self.original:
            return
        ch = max(1, self.canvas.winfo_height())
        ih = self.original.height * self.scale
        if ih <= ch:
            return
        if args[0] == "moveto":
            fraction = float(args[1])
            max_first = max(0.0, 1.0 - ch / ih)
            fraction = max(0.0, min(max_first, fraction))
            self.offset_y = -fraction * ih
        elif args[0] == "scroll":
            amount = int(args[1])
            step = 42 if args[2] == "units" else int(ch * 0.82)
            self.offset_y -= amount * step
        self._clamp_offsets()
        self.redraw()

    def pan_move(self, event):
        if not self._pan_last:
            return
        dx = event.x - self._pan_last[0]
        dy = event.y - self._pan_last[1]
        self.offset_x += dx
        self.offset_y += dy
        self._pan_last = (event.x, event.y)
        self._clamp_offsets()
        self.redraw()

    def _zoom_at(self, x, y, factor):
        if not self.original:
            return
        before = self.canvas_to_image(x, y)
        new_scale = max(0.05, min(8.0, self.scale * factor))
        self.scale = new_scale
        if before:
            self.offset_x = x - before[0] * self.scale
            self.offset_y = y - before[1] * self.scale
        self._clamp_offsets()
        self.redraw()

    def zoom(self, event):
        self._zoom_at(event.x, event.y, 1.14 if event.delta > 0 else 1 / 1.14)

    # ------------------------------------------------------------------
    # Powell corregido: elimina cualquier cálculo antiguo que use Prn como Dn
    # ------------------------------------------------------------------
    def calculate_values(self):
        r = super().calculate_values()
        for key in ("Powell Nasofrontal", "Powell Nasofacial", "Powell Nasomental", "Powell Mentocervical"):
            r.pop(key, None)

        if self.require("Gsoft", "Nsoft", "Dn"):
            r["Powell Nasofrontal"] = core.angle3(self.points["Gsoft"], self.points["Nsoft"], self.points["Dn"])
        if self.require("Gsoft", "Pgsoft", "Nsoft", "Dn"):
            raw = core.angle_lines(self.points["Gsoft"], self.points["Pgsoft"], self.points["Nsoft"], self.points["Dn"])
            r["Powell Nasofacial"] = min(raw, 180.0 - raw)
        if self.require("Nsoft", "Dn", "Prn", "Pgsoft"):
            raw = core.angle_lines(self.points["Nsoft"], self.points["Dn"], self.points["Prn"], self.points["Pgsoft"])
            r["Powell Nasomental"] = core.closest_supplement(raw, 126.0)
        if self.require("Gsoft", "Pgsoft", "Mesoft", "Csoft"):
            raw = core.angle_lines(self.points["Gsoft"], self.points["Pgsoft"], self.points["Mesoft"], self.points["Csoft"])
            r["Powell Mentocervical"] = core.closest_supplement(raw, 87.5)
        return r

    # ------------------------------------------------------------------
    # Resultados: sólo aparecen mediciones que realmente tienen un valor
    # ------------------------------------------------------------------
    @staticmethod
    def _finite(value):
        return isinstance(value, (int, float)) and math.isfinite(value)

    def _result_interpretation(self, key, value, r):
        if key in ("SNA", "SNB", "ANB", "SN–PoOr", "SN–GoGn", "SN–OPT", "SN–CVT"):
            return self.interpret(key, value)
        if key == "OPT–CVT":
            return "Interpretación clínica: relación angular entre OPT y CVT que describe la configuración cervical superior. Se reporta como hallazgo postural descriptivo; no asigna por sí sola un diagnóstico patológico."
        if key == "Tangente posterior C2–C7":
            return "Interpretación clínica: relación angular entre las tangentes posteriores de C2 y C7. Se utiliza como descripción de la configuración cervical y debe correlacionarse con el resto del análisis."
        if key == "MGP–OP":
            return "Interpretación clínica: " + self._interpret_mgp_op(value)
        if key == "MGP–CVT":
            return "Interpretación clínica: relación entre el plano de McGregor y CVT; describe la orientación craneocervical. No se aplica un único diagnóstico automático sin una referencia validada para la población estudiada."
        if key == "U1–NA":
            return "Interpretación clínica: " + self._interpret_u1na(value)
        if key == "L1–NB":
            return "Interpretación clínica: " + self._interpret_l1nb(value)
        if key == "Interincisal":
            return "Interpretación clínica: " + self._interpret_interincisal(value)
        if key.startswith("Powell "):
            short = key.replace("Powell ", "")
            diagnosis, explanation = v08.clinical_powell_classify(short, value)
            _, _, norm = v07.POWELL_NORMS[short]
            return f"Norma de Powell: {norm}.\nInterpretación clínica: {diagnosis}. {explanation}"
        return ""

    def calculate(self):
        r = self.calculate_values()
        self.results_cache = r
        lines = []

        order = [
            "SNA", "SNB", "ANB", "SN–PoOr", "SN–GoGn",
            "SN–OPT", "SN–CVT", "OPT–CVT", "Tangente posterior C2–C7",
            "MGP–OP", "MGP–CVT", "U1–NA", "L1–NB", "Interincisal",
            "Powell Nasofrontal", "Powell Nasofacial", "Powell Nasomental", "Powell Mentocervical",
        ]

        for key in order:
            value = r.get(key)
            if not self._finite(value):
                continue
            lines.append(f"{key}: {value:.2f}°")
            interpretation = self._result_interpretation(key, value, r)
            if interpretation:
                lines.append(interpretation)
            lines.append("")

        # No se muestra la profundidad en píxeles como si fuera un análisis.
        # Sólo aparece cuando existe calibración y, por tanto, valor clínico en mm.
        mm = r.get("Profundidad cervical (mm)")
        if self._finite(mm):
            lines.append(f"Profundidad cervical: {mm:.2f} mm")
            lines.append("Interpretación clínica: " + self.cervical_interpretation(r))
            lines.append("")

        if not lines:
            lines = ["Aún no hay mediciones calculables con los puntos colocados."]

        # Resumen sólo si existen valores que lo sustentan; nunca se listan
        # análisis pendientes ni elementos meramente de referencia.
        summary = []
        try:
            sk = self._skeletal_summary(r)
            if sk:
                summary.append("• Esquelético: " + sk)
        except Exception:
            pass
        if self._finite(r.get("SN–GoGn")):
            v = r["SN–GoGn"]
            summary.append("• Vertical: " + ("patrón hipodivergente." if v < 27 else "patrón hiperdivergente." if v > 37 else "patrón normodivergente."))
        if self._finite(r.get("U1–NA")) or self._finite(r.get("L1–NB")):
            dental = []
            if self._finite(r.get("U1–NA")):
                dental.append("incisivo superior retroinclinado" if r["U1–NA"] < 20 else "incisivo superior proinclinado" if r["U1–NA"] > 24 else "incisivo superior en inclinación de referencia")
            if self._finite(r.get("L1–NB")):
                dental.append("incisivo inferior retroinclinado" if r["L1–NB"] < 23 else "incisivo inferior proinclinado" if r["L1–NB"] > 27 else "incisivo inferior en inclinación de referencia")
            summary.append("• Dental: " + "; ".join(dental) + ".")
        if self._finite(r.get("MGP–OP")):
            summary.append("• Craneocervical: " + self._interpret_mgp_op(r["MGP–OP"]))
        if self._finite(mm):
            summary.append("• Curvatura cervical: " + self.cervical_interpretation(r))

        if summary:
            lines += ["RESUMEN CLÍNICO"] + summary

        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete("1.0", tk.END)
        self.results_text.insert("1.0", "\n".join(lines).strip())
        self.results_text.config(state=tk.DISABLED)
        self.status.config(text=f"Análisis calculado: {sum(1 for k in order if self._finite(r.get(k))) + (1 if self._finite(mm) else 0)} mediciones con valor.")
        # Calcular NO vuelve a llenar la radiografía de líneas. Se activan sólo
        # desde VER > Mostrar líneas de trazado si el usuario quiere revisarlas.
        self.hide_traces()


if __name__ == "__main__":
    ui.enable_dpi_awareness()
    app = CleanWorkflowYomCeph()
    app.mainloop()
