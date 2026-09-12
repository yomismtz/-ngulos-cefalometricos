import tkinter as tk

import yomceph_desktop_hidpi as ui
import yomceph_desktop_v112_guide_menu as v112

APP_VERSION = "0.11.3"


class WorkspaceYomCeph(v112.GuideMenuYomCeph):
    """v0.11.3: más espacio para la radiografía y menú ARCHIVO."""

    def __init__(self):
        super().__init__()
        self.title("YomCeph Desktop · Investigación · Base de datos · v0.11.3")
        self._install_file_menu()
        self._compact_right_panel()
        # Reaplicar proporciones después de que Windows termine de maximizar.
        self.after(320, self._set_initial_sashes)
        self.after(750, self._set_initial_sashes)
        self.status.config(text="v0.11.3 · Área radiográfica ampliada · ARCHIVO arriba para abrir o iniciar casos")

    # ------------------------------------------------------------------
    # Menú Archivo en la barra superior
    # ------------------------------------------------------------------
    def _install_file_menu(self):
        try:
            menu_name = self.cget("menu")
            menubar = self.nametowidget(menu_name) if menu_name else tk.Menu(self)
        except Exception:
            menubar = tk.Menu(self)
            self.config(menu=menubar)

        # Evitar duplicarlo si la interfaz se reconstruye.
        try:
            end = menubar.index("end")
            if end is not None:
                for i in range(end + 1):
                    if menubar.entrycget(i, "label") == "ARCHIVO":
                        return
        except Exception:
            pass

        file_menu = tk.Menu(menubar, tearoff=False)
        file_menu.add_command(label="Nuevo archivo / caso", command=self.new_case, accelerator="Ctrl+N")
        file_menu.add_command(label="Abrir radiografía...", command=self.open_image, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Abrir proyecto YomCeph...", command=self.load_project)
        file_menu.add_command(label="Guardar proyecto YomCeph...", command=self.save_project, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.destroy)

        try:
            menubar.insert_cascade(0, label="ARCHIVO", menu=file_menu)
        except Exception:
            menubar.add_cascade(label="ARCHIVO", menu=file_menu)

        self.bind_all("<Control-n>", lambda _e: self.new_case())
        self.bind_all("<Control-o>", lambda _e: self.open_image())
        self.bind_all("<Control-s>", lambda _e: self.save_project())

    # ------------------------------------------------------------------
    # Distribución: más espacio central para la radiografía
    # ------------------------------------------------------------------
    def _compact_right_panel(self):
        # La columna Guía/Resultados se mantiene, pero con una anchura solicitada
        # mucho menor para que no robe espacio al lienzo radiográfico.
        nb = getattr(self, "_vertebral_notebook", None)
        if nb is not None:
            try:
                nb.configure(width=235)
            except Exception:
                pass

        for widget in (
            getattr(self, "point_title", None),
            getattr(self, "point_desc", None),
            getattr(self, "point_status", None),
        ):
            if widget is not None:
                try:
                    widget.configure(wraplength=215)
                except Exception:
                    pass

        results = getattr(self, "results_text", None)
        if results is not None:
            try:
                results.configure(width=27)
            except Exception:
                pass

        # Ajustar también cualquier etiqueta auxiliar de la pestaña Guía.
        if nb is not None:
            self._shrink_wrapped_labels(nb)

    def _shrink_wrapped_labels(self, parent):
        try:
            children = parent.winfo_children()
        except Exception:
            return
        for child in children:
            try:
                current = child.cget("wraplength")
                if current and float(current) > 215:
                    child.configure(wraplength=215)
            except Exception:
                pass
            self._shrink_wrapped_labels(child)

    def _set_initial_sashes(self):
        """Da prioridad al área central de la radiografía."""
        try:
            self.update_idletasks()
            width = self.body_panes.winfo_width()
            if width < 820:
                return

            # Izquierda conserva espacio suficiente para nombres de landmarks.
            left_w = max(225, int(width * 0.17))
            # Derecha baja de ~25% a ~15.5% del ancho total.
            right_w = max(210, int(width * 0.155))

            # En pantallas pequeñas no dejar el lienzo central excesivamente estrecho.
            min_center = 520
            if left_w + right_w + min_center > width:
                available = max(180, width - left_w - min_center)
                right_w = min(right_w, available)

            self.body_panes.sashpos(0, left_w)
            self.body_panes.sashpos(1, width - right_w)
        except Exception:
            pass


if __name__ == "__main__":
    ui.enable_dpi_awareness()
    app = WorkspaceYomCeph()
    app.mainloop()
