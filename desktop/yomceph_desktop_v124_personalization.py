"""Personalización visual de YomCeph Desktop v0.12.4.

Añade una barra compacta de apariencia, selector de tipografía y tamaño y cinco
paletas de color. Las preferencias se guardan localmente junto a los datos de la
aplicación; nunca se envían fuera del equipo.
"""

from __future__ import annotations

import json
import tkinter as tk
from pathlib import Path
from tkinter import font as tkfont
from tkinter import messagebox, ttk

import yomceph_desktop_hidpi as ui
import yomceph_desktop_v120_distribution as distribution
import yomceph_desktop_v123_hardening as hardening

APP_VERSION = "0.12.4"
hardening.APP_VERSION = APP_VERSION
distribution.APP_VERSION = APP_VERSION

REQUIRED_COLOR_KEYS = tuple(ui.C.keys())
DEFAULT_PREFERENCES = {
    "font_family": "Segoe UI",
    "font_size": 10,
    "palette": "YomCeph violeta",
}

PALETTES = {
    "YomCeph violeta": {
        "purple": "#6E4A9E",
        "purple_dark": "#4E3474",
        "lilac": "#DCCCF2",
        "lilac_soft": "#F3EEFA",
        "mint": "#DDF4EA",
        "mint_deep": "#2F806F",
        "turquoise": "#43B9A8",
        "turquoise_dark": "#247E73",
        "gold": "#D6AD55",
        "gold_dark": "#8F6B1E",
        "paper": "#FBF9FD",
        "panel": "#FFFFFF",
        "text": "#2F2B35",
        "muted": "#6D6576",
        "canvas": "#0B0B10",
        "border": "#E7E0EE",
    },
    "Noche radiográfica": {
        "purple": "#8468B6",
        "purple_dark": "#5E4787",
        "lilac": "#4B405C",
        "lilac_soft": "#2A2531",
        "mint": "#243D37",
        "mint_deep": "#A6E0D1",
        "turquoise": "#43B9A8",
        "turquoise_dark": "#65D1C1",
        "gold": "#D9B65F",
        "gold_dark": "#F0CF79",
        "paper": "#15131A",
        "panel": "#1F1C25",
        "text": "#F5F2F7",
        "muted": "#BFB7C8",
        "canvas": "#050507",
        "border": "#3A3344",
    },
    "Azul clínico": {
        "purple": "#34699A",
        "purple_dark": "#244B70",
        "lilac": "#CFE1F2",
        "lilac_soft": "#EEF5FB",
        "mint": "#DDF3F1",
        "mint_deep": "#236D68",
        "turquoise": "#2A9D8F",
        "turquoise_dark": "#1E7168",
        "gold": "#E3B653",
        "gold_dark": "#8B681C",
        "paper": "#F6FAFD",
        "panel": "#FFFFFF",
        "text": "#24313C",
        "muted": "#5E6C78",
        "canvas": "#07121C",
        "border": "#D9E6EF",
    },
    "Menta suave": {
        "purple": "#4D7C70",
        "purple_dark": "#31594F",
        "lilac": "#CEE8DF",
        "lilac_soft": "#EEF8F4",
        "mint": "#D9F2E7",
        "mint_deep": "#286556",
        "turquoise": "#3A9D89",
        "turquoise_dark": "#26715F",
        "gold": "#D5B45C",
        "gold_dark": "#846B28",
        "paper": "#F7FBF9",
        "panel": "#FFFFFF",
        "text": "#263631",
        "muted": "#61716B",
        "canvas": "#08100E",
        "border": "#DCEAE4",
    },
    "Arena cálida": {
        "purple": "#80604F",
        "purple_dark": "#5D4437",
        "lilac": "#E7D7C8",
        "lilac_soft": "#F8F1E9",
        "mint": "#E7EFE4",
        "mint_deep": "#526A4D",
        "turquoise": "#668F85",
        "turquoise_dark": "#476C63",
        "gold": "#D2A74F",
        "gold_dark": "#80601F",
        "paper": "#FCF8F2",
        "panel": "#FFFDFC",
        "text": "#3D332D",
        "muted": "#74665E",
        "canvas": "#100D0B",
        "border": "#E8DDD2",
    },
}


