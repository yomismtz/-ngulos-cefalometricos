import tkinter as tk

import yomceph_desktop as core
import yomceph_desktop_hidpi as ui
import yomceph_desktop_hidpi_guided_tangents as guided
import yomceph_desktop_v06_extended as v06

APP_VERSION = "0.7.0"

# Análisis de Powell en tejidos blandos.
# Con seis puntos se forman automáticamente los cuatro ángulos clásicos.
POWELL_POINTS = [
    ("Gsoft", "G' · Glabela de tejido blando",
     "Marque el punto más prominente de la frente sobre el perfil de tejidos blandos, en la línea media. Es el extremo superior del plano facial de Powell."),
    ("Nsoft", "N' · Nasion de tejido blando",
     "Marque la concavidad más profunda de la raíz nasal, entre la frente y el dorso de la nariz. No use el Nasion óseo para esta medición."),
    ("Prn", "Prn · Pronasale",
     "Marque el punto más anterior y prominente de la punta de la nariz. Junto con N' define la línea dorsonasal simplificada usada para los ángulos de Powell."),
    ("Pgsoft", "Pg' · Pogonion de tejido blando",
     "Marque el punto más anterior del contorno del mentón blando. Junto con G' forma el plano facial de Powell."),
    ("Mesoft", "Me' · Menton de tejido blando",
     "Marque el punto más inferior del contorno del mentón blando. Se usa para construir la línea mentocervical."),
    ("Csoft", "C · Punto cervical",
     "Marque el punto más profundo de la unión entre el área submandibular y el cuello. Junto con Me' forma la línea mentocervical."),
]

POINTS = list(v06.POINTS) + POWELL_POINTS
POINT_ORDER = [p[0] for p in POINTS]
POINT_INFO = {p[0]: (p[1], p[2]) for p in POINTS}
POWELL_SEQUENCE = ["Gsoft", "Nsoft", "Prn", "Pgsoft", "Mesoft", "Csoft"]

POWELL_HELP = {
    "Gsoft": "PASO 1/6 · POWELL\nMarque G': el punto más prominente de la frente. Después localizaremos N'.",
    "Nsoft": "PASO 2/6 · POWELL\nMarque N': la depresión más profunda de la raíz nasal. Con G' ya queda definida la línea frontonasal.",
    "Prn": "PASO 3/6 · POWELL\nMarque Prn: la punta más anterior de la nariz. Con N' + Prn aparece la línea dorsonasal y ya puede calcularse el ángulo nasofrontal.",
    "Pgsoft": "PASO 4/6 · POWELL\nMarque Pg': el punto más anterior del mentón blando. Con G' + Pg' aparece el plano facial; ya se calculan nasofacial y nasomental.",
    "Mesoft": "PASO 5/6 · POWELL\nMarque Me': el punto más inferior del mentón blando. Falta C para formar la línea mentocervical.",
    "Csoft": "PASO 6/6 · POWELL\nMarque C: el punto más profundo entre región submandibular y cuello. Al colocarlo aparece la línea Me'–C y se calcula el ángulo mentocervical.",
}

POWELL_NORMS = {
    "Nasofrontal": (115.0, 130.0, "115°–130°"),
    "Nasofacial": (30.0, 40.0, "30°–40°"),
    "Nasomental": (120.0, 132.0, "120°–132°"),
    "Mentocervical": (80.0, 95.0, "80°–95°"),
}

POWELL_MEANING = {
    "Nasofrontal": "Relaciona la frente con el dorso nasal y describe la transición frontonasal.",
    "Nasofacial": "Evalúa el balance de la proyección nasal respecto al plano facial G'–Pg'.",
    "Nasomental": "Relaciona la proyección de la nariz con la del mentón; es una medida global nariz–mentón.",
    "Mentocervical": "Describe la relación entre el plano facial y el contorno submandibular/cervical; está influido por proyección del mentón y tejidos blandos del cuello.",
}


def classify(name, value):
    lo, hi, norm = POWELL_NORMS[name]
    if value < lo:
        return "BAJO", f"Por debajo de la norma ({norm}). El ángulo es más agudo que el intervalo de referencia."
    if value > hi:
        return "ALTO", f"Por encima de la norma ({norm}). El ángulo es más abierto/obtuso que el intervalo de referencia."
    return "EN NORMA", f"Dentro del intervalo de referencia ({norm})."


