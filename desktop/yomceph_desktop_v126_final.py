"""Entrada pública de YomCeph Desktop v0.12.6.

Completa los bloques cefalométricos que pueden reproducirse honestamente en una
lateral de cráneo y corrige el uso histórico Ptm/Pt en el eje facial.
"""

import tkinter as tk

import yomceph_desktop_hidpi as ui
import yomceph_desktop_v124_final as v124final
import yomceph_desktop_v124_personalization as v124personal
import yomceph_desktop_v125_research_flow as v125
from yomceph_v126_remaining_analyses import install_remaining_analyses, remaining_values

APP_VERSION = "0.12.6"
v125.APP_VERSION = APP_VERSION
v124final.APP_VERSION = APP_VERSION
v124personal.APP_VERSION = APP_VERSION


class YomCephV126Final(v125.YomCephV125ResearchFlow):
    """v0.12.5 research-first workflow plus verified v0.12.6 analyses."""

    def __init__(self):
        # Install before the inherited UI propagates EXTRA_POINTS into the master
        # landmark catalog, then re-assert statuses after v0.12.5 installs its
        # compatibility extensions.
        install_remaining_analyses()
        super().__init__()
        install_remaining_analyses()
        self.title(f"YomCeph Desktop · v{APP_VERSION}")

    def _apply_language(self):
        try:
            self.title(f"YomCeph Desktop · v{APP_VERSION}")
        except tk.TclError:
            pass

    def calculate_values(self):
        values = super().calculate_values()
        # v0.12.5 temporarily reused Ptm for a Ricketts Pt construction. Pt and
        # Ptm are not the same landmark. Never expose that legacy calculation in
        # v0.12.6; the correct facial axis is now under Ricketts using Pt.
        values.pop("McNamara · eje facial BaN–PtmGn", None)
        values.update(remaining_values(self.points, getattr(self, "mm_per_pixel", None)))
        return values


if __name__ == "__main__":
    ui.enable_dpi_awareness()
    app = YomCephV126Final()
    app.mainloop()
