import json
import sqlite3
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, simpledialog, ttk

import yomceph_desktop_hidpi as ui
import yomceph_desktop_v11_database as v11db
import yomceph_desktop_v115 as v115
import yomceph_desktop_v116 as v116
import yomceph_desktop_v120 as v120
from yomceph_v120_geometry import jarabak_values, w_angle, wits_ao_bo, yen_angle

APP_VERSION = "0.12.0"
PUBLIC_STEINER_REFERENCES = {"none", "classic"}


class YomCephV120Final(v120.YomCephV120):
    """Entrada pública final de v0.12.0.

    Mantiene el constructor de investigaciones, pero no incluye ninguna escuela,
    universidad, clínica, muestra, país o protocolo institucional preconfigurado.
    Los datos heredados se conservan mediante una migración neutral.
    """

    def __init__(self):
        self._public_defaults_initialized = False
        super().__init__()

    def _ensure_metadata_vars(self):
        # v0.11.6 tenía valores de una investigación local como valores iniciales.
        # La edición pública parte siempre de un perfil general y campos vacíos.
        super()._ensure_metadata_vars()
        if not self._public_defaults_initialized:
            self.profile_var.set(v116.PROFILE_GENERAL)
            self.study_name_var.set("")
            self.study_target_var.set("")
            self.country_var.set("")
            self.institution_var.set("")
            self.steiner_reference = "none"
            self._public_defaults_initialized = True

    def _init_database(self):
        # Evita las migraciones institucionales heredadas de v0.11.6/v0.12 beta.
        # Se parte del esquema científico v0.11.5 y se añaden sólo campos genéricos.
        v115.YomCephV115._init_database(self)
        with sqlite3.connect(self._db_path) as con:
            existing = {row[1] for row in con.execute("PRAGMA table_info(cases)")}
            additions = {
                "app_profile": "TEXT",
                "study_name": "TEXT",
                "study_target": "INTEGER",
                "birth_date": "TEXT",
                "sex_code": "TEXT",
                "gender_identity": "TEXT",
                "country": "TEXT",
                "institution": "TEXT",
                "ui_language": "TEXT",
                "workflow_type": "TEXT",
                "research_study_id": "TEXT",
                "local_case_id": "TEXT",
                "study_groups_json": "TEXT",
                "eligibility_status": "TEXT",
                "eligibility_reason": "TEXT",
                "selected_measurements_json": "TEXT",
                "steiner_reference": "TEXT",
            }
            for name, sql_type in additions.items():
                if name not in existing:
                    con.execute(f"ALTER TABLE cases ADD COLUMN {name} {sql_type}")

            con.execute(
                """CREATE TABLE IF NOT EXISTS research_studies (
                    study_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    target_n INTEGER NOT NULL,
                    allow_target_increase INTEGER NOT NULL DEFAULT 1,
                    age_min INTEGER,
                    age_max INTEGER,
                    inclusion_criteria TEXT,
                    exclusion_criteria TEXT,
                    country TEXT,
                    institution TEXT,
                    group_fields_json TEXT NOT NULL DEFAULT '[]',
                    analyses_json TEXT NOT NULL DEFAULT '[]',
                    measurements_json TEXT NOT NULL DEFAULT '[]',
                    steiner_reference TEXT NOT NULL DEFAULT 'none',
                    protocol_version INTEGER NOT NULL DEFAULT 1,
                    protocol_locked INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )"""
            )

            now = datetime.now().isoformat(timespec="seconds")
            legacy_profile = "uam" + "2026"

            # Bases creadas con versiones previas pueden contener un perfil local.
            # Se conserva la información del usuario, pero se neutraliza la identidad
            # institucional y nunca se recrea en una instalación limpia.
            con.execute(
                """UPDATE cases
                   SET app_profile=?,
                       study_name=CASE WHEN study_name IS NULL OR study_name='' OR app_profile=?
                                       THEN 'Investigación importada' ELSE study_name END,
                       institution=CASE WHEN app_profile=? THEN '' ELSE institution END,
                       steiner_reference='none'
                   WHERE app_profile=?""",
                (v116.PROFILE_CUSTOM, legacy_profile, legacy_profile, legacy_profile),
            )

            old_study = con.execute(
                "SELECT 1 FROM research_studies WHERE study_id=?", (legacy_profile,)
            ).fetchone()
            if old_study:
                linked = con.execute(
                    "SELECT COUNT(*) FROM cases WHERE research_study_id=?", (legacy_profile,)
                ).fetchone()[0]
                if linked == 0:
                    con.execute("DELETE FROM research_studies WHERE study_id=?", (legacy_profile,))
                else:
                    neutral_id = "investigacion_importada"
                    suffix = 2
                    while con.execute(
                        "SELECT 1 FROM research_studies WHERE study_id=?", (neutral_id,)
                    ).fetchone():
                        neutral_id = f"investigacion_importada_{suffix}"
                        suffix += 1
                    con.execute(
                        """UPDATE research_studies
                           SET study_id=?, name='Investigación importada', institution='',
                               group_fields_json='[]', inclusion_criteria='', exclusion_criteria='',
                               steiner_reference='none', updated_at=?
                           WHERE study_id=?""",
                        (neutral_id, now, legacy_profile),
                    )
                    con.execute(
                        """UPDATE cases
                           SET research_study_id=?, app_profile=?,
                               study_name='Investigación importada', institution='',
                               steiner_reference='none'
                           WHERE research_study_id=?""",
                        (neutral_id, v116.PROFILE_CUSTOM, legacy_profile),
                    )

            # Importación genérica de investigaciones antiguas basada sólo en los
            # datos existentes del usuario; no se inyectan nombres ni centros.
            old_rows = con.execute(
                """SELECT DISTINCT study_name
                   FROM cases
                   WHERE (workflow_type IS NULL OR workflow_type='')
                     AND study_name IS NOT NULL AND TRIM(study_name)<>''"""
            ).fetchall()
            default_measures = [
                key for key in list(v11db.STEINER_ORDER) + list(v11db.POSTURE_ORDER)
                if key in v120.MEASUREMENTS
            ]
            default_analyses = []
            for key in default_measures:
                aid = v120.MEASUREMENTS[key]["analysis"]
                if aid not in default_analyses:
                    default_analyses.append(aid)

            for (study_name,) in old_rows:
                cases = con.execute(
                    "SELECT case_id, study_target, country, institution FROM cases WHERE study_name=?",
                    (study_name,),
                ).fetchall()
                if not cases:
                    continue
                target = max(
                    [row[1] for row in cases if isinstance(row[1], int) and row[1] > 0]
                    or [len(cases)]
                )
                country = next((row[2] for row in cases if row[2]), "")
                institution = next((row[3] for row in cases if row[3]), "")
                base = "legacy_" + v120._safe_id(study_name)
                study_id = base
                i = 2
                while con.execute(
                    "SELECT 1 FROM research_studies WHERE study_id=?", (study_id,)
                ).fetchone():
                    study_id = f"{base}_{i}"
                    i += 1
                con.execute(
                    """INSERT INTO research_studies(
                        study_id,name,target_n,allow_target_increase,age_min,age_max,
                        inclusion_criteria,exclusion_criteria,country,institution,
                        group_fields_json,analyses_json,measurements_json,steiner_reference,
                        protocol_version,protocol_locked,created_at,updated_at
                    ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (
                        study_id, study_name, target, 1, None, None, "", "", country,
                        institution, "[]", json.dumps(default_analyses, ensure_ascii=False),
                        json.dumps(default_measures, ensure_ascii=False), "none", 1, 1,
                        now, now,
                    ),
                )
                con.execute(
                    """UPDATE cases
                       SET workflow_type='research', research_study_id=?,
                           local_case_id=COALESCE(NULLIF(local_case_id,''),case_id),
                           app_profile=?, eligibility_status=COALESCE(eligibility_status,'eligible'),
                           selected_measurements_json=COALESCE(NULLIF(selected_measurements_json,''),?),
                           steiner_reference='none'
                       WHERE study_name=? AND (workflow_type IS NULL OR workflow_type='')""",
                    (
                        study_id, v116.PROFILE_CUSTOM,
                        json.dumps(default_measures, ensure_ascii=False), study_name,
                    ),
                )

            con.execute(
                """UPDATE cases
                   SET workflow_type='individual',
                       local_case_id=COALESCE(NULLIF(local_case_id,''),case_id),
                       app_profile=COALESCE(NULLIF(app_profile,''),?),
                       steiner_reference=CASE
                           WHEN steiner_reference='classic' THEN 'classic' ELSE 'none' END
                   WHERE workflow_type IS NULL OR workflow_type=''""",
                (v116.PROFILE_GENERAL,),
            )
            con.commit()

    def _show_workflow_home(self):
        if self._startup_home_shown:
            return
        self._startup_home_shown = True
        win = tk.Toplevel(self)
        win.title("YomCeph · ¿Qué vamos a hacer hoy?")
        win.transient(self)
        win.grab_set()
        win.configure(bg=ui.C["paper"])
        win.protocol("WM_DELETE_WINDOW", lambda: (win.destroy(), self.destroy()))
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        w, h = min(790, int(sw * .9)), min(540, int(sh * .84))
        win.geometry(f"{w}x{h}+{max(0, (sw-w)//2)}+{max(0, (sh-h)//2)}")

        head = tk.Frame(win, bg=ui.C["purple"], padx=28, pady=20)
        head.pack(fill=tk.X)
        tk.Label(
            head, text="¿Qué vamos a hacer hoy?", bg=ui.C["purple"], fg="white",
            font=("Segoe UI Semibold", 22),
        ).pack(anchor="w")
        tk.Label(
            head,
            text="Elige el objetivo. YomCeph mostrará sólo los datos y puntos necesarios.",
            bg=ui.C["purple"], fg=ui.C["lilac_soft"], font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(4, 0))

        body = ttk.Frame(win, padding=24)
        body.pack(fill=tk.BOTH, expand=True)
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        ind = ttk.LabelFrame(body, text="👤 Caso individual", padding=18)
        ind.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        ttk.Label(
            ind,
            text="Una radiografía o un paciente para revisar. No entra en estadísticas de investigación.",
            wraplength=300,
        ).pack(anchor="w", pady=(0, 18))
        ttk.Button(
            ind, text="Trabajar caso individual",
            command=lambda: self._start_individual(win), style="Purple.TButton",
        ).pack(fill=tk.X)

        res = ttk.LabelFrame(body, text="📊 Investigación", padding=18)
        res.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        ttk.Label(
            res,
            text="Crea tu propio protocolo: muestra, edades, grupos, criterios, análisis y resultados.",
            wraplength=300,
        ).pack(anchor="w", pady=(0, 10))
        ttk.Button(
            res, text="Nueva investigación",
            command=lambda: self._new_research(win), style="Gold.TButton",
        ).pack(fill=tk.X, pady=3)
        ttk.Button(
            res, text="Abrir investigación existente",
            command=lambda: self._choose_existing_study(win), style="Soft.TButton",
        ).pack(fill=tk.X, pady=3)

    def _activate_study(self, study_id, close_window=None):
        study = self._get_study(study_id)
        if not study:
            messagebox.showerror("Investigación", "No se pudo abrir el protocolo.")
            return
        if close_window:
            try:
                close_window.destroy()
            except Exception:
                pass
        self.workflow_type = "research"
        self.current_study_id = study_id
        self.current_study = study
        self.selected_measure_keys = [k for k in study["measurements"] if k in v120.MEASUREMENTS]
        ref = study.get("steiner_reference") or "none"
        self.steiner_reference = ref if ref in PUBLIC_STEINER_REFERENCES else "none"
        self.case_group_values = {}
        self.manual_eligibility = "pending"
        self.analysis_mode = "Ambos"
        self.profile_var.set(v116.PROFILE_CUSTOM)
        self.study_name_var.set(study["name"])
        self.study_target_var.set(str(study["target_n"]))
        self.country_var.set(study.get("country") or "")
        self.institution_var.set(study.get("institution") or "")
        self._apply_selected_measurements()
        self._update_compact_context()
        self._update_db_counter()
        self.status.config(text=f"Investigación activa: {study['name']}. Capture los datos del caso.")
        self.open_case_data(first_time=True)

    def open_protocol_editor(self, new_study=False):
        existing = None if new_study else self.current_study
        if existing and existing.get("protocol_locked"):
            self._show_locked_protocol(existing)
            return

        win = tk.Toplevel(self)
        win.title("YomCeph · Protocolo de investigación")
        win.transient(self)
        win.grab_set()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        w, h = min(980, int(sw * .94)), min(820, int(sh * .92))
        win.geometry(f"{w}x{h}+{max(0, (sw-w)//2)}+{max(0, (sh-h)//2)}")
        outer = ttk.Frame(win)
        outer.pack(fill=tk.BOTH, expand=True)
        canvas = tk.Canvas(outer, bg=ui.C["paper"], highlightthickness=0)
        scroll = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        content = ttk.Frame(canvas, padding=18)
        cid = canvas.create_window((0, 0), window=content, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(cid, width=e.width))

        ttk.Label(
            content, text="Diseño de la investigación", style="Section.TLabel",
            font=("Segoe UI Semibold", 17),
        ).pack(anchor="w")
        ttk.Label(
            content,
            text="Define tu protocolo. Se bloqueará después del primer caso incluido para proteger la reproducibilidad.",
            style="Muted.TLabel",
        ).pack(anchor="w", pady=(2, 10))

        basics = ttk.LabelFrame(content, text="1 · Muestra y criterios", padding=12)
        basics.pack(fill=tk.X, pady=5)
        name_var = tk.StringVar(value=(existing or {}).get("name", ""))
        target_value = "" if not existing else str(existing.get("target_n", ""))
        target_var = tk.StringVar(value=target_value)
        allow_inc = tk.BooleanVar(value=bool((existing or {}).get("allow_target_increase", 1)))
        amin_var = tk.StringVar(value="" if (existing or {}).get("age_min") is None else str(existing["age_min"]))
        amax_var = tk.StringVar(value="" if (existing or {}).get("age_max") is None else str(existing["age_max"]))
        country_var = tk.StringVar(value=(existing or {}).get("country", ""))
        institution_var = tk.StringVar(value=(existing or {}).get("institution", ""))
        existing_ref = (existing or {}).get("steiner_reference", "none")
        steiner_var = tk.StringVar(value=existing_ref if existing_ref in PUBLIC_STEINER_REFERENCES else "none")

        grid = ttk.Frame(basics)
        grid.pack(fill=tk.X)
        for c in (1, 3):
            grid.columnconfigure(c, weight=1)
        ttk.Label(grid, text="Nombre:").grid(row=0, column=0, sticky="w", pady=3)
        ttk.Entry(grid, textvariable=name_var).grid(row=0, column=1, columnspan=3, sticky="ew", padx=4, pady=3)
        ttk.Label(grid, text="Muestra planeada:").grid(row=1, column=0, sticky="w", pady=3)
        ttk.Entry(grid, textvariable=target_var, width=8).grid(row=1, column=1, sticky="w", padx=4, pady=3)
        ttk.Checkbutton(
            grid, text="Permitir aumentar la muestra posteriormente", variable=allow_inc,
        ).grid(row=1, column=2, columnspan=2, sticky="w", pady=3)
        ttk.Label(grid, text="Edad mínima:").grid(row=2, column=0, sticky="w", pady=3)
        ttk.Entry(grid, textvariable=amin_var, width=8).grid(row=2, column=1, sticky="w", padx=4, pady=3)
        ttk.Label(grid, text="Edad máxima:").grid(row=2, column=2, sticky="w", pady=3)
        ttk.Entry(grid, textvariable=amax_var, width=8).grid(row=2, column=3, sticky="w", padx=4, pady=3)
        ttk.Label(grid, text="País:").grid(row=3, column=0, sticky="w", pady=3)
        ttk.Entry(grid, textvariable=country_var).grid(row=3, column=1, sticky="ew", padx=4, pady=3)
        ttk.Label(grid, text="Institución (opcional):").grid(row=3, column=2, sticky="w", pady=3)
        ttk.Entry(grid, textvariable=institution_var).grid(row=3, column=3, sticky="ew", padx=4, pady=3)
        ttk.Label(basics, text="Criterios de inclusión:").pack(anchor="w", pady=(6, 2))
        inclusion = tk.Text(basics, height=3, wrap=tk.WORD)
        inclusion.pack(fill=tk.X)
        inclusion.insert("1.0", (existing or {}).get("inclusion_criteria", ""))
        ttk.Label(basics, text="Criterios de exclusión:").pack(anchor="w", pady=(6, 2))
        exclusion = tk.Text(basics, height=3, wrap=tk.WORD)
        exclusion.pack(fill=tk.X)
        exclusion.insert("1.0", (existing or {}).get("exclusion_criteria", ""))

        groups = ttk.LabelFrame(content, text="2 · Procedencia, grupo o momento", padding=12)
        groups.pack(fill=tk.X, pady=5)
        ttk.Label(
            groups, text="Una variable por línea: Nombre=opción1|opción2|opción3",
            style="Muted.TLabel",
        ).pack(anchor="w")
        ttk.Label(
            groups,
            text="Ej.: Centro=Centro A|Centro B · Grupo=Caso|Control · Momento=Pre|Post",
        ).pack(anchor="w", pady=(2, 5))
        group_text = tk.Text(groups, height=5, wrap=tk.WORD)
        group_text.pack(fill=tk.X)
        if existing:
            group_text.insert(
                "1.0",
                "\n".join(
                    f"{field.get('name', 'Grupo')}=" + "|".join(field.get("options", []))
                    for field in existing.get("group_fields", [])
                ),
            )

        analyses_box = ttk.LabelFrame(content, text="3 · Análisis y resultados", padding=12)
        analyses_box.pack(fill=tk.X, pady=5)
        ttk.Label(
            analyses_box,
            text="Puede combinar análisis. Sólo las mediciones con geometría verificada se pueden activar.",
            style="Muted.TLabel",
        ).pack(anchor="w", pady=(0, 6))
        selected = set((existing or {}).get("measurements", []))
        analysis_vars = {}
        measure_vars = {}
        for aid, spec in v120.ANALYSES.items():
            fr = ttk.LabelFrame(analyses_box, text=spec["name"], padding=7)
            fr.pack(fill=tk.X, pady=3)
            active = v120.analysis_measurements(aid, active_only=True)
            av = tk.BooleanVar(value=any(k in selected for k in active))
            analysis_vars[aid] = av
            cb = ttk.Checkbutton(fr, text="Incluir análisis", variable=av)
            cb.pack(anchor="w")
            if not active:
                cb.state(["disabled"])
            status = {
                v120.STATUS_ACTIVE: "Disponible",
                v120.STATUS_VALIDATION: "En validación",
                v120.STATUS_REFERENCE_ONLY: "Referencia metodológica",
                v120.STATUS_OTHER_PROJECTION: "Requiere otra proyección",
            }.get(spec.get("status"), spec.get("status"))
            ttk.Label(
                fr, text=f"{status}. {spec.get('summary', '')}", style="Muted.TLabel",
                wraplength=820, justify=tk.LEFT,
            ).pack(anchor="w", padx=(22, 0))
            for key in active:
                mv = tk.BooleanVar(value=key in selected)
                measure_vars[key] = mv
                ttk.Checkbutton(
                    fr, text=v120.MEASUREMENTS[key]["label"], variable=mv,
                ).pack(anchor="w", padx=(35, 0))

        ref = ttk.LabelFrame(content, text="4 · Referencia Steiner", padding=10)
        ref.pack(fill=tk.X, pady=5)
        ttk.Radiobutton(
            ref, text="Sin clasificación automática", value="none", variable=steiner_var,
        ).pack(anchor="w")
        ttk.Radiobutton(
            ref, text="Steiner clásica publicada", value="classic", variable=steiner_var,
        ).pack(anchor="w")

        def save_protocol():
            name = name_var.get().strip()
            if not name:
                messagebox.showwarning("Protocolo", "Escriba el nombre.", parent=win)
                return
            try:
                target = int(target_var.get())
                if not 1 <= target <= v120.MAX_RESEARCH_CASES:
                    raise ValueError
                amin = int(amin_var.get()) if amin_var.get().strip() else None
                amax = int(amax_var.get()) if amax_var.get().strip() else None
                if amin is not None and not 0 <= amin <= 130:
                    raise ValueError
                if amax is not None and not 0 <= amax <= 130:
                    raise ValueError
                if amin is not None and amax is not None and amin > amax:
                    raise ValueError
            except ValueError:
                messagebox.showwarning(
                    "Protocolo", "Revise muestra (1–1000) y rango de edad (0–130).", parent=win,
                )
                return

            fields = []
            for raw in group_text.get("1.0", "end").splitlines():
                raw = raw.strip()
                if not raw:
                    continue
                if "=" not in raw:
                    messagebox.showwarning("Grupos", f"Formato inválido: {raw}", parent=win)
                    return
                fname, opts = raw.split("=", 1)
                options = [x.strip() for x in opts.split("|") if x.strip()]
                if not fname.strip() or not options:
                    messagebox.showwarning("Grupos", f"Variable incompleta: {raw}", parent=win)
                    return
                fields.append({"name": fname.strip(), "options": options})

            measures = [k for k, var in measure_vars.items() if var.get()]
            for aid, var in analysis_vars.items():
                if var.get() and not any(v120.MEASUREMENTS[k]["analysis"] == aid for k in measures):
                    measures.extend(
                        k for k in v120.analysis_measurements(aid, active_only=True)
                        if k not in measures
                    )
            if not measures:
                messagebox.showwarning(
                    "Análisis", "Seleccione al menos una medición disponible.", parent=win,
                )
                return
            aids = []
            for key in measures:
                aid = v120.MEASUREMENTS[key]["analysis"]
                if aid not in aids:
                    aids.append(aid)
            data = dict(
                name=name,
                target_n=target,
                allow_target_increase=allow_inc.get(),
                age_min=amin,
                age_max=amax,
                inclusion=inclusion.get("1.0", "end").strip(),
                exclusion=exclusion.get("1.0", "end").strip(),
                country=country_var.get().strip(),
                institution=institution_var.get().strip(),
                group_fields=fields,
                analyses=aids,
                measurements=measures,
                steiner_reference=steiner_var.get(),
            )
            sid = self._save_study(data, (existing or {}).get("study_id"))
            win.destroy()
            self._activate_study(sid)

        buttons = ttk.Frame(content)
        buttons.pack(fill=tk.X, pady=12)
        ttk.Button(
            buttons, text="Guardar protocolo y continuar", command=save_protocol,
            style="Purple.TButton",
        ).pack(side=tk.RIGHT)
        ttk.Button(
            buttons, text="Cancelar", command=win.destroy, style="Soft.TButton",
        ).pack(side=tk.RIGHT, padx=6)

    def _open_analysis_selector(self, title, on_accept):
        win = tk.Toplevel(self)
        win.title(title)
        win.transient(self)
        win.grab_set()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        w, h = min(850, int(sw * .92)), min(760, int(sh * .9))
        win.geometry(f"{w}x{h}+{max(0, (sw-w)//2)}+{max(0, (sh-h)//2)}")
        outer = ttk.Frame(win)
        outer.pack(fill=tk.BOTH, expand=True)
        canvas = tk.Canvas(outer, bg=ui.C["paper"], highlightthickness=0)
        sc = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        content = ttk.Frame(canvas, padding=16)
        cid = canvas.create_window((0, 0), window=content, anchor="nw")
        canvas.configure(yscrollcommand=sc.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sc.pack(side=tk.RIGHT, fill=tk.Y)
        content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(cid, width=e.width))
        ttk.Label(
            content, text=title, style="Section.TLabel", font=("Segoe UI Semibold", 16),
        ).pack(anchor="w", pady=(0, 8))

        vars_ = {}
        for aid, spec in v120.ANALYSES.items():
            fr = ttk.LabelFrame(content, text=spec["name"], padding=7)
            fr.pack(fill=tk.X, pady=3)
            active = v120.analysis_measurements(aid, active_only=True)
            ttk.Label(
                fr, text=spec.get("summary", ""), style="Muted.TLabel",
                wraplength=740, justify=tk.LEFT,
            ).pack(anchor="w")
            if not active:
                ttk.Label(
                    fr,
                    text="No calculable todavía: en validación o requiere otra proyección.",
                    style="Muted.TLabel",
                ).pack(anchor="w", padx=(20, 0))
            for key in active:
                var = tk.BooleanVar(value=key in self.selected_measure_keys)
                vars_[key] = var
                ttk.Checkbutton(
                    fr, text=v120.MEASUREMENTS[key]["label"], variable=var,
                ).pack(anchor="w", padx=(20, 0))

        current_ref = self.steiner_reference if self.steiner_reference in PUBLIC_STEINER_REFERENCES else "none"
        ref = tk.StringVar(value=current_ref)
        box = ttk.LabelFrame(content, text="Referencia Steiner", padding=8)
        box.pack(fill=tk.X, pady=5)
        ttk.Radiobutton(box, text="Sin clasificación", value="none", variable=ref).pack(anchor="w")
        ttk.Radiobutton(box, text="Steiner clásica", value="classic", variable=ref).pack(anchor="w")

        def accept():
            keys = [k for k, var in vars_.items() if var.get()]
            if not keys:
                messagebox.showwarning(
                    "Análisis", "Seleccione al menos una medición.", parent=win,
                )
                return
            win.destroy()
            on_accept(keys, ref.get())

        ttk.Button(
            content, text="Continuar", command=accept, style="Purple.TButton",
        ).pack(anchor="e", pady=10)

    def _storage_case_id(self, local_id):
        local = (local_id or "").strip()
        if self.workflow_type == "research" and self.current_study_id:
            return f"R:{self.current_study_id}:{local}"
        return f"I:{local}"

    def load_case_from_database(self, storage_id):
        result = super().load_case_from_database(storage_id)
        if self.steiner_reference not in PUBLIC_STEINER_REFERENCES:
            self.steiner_reference = "none"
        if self.workflow_type == "research":
            self.profile_var.set(v116.PROFILE_CUSTOM)
        else:
            self.profile_var.set(v116.PROFILE_GENERAL)
        return result

    def _diagnosis_for(self, key, value):
        original = self.steiner_reference
        if original not in PUBLIC_STEINER_REFERENCES:
            self.steiner_reference = "none"
        try:
            return super()._diagnosis_for(key, value)
        finally:
            self.steiner_reference = original

    def _show_pane(self, pane, position, weight):
        if pane is None or self._pane_present(pane):
            return
        try:
            panes = list(self.body_panes.panes())
            if position == "end":
                self.body_panes.add(pane, weight=weight)
            else:
                index = max(0, min(int(position), len(panes)))
                self.body_panes.insert(index, pane, weight=weight)
        except Exception:
            try:
                self.body_panes.add(pane, weight=weight)
            except Exception:
                pass

    def calculate_values(self):
        # Conserva todos los cálculos históricos validados y luego reemplaza las
        # nuevas variables v0.12 por las funciones puras probadas.
        r = super().calculate_values()
        p = self.points

        if all(k in p for k in ("S", "M", "G")):
            value = yen_angle(p["S"], p["M"], p["G"])
            if value is not None:
                r["YEN"] = value
            value = w_angle(p["S"], p["M"], p["G"])
            if value is not None:
                r["W"] = value

        if all(k in p for k in ("A", "B", "OcA", "OcP")):
            value = wits_ao_bo(p["A"], p["B"], p["OcP"], p["OcA"], self.mm_per_pixel)
            if value is not None:
                r["Wits AO–BO"] = value
            else:
                r.pop("Wits AO–BO", None)

        for key in list(r):
            if key.startswith("Jarabak"):
                r.pop(key, None)
        r.update(jarabak_values(p, self.mm_per_pixel))
        return r


if __name__ == "__main__":
    ui.enable_dpi_awareness()
    app = YomCephV120Final()
    app.mainloop()
