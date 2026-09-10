import tkinter as tk
from tkinter import ttk

import yomceph_desktop_hidpi as ui
import yomceph_desktop_v09_clean_workflow as v09

APP_VERSION = "0.10.0"

MEASURE_ROWS = [
    ("SNA", "SN con NA (S–N / N–A)", "82° ± 2° (80–84°)",
     "Maxila relativamente retrusiva/retrognática respecto a SN.",
     "Posición sagital maxilar ortognática respecto a SN.",
     "Maxila relativamente protrusiva/prognática respecto a SN."),
    ("SNB", "SN con NB (S–N / N–B)", "80° ± 2° (78–82°)",
     "Mandíbula relativamente retrusiva/retrognática respecto a SN.",
     "Posición sagital mandibular ortognática respecto a SN.",
     "Mandíbula relativamente protrusiva/prognática respecto a SN."),
    ("ANB", "Diferencia SNA–SNB", "2° ± 2° (0–4°)",
     "Relación sagital compatible con Clase III esquelética; revisar SNA y SNB para definir el componente.",
     "Relación sagital compatible con Clase I esquelética.",
     "Relación sagital compatible con Clase II esquelética; revisar SNA y SNB para definir el componente."),
    ("SN–PoOr", "SN con Frankfort (Po–Or)", "7° ± 3° (4–10°) · referencia adoptada",
     "Menor divergencia entre base craneal SN y plano de Frankfort; hallazgo de orientación craneal, no diagnóstico aislado.",
     "Relación SN–Frankfort dentro de la referencia adoptada.",
     "Mayor divergencia entre base craneal SN y plano de Frankfort; hallazgo de orientación craneal, no diagnóstico aislado."),
    ("SN–GoGn", "SN con plano mandibular Go–Gn", "32° ± 5° (27–37°)",
     "Patrón hipodivergente, tendencia de crecimiento horizontal/rotación mandibular anterior.",
     "Patrón normodivergente.",
     "Patrón hiperdivergente, tendencia de crecimiento vertical/rotación mandibular posterior."),
    ("SN–OPT", "SN con tangente OPT", "94–100° · rango actual del protocolo",
     "Ángulo craneocervical reducido: tendencia relativa a flexión de la cabeza respecto a la columna superior; correlacionar con la posición de adquisición.",
     "Relación craneocervical dentro del rango adoptado por el protocolo.",
     "Ángulo craneocervical aumentado: tendencia relativa a extensión de la cabeza respecto a la columna superior; correlacionar con la posición de adquisición."),
    ("SN–CVT", "SN con tangente CVT", "96–102° · rango actual del protocolo",
     "Ángulo craneocervical reducido: tendencia relativa a flexión de la cabeza respecto a la columna cervical.",
     "Relación craneocervical dentro del rango adoptado por el protocolo.",
     "Ángulo craneocervical aumentado: tendencia relativa a extensión de la cabeza respecto a la columna cervical."),
    ("OPT–CVT", "Tangente OPT con tangente CVT", "Sin rango universal automático",
     "Menor divergencia entre OPT y CVT; menor curvatura angular relativa del segmento cervical superior.",
     "Se reporta como variable descriptiva; no se clasifica automáticamente como normal/anormal.",
     "Mayor divergencia entre OPT y CVT; mayor curvatura angular relativa del segmento cervical superior."),
    ("Tangente posterior C2–C7", "Tangente posterior de C2 con tangente posterior de C7", "Sin rango universal automático",
     "Menor diferencia angular entre C2 y C7; configuración cervical más alineada entre ambos extremos.",
     "Se reporta descriptivamente; no existe un umbral pediátrico único configurado.",
     "Mayor diferencia angular entre C2 y C7; mayor cambio de orientación entre los extremos cervicales."),
    ("MGP–OP", "McGregor con plano odontoideo", "96–106° (Rocabado)",
     "<96°: postura craneocervical compatible con extensión de la cabeza.",
     "96–106°: postura craneocervical neutra/funcional según la referencia de Rocabado.",
     ">106°: postura craneocervical compatible con flexión de la cabeza."),
    ("MGP–CVT", "McGregor con CVT", "Sin rango pediátrico único automático",
     "Ángulo más cerrado entre McGregor y CVT; cambio de orientación craneocervical que debe interpretarse junto con otras medidas.",
     "Se reporta como relación angular descriptiva.",
     "Ángulo más abierto entre McGregor y CVT; cambio de orientación craneocervical que debe interpretarse junto con otras medidas."),
    ("U1–NA", "Eje incisivo superior con NA", "22° ± 2° (20–24°)",
     "Incisivo superior retroinclinado/palatinizado respecto a NA.",
     "Inclinación del incisivo superior dentro de la referencia de Steiner.",
     "Incisivo superior proinclinado/vestibularizado respecto a NA."),
    ("L1–NB", "Eje incisivo inferior con NB", "25° ± 2° (23–27°)",
     "Incisivo inferior retroinclinado/lingualizado respecto a NB.",
     "Inclinación del incisivo inferior dentro de la referencia de Steiner.",
     "Incisivo inferior proinclinado/vestibularizado respecto a NB."),
    ("Interincisal U1–L1", "Eje U1 con eje L1", "130° ± 5° · referencia operativa de la app",
     "<125°: ángulo disminuido, compatible con mayor proinclinación dentoalveolar; revisar U1–NA y L1–NB.",
     "125–135°: relación interincisal dentro de la referencia operativa.",
     ">135°: ángulo aumentado, compatible con incisivos relativamente más verticalizados/retroinclinados."),
    ("Powell nasofrontal", "G'–N' con tangente N'–Dn", "115–130°",
     "Transición frente–raíz nasal más aguda; radix relativamente más marcado.",
     "Transición frontonasal armónica según Powell.",
     "Transición frente–raíz nasal más obtusa/abierta; radix relativamente menos definido."),
    ("Powell nasofacial", "Plano facial G'–Pg' con tangente dorsonasal N'–Dn", "30–40°",
     "Proyección nasal relativa disminuida respecto al plano facial.",
     "Proyección nasal armónica respecto al plano facial.",
     "Prominencia/proyección nasal relativa aumentada respecto al plano facial."),
    ("Powell nasomental", "Tangente dorsonasal N'–Dn con línea Prn–Pg'", "120–132°",
     "Relación nariz–mentón más cerrada; revisar conjuntamente proyección nasal y mentoniana.",
     "Balance nariz–mentón armónico según Powell.",
     "Relación nariz–mentón más abierta; revisar conjuntamente proyección nasal y mentoniana."),
    ("Powell mentocervical", "Plano facial G'–Pg' con línea Me'–C", "80–95° · rango configurado en YomCeph",
     "Ángulo cervicomental más cerrado; interpretar con proyección del mentón y tejidos blandos submandibulares.",
     "Relación mentón–cuello dentro del rango configurado.",
     "Ángulo cervicomental más abierto, compatible con menor definición cervicomental; revisar mentón y tejidos blandos."),
    ("Profundidad cervical", "Distancia perpendicular de PC a referencia C2–C7", "7–15 mm · rango actual del protocolo",
     "<7 mm: rectificación/disminución de la lordosis. Si PC cae al lado opuesto de la tangente, valorar inversión/cifosis.",
     "7–15 mm: lordosis cervical dentro del intervalo adoptado.",
     ">15 mm: curvatura aumentada/hiperlordosis según el protocolo adoptado."),
]

