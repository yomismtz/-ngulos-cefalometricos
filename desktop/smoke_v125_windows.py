"""Smoke test Windows/Tk para el flujo de investigación v0.12.5."""

import os
import shutil
import sqlite3
import tempfile
import tkinter as tk
from tkinter import messagebox

_TEMP_DATA = tempfile.mkdtemp(prefix="yomceph-v125-smoke-")
os.environ["LOCALAPPDATA"] = _TEMP_DATA

import yomceph_desktop_hidpi as ui
import yomceph_scientific_catalog as catalog
from yomceph_desktop_v125_research_flow import APP_VERSION, AUTO_START, YomCephV125ResearchFlow


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
    old_info = messagebox.showinfo
    old_warning = messagebox.showwarning
    old_error = messagebox.showerror
    messagebox.showinfo = lambda *a, **k: None
    messagebox.showwarning = lambda *a, **k: None
    messagebox.showerror = lambda *a, **k: None
    try:
        app = YomCephV125ResearchFlow()
        app.withdraw()
        app.update()
        _destroy_toplevels(app)

        assert APP_VERSION == "0.12.5"
        assert "v0.12.5" in app.title(), app.title()
        for aid in ("tweed", "mcnamara", "airway", "rocabado", "downs"):
            assert catalog.ANALYSES[aid]["status"] == catalog.STATUS_ACTIVE

        study_id = app._save_study(
            {
                "name": "Prueba flujo posterior al trazado",
                "target_n": 10,
                "allow_target_increase": True,
                "age_min": 6,
                "age_max": 15,
                "inclusion": "",
                "exclusion": "",
                "country": "México",
                "institution": "",
                "group_fields": [{"name": "Grupo", "options": ["Caso", "Control"]}],
                "analyses": ["steiner", "tweed"],
                "measurements": ["SNA", "Tweed · FMA"],
                "steiner_reference": "none",
            }
        )
        with sqlite3.connect(app._db_path) as con:
            row = con.execute(
                "SELECT inclusion_criteria,exclusion_criteria FROM research_studies WHERE study_id=?",
                (study_id,),
            ).fetchone()
        assert row and AUTO_START in row[0] and AUTO_START in row[1]
        assert "México" in row[0]

        _destroy_toplevels(app)
        app._activate_study(study_id)
        app.update_idletasks()
        dialogs = [c for c in app.winfo_children() if isinstance(c, tk.Toplevel)]
        assert dialogs == [], "Activar investigación no debe abrir Datos del caso"
        assert app.workflow_type == "research"
        assert "radiografía" in app.status.cget("text").casefold()
        assert app.primary_save_button.cget("text") == "✓ Finalizar"

        # Nuevo caso tampoco debe forzar la ficha antes de trazar.
        app.next_case()
        app.update_idletasks()
        dialogs = [c for c in app.winfo_children() if isinstance(c, tk.Toplevel)]
        assert dialogs == [], "Nuevo caso de investigación no debe abrir ficha automáticamente"

        print("YomCeph v0.12.5 research-flow Windows UI smoke test: OK")
    finally:
        messagebox.showinfo = old_info
        messagebox.showwarning = old_warning
        messagebox.showerror = old_error
        if app is not None:
            try:
                app.destroy()
            except tk.TclError:
                pass
        shutil.rmtree(_TEMP_DATA, ignore_errors=True)


if __name__ == "__main__":
    main()
