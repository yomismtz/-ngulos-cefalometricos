import sqlite3
import tkinter as tk

import yomceph_desktop_hidpi as ui
from yomceph_desktop_v120_release import YomCephV120Release
from yomceph_v120_geometry import legacy_active_angles

APP_VERSION = "0.12.0"


class YomCephV120ReleaseFinal(YomCephV120Release):
    """Entrada final de la candidata pública v0.12.

    La cadena histórica todavía contiene ``closest_supplement`` para abrir
    proyectos creados con versiones anteriores. Esta clase reemplaza, antes de
    mostrar o persistir resultados de v0.12, todas las mediciones activas que lo
    usaban por construcciones geométricas explícitas e independientes de normas.
    """

    def _init_database(self):
        super()._init_database()
        # ``legacy_imported`` sólo pertenece a la migración neutral creada por
        # YomCeph. Si un usuario llama casualmente a su propio estudio
        # "Investigación importada", no debe recibir una referencia histórica.
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
        # La barra compacta deja el alto contraste en el menú en lugar de ocupar
        # espacio permanente sobre la radiografía.
        try:
            for child in self.universal_wrapper.winfo_children():
                if str(child.cget("text")) != "Más ▾":
                    continue
                menu_name = child.cget("menu")
                menu = self.nametowidget(str(menu_name))
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


if __name__ == "__main__":
    ui.enable_dpi_awareness()
    app = YomCephV120ReleaseFinal()
    app.mainloop()