LINE_ROWS = [
    ("SN / NSL", "S–N", "Base craneal anterior. Referencia para SNA, SNB, SN–GoGn, SN–OPT, SN–CVT y SN–PoOr."),
    ("NA", "N–A", "Referencia sagital maxilar y referencia dental para U1–NA."),
    ("NB", "N–B", "Referencia sagital mandibular y referencia dental para L1–NB."),
    ("Frankfort / PoOr", "Po–Or", "Plano de Frankfort; se compara con SN."),
    ("Plano mandibular", "Go–Gn", "Referencia vertical mandibular para SN–GoGn."),
    ("OPT", "cv2tg–cv2ip", "Tangente posterior del proceso odontoideo/C2 usada en postura craneocervical."),
    ("CVT", "cv2tg–cv4ip", "Tangente cervical superior usada en postura craneocervical."),
    ("Tangentes posteriores C2–C7", "PS–PI de cada cuerpo vertebral", "La app construye una tangente posterior por vértebra al completar sus dos puntos."),
    ("Referencia de profundidad C2–C7", "C2ps–C7pi", "Línea de referencia sobre la que se calcula la distancia perpendicular de PC."),
    ("McGregor / MGP", "PNS–C0", "Plano palato-suboccipital usado con el plano odontoideo y con CVT."),
    ("Plano odontoideo / OP", "Ops–Opi", "Eje/plano odontoideo de Rocabado. No confundir con OPT."),
    ("Eje U1", "U1a–U1i", "Eje longitudinal del incisivo superior."),
    ("Eje L1", "L1a–L1i", "Eje longitudinal del incisivo inferior."),
    ("G'–N'", "Glabela blanda–Nasion blando", "Componente frontonasal de Powell."),
    ("Tangente dorsonasal", "N'–Dn", "Dirección del dorso nasal para los ángulos de Powell. Prn se mantiene independiente."),
    ("Plano facial de Powell", "G'–Pg'", "Referencia facial para nasofacial y mentocervical."),
    ("Línea nasomental", "Prn–Pg'", "Relaciona punta nasal y mentón blando en el análisis nasomental."),
    ("Línea mentocervical", "Me'–C", "Referencia del contorno mentón–cuello para el ángulo mentocervical."),
]