def normalize_preferences(value):
    """Normaliza preferencias leídas de disco sin confiar en su contenido."""
    value = value if isinstance(value, dict) else {}
    palette = str(value.get("palette") or DEFAULT_PREFERENCES["palette"])
    if palette not in PALETTES:
        palette = DEFAULT_PREFERENCES["palette"]
    family = str(value.get("font_family") or DEFAULT_PREFERENCES["font_family"]).strip()
    if not family or len(family) > 100:
        family = DEFAULT_PREFERENCES["font_family"]
    try:
        size = int(value.get("font_size", DEFAULT_PREFERENCES["font_size"]))
    except (TypeError, ValueError):
        size = DEFAULT_PREFERENCES["font_size"]
    size = max(8, min(18, size))
    return {"font_family": family, "font_size": size, "palette": palette}


def _hex_rgb(value):
    value = str(value).lstrip("#")
    if len(value) != 6:
        raise ValueError("color hexadecimal inválido")
    return tuple(int(value[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


def _relative_luminance(value):
    channels = []
    for channel in _hex_rgb(value):
        channels.append(channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4)
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def contrast_ratio(a, b):
    la, lb = _relative_luminance(a), _relative_luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


class YomCephV124Personalization(hardening.YomCephV123Hardening):
    """v0.12.4: endurecimiento v0.12.3 + personalización persistente."""

    def __init__(self):
        self._personalization = dict(DEFAULT_PREFERENCES)
        self._personalization_palette_snapshot = dict(ui.C)
        self._personalization_map_job = None
        super().__init__()
        self.title(f"YomCeph Desktop · v{APP_VERSION}")
        self._preferences_path = Path(self._data_dir) / "ui_preferences.json"
        self._personalization = self._load_personalization()
        self._apply_personalization(self._personalization, persist=False)
        self.bind_all("<Map>", self._on_widget_mapped, add="+")

    def _apply_language(self):
        try:
            self.title(f"YomCeph Desktop · v{APP_VERSION}")
        except tk.TclError:
            pass

    # ------------------------------------------------------------------
    # Barra y diálogo
    # ------------------------------------------------------------------
    def _install_database_bar(self):
        super()._install_database_bar()
        self.personalization_bar = ttk.Frame(self, padding=(5, 1))
        try:
            self.personalization_bar.pack(fill=tk.X, before=self.body_panes)
        except Exception:
            self.personalization_bar.pack(fill=tk.X)

        ttk.Label(self.personalization_bar, text="Vista:", style="Muted.TLabel").pack(side=tk.LEFT, padx=(2, 4))
        self.personalization_summary = ttk.Label(
            self.personalization_bar,
            text="YomCeph violeta · Segoe UI 10",
            style="Muted.TLabel",
        )
        self.personalization_summary.pack(side=tk.LEFT)
        ttk.Button(
            self.personalization_bar,
            text="A−",
            width=3,
            command=lambda: self._quick_font_step(-1),
            style="Soft.TButton",
        ).pack(side=tk.RIGHT, padx=1)
        ttk.Button(
            self.personalization_bar,
            text="A+",
            width=3,
            command=lambda: self._quick_font_step(1),
            style="Soft.TButton",
        ).pack(side=tk.RIGHT, padx=1)
        ttk.Button(
            self.personalization_bar,
            text="⚙ Configuración",
            command=self.open_personalization_settings,
            style="Soft.TButton",
        ).pack(side=tk.RIGHT, padx=(3, 2))

        menu = self._get_more_menu()
        if menu is not None and "Personalización…" not in self._menu_labels(menu):
            menu.add_separator()
            menu.add_command(label="Personalización…", command=self.open_personalization_settings)

    def _quick_font_step(self, delta):
        prefs = dict(self._personalization)
        prefs["font_size"] = max(8, min(18, int(prefs.get("font_size", 10)) + int(delta)))
        self._apply_personalization(prefs, persist=True)

    def open_personalization_settings(self):
        win = tk.Toplevel(self)
        win.title("YomCeph · Personalización")
        win.transient(self)
        win.grab_set()
        win.resizable(False, False)

        frame = ttk.Frame(win, padding=18)
        frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(frame, text="Apariencia de YomCeph", style="Section.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 4)
        )
        ttk.Label(
            frame,
            text="Los cambios son sólo visuales. No modifican radiografías, puntos, mediciones ni resultados.",
            style="Muted.TLabel",
            wraplength=520,
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 14))

        families = sorted({str(name) for name in tkfont.families(self) if str(name).strip()}, key=str.casefold)
        current_family = self._personalization.get("font_family", "Segoe UI")
        if current_family not in families:
            families.insert(0, current_family)
        family_var = tk.StringVar(value=current_family)
        size_var = tk.IntVar(value=int(self._personalization.get("font_size", 10)))
        palette_var = tk.StringVar(value=self._personalization.get("palette", DEFAULT_PREFERENCES["palette"]))

        ttk.Label(frame, text="Tipo de letra:").grid(row=2, column=0, sticky="w", pady=5)
        ttk.Combobox(frame, textvariable=family_var, values=families, state="readonly", width=38).grid(
            row=2, column=1, sticky="ew", pady=5
        )
        ttk.Label(frame, text="Tamaño base:").grid(row=3, column=0, sticky="w", pady=5)
        ttk.Spinbox(frame, from_=8, to=18, textvariable=size_var, width=8).grid(
            row=3, column=1, sticky="w", pady=5
        )
        ttk.Label(frame, text="Paleta de color:").grid(row=4, column=0, sticky="w", pady=5)
        palette_combo = ttk.Combobox(
            frame,
            textvariable=palette_var,
            values=list(PALETTES),
            state="readonly",
            width=38,
        )
        palette_combo.grid(row=4, column=1, sticky="ew", pady=5)

        preview = tk.Frame(frame, bd=0, padx=10, pady=9)
        preview.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(12, 8))
        preview_title = tk.Label(preview, text="Vista previa · YomCeph", anchor="w")
        preview_title.pack(fill=tk.X)
        preview_text = tk.Label(
            preview,
            text="Texto, botones y paneles mantendrán contraste legible.",
            anchor="w",
        )
        preview_text.pack(fill=tk.X, pady=(3, 0))

        def refresh_preview(*_args):
            palette = PALETTES.get(palette_var.get(), PALETTES[DEFAULT_PREFERENCES["palette"]])
            try:
                size = max(8, min(18, int(size_var.get())))
            except (tk.TclError, ValueError):
                size = 10
            family = family_var.get() or "Segoe UI"
            preview.configure(bg=palette["panel"], highlightbackground=palette["border"], highlightthickness=1)
            preview_title.configure(
                bg=palette["panel"], fg=palette["purple_dark"], font=(family, size + 2, "bold")
            )
            preview_text.configure(bg=palette["panel"], fg=palette["text"], font=(family, size))

        family_var.trace_add("write", refresh_preview)
        size_var.trace_add("write", refresh_preview)
        palette_var.trace_add("write", refresh_preview)
        refresh_preview()

        buttons = ttk.Frame(frame)
        buttons.grid(row=6, column=0, columnspan=2, sticky="e", pady=(12, 0))

        def selected_preferences():
            return normalize_preferences(
                {
                    "font_family": family_var.get(),
                    "font_size": size_var.get(),
                    "palette": palette_var.get(),
                }
            )

        ttk.Button(
            buttons,
            text="Restaurar",
            command=lambda: self._reset_personalization_dialog(
                family_var, size_var, palette_var, refresh_preview
            ),
            style="Soft.TButton",
        ).pack(side=tk.LEFT, padx=3)
        ttk.Button(
            buttons,
            text="Aplicar",
            command=lambda: self._apply_personalization(selected_preferences(), persist=False),
            style="Turquoise.TButton",
        ).pack(side=tk.LEFT, padx=3)

        def save_and_close():
            self._apply_personalization(selected_preferences(), persist=True)
            try:
                win.grab_release()
            except tk.TclError:
                pass
            win.destroy()

        ttk.Button(buttons, text="Guardar", command=save_and_close, style="Purple.TButton").pack(
            side=tk.LEFT, padx=3
        )
        ttk.Button(buttons, text="Cerrar", command=win.destroy, style="Soft.TButton").pack(
            side=tk.LEFT, padx=3
        )

        frame.columnconfigure(1, weight=1)
        win.update_idletasks()
        w, h = win.winfo_reqwidth(), win.winfo_reqheight()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        win.geometry(f"{w}x{h}+{max(0, (sw-w)//2)}+{max(0, (sh-h)//2)}")

    def _reset_personalization_dialog(self, family_var, size_var, palette_var, refresh):
        family_var.set(DEFAULT_PREFERENCES["font_family"])
        size_var.set(DEFAULT_PREFERENCES["font_size"])
        palette_var.set(DEFAULT_PREFERENCES["palette"])
        refresh()

    # ------------------------------------------------------------------
    # Persistencia segura
    # ------------------------------------------------------------------
    def _load_personalization(self):
        try:
            raw = json.loads(self._preferences_path.read_text(encoding="utf-8"))
        except (OSError, ValueError, TypeError):
            return dict(DEFAULT_PREFERENCES)
        return normalize_preferences(raw)

    def _save_personalization(self):
        prefs = normalize_preferences(self._personalization)
        try:
            self._preferences_path.parent.mkdir(parents=True, exist_ok=True)
            temp = self._preferences_path.with_suffix(".tmp")
            temp.write_text(json.dumps(prefs, ensure_ascii=False, indent=2), encoding="utf-8")
            temp.replace(self._preferences_path)
        except OSError as exc:
            messagebox.showwarning(
                "Personalización",
                "La apariencia se aplicó para esta sesión, pero no se pudo guardar como preferencia.\n\n"
                + str(exc),
            )

    # ------------------------------------------------------------------
    # Aplicación de tipografía y color
    # ------------------------------------------------------------------
    def _apply_personalization(self, preferences, persist=False):
        prefs = normalize_preferences(preferences)
        old_palette = dict(self._personalization_palette_snapshot or ui.C)
        new_palette = dict(PALETTES[prefs["palette"]])
        ui.C.clear()
        ui.C.update(new_palette)
        self._personalization_palette_snapshot = dict(new_palette)
        self._personalization = prefs

        self._configure_personalization_styles(prefs)
        self._apply_widget_tree(self, old_palette, new_palette, prefs)
        self._update_personalization_summary()
        try:
            self.redraw()
        except Exception:
            pass
        try:
            self.draw_vertebral_guide()
        except Exception:
            pass
        if persist:
            self._save_personalization()

    def _configure_personalization_styles(self, prefs):
        family = prefs["font_family"]
        size = prefs["font_size"]
        c = ui.C
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(".", font=(family, size), background=c["paper"], foreground=c["text"])
        style.configure("TFrame", background=c["paper"])
        style.configure("Panel.TFrame", background=c["panel"])
        style.configure("TLabel", background=c["paper"], foreground=c["text"], font=(family, size))
        style.configure("Panel.TLabel", background=c["panel"], foreground=c["text"], font=(family, size))
        style.configure(
            "Section.TLabel",
            background=c["panel"],
            foreground=c["purple_dark"],
            font=(family, size + 1, "bold"),
        )
        style.configure(
            "Muted.TLabel",
            background=c["panel"],
            foreground=c["muted"],
            font=(family, max(8, size - 1)),
        )
        style.configure("Purple.TButton", background=c["purple"], foreground="white", font=(family, size))
        style.map("Purple.TButton", background=[("active", c["purple_dark"])])
        style.configure("Mint.TButton", background=c["mint"], foreground=c["mint_deep"], font=(family, size))
        style.map("Mint.TButton", background=[("active", c["lilac"])])
        style.configure("Turquoise.TButton", background=c["turquoise"], foreground="white", font=(family, size))
        style.map("Turquoise.TButton", background=[("active", c["turquoise_dark"])])
        style.configure("Gold.TButton", background=c["gold"], foreground="#2F2616", font=(family, size, "bold"))
        style.map("Gold.TButton", background=[("active", c["gold_dark"])])
        style.configure("Soft.TButton", background=c["lilac_soft"], foreground=c["purple_dark"], font=(family, size))
        style.map("Soft.TButton", background=[("active", c["lilac"])])
        style.configure("TNotebook", background=c["paper"])
        style.configure("TNotebook.Tab", background=c["lilac_soft"], foreground=c["purple_dark"], font=(family, size, "bold"))
        style.map(
            "TNotebook.Tab",
            background=[("selected", c["mint"])],
            foreground=[("selected", c["turquoise_dark"])],
        )
        style.configure("TRadiobutton", background=c["panel"], foreground=c["text"], font=(family, size))
        style.configure("TCheckbutton", background=c["panel"], foreground=c["text"], font=(family, size))
        style.configure("Horizontal.TProgressbar", troughcolor=c["lilac_soft"], background=c["turquoise"])

        for named in (
            "TkDefaultFont",
            "TkTextFont",
            "TkMenuFont",
            "TkHeadingFont",
            "TkCaptionFont",
            "TkSmallCaptionFont",
            "TkIconFont",
            "TkTooltipFont",
        ):
            try:
                font = tkfont.nametofont(named)
                font.configure(family=family, size=size)
            except tk.TclError:
                pass

    @staticmethod
    def _mapped_color(value, old_palette, new_palette):
        if not value:
            return value
        text = str(value).lower()
        for key in REQUIRED_COLOR_KEYS:
            if str(old_palette.get(key, "")).lower() == text:
                return new_palette[key]
        return value

    def _apply_widget_tree(self, root, old_palette=None, new_palette=None, prefs=None):
        old_palette = old_palette or dict(self._personalization_palette_snapshot)
        new_palette = new_palette or dict(ui.C)
        prefs = prefs or self._personalization
        try:
            widgets = [root] + list(root.winfo_children())
        except tk.TclError:
            return
        for widget in widgets:
            try:
                self._apply_widget_appearance(widget, old_palette, new_palette, prefs)
            except (tk.TclError, ValueError):
                pass
            if widget is not root:
                self._apply_widget_tree(widget, old_palette, new_palette, prefs)

        # La barra de estado/QC usa colores propios en capas heredadas.
        try:
            self.case_state_frame.configure(bg=new_palette["lilac_soft"])
            self.case_state_label.configure(bg=new_palette["lilac_soft"], fg=new_palette["text"])
            self.qc_button.configure(
                bg=new_palette["lilac_soft"],
                fg=new_palette["text"],
                activebackground=new_palette["lilac"],
                activeforeground=new_palette["text"],
            )
        except (AttributeError, tk.TclError):
            pass

    def _apply_widget_appearance(self, widget, old_palette, new_palette, prefs):
        # Recolorea widgets tk clásicos que no obedecen a ttk.Style.
        options = set(widget.keys())
        for option in (
            "background",
            "bg",
            "foreground",
            "fg",
            "activebackground",
            "activeforeground",
            "selectbackground",
            "selectforeground",
            "highlightbackground",
            "highlightcolor",
        ):
            if option not in options:
                continue
            try:
                current = widget.cget(option)
                mapped = self._mapped_color(current, old_palette, new_palette)
                if mapped != current:
                    widget.configure(**{option: mapped})
            except tk.TclError:
                pass

        if "font" not in options:
            return
        if not hasattr(widget, "_yomceph_font_baseline"):
            try:
                actual = tkfont.Font(self, font=widget.cget("font")).actual()
                widget._yomceph_font_baseline = {
                    "size": abs(int(actual.get("size") or 10)),
                    "weight": actual.get("weight", "normal"),
                    "slant": actual.get("slant", "roman"),
                    "underline": int(bool(actual.get("underline", 0))),
                    "overstrike": int(bool(actual.get("overstrike", 0))),
                }
            except (tk.TclError, ValueError, TypeError):
                widget._yomceph_font_baseline = {
                    "size": 10,
                    "weight": "normal",
                    "slant": "roman",
                    "underline": 0,
                    "overstrike": 0,
                }
        base = widget._yomceph_font_baseline
        scaled = max(7, round(base["size"] * int(prefs["font_size"]) / 10.0))
        try:
            font = tkfont.Font(
                self,
                family=prefs["font_family"],
                size=scaled,
                weight=base["weight"],
                slant=base["slant"],
                underline=base["underline"],
                overstrike=base["overstrike"],
            )
            widget.configure(font=font)
            widget._yomceph_personal_font = font
        except tk.TclError:
            pass

    def _update_personalization_summary(self):
        try:
            self.personalization_summary.configure(
                text=(
                    f"{self._personalization['palette']} · "
                    f"{self._personalization['font_family']} {self._personalization['font_size']}"
                )
            )
        except (AttributeError, tk.TclError):
            pass

    def _on_widget_mapped(self, event):
        # Los diálogos heredados con fuentes explícitas también reciben la
        # personalización al aparecer, sin modificar su lógica clínica.
        try:
            top = event.widget.winfo_toplevel()
        except tk.TclError:
            return
        if top is self:
            return
        if self._personalization_map_job is not None:
            try:
                self.after_cancel(self._personalization_map_job)
            except tk.TclError:
                pass
        self._personalization_map_job = self.after(
            40,
            lambda: self._apply_widget_tree(top, dict(ui.C), dict(ui.C), self._personalization),
        )


if __name__ == "__main__":
    ui.enable_dpi_awareness()
    app = YomCephV124Personalization()
    app.mainloop()
