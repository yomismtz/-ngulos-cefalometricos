import sqlite3

import yomceph_desktop_hidpi as ui
import yomceph_desktop_v11_database as v11db
import yomceph_desktop_v116 as v116
import yomceph_desktop_v120 as v120
import yomceph_desktop_v120_final as public_base

APP_VERSION = "0.12.0"
PUBLIC_STEINER_REFERENCES = {"none", "classic"}
INTERNAL_STEINER_REFERENCES = PUBLIC_STEINER_REFERENCES | {"legacy_imported"}

# El catálogo que ve la interfaz pública nunca debe sugerir afiliación con una
# universidad, escuela, clínica o investigación concreta.
v120.ANALYSES["steiner"]["summary"] = (
    "Esquelético, vertical, dental y tejidos blandos. Los valores crudos se "
    "conservan siempre; la clasificación automática puede desactivarse o usar "
    "una referencia clásica publicada identificada explícitamente."
)


class YomCephV120Release(public_base.YomCephV120Final):
    """Candidata pública auditada de YomCeph v0.12.

    Reglas críticas:
    - ninguna referencia institucional aparece como opción pública;
    - "Sin clasificación" nunca hereda normas ni diagnósticos de versiones previas;
    - una referencia histórica importada puede conservarse internamente sólo para
      reproducibilidad de bases antiguas, sin mostrarse como institución pública.
    """

    def _init_database(self):
        super()._init_database()
        with sqlite3.connect(self._db_path) as con:
            # La capa pública anterior neutralizaba el nombre del estudio importado,
            # pero también anulaba su referencia histórica. La recuperamos con un
            # identificador interno neutro para mantener reproducibilidad.
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
            from tkinter import messagebox
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
        self.selected_measure_keys = [
            key for key in study["measurements"] if key in v120.MEASUREMENTS
        ]
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
        self.status.config(
            text=f"Investigación activa: {study['name']}. Capture los datos del caso."
        )
        self.open_case_data(first_time=True)

    def load_case_from_database(self, storage_id):
        result = super().load_case_from_database(storage_id)
        # La referencia histórica sólo puede sobrevivir en investigaciones
        # importadas. Cualquier valor desconocido se degrada de forma segura a none.
        if self.steiner_reference not in INTERNAL_STEINER_REFERENCES:
            self.steiner_reference = "none"
        return result

    def _protocol_diagnosis(self, key, value):
        """Referencia Steiner explícita, nunca heredada de forma implícita.

        Esta función también es utilizada por la rutina histórica de persistencia.
        Devolver norm/sd/diff como None cuando la referencia es ``none`` impide que
        SQLite reciba silenciosamente normas antiguas aun cuando la UI muestre
        "Sin clasificación".
        """
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
            if value < lo:
                state = "DISMINUIDO"
            elif value > hi:
                state = "AUMENTADO"
            else:
                state = "EN RANGO"
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
        # Las variables Steiner no deben caer en la clasificación histórica del
        # padre cuando la persona eligió "Sin clasificación".
        if key in v11db.STEINER_PROTOCOL:
            state, _diagnosis, _diff, norm, _sd, _unit = self._protocol_diagnosis(
                key, value
            )
            return state if norm is not None else ""
        return super()._classification_for(key, value)

    def _diagnosis_for_result(self, key, value, results):
        if key in v11db.STEINER_PROTOCOL:
            _state, diagnosis, _diff, norm, _sd, _unit = self._protocol_diagnosis(
                key, value
            )
            if norm is None:
                return ""
            if self.steiner_reference == "classic":
                return diagnosis + " No sustituye el diagnóstico clínico."
            # En importaciones históricas se preserva el texto previo sólo por
            # reproducibilidad; nunca se ofrece como una opción institucional.
            return diagnosis
        return super()._diagnosis_for_result(key, value, results)

    def _diagnosis_for(self, key, value):
        # Protección adicional para rutas heredadas que llamen a _diagnosis_for.
        if key in v11db.STEINER_PROTOCOL:
            _state, diagnosis, _diff, norm, _sd, _unit = self._protocol_diagnosis(
                key, value
            )
            return diagnosis if norm is not None else ""
        return super()._diagnosis_for(key, value)


if __name__ == "__main__":
    ui.enable_dpi_awareness()
    app = YomCephV120Release()
    app.mainloop()
