import tkinter as tk

import yomceph_desktop as core
import yomceph_desktop_hidpi as ui
import yomceph_desktop_hidpi_guided_tangents as guided
import yomceph_desktop_v06_extended as v06
import yomceph_desktop_v07_powell as v07

APP_VERSION = "0.7.1"

# Punto adicional para representar correctamente la TANGENTE al dorso nasal.
# Prn se conserva separado porque la punta nasal se usa para la línea nasomental.
DN_POINT = (
    "Dn",
    "Dn · punto de tangencia del dorso nasal",
    "Sobre el dorso de la nariz, marque el punto donde una regla apoyada desde N' sigue mejor la dirección general del dorso antes de que éste cambie hacia la punta. No es necesariamente Prn. La app forma la tangente N'–Dn automáticamente."
)

# Inserta Dn después de N' y antes de Prn para un recorrido lógico.
POINTS = []
for p in v07.POINTS:
    POINTS.append(p)
    if p[0] == "Nsoft":
        POINTS.append(DN_POINT)
POINT_ORDER = [p[0] for p in POINTS]
POINT_INFO = {p[0]: (p[1], p[2]) for p in POINTS}
POWELL_SEQUENCE = ["Gsoft", "Nsoft", "Dn", "Prn", "Pgsoft", "Mesoft", "Csoft"]

POWELL_HELP = dict(v07.POWELL_HELP)
POWELL_HELP.update({
    "Gsoft": "PASO 1/7 · POWELL\nMarque G': el punto más prominente de la frente.",
    "Nsoft": "PASO 2/7 · POWELL\nMarque N': la depresión más profunda de la raíz nasal.",
    "Dn": "PASO 3/7 · TANGENTE DORSONASAL\nImagine una regla apoyada en N' que siga la dirección del dorso nasal. Marque un segundo punto Dn sobre ese dorso. Al colocarlo aparece automáticamente la tangente N'–Dn.",
    "Prn": "PASO 4/7 · POWELL\nMarque Prn: el punto más anterior de la punta nasal. Prn NO sustituye a Dn: se usa para la línea nariz–mentón.",
    "Pgsoft": "PASO 5/7 · POWELL\nMarque Pg': el punto más anterior del mentón blando. Se forma el plano facial G'–Pg' y la línea Prn–Pg'.",
    "Mesoft": "PASO 6/7 · POWELL\nMarque Me': el punto más inferior del mentón blando.",
    "Csoft": "PASO 7/7 · POWELL\nMarque C: el punto más profundo de la unión submandibular-cuello. Se forma la línea mentocervical Me'–C.",
})


