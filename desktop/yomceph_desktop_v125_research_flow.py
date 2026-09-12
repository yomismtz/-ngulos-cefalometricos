"""YomCeph Desktop v0.12.5: investigación primero, elegibilidad al finalizar.

El protocolo se activa sin abrir una ficha de paciente. El investigador abre la
radiografía, intenta el trazado y sólo al finalizar registra los metadatos y la
decisión de inclusión. YomCeph deriva exclusiones objetivas de edad, país,
landmarks requeridos y calibración, y permite registrar causas radiográficas
adicionales. Los casos excluidos se conservan para trazabilidad y no cuentan
como incluidos.
"""

from __future__ import annotations

import json
import re
import sqlite3
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk

import yomceph_desktop_v116 as v116
import yomceph_desktop_v120 as v120
import yomceph_desktop_v124_final as v124final
import yomceph_desktop_v124_personalization as v124personal
from yomceph_scientific_catalog import MEASUREMENTS, required_landmarks
from yomceph_v125_extended_analyses import extended_values, install_catalog_extensions

APP_VERSION = "0.12.5"
v124final.APP_VERSION = APP_VERSION
v124personal.APP_VERSION = APP_VERSION

AUTO_START = "[YomCeph · criterios automáticos]"
AUTO_END = "[fin criterios automáticos]"

DEFAULT_EXCLUSION_REASONS = (
    "Calidad radiográfica insuficiente para el análisis seleccionado",
    "No es posible identificar con seguridad todos los landmarks requeridos",
    "Anatomía relevante recortada o fuera del campo radiográfico",
    "Artefactos o superposición impiden una medición reproducible",
    "Proyección o posicionamiento radiográfico inadecuado",
    "Registro duplicado o radiografía no correspondiente al caso",
)


def _clean_text(value):
    return str(value or "").strip()


def _age_label(age_min, age_max):
    if age_min is None and age_max is None:
        return "sin restricción de edad predefinida"
    if age_min is None:
        return f"hasta {age_max} años"
    if age_max is None:
        return f"desde {age_min} años"
    return f"de {age_min} a {age_max} años cumplidos"


def automatic_protocol_criteria(age_min=None, age_max=None, country=""):
    """Textos de protocolo derivados de edad/país, sin borrar criterios propios."""
    age_text = _age_label(age_min, age_max)
    country = _clean_text(country)
    place = f"; procedencia/país del protocolo: {country}" if country else ""
    inclusion = (
        f"{AUTO_START}\n"
        f"• Edad {age_text}{place}.\n"
        "• Radiografía compatible con los análisis seleccionados y con anatomía suficiente para intentar el trazado.\n"
        "• Landmarks requeridos identificables y, cuando existan mediciones lineales, calibración disponible.\n"
        f"{AUTO_END}"
    )
    exclusion = (
        f"{AUTO_START}\n"
        "• Edad fuera del rango definido por el protocolo.\n"
        + (f"• País/procedencia distinto de {country}.\n" if country else "")
        + "• Calidad radiográfica insuficiente, proyección/posicionamiento inadecuado, anatomía recortada o artefactos que impidan el análisis.\n"
        "• Imposibilidad de identificar con seguridad todos los landmarks requeridos.\n"
        "• Ausencia de calibración cuando el protocolo requiere resultados lineales en milímetros.\n"
        f"{AUTO_END}"
    )
    return inclusion, exclusion


def merge_automatic_criteria(existing, automatic):
    """Reemplaza sólo el bloque automático y conserva el texto escrito por el usuario."""
    text = _clean_text(existing)
    pattern = re.compile(
        re.escape(AUTO_START) + r".*?" + re.escape(AUTO_END),
        flags=re.DOTALL,
    )
    custom = pattern.sub("", text).strip()
    return automatic if not custom else automatic + "\n\nCriterios adicionales del investigador:\n" + custom


