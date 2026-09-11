import tkinter as tk

import yomceph_desktop_hidpi as ui
import yomceph_desktop_v120 as v120
from yomceph_v120_geometry import jarabak_values, w_angle, wits_ao_bo, yen_angle

APP_VERSION = "0.12.0"


class YomCephV120Final(v120.YomCephV120):
    """Entrada final de v0.12.0.

    Sustituye las nuevas fórmulas inline por funciones geométricas puras cubiertas
    por pruebas unitarias y hace más robusta la reinserción de paneles responsivos.
    """

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