class AccuratePowellYomCeph(v07.PowellYomCeph):
    def __init__(self):
        # Propaga el catálogo corregido a todas las capas antes de que se construya el UI.
        v07.POINTS = POINTS
        v07.POINT_ORDER = POINT_ORDER
        v07.POINT_INFO = POINT_INFO
        v06.POINTS = POINTS
        v06.POINT_ORDER = POINT_ORDER
        v06.POINT_INFO = POINT_INFO
        guided.POINTS = POINTS
        guided.POINT_ORDER = POINT_ORDER
        guided.POINT_INFO = POINT_INFO
        core.POINTS = POINTS
        core.POINT_ORDER = POINT_ORDER
        core.POINT_INFO = POINT_INFO
        super().__init__()
        self.title("YomCeph Desktop · Investigación · Powell · v0.7.1")
        self.status.config(text="Listo · F6 OPT/CVT · F7 C2–C7 · F9 McGregor/OP · F10 incisivos · F12 Powell")

    def _install_guided_menu(self):
        menubar = tk.Menu(self)
        guide = tk.Menu(menubar, tearoff=False)
        guide.add_command(label="1. OPT y CVT", command=self.start_opt_guide, accelerator="F6")
        guide.add_command(label="2. Tangentes posteriores C2–C7", command=self.start_posterior_guide, accelerator="F7")
        guide.add_command(label="3. McGregor + plano odontoideo OP", command=self.start_mcgregor_guide, accelerator="F9")
        guide.add_command(label="4. Incisivos e interincisal", command=self.start_dental_guide, accelerator="F10")
        guide.add_command(label="5. Powell · tejidos blandos (7 puntos)", command=self.start_powell_guide, accelerator="F12")
        guide.add_command(label="6. Ir a profundidad cervical (PC)", command=lambda: self._select_key("PC"))
        guide.add_separator()
        guide.add_command(label="Salir del modo guiado", command=self.stop_guide, accelerator="F8")
        menubar.add_cascade(label="TRAZADO GUIADO", menu=guide)
        self.config(menu=menubar)

    def start_powell_guide(self):
        self.guided_mode = "Powell"
        self.guided_sequence = POWELL_SEQUENCE[:]
        self._select_first_missing()
        self.status.config(text="Powell: G' → N' → Dn (tangente del dorso) → Prn → Pg' → Me' → C.")
        self.redraw()

    def update_point_guide(self):
        # Usa la actualización genérica de v0.6 para no volver a insertar la ayuda simplificada de v0.7.
        v06.ExtendedYomCeph.update_point_guide(self)
        key = self.selected_point.get()
        if hasattr(self, "point_desc") and key in POWELL_HELP:
            _, desc = POINT_INFO[key]
            self.point_desc.config(
                text=f"{POWELL_HELP[key]}\n\nDÓNDE MARCAR:\n{desc}\n\n"
                     "POWELL = TEJIDOS BLANDOS. G', N', Pg' y Me' son distintos de los puntos óseos. "
                     "La tangente dorsonasal se construye con N' + Dn; Prn es la punta de la nariz."
            )

    def redraw(self):
        # Dibuja todo lo previo (cervical, McGregor e incisivos) pero evita la línea simplificada N'–Prn de v0.7.
        v06.ExtendedYomCeph.redraw(self)
        if not self.original:
            return
        self._extended_line("Gsoft", "Nsoft", "#D6AD55", "G'–N'", extent=20, width=3)
        self._extended_line("Nsoft", "Dn", "#43B9A8", "Tangente dorsonasal", extent=26, width=3)
        self._extended_line("Gsoft", "Pgsoft", "#6E4A9E", "Plano facial", extent=24, width=3)
        self._extended_line("Prn", "Pgsoft", "#C986D8", "Línea nasomental", extent=20, width=3)
        self._extended_line("Mesoft", "Csoft", "#78D7CB", "Línea mentocervical", extent=22, width=3)

    def calculate_values(self):
        r = v06.ExtendedYomCeph.calculate_values(self)
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

    def calculate(self):
        # Conserva resultados de v0.6 (cervicales, McGregor, incisivos) y añade Powell corregido.
        v06.ExtendedYomCeph.calculate(self)
        r = self.results_cache
        extra = ["", "ANÁLISIS DE POWELL · TEJIDOS BLANDOS"]
        mapping = [
            ("Nasofrontal", "Powell Nasofrontal"),
            ("Nasofacial", "Powell Nasofacial"),
            ("Nasomental", "Powell Nasomental"),
            ("Mentocervical", "Powell Mentocervical"),
        ]
        for short, key in mapping:
            _, _, norm = v07.POWELL_NORMS[short]
            extra.append("")
            extra.append(f"Ángulo {short}")
            if key not in r:
                extra += [
                    "Resultado: pendiente; faltan puntos. Use F12 para la guía Powell.",
                    f"Norma de Powell: {norm}",
                    "Significado: " + v07.POWELL_MEANING[short],
                ]
                continue
            value = r[key]
            state, interpretation = v07.classify(short, value)
            extra += [
                f"Resultado: {value:.2f}° · {state}",
                f"Norma de Powell: {norm}",
                "Significado: " + v07.POWELL_MEANING[short],
                "Interpretación: " + interpretation,
            ]
            if short == "Nasomental":
                extra.append("La nariz y el mentón influyen conjuntamente; un valor alto o bajo no debe atribuirse automáticamente a una sola estructura.")
            elif short == "Mentocervical":
                extra.append("La proyección del mentón, el contorno submandibular y los tejidos blandos cervicales pueden modificar este ángulo.")
        extra += [
            "",
            "Técnica: la línea dorsonasal se construye como tangente N'–Dn; Prn se mantiene como punto independiente de la punta nasal para la línea Prn–Pg'.",
            "Nota: los rangos de Powell son referencias de perfil de tejidos blandos y pueden variar con edad, sexo y población.",
        ]
        try:
            self.results_text.config(state=tk.NORMAL)
            self.results_text.insert(tk.END, "\n" + "\n".join(extra))
            self.results_text.config(state=tk.DISABLED)
        except Exception:
            pass


if __name__ == "__main__":
    ui.enable_dpi_awareness()
    app = AccuratePowellYomCeph()
    app.mainloop()
