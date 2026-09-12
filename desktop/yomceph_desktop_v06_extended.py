import math
import tkinter as tk

import yomceph_desktop as core
import yomceph_desktop_hidpi as ui
import yomceph_desktop_hidpi_guided_tangents as guided

APP_VERSION = "0.6.0"

# Extensión: Rocabado/McGregor + medidas dentales.
# IMPORTANTE: OP (plano odontoideo) y OPT (tangente posterior del odontoides)
# son referencias diferentes y se mantienen separadas.
EXTRA_POINTS = [
    ("PNS", "Espina nasal posterior (PNS)",
     "Marque el extremo más posterior del paladar duro: la espina nasal posterior. Este punto será el extremo anterior del plano de McGregor."),
    ("C0", "Base occipital inferior (C0)",
     "Busque la superficie inferior del occipital y marque su punto más inferior, donde se apoya la línea de McGregor. No marque el arco posterior de C1."),
    ("Ops", "Ápice del odontoides (Ops/C2ap)",
     "Localice la apófisis odontoides de C2 y marque su punto más superior (la punta del dens). Es el extremo superior del plano odontoideo OP."),
    ("Opi", "C2 anteroinferior (Opi/C2ia)",
     "Marque el punto más anterior e inferior del cuerpo de C2. Este punto y Ops forman el plano odontoideo OP. No lo confunda con cv2ip, que está en el borde posteroinferior."),
    ("U1a", "Ápice incisivo superior (U1a)",
     "Seleccione el incisivo central superior más nítido. Marque el centro de su ápice radicular. Si el ápice no está formado o no se identifica con claridad, no fuerce el punto."),
    ("U1i", "Borde incisal superior (U1i)",
     "En el mismo incisivo central superior, marque el centro del borde incisal. U1a–U1i forma el eje longitudinal del incisivo superior."),
    ("L1a", "Ápice incisivo inferior (L1a)",
     "Seleccione el incisivo central inferior más nítido. Marque el centro de su ápice radicular. Si el ápice no es identificable, deje la medición pendiente."),
    ("L1i", "Borde incisal inferior (L1i)",
     "En el mismo incisivo central inferior, marque el centro del borde incisal. L1a–L1i forma el eje longitudinal del incisivo inferior."),
]

POINTS = list(guided.POINTS) + EXTRA_POINTS
POINT_ORDER = [p[0] for p in POINTS]
POINT_INFO = {p[0]: (p[1], p[2]) for p in POINTS}

MCGREGOR_SEQUENCE = ["PNS", "C0", "Ops", "Opi"]
DENTAL_SEQUENCE = ["U1a", "U1i", "L1a", "L1i"]

EXTRA_HELP = {
    "PNS": (
        "PASO 1/4 · McGREGOR / ODONTOIDES\n"
        "Localice primero el final posterior del paladar duro. Marque PNS.\n\n"
        "Después marcaremos C0. Cuando existan PNS + C0 aparecerá automáticamente el PLANO DE McGREGOR (MGP)."
    ),
    "C0": (
        "PASO 2/4 · PLANO DE McGREGOR\n"
        "Siga la base del hueso occipital y marque su punto más inferior.\n\n"
        "Al colocar C0, YomCeph unirá PNS–C0 y mostrará MGP. Esa línea NO es CVT ni OPT."
    ),
    "Ops": (
        "PASO 3/4 · PLANO ODONTOIDEO (OP)\n"
        "Busque la punta de la apófisis odontoides de C2 y marque su punto más superior.\n\n"
        "Todavía falta Opi para formar OP."
    ),
    "Opi": (
        "PASO 4/4 · PLANO ODONTOIDEO (OP)\n"
        "Marque el punto ANTERIOR-INFERIOR del cuerpo de C2.\n\n"
        "Al colocar Opi aparecerá OP. Con MGP + OP se calcula el ángulo craneocervical de Rocabado."
    ),
    "U1a": (
        "PASO 1/4 · INCISIVOS\n"
        "Marque el ápice del incisivo central superior más claramente visible. Use el mismo diente para el siguiente punto."
    ),
    "U1i": (
        "PASO 2/4 · INCISIVO SUPERIOR\n"
        "Marque el centro de su borde incisal. Aparecerá el eje U1. Con N y A se calcula U1–NA."
    ),
    "L1a": (
        "PASO 3/4 · INCISIVO INFERIOR\n"
        "Marque el ápice del incisivo central inferior más claramente visible."
    ),
    "L1i": (
        "PASO 4/4 · INCISIVO INFERIOR\n"
        "Marque el centro de su borde incisal. Aparecerá el eje L1. Con N y B se calcula L1–NB; con U1 se calcula el interincisal."
    ),
}