class VisualHelpYomCeph(v09.CleanWorkflowYomCeph):
    def __init__(self):
        super().__init__()
        self.title("YomCeph Desktop · v0.10 · Ayuda visual")
        self.bind("<F1>", lambda e: self.open_measurement_help())
        self._install_help_menu()
        self.status.config(text="v0.10 · F1 = tabla visual de medidas, normas e interpretación")

    def _install_help_menu(self):
        try:
            menu_name = self.cget("menu")
            menubar = self.nametowidget(menu_name) if menu_name else tk.Menu(self)
        except Exception:
            menubar = tk.Menu(self)
            self.config(menu=menubar)
        help_menu = tk.Menu(menubar, tearoff=False)
        help_menu.add_command(label="Tabla de ángulos, normas e interpretación", command=self.open_measurement_help, accelerator="F1")
        help_menu.add_command(label="Líneas y planos de referencia", command=lambda: self.open_measurement_help(tab=1))
        menubar.add_cascade(label="AYUDA DE MEDICIONES", menu=help_menu)

    def open_measurement_help(self, tab=0):
        win = tk.Toplevel(self)
        win.title("YomCeph · Ayuda visual de mediciones")
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        w, h = min(1500, int(sw * 0.92)), min(850, int(sh * 0.86))
        win.geometry(f"{w}x{h}+{max(0,(sw-w)//2)}+{max(0,(sh-h)//2)}")
        win.minsize(min(900, w), min(560, h))
        win.configure(bg=ui.C["paper"])

        header = tk.Frame(win, bg=ui.C["purple"], height=72)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text="Ayuda visual · mediciones YomCeph", bg=ui.C["purple"], fg="white",
                 font=("Segoe UI Semibold", 18)).pack(anchor="w", padx=18, pady=(10, 0))
        tk.Label(header, text="Valor de referencia + significado clínico cuando el resultado es menor, está en rango o es mayor.",
                 bg=ui.C["purple"], fg=ui.C["lilac_soft"], font=("Segoe UI", 9)).pack(anchor="w", padx=18)

        note = tk.Label(win,
            text=("Importante: los rangos de Steiner, Powell y Rocabado se muestran como referencias cefalométricas. "
                  "SN–OPT, SN–CVT y profundidad cervical usan los rangos actualmente adoptados en este protocolo; "
                  "OPT–CVT, tangente posterior C2–C7 y MGP–CVT se mantienen descriptivos porque YomCeph no les asigna un umbral pediátrico universal. "
                  "NSL/VER, OPT/HOR y CVT/HOR no se calculan automáticamente porque requieren una vertical/horizontal verdadera estandarizada durante la toma radiográfica."),
            bg=ui.C["mint"], fg=ui.C["text"], justify=tk.LEFT, wraplength=max(700, w-60),
            font=("Segoe UI", 9), padx=12, pady=9)
        note.pack(fill=tk.X, padx=12, pady=(10, 6))

        nb = ttk.Notebook(win)
        nb.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 10))
        t1 = ttk.Frame(nb, style="Panel.TFrame", padding=6)
        t2 = ttk.Frame(nb, style="Panel.TFrame", padding=6)
        nb.add(t1, text="Ángulos y mediciones")
        nb.add(t2, text="Líneas y planos")

        cols = ("medida", "construccion", "norma", "bajo", "normal", "alto")
        tree = ttk.Treeview(t1, columns=cols, show="headings", height=20)
        headings = {
            "medida": "Medición", "construccion": "Cómo se forma", "norma": "Norma / referencia",
            "bajo": "Si está por debajo", "normal": "Si está en referencia", "alto": "Si está por encima",
        }
        widths = {"medida":160, "construccion":220, "norma":210, "bajo":370, "normal":310, "alto":370}
        for c in cols:
            tree.heading(c, text=headings[c])
            tree.column(c, width=widths[c], minwidth=120, stretch=False, anchor="w")
        for row in MEASURE_ROWS:
            tree.insert("", tk.END, values=row)
        vs = ttk.Scrollbar(t1, orient="vertical", command=tree.yview)
        hs = ttk.Scrollbar(t1, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vs.set, xscrollcommand=hs.set)
        tree.grid(row=0, column=0, sticky="nsew")
        vs.grid(row=0, column=1, sticky="ns")
        hs.grid(row=1, column=0, sticky="ew")
        t1.rowconfigure(0, weight=1); t1.columnconfigure(0, weight=1)

        lcols = ("linea", "puntos", "uso")
        ltree = ttk.Treeview(t2, columns=lcols, show="headings", height=20)
        ltree.heading("linea", text="Línea / plano")
        ltree.heading("puntos", text="Puntos que la forman")
        ltree.heading("uso", text="Qué representa / para qué se usa")
        ltree.column("linea", width=240, minwidth=160, stretch=False, anchor="w")
        ltree.column("puntos", width=310, minwidth=180, stretch=False, anchor="w")
        ltree.column("uso", width=800, minwidth=300, stretch=True, anchor="w")
        for row in LINE_ROWS:
            ltree.insert("", tk.END, values=row)
        lvs = ttk.Scrollbar(t2, orient="vertical", command=ltree.yview)
        lhs = ttk.Scrollbar(t2, orient="horizontal", command=ltree.xview)
        ltree.configure(yscrollcommand=lvs.set, xscrollcommand=lhs.set)
        ltree.grid(row=0, column=0, sticky="nsew")
        lvs.grid(row=0, column=1, sticky="ns")
        lhs.grid(row=1, column=0, sticky="ew")
        t2.rowconfigure(0, weight=1); t2.columnconfigure(0, weight=1)

        legend = tk.Frame(win, bg=ui.C["lilac_soft"])
        legend.pack(fill=tk.X, padx=12, pady=(0, 10))
        tk.Label(legend, text="✓ Verde = punto colocado    ·    F1 = abrir esta ayuda    ·    Las líneas de trazado siguen ocultas por defecto",
                 bg=ui.C["lilac_soft"], fg=ui.C["purple_dark"], font=("Segoe UI Semibold", 9), pady=7).pack()

        try:
            nb.select(tab)
        except Exception:
            pass
        win.transient(self)
        win.focus_set()


if __name__ == "__main__":
    ui.enable_dpi_awareness()
    app = VisualHelpYomCeph()
    app.mainloop()