class PowellYomCeph(v06.ExtendedYomCeph):
    def __init__(self):
        # Propaga el catálogo extendido a las clases base antes de crear la interfaz.
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
        self.title("YomCeph Desktop · Investigación · Powell · v0.7")
        self.bind("<F11>", self.toggle_fullscreen)
        self.bind("<F12>", lambda e: self.start_powell_guide())
        self.status.config(text="Listo · F6 OPT/CVT · F7 C2–C7 · F9 McGregor/OP · F10 incisivos · F12 Powell")

    def _install_guided_menu(self):
        menubar = tk.Menu(self)
        guide = tk.Menu(menubar, tearoff=False)
        guide.add_command(label="1. OPT y CVT", command=self.start_opt_guide, accelerator="F6")
        guide.add_command(label="2. Tangentes posteriores C2–C7", command=self.start_posterior_guide, accelerator="F7")
        guide.add_command(label="3. McGregor + plano odontoideo OP", command=self.start_mcgregor_guide, accelerator="F9")
        guide.add_command(label="4. Incisivos e interincisal", command=self.start_dental_guide, accelerator="F10")
        guide.add_command(label="5. Powell · tejidos blandos (6 puntos)", command=self.start_powell_guide, accelerator="F12")
        guide.add_command(label="6. Ir a profundidad cervical (PC)", command=lambda: self._select_key("PC"))
        guide.add_separator()
        guide.add_command(label="Salir del modo guiado", command=self.stop_guide, accelerator="F8")
        menubar.add_cascade(label="TRAZADO GUIADO", menu=guide)
        self.config(menu=menubar)

    def start_powell_guide(self):
        self.guided_mode = "Powell"
        self.guided_sequence = POWELL_SEQUENCE[:]
        self._select_first_missing()
        self.status.config(text="Guía Powell: G' → N' → Prn → Pg' → Me' → C. Las líneas aparecen automáticamente.")
        self.redraw()

    def update_point_guide(self):
        super().update_point_guide()
        key = self.selected_point.get()
        if hasattr(self, "point_desc") and key in POWELL_HELP:
            _, desc = POINT_INFO[key]
            self.point_desc.config(
                text=f"{POWELL_HELP[key]}\n\nDÓNDE MARCAR:\n{desc}\n\n"
                     "Estos son puntos de TEJIDO BLANDO. No los confunda con N, Pg o Me óseos de otros análisis."
            )

    def redraw(self):
        super().redraw()
        if not self.original:
            return
        self._extended_line("Gsoft", "Nsoft", "#D6AD55", "G'–N'", extent=20, width=3)
        self._extended_line("Nsoft", "Prn", "#43B9A8", "Dorso nasal", extent=20, width=3)
        self._extended_line("Gsoft", "Pgsoft", "#6E4A9E", "Plano facial", extent=24, width=3)
        self._extended_line("Prn", "Pgsoft", "#C986D8", "Plano E / nasomental", extent=20, width=3)
        self._extended_line("Mesoft", "Csoft", "#78D7CB", "Línea mentocervical", extent=22, width=3)

    def calculate_values(self):
        r = super().calculate_values()

        # Nasofrontal: G'–N' con N'–Prn, vértice N'.
        if self.require("Gsoft", "Nsoft", "Prn"):
            r["Powell Nasofrontal"] = core.angle3(self.points["Gsoft"], self.points["Nsoft"], self.points["Prn"])

        # Nasofacial: ángulo menor entre plano facial G'–Pg' y dorso N'–Prn.
        if self.require("Gsoft", "Pgsoft", "Nsoft", "Prn"):
            raw = core.angle_lines(self.points["Gsoft"], self.points["Pgsoft"], self.points["Nsoft"], self.points["Prn"])
            r["Powell Nasofacial"] = min(raw, 180.0 - raw)

        # Nasomental: N'–Prn con Prn–Pg', vértice Prn.
        if self.require("Nsoft", "Prn", "Pgsoft"):
            r["Powell Nasomental"] = core.angle3(self.points["Nsoft"], self.points["Prn"], self.points["Pgsoft"])

        # Mentocervical: plano facial G'–Pg' con línea Me'–C; se selecciona
        # el suplemento más cercano al intervalo clásico de Powell.
        if self.require("Gsoft", "Pgsoft", "Mesoft", "Csoft"):
            raw = core.angle_lines(self.points["Gsoft"], self.points["Pgsoft"], self.points["Mesoft"], self.points["Csoft"])
            r["Powell Mentocervical"] = core.closest_supplement(raw, 87.5)
        return r

    def calculate(self):
        super().calculate()
        r = self.results_cache
        extra = ["", "ANÁLISIS DE POWELL · TEJIDOS BLANDOS"]
        mapping = [
            ("Nasofrontal", "Powell Nasofrontal"),
            ("Nasofacial", "Powell Nasofacial"),
            ("Nasomental", "Powell Nasomental"),
            ("Mentocervical", "Powell Mentocervical"),
        ]
        for short, key in mapping:
            lo, hi, norm = POWELL_NORMS[short]
            extra.append("")
            extra.append(f"Ángulo {short}")
            if key not in r:
                extra.append("Resultado: pendiente; faltan puntos de tejido blando. Use F12 para el recorrido guiado.")
                extra.append(f"Norma de Powell: {norm}")
                extra.append("Significado: " + POWELL_MEANING[short])
                continue
            value = r[key]
            state, interpretation = classify(short, value)
            extra.append(f"Resultado: {value:.2f}° · {state}")
            extra.append(f"Norma de Powell: {norm}")
            extra.append("Significado: " + POWELL_MEANING[short])
            extra.append("Interpretación: " + interpretation)
            if short == "Nasomental":
                if value > hi:
                    extra.append("Nota: un aumento puede acompañar una mayor proyección relativa del mentón; nariz y mentón deben valorarse conjuntamente.")
                elif value < lo:
                    extra.append("Nota: la relación nariz–mentón está por debajo del rango; no atribuya el cambio a una sola estructura sin revisar el perfil completo.")
            if short == "Mentocervical":
                if value > hi:
                    extra.append("Nota: un ángulo más abierto puede relacionarse con menor proyección relativa del mentón y/o con el contorno submandibular; confirme visualmente.")
                elif value < lo:
                    extra.append("Nota: el ángulo es más agudo que la norma; puede reflejar mayor definición cervicomental/proyección relativa del mentón.")

        extra += [
            "",
            "Nota metodológica: Powell es un análisis de perfil de TEJIDOS BLANDOS. Sus valores de referencia no deben interpretarse como diagnóstico aislado y pueden variar según edad, sexo y población.",
        ]
        try:
            self.results_text.config(state=tk.NORMAL)
            self.results_text.insert(tk.END, "\n" + "\n".join(extra))
            self.results_text.config(state=tk.DISABLED)
        except Exception:
            pass


if __name__ == "__main__":
    ui.enable_dpi_awareness()
    app = PowellYomCeph()
    app.mainloop()