class ExtendedYomCeph(guided.GuidedTangentsYomCeph):
    def __init__(self):
        # La clase v0.5 usa sus constantes durante la creación del UI; las extendemos.
        guided.POINTS = POINTS
        guided.POINT_ORDER = POINT_ORDER
        guided.POINT_INFO = POINT_INFO
        super().__init__()
        self.title("YomCeph Desktop · Investigación · v0.6")
        self.status.config(text="Listo · F6 OPT/CVT · F7 tangentes C2–C7 · F9 McGregor/OP · F10 incisivos")
        self.bind("<F9>", lambda e: self.start_mcgregor_guide())
        self.bind("<F10>", lambda e: self.start_dental_guide())

    def _install_guided_menu(self):
        menubar = tk.Menu(self)
        guide = tk.Menu(menubar, tearoff=False)
        guide.add_command(label="1. Formar OPT y CVT (3 puntos)", command=self.start_opt_guide, accelerator="F6")
        guide.add_command(label="2. Tangentes posteriores C2–C7", command=self.start_posterior_guide, accelerator="F7")
        guide.add_command(label="3. Plano McGregor + plano odontoideo OP", command=self.start_mcgregor_guide, accelerator="F9")
        guide.add_command(label="4. Ejes de incisivos e interincisal", command=self.start_dental_guide, accelerator="F10")
        guide.add_command(label="5. Ir a profundidad cervical (PC)", command=lambda: self._select_key("PC"))
        guide.add_separator()
        guide.add_command(label="Salir del modo guiado", command=self.stop_guide, accelerator="F8")
        menubar.add_cascade(label="TRAZADO GUIADO", menu=guide)
        self.config(menu=menubar)

    def start_mcgregor_guide(self):
        self.guided_mode = "McGregor + OP"
        self.guided_sequence = MCGREGOR_SEQUENCE[:]
        self._select_first_missing()
        self.status.config(text="Guía McGregor/OP: PNS → C0 → ápice del odontoides → C2 anteroinferior.")
        self.redraw()

    def start_dental_guide(self):
        self.guided_mode = "Incisivos"
        self.guided_sequence = DENTAL_SEQUENCE[:]
        self._select_first_missing()
        self.status.config(text="Guía dental: marque ápice y borde incisal del superior; después del inferior.")
        self.redraw()

    def update_point_guide(self):
        super().update_point_guide()
        key = self.selected_point.get()
        if hasattr(self, "point_desc") and key in EXTRA_HELP:
            title, desc = POINT_INFO[key]
            self.point_desc.config(
                text=f"{EXTRA_HELP[key]}\n\nDÓNDE MARCAR:\n{desc}\n\n"
                     "RECUERDE: OP y OPT NO son la misma línea. OP usa el ápice del odontoides y C2 anteroinferior; "
                     "OPT es la tangente posterior del odontoides y usa cv2tg + cv2ip."
            )

    def redraw(self):
        super().redraw()
        if not self.original:
            return
        self._extended_line("PNS", "C0", ui.C["gold"], "MGP · McGregor", extent=28, width=3)
        self._extended_line("Ops", "Opi", "#E18ACB", "OP · plano odontoideo", extent=25, width=3)
        self._extended_line("U1a", "U1i", "#74D8C8", "Eje U1", extent=18, width=3)
        self._extended_line("L1a", "L1i", "#C79AE8", "Eje L1", extent=18, width=3)

    @staticmethod
    def _acute_line_angle(value):
        return min(value, 180.0 - value)

    def calculate_values(self):
        r = super().calculate_values()

        # Rocabado: McGregor (PNS-C0) / plano odontoideo OP (Ops-Opi).
        if self.require("PNS", "C0", "Ops", "Opi"):
            raw = core.angle_lines(self.points["PNS"], self.points["C0"], self.points["Ops"], self.points["Opi"])
            r["MGP–OP"] = core.closest_supplement(raw, 101.0)

        # McGregor respecto de CVT: se conserva como variable descriptiva porque
        # no se adopta aquí un único rango pediátrico universal.
        if self.require("PNS", "C0", "cv2tg", "cv4ip"):
            raw = core.angle_lines(self.points["PNS"], self.points["C0"], self.points["cv2tg"], self.points["cv4ip"])
            r["MGP–CVT"] = core.closest_supplement(raw, 90.0)

        # Steiner dental.
        if self.require("U1a", "U1i", "N", "A"):
            raw = core.angle_lines(self.points["U1a"], self.points["U1i"], self.points["N"], self.points["A"])
            r["U1–NA"] = self._acute_line_angle(raw)
        if self.require("L1a", "L1i", "N", "B"):
            raw = core.angle_lines(self.points["L1a"], self.points["L1i"], self.points["N"], self.points["B"])
            r["L1–NB"] = self._acute_line_angle(raw)
        if self.require("U1a", "U1i", "L1a", "L1i"):
            raw = core.angle_lines(self.points["U1a"], self.points["U1i"], self.points["L1a"], self.points["L1i"])
            acute = self._acute_line_angle(raw)
            r["Interincisal"] = 180.0 - acute
        return r

    def _interpret_mgp_op(self, value):
        if value < 96:
            return "Por debajo de 96°: patrón compatible con extensión de la cabeza respecto a la columna cervical superior según la referencia de Rocabado."
        if value > 106:
            return "Por encima de 106°: patrón compatible con flexión de la cabeza respecto a la columna cervical superior según la referencia de Rocabado."
        return "Entre 96° y 106°: dentro del intervalo de referencia de Rocabado para el ángulo craneocervical."

    def _interpret_u1na(self, value):
        if value < 20:
            return "Valor menor que 20°: incisivo superior relativamente retroinclinado respecto a NA."
        if value > 24:
            return "Valor mayor que 24°: incisivo superior relativamente proinclinado respecto a NA."
        return "Dentro de la referencia de Steiner 22° ± 2°."

    def _interpret_l1nb(self, value):
        if value < 23:
            return "Valor menor que 23°: incisivo inferior relativamente retroinclinado respecto a NB."
        if value > 27:
            return "Valor mayor que 27°: incisivo inferior relativamente proinclinado respecto a NB."
        return "Dentro de la referencia de Steiner 25° ± 2°."

    def _interpret_interincisal(self, value):
        if value > 135:
            return "Mayor de 135°: relación interincisal compatible con incisivos relativamente retroinclinados."
        if value < 125:
            return "Menor de 125°: relación interincisal compatible con incisivos relativamente proinclinados."
        return "Dentro de la referencia convencional aproximada de 130° ± 5°."

    def calculate(self):
        super().calculate()
        r = self.results_cache
        extra = ["", "McGREGOR / ODONTOIDES"]
        if "MGP–OP" in r:
            extra += [
                f"MGP–OP (ángulo craneocervical): {r['MGP–OP']:.2f}°",
                "Referencia: 96°–106°.",
                "Interpretación: " + self._interpret_mgp_op(r["MGP–OP"]),
            ]
        else:
            extra.append("MGP–OP: pendiente. Marque PNS, C0, Ops y Opi (F9).")

        if "MGP–CVT" in r:
            extra += [
                f"MGP–CVT: {r['MGP–CVT']:.2f}°",
                "Interpretación: relación angular descriptiva entre el plano de McGregor y CVT. No se aplica un rango pediátrico universal automático.",
            ]
        else:
            extra.append("MGP–CVT: pendiente. Requiere McGregor (PNS–C0) y CVT (cv2tg–cv4ip).")

        extra += ["", "MEDIDAS DENTALES"]
        if "U1–NA" in r:
            extra += [f"U1–NA: {r['U1–NA']:.2f}°", "Referencia: Steiner 22° ± 2°.", "Interpretación: " + self._interpret_u1na(r["U1–NA"])]
        else:
            extra.append("U1–NA: pendiente. Requiere U1a, U1i, N y A.")
        if "L1–NB" in r:
            extra += [f"L1–NB: {r['L1–NB']:.2f}°", "Referencia: Steiner 25° ± 2°.", "Interpretación: " + self._interpret_l1nb(r["L1–NB"])]
        else:
            extra.append("L1–NB: pendiente. Requiere L1a, L1i, N y B.")
        if "Interincisal" in r:
            extra += [f"Ángulo interincisal: {r['Interincisal']:.2f}°", "Referencia convencional: 130° ± 5°.", "Interpretación: " + self._interpret_interincisal(r["Interincisal"])]
        else:
            extra.append("Interincisal: pendiente. Requiere los ejes completos U1 y L1.")

        extra += [
            "",
            "Nota pediátrica: las referencias dentales convencionales deben interpretarse con cautela durante dentición mixta o con raíces en desarrollo. "
            "La app permite medirlas, pero pueden excluirse del análisis estadístico principal si así lo define el protocolo.",
            "",
            "Diferencia clave: OP = plano odontoideo anterior (Ops–Opi). OPT = tangente posterior del odontoides (cv2tg–cv2ip). "
            "OPT–CVT ya se calcula en el módulo cervical.",
        ]
        try:
            self.results_text.config(state=tk.NORMAL)
            self.results_text.insert(tk.END, "\n" + "\n".join(extra))
            self.results_text.config(state=tk.DISABLED)
        except Exception:
            pass


if __name__ == "__main__":
    ui.enable_dpi_awareness()
    app = ExtendedYomCeph()
    app.mainloop()
