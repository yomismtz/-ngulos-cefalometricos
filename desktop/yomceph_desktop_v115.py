import yomceph_desktop_hidpi as ui
import yomceph_desktop_v114_research_metadata as v114
import yomceph_desktop_v115_quality_audit as quality

APP_VERSION = "0.11.5"


class YomCephV115(quality.QualityAuditYomCeph):
    """Entrada final v0.11.5 con estado de guardado sensible a cambios reales."""

    def canvas_left_up(self, event):
        was_dragging = bool(self._dragging_point)
        # Saltar el override provisional de v0.11.5 quality_audit, que marcaba
        # el caso como modificado ante cualquier clic izquierdo sin efecto.
        result = v114.ResearchMetadataYomCeph.canvas_left_up(self, event)
        if was_dragging:
            self._mark_dirty(schedule_qc=True)
        return result


if __name__ == "__main__":
    ui.enable_dpi_awareness()
    app = YomCephV115()
    app.mainloop()
