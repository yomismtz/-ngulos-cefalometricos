import csv
import json
import math
import re
import sqlite3
import statistics
import unicodedata
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import yomceph_desktop_hidpi as ui
import yomceph_desktop_v11_database as v11db
import yomceph_desktop_v116 as v116
import yomceph_desktop_v120 as v120
import yomceph_desktop_v120_final as public_base

APP_VERSION = "0.12.0"
PUBLIC_STEINER_REFERENCES = {"none", "classic"}
INTERNAL_STEINER_REFERENCES = PUBLIC_STEINER_REFERENCES | {"legacy_imported"}

# La interfaz pública no sugiere afiliación con ninguna universidad, escuela,
# clínica, país o investigación concreta.
v120.ANALYSES["steiner"]["summary"] = (
    "Esquelético, vertical, dental y tejidos blandos. Los valores crudos se "
    "conservan siempre; la clasificación automática puede desactivarse o usar "
    "una referencia clásica publicada identificada explícitamente."
)

# Definiciones más reproducibles para los puntos de YEN/W antes de que v0.12
# amplíe el catálogo maestro de landmarks.
for _i, _point in enumerate(list(v120.EXTRA_POINTS)):
    if _point[0] == "M":
        v120.EXTRA_POINTS[_i] = (
            "M",
            "M · centro de la premaxila",
            "Marque el centro del mayor círculo que pueda inscribirse en la región anterior de la maxila y sea tangente a sus límites anterior, superior y palatino según la definición del método YEN/W.",
        )
    elif _point[0] == "G":
        v120.EXTRA_POINTS[_i] = (
            "G",
            "G · centro de la sínfisis mandibular",
            "Marque el centro del mayor círculo que pueda inscribirse en la sínfisis mandibular y sea tangente a sus límites internos anterior, posterior e inferior según la definición del método YEN/W.",
        )


def _spss_base_name(value):
    text = unicodedata.normalize("NFKD", str(value or "var"))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[^A-Za-z0-9_]+", "_", text).strip("_") or "var"
    if text[0].isdigit():
        text = "v_" + text
    return text[:56]


def _unique_spss_names(headers):
    used = set()
    out = []
    for header in headers:
        base = _spss_base_name(header)
        candidate = base
        number = 2
        while candidate.casefold() in used:
            suffix = f"_{number}"
            candidate = base[: 64 - len(suffix)] + suffix
            number += 1
        used.add(candidate.casefold())
        out.append(candidate)
    return out


