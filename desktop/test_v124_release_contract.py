from pathlib import Path

from yomceph_desktop_v124_final import APP_VERSION


ROOT = Path(__file__).resolve().parents[1]
DESKTOP = ROOT / "desktop"


def _read(path):
    return path.read_text(encoding="utf-8")


def test_v124_module_contract_is_preserved_as_regression_baseline():
    # v0.12.4 permanece como capa histórica de personalización. La versión
    # distribuida puede avanzar sin reescribir retrospectivamente este módulo.
    assert APP_VERSION == "0.12.4"
    final_entry = _read(DESKTOP / "yomceph_desktop_v124_final.py")
    personalization = _read(DESKTOP / "yomceph_desktop_v124_personalization.py")
    assert "YomCephV124Final" in final_entry
    assert 'APP_VERSION = "0.12.4"' in personalization


def test_v124_regression_tests_remain_in_workflows():
    build = _read(ROOT / ".github" / "workflows" / "build-windows-exe.yml")
    publish = _read(ROOT / ".github" / "workflows" / "publish-release.yml")
    for workflow in (build, publish):
        assert "desktop/smoke_v124_windows.py" in workflow
        assert "desktop/test_v124_personalization.py" in workflow
        assert "desktop/test_v124_release_contract.py" in workflow


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
