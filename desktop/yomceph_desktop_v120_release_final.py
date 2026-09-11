import sqlite3
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, simpledialog

import yomceph_desktop_hidpi as ui
from yomceph_desktop_v120_release import YomCephV120Release
from yomceph_v120_geometry import legacy_active_angles

APP_VERSION = "0.12.0"
MAX_RESEARCH_CASES = 1000


class YomCephV120ReleaseFinal(YomCephV120Release):
    """Entrada final de la candidata pública v0.12.

    La cadena histórica todavía contiene ``closest_supplement`` para abrir
    proyectos creados con versiones anteriores. Esta clase reemplaza, antes de
    mostrar o persistir resultados de v0.12, todas las mediciones activas que lo
    usaban por construcciones geométricas explícitas e independientes de normas.
    """

    def _init_database(self):
        super()._init_database()
        with sqlite3.connect(self._db_path) as con:
            con.execute(
                """UPDATE research_studies
                   SET steiner_reference='none'
                   WHERE steiner_reference='legacy_imported'
                     AND study_id NOT GLOB 'investigacion_importada*'"""
            )
            con.execute(
                """UPDATE cases
                   SET steiner_reference='none'
                   WHERE steiner_reference='legacy_imported'
                     AND (research_study_id IS NULL
                          OR research_study_id NOT GLOB 'investigacion_importada*')"""
            )
            con.commit()

    def _install_database_bar(self):
        super()._install_database_bar()
        try:
            for child in self.universal_wrapper.winfo_children():
                if str(child.cget("text")) != "Más ▾":
                    continue
                menu = self.nametowidget(str(child.cget("menu")))
                menu.add_separator()
                menu.add_checkbutton(
                    label="Alto contraste",
                    variable=self.high_contrast_var,
                    command=self._apply_high_contrast,
                )
                break
        except Exception:
            pass

    def calculate_values(self):
        values = super().calculate_values()
        values.update(legacy_active_angles(self.points))
        return values

    def _ensure_research_capacity(self, local_case_id):
        """Evita rebasar silenciosamente la muestra planeada.

        Actualizar un caso ya incluido no consume una plaza. Una ampliación
        autorizada incrementa la versión del protocolo para dejar trazabilidad.
        """
        if self.workflow_type != "research" or not self.current_study_id or not self.current_study:
            return True
        status, _reason = self._evaluate_eligibility()
        if status != "eligible":
            return True

        storage_id = self._storage_case_id(local_case_id)
        with sqlite3.connect(self._db_path) as con:
            already_included = con.execute(
                """SELECT 1 FROM cases
                   WHERE case_id=? AND research_study_id=? AND eligibility_status='eligible'""",
                (storage_id, self.current_study_id),
            ).fetchone() is not None
            if already_included:
                return True
            included = con.execute(
                """SELECT COUNT(*) FROM cases
                   WHERE research_study_id=? AND eligibility_status='eligible'""",
                (self.current_study_id,),
            ).fetchone()[0]

        target = int(self.current_study.get("target_n") or 0)
        if included < target:
            return True

        if included >= MAX_RESEARCH_CASES or target >= MAX_RESEARCH_CASES:
            messagebox.showwarning(
                "Capacidad de investigación",
                f"YomCeph v0.12 admite hasta {MAX_RESEARCH_CASES} casos planeados por investigación. "
                "No se puede ampliar más esta muestra."
            )
            return False

        if not bool(self.current_study.get("allow_target_increase")):
            messagebox.showwarning(
                "Muestra completa",
                f"La investigación ya alcanzó la muestra planeada de {target} casos incluidos.\n\n"
                "El protocolo no permite ampliarla. Este caso no se guardará como incluido."
            )
            return False

        new_target = simpledialog.askinteger(
            "Ampliar muestra",
            f"La investigación ya alcanzó {included}/{target} casos incluidos.\n\n"
            "Para incluir este paciente, registre primero el nuevo tamaño planeado de muestra:",
            minvalue=included + 1,
            maxvalue=MAX_RESEARCH_CASES,
            parent=self,
        )
        if not new_target:
            return False
        now = datetime.now().isoformat(timespec="seconds")
        with sqlite3.connect(self._db_path) as con:
            con.execute(
                "UPDATE research_studies SET target_n=?, protocol_version=protocol_version+1, updated_at=? WHERE study_id=?",
                (new_target, now, self.current_study_id),
            )
            con.commit()
        self.current_study = self._get_study(self.current_study_id)
        self.study_target_var.set(str(new_target))
        self._update_db_counter()
        messagebox.showinfo(
            "Muestra ampliada",
            f"El tamaño planeado quedó registrado como {new_target}. La versión del protocolo se incrementó para mantener trazabilidad."
        )
        return True

    def save_case_to_database(self):
        local = self.case_id.get().strip()
        if local and not self._ensure_research_capacity(local):
            return
        return super().save_case_to_database()


if __name__ == "__main__":
    ui.enable_dpi_awareness()
    app = YomCephV120ReleaseFinal()
    app.mainloop()
