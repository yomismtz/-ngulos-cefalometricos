"""Smoke test de la distribución pública de YomCeph en un runner Windows.

A diferencia de pytest/py_compile, esta prueba instancia la interfaz Tk real y
fuerza las rutas de UI que han causado errores de Tcl/Tk en ejecutables.
"""

import os
import shutil
import sqlite3
import tempfile
import tkinter as tk
from tkinter import ttk

# Debe fijarse antes de crear la aplicación para no tocar datos reales del runner.
_TEMP_DATA = tempfile.mkdtemp(prefix="yomceph-smoke-")
os.environ["LOCALAPPDATA"] = _TEMP_DATA

import yomceph_desktop_hidpi as ui
from yomceph_desktop_v120_distribution import YomCephV120Distribution


def _menu_labels(app):
    for child in app.universal_wrapper.winfo_children():
        if isinstance(child, ttk.Menubutton):
            menu_name = child.cget("menu")
            if not menu_name:
                continue
            menu = app.nametowidget(str(menu_name))
            end = menu.index("end")
            if end is None:
                return []
            labels = []
            for i in range(end + 1):
                try:
                    label = menu.entrycget(i, "label")
                except tk.TclError:
                    continue
                if label:
                    labels.append(label)
            return labels
    raise AssertionError("No se encontró el menú Más ▾")


def _destroy_toplevels(app):
    for child in list(app.winfo_children()):
        if isinstance(child, tk.Toplevel):
            try:
                child.grab_release()
            except tk.TclError:
                pass
            child.destroy()


def main():
    ui.enable_dpi_awareness()
    app = None
    try:
        app = YomCephV120Distribution()
        app.withdraw()
        app.update_idletasks()

        # Regresión del crash reportado: QualityAudit configura bg/fg del botón QC.
        assert isinstance(app.qc_button, tk.Button), type(app.qc_button)
        app._refresh_case_state()
        app.update_idletasks()

        # Instalación limpia: ninguna universidad, clínica o estudio viene precargado.
        with sqlite3.connect(app._db_path) as con:
            studies = con.execute("SELECT COUNT(*) FROM research_studies").fetchone()[0]
        assert studies == 0, f"Una instalación limpia creó {studies} estudios preconfigurados"

        labels = _menu_labels(app)
        assert "Alto contraste" in labels, labels
        assert "Buscar actualizaciones" in labels, labels

        # Fuerza una segunda ruta de configuración de widgets Tk/ttk.
        app.high_contrast_var.set(True)
        app._apply_high_contrast()
        app.update_idletasks()
        app.high_contrast_var.set(False)
        app._apply_high_contrast()
        app.update_idletasks()

        # Construye las pantallas principales sin requerir interacción humana.
        app._show_workflow_home()
        app.update_idletasks()
        _destroy_toplevels(app)
        app._startup_home_shown = True

        app.open_protocol_editor(new_study=True)
        app.update_idletasks()
        _destroy_toplevels(app)

        app.open_case_data(first_time=False)
        app.update_idletasks()
        _destroy_toplevels(app)

        print("YomCeph Windows UI smoke test: OK")
    finally:
        if app is not None:
            try:
                app.destroy()
            except tk.TclError:
                pass
        shutil.rmtree(_TEMP_DATA, ignore_errors=True)


if __name__ == "__main__":
    main()
