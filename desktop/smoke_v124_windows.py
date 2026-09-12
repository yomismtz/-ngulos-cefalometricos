"""Smoke test real de YomCeph v0.12.4 en Windows/Tk."""

import json
import os
import shutil
import sqlite3
import tempfile
import tkinter as tk
from tkinter import messagebox, ttk

_TEMP_DATA = tempfile.mkdtemp(prefix="yomceph-v124-smoke-")
os.environ["LOCALAPPDATA"] = _TEMP_DATA

import yomceph_desktop_hidpi as ui
from yomceph_desktop_v124_personalization import APP_VERSION, PALETTES
from yomceph_desktop_v124_final import YomCephV124Final


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
    messagebox.showinfo = lambda *a, **k: None
    messagebox.showwarning = lambda *a, **k: None
    try:
        app = YomCephV124Final()
        app.withdraw()
        app.update_idletasks()

        assert APP_VERSION == "0.12.4"
        assert "v0.12.4" in app.title(), app.title()
        assert hasattr(app, "personalization_bar")
        assert hasattr(app, "personalization_summary")
        assert len(PALETTES) == 5

        with sqlite3.connect(app._db_path) as con:
            studies = con.execute("SELECT COUNT(*) FROM research_studies").fetchone()[0]
        assert studies == 0, f"La instalación limpia creó {studies} estudios"

        app._apply_personalization(
            {"font_family": "Arial", "font_size": 12, "palette": "Azul clínico"},
            persist=True,
        )
        app.update_idletasks()
        assert app._personalization["font_family"] == "Arial"
        assert app._personalization["font_size"] == 12
        assert app._personalization["palette"] == "Azul clínico"
        assert ui.C["purple"] == PALETTES["Azul clínico"]["purple"]
        assert "Arial 12" in app.personalization_summary.cget("text")

        prefs_path = app._preferences_path
        assert prefs_path.is_file(), prefs_path
        loaded = json.loads(prefs_path.read_text(encoding="utf-8"))
        assert loaded["font_family"] == "Arial"
        assert loaded["font_size"] == 12
        assert loaded["palette"] == "Azul clínico"

        style = ttk.Style(app)
        assert style.lookup("Treeview", "background") == PALETTES["Azul clínico"]["panel"]
        assert style.lookup("Treeview", "foreground") == PALETTES["Azul clínico"]["text"]

        app._quick_font_step(1)
        assert app._personalization["font_size"] == 13
        for _ in range(20):
            app._quick_font_step(1)
        assert app._personalization["font_size"] == 18
        for _ in range(30):
            app._quick_font_step(-1)
        assert app._personalization["font_size"] == 8

        app.open_personalization_settings()
        app.update_idletasks()
        dialogs = [c for c in app.winfo_children() if isinstance(c, tk.Toplevel)]
        assert any("Personalización" in d.title() for d in dialogs)
        _destroy_toplevels(app)

        app._apply_personalization(
            {"font_family": "Segoe UI", "font_size": 10, "palette": "Noche radiográfica"},
            persist=False,
        )
        app.update_idletasks()
        assert ui.C["paper"] == PALETTES["Noche radiográfica"]["paper"]
        app.high_contrast_var.set(True)
        app._apply_high_contrast()
        assert app.canvas.cget("background") == "#000000"
        app.high_contrast_var.set(False)
        app._apply_high_contrast()
        assert app.canvas.cget("background").lower() == PALETTES["Noche radiográfica"]["canvas"].lower()

        app._apply_personalization(
            {"font_family": "Segoe UI", "font_size": 10, "palette": "YomCeph violeta"},
            persist=False,
        )
        app.update_idletasks()

        print("YomCeph v0.12.4 personalization Windows UI smoke test: OK")
    finally:
        messagebox.showinfo = old_info
        messagebox.showwarning = old_warning
        if app is not None:
            try:
                app.destroy()
            except tk.TclError:
                pass
        shutil.rmtree(_TEMP_DATA, ignore_errors=True)


if __name__ == "__main__":
    main()