def research_case_decision(
    study,
    age_years,
    age_months,
    case_country,
    required_points,
    placed_points,
    manual_reasons=(),
    linear_calibration_required=False,
    calibrated=True,
):
    """Pure decision helper used by UI and tests."""
    exclusion = []
    pending = []

    try:
        years = int(str(age_years).strip())
    except Exception:
        years = None
    try:
        months = int(str(age_months or "0").strip())
    except Exception:
        months = None

    if years is None or months is None or months < 0 or months > 11:
        pending.append("Edad incompleta o no válida")
    else:
        age = years + months / 12.0
        amin = study.get("age_min")
        amax = study.get("age_max")
        if amin is not None and age < float(amin):
            exclusion.append(f"Edad {years}a {months}m menor que el mínimo de {amin} años")
        if amax is not None:
            max_value = float(amax)
            upper_exclusive = max_value + 1.0 if max_value.is_integer() else max_value
            if age >= upper_exclusive:
                exclusion.append(f"Edad {years}a {months}m fuera del máximo de {amax} años")

    expected_country = _clean_text(study.get("country"))
    observed_country = _clean_text(case_country)
    if expected_country:
        if not observed_country:
            pending.append("País/procedencia pendiente")
        elif observed_country.casefold() != expected_country.casefold():
            exclusion.append(
                f"País/procedencia '{observed_country}' distinto del definido en el protocolo: {expected_country}"
            )

    required = [str(key) for key in required_points]
    placed = {str(key) for key in placed_points}
    missing = [key for key in required if key not in placed]
    if missing:
        preview = ", ".join(missing[:8])
        if len(missing) > 8:
            preview += f" y {len(missing) - 8} más"
        exclusion.append(f"Landmarks requeridos no identificados: {preview}")

    if linear_calibration_required and not calibrated:
        exclusion.append("Falta calibración para las mediciones lineales seleccionadas")

    for reason in manual_reasons or ():
        reason = _clean_text(reason)
        if reason and reason not in exclusion:
            exclusion.append(reason)

    if exclusion:
        return "not_eligible", exclusion, pending
    if pending:
        return "pending", [], pending
    return "eligible", [], []


