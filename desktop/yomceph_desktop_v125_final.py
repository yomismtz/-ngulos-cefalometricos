"""Entrada pública final de YomCeph Desktop v0.12.5."""

import yomceph_desktop_hidpi as ui
from yomceph_desktop_v125_research_flow import APP_VERSION, YomCephV125ResearchFlow


class YomCephV125Final(YomCephV125ResearchFlow):
    pass


if __name__ == "__main__":
    ui.enable_dpi_awareness()
    app = YomCephV125Final()
    app.mainloop()
