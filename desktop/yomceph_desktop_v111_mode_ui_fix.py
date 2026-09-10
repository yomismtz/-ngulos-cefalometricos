import tkinter as tk
from tkinter import messagebox

import yomceph_desktop as core
import yomceph_desktop_hidpi as ui
import yomceph_desktop_v11_database as v11

APP_VERSION = "0.11.1"


class ModeFilteredYomCeph(v11.ResearchDatabaseYomCeph):
    """v0.11.1: separa de forma estricta la interfaz Steiner/Postura."""

    def __init__(self):
        super().__init__()
        self.title("YomCeph Desktop · Investigación · Base de datos · v0.11.1")
        self.after(250, self._sync_mode_ui)

    # ------------------------------------------------------------------
    # Plano vertebral: ocultarlo DE VERDAD en Steiner.
    # Se usa el estado del tab de ttk.Notebook en vez de forget/add por nombre.
    # ------------------------------------------------------------------
    def _capture_vertebral_tab(self):
        try:
            self._vertebral_tab = self.guide_canvas.master
            self._vertebral_notebook = self._vertebral_tab.master
        except Exception:
            self._vertebral_tab = None
            self._vertebral_notebook = None

    def _set_vertebral_visibility(self, visible):
        tab = self._vertebral_tab
        nb = self._vertebral_notebook
        if tab is None or nb is None:
            return
        try:
            if not visible:
                # Si el usuario está parado en esa pestaña, páselo a Guía antes de ocultarla.
                try:
                    if str(nb.select()) == str(tab):
                        tabs = nb.tabs()
                        if tabs:
                            nb.select(tabs[0])
                except Exception:
                    pass
                nb.tab(tab, state="hidden")
            else:
                nb.tab(tab, state="normal")
        except Exception:
            # Fallback para implementaciones Tk que no acepten state=hidden.
            try:
                tabs = [str(x) for x in nb.tabs()]
                tab_name = str(tab)
                if visible and tab_name not in tabs:
                    nb.add(tab, text="Plano vertebral")
                elif not visible and tab_name in tabs:
                    nb.forget(tab)
            except Exception:
                pass

    # ------------------------------------------------------------------
    # Lista lateral: únicamente landmarks del análisis elegido.
    # ------------------------------------------------------------------
    def _active_keys_for_mode(self, mode):
        if mode == "Steiner":
            allowed = set(v11.STEINER_POINTS)
        elif mode == "Postura craneofacial":
            allowed = set(v11.POSTURE_POINTS)
        else:
            allowed = set(v11.STEINER_POINTS) | set(v11.POSTURE_POINTS)
        return [k for k in v11.MASTER_ORDER if k in allowed]

    def apply_analysis_mode(self, mode):
        if mode not in ("Steiner", "Postura craneofacial", "Ambos"):
            mode = "Ambos"
        self.analysis_mode = mode
        self.active_point_order = self._active_keys_for_mode(mode)

        # Steiner: sin plano vertebral. Postura/Ambos: visible.
        self._set_vertebral_visibility(mode != "Steiner")

        # Si el punto seleccionado pertenece al otro módulo, mover la selección
        # al primer punto activo antes de reconstruir la lista.
        if self.active_point_order and self.selected_point.get() not in self.active_point_order:
            first_missing = next((k for k in self.active_point_order if k not in self.points), self.active_point_order[0])
            self.selected_point.set(first_missing)

        self._rebuild_active_point_list()
        self._sync_progress()
        self._refresh_guided_menu_for_mode()
        self._update_db_counter()
        self.redraw()
        self.status.config(
            text=(f"Modo {mode}: sólo aparecen los puntos de este análisis. "
                  + ("Plano vertebral oculto." if mode == "Steiner" else "Plano vertebral disponible."))
        )

    def _rebuild_active_point_list(self):
        if not hasattr(self, "point_list"):
            return
        current = self.selected_point.get()
        self.point_list.delete(0, tk.END)
        selected_index = 0
        for i, key in enumerate(self.active_point_order):
            title = v11.MASTER_INFO[key][0]
            placed = key in self.points
            self.point_list.insert(tk.END, f"{'✓' if placed else '○'} {key} · {title}")
            self.point_list.itemconfig(i, foreground=("#238B67" if placed else ui.C["muted"]))
            if key == current:
                selected_index = i
        if self.active_point_order:
            self.point_list.selection_clear(0, tk.END)
            self.point_list.selection_set(selected_index)
            self.point_list.see(selected_index)
        self._sync_progress()
        try:
            self.update_point_guide()
        except Exception:
            pass

    def _refresh_point_list_marks(self):
        # Nunca vuelve a poblar la lista con MASTER_ORDER completo.
        if not hasattr(self, "point_list"):
            return
        current = self.selected_point.get()
        self.point_list.delete(0, tk.END)
        selected_index = 0
        for i, key in enumerate(self.active_point_order):
            title = v11.MASTER_INFO[key][0]
            placed = key in self.points
            self.point_list.insert(tk.END, f"{'✓' if placed else '○'} {key} · {title}")
            self.point_list.itemconfig(i, foreground=("#238B67" if placed else ui.C["muted"]))
            if key == current:
                selected_index = i
        if self.active_point_order:
            self.point_list.selection_set(selected_index)
            self.point_list.see(selected_index)
        self._sync_progress()

    def _sync_progress(self):
        if not hasattr(self, "progress_var"):
            return
        total = len(self.active_point_order)
        placed = sum(1 for key in self.active_point_order if key in self.points)
        # El widget base tiene maximum=MASTER; escalamos el valor para que la barra
        # represente el porcentaje real del módulo activo.
        master_total = max(1, len(core.POINT_ORDER))
        self.progress_var.set((placed / total) * master_total if total else 0)
        if hasattr(self, "progress_label"):
            self.progress_label.config(text=f"{placed} / {total} puntos · {self.analysis_mode}")

    # ------------------------------------------------------------------
    # Menú guiado: no ofrecer recorridos del módulo que está desactivado.
    # ------------------------------------------------------------------
    def _refresh_guided_menu_for_mode(self):
        try:
            menu_name = self.cget("menu")
            menubar = self.nametowidget(menu_name)
        except Exception:
            return

        # Quita el cascade anterior TRAZADO GUIADO si existe.
        try:
            end = menubar.index("end")
            if end is not None:
                for i in range(end, -1, -1):
                    try:
                        if menubar.entrycget(i, "label") == "TRAZADO GUIADO":
                            menubar.delete(i)
                    except Exception:
                        pass
        except Exception:
            pass

        guide = tk.Menu(menubar, tearoff=False)
        if self.analysis_mode in ("Postura craneofacial", "Ambos"):
            guide.add_command(label="OPT y CVT", command=self.start_opt_guide, accelerator="F6")
            guide.add_command(label="Tangentes posteriores C2–C7", command=self.start_posterior_guide, accelerator="F7")
            guide.add_command(label="McGregor + plano odontoideo OP", command=self.start_mcgregor_guide, accelerator="F9")
            guide.add_command(label="Powell · tejidos blandos", command=self.start_powell_guide, accelerator="F12")
            guide.add_command(label="Profundidad cervical (PC)", command=lambda: self._select_key("PC"))
        if self.analysis_mode in ("Steiner", "Ambos"):
            if guide.index("end") is not None:
                guide.add_separator()
            guide.add_command(label="Incisivos e interincisal", command=self.start_dental_guide, accelerator="F10")
        guide.add_separator()
        guide.add_command(label="Salir del modo guiado", command=self.stop_guide, accelerator="F8")
        menubar.add_cascade(label="TRAZADO GUIADO", menu=guide)

    # ------------------------------------------------------------------
    # Radiografía: si se cambia de modo durante un caso, los puntos del otro
    # módulo se conservan en memoria pero NO se dibujan ni interfieren visualmente.
    # ------------------------------------------------------------------
    def redraw(self):
        if not hasattr(self, "active_point_order") or not self.active_point_order:
            return super().redraw()
        all_points = self.points
        visible = set(self.active_point_order)
        try:
            self.points = {k: v for k, v in all_points.items() if k in visible}
            super().redraw()
        finally:
            self.points = all_points

    def _sync_mode_ui(self):
        try:
            self._set_vertebral_visibility(self.analysis_mode != "Steiner")
            self._rebuild_active_point_list()
            self._refresh_guided_menu_for_mode()
            self._sync_progress()
        except Exception:
            pass


if __name__ == "__main__":
    ui.enable_dpi_awareness()
    app = ModeFilteredYomCeph()
    app.mainloop()
