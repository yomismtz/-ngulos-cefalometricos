"""Smoke test de YomCeph Desktop v0.12.6 en Windows/Tk."""

import os
import shutil
import tempfile
import tkinter as tk
from tkinter import messagebox

_TEMP_DATA = tempfile.mkdtemp(prefix="yomceph-v126-smoke-")
os.environ["LOCALAPPDATA"] = _TEMP_DATA

import yomceph_desktop_hidpi as ui
import yomceph_desktop_v11_database as v11db
import yomceph_scientific_catalog as catalog
from yomceph_desktop_v126_final import APP_VERSION, YomCephV126Final


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
        app = YomCephV126Final()
        app.withdraw()
        app.update_idletasks()
        assert APP_VERSION == "0.12.6"
        assert "v0.12.6" in app.title(), app.title()

        for analysis_id in ("ricketts", "cogs", "sassouni", "bimler", "g_triangle"):
            assert catalog.ANALYSES[analysis_id]["status"] == catalog.STATUS_ACTIVE
            assert catalog.analysis_measurements(analysis_id, active_only=True)
        assert catalog.ANALYSES["alexander"]["status"] == catalog.STATUS_REFERENCE_ONLY
        assert catalog.ANALYSES["ritucci"]["status"] == catalog.STATUS_OTHER_PROJECTION

        for landmark in ("Pt", "Pm", "DC", "R1", "R2", "R3", "R4", "U6", "L6", "SasCl", "SasRo", "SasSi", "SasMbP", "GoA", "Cls", "Cli", "Gtri"):
            assert landmark in v11db.MASTER_INFO, landmark

        old = catalog.MEASUREMENTS.get("McNamara · eje facial BaN–PtmGn")
        assert old and old["status"] == catalog.STATUS_VALIDATION
        _destroy_toplevels(app)
        print("YomCeph v0.12.6 Windows UI smoke test: OK")
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