class YomCephV120Release(public_base.YomCephV120Final):
    """Candidata pública auditada de YomCeph v0.12.

    Reglas de esta capa:
    - ninguna referencia institucional aparece como opción pública;
    - "Sin clasificación" nunca hereda normas ni diagnósticos de versiones previas;
    - una referencia histórica importada puede conservarse internamente sólo para
      reproducibilidad de bases antiguas;
    - las variables de grupo de investigación son cerradas y reproducibles;
    - la exportación conserva datos crudos, denominadores y nombres SPSS únicos.
    """

    # ------------------------------------------------------------------
    # Interfaz compacta: la radiografía conserva la mayor área posible.
    # ------------------------------------------------------------------
    def _install_database_bar(self):
        self._ensure_metadata_vars()
        bar = ttk.Frame(self, padding=(5, 2))
        try:
            bar.pack(fill=tk.X, before=self.body_panes)
        except Exception:
            bar.pack(fill=tk.X)
        self.universal_wrapper = bar

        self.workflow_badge = tk.Label(
            bar,
            text="CASO INDIVIDUAL",
            bg=ui.C["purple_dark"],
            fg="white",
            padx=7,
            pady=2,
            font=("Segoe UI", 8, "bold"),
        )
        self.workflow_badge.pack(side=tk.LEFT, padx=(0, 5))
        self.study_compact_label = ttk.Label(bar, text="Sin investigación", style="Section.TLabel")
        self.study_compact_label.pack(side=tk.LEFT, padx=(0, 6))
        ttk.Label(bar, text="Caso:", style="Muted.TLabel").pack(side=tk.LEFT)
        ttk.Entry(bar, textvariable=self.case_id, width=8).pack(side=tk.LEFT, padx=(3, 5))

        ttk.Button(bar, text="📂 RX", command=self.open_image, style="Purple.TButton").pack(side=tk.LEFT, padx=1)
        ttk.Button(bar, text="📏 Cal.", command=self.start_calibration, style="Turquoise.TButton").pack(side=tk.LEFT, padx=1)
        ttk.Button(bar, text="✓ Calc.", command=self.calculate, style="Gold.TButton").pack(side=tk.LEFT, padx=1)
        ttk.Button(bar, text="💾 Guardar", command=self.save_case_to_database, style="Mint.TButton").pack(side=tk.LEFT, padx=1)
        ttk.Button(bar, text="＋ Caso", command=self.next_case, style="Soft.TButton").pack(side=tk.LEFT, padx=1)

        self.db_counter = ttk.Label(bar, text="", style="Muted.TLabel")
        self.db_counter.pack(side=tk.RIGHT, padx=(5, 3))

        more = ttk.Menubutton(bar, text="Más ▾", style="Soft.TButton")
        menu = tk.Menu(more, tearoff=False)
        menu.add_command(label="Datos del caso", command=self.open_case_data)
        menu.add_command(label="Base de datos", command=self.open_database_browser)
        menu.add_command(label="Exportar investigación", command=self.export_research_package)
        menu.add_command(label="Protocolo de investigación", command=self._open_protocol_from_menu)
        menu.add_separator()
        menu.add_command(label="Mostrar/ocultar puntos", command=self.toggle_left_panel)
        menu.add_command(label="Mostrar/ocultar resultados", command=self.toggle_right_panel)
        more.configure(menu=menu)
        more.pack(side=tk.RIGHT, padx=2)

        self.case_state_frame = tk.Frame(self, bg="#EEF2F6", padx=6, pady=1)
        try:
            self.case_state_frame.pack(fill=tk.X, before=self.body_panes)
        except Exception:
            self.case_state_frame.pack(fill=tk.X)
        self.case_state_label = tk.Label(
            self.case_state_frame,
            text="CASO — · NUEVO",
            bg="#EEF2F6",
            fg="#233044",
            font=("Segoe UI", 8, "bold"),
            anchor="w",
        )
        self.case_state_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.qc_button = ttk.Button(
            self.case_state_frame,
            text="QC",
            command=self.show_quality_control,
            style="Soft.TButton",
        )
        self.qc_button.pack(side=tk.RIGHT)

        # Controles heredados que la capa v0.12 ya no muestra permanentemente.
        self.profile_combo = self.language_combo = self.interface_combo = None
        self.study_row = self.meta1 = self.meta2 = None
        self.open_db_button = self.export_db_button = self.more_info_button = None
        self.high_contrast_check = None

    def _open_protocol_from_menu(self):
        if self.workflow_type == "research" and self.current_study:
            self.open_protocol_editor()
        else:
            messagebox.showinfo(
                "Protocolo",
                "Los protocolos pertenecen a una investigación. Inicie o abra una investigación desde la pantalla inicial.",
            )

    # ------------------------------------------------------------------
    # Base neutral y trazabilidad histórica.
    # ------------------------------------------------------------------
    def _init_database(self):
        super()._init_database()
        with sqlite3.connect(self._db_path) as con:
            # La capa pública anterior neutralizaba el nombre del estudio importado,
            # pero también anulaba su referencia histórica. La recuperamos con un
            # identificador interno neutro para reproducir bases antiguas.
            con.execute(
                """UPDATE research_studies
                   SET steiner_reference='legacy_imported'
                   WHERE name='Investigación importada'
                     AND steiner_reference='none'"""
            )
            con.execute(
                """UPDATE cases
                   SET steiner_reference='legacy_imported'
                   WHERE study_name='Investigación importada'
                     AND workflow_type='research'
                     AND (steiner_reference IS NULL OR steiner_reference='none')"""
            )
            con.commit()

    def _activate_study(self, study_id, close_window=None):
        study = self._get_study(study_id)
        if not study:
            messagebox.showerror("Investigación", "No se pudo abrir el protocolo.")
            return
        if close_window:
            try:
                close_window.destroy()
            except Exception:
                pass
        self.workflow_type = "research"
        self.current_study_id = study_id
        self.current_study = study
        self.selected_measure_keys = [key for key in study["measurements"] if key in v120.MEASUREMENTS]
        ref = study.get("steiner_reference") or "none"
        self.steiner_reference = ref if ref in INTERNAL_STEINER_REFERENCES else "none"
        self.case_group_values = {}
        self.manual_eligibility = "pending"
        self.analysis_mode = "Ambos"
        self.profile_var.set(v116.PROFILE_CUSTOM)
        self.study_name_var.set(study["name"])
        self.study_target_var.set(str(study["target_n"]))
        self.country_var.set(study.get("country") or "")
        self.institution_var.set(study.get("institution") or "")
        self._apply_selected_measurements()
        self._update_compact_context()
        self._update_db_counter()
        self.status.config(text=f"Investigación activa: {study['name']}. Capture los datos del caso.")
        self.open_case_data(first_time=True)

    def load_case_from_database(self, storage_id):
        result = super().load_case_from_database(storage_id)
        if self.steiner_reference not in INTERNAL_STEINER_REFERENCES:
            self.steiner_reference = "none"
        return result

    # ------------------------------------------------------------------
    # Protocolo: grupos únicos y opciones sin duplicados.
    # ------------------------------------------------------------------
    def _save_study(self, data, existing_id=None):
        cleaned = dict(data)
        reserved = {
            "caso", "edad_anos", "edad_meses", "sexo", "codigo_sexo", "genero",
            "pais", "institucion", "fecha_rx", "elegibilidad", "motivo_elegibilidad",
            "centro_origen_importado",
        }
        used = set(reserved)
        normalized = []
        adjusted = False
        for field in data.get("group_fields", []):
            original_name = str(field.get("name", "Grupo")).strip() or "Grupo"
            name = original_name
            key = _spss_base_name(name).casefold()
            suffix = 2
            while key in used:
                name = f"{original_name} {suffix}"
                key = _spss_base_name(name).casefold()
                suffix += 1
                adjusted = True
            used.add(key)
            seen_options = set()
            options = []
            for raw in field.get("options", []):
                option = str(raw).strip()
                if not option:
                    continue
                folded = option.casefold()
                if folded in seen_options:
                    adjusted = True
                    continue
                seen_options.add(folded)
                options.append(option)
            if options:
                normalized.append({"name": name, "options": options})
        cleaned["group_fields"] = normalized
        if adjusted:
            messagebox.showwarning(
                "Variables del estudio",
                "Se detectaron nombres u opciones repetidos. YomCeph los normalizó para evitar columnas ambiguas en la base y en SPSS.",
            )
        return super()._save_study(cleaned, existing_id)

    # ------------------------------------------------------------------
    # Elegibilidad por edad: usa meses cuando están disponibles. Un máximo entero
    # de 15 años incluye todo el año de edad 15 (<16), que es la convención más
    # natural cuando el protocolo se expresa por años cumplidos.
    # ------------------------------------------------------------------
    def _evaluate_eligibility(self):
        if self.workflow_type != "research" or not self.current_study:
            return "not_applicable", "Caso individual"
        try:
            years = int(self.age_years_var.get().strip())
        except Exception:
            return "pending", "Edad pendiente"
        try:
            months = int(self.age_months_var.get().strip() or "0")
        except Exception:
            return "pending", "Meses de edad no válidos"
        if not 0 <= months <= 11:
            return "pending", "Meses de edad fuera de 0–11"

        age = years + months / 12.0
        amin = self.current_study.get("age_min")
        amax = self.current_study.get("age_max")
        if amin is not None and age < float(amin):
            return "not_eligible", f"Edad {years}a {months}m menor que el mínimo de {amin} años"
        if amax is not None:
            max_value = float(amax)
            upper_exclusive = max_value + 1.0 if max_value.is_integer() else max_value
            if age >= upper_exclusive:
                return "not_eligible", f"Edad {years}a {months}m fuera del máximo de {amax} años"
        if self.manual_eligibility == "no":
            return "not_eligible", "No cumple criterios de inclusión/exclusión"
        if self.manual_eligibility == "yes":
            return "eligible", "Cumple rango de edad y criterios confirmados"
        return "pending", "Edad dentro del rango; falta confirmar criterios"

    # ------------------------------------------------------------------
    # Datos del caso: diálogo desplazable y grupos cerrados según protocolo.
    # ------------------------------------------------------------------
    def open_case_data(self, first_time=False):
        win = tk.Toplevel(self)
        win.title("Datos del caso")
        win.transient(self)
        win.grab_set()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        w, h = min(720, int(sw * 0.92)), min(760, int(sh * 0.88))
        win.geometry(f"{w}x{h}+{max(0, (sw-w)//2)}+{max(0, (sh-h)//2)}")

        outer = ttk.Frame(win)
        outer.pack(fill=tk.BOTH, expand=True)
        canvas = tk.Canvas(outer, bg=ui.C["paper"], highlightthickness=0)
        scroll = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        fr = ttk.Frame(canvas, padding=14)
        cid = canvas.create_window((0, 0), window=fr, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        fr.bind("<Configure>", lambda _e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(cid, width=e.width))

        ttk.Label(fr, text="Datos del caso", style="Section.TLabel", font=("Segoe UI Semibold", 16)).pack(anchor="w")
        if self.workflow_type == "research" and self.current_study:
            st = self.current_study
            ttk.Label(
                fr,
                text=f"{st['name']} · rango del protocolo: {st.get('age_min', '—')} a {st.get('age_max', '—')} años",
                style="Muted.TLabel",
            ).pack(anchor="w", pady=(2, 8))
        else:
            ttk.Label(fr, text="Caso individual · no entra en estadísticas de investigación.", style="Muted.TLabel").pack(anchor="w", pady=(2, 8))

        grid = ttk.Frame(fr)
        grid.pack(fill=tk.X)
        for col in (1, 3):
            grid.columnconfigure(col, weight=1)
        ttk.Label(grid, text="Caso / ID:").grid(row=0, column=0, sticky="w", pady=3)
        ttk.Entry(grid, textvariable=self.case_id).grid(row=0, column=1, columnspan=3, sticky="ew", padx=4, pady=3)
        ttk.Label(grid, text="Edad (años):").grid(row=1, column=0, sticky="w", pady=3)
        age_entry = ttk.Entry(grid, textvariable=self.age_years_var, width=8)
        age_entry.grid(row=1, column=1, sticky="w", padx=4, pady=3)
        ttk.Label(grid, text="Meses:").grid(row=1, column=2, sticky="w", pady=3)
        month_entry = ttk.Entry(grid, textvariable=self.age_months_var, width=8)
        month_entry.grid(row=1, column=3, sticky="w", padx=4, pady=3)
        ttk.Label(grid, text="Nacimiento:").grid(row=2, column=0, sticky="w", pady=3)
        ttk.Entry(grid, textvariable=self.birth_date_var).grid(row=2, column=1, sticky="ew", padx=4, pady=3)
        ttk.Label(grid, text="Fecha RX:").grid(row=2, column=2, sticky="w", pady=3)
        ttk.Entry(grid, textvariable=self.radiograph_date_var).grid(row=2, column=3, sticky="ew", padx=4, pady=3)
        ttk.Label(grid, text="Sexo registrado:").grid(row=3, column=0, sticky="w", pady=3)
        sex = ttk.Combobox(grid, state="readonly", values=[self._sex_label(c) for c in v116.SEX_CODES])
        sex.grid(row=3, column=1, sticky="ew", padx=4, pady=3)
        sex.set(self._sex_label(self.sex_code_var.get()))
        ttk.Label(grid, text="Identidad de género (opcional):").grid(row=3, column=2, sticky="w", pady=3)
        ttk.Entry(grid, textvariable=self.gender_identity_var).grid(row=3, column=3, sticky="ew", padx=4, pady=3)

        group_widgets = {}
        if self.workflow_type == "research" and self.current_study:
            gbox = ttk.LabelFrame(fr, text="Procedencia / grupos del estudio", padding=9)
            gbox.pack(fill=tk.X, pady=8)
            for field in self.current_study.get("group_fields", []):
                row = ttk.Frame(gbox)
                row.pack(fill=tk.X, pady=2)
                name = field.get("name", "Grupo")
                ttk.Label(row, text=name + ":", width=22).pack(side=tk.LEFT)
                var = tk.StringVar(value=self.case_group_values.get(name, ""))
                combo = ttk.Combobox(row, textvariable=var, values=field.get("options", []), state="readonly")
                combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
                group_widgets[name] = var

            crit = ttk.LabelFrame(fr, text="Elegibilidad", padding=9)
            crit.pack(fill=tk.X, pady=8)
            ttk.Label(
                crit,
                text="YomCeph valida la edad. Los demás criterios los confirma el investigador.",
                style="Muted.TLabel",
                wraplength=620,
            ).pack(anchor="w")
            elig = tk.StringVar(value=self.manual_eligibility)
            ttk.Radiobutton(crit, text="Cumple criterios de inclusión/exclusión", value="yes", variable=elig).pack(anchor="w")
            ttk.Radiobutton(crit, text="No cumple criterios", value="no", variable=elig).pack(anchor="w")
            ttk.Radiobutton(crit, text="Pendiente de confirmar", value="pending", variable=elig).pack(anchor="w")
        else:
            elig = tk.StringVar(value="pending")

        note = tk.Label(fr, text="", anchor="w", justify=tk.LEFT, padx=8, pady=5)
        note.pack(fill=tk.X, pady=(5, 0))

        def refresh_note(_event=None):
            old = self.manual_eligibility
            self.manual_eligibility = elig.get()
            status, reason = self._evaluate_eligibility()
            self.manual_eligibility = old
            if status == "not_eligible":
                note.config(text="⚠ NO CORRESPONDE A LA INVESTIGACIÓN · " + reason, bg="#FFF3BF", fg="#6A4B00")
            elif status == "eligible":
                note.config(text="✓ Elegible para la investigación · " + reason, bg="#E7F7EE", fg="#17633D")
            else:
                note.config(text="Elegibilidad pendiente · " + reason, bg="#EEF2F6", fg="#344054")

        age_entry.bind("<KeyRelease>", refresh_note)
        month_entry.bind("<KeyRelease>", refresh_note)
        for child in fr.winfo_children():
            pass
        elig.trace_add("write", lambda *_: refresh_note())
        refresh_note()

        def accept():
            self.sex_code_var.set(self._sex_code_from_label(sex.get()))
            self.manual_eligibility = elig.get()
            self.case_group_values = {name: var.get().strip() for name, var in group_widgets.items()}
            status, reason = self._evaluate_eligibility()
            if status == "not_eligible" and self.workflow_type == "research":
                messagebox.showwarning(
                    "Elegibilidad",
                    "Este caso puede conservarse para trazabilidad, pero no entrará en los cálculos de casos incluidos.\n\n" + reason,
                    parent=win,
                )
            win.destroy()
            self._update_compact_context()

        ttk.Button(fr, text="Guardar datos del caso", command=accept, style="Purple.TButton").pack(anchor="e", pady=(8, 0))

    # ------------------------------------------------------------------
    # Referencias Steiner: explícitas y aisladas del protocolo histórico.
    # ------------------------------------------------------------------
    def _protocol_diagnosis(self, key, value):
        unit = self._measurement_unit(key)
        reference = self.steiner_reference or "none"
        if reference == "none":
            return "", "", None, None, None, unit
        if reference == "classic":
            item = v120.CLASSIC_STEINER.get(key)
            if not item:
                return "", "", None, None, None, unit
            mean, sd, unit = item
            lo, hi = mean - sd, mean + sd
            state = "DISMINUIDO" if value < lo else ("AUMENTADO" if value > hi else "EN RANGO")
            diagnosis = f"{state} según la referencia clásica publicada seleccionada."
            return state, diagnosis, value - mean, mean, sd, unit
        if reference == "legacy_imported" and key in v11db.STEINER_PROTOCOL:
            mean, sd, unit, low, normal, high = v11db.STEINER_PROTOCOL[key]
            lo, hi = mean - sd, mean + sd
            if value < lo:
                state, diagnosis = "DISMINUIDO", low
            elif value > hi:
                state, diagnosis = "AUMENTADO", high
            else:
                state, diagnosis = "EN RANGO", normal
            return state, diagnosis, value - mean, mean, sd, unit
        return "", "", None, None, None, unit

    def _classification_for(self, key, value):
        if key in v11db.STEINER_PROTOCOL:
            state, _diagnosis, _diff, norm, _sd, _unit = self._protocol_diagnosis(key, value)
            return state if norm is not None else ""
        return super()._classification_for(key, value)

    def _diagnosis_for_result(self, key, value, results):
        if key in v11db.STEINER_PROTOCOL:
            _state, diagnosis, _diff, norm, _sd, _unit = self._protocol_diagnosis(key, value)
            if norm is None:
                return ""
            if self.steiner_reference == "classic":
                return diagnosis + " No sustituye el diagnóstico clínico."
            return diagnosis
        return super()._diagnosis_for_result(key, value, results)

    def _diagnosis_for(self, key, value):
        if key in v11db.STEINER_PROTOCOL:
            _state, diagnosis, _diff, norm, _sd, _unit = self._protocol_diagnosis(key, value)
            return diagnosis if norm is not None else ""
        return super()._diagnosis_for(key, value)

    def _has_category_rule(self, key):
        if key in ("YEN", "W", "Jarabak ratio") or key in v120.POWELL_RANGES:
            return True
        if key in v11db.STEINER_PROTOCOL:
            if self.steiner_reference == "classic":
                return key in v120.CLASSIC_STEINER
            return self.steiner_reference == "legacy_imported"
        return False

    # ------------------------------------------------------------------
    # Exportación reproducible: datos humanos + CSV SPSS con nombres únicos.
    # ------------------------------------------------------------------
    def export_research_package(self):
        if self.workflow_type != "research" or not self.current_study:
            messagebox.showinfo("Exportar", "Los paquetes estadísticos se generan únicamente para una investigación activa.")
            return
        folder = filedialog.askdirectory(title="Carpeta para exportar la investigación")
        if not folder:
            return

        cases, measure_data = self._research_rows()
        study = self.current_study
        selected = [key for key in study.get("measurements", []) if key in v120.MEASUREMENTS]
        group_names = [field.get("name") for field in study.get("group_fields", []) if field.get("name")]

        parsed = []
        legacy_center_needed = False
        for row in cases:
            cid, local, years, months, sex, sexcode, gender, country, institution, clinic, rx, groups_raw, elig, reason, updated = row
            groups = v120._loads(groups_raw, {})
            if clinic and clinic not in set(groups.values()):
                legacy_center_needed = True
            parsed.append((cid, local, years, months, sex, sexcode, gender, country, institution, clinic, rx, groups, elig, reason, updated))

        headers = [
            "Caso", "Edad_años", "Edad_meses", "Sexo", "Codigo_sexo", "Genero",
            "Pais", "Institucion", "Fecha_RX", "Elegibilidad", "Motivo_elegibilidad",
        ]
        if legacy_center_needed:
            headers.append("Centro_origen_importado")
        headers.extend(group_names)

        category_headers = {}
        for key in selected:
            headers.append(key)
            if self._has_category_rule(key):
                cat_header = key + "__categoria"
                category_headers[key] = cat_header
                headers.append(cat_header)

        matrix = []
        for cid, local, years, months, sex, sexcode, gender, country, institution, clinic, rx, groups, elig, reason, updated in parsed:
            out = [
                local,
                "" if years is None else years,
                "" if months is None else months,
                sex or "",
                sexcode or "",
                gender or "",
                country or "",
                institution or "",
                rx or "",
                elig or "",
                reason or "",
            ]
            if legacy_center_needed:
                out.append(clinic or "")
            out.extend(groups.get(name, "") for name in group_names)
            measures = measure_data.get(cid, {})
            for key in selected:
                value = measures.get(key, ("", ""))[0] if key in measures else ""
                out.append(value)
                if key in category_headers:
                    category = ""
                    if isinstance(value, (int, float)) and math.isfinite(float(value)):
                        category = self._classification_for(key, float(value))
                    out.append(category)
            matrix.append(out)

        spss_names = _unique_spss_names(headers)
        spss_map = dict(zip(headers, spss_names))
        base = v120._safe_id(study["name"])
        csv_path = Path(folder) / f"{base}_datos_SPSS.csv"
        with open(csv_path, "w", newline="", encoding="utf-8-sig") as handle:
            writer = csv.writer(handle)
            writer.writerow(spss_names)
            writer.writerows(matrix)

        xlsx_path = Path(folder) / f"{base}_YomCeph.xlsx"
        self._write_excel_release(xlsx_path, headers, matrix, selected, group_names, category_headers, spss_map)
        sps_path = Path(folder) / f"{base}_importar_SPSS.sps"
        self._write_spss_syntax_release(sps_path, csv_path, headers, spss_map, selected, group_names, category_headers)
        self.status.config(text=f"✓ Investigación exportada: {folder}")
        messagebox.showinfo(
            "Exportar",
            f"Archivos creados:\n{xlsx_path.name}\n{csv_path.name}\n{sps_path.name}\n\nEl CSV usa nombres de variables válidos y únicos para IBM SPSS.",
        )

    def _write_excel_release(self, path, headers, matrix, selected, group_names, category_headers, spss_map):
        from openpyxl import Workbook
        from openpyxl.styles import Font
        from openpyxl.utils import get_column_letter

        wb = Workbook()
        ws = wb.active
        ws.title = "Datos"
        ws.append(headers)
        for cell in ws[1]:
            cell.font = Font(bold=True)
        for row in matrix:
            ws.append(row)
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
        for i, header in enumerate(headers, 1):
            ws.column_dimensions[get_column_letter(i)].width = min(34, max(11, len(str(header)) + 2))

        idx = {header: i for i, header in enumerate(headers)}
        included = [row for row in matrix if row[idx["Elegibilidad"]] == "eligible"]

        desc = wb.create_sheet("Descriptivos")
        desc.append(["Variable", "N válido", "Media", "DE", "Mínimo", "Máximo"])
        for cell in desc[1]:
            cell.font = Font(bold=True)
        for key in selected:
            vals = []
            for row in included:
                value = row[idx[key]]
                if isinstance(value, (int, float)) and math.isfinite(float(value)):
                    vals.append(float(value))
            desc.append([
                key,
                len(vals),
                statistics.mean(vals) if vals else "",
                statistics.stdev(vals) if len(vals) > 1 else "",
                min(vals) if vals else "",
                max(vals) if vals else "",
            ])

        freq = wb.create_sheet("Frecuencias")
        freq.append(["Población", "Variable", "Categoría", "N", "Denominador", "Porcentaje"])
        for cell in freq[1]:
            cell.font = Font(bold=True)
        # Estado de elegibilidad entre todos los registros.
        eligibility_counts = {}
        for row in matrix:
            value = str(row[idx["Elegibilidad"]] or "(vacío)")
            eligibility_counts[value] = eligibility_counts.get(value, 0) + 1
        total_registered = len(matrix)
        for value, n in sorted(eligibility_counts.items()):
            freq.append(["Todos los registrados", "Elegibilidad", value, n, total_registered, (n * 100 / total_registered if total_registered else "")])
        # Sexo y grupos sólo entre los incluidos.
        for header in ["Sexo"] + group_names:
            counts = {}
            for row in included:
                value = str(row[idx[header]] or "(vacío)")
                counts[value] = counts.get(value, 0) + 1
            denominator = len(included)
            for value, n in sorted(counts.items()):
                freq.append(["Casos incluidos", header, value, n, denominator, (n * 100 / denominator if denominator else "")])

        prev = wb.create_sheet("Prevalencias")
        prev.append(["Variable", "Categoría", "N", "N válido categorizado", "Porcentaje", "Nota"])
        for cell in prev[1]:
            cell.font = Font(bold=True)
        for key, cat_header in category_headers.items():
            counts = {}
            for row in included:
                category = str(row[idx[cat_header]] or "").strip()
                if category:
                    counts[category] = counts.get(category, 0) + 1
            denominator = sum(counts.values())
            for category, n in sorted(counts.items()):
                prev.append([
                    key,
                    category,
                    n,
                    denominator,
                    n * 100 / denominator if denominator else "",
                    "Sólo categorías con regla explícita de referencia/protocolo.",
                ])

        dic = wb.create_sheet("Diccionario")
        dic.append(["Variable/columna", "Nombre SPSS", "Etiqueta", "Unidad", "Análisis", "Landmarks", "Tipo"])
        for cell in dic[1]:
            cell.font = Font(bold=True)
        measurement_set = set(selected)
        for header in headers:
            if header in measurement_set:
                spec = v120.MEASUREMENTS[header]
                dic.append([header, spss_map[header], spec.get("label", header), spec.get("unit", ""), spec.get("analysis", ""), ", ".join(spec.get("required", [])), "Medición continua"])
            elif header.endswith("__categoria"):
                dic.append([header, spss_map[header], "Categoría derivada con regla explícita", "", "", "", "Categórica"])
            else:
                dic.append([header, spss_map[header], header, "", "", "", "Metadato/categórica"])

        prot = wb.create_sheet("Protocolo")
        st = self.current_study
        protocol_rows = [
            ("Nombre", st["name"]),
            ("Muestra planeada", st["target_n"]),
            ("Permite aumentar", bool(st["allow_target_increase"])),
            ("Edad mínima", st.get("age_min")),
            ("Edad máxima", st.get("age_max")),
            ("País", st.get("country")),
            ("Institución", st.get("institution")),
            ("Inclusión", st.get("inclusion_criteria")),
            ("Exclusión", st.get("exclusion_criteria")),
            ("Referencia Steiner", "Clásica publicada" if st.get("steiner_reference") == "classic" else ("Referencia histórica importada" if st.get("steiner_reference") == "legacy_imported" else "Sin clasificación automática")),
            ("Versión protocolo", st.get("protocol_version")),
            ("N registrados", len(matrix)),
            ("N incluidos", len(included)),
            ("Análisis", ", ".join(st.get("analyses", []))),
            ("Mediciones", ", ".join(selected)),
        ]
        for row in protocol_rows:
            prot.append([row[0], "" if row[1] is None else row[1]])

        wb.save(path)

    def _write_spss_syntax_release(self, path, csv_path, headers, spss_map, selected, group_names, category_headers):
        numeric_headers = {"Edad_años", "Edad_meses"} | set(selected)
        file_literal = str(csv_path).replace("'", "''")
        lines = [
            "* YomCeph v0.12 - importación reproducible para IBM SPSS.",
            f"GET DATA /TYPE=TXT /FILE='{file_literal}' /ENCODING='UTF8'",
            " /DELCASE=LINE /DELIMITERS=\",\" /QUALIFIER='\"' /ARRANGEMENT=DELIMITED /FIRSTCASE=2",
            " /VARIABLES=",
        ]
        for header in headers:
            name = spss_map[header]
            fmt = "F14.6" if header in numeric_headers else "A255"
            lines.append(f"  {name} {fmt}")
        lines.append(".")
        lines.append("CACHE.")
        lines.append("EXECUTE.")
        lines.append("")
        for header in headers:
            label = str(header).replace("'", "''")
            lines.append(f"VARIABLE LABELS {spss_map[header]} '{label}'.")
        lines.append("")
        elig_name = spss_map["Elegibilidad"]
        lines.append("* Descriptivos y frecuencias de la muestra incluida.")
        lines.append("TEMPORARY.")
        lines.append(f"SELECT IF ({elig_name} = 'eligible').")
        if selected:
            lines.append("DESCRIPTIVES VARIABLES=" + " ".join(spss_map[key] for key in selected) + " /STATISTICS=MEAN STDDEV MIN MAX.")
        freq_headers = ["Sexo"] + group_names + list(category_headers.values())
        if freq_headers:
            lines.append("FREQUENCIES VARIABLES=" + " ".join(spss_map[h] for h in freq_headers if h in spss_map) + ".")
        lines.append("EXECUTE.")
        path.write_text("\n".join(lines), encoding="utf-8-sig")


if __name__ == "__main__":
    ui.enable_dpi_awareness()
    app = YomCephV120Release()
    app.mainloop()
