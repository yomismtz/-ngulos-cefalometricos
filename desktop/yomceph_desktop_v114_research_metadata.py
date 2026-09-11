import csv
import json
import os
import sqlite3
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, ttk

import yomceph_desktop_hidpi as ui
import yomceph_desktop_v11_database as v11db
import yomceph_desktop_v113_workspace as v113

APP_VERSION = "0.11.4"
CLINICS = ("", "Tepepan", "Tláhuac", "San Lorenzo", "Nezahualcóyotl")
SEX_OPTIONS = ("", "Femenino", "Masculino", "No registrado")


class ResearchMetadataYomCeph(v113.WorkspaceYomCeph):
    """v0.11.4: metadatos de investigación + protección contra sobrescritura accidental."""

    def __init__(self):
        super().__init__()
        self.title("YomCeph Desktop · Investigación · Base de datos · v0.11.4")
        self.status.config(
            text="v0.11.4 · Metadatos de investigación · Protección de casos activos"
        )

    # ------------------------------------------------------------------
    # Variables auxiliares de metadatos
    # ------------------------------------------------------------------
    def _ensure_metadata_vars(self):
        if not hasattr(self, "age_years_var"):
            self.age_years_var = tk.StringVar(master=self, value="")
            self.age_months_var = tk.StringVar(master=self, value="")
            self.sex_var = tk.StringVar(master=self, value="")
            self.clinic_var = tk.StringVar(master=self, value="")
            self.radiograph_date_var = tk.StringVar(master=self, value="")

    def _clear_metadata(self):
        self._ensure_metadata_vars()
        for var in (
            self.age_years_var,
            self.age_months_var,
            self.sex_var,
            self.clinic_var,
            self.radiograph_date_var,
        ):
            var.set("")

    def _validated_metadata(self):
        self._ensure_metadata_vars()
        years_text = self.age_years_var.get().strip()
        months_text = self.age_months_var.get().strip()
        years = None
        months = None

        if years_text:
            try:
                years = int(years_text)
            except ValueError:
                raise ValueError("La edad en años debe ser un número entero.")
            if not 0 <= years <= 15:
                raise ValueError("La edad en años debe estar entre 0 y 15.")

        if months_text:
            try:
                months = int(months_text)
            except ValueError:
                raise ValueError("Los meses de edad deben ser un número entero.")
            if not 0 <= months <= 11:
                raise ValueError("Los meses de edad deben estar entre 0 y 11.")
            if years is None:
                raise ValueError("Si registra meses de edad, capture también los años (puede ser 0).")

        date_text = self.radiograph_date_var.get().strip()
        if date_text:
            try:
                datetime.strptime(date_text, "%Y-%m-%d")
            except ValueError:
                raise ValueError("La fecha de radiografía debe escribirse como AAAA-MM-DD.")

        return {
            "age_years": years,
            "age_months": months,
            "sex": self.sex_var.get().strip(),
            "clinic": self.clinic_var.get().strip(),
            "radiograph_date": date_text,
        }

    # ------------------------------------------------------------------
    # Migración no destructiva de la base existente
    # ------------------------------------------------------------------
    def _init_database(self):
        super()._init_database()
        with sqlite3.connect(self._db_path) as con:
            existing = {row[1] for row in con.execute("PRAGMA table_info(cases)")}
            additions = {
                "age_years": "INTEGER",
                "age_months": "INTEGER",
                "sex": "TEXT",
                "clinic": "TEXT",
                "radiograph_date": "TEXT",
            }
            for name, sql_type in additions.items():
                if name not in existing:
                    con.execute(f"ALTER TABLE cases ADD COLUMN {name} {sql_type}")
            con.commit()

    # ------------------------------------------------------------------
    # Barra de investigación con metadatos
    # ------------------------------------------------------------------
    def _install_database_bar(self):
        self._ensure_metadata_vars()

        wrapper = ttk.Frame(self, padding=(10, 4))
        try:
            wrapper.pack(fill=tk.X, before=self.body_panes)
        except Exception:
            wrapper.pack(fill=tk.X)

        top = ttk.Frame(wrapper)
        top.pack(fill=tk.X)
        ttk.Label(top, text="Base de investigación", style="Section.TLabel").pack(side=tk.LEFT, padx=(0, 8))
        self.db_counter = ttk.Label(top, text="0 / 103 casos", style="Muted.TLabel")
        self.db_counter.pack(side=tk.LEFT, padx=(0, 14))
        self.mode_label = ttk.Label(top, text="Modo: Ambos", style="Muted.TLabel")
        self.mode_label.pack(side=tk.LEFT, padx=(0, 14))

        ttk.Button(top, text="✓ Guardar en base", command=self.save_case_to_database, style="Mint.TButton").pack(side=tk.LEFT, padx=3)
        ttk.Button(top, text="Abrir base", command=self.open_database_browser, style="Soft.TButton").pack(side=tk.LEFT, padx=3)
        ttk.Button(top, text="Exportar CSV para Excel", command=self.export_database_csv, style="Gold.TButton").pack(side=tk.LEFT, padx=3)
        ttk.Button(top, text="Nuevo caso / análisis", command=self.new_case, style="Turquoise.TButton").pack(side=tk.LEFT, padx=3)

        meta = ttk.Frame(wrapper, padding=(0, 5, 0, 0))
        meta.pack(fill=tk.X)

        ttk.Label(meta, text="Edad:", style="Muted.TLabel").pack(side=tk.LEFT)
        ttk.Entry(meta, textvariable=self.age_years_var, width=4).pack(side=tk.LEFT, padx=(4, 2))
        ttk.Label(meta, text="años", style="Muted.TLabel").pack(side=tk.LEFT)
        ttk.Entry(meta, textvariable=self.age_months_var, width=3).pack(side=tk.LEFT, padx=(4, 2))
        ttk.Label(meta, text="meses", style="Muted.TLabel").pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(meta, text="Sexo:", style="Muted.TLabel").pack(side=tk.LEFT)
        ttk.Combobox(meta, textvariable=self.sex_var, values=SEX_OPTIONS, state="readonly", width=13).pack(side=tk.LEFT, padx=(4, 10))

        ttk.Label(meta, text="Clínica:", style="Muted.TLabel").pack(side=tk.LEFT)
        ttk.Combobox(meta, textvariable=self.clinic_var, values=CLINICS, state="readonly", width=17).pack(side=tk.LEFT, padx=(4, 10))

        ttk.Label(meta, text="Fecha RX:", style="Muted.TLabel").pack(side=tk.LEFT)
        ttk.Entry(meta, textvariable=self.radiograph_date_var, width=12).pack(side=tk.LEFT, padx=(4, 4))
        ttk.Label(meta, text="AAAA-MM-DD", style="Muted.TLabel").pack(side=tk.LEFT)

    # ------------------------------------------------------------------
    # Protección contra sustituir por accidente la radiografía de un caso activo
    # ------------------------------------------------------------------
    def open_image(self):
        if self.original is not None:
            messagebox.showwarning(
                "Caso activo protegido",
                "Ya hay una radiografía cargada en el caso actual.\n\n"
                "Para evitar sobrescribir por accidente otro paciente, YomCeph no reemplazará la imagen desde 'Abrir radiografía'.\n\n"
                "Guarde el caso actual y use 'Nuevo caso / análisis' antes de cargar la siguiente radiografía."
            )
            return
        return super().open_image()

    # ------------------------------------------------------------------
    # Guardado con metadatos
    # ------------------------------------------------------------------
    def save_case_to_database(self):
        case_id = self.case_id.get().strip()
        if not case_id:
            messagebox.showwarning("Base de datos", "Escriba primero el número o identificador del caso.")
            return
        if not self.original:
            messagebox.showwarning("Base de datos", "Abra la radiografía del caso antes de guardarlo.")
            return

        try:
            metadata = self._validated_metadata()
        except ValueError as exc:
            messagebox.showwarning("Datos del caso", str(exc))
            return

        r = self.calculate_values()
        now = datetime.now().isoformat(timespec="seconds")
        stored_image = self._copy_case_image(case_id)
        points_json = json.dumps(self.points, ensure_ascii=False)

        with sqlite3.connect(self._db_path) as con:
            exists = con.execute("SELECT 1 FROM cases WHERE case_id=?", (case_id,)).fetchone() is not None
            if exists:
                ok = messagebox.askyesno(
                    "Actualizar caso",
                    f"El caso {case_id} ya existe.\n\n¿Desea actualizar sus puntos, resultados y datos del paciente?"
                )
                if not ok:
                    return
                created = con.execute("SELECT created_at FROM cases WHERE case_id=?", (case_id,)).fetchone()[0]
            else:
                created = now

            con.execute("""
                INSERT INTO cases(
                    case_id, analysis_mode, image_path, stored_image_path, face_direction,
                    mm_per_pixel, points_json, created_at, updated_at,
                    age_years, age_months, sex, clinic, radiograph_date
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(case_id) DO UPDATE SET
                    analysis_mode=excluded.analysis_mode,
                    image_path=excluded.image_path,
                    stored_image_path=excluded.stored_image_path,
                    face_direction=excluded.face_direction,
                    mm_per_pixel=excluded.mm_per_pixel,
                    points_json=excluded.points_json,
                    updated_at=excluded.updated_at,
                    age_years=excluded.age_years,
                    age_months=excluded.age_months,
                    sex=excluded.sex,
                    clinic=excluded.clinic,
                    radiograph_date=excluded.radiograph_date
            """, (
                case_id, self.analysis_mode, self.image_path or "", stored_image or "",
                self.face_direction.get(), self.mm_per_pixel, points_json, created, now,
                metadata["age_years"], metadata["age_months"], metadata["sex"],
                metadata["clinic"], metadata["radiograph_date"],
            ))

            con.execute("DELETE FROM measurements WHERE case_id=?", (case_id,))
            for key in self._active_measure_order():
                value = r.get(key)
                if not self._finite(value):
                    continue
                unit = self._measurement_unit(key)
                norm = sd = diff = None
                diagnosis = self._diagnosis_for_result(key, value, r)
                if key in v11db.STEINER_PROTOCOL:
                    _, dx, diff, norm, sd, unit = self._protocol_diagnosis(key, value)
                    diagnosis = dx
                con.execute("""
                    INSERT INTO measurements(case_id, name, value, unit, norm, sd, difference, diagnosis)
                    VALUES(?,?,?,?,?,?,?,?)
                """, (case_id, key, float(value), unit, norm, sd, diff, diagnosis))
            con.commit()

        self._backup_database()
        self.results_cache = r
        self._update_db_counter()
        self.status.config(text=f"✓ Caso {case_id} guardado permanentemente en la base de investigación.")
        messagebox.showinfo(
            "Base de datos",
            f"Caso {case_id} guardado.\n\nEdad, sexo, clínica y fecha de radiografía quedaron asociados al mismo registro."
        )

    def load_case_from_database(self, case_id):
        super().load_case_from_database(case_id)
        self._ensure_metadata_vars()
        with sqlite3.connect(self._db_path) as con:
            row = con.execute("""
                SELECT age_years, age_months, sex, clinic, radiograph_date
                FROM cases WHERE case_id=?
            """, (case_id,)).fetchone()
        if row:
            years, months, sex, clinic, rx_date = row
            self.age_years_var.set("" if years is None else str(years))
            self.age_months_var.set("" if months is None else str(months))
            self.sex_var.set(sex or "")
            self.clinic_var.set(clinic or "")
            self.radiograph_date_var.set(rx_date or "")

    # ------------------------------------------------------------------
    # CSV para Excel: metadatos + celdas vacías para valores no calculables
    # ------------------------------------------------------------------
    def export_database_csv(self):
        path = filedialog.asksaveasfilename(
            title="Exportar base para Excel",
            defaultextension=".csv",
            initialfile="YomCeph_base_103_casos.csv",
            filetypes=[("CSV compatible con Excel", "*.csv")],
        )
        if not path:
            return

        all_keys = []
        for key in v11db.STEINER_ORDER + v11db.POSTURE_ORDER:
            if key not in all_keys:
                all_keys.append(key)

        with sqlite3.connect(self._db_path) as con:
            cases = con.execute("""
                SELECT case_id, age_years, age_months, sex, clinic, radiograph_date,
                       analysis_mode, updated_at
                FROM cases
                ORDER BY case_id
            """).fetchall()
            data = {}
            for case_id, name, value, diagnosis in con.execute(
                "SELECT case_id, name, value, diagnosis FROM measurements"
            ):
                data.setdefault(case_id, {})[name] = (value, diagnosis or "")

        headers = [
            "Caso", "Edad años", "Edad meses", "Edad decimal (años)",
            "Sexo", "Clínica", "Fecha radiografía", "Tipo de análisis", "Última actualización"
        ]
        for key in all_keys:
            display = "Profundidad cervical" if key == "Profundidad cervical (mm)" else key
            headers.extend([display, display + " - Diagnóstico"])

        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            for case_id, years, months, sex, clinic, rx_date, mode, updated in cases:
                if years is None:
                    age_decimal = ""
                else:
                    age_decimal = round(float(years) + float(months or 0) / 12.0, 4)
                row = [
                    case_id,
                    "" if years is None else years,
                    "" if months is None else months,
                    age_decimal,
                    sex or "",
                    clinic or "",
                    rx_date or "",
                    mode,
                    updated,
                ]
                measures = data.get(case_id, {})
                for key in all_keys:
                    if key in measures:
                        value, diagnosis = measures[key]
                        row.extend([value, diagnosis])
                    else:
                        row.extend(["", ""])
                writer.writerow(row)

        self.status.config(text=f"Base completa exportada: {os.path.basename(path)}")
        messagebox.showinfo(
            "Exportación",
            f"Base exportada correctamente.\n\nCasos: {len(cases)}\nArchivo: {path}"
        )

    # ------------------------------------------------------------------
    # Nuevo caso: limpia identidad, imagen, puntos, calibración y metadatos
    # ------------------------------------------------------------------
    def new_case(self):
        if self.original is not None or self.points or self.case_id.get().strip():
            if not messagebox.askyesno(
                "Nuevo caso",
                "¿Iniciar un nuevo caso?\n\nSi hizo cambios en el caso actual, guárdelo primero en la base de datos."
            ):
                return

        self.image_path = None
        self.original = None
        self.points = {}
        self.results_cache = {}
        self.mm_per_pixel = None
        self.calibration_points = []
        self.case_id.set("")
        self._clear_metadata()
        self.cal_label.config(text="Sin calibración")
        self.redraw()
        self.choose_analysis_mode(startup=False)
        self.status.config(text="Nuevo caso: capture los datos y abra la radiografía correspondiente.")


if __name__ == "__main__":
    ui.enable_dpi_awareness()
    app = ResearchMetadataYomCeph()
    app.mainloop()
