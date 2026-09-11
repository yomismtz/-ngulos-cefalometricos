"""Entrada de distribución de YomCeph Desktop v0.12.

Añade importación de radiografías en formatos de imagen comunes y PDF sobre la
candidata pública auditada. Los PDF se convierten internamente a PNG sin pérdida
después de seleccionar la página para conservar compatibilidad con la base local,
el trazado, la calibración y los proyectos existentes.
"""

from pathlib import Path
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

APP_VERSION = "0.12.0"


class YomCephV120Distribution(YomCephV120ReleaseFinal):
    """Distribución final con importación multiformato/PDF."""

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

        # Mantiene el comportamiento de QC/estado de las capas v0.11.5+.
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
