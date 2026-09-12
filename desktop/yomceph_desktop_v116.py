import csv
import json
import math
import os
import sqlite3
import tkinter as tk
from datetime import date, datetime
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog, ttk

import yomceph_desktop as core
import yomceph_desktop_hidpi as ui
import yomceph_desktop_v11_database as v11db
import yomceph_desktop_v115 as v115

APP_VERSION = "0.11.6"
MAX_RESEARCH_CASES = 1000
UAM_TARGET = 103
UAM_CLINICS = ("", "Tepepan", "Tláhuac", "San Lorenzo", "Nezahualcóyotl")
PROFILE_GENERAL = "general"
PROFILE_CUSTOM = "research_custom"
PROFILE_UAM = "uam2026"

COUNTRIES = (
    "", "México", "Argentina", "Bolivia", "Brasil", "Canadá", "Chile", "Colombia",
    "Costa Rica", "Cuba", "Ecuador", "El Salvador", "España", "Estados Unidos",
    "Guatemala", "Honduras", "Nicaragua", "Panamá", "Paraguay", "Perú",
    "Puerto Rico", "República Dominicana", "Uruguay", "Venezuela", "Otro / Other",
)

SEX_CODES = (
    "", "female", "male", "intersex_dsd", "other_recorded", "not_recorded", "prefer_not_say"
)


