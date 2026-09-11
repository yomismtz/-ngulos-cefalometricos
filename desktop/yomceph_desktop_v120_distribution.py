"""Entrada pública de YomCeph Desktop v0.12.

Incluye importación de radiografías multiformato/PDF y un actualizador seguro.
La comprobación de versión consulta metadatos públicos de GitHub Releases; nunca
envía radiografías, datos de pacientes, landmarks ni resultados.
"""

from pathlib import Path
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

import yomceph_desktop_hidpi as ui
from yomceph_desktop_v120_release_final import YomCephV120ReleaseFinal
from yomceph_radiograph_loader import (
    FILE_DIALOG_TYPES,
    RadiographLoadError,
    load_radiograph,
    materialize_as_png,
    radiograph_page_count,
)
from yomceph_updater import (
    UpdateError,
    download_verified_installer,
    fetch_latest_update,
    launch_installer,
)

APP_VERSION = "0.12.0"


class YomCephV120Distribution(YomCephV120ReleaseFinal):
    """Distribución pública: PDF/multiformato + actualizaciones verificadas."""

    def __init__(self):
        self._update_check_in_progress = False
        self._update_download_in_progress = False
        super().__init__()
        # No bloquea el inicio ni la pantalla "¿Qué vamos a hacer hoy?".
        self.after(2500, lambda: self.check_for_updates(manual=False))

    def _install_database_bar(self):
        super()._install_database_bar()

        # Compatibilidad con QualityAuditYomCeph._refresh_case_state(): esa capa
        # heredada cambia bg/fg/activebackground directamente. ttk.Button no
        # admite esas opciones y provocaba TclError: unknown option "-bg" al
        # iniciar la distribución v0.12. El botón QC público debe ser tk.Button.
        try:
            old_qc = self.qc_button
            old_qc.destroy()
            self.qc_button = tk.Button(
                self.case_state_frame,
                text="QC pendiente",
                command=self.show_quality_control,
                bg="#DCE3EA",
                fg="#233044",
                activebackground="#DCE3EA",
                activeforeground="#233044",
                relief=tk.FLAT,
                bd=0,
                padx=8,
                pady=2,
                font=("Segoe UI", 9, "bold"),
                cursor="hand2",
            )
            self.qc_button.pack(side=tk.RIGHT)
        except Exception:
            pass

        # El control manual vive en Más ▾ para no robar espacio a la radiografía.
        try:
            for child in self.universal_wrapper.winfo_children():
                if str(child.cget("text")) != "Más ▾":
                    continue
                menu = self.nametowidget(str(child.cget("menu")))
                menu.add_separator()
                menu.add_command(
                    label="Buscar actualizaciones",
                    command=lambda: self.check_for_updates(manual=True),
                )
                break
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Actualizaciones
    # ------------------------------------------------------------------
    def _has_unsaved_case(self):
        if getattr(self, "_case_saved", False):
            return False
        return bool(
            getattr(self, "original", None) is not None
            or getattr(self, "points", {})
            or self.case_id.get().strip()
        )

    def check_for_updates(self, manual=False):
        if self._update_check_in_progress or self._update_download_in_progress:
            if manual:
                messagebox.showinfo("Actualizaciones", "YomCeph ya está comprobando o descargando una actualización.")
            return
        self._update_check_in_progress = True
        if manual:
            try:
                self.status.config(text="Buscando actualizaciones…")
            except Exception:
                pass

        def worker():
            try:
                update = fetch_latest_update(APP_VERSION)
                error = None
            except Exception as exc:
                update = None
                error = exc
            self.after(0, lambda: self._finish_update_check(update, error, manual))

        threading.Thread(target=worker, name="YomCephUpdateCheck", daemon=True).start()

    def _finish_update_check(self, update, error, manual):
        self._update_check_in_progress = False
        if error is not None:
            # La app puede seguir trabajando totalmente offline. En comprobación
            # automática no se molesta al usuario por ausencia de conexión.
            if manual:
                messagebox.showwarning("Actualizaciones", str(error))
                try:
                    self.status.config(text="No se pudo comprobar actualizaciones; YomCeph continúa en modo local.")
                except Exception:
                    pass
            return
        if update is None:
            if manual:
                messagebox.showinfo("Actualizaciones", f"YomCeph v{APP_VERSION} está actualizado.")
                try:
                    self.status.config(text=f"YomCeph v{APP_VERSION} · versión actual")
                except Exception:
                    pass
            return

        if self._has_unsaved_case():
            messagebox.showinfo(
                "Actualización disponible",
                f"Está disponible YomCeph v{update.version}.\n\n"
                "Hay un caso con cambios sin guardar. Guárdelo primero y después use "
                "Más ▾ → Buscar actualizaciones. YomCeph no cerrará un trabajo sin guardar.",
            )
            return

        if not messagebox.askyesno(
            "Actualización disponible",
            f"Está disponible YomCeph v{update.version}.\n\n"
            "¿Desea descargarla, verificarla e instalarla ahora?\n\n"
            "La base de datos y las radiografías guardadas permanecen fuera de la carpeta de instalación.",
        ):
            return
        self._download_update(update)

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
                installer = download_verified_installer(update, destination, APP_VERSION)
                error = None
            except Exception as exc:
                installer = None
                error = exc
            self.after(0, lambda: self._finish_update_download(update, installer, error))

        threading.Thread(target=worker, name="YomCephUpdateDownload", daemon=True).start()

    def _finish_update_download(self, update, installer, error):
        self._update_download_in_progress = False
        if error is not None:
            messagebox.showerror("Actualización", f"No se pudo instalar la actualización.\n\n{error}")
            try:
                self.status.config(text="Actualización cancelada; no se modificó la instalación actual.")
            except Exception:
                pass
            return
        if self._has_unsaved_case():
            messagebox.showwarning(
                "Actualización preparada",
                "La actualización se descargó y verificó, pero apareció trabajo sin guardar. "
                "Guarde el caso y vuelva a buscar actualizaciones para instalarla.",
            )
            return
        try:
            launch_installer(installer)
        except (UpdateError, OSError) as exc:
            messagebox.showerror("Actualización", f"El instalador verificado no pudo iniciarse.\n\n{exc}")
            return
        try:
            self.status.config(text=f"Instalando YomCeph v{update.version}…")
            self.update_idletasks()
        except Exception:
            pass
        # Inno Setup conserva los datos locales, actualiza la misma AppId y
        # vuelve a abrir YomCeph al terminar.
        self.after(250, self.destroy)

    # ------------------------------------------------------------------
    # Radiografías: imágenes + PDF
    # ------------------------------------------------------------------
    def open_image(self):
        path = filedialog.askopenfilename(
            title="Seleccionar radiografía",
            filetypes=FILE_DIALOG_TYPES,
        )
        if not path:
            return

        try:
            page_count = radiograph_page_count(path)
        except RadiographLoadError as exc:
            messagebox.showerror("Radiografía", str(exc))
            return

        page_index = 0
        if page_count > 1:
            page_number = simpledialog.askinteger(
                "Seleccionar página",
                f"El archivo contiene {page_count} páginas/imágenes.\n\n"
                f"Seleccione la página que contiene la radiografía (1–{page_count}):",
                minvalue=1,
                maxvalue=page_count,
                initialvalue=1,
                parent=self,
            )
            if page_number is None:
                return
            page_index = page_number - 1

        try:
            imported = load_radiograph(path, page_index=page_index)
        except RadiographLoadError as exc:
            messagebox.showerror("Radiografía", str(exc))
            return
        except Exception as exc:
            messagebox.showerror("Radiografía", f"No se pudo abrir el archivo.\n\n{exc}")
            return

        source_path = Path(path)
        working_path = source_path

        # El flujo histórico vuelve a abrir self.image_path con Pillow al guardar
        # proyectos/casos. PDF no es una imagen Pillow y una página >1 de TIFF/GIF
        # perdería la selección. Por eso esos casos se materializan como PNG.
        must_materialize = imported.source_kind == "pdf" or imported.page_index != 0
        if must_materialize:
            try:
                base_dir = Path(self._data_dir) if getattr(self, "_data_dir", None) else Path.home() / ".yomceph"
                working_path = materialize_as_png(imported, base_dir / "imports")
            except Exception as exc:
                messagebox.showerror(
                    "Radiografía",
                    "La imagen se pudo leer, pero no se pudo crear la copia PNG de trabajo.\n\n"
                    f"{exc}",
                )
                return

        self.original = imported.image.copy()
        self.image_path = str(working_path)
        self._radiograph_source_path = str(source_path)
        self._radiograph_source_page = imported.page_index
        self._radiograph_source_page_count = imported.page_count
        self._radiograph_source_kind = imported.source_kind
        self._radiograph_effective_dpi = imported.effective_dpi

        self.points.clear()
        self.mm_per_pixel = None
        self.calibration_points = []
        if hasattr(self, "calibration_real_mm"):
            self.calibration_real_mm = None
        self.calibrating = False
        try:
            self.cal_label.config(text="Sin calibración")
        except Exception:
            pass

        details = source_path.name
        if imported.page_count > 1:
            details += f" · página {imported.page_number}/{imported.page_count}"
        if imported.source_kind == "pdf":
            details += f" · PDF importado a {imported.effective_dpi:.0f} ppp"
        self.status.config(text=details)

        try:
            self.update_point_guide()
        except Exception:
            pass
        self.after(50, self.fit_image)

        if hasattr(self, "_case_saved"):
            self._case_saved = False
        try:
            self._refresh_quality_control()
        except Exception:
            try:
                self._refresh_case_state()
            except Exception:
                pass


if __name__ == "__main__":
    ui.enable_dpi_awareness()
    app = YomCephV120Distribution()
    app.mainloop()
