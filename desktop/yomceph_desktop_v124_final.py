"""Cierre visual de YomCeph Desktop v0.12.4.

Completa la personalización de la candidata v0.12.4 para controles ttk, hace
compatible el modo de alto contraste con la paleta elegida y mantiene el
contrato histórico de v0.12.3 aislado del nuevo actualizador.
"""

from pathlib import Path
import threading
import tkinter as tk
from tkinter import messagebox, ttk

import yomceph_desktop_hidpi as ui
import yomceph_desktop_v120_distribution as distribution
import yomceph_desktop_v123_hardening as hardening
from yomceph_desktop_v124_personalization import (
    APP_VERSION,
    YomCephV124Personalization,
)

# Importar la capa de personalización ajusta temporalmente las constantes
# heredadas. Las restauramos para que v0.12.3 siga siendo reproducible; esta
# clase usa APP_VERSION=0.12.4 de forma explícita en título y actualizador.
hardening.APP_VERSION = "0.12.3"
distribution.APP_VERSION = "0.12.2"


class YomCephV124Final(YomCephV124Personalization):
    def _configure_personalization_styles(self, prefs):
        super()._configure_personalization_styles(prefs)
        c = ui.C
        family = prefs["font_family"]
        size = prefs["font_size"]
        style = ttk.Style(self)

        style.configure(
            "Treeview",
            background=c["panel"],
            fieldbackground=c["panel"],
            foreground=c["text"],
            font=(family, size),
            bordercolor=c["border"],
            lightcolor=c["border"],
            darkcolor=c["border"],
        )
        style.map(
            "Treeview",
            background=[("selected", c["purple"])],
            foreground=[("selected", "white")],
        )
        style.configure(
            "Treeview.Heading",
            background=c["lilac_soft"],
            foreground=c["purple_dark"],
            font=(family, size, "bold"),
            relief="flat",
        )
        style.map("Treeview.Heading", background=[("active", c["lilac"])])

        for style_name in ("TEntry", "TCombobox", "TSpinbox"):
            style.configure(
                style_name,
                fieldbackground=c["panel"],
                background=c["panel"],
                foreground=c["text"],
                insertcolor=c["text"],
                font=(family, size),
            )
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", c["panel"])],
            foreground=[("readonly", c["text"])],
            selectbackground=[("readonly", c["purple"])],
            selectforeground=[("readonly", "white")],
        )
        style.configure(
            "TLabelframe",
            background=c["panel"],
            bordercolor=c["border"],
            lightcolor=c["border"],
            darkcolor=c["border"],
        )
        style.configure(
            "TLabelframe.Label",
            background=c["panel"],
            foreground=c["purple_dark"],
            font=(family, size, "bold"),
        )

    def _apply_high_contrast(self):
        enabled = bool(self.high_contrast_var.get())
        try:
            self.canvas.configure(background="#000000" if enabled else ui.C["canvas"])
            base = int(self._personalization.get("font_size", 10))
            family = self._personalization.get("font_family", "Segoe UI")
            self.case_state_label.configure(
                font=(family, base + 1 if enabled else max(8, base), "bold")
            )
        except Exception:
            pass
        self.status.config(
            text=(
                "Alto contraste activado."
                if enabled
                else f"Alto contraste desactivado · paleta {self._personalization.get('palette', 'YomCeph violeta')}."
            )
        )

    def _apply_language(self):
        try:
            self.title(f"YomCeph Desktop · v{APP_VERSION}")
        except tk.TclError:
            pass

    def load_case_from_database(self, storage_id):
        result = super().load_case_from_database(storage_id)
        try:
            self.title(f"YomCeph Desktop · v{APP_VERSION}")
        except tk.TclError:
            pass
        return result

    # Actualizador v0.12.4 sin modificar las constantes históricas v0.12.3.
    def check_for_updates(self, manual=False):
        if self._update_check_in_progress or self._update_download_in_progress:
            if manual:
                messagebox.showinfo(
                    "Actualizaciones",
                    "YomCeph ya está comprobando o descargando una actualización.",
                )
            return
        self._update_check_in_progress = True
        if manual:
            try:
                self.status.config(text="Buscando actualizaciones…")
            except Exception:
                pass

        def worker():
            try:
                update = distribution.fetch_latest_update(APP_VERSION)
                error = None
            except Exception as exc:
                update = None
                error = exc
            self._v123_update_queue.put(("check", update, error, manual))

        threading.Thread(target=worker, name="YomCephUpdateCheck", daemon=True).start()

    def _download_update(self, update):
        self._update_download_in_progress = True
        try:
            self.status.config(text=f"Descargando YomCeph v{update.version}…")
        except Exception:
            pass
        base = Path(self._data_dir) if getattr(self, "_data_dir", None) else Path.home() / ".yomceph"
        destination = base / "updates"

        def worker():
            try:
                installer = distribution.download_verified_installer(
                    update, destination, APP_VERSION
                )
                error = None
            except Exception as exc:
                installer = None
                error = exc
            self._v123_update_queue.put(("download", update, installer, error))

        threading.Thread(target=worker, name="YomCephUpdateDownload", daemon=True).start()


if __name__ == "__main__":
    ui.enable_dpi_awareness()
    app = YomCephV124Final()
    app.mainloop()