class YomCephV116(v115.YomCephV115):
    """v0.11.6: interfaz progresiva, datos universales e internacionalización ES/EN."""

    def __init__(self):
        self.language_var = None
        self.profile_var = None
        self.interface_var = None
        self.study_name_var = None
        self.study_target_var = None
        self.birth_date_var = None
        self.sex_code_var = None
        self.gender_identity_var = None
        self.country_var = None
        self.institution_var = None
        self.high_contrast_var = None
        self._universal_widgets = []
        self._advanced_widgets = []
        self._simple_widgets = []
        self._uam_only_widgets = []
        self._i18n = self._load_i18n()
        super().__init__()
        self.title(self._t("app_title"))
        self.status.config(text=self._t("simple_help"))
        self._apply_profile_rules(initial=True)
        self._apply_interface_mode()
        self._apply_language()
        self._refresh_case_state()

    # ------------------------------------------------------------------
    # I18N
    # ------------------------------------------------------------------
    def _load_i18n(self):
        path = Path(__file__).with_name("yomceph_i18n.json")
        try:
            with open(path, "r", encoding="utf-8") as handle:
                return json.load(handle)
        except Exception:
            return {"languages": {}}

    def _lang(self):
        if self.language_var is None:
            return "es"
        return self.language_var.get() if self.language_var.get() in ("es", "en") else "es"

    def _t(self, key):
        lang = self._lang()
        return (
            self._i18n.get("languages", {}).get(lang, {}).get("strings", {}).get(key)
            or self._i18n.get("languages", {}).get("es", {}).get("strings", {}).get(key)
            or key
        )

    def _sex_label(self, code):
        lang = self._lang()
        table = self._i18n.get("languages", {}).get(lang, {}).get("sex", {})
        return table.get(code, code)

    def _profile_label(self, code):
        keys = {
            PROFILE_GENERAL: "profile_general",
            PROFILE_CUSTOM: "profile_custom",
            PROFILE_UAM: "profile_uam",
        }
        return self._t(keys.get(code, "profile_general"))

    def _profile_from_label(self, label):
        for code in (PROFILE_GENERAL, PROFILE_CUSTOM, PROFILE_UAM):
            if label == self._profile_label(code):
                return code
        return PROFILE_GENERAL

    # ------------------------------------------------------------------
    # Variables y migración no destructiva
    # ------------------------------------------------------------------
    def _ensure_metadata_vars(self):
        super()._ensure_metadata_vars()
        if self.language_var is None:
            self.language_var = tk.StringVar(master=self, value="es")
            self.profile_var = tk.StringVar(master=self, value=PROFILE_UAM)
            self.interface_var = tk.StringVar(master=self, value="simple")
            self.study_name_var = tk.StringVar(master=self, value="Investigación UAM 2026")
            self.study_target_var = tk.StringVar(master=self, value=str(UAM_TARGET))
            self.birth_date_var = tk.StringVar(master=self, value="")
            self.sex_code_var = tk.StringVar(master=self, value="")
            self.gender_identity_var = tk.StringVar(master=self, value="")
            self.country_var = tk.StringVar(master=self, value="México")
            self.institution_var = tk.StringVar(master=self, value="")
            self.high_contrast_var = tk.BooleanVar(master=self, value=False)

    def _clear_metadata(self):
        super()._clear_metadata()
        self._ensure_metadata_vars()
        self.birth_date_var.set("")
        self.sex_code_var.set("")
        self.gender_identity_var.set("")
        self.country_var.set("México" if self.profile_var.get() == PROFILE_UAM else "")
        self.institution_var.set("")
        if self.profile_var.get() == PROFILE_GENERAL:
            self.study_name_var.set("")
            self.study_target_var.set("")

    def _init_database(self):
        super()._init_database()
        with sqlite3.connect(self._db_path) as con:
            existing = {row[1] for row in con.execute("PRAGMA table_info(cases)")}
            additions = {
                "app_profile": "TEXT",
                "study_name": "TEXT",
                "study_target": "INTEGER",
                "birth_date": "TEXT",
                "sex_code": "TEXT",
                "gender_identity": "TEXT",
                "country": "TEXT",
                "institution": "TEXT",
                "ui_language": "TEXT",
            }
            for name, sql_type in additions.items():
                if name not in existing:
                    con.execute(f"ALTER TABLE cases ADD COLUMN {name} {sql_type}")

            # La base v0.11.5 era exclusivamente la investigación actual. Se etiqueta
            # lo existente como UAM 2026 sin modificar puntos, resultados ni metadatos.
            con.execute("""
                UPDATE cases
                SET app_profile=COALESCE(app_profile, ?),
                    study_name=COALESCE(study_name, ?),
                    study_target=COALESCE(study_target, ?),
                    country=COALESCE(NULLIF(country,''), 'México'),
                    ui_language=COALESCE(ui_language, 'es')
                WHERE app_profile IS NULL OR app_profile=''
            """, (PROFILE_UAM, "Investigación UAM 2026", UAM_TARGET))
            con.commit()

    # ------------------------------------------------------------------
    # Barra universal y flujo progresivo
    # ------------------------------------------------------------------
    def _install_database_bar(self):
        self._ensure_metadata_vars()
        wrapper = ttk.Frame(self, padding=(10, 5))
        try:
            wrapper.pack(fill=tk.X, before=self.body_panes)
        except Exception:
            wrapper.pack(fill=tk.X)
        self.universal_wrapper = wrapper

        row1 = ttk.Frame(wrapper)
        row1.pack(fill=tk.X)
        ttk.Label(row1, text="YomCeph", style="Section.TLabel").pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(row1, textvariable=tk.StringVar(master=self, value="Uso / Use:"), style="Muted.TLabel").pack(side=tk.LEFT)
        self.profile_combo = ttk.Combobox(row1, state="readonly", width=30)
        self.profile_combo.pack(side=tk.LEFT, padx=(4, 10))
        self.profile_combo.bind("<<ComboboxSelected>>", self._on_profile_selected)

        ttk.Label(row1, text="Idioma / Language:", style="Muted.TLabel").pack(side=tk.LEFT)
        self.language_combo = ttk.Combobox(row1, state="readonly", width=11, values=("Español", "English"))
        self.language_combo.set("Español")
        self.language_combo.pack(side=tk.LEFT, padx=(4, 10))
        self.language_combo.bind("<<ComboboxSelected>>", self._on_language_selected)

        ttk.Label(row1, text="Interfaz / Interface:", style="Muted.TLabel").pack(side=tk.LEFT)
        self.interface_combo = ttk.Combobox(row1, state="readonly", width=22)
        self.interface_combo.pack(side=tk.LEFT, padx=(4, 10))
        self.interface_combo.bind("<<ComboboxSelected>>", self._on_interface_selected)

        self.high_contrast_check = ttk.Checkbutton(
            row1, text="Alto contraste", variable=self.high_contrast_var,
            command=self._apply_high_contrast,
        )
        self.high_contrast_check.pack(side=tk.RIGHT)
        self._advanced_widgets.append(self.high_contrast_check)

        self.step_frame = ttk.Frame(wrapper, padding=(0, 6, 0, 2))
        self.step_frame.pack(fill=tk.X)
        self.step_buttons = []
        step_specs = [
            ("step_data", self._focus_case_data),
            ("step_image", self.open_image),
            ("step_cal", self.start_calibration),
            ("step_points", self._focus_landmarks),
            ("step_qc", self.show_quality_control),
            ("step_results", self.calculate),
            ("step_save", self.save_case_to_database),
        ]
        for key, command in step_specs:
            button = ttk.Button(self.step_frame, text=self._t(key), command=command, style="Soft.TButton")
            button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
            self.step_buttons.append((key, button))

        study = ttk.Frame(wrapper, padding=(0, 4, 0, 2))
        study.pack(fill=tk.X)
        self.study_row = study
        self.study_name_label = ttk.Label(study, text=self._t("study_name") + ":", style="Muted.TLabel")
        self.study_name_label.pack(side=tk.LEFT)
        self.study_name_entry = ttk.Entry(study, textvariable=self.study_name_var, width=30)
        self.study_name_entry.pack(side=tk.LEFT, padx=(4, 10))
        self.study_target_label = ttk.Label(study, text=self._t("target") + ":", style="Muted.TLabel")
        self.study_target_label.pack(side=tk.LEFT)
        self.study_target_entry = ttk.Entry(study, textvariable=self.study_target_var, width=6)
        self.study_target_entry.pack(side=tk.LEFT, padx=(4, 8))
        self.db_counter = ttk.Label(study, text="0 casos", style="Muted.TLabel")
        self.db_counter.pack(side=tk.LEFT, padx=(4, 12))
        self.mode_label = ttk.Label(study, text="Modo: Ambos", style="Muted.TLabel")
        self.mode_label.pack(side=tk.LEFT)

        self.advanced_button_frame = ttk.Frame(study)
        self.advanced_button_frame.pack(side=tk.RIGHT)
        self.open_db_button = ttk.Button(self.advanced_button_frame, text=self._t("open_db"), command=self.open_database_browser, style="Soft.TButton")
        self.open_db_button.pack(side=tk.LEFT, padx=2)
        self.export_db_button = ttk.Button(self.advanced_button_frame, text=self._t("export_study"), command=self.export_database_csv, style="Gold.TButton")
        self.export_db_button.pack(side=tk.LEFT, padx=2)
        self.more_info_button = ttk.Button(self.advanced_button_frame, text=self._t("more_info"), command=self._show_profile_info, style="Soft.TButton")
        self.more_info_button.pack(side=tk.LEFT, padx=2)
        self._advanced_widgets.extend([self.open_db_button, self.export_db_button])

        meta1 = ttk.Frame(wrapper, padding=(0, 4, 0, 0))
        meta1.pack(fill=tk.X)
        self.meta1 = meta1
        ttk.Label(meta1, text=self._t("age") + ":", style="Muted.TLabel").pack(side=tk.LEFT)
        self.age_years_entry = ttk.Entry(meta1, textvariable=self.age_years_var, width=4)
        self.age_years_entry.pack(side=tk.LEFT, padx=(4, 2))
        self.years_label = ttk.Label(meta1, text=self._t("years"), style="Muted.TLabel")
        self.years_label.pack(side=tk.LEFT)
        self.age_months_entry = ttk.Entry(meta1, textvariable=self.age_months_var, width=3)
        self.age_months_entry.pack(side=tk.LEFT, padx=(4, 2))
        self.months_label = ttk.Label(meta1, text=self._t("months"), style="Muted.TLabel")
        self.months_label.pack(side=tk.LEFT, padx=(0, 10))

        self.birth_label = ttk.Label(meta1, text=self._t("birth_date") + ":", style="Muted.TLabel")
        self.birth_label.pack(side=tk.LEFT)
        self.birth_entry = ttk.Entry(meta1, textvariable=self.birth_date_var, width=12)
        self.birth_entry.pack(side=tk.LEFT, padx=(4, 10))

        self.sex_label_widget = ttk.Label(meta1, text=self._t("sex") + ":", style="Muted.TLabel")
        self.sex_label_widget.pack(side=tk.LEFT)
        self.sex_combo = ttk.Combobox(meta1, state="readonly", width=28)
        self.sex_combo.pack(side=tk.LEFT, padx=(4, 10))
        self.sex_combo.bind("<<ComboboxSelected>>", self._on_sex_selected)

        meta2 = ttk.Frame(wrapper, padding=(0, 4, 0, 1))
        meta2.pack(fill=tk.X)
        self.meta2 = meta2
        self.gender_label = ttk.Label(meta2, text=self._t("gender") + ":", style="Muted.TLabel")
        self.gender_label.pack(side=tk.LEFT)
        self.gender_entry = ttk.Entry(meta2, textvariable=self.gender_identity_var, width=24)
        self.gender_entry.pack(side=tk.LEFT, padx=(4, 10))

        self.country_label = ttk.Label(meta2, text=self._t("country") + ":", style="Muted.TLabel")
        self.country_label.pack(side=tk.LEFT)
        self.country_combo = ttk.Combobox(meta2, textvariable=self.country_var, values=COUNTRIES, state="normal", width=18)
        self.country_combo.pack(side=tk.LEFT, padx=(4, 10))

        self.institution_label = ttk.Label(meta2, text=self._t("institution") + ":", style="Muted.TLabel")
        self.institution_label.pack(side=tk.LEFT)
        self.institution_entry = ttk.Entry(meta2, textvariable=self.institution_var, width=25)
        self.institution_entry.pack(side=tk.LEFT, padx=(4, 10))

        self.clinic_label = ttk.Label(meta2, text=self._t("clinic_site") + ":", style="Muted.TLabel")
        self.clinic_label.pack(side=tk.LEFT)
        self.clinic_combo = ttk.Combobox(meta2, textvariable=self.clinic_var, state="normal", width=20)
        self.clinic_combo.pack(side=tk.LEFT, padx=(4, 10))

        self.rx_label = ttk.Label(meta2, text=self._t("rx_date") + ":", style="Muted.TLabel")
        self.rx_label.pack(side=tk.LEFT)
        self.rx_entry = ttk.Entry(meta2, textvariable=self.radiograph_date_var, width=12)
        self.rx_entry.pack(side=tk.LEFT, padx=(4, 2))

        self.case_state_frame = tk.Frame(self, bg="#EEF2F6", padx=10, pady=5)
        try:
            self.case_state_frame.pack(fill=tk.X, before=self.body_panes)
        except Exception:
            self.case_state_frame.pack(fill=tk.X)
        self.case_state_label = tk.Label(
            self.case_state_frame, text="CASO — · 0/0 puntos · SIN CALIBRAR · NUEVO",
            bg="#EEF2F6", fg="#233044", font=("Segoe UI", 10, "bold"), anchor="w"
        )
        self.case_state_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.qc_button = tk.Button(
            self.case_state_frame, text="QC pendiente", command=self.show_quality_control,
            relief=tk.FLAT, padx=10, pady=3, cursor="hand2",
        )
        self.qc_button.pack(side=tk.RIGHT)

        if not getattr(self, "_state_traces_installed", False):
            self._state_traces_installed = True
            for var in (
                self.case_id, self.face_direction, self.age_years_var, self.age_months_var,
                self.clinic_var, self.radiograph_date_var, self.birth_date_var,
                self.sex_code_var, self.gender_identity_var, self.country_var,
                self.institution_var, self.study_name_var, self.study_target_var,
            ):
                var.trace_add("write", self._tracked_field_changed)

    # ------------------------------------------------------------------
    # Perfil e interfaz
    # ------------------------------------------------------------------
    def _refresh_profile_combo(self):
        values = [self._profile_label(PROFILE_GENERAL), self._profile_label(PROFILE_CUSTOM), self._profile_label(PROFILE_UAM)]
        self.profile_combo.configure(values=values)
        self.profile_combo.set(self._profile_label(self.profile_var.get()))

    def _on_profile_selected(self, _event=None):
        self.profile_var.set(self._profile_from_label(self.profile_combo.get()))
        self._apply_profile_rules(initial=False)
        self._mark_dirty(schedule_qc=True)

    def _on_language_selected(self, _event=None):
        self.language_var.set("en" if self.language_combo.get() == "English" else "es")
        self._apply_language()

    def _on_interface_selected(self, _event=None):
        simple_label = self._t("simple")
        self.interface_var.set("simple" if self.interface_combo.get() == simple_label else "advanced")
        self._apply_interface_mode()

    def _on_sex_selected(self, _event=None):
        selected = self.sex_combo.get()
        code = next((code for code in SEX_CODES if self._sex_label(code) == selected), "")
        self.sex_code_var.set(code)
        self.sex_var.set(self._sex_label(code))

    def _apply_profile_rules(self, initial=False):
        if not hasattr(self, "profile_combo"):
            return
        profile = self.profile_var.get()
        if profile == PROFILE_UAM:
            self.study_name_var.set("Investigación UAM 2026")
            self.study_target_var.set(str(UAM_TARGET))
            self.country_var.set("México")
            self.study_name_entry.configure(state="readonly")
            self.study_target_entry.configure(state="readonly")
            self.country_combo.configure(state="readonly")
            self.clinic_combo.configure(values=UAM_CLINICS, state="readonly")
            if self.clinic_var.get() not in UAM_CLINICS:
                self.clinic_var.set("")
        elif profile == PROFILE_CUSTOM:
            if not self.study_name_var.get().strip() or self.study_name_var.get() == "Investigación UAM 2026":
                self.study_name_var.set("Nueva investigación" if self._lang() == "es" else "New research study")
            if not self.study_target_var.get().strip() or self.study_target_var.get() == str(UAM_TARGET):
                self.study_target_var.set("100")
            self.study_name_entry.configure(state="normal")
            self.study_target_entry.configure(state="normal")
            self.country_combo.configure(state="normal")
            self.clinic_combo.configure(values=(), state="normal")
        else:
            self.study_name_var.set("")
            self.study_target_var.set("")
            self.study_name_entry.configure(state="disabled")
            self.study_target_entry.configure(state="disabled")
            self.country_combo.configure(state="normal")
            self.clinic_combo.configure(values=(), state="normal")

        self._refresh_profile_combo()
        self._update_db_counter()
        if not initial:
            self._show_profile_hint()

    def _show_profile_hint(self):
        profile = self.profile_var.get()
        key = "uam_help" if profile == PROFILE_UAM else ("custom_help" if profile == PROFILE_CUSTOM else "general_help")
        self.status.config(text=self._t(key))

    def _show_profile_info(self):
        profile = self.profile_var.get()
        key = "uam_help" if profile == PROFILE_UAM else ("custom_help" if profile == PROFILE_CUSTOM else "general_help")
        messagebox.showinfo(self._t("more_info"), self._t(key))

    def _apply_interface_mode(self):
        if not hasattr(self, "meta2"):
            return
        simple = self.interface_var.get() == "simple"
        if simple:
            self.meta2.pack_forget()
            self.advanced_button_frame.pack_forget()
            self.high_contrast_check.pack_forget()
            self.status.config(text=self._t("simple_help"))
        else:
            if not self.meta2.winfo_manager():
                self.meta2.pack(fill=tk.X, pady=(2, 0))
            if not self.advanced_button_frame.winfo_manager():
                self.advanced_button_frame.pack(side=tk.RIGHT)
            if not self.high_contrast_check.winfo_manager():
                self.high_contrast_check.pack(side=tk.RIGHT)
        self._refresh_case_state()

    def _apply_high_contrast(self):
        enabled = bool(self.high_contrast_var.get())
        try:
            self.canvas.configure(background=("#000000" if enabled else "#101010"))
            self.case_state_label.configure(font=("Segoe UI", 11 if enabled else 10, "bold"))
        except Exception:
            pass
        self.status.config(text=("Alto contraste activado." if enabled else "Alto contraste desactivado."))

    def _apply_language(self):
        if not hasattr(self, "profile_combo"):
            return
        self.title(self._t("app_title"))
        self.language_combo.set("English" if self._lang() == "en" else "Español")
        self.interface_combo.configure(values=(self._t("simple"), self._t("advanced")))
        self.interface_combo.set(self._t("simple") if self.interface_var.get() == "simple" else self._t("advanced"))
        self.high_contrast_check.configure(text=self._t("high_contrast"))
        for key, button in self.step_buttons:
            button.configure(text=self._t(key))
        self.study_name_label.configure(text=self._t("study_name") + ":")
        self.study_target_label.configure(text=self._t("target") + ":")
        self.birth_label.configure(text=self._t("birth_date") + ":")
        self.sex_label_widget.configure(text=self._t("sex") + ":")
        self.gender_label.configure(text=self._t("gender") + ":")
        self.country_label.configure(text=self._t("country") + ":")
        self.institution_label.configure(text=self._t("institution") + ":")
        self.clinic_label.configure(text=self._t("clinic_site") + ":")
        self.rx_label.configure(text=self._t("rx_date") + ":")
        self.years_label.configure(text=self._t("years"))
        self.months_label.configure(text=self._t("months"))
        self.open_db_button.configure(text=self._t("open_db"))
        self.export_db_button.configure(text=self._t("export_study"))
        self.more_info_button.configure(text=self._t("more_info"))
        self.sex_combo.configure(values=tuple(self._sex_label(code) for code in SEX_CODES))
        self.sex_combo.set(self._sex_label(self.sex_code_var.get()))
        self._refresh_profile_combo()
        self._apply_profile_rules(initial=True)
        self._apply_interface_mode()

    def _focus_case_data(self):
        try:
            self.age_years_entry.focus_set()
        except Exception:
            pass
        self.status.config(text=self._t("simple_help"))

    def _focus_landmarks(self):
        try:
            self.point_list.focus_set()
        except Exception:
            pass
        self.status.config(text=("Seleccione un landmark y colóquelo sobre la radiografía." if self._lang() == "es" else "Select a landmark and place it on the radiograph."))

    # ------------------------------------------------------------------
    # Fechas, números y metadatos universales
    # ------------------------------------------------------------------
    def _parse_decimal(self, text):
        cleaned = str(text).strip().replace(" ", "")
        if not cleaned:
            return None
        if "," in cleaned and "." in cleaned:
            if cleaned.rfind(",") > cleaned.rfind("."):
                cleaned = cleaned.replace(".", "").replace(",", ".")
            else:
                cleaned = cleaned.replace(",", "")
        else:
            cleaned = cleaned.replace(",", ".")
        return float(cleaned)

    def _parse_date_to_iso(self, text):
        raw = str(text or "").strip()
        if not raw:
            return ""
        formats = ["%Y-%m-%d"]
        formats += ["%d/%m/%Y", "%d-%m-%Y"] if self._lang() == "es" else ["%m/%d/%Y", "%m-%d-%Y"]
        for fmt in formats:
            try:
                return datetime.strptime(raw, fmt).date().isoformat()
            except ValueError:
                pass
        raise ValueError(self._t("date_hint"))

    def _format_iso_date(self, iso_value):
        if not iso_value:
            return ""
        try:
            parsed = datetime.strptime(iso_value, "%Y-%m-%d").date()
        except ValueError:
            return iso_value
        return parsed.strftime("%d/%m/%Y" if self._lang() == "es" else "%m/%d/%Y")

    def _validated_metadata(self):
        self._ensure_metadata_vars()
        profile = self.profile_var.get()
        years_text = self.age_years_var.get().strip()
        months_text = self.age_months_var.get().strip()
        years = None
        months = None
        if years_text:
            try:
                years = int(years_text)
            except ValueError:
                raise ValueError("La edad en años debe ser un entero." if self._lang() == "es" else "Age in years must be an integer.")
            upper = 15 if profile == PROFILE_UAM else 130
            if not 0 <= years <= upper:
                raise ValueError((f"La edad debe estar entre 0 y {upper} años." if self._lang() == "es" else f"Age must be between 0 and {upper} years."))
        if months_text:
            try:
                months = int(months_text)
            except ValueError:
                raise ValueError("Los meses deben ser un entero." if self._lang() == "es" else "Months must be an integer.")
            if not 0 <= months <= 11:
                raise ValueError("Los meses deben estar entre 0 y 11." if self._lang() == "es" else "Months must be between 0 and 11.")
            if years is None:
                raise ValueError("Capture también los años (puede ser 0)." if self._lang() == "es" else "Enter years too (0 is allowed).")

        rx_iso = self._parse_date_to_iso(self.radiograph_date_var.get())
        birth_iso = self._parse_date_to_iso(self.birth_date_var.get())
        if birth_iso and rx_iso and birth_iso > rx_iso:
            raise ValueError("La fecha de nacimiento no puede ser posterior a la radiografía." if self._lang() == "es" else "Birth date cannot be later than the radiograph date.")

        if profile == PROFILE_UAM and self.clinic_var.get().strip() not in UAM_CLINICS:
            raise ValueError("Seleccione una de las cuatro clínicas del protocolo UAM 2026.")

        if profile == PROFILE_CUSTOM:
            if not self.study_name_var.get().strip():
                raise ValueError("Escriba el nombre de la investigación." if self._lang() == "es" else "Enter the research study name.")
            try:
                target = int(self.study_target_var.get().strip())
            except ValueError:
                raise ValueError("La meta de casos debe ser un entero entre 1 y 1000." if self._lang() == "es" else "Case target must be an integer from 1 to 1000.")
            if not 1 <= target <= MAX_RESEARCH_CASES:
                raise ValueError("La investigación admite de 1 a 1000 casos." if self._lang() == "es" else "Research mode supports 1 to 1000 cases.")

        sex_code = self.sex_code_var.get().strip()
        sex_label = self._sex_label(sex_code)
        self.sex_var.set(sex_label)
        return {
            "age_years": years,
            "age_months": months,
            "sex": sex_label,
            "clinic": self.clinic_var.get().strip(),
            "radiograph_date": rx_iso,
            "birth_date": birth_iso,
            "sex_code": sex_code,
            "gender_identity": self.gender_identity_var.get().strip(),
            "country": self.country_var.get().strip(),
            "institution": self.institution_var.get().strip(),
        }

    def finish_calibration(self):
        self.calibrating = False
        if len(self.calibration_points) != 2:
            self._restore_calibration_backup()
            return
        pixel_distance = core.dist(*self.calibration_points)
        if pixel_distance < 5:
            messagebox.showwarning("Calibración", "Los puntos están demasiado juntos." if self._lang() == "es" else "Calibration points are too close together.")
            self._restore_calibration_backup()
            return
        prompt = "Longitud real entre los dos puntos (mm). Puede usar coma o punto decimal:" if self._lang() == "es" else "Real length between the two points (mm). You may use comma or decimal point:"
        raw = simpledialog.askstring("Calibración / Calibration", prompt)
        if raw is None:
            self._restore_calibration_backup()
            return
        try:
            real_mm = self._parse_decimal(raw)
            if real_mm is None or real_mm <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Calibración / Calibration", "Valor no válido." if self._lang() == "es" else "Invalid value.")
            self._restore_calibration_backup()
            return
        self.calibration_real_mm = float(real_mm)
        self.mm_per_pixel = self.calibration_real_mm / pixel_distance
        self._calibration_backup = None
        self.cal_label.config(text=f"Calibrado: {self.mm_per_pixel:.5f} mm/píxel")
        self.status.config(text=f"Calibración: {real_mm:g} mm / {pixel_distance:.2f} px")
        self.redraw()
        self._mark_dirty(schedule_qc=True)

    # ------------------------------------------------------------------
    # Persistencia universal encima del guardado científico v0.11.5
    # ------------------------------------------------------------------
    def save_case_to_database(self):
        try:
            universal = self._validated_metadata()
        except ValueError as exc:
            messagebox.showwarning(self._t("case_data"), str(exc))
            return

        before = self._loaded_case_id
        super().save_case_to_database()
        case_id = self.case_id.get().strip()
        if not case_id or self._loaded_case_id != case_id:
            return
        # Si el usuario canceló una actualización, super() no deja el caso como guardado.
        if not self._case_saved:
            return
        profile = self.profile_var.get()
        target = None
        if profile == PROFILE_UAM:
            target = UAM_TARGET
        elif profile == PROFILE_CUSTOM:
            target = int(self.study_target_var.get().strip())
        with sqlite3.connect(self._db_path) as con:
            con.execute("""
                UPDATE cases SET
                    app_profile=?, study_name=?, study_target=?, birth_date=?,
                    sex_code=?, gender_identity=?, country=?, institution=?, ui_language=?
                WHERE case_id=?
            """, (
                profile, self.study_name_var.get().strip(), target, universal["birth_date"],
                universal["sex_code"], universal["gender_identity"], universal["country"],
                universal["institution"], self._lang(), case_id,
            ))
            row = con.execute("SELECT id, details FROM case_history WHERE case_id=? ORDER BY id DESC LIMIT 1", (case_id,)).fetchone()
            if row:
                history_id, raw_details = row
                try:
                    details = json.loads(raw_details or "{}")
                except Exception:
                    details = {}
                details.update({
                    "app_profile": profile,
                    "study_name": self.study_name_var.get().strip(),
                    "study_target": target,
                    "country": universal["country"],
                    "institution": universal["institution"],
                    "sex_code": universal["sex_code"],
                    "gender_identity_recorded": bool(universal["gender_identity"]),
                    "ui_language": self._lang(),
                })
                con.execute("UPDATE case_history SET details=? WHERE id=?", (json.dumps(details, ensure_ascii=False), history_id))
            con.commit()
        self._update_db_counter()
        self._refresh_case_state()

    def load_case_from_database(self, case_id):
        self._suspend_dirty = True
        try:
            super().load_case_from_database(case_id)
            with sqlite3.connect(self._db_path) as con:
                row = con.execute("""
                    SELECT app_profile, study_name, study_target, birth_date, sex_code,
                           gender_identity, country, institution, ui_language
                    FROM cases WHERE case_id=?
                """, (case_id,)).fetchone()
            if row:
                profile, study_name, target, birth, sex_code, gender, country, institution, lang = row
                self.profile_var.set(profile or PROFILE_UAM)
                self.study_name_var.set(study_name or ("Investigación UAM 2026" if self.profile_var.get() == PROFILE_UAM else ""))
                self.study_target_var.set("" if target is None else str(target))
                self.birth_date_var.set(self._format_iso_date(birth or ""))
                self.sex_code_var.set(sex_code or "")
                self.gender_identity_var.set(gender or "")
                self.country_var.set(country or "")
                self.institution_var.set(institution or "")
                if lang in ("es", "en"):
                    self.language_var.set(lang)
                # La fecha RX se muestra en el formato de la interfaz, pero permanece ISO en SQLite.
                self.radiograph_date_var.set(self._format_iso_date(self.radiograph_date_var.get()))
        finally:
            self._suspend_dirty = False
        self._apply_language()
        self._apply_profile_rules(initial=True)
        self._case_saved = True
        self._refresh_case_state()

    def new_case(self):
        profile = self.profile_var.get()
        language = self._lang()
        interface = self.interface_var.get()
        result = super().new_case()
        self.language_var.set(language)
        self.profile_var.set(profile)
        self.interface_var.set(interface)
        self._apply_profile_rules(initial=True)
        self._apply_language()
        self._apply_interface_mode()
        return result

    def _update_db_counter(self):
        if not hasattr(self, "db_counter") or not self._db_path:
            return
        profile = self.profile_var.get() if self.profile_var is not None else PROFILE_UAM
        study_name = self.study_name_var.get().strip() if self.study_name_var is not None else "Investigación UAM 2026"
        try:
            with sqlite3.connect(self._db_path) as con:
                if profile == PROFILE_GENERAL:
                    count = con.execute("SELECT COUNT(*) FROM cases WHERE app_profile=?", (PROFILE_GENERAL,)).fetchone()[0]
                    text = f"{count} casos"
                elif profile == PROFILE_UAM:
                    count = con.execute("SELECT COUNT(*) FROM cases WHERE app_profile=?", (PROFILE_UAM,)).fetchone()[0]
                    text = f"{count} / {UAM_TARGET} casos"
                else:
                    count = con.execute("SELECT COUNT(*) FROM cases WHERE app_profile=? AND study_name=?", (PROFILE_CUSTOM, study_name)).fetchone()[0]
                    try:
                        target = int(self.study_target_var.get().strip())
                    except Exception:
                        target = 0
                    text = f"{count} / {target or '?'} casos"
            self.db_counter.config(text=text)
        except Exception:
            pass

    def export_database_csv(self):
        profile = self.profile_var.get()
        default_name = "YomCeph_general.csv" if profile == PROFILE_GENERAL else "YomCeph_investigacion.csv"
        path = filedialog.asksaveasfilename(
            title=self._t("export_study"), defaultextension=".csv", initialfile=default_name,
            filetypes=[("CSV", "*.csv")],
        )
        if not path:
            return
        all_keys = []
        for key in v11db.STEINER_ORDER + v11db.POSTURE_ORDER:
            if key not in all_keys:
                all_keys.append(key)
        params = []
        where = ""
        if profile == PROFILE_UAM:
            where = "WHERE app_profile=?"; params = [PROFILE_UAM]
        elif profile == PROFILE_CUSTOM:
            where = "WHERE app_profile=? AND study_name=?"; params = [PROFILE_CUSTOM, self.study_name_var.get().strip()]
        else:
            where = "WHERE app_profile=?"; params = [PROFILE_GENERAL]
        with sqlite3.connect(self._db_path) as con:
            cases = con.execute(f"""
                SELECT case_id, app_profile, study_name, study_target, age_years, age_months,
                       birth_date, sex, sex_code, gender_identity, country, institution, clinic,
                       radiograph_date, analysis_mode, updated_at, mm_per_pixel,
                       calibration_real_mm, calibration_points_json
                FROM cases {where}
                ORDER BY CASE WHEN case_id<>'' AND case_id NOT GLOB '*[^0-9]*'
                              THEN CAST(case_id AS INTEGER) ELSE 2147483647 END,
                         case_id COLLATE NOCASE
            """, params).fetchall()
            data = {}
            for db_case_id, name, value, diagnosis in con.execute("SELECT case_id,name,value,diagnosis FROM measurements"):
                data.setdefault(db_case_id, {})[name] = (value, diagnosis or "")
        headers = [
            "Caso", "Perfil", "Estudio", "Meta de casos", "Edad años", "Edad meses",
            "Edad decimal (años)", "Fecha nacimiento", "Sexo registrado", "Código sexo",
            "Identidad de género", "País", "Institución", "Clínica/sede", "Fecha radiografía",
            "Tipo de análisis", "Última actualización", "Calibración mm/píxel",
            "Referencia calibración (mm)", "Cal P1 X", "Cal P1 Y", "Cal P2 X", "Cal P2 Y",
            "Trazabilidad calibración",
        ]
        for key in all_keys:
            display = "Profundidad cervical" if key == "Profundidad cervical (mm)" else key
            headers.extend([display, display + " - Diagnóstico"])
        with open(path, "w", newline="", encoding="utf-8-sig") as handle:
            writer = csv.writer(handle)
            writer.writerow(headers)
            for rowdata in cases:
                (db_case_id, db_profile, study_name, study_target, years, months, birth, sex,
                 sex_code, gender, country, institution, clinic, rx_date, mode, updated, mmpp,
                 real_mm, calibration_json) = rowdata
                age_decimal = "" if years is None else round(float(years) + float(months or 0) / 12.0, 4)
                try:
                    calibration = json.loads(calibration_json or "[]")
                except Exception:
                    calibration = []
                p1 = calibration[0] if len(calibration) >= 1 else ("", "")
                p2 = calibration[1] if len(calibration) >= 2 else ("", "")
                traceable = "Sí" if mmpp and real_mm and len(calibration) == 2 else ("Legada/incompleta" if mmpp else "No")
                out = [db_case_id, db_profile or "", study_name or "", "" if study_target is None else study_target,
                       "" if years is None else years, "" if months is None else months, age_decimal,
                       birth or "", sex or "", sex_code or "", gender or "", country or "",
                       institution or "", clinic or "", rx_date or "", mode, updated,
                       "" if mmpp is None else mmpp, "" if real_mm is None else real_mm,
                       p1[0], p1[1], p2[0], p2[1], traceable]
                measures = data.get(db_case_id, {})
                for key in all_keys:
                    if key in measures:
                        value, diagnosis = measures[key]; out.extend([value, diagnosis])
                    else:
                        out.extend(["", ""])
                writer.writerow(out)
        self.status.config(text=(f"Estudio exportado: {os.path.basename(path)}" if self._lang() == "es" else f"Study exported: {os.path.basename(path)}"))
        messagebox.showinfo(self._t("export_study"), (f"Casos exportados: {len(cases)}" if self._lang() == "es" else f"Exported cases: {len(cases)}"))


if __name__ == "__main__":
    ui.enable_dpi_awareness()
    app = YomCephV116()
    app.mainloop()