class YomCephV125ResearchFlow(v124final.YomCephV124Final):
    def __init__(self):
        install_catalog_extensions()
        self.case_exclusion_reasons = []
        self.case_exclusion_other = ""
        self._v125_suppress_first_case_dialog = False
        self._v125_finalize_in_progress = False
        self._v125_last_decision_reasons = []
        super().__init__()
        self.title(f"YomCeph Desktop · v{APP_VERSION}")

    def _apply_language(self):
        try:
            self.title(f"YomCeph Desktop · v{APP_VERSION}")
        except tk.TclError:
            pass

    def _init_database(self):
        super()._init_database()
        with sqlite3.connect(self._db_path) as con:
            columns = {row[1] for row in con.execute("PRAGMA table_info(cases)")}
            if "eligibility_reasons_json" not in columns:
                con.execute("ALTER TABLE cases ADD COLUMN eligibility_reasons_json TEXT")
            if "eligibility_decided_at" not in columns:
                con.execute("ALTER TABLE cases ADD COLUMN eligibility_decided_at TEXT")
            con.commit()

    def _install_database_bar(self):
        super()._install_database_bar()
        self.primary_save_button = None
        for child in self.universal_wrapper.winfo_children():
            if not isinstance(child, ttk.Button):
                continue
            try:
                if str(child.cget("text")) == "💾 Guardar":
                    self.primary_save_button = child
                    break
            except tk.TclError:
                continue
        self._v125_update_save_label()

    def _v125_update_save_label(self):
        if getattr(self, "primary_save_button", None) is None:
            return
        try:
            self.primary_save_button.configure(
                text="✓ Finalizar" if self.workflow_type == "research" else "💾 Guardar"
            )
        except tk.TclError:
            pass

    def _update_compact_context(self):
        result = super()._update_compact_context()
        self._v125_update_save_label()
        return result

    def _case_snapshot(self):
        snap = super()._case_snapshot()
        snap["exclusion_reasons"] = tuple(sorted(_clean_text(x) for x in getattr(self, "case_exclusion_reasons", []) if _clean_text(x)))
        snap["exclusion_other"] = _clean_text(getattr(self, "case_exclusion_other", ""))
        return snap

    def _activate_study(self, study_id, close_window=None):
        # Reutiliza toda la activación neutral/auditada, pero suprime exclusivamente
        # el popup automático de datos. La radiografía y el trazado van primero.
        self._v125_suppress_first_case_dialog = True
        try:
            result = super()._activate_study(study_id, close_window=close_window)
        finally:
            self._v125_suppress_first_case_dialog = False
        self.case_exclusion_reasons = []
        self.case_exclusion_other = ""
        if self.current_study:
            self.status.config(
                text=(
                    f"Investigación activa: {self.current_study['name']}. "
                    "Abra la radiografía, realice el trazado y use ✓ Finalizar al terminar."
                )
            )
        self._v125_update_save_label()
        return result

    def open_case_data(self, first_time=False):
        if first_time and self._v125_suppress_first_case_dialog:
            return None
        return super().open_case_data(first_time=first_time)

    def next_case(self):
        self._v125_suppress_first_case_dialog = True
        try:
            result = super().next_case()
        finally:
            self._v125_suppress_first_case_dialog = False
        if result is False:
            return False
        self.case_exclusion_reasons = []
        self.case_exclusion_other = ""
        if self.workflow_type == "research":
            self.status.config(
                text="Nuevo caso de investigación. Abra la radiografía y trace antes de registrar la elegibilidad."
            )
        self._v125_update_save_label()
        return result

    def new_case(self):
        result = super().new_case()
        self.case_exclusion_reasons = []
        self.case_exclusion_other = ""
        return result

    def _save_study(self, data, existing_id=None):
        cleaned = dict(data)
        auto_inclusion, auto_exclusion = automatic_protocol_criteria(
            cleaned.get("age_min"), cleaned.get("age_max"), cleaned.get("country", "")
        )
        cleaned["inclusion"] = merge_automatic_criteria(cleaned.get("inclusion", ""), auto_inclusion)
        cleaned["exclusion"] = merge_automatic_criteria(cleaned.get("exclusion", ""), auto_exclusion)
        return super()._save_study(cleaned, existing_id=existing_id)

    def calculate_values(self):
        values = super().calculate_values()
        values.update(extended_values(self.points, getattr(self, "mm_per_pixel", None)))
        return values

    def _linear_calibration_required(self):
        return any(
            MEASUREMENTS.get(key, {}).get("unit") == "mm"
            for key in (self.selected_measure_keys or [])
        )

    def _decision(self, manual_reasons=None):
        if self.workflow_type != "research" or not self.current_study:
            return "not_applicable", [], []
        required = required_landmarks(self.selected_measure_keys)
        reasons = list(self.case_exclusion_reasons if manual_reasons is None else manual_reasons)
        other = _clean_text(self.case_exclusion_other)
        if other:
            reasons.append("Otro: " + other)
        return research_case_decision(
            self.current_study,
            self.age_years_var.get(),
            self.age_months_var.get(),
            self.country_var.get(),
            required,
            self.points.keys(),
            reasons,
            linear_calibration_required=self._linear_calibration_required(),
            calibrated=bool(getattr(self, "mm_per_pixel", None) and self.mm_per_pixel > 0),
        )

    def _evaluate_eligibility(self):
        if self.workflow_type != "research" or not self.current_study:
            return "not_applicable", "Caso individual"
        status, exclusions, pending = self._decision()
        if self.manual_eligibility == "no" and not exclusions:
            exclusions = ["Caso excluido por decisión documentada del investigador"]
            status = "not_eligible"
        elif self.manual_eligibility == "pending" and status == "eligible":
            # Durante el trazado no se declara incluido todavía. El diálogo de
            # finalización cambia este valor a yes sólo tras la revisión final.
            status = "pending"
            pending = ["Pendiente de finalizar el caso"]
        if status == "not_eligible":
            reason = "; ".join(exclusions)
            self._v125_last_decision_reasons = exclusions
            return status, reason
        if status == "pending":
            return status, "; ".join(pending) or "Elegibilidad pendiente"
        self._v125_last_decision_reasons = []
        return "eligible", "Cumple los criterios automáticos y no tiene causas de exclusión registradas"

    def _next_research_id(self):
        if not self.current_study_id:
            return ""
        try:
            with sqlite3.connect(self._db_path) as con:
                rows = con.execute(
                    "SELECT local_case_id FROM cases WHERE research_study_id=?",
                    (self.current_study_id,),
                ).fetchall()
            numeric = [int(row[0]) for row in rows if row and str(row[0] or "").isdigit()]
            return str(max(numeric, default=0) + 1)
        except Exception:
            return ""

    def save_case_to_database(self):
        if self.workflow_type == "research" and not self._v125_finalize_in_progress:
            return self.open_research_finalization()

        result = super().save_case_to_database()
        if self.workflow_type == "research" and getattr(self, "_case_saved", False):
            local = self.case_id.get().strip()
            storage = self._storage_case_id(local) if local else ""
            if storage:
                status, reason = self._evaluate_eligibility()
                reasons = list(self._v125_last_decision_reasons)
                with sqlite3.connect(self._db_path) as con:
                    con.execute(
                        """UPDATE cases
                           SET eligibility_reasons_json=?, eligibility_decided_at=?
                           WHERE case_id=?""",
                        (
                            json.dumps(reasons, ensure_ascii=False),
                            datetime.now().isoformat(timespec="seconds"),
                            storage,
                        ),
                    )
                    con.commit()
        return result

    def open_research_finalization(self):
        if self.workflow_type != "research" or not self.current_study:
            return super().save_case_to_database()
        if getattr(self, "original", None) is None:
            messagebox.showwarning(
                "Finalizar caso",
                "Primero abra la radiografía. La decisión de inclusión/exclusión se registra después de intentar el análisis."
            )
            return False

        if not self.case_id.get().strip():
            suggested = self._next_research_id()
            if suggested:
                self.case_id.set(suggested)

        win = tk.Toplevel(self)
        win.title("YomCeph · Finalizar caso de investigación")
        win.transient(self)
        win.grab_set()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        w, h = min(760, int(sw * 0.94)), min(820, int(sh * 0.90))
        win.geometry(f"{w}x{h}+{max(0,(sw-w)//2)}+{max(0,(sh-h)//2)}")

        outer = ttk.Frame(win)
        outer.pack(fill=tk.BOTH, expand=True)
        canvas = tk.Canvas(outer, highlightthickness=0)
        scroll = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        body = ttk.Frame(canvas, padding=16)
        item = canvas.create_window((0, 0), window=body, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        body.bind("<Configure>", lambda _e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(item, width=e.width))

        ttk.Label(body, text="Finalizar después del trazado", style="Section.TLabel", font=("Segoe UI Semibold", 16)).pack(anchor="w")
        ttk.Label(
            body,
            text=(
                "YomCeph revisará edad, país, landmarks y calibración. Si un punto no fue visible o la radiografía no permite medirlo, "
                "el caso se conserva como excluido y no entra en los cálculos de incluidos."
            ),
            style="Muted.TLabel",
            wraplength=max(520, w - 70),
        ).pack(anchor="w", pady=(3, 10))

        meta = ttk.LabelFrame(body, text="Datos mínimos", padding=10)
        meta.pack(fill=tk.X, pady=5)
        grid = ttk.Frame(meta)
        grid.pack(fill=tk.X)
        for col in (1, 3):
            grid.columnconfigure(col, weight=1)

        case_var = tk.StringVar(value=self.case_id.get())
        years_var = tk.StringVar(value=self.age_years_var.get())
        months_var = tk.StringVar(value=self.age_months_var.get() or "0")
        country_var = tk.StringVar(value=self.country_var.get() or self.current_study.get("country", ""))
        current_sex = self._sex_label(self.sex_code_var.get()) if self.sex_code_var.get() else ""
        sex_var = tk.StringVar(value=current_sex)
        sex_labels = [self._sex_label(code) for code in v116.SEX_CODES]

        ttk.Label(grid, text="Caso:").grid(row=0, column=0, sticky="w", pady=3)
        ttk.Entry(grid, textvariable=case_var, width=12).grid(row=0, column=1, sticky="ew", padx=4)
        ttk.Label(grid, text="Sexo registrado:").grid(row=0, column=2, sticky="w", pady=3)
        ttk.Combobox(grid, textvariable=sex_var, values=sex_labels, state="readonly").grid(row=0, column=3, sticky="ew", padx=4)
        ttk.Label(grid, text="Edad (años):").grid(row=1, column=0, sticky="w", pady=3)
        ttk.Entry(grid, textvariable=years_var, width=8).grid(row=1, column=1, sticky="w", padx=4)
        ttk.Label(grid, text="Meses:").grid(row=1, column=2, sticky="w", pady=3)
        ttk.Entry(grid, textvariable=months_var, width=8).grid(row=1, column=3, sticky="w", padx=4)
        ttk.Label(grid, text="País/procedencia:").grid(row=2, column=0, sticky="w", pady=3)
        ttk.Entry(grid, textvariable=country_var).grid(row=2, column=1, columnspan=3, sticky="ew", padx=4)

        group_vars = {}
        if self.current_study.get("group_fields"):
            groups = ttk.LabelFrame(body, text="Variables del protocolo", padding=10)
            groups.pack(fill=tk.X, pady=5)
            for field in self.current_study.get("group_fields", []):
                name = field.get("name", "Grupo")
                row = ttk.Frame(groups)
                row.pack(fill=tk.X, pady=2)
                ttk.Label(row, text=name + ":", width=24).pack(side=tk.LEFT)
                var = tk.StringVar(value=self.case_group_values.get(name, ""))
                ttk.Combobox(row, textvariable=var, values=field.get("options", []), state="readonly").pack(side=tk.LEFT, fill=tk.X, expand=True)
                group_vars[name] = var

        reasons_box = ttk.LabelFrame(body, text="Causas radiográficas adicionales de exclusión", padding=10)
        reasons_box.pack(fill=tk.X, pady=5)
        reason_vars = {}
        previous = set(self.case_exclusion_reasons)
        for reason in DEFAULT_EXCLUSION_REASONS:
            var = tk.BooleanVar(value=reason in previous)
            ttk.Checkbutton(reasons_box, text=reason, variable=var).pack(anchor="w", pady=1)
            reason_vars[reason] = var
        ttk.Label(reasons_box, text="Otro motivo:", style="Muted.TLabel").pack(anchor="w", pady=(6, 2))
        other_var = tk.StringVar(value=self.case_exclusion_other)
        ttk.Entry(reasons_box, textvariable=other_var).pack(fill=tk.X)

        auto = ttk.LabelFrame(body, text="Revisión automática", padding=10)
        auto.pack(fill=tk.X, pady=5)
        decision_label = tk.Label(auto, anchor="w", justify=tk.LEFT, padx=8, pady=7, wraplength=max(500, w - 90))
        decision_label.pack(fill=tk.X)

        def selected_reasons():
            return [reason for reason, var in reason_vars.items() if var.get()]

        def preview(*_args):
            required = required_landmarks(self.selected_measure_keys)
            status, exclusions, pending = research_case_decision(
                self.current_study,
                years_var.get(),
                months_var.get(),
                country_var.get(),
                required,
                self.points.keys(),
                selected_reasons() + (["Otro: " + other_var.get().strip()] if other_var.get().strip() else []),
                linear_calibration_required=self._linear_calibration_required(),
                calibrated=bool(getattr(self, "mm_per_pixel", None) and self.mm_per_pixel > 0),
            )
            missing_count = sum(1 for key in required if key not in self.points)
            if status == "eligible":
                decision_label.configure(text=f"✓ ELEGIBLE · landmarks completos ({len(required)}/{len(required)}).", bg="#E7F7EE", fg="#17633D")
            elif status == "not_eligible":
                decision_label.configure(text="⚠ EXCLUIR · " + "\n• ".join(exclusions), bg="#FFF3BF", fg="#6A4B00")
            else:
                decision_label.configure(text="PENDIENTE · " + "; ".join(pending) + f" · landmarks faltantes: {missing_count}", bg="#EEF2F6", fg="#344054")

        for var in (years_var, months_var, country_var, other_var):
            var.trace_add("write", preview)
        for var in reason_vars.values():
            var.trace_add("write", preview)
        preview()

        buttons = ttk.Frame(body)
        buttons.pack(fill=tk.X, pady=(10, 4))

        def finalize():
            case_id = case_var.get().strip()
            if not case_id:
                messagebox.showwarning("Caso", "Escriba un identificador de caso.", parent=win)
                return
            self._v123_internal_mutation = True
            try:
                self.case_id.set(case_id)
                self.age_years_var.set(years_var.get().strip())
                self.age_months_var.set(months_var.get().strip() or "0")
                self.country_var.set(country_var.get().strip())
                self.sex_code_var.set(self._sex_code_from_label(sex_var.get()))
                self.case_group_values = {name: var.get().strip() for name, var in group_vars.items()}
                self.case_exclusion_reasons = selected_reasons()
                self.case_exclusion_other = other_var.get().strip()
            finally:
                self._v123_internal_mutation = False

            status, exclusions, pending = self._decision()
            if status == "pending":
                messagebox.showwarning(
                    "Datos pendientes",
                    "No se puede decidir la elegibilidad todavía:\n\n• " + "\n• ".join(pending),
                    parent=win,
                )
                return
            self.manual_eligibility = "no" if status == "not_eligible" else "yes"
            self._v125_last_decision_reasons = exclusions
            self._sync_dirty_state()
            self._v125_finalize_in_progress = True
            try:
                result = self.save_case_to_database()
            finally:
                self._v125_finalize_in_progress = False
            if getattr(self, "_case_saved", False):
                try:
                    win.grab_release()
                except tk.TclError:
                    pass
                win.destroy()
                if status == "not_eligible":
                    self.status.config(text=f"Caso {case_id} registrado como excluido · no cuenta en la muestra incluida.")
                else:
                    self.status.config(text=f"Caso {case_id} incluido en la investigación.")
            return result

        ttk.Button(buttons, text="Cancelar", command=win.destroy, style="Soft.TButton").pack(side=tk.RIGHT, padx=3)
        ttk.Button(buttons, text="Finalizar y guardar", command=finalize, style="Purple.TButton").pack(side=tk.RIGHT, padx=3)
        return win


if __name__ == "__main__":
    import yomceph_desktop_hidpi as ui

    ui.enable_dpi_awareness()
    app = YomCephV125ResearchFlow()
    app.mainloop()
