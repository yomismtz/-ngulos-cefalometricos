"""Endurecimiento de YomCeph Desktop v0.12.3.

No modifica fórmulas cefalométricas. Corrige rutas de estado, guardado,
cambio de caso y cierre que podían descartar trabajo sin intención del usuario.
"""

from __future__ import annotations

import json
import queue
import sqlite3
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from PIL import Image

import yomceph_desktop_hidpi as ui
import yomceph_desktop_v120_distribution as distribution
import yomceph_desktop_v120_release as release

APP_VERSION = "0.12.3"
distribution.APP_VERSION = APP_VERSION


class YomCephV123Hardening(distribution.YomCephV120Distribution):
    """Distribución pública con protección reforzada contra pérdida de trabajo."""

    def __init__(self):
        self._v123_internal_mutation = True
        self._v123_saving = False
        self._v123_loading = False
        self._v123_saved_snapshot = None
        self._v123_snapshot_is_persisted = False
        self._v123_update_queue = queue.Queue()
        super().__init__()
        self._v123_internal_mutation = False
        self._install_v123_dirty_traces()
        self._v123_saved_snapshot = self._case_snapshot()
        self._v123_snapshot_is_persisted = False
        self.protocol("WM_DELETE_WINDOW", self._request_close)
        self.title(f"YomCeph Desktop · v{APP_VERSION}")
        self.after(120, self._poll_update_queue)

    def _apply_language(self):
        try:
            self.title(f"YomCeph Desktop · v{APP_VERSION}")
        except tk.TclError:
            pass

    def _get_more_menu(self):
        for child in getattr(self, "universal_wrapper", self).winfo_children():
            if not isinstance(child, ttk.Menubutton):
                continue
            try:
                menu_name = child.cget("menu")
                if menu_name:
                    return self.nametowidget(str(menu_name))
            except (tk.TclError, KeyError):
                continue
        return None

    @staticmethod
    def _menu_labels(menu):
        labels = set()
        if menu is None:
            return labels
        try:
            end = menu.index("end")
        except tk.TclError:
            return labels
        if end is None:
            return labels
        for index in range(end + 1):
            try:
                label = menu.entrycget(index, "label")
            except tk.TclError:
                continue
            if label:
                labels.add(str(label))
        return labels

    def _install_database_bar(self):
        release.YomCephV120Release._install_database_bar(self)
        old_qc = getattr(self, "qc_button", None)
        if old_qc is not None:
            try:
                old_qc.destroy()
            except tk.TclError:
                pass
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
        menu = self._get_more_menu()
        labels = self._menu_labels(menu)
        if menu is not None:
            if "Alto contraste" not in labels and hasattr(self, "high_contrast_var"):
                menu.add_separator()
                menu.add_checkbutton(
                    label="Alto contraste",
                    variable=self.high_contrast_var,
                    command=self._apply_high_contrast,
                )
                labels.add("Alto contraste")
            if "Buscar actualizaciones" not in labels:
                menu.add_separator()
                menu.add_command(
                    label="Buscar actualizaciones",
                    command=lambda: self.check_for_updates(manual=True),
                )

    def _install_database_menu(self):
        try:
            menu_name = self.cget("menu")
            menubar = self.nametowidget(menu_name) if menu_name else tk.Menu(self)
        except (tk.TclError, KeyError):
            menubar = tk.Menu(self)
        self.config(menu=menubar)
        menu = tk.Menu(menubar, tearoff=False)
        menu.add_command(label="Guardar caso", command=self.save_case_to_database)
        menu.add_command(label="Abrir base de datos", command=self.open_database_browser)
        menu.add_command(label="Exportar investigación activa", command=self.export_research_package)
        menu.add_separator()
        menu.add_command(label="Análisis / resultados", command=lambda: self.choose_analysis_mode(startup=False))
        menu.add_command(label="Nuevo caso", command=self.next_case)
        menu.add_command(label="Inicio / cambiar tipo de trabajo", command=self._return_to_workflow_home)
        menubar.add_cascade(label="YOMCEPH", menu=menu)

    @staticmethod
    def _var_value(var, default=""):
        try:
            return var.get()
        except Exception:
            return default

    @staticmethod
    def _freeze_points(points):
        frozen = []
        for key, value in sorted((points or {}).items()):
            try:
                x, y = value
                frozen.append((str(key), round(float(x), 8), round(float(y), 8)))
            except Exception:
                frozen.append((str(key), repr(value)))
        return tuple(frozen)

    @staticmethod
    def _freeze_calibration(points):
        out = []
        for value in points or []:
            try:
                x, y = value
                out.append((round(float(x), 8), round(float(y), 8)))
            except Exception:
                out.append((repr(value),))
        return tuple(out)

    def _case_snapshot(self):
        return {
            "case_id": str(self._var_value(getattr(self, "case_id", None))).strip(),
            "image_path": str(getattr(self, "image_path", "") or ""),
            "points": self._freeze_points(getattr(self, "points", {})),
            "mm_per_pixel": getattr(self, "mm_per_pixel", None),
            "calibration_points": self._freeze_calibration(getattr(self, "calibration_points", [])),
            "calibration_real_mm": getattr(self, "calibration_real_mm", None),
            "face_direction": str(self._var_value(getattr(self, "face_direction", None), "right")),
            "age_years": str(self._var_value(getattr(self, "age_years_var", None))).strip(),
            "age_months": str(self._var_value(getattr(self, "age_months_var", None))).strip(),
            "birth_date": str(self._var_value(getattr(self, "birth_date_var", None))).strip(),
            "radiograph_date": str(self._var_value(getattr(self, "radiograph_date_var", None))).strip(),
            "sex_code": str(self._var_value(getattr(self, "sex_code_var", None))).strip(),
            "gender_identity": str(self._var_value(getattr(self, "gender_identity_var", None))).strip(),
            "clinic": str(self._var_value(getattr(self, "clinic_var", None))).strip(),
            "country": str(self._var_value(getattr(self, "country_var", None))).strip(),
            "institution": str(self._var_value(getattr(self, "institution_var", None))).strip(),
            "workflow_type": str(getattr(self, "workflow_type", "individual") or "individual"),
            "study_id": str(getattr(self, "current_study_id", "") or ""),
            "groups": json.dumps(
                getattr(self, "case_group_values", {}) or {},
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ),
            "manual_eligibility": str(getattr(self, "manual_eligibility", "pending") or "pending"),
            "selected_measurements": tuple(getattr(self, "selected_measure_keys", []) or []),
            "steiner_reference": str(getattr(self, "steiner_reference", "none") or "none"),
        }

    def _case_has_content(self):
        if getattr(self, "original", None) is not None or getattr(self, "points", {}):
            return True
        snap = self._case_snapshot()
        if snap["case_id"]:
            return True
        for key in (
            "age_years", "age_months", "birth_date", "radiograph_date",
            "sex_code", "gender_identity", "clinic",
        ):
            if snap[key]:
                return True
        if getattr(self, "case_group_values", {}):
            return True
        return str(getattr(self, "manual_eligibility", "pending")) not in ("", "pending")

    def _capture_saved_snapshot(self):
        self._v123_saved_snapshot = self._case_snapshot()
        self._v123_snapshot_is_persisted = True
        self._case_saved = True

    def _sync_dirty_state(self, *_args):
        if (
            getattr(self, "_v123_internal_mutation", False)
            or getattr(self, "_v123_saving", False)
            or getattr(self, "_v123_loading", False)
        ):
            return
        if not self._case_has_content():
            self._case_saved = False
            return
        current = self._case_snapshot()
        self._case_saved = bool(
            self._v123_snapshot_is_persisted
            and self._v123_saved_snapshot is not None
            and current == self._v123_saved_snapshot
        )
        try:
            self._refresh_case_state()
        except Exception:
            pass

    def _install_v123_dirty_traces(self):
        if getattr(self, "_v123_dirty_traces_installed", False):
            return
        self._v123_dirty_traces_installed = True
        for name in (
            "case_id", "face_direction", "age_years_var", "age_months_var",
            "birth_date_var", "radiograph_date_var", "sex_code_var",
            "gender_identity_var", "clinic_var", "country_var", "institution_var",
        ):
            var = getattr(self, name, None)
            if var is not None:
                try:
                    var.trace_add("write", self._sync_dirty_state)
                except Exception:
                    pass

    def _has_unsaved_case(self):
        if not self._case_has_content():
            return False
        if not self._v123_snapshot_is_persisted or self._v123_saved_snapshot is None:
            return True
        return self._case_snapshot() != self._v123_saved_snapshot

    def _update_compact_context(self):
        result = super()._update_compact_context()
        self._sync_dirty_state()
        return result

    def _finish_individual_setup(self, keys, steiner_reference="none"):
        result = super()._finish_individual_setup(keys, steiner_reference)
        self._sync_dirty_state()
        return result

    def open_case_data(self, first_time=False):
        direct_names = (
            "case_id", "age_years_var", "age_months_var", "birth_date_var",
            "radiograph_date_var", "gender_identity_var",
        )
        before_values = {
            name: self._var_value(getattr(self, name, None)) for name in direct_names
        }
        before_windows = set(self.winfo_children())
        result = super().open_case_data(first_time=first_time)
        new_windows = [
            child for child in self.winfo_children()
            if child not in before_windows and isinstance(child, tk.Toplevel)
        ]
        if not new_windows:
            return result
        win = new_windows[-1]

        def cancel_dialog():
            self._v123_internal_mutation = True
            try:
                for name, value in before_values.items():
                    var = getattr(self, name, None)
                    if var is not None:
                        var.set(value)
            finally:
                self._v123_internal_mutation = False
            try:
                win.grab_release()
            except tk.TclError:
                pass
            try:
                win.destroy()
            except tk.TclError:
                pass
            self._sync_dirty_state()

        win.protocol("WM_DELETE_WINDOW", cancel_dialog)
        win.bind("<Escape>", lambda _event: cancel_dialog())
        return result

    def save_case_to_database(self):
        local = self.case_id.get().strip()
        if (
            getattr(self, "_loaded_case_id", None)
            and self._v123_snapshot_is_persisted
            and self._v123_saved_snapshot is not None
        ):
            saved_local = str(self._v123_saved_snapshot.get("case_id", "")).strip()
            if local != saved_local:
                messagebox.showerror(
                    "Identificador protegido",
                    "El identificador de un caso ya guardado no puede cambiarse mientras se edita. "
                    "Para crear otro registro use “＋ Caso”.",
                )
                self._v123_internal_mutation = True
                try:
                    self.case_id.set(saved_local)
                finally:
                    self._v123_internal_mutation = False
                self._sync_dirty_state()
                return
            if self._case_snapshot() == self._v123_saved_snapshot:
                messagebox.showinfo("Guardar", "No hay cambios pendientes en este caso.")
                return

        expected_storage = self._storage_case_id(local) if local else ""
        self._v123_saving = True
        self._v123_internal_mutation = True
        self._case_saved = False
        try:
            result = super().save_case_to_database()
        except Exception as exc:
            self._case_saved = False
            messagebox.showerror(
                "Guardado incompleto",
                "YomCeph encontró un error durante el guardado. El caso permanece marcado "
                f"como no guardado para que pueda reintentarlo.\n\n{exc}",
            )
            return
        finally:
            self._v123_internal_mutation = False
            self._v123_saving = False

        if not getattr(self, "_case_saved", False) or not expected_storage:
            self._sync_dirty_state()
            return result

        try:
            with sqlite3.connect(self._db_path) as con:
                exists = con.execute(
                    "SELECT 1 FROM cases WHERE case_id=?", (expected_storage,)
                ).fetchone()
            if not exists:
                raise RuntimeError("no se encontró el registro después de guardar")
        except Exception as exc:
            self._case_saved = False
            messagebox.showerror(
                "Verificación de guardado",
                "El guardado no pudo verificarse. No cierre el caso; vuelva a intentar.\n\n"
                + str(exc),
            )
            return result

        try:
            self._backup_database()
        except Exception:
            pass
        self._capture_saved_snapshot()
        try:
            self._refresh_case_state()
        except Exception:
            pass
        return result

    def _preflight_saved_case(self, storage_id):
        try:
            with sqlite3.connect(self._db_path) as con:
                row = con.execute(
                    "SELECT stored_image_path,image_path FROM cases WHERE case_id=?",
                    (storage_id,),
                ).fetchone()
        except Exception as exc:
            messagebox.showerror("Abrir caso", f"No se pudo consultar el registro.\n\n{exc}")
            return False
        if not row:
            messagebox.showerror("Abrir caso", "El caso seleccionado ya no existe en la base.")
            return False
        candidates = [Path(value) for value in row if value]
        if not candidates:
            messagebox.showerror("Abrir caso", "El registro no contiene una radiografía guardada.")
            return False
        path = next((candidate for candidate in candidates if candidate.is_file()), None)
        if path is None:
            messagebox.showerror(
                "Abrir caso",
                "No se encontró la copia local ni la ruta original de la radiografía asociada al caso.\n\n"
                + "\n".join(str(candidate) for candidate in candidates),
            )
            return False
        try:
            with Image.open(path) as image:
                image.verify()
        except Exception as exc:
            messagebox.showerror(
                "Abrir caso",
                "La copia local de la radiografía no puede leerse. El caso actual no fue reemplazado.\n\n"
                + str(exc),
            )
            return False
        return True

    def load_case_from_database(self, storage_id):
        if self._has_unsaved_case() and not messagebox.askyesno(
            "Cambios sin guardar",
            "El caso actual tiene cambios sin guardar.\n\n"
            "¿Descartarlos y abrir el caso seleccionado?",
        ):
            return
        if not self._preflight_saved_case(storage_id):
            return

        self._v123_loading = True
        self._v123_internal_mutation = True
        try:
            result = super().load_case_from_database(storage_id)
        except Exception as exc:
            self._case_saved = False
            messagebox.showerror(
                "Abrir caso",
                "No se pudo abrir el caso. El registro no se considera cargado.\n\n" + str(exc),
            )
            return
        finally:
            self._v123_internal_mutation = False
            self._v123_loading = False

        if getattr(self, "_loaded_case_id", None) != storage_id:
            self._case_saved = False
            return result
        self._capture_saved_snapshot()
        self.title(f"YomCeph Desktop · v{APP_VERSION}")
        return result

    def open_image(self):
        if getattr(self, "original", None) is not None:
            messagebox.showwarning(
                "Caso activo protegido",
                "Ya hay una radiografía cargada. Para evitar reemplazar por accidente "
                "la imagen o los puntos de este caso, guarde el trabajo y use “＋ Caso” "
                "antes de abrir otra radiografía.",
            )
            return
        try:
            result = super().open_image()
        except Exception as exc:
            messagebox.showerror(
                "Radiografía",
                "No se pudo abrir el archivo seleccionado. El caso actual no fue modificado.\n\n"
                + str(exc),
            )
            return
        self._sync_dirty_state()
        return result

    def _confirm_discard_unsaved(self):
        if not self._has_unsaved_case():
            return True
        return messagebox.askyesno(
            "Cambios sin guardar",
            "El caso actual tiene cambios sin guardar.\n\n¿Desea descartarlos y continuar?",
        )

    def _reset_case_specific_state(self):
        self._v123_internal_mutation = True
        try:
            self.image_path = None
            self.original = None
            self.tk_image = None
            self.points = {}
            self.results_cache = {}
            self.mm_per_pixel = None
            self.calibration_points = []
            self.calibrating = False
            if hasattr(self, "calibration_real_mm"):
                self.calibration_real_mm = None
            if hasattr(self, "_calibration_backup"):
                self._calibration_backup = None
            self._loaded_case_id = None
            self._case_saved = False
            if hasattr(self, "_qc_warnings"):
                self._qc_warnings = []

            for name in (
                "case_id", "age_years_var", "age_months_var", "birth_date_var",
                "radiograph_date_var", "sex_code_var", "gender_identity_var", "clinic_var",
            ):
                var = getattr(self, name, None)
                if var is not None:
                    var.set("")
            if hasattr(self, "sex_var"):
                self.sex_var.set("")
            if hasattr(self, "face_direction"):
                self.face_direction.set("right")

            self.case_group_values = {}
            self.manual_eligibility = "pending"
            try:
                self.cal_label.config(text="Sin calibración")
            except Exception:
                pass
            try:
                self.results_text.config(state=tk.NORMAL)
                self.results_text.delete("1.0", tk.END)
                self.results_text.config(state=tk.DISABLED)
            except Exception:
                pass
            try:
                self.redraw()
            except Exception:
                pass
            self._apply_selected_measurements()
            try:
                self._refresh_quality_control()
            except Exception:
                try:
                    self._refresh_case_state()
                except Exception:
                    pass
            self._update_compact_context()
        finally:
            self._v123_internal_mutation = False

        self._v123_saved_snapshot = self._case_snapshot()
        self._v123_snapshot_is_persisted = False
        self._case_saved = False

    def new_case(self):
        if not self._confirm_discard_unsaved():
            return False
        self._reset_case_specific_state()
        self.status.config(text="Nuevo caso preparado. Capture los datos y abra la radiografía.")
        return True

    def next_case(self):
        if not self._confirm_discard_unsaved():
            return False
        next_id = ""
        if self.workflow_type == "research" and self.current_study_id:
            try:
                with sqlite3.connect(self._db_path) as con:
                    rows = [
                        row[0]
                        for row in con.execute(
                            "SELECT local_case_id FROM cases WHERE research_study_id=?",
                            (self.current_study_id,),
                        ).fetchall()
                        if str(row[0] or "").isdigit()
                    ]
                next_id = str(max([int(value) for value in rows], default=0) + 1)
            except Exception:
                next_id = ""

        self._reset_case_specific_state()
        self._v123_internal_mutation = True
        try:
            self.case_id.set(next_id)
        finally:
            self._v123_internal_mutation = False
        self._sync_dirty_state()
        self.open_case_data(first_time=True)
        return True

    def _return_to_workflow_home(self):
        if not self._confirm_discard_unsaved():
            return
        self._reset_case_specific_state()
        self.workflow_type = "individual"
        self.current_study_id = None
        self.current_study = None
        self.case_group_values = {}
        self.manual_eligibility = "pending"
        self._startup_home_shown = False
        self._update_compact_context()
        self.after(0, self._show_workflow_home)

    def _open_protocol_from_menu(self):
        if self._has_unsaved_case():
            messagebox.showinfo(
                "Protocolo",
                "Guarde o descarte el caso actual antes de editar el protocolo de investigación.",
            )
            return
        return super()._open_protocol_from_menu()

    def choose_analysis_mode(self, startup=False):
        if not startup and self._has_unsaved_case():
            messagebox.showinfo(
                "Análisis",
                "Guarde o descarte el caso actual antes de cambiar los análisis o resultados.",
            )
            return
        return super().choose_analysis_mode(startup=startup)

    def export_research_package(self):
        if self._has_unsaved_case():
            messagebox.showinfo(
                "Exportar",
                "El caso actual tiene cambios sin guardar. Guárdelo antes de exportar para que la base y los archivos coincidan.",
            )
            return
        return super().export_research_package()

    def _request_close(self):
        if self._has_unsaved_case() and not messagebox.askyesno(
            "Salir de YomCeph",
            "Hay cambios sin guardar en el caso actual.\n\n¿Salir y descartarlos?",
        ):
            return
        try:
            self.destroy()
        except tk.TclError:
            pass

    def _poll_update_queue(self):
        try:
            while True:
                item = self._v123_update_queue.get_nowait()
                if item[0] == "check":
                    _, update, error, manual = item
                    self._finish_update_check(update, error, manual)
                elif item[0] == "download":
                    _, update, installer, error = item
                    self._finish_update_download(update, installer, error)
        except queue.Empty:
            pass
        except tk.TclError:
            return
        try:
            self.after(150, self._poll_update_queue)
        except (tk.TclError, RuntimeError):
            pass

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
                installer = distribution.download_verified_installer(update, destination, APP_VERSION)
                error = None
            except Exception as exc:
                installer = None
                error = exc
            self._v123_update_queue.put(("download", update, installer, error))

        threading.Thread(target=worker, name="YomCephUpdateDownload", daemon=True).start()


if __name__ == "__main__":
    ui.enable_dpi_awareness()
    app = YomCephV123Hardening()
    app.mainloop()
