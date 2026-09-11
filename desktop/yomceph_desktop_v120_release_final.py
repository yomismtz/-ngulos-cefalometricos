import yomceph_desktop_hidpi as ui
from yomceph_desktop_v120_release import YomCephV120Release
from yomceph_v120_geometry import legacy_active_angles

APP_VERSION = "0.12.0"


class YomCephV120ReleaseFinal(YomCephV120Release):
    """Entrada final de la candidata pública v0.12.

    La cadena histórica todavía contiene ``closest_supplement`` para abrir
    proyectos creados con versiones anteriores. Esta clase reemplaza, antes de
    mostrar o persistir resultados de v0.12, todas las mediciones activas que lo
    usaban por construcciones geométricas explícitas e independientes de normas.
    """

    def calculate_values(self):
        values = super().calculate_values()
        values.update(legacy_active_angles(self.points))
        return values


if __name__ == "__main__":
    ui.enable_dpi_awareness()
    app = YomCephV120ReleaseFinal()
    app.mainloop()
