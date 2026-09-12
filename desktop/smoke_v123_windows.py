"""Smoke test real de YomCeph v0.12.3 en Windows/Tk."""

import os
import shutil
import sqlite3
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

_TEMP_DATA = tempfile.mkdtemp(prefix="yomceph-v123-smoke-")
os.environ["LOCALAPPDATA"] = _TEMP_DATA

import yomceph_desktop_hidpi as ui
from yomceph_desktop_v123_hardening import APP_VERSION, YomCephV123Hardening


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
            for index in range(end + 1):
                try:
                    label = menu.entrycget(index, "label")
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
    old_yesno = messagebox.askyesno
    old_warning = messagebox.showwarning
    old_open = filedialog.askopenfilename
    try:
        app = YomCephV123Hardening()
        app.withdraw()
        app.update_idletasks()

        assert APP_VERSION == "0.12.3"
        app._apply_language()
        assert "v0.12.3" in app.title(), app.title()
        assert isinstance(app.qc_button, tk.Button), type(app.qc_button)
        app._refresh_case_state()
        app.update_idletasks()

        with sqlite3.connect(app._db_path) as con:
            studies = con.execute("SELECT COUNT(*) FROM research_studies").fetchone()[0]
        assert studies == 0, f"La instalación limpia creó {studies} estudios"

        labels = _menu_labels(app)
        assert "Alto contraste" in labels, labels
        assert "Buscar actualizaciones" in labels, labels

        app.high_contrast_var.set(True)
        app._apply_high_contrast()
        app.update_idletasks()
        app.high_contrast_var.set(False)
        app._apply_high_contrast()
        app.update_idletasks()

        app.original = object()
        app.image_path = "radiografia-prueba.png"
        app.points = {"S": (12.0, 14.0)}
        app.case_id.set("CASO-A")
        app._v123_snapshot_is_persisted = False
        before = (app.original, app.image_path, dict(app.points), app.case_id.get())
        messagebox.askyesno = lambda *a, **k: False
        assert app.new_case() is False
        after = (app.original, app.image_path, dict(app.points), app.case_id.get())
        assert after == before, (before, after)

        messagebox.showwarning = lambda *a, **k: None
        filedialog.askopenfilename = lambda *a, **k: (_ for _ in ()).throw(
            AssertionError("No debe abrir el selector con una RX activa")
        )
        app.open_image()
        assert app.original is before[0]
        assert app.points == before[2]

        messagebox.askyesno = old_yesno
        messagebox.showwarning = old_warning
        filedialog.askopenfilename = old_open
        app._reset_case_specific_state()

        app._startup_home_shown = False
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

        print("YomCeph v0.12.3 Windows UI smoke test: OK")
    finally:
        messagebox.askyesno = old_yesno
        messagebox.showwarning = old_warning
        filedialog.askopenfilename = old_open
        if app is not None:
            try:
                app.destroy()
            except tk.TclError:
                pass
        shutil.rmtree(_TEMP_DATA, ignore_errors=True)


if __name__ == "__main__":
    main()
