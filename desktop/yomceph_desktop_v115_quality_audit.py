import csv
import json
import math
import os
import sqlite3
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, simpledialog

from PIL import Image, ImageOps

import yomceph_desktop as core
import yomceph_desktop_hidpi as ui
import yomceph_desktop_v11_database as v11db
import yomceph_desktop_v114_research_metadata as v114

APP_VERSION = "0.11.5"


class QualityAuditYomCeph(v114.ResearchMetadataYomCeph):
    """v0.11.5: control de calidad, trazabilidad de calibración e historial."""

    def __init__(self):
        self.calibration_real_mm = None
        self._case_saved = False
        self._suspend_dirty = False
        self._qc_warnings = []
        self._qc_after_id = None
        self._calibration_backup = None
        super().__init__()
        self.title("YomCeph Desktop · Investigación · Control de calidad · v0.11.5")
        self.status.config(
            text="v0.11.5 · QC automático · calibración trazable · historial de cambios"
        )
        self._refresh_quality_control()
        self._refresh_case_state()

    def _init_database(self):
        super()._init_database()
        with sqlite3.connect(self._db_path) as con:
            existing = {row[1] for row in con.execute("PRAGMA table_info(cases)")}
            additions = {
                "calibration_points_json": "TEXT",
                "calibration_real_mm": "REAL",
            }
            for name, sql_type in additions.items():
                if name not in existing:
                    con.execute(f"ALTER TABLE cases ADD COLUMN {name} {sql_type}")

            con.execute("""
                CREATE TABLE IF NOT EXISTS case_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    case_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    changed_at TEXT NOT NULL,
                    landmark_count INTEGER NOT NULL,
                    qc_warning_count INTEGER NOT NULL DEFAULT 0,
                    analysis_mode TEXT,
                    details TEXT,
                    FOREIGN KEY(case_id) REFERENCES cases(case_id) ON DELETE CASCADE
                )
            """)
            con.commit()

    def _install_database_bar(self):
        super()._install_database_bar()

        self.case_state_frame = tk.Frame(self, bg="#EEF2F6", padx=10, pady=4)
        try:
            self.case_state_frame.pack(fill=tk.X, before=self.body_panes)
        except Exception:
            self.case_state_frame.pack(fill=tk.X)

        self.case_state_label = tk.Label(
            self.case_state_frame,
            text="CASO — · 0/0 puntos · SIN CALIBRAR · NUEVO",
            bg="#EEF2F6",
            fg="#233044",
            font=("Segoe UI", 10, "bold"),
            anchor="w",
        )
        self.case_state_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.qc_button = tk.Button(
            self.case_state_frame,
            text="QC pendiente",
            command=self.show_quality_control,
            relief=tk.FLAT,
            padx=10,
            pady=2,
            cursor="hand2",
        )
        self.qc_button.pack(side=tk.RIGHT)

        if not getattr(self, "_state_traces_installed", False):
            self._state_traces_installed = True
            self.case_id.trace_add("write", self._tracked_field_changed)
            self.face_direction.trace_add("write", self._tracked_field_changed)
            for var in (
                self.age_years_var,
                self.age_months_var,
                self.sex_var,
                self.clinic_var,
                self.radiograph_date_var,
            ):
                var.trace_add("write", self._tracked_field_changed)

    def _tracked_field_changed(self, *_args):
        if self._suspend_dirty:
            return
        if self.original is not None or self.points or self.case_id.get().strip():
            self._mark_dirty(schedule_qc=True)
        else:
            self._refresh_case_state()

    def _mark_dirty(self, schedule_qc=True):
        if self._suspend_dirty:
            return
        self._case_saved = False
        self._refresh_case_state()
        if schedule_qc:
            self._schedule_quality_control()

    def _schedule_quality_control(self):
        try:
            if self._qc_after_id is not None:
                self.after_cancel(self._qc_after_id)
            self._qc_after_id = self.after(180, self._refresh_quality_control)
        except Exception:
            self._qc_after_id = None

    @staticmethod
    def _display_case_id(case_id):
        text = str(case_id or "").strip()
        if not text:
            return "—"
        return text.zfill(3) if text.isdigit() else text

    def _calibration_is_traceable(self):
        return bool(
            self.mm_per_pixel
            and self.calibration_real_mm
            and len(self.calibration_points) == 2
        )

    def _refresh_case_state(self):
        if not hasattr(self, "case_state_label"):
            return

        case_id = self._display_case_id(self.case_id.get())
        active = list(getattr(self, "active_point_order", []) or [])
        placed = sum(1 for key in active if key in self.points)
        total = len(active)

        if self._calibration_is_traceable():
            calibration = "CALIBRADO"
        elif self.mm_per_pixel:
            calibration = "CALIBRACIÓN LEGADA"
        else:
            calibration = "SIN CALIBRAR"

        has_case_content = bool(self.original is not None or self.points or self.case_id.get().strip())
        if self._case_saved and has_case_content:
            save_state = "GUARDADO"
        elif has_case_content:
            save_state = "SIN GUARDAR"
        else:
            save_state = "NUEVO"

        qc_count = len(self._qc_warnings)
        if self.original is None:
            qc_text = "QC pendiente"
        else:
            qc_text = f"⚠ QC: {qc_count}" if qc_count else "✓ QC"
        text = (
            f"CASO {case_id} · {placed}/{total} puntos · "
            f"{calibration} · {save_state} · {qc_text}"
        )

        if qc_count:
            bg, fg = "#FFF3BF", "#6B5200"
            button_bg, button_fg = "#FFD966", "#5A4300"
        elif self._case_saved and has_case_content:
            bg, fg = "#E9F7EF", "#145A32"
            button_bg, button_fg = "#CDEED8", "#145A32"
        else:
            bg, fg = "#EEF2F6", "#233044"
            button_bg, button_fg = "#DCE3EA", "#233044"

        self.case_state_frame.configure(bg=bg)
        self.case_state_label.configure(text=text, bg=bg, fg=fg)
        qc_button_text = (
            "QC pendiente" if self.original is None
            else (f"⚠ Ver QC ({qc_count})" if qc_count else "✓ QC sin alertas")
        )
        self.qc_button.configure(
            text=qc_button_text,
            bg=button_bg,
            fg=button_fg,
            activebackground=button_bg,
            activeforeground=button_fg,
        )

    def _quality_control_warnings(self):
        warnings = []
        if self.original is None:
            return warnings

        active = list(getattr(self, "active_point_order", []) or [])
        placed = [(key, self.points[key]) for key in active if key in self.points]

        width, height = self.original.size
        diagonal = math.hypot(width, height)
        near_threshold = max(4.0, min(12.0, diagonal * 0.002))

        for key, point in placed:
            try:
                x, y = float(point[0]), float(point[1])
            except Exception:
                warnings.append(f"{key}: coordenada inválida o no numérica.")
                continue
            if x < 0 or y < 0 or x >= width or y >= height:
                warnings.append(f"{key}: el landmark quedó fuera de los límites de la radiografía.")

        close_pairs = 0
        for i in range(len(placed)):
            key_a, point_a = placed[i]
            for j in range(i + 1, len(placed)):
                key_b, point_b = placed[j]
                try:
                    distance_px = core.dist(point_a, point_b)
                except Exception:
                    continue
                if distance_px <= 1.5:
                    warnings.append(
                        f"{key_a} y {key_b}: puntos prácticamente duplicados "
                        f"({distance_px:.1f} px)."
                    )
                    close_pairs += 1
                elif distance_px <= near_threshold:
                    warnings.append(
                        f"{key_a} y {key_b}: puntos extremadamente próximos "
                        f"({distance_px:.1f} px; umbral QC {near_threshold:.1f} px)."
                    )
                    close_pairs += 1
                if close_pairs >= 8:
                    warnings.append("Hay más pares de landmarks extremadamente próximos; revise el trazado completo.")
                    break
            if close_pairs >= 8:
                break

        try:
            linear_keys = [
                key for key in self._active_measure_order()
                if self._measurement_unit(key) == "mm"
            ]
        except Exception:
            linear_keys = []

        if linear_keys and not self.mm_per_pixel:
            warnings.append(
                "Sin calibración: las mediciones lineales en mm quedarán sin calcular/interpretar."
            )
        elif self.mm_per_pixel:
            if not self._calibration_is_traceable():
                warnings.append(
                    "La escala mm/píxel existe, pero faltan los dos puntos o la longitud real de calibración. "
                    "Es una calibración legada/incompleta; recalibre para dejar trazabilidad completa."
                )
            else:
                pixel_distance = core.dist(*self.calibration_points)
                if pixel_distance <= 0:
                    warnings.append("Calibración inválida: los dos puntos de referencia coinciden.")
                else:
                    reconstructed = float(self.calibration_real_mm) / pixel_distance
                    if abs(reconstructed - float(self.mm_per_pixel)) > max(1e-9, abs(self.mm_per_pixel) * 0.005):
                        warnings.append(
                            "Incoherencia interna de calibración: mm/píxel no coincide con "
                            "la longitud real y los dos puntos guardados."
                        )

        try:
            results = self.calculate_values()
        except Exception as exc:
            warnings.append(f"No se pudo ejecutar el control geométrico: {exc}")
            return warnings

        if all(key in results and self._finite(results[key]) for key in ("SNA", "SNB", "ANB")):
            expected_anb = results["SNA"] - results["SNB"]
            if abs(results["ANB"] - expected_anb) > 0.05:
                warnings.append(
                    f"Incoherencia ANB: {results['ANB']:.2f}° no coincide con "
                    f"SNA − SNB ({expected_anb:.2f}°)."
                )
            if abs(results["ANB"]) > 45:
                warnings.append(
                    f"ANB geométricamente extremo ({results['ANB']:.2f}°); revise N, A y B."
                )

        try:
            measure_order = self._active_measure_order()
        except Exception:
            measure_order = []

        for key in measure_order:
            if key == "ANB" or key not in results:
                continue
            if not self._finite(results[key]):
                warnings.append(f"{key}: resultado no finito; revise los puntos que definen la medición.")
                continue
            try:
                unit = self._measurement_unit(key)
            except Exception:
                unit = ""
            if unit != "°":
                continue
            value = float(results[key])
            if value < 0 or value > 180:
                warnings.append(
                    f"{key}: ángulo fuera del intervalo geométrico 0–180° ({value:.2f}°)."
                )
            elif value <= 1.0 or value >= 179.0:
                warnings.append(
                    f"{key}: ángulo casi degenerado ({value:.2f}°); revise los landmarks/planos que lo forman."
                )

        return warnings

    def _refresh_quality_control(self):
        self._qc_after_id = None
        self._qc_warnings = self._quality_control_warnings()
        self._refresh_case_state()
        return list(self._qc_warnings)

    def show_quality_control(self):
        warnings = self._refresh_quality_control()
        if not self.original:
            messagebox.showinfo("Control de calidad", "Abra una radiografía para ejecutar el control de calidad.")
            return
        if not warnings:
            messagebox.showinfo(
                "Control de calidad",
                "No se detectaron alertas geométricas automáticas.\n\n"
                "Este control no sustituye la revisión del observador."
            )
            return
        messagebox.showwarning(
            "Control de calidad · advertencias",
            "YomCeph no ha corregido ningún dato. Revise:\n\n" +
            "\n".join(f"• {item}" for item in warnings)
        )

    def start_calibration(self):
        if not self.original:
            messagebox.showinfo("Calibración", "Primero abra una radiografía.")
            return
        self._calibration_backup = (
            self.mm_per_pixel,
            list(self.calibration_points),
            self.calibration_real_mm,
        )
        self.calibration_points = []
        self.calibrating = True
        self.status.config(
            text="Calibración: marque dos extremos de una referencia de longitud conocida."
        )
        self._refresh_case_state()

    def _restore_calibration_backup(self):
        if self._calibration_backup is None:
            return
        self.mm_per_pixel, points, self.calibration_real_mm = self._calibration_backup
        self.calibration_points = list(points)
        self._calibration_backup = None
        self.cal_label.config(
            text=(f"Calibrado: {self.mm_per_pixel:.5f} mm/píxel" if self.mm_per_pixel else "Sin calibración")
        )
        self.redraw()
        self._refresh_quality_control()

    def finish_calibration(self):
        self.calibrating = False
        if len(self.calibration_points) != 2:
            self._restore_calibration_backup()
            return

        pixel_distance = core.dist(*self.calibration_points)
        if pixel_distance < 5:
            messagebox.showwarning(
                "Calibración", "Los puntos de calibración están demasiado juntos. Se conserva la calibración anterior."
            )
            self._restore_calibration_backup()
            return

        real_mm = simpledialog.askfloat(
            "Calibración",
            "Longitud real entre los dos puntos (mm):",
            minvalue=0.1,
        )
        if not real_mm:
            self._restore_calibration_backup()
            return

        self.calibration_real_mm = float(real_mm)
        self.mm_per_pixel = self.calibration_real_mm / pixel_distance
        self._calibration_backup = None
        self.cal_label.config(text=f"Calibrado: {self.mm_per_pixel:.5f} mm/píxel")
        self.status.config(
            text=f"Calibración trazable guardada: {real_mm:g} mm / {pixel_distance:.2f} px."
        )
        self.redraw()
        self._mark_dirty(schedule_qc=True)

    def canvas_left_down(self, event):
        was_calibrating = bool(self.calibrating)
        before = dict(self.points)
        result = super().canvas_left_down(event)
        if not was_calibrating and self.points != before:
            self._case_saved = False
            self._refresh_case_state()
        return result

    def canvas_left_up(self, event):
        result = super().canvas_left_up(event)
        if self.original is not None:
            self._mark_dirty(schedule_qc=True)
        return result

    def delete_selected(self):
        before = dict(self.points)
        result = super().delete_selected()
        if self.points != before:
            self._mark_dirty(schedule_qc=True)
        return result

    def delete_all(self):
        before = dict(self.points)
        result = super().delete_all()
        if self.points != before:
            self._mark_dirty(schedule_qc=True)
        return result

    def apply_analysis_mode(self, mode):
        result = super().apply_analysis_mode(mode)
        if hasattr(self, "case_state_label"):
            self._refresh_case_state()
            self._schedule_quality_control()
        return result

    def calculate(self):
        result = super().calculate()
        warnings = self._refresh_quality_control()
        if warnings:
            self.status.config(
                text=f"Análisis calculado · ⚠ QC detectó {len(warnings)} advertencia(s). Pulse 'Ver QC'."
            )
        return result

    def open_image(self):
        previous = self.original
        result = super().open_image()
        if previous is None and self.original is not None:
            self.calibration_real_mm = None
            self._case_saved = False
            self._refresh_quality_control()
        return result

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

        with sqlite3.connect(self._db_path) as con:
            previous = con.execute(
                "SELECT created_at FROM cases WHERE case_id=?", (case_id,)
            ).fetchone()
        exists = previous is not None

        if exists and self._loaded_case_id != case_id:
            messagebox.showerror(
                "Número de caso ya utilizado",
                f"El caso {case_id} ya existe en la base.\n\n"
                "Por seguridad, un caso nuevo NO puede sobrescribir un identificador existente. "
                "Si desea corregir ese paciente, ábralo primero desde 'Abrir base'."
            )
            return

        if exists:
            ok = messagebox.askyesno(
                "Actualizar caso existente",
                f"Está editando el caso {case_id}, abierto previamente desde la base.\n\n"
                "¿Desea guardar las correcciones?"
            )
            if not ok:
                return

        warnings = self._refresh_quality_control()
        if warnings:
            preview = "\n".join(f"• {item}" for item in warnings[:10])
            if len(warnings) > 10:
                preview += f"\n• … y {len(warnings) - 10} advertencia(s) adicional(es)."
            proceed = messagebox.askyesno(
                "⚠ Control de calidad",
                "YomCeph detectó advertencias. No se ha corregido ningún valor.\n\n"
                + preview
                + "\n\n¿Desea guardar el caso de todas formas?"
            )
            if not proceed:
                return

        results = self.calculate_values()
        now = datetime.now().isoformat(timespec="seconds")
        created = previous[0] if exists else now
        points_json = json.dumps(self.points, ensure_ascii=False)
        calibration_points_json = json.dumps(self.calibration_points, ensure_ascii=False)
        stored_image = self._copy_case_image(case_id)
        action = "actualizado" if exists else "creado"

        active_total = len(getattr(self, "active_point_order", []) or [])
        active_placed = sum(
            1 for key in (getattr(self, "active_point_order", []) or []) if key in self.points
        )
        history_details = json.dumps(
            {
                "active_landmarks": f"{active_placed}/{active_total}",
                "calibrated": bool(self.mm_per_pixel),
                "calibration_traceable": self._calibration_is_traceable(),
                "mm_per_pixel": self.mm_per_pixel,
                "calibration_real_mm": self.calibration_real_mm,
                "qc_warnings": warnings,
            },
            ensure_ascii=False,
        )

        with sqlite3.connect(self._db_path) as con:
            con.execute("PRAGMA foreign_keys=ON")
            con.execute("""
                INSERT INTO cases(
                    case_id, analysis_mode, image_path, stored_image_path, face_direction,
                    mm_per_pixel, points_json, created_at, updated_at,
                    age_years, age_months, sex, clinic, radiograph_date,
                    calibration_points_json, calibration_real_mm
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
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
                    radiograph_date=excluded.radiograph_date,
                    calibration_points_json=excluded.calibration_points_json,
                    calibration_real_mm=excluded.calibration_real_mm
            """, (
                case_id, self.analysis_mode, self.image_path or "", stored_image or "",
                self.face_direction.get(), self.mm_per_pixel, points_json, created, now,
                metadata["age_years"], metadata["age_months"], metadata["sex"],
                metadata["clinic"], metadata["radiograph_date"],
                calibration_points_json, self.calibration_real_mm,
            ))

            con.execute("DELETE FROM measurements WHERE case_id=?", (case_id,))
            for key in self._active_measure_order():
                value = results.get(key)
                if not self._finite(value):
                    continue
                unit = self._measurement_unit(key)
                norm = sd = diff = None
                diagnosis = self._diagnosis_for_result(key, value, results)
                if key in v11db.STEINER_PROTOCOL:
                    _, dx, diff, norm, sd, unit = self._protocol_diagnosis(key, value)
                    diagnosis = dx
                con.execute("""
                    INSERT INTO measurements(case_id, name, value, unit, norm, sd, difference, diagnosis)
                    VALUES(?,?,?,?,?,?,?,?)
                """, (case_id, key, float(value), unit, norm, sd, diff, diagnosis))

            con.execute("""
                INSERT INTO case_history(
                    case_id, action, changed_at, landmark_count,
                    qc_warning_count, analysis_mode, details
                ) VALUES(?,?,?,?,?,?,?)
            """, (
                case_id, action, now, len(self.points), len(warnings),
                self.analysis_mode, history_details,
            ))
            con.commit()

        self._loaded_case_id = case_id
        self._case_saved = True
        self._backup_database()
        self.results_cache = results
        self._update_db_counter()
        self._refresh_case_state()
        self.status.config(
            text=f"✓ Caso {case_id} {action} · historial registrado · QC: {len(warnings)} advertencia(s)."
        )
        messagebox.showinfo(
            "Base de datos",
            f"Caso {case_id} {action} correctamente.\n\n"
            f"Landmarks: {active_placed}/{active_total}\n"
            f"Calibración trazable: {'sí' if self._calibration_is_traceable() else 'no'}\n"
            f"Advertencias QC: {len(warnings)}"
        )

    def load_case_from_database(self, case_id):
        self._suspend_dirty = True
        try:
            super().load_case_from_database(case_id)
            with sqlite3.connect(self._db_path) as con:
                row = con.execute("""
                    SELECT calibration_points_json, calibration_real_mm
                    FROM cases WHERE case_id=?
                """, (case_id,)).fetchone()
            if row:
                raw_points, real_mm = row
                try:
                    decoded = json.loads(raw_points or "[]")
                    self.calibration_points = [
                        tuple(point) for point in decoded
                        if isinstance(point, (list, tuple)) and len(point) == 2
                    ]
                except Exception:
                    self.calibration_points = []
                self.calibration_real_mm = real_mm
            else:
                self.calibration_points = []
                self.calibration_real_mm = None
        finally:
            self._suspend_dirty = False

        self._case_saved = True
        self._refresh_quality_control()
        self._refresh_case_state()

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
                       analysis_mode, updated_at, mm_per_pixel,
                       calibration_real_mm, calibration_points_json
                FROM cases
                ORDER BY
                    CASE
                        WHEN case_id <> '' AND case_id NOT GLOB '*[^0-9]*'
                        THEN CAST(case_id AS INTEGER)
                        ELSE 2147483647
                    END,
                    case_id COLLATE NOCASE
            """).fetchall()
            data = {}
            for db_case_id, name, value, diagnosis in con.execute(
                "SELECT case_id, name, value, diagnosis FROM measurements"
            ):
                data.setdefault(db_case_id, {})[name] = (value, diagnosis or "")

        headers = [
            "Caso", "Edad años", "Edad meses", "Edad decimal (años)",
            "Sexo", "Clínica", "Fecha radiografía", "Tipo de análisis",
            "Última actualización", "Calibración mm/píxel",
            "Referencia calibración (mm)", "Calibración P1 X", "Calibración P1 Y",
            "Calibración P2 X", "Calibración P2 Y", "Trazabilidad calibración",
        ]
        for key in all_keys:
            display = "Profundidad cervical" if key == "Profundidad cervical (mm)" else key
            headers.extend([display, display + " - Diagnóstico"])

        with open(path, "w", newline="", encoding="utf-8-sig") as handle:
            writer = csv.writer(handle)
            writer.writerow(headers)
            for (
                db_case_id, years, months, sex, clinic, rx_date, mode, updated,
                mmpp, real_mm, calibration_json,
            ) in cases:
                age_decimal = (
                    "" if years is None
                    else round(float(years) + float(months or 0) / 12.0, 4)
                )
                try:
                    calibration = json.loads(calibration_json or "[]")
                except Exception:
                    calibration = []
                p1 = calibration[0] if len(calibration) >= 1 else ("", "")
                p2 = calibration[1] if len(calibration) >= 2 else ("", "")
                traceable = "Sí" if mmpp and real_mm and len(calibration) == 2 else ("Legada/incompleta" if mmpp else "No")

                row = [
                    db_case_id,
                    "" if years is None else years,
                    "" if months is None else months,
                    age_decimal,
                    sex or "",
                    clinic or "",
                    rx_date or "",
                    mode,
                    updated,
                    "" if mmpp is None else mmpp,
                    "" if real_mm is None else real_mm,
                    p1[0], p1[1], p2[0], p2[1], traceable,
                ]

                measures = data.get(db_case_id, {})
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
            f"Base exportada correctamente.\n\nCasos: {len(cases)}\nArchivo: {path}\nOrden: numérico para identificadores 1–103."
        )

    def save_project(self):
        if not self.original or not self.image_path:
            messagebox.showinfo("Guardar", "Primero abra una radiografía.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".yomceph.json",
            filetypes=[("Proyecto YomCeph", "*.yomceph.json"), ("JSON", "*.json")],
        )
        if not path:
            return
        data = {
            "version": APP_VERSION,
            "case_id": self.case_id.get(),
            "image_path": self.image_path,
            "points": self.points,
            "mm_per_pixel": self.mm_per_pixel,
            "calibration_points": self.calibration_points,
            "calibration_real_mm": self.calibration_real_mm,
            "face_direction": self.face_direction.get(),
        }
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
        self.status.config(text=f"Proyecto guardado: {os.path.basename(path)}")

    def load_project(self):
        path = filedialog.askopenfilename(
            filetypes=[("Proyecto YomCeph", "*.json"), ("Todos", "*.*")]
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            image_path = data["image_path"]
            self.original = ImageOps.exif_transpose(Image.open(image_path)).convert("RGB")
            self.image_path = image_path
            self.points = {key: tuple(value) for key, value in data.get("points", {}).items()}
            self.mm_per_pixel = data.get("mm_per_pixel")
            self.calibration_points = [
                tuple(value) for value in data.get("calibration_points", [])
            ]
            self.calibration_real_mm = data.get("calibration_real_mm")
            self._suspend_dirty = True
            try:
                self.case_id.set(data.get("case_id", ""))
                self.face_direction.set(data.get("face_direction", "right"))
            finally:
                self._suspend_dirty = False
            self._loaded_case_id = None
            self._case_saved = False
            self.cal_label.config(
                text=(f"Calibrado: {self.mm_per_pixel:.5f} mm/píxel" if self.mm_per_pixel else "Sin calibración")
            )
            self.after(50, self.fit_image)
            self.update_point_guide()
            self._refresh_point_list_marks()
            self._refresh_quality_control()
        except Exception as exc:
            messagebox.showerror("Abrir proyecto", f"No se pudo abrir.\n\n{exc}")

    def new_case(self):
        previous_original = self.original
        previous_case = self.case_id.get().strip()
        result = super().new_case()
        cleared = self.original is None and not self.points and not self.case_id.get().strip()
        if cleared and (previous_original is not None or previous_case or self._loaded_case_id is None):
            self.calibration_real_mm = None
            self._calibration_backup = None
            self._case_saved = False
            self._qc_warnings = []
            self._refresh_case_state()
        return result


if __name__ == "__main__":
    ui.enable_dpi_awareness()
    app = QualityAuditYomCeph()
    app.mainloop()
