from pathlib import Path
import re

from yomceph_desktop_v124_final import APP_VERSION


ROOT = Path(__file__).resolve().parents[1]
DESKTOP = ROOT / "desktop"


def _read(path):
    return path.read_text(encoding="utf-8")


def test_v124_release_contract_is_consistent():
    version = _read(DESKTOP / "VERSION").strip()
    assert version == "0.12.4"
    assert re.fullmatch(r"\d+\.\d+\.\d+", version)
    assert APP_VERSION == version
    installer = _read(DESKTOP / "YomCeph_v0120.iss")
    assert f'#define MyAppVersion "{version}"' in installer


def test_workflows_package_v124_final_entrypoint():
    build = _read(ROOT / ".github" / "workflows" / "build-windows-exe.yml")
    publish = _read(ROOT / ".github" / "workflows" / "publish-release.yml")
    for workflow in (build, publish):
        assert "desktop/yomceph_desktop_v124_final.py" in workflow
        assert "desktop/smoke_v124_windows.py" in workflow
        assert "desktop/test_v124_personalization.py" in workflow
        assert "desktop/test_v124_release_contract.py" in workflow
    assert "desktop/yomceph_desktop_v124_final.py -Raw" in publish


def test_v124_personalization_contract_has_five_named_palettes():
    source = _read(DESKTOP / "yomceph_desktop_v124_personalization.py")
    for name in (
        "YomCeph violeta",
        "Noche radiográfica",
        "Azul clínico",
        "Menta suave",
        "Arena cálida",
    ):
        assert name in source
    assert "⚙ Configuración" in source
    assert "font_family" in source
    assert "font_size" in source
    assert "ui_preferences.json" in source
