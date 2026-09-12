from pathlib import Path

import yomceph_desktop_v120_distribution as distribution
import yomceph_desktop_v123_hardening as hardening


ROOT = Path(__file__).resolve().parents[1]
DESKTOP = ROOT / "desktop"


def _read(path):
    return path.read_text(encoding="utf-8")


def test_v123_historical_version_is_stable():
    """v0.12.3 sigue siendo una capa histórica reproducible aunque exista v0.12.4."""
    assert hardening.APP_VERSION == "0.12.3"
    assert distribution.APP_VERSION in {"0.12.2", "0.12.3"}


def test_v123_hardening_source_remains_available():
    source = _read(DESKTOP / "yomceph_desktop_v123_hardening.py")
    assert 'APP_VERSION = "0.12.3"' in source
    assert "class YomCephV123Hardening" in source
    assert "_confirm_discard_unsaved" in source
    assert "_preflight_saved_case" in source


def test_hardening_bypasses_unsafe_releasefinal_toolbar_scan():
    source = _read(DESKTOP / "yomceph_desktop_v123_hardening.py")
    assert "release.YomCephV120Release._install_database_bar(self)" in source
    assert "isinstance(child, ttk.Menubutton)" in source


def test_hardening_has_explicit_data_loss_guards():
    source = _read(DESKTOP / "yomceph_desktop_v123_hardening.py")
    for marker in (
        "_confirm_discard_unsaved",
        "_preflight_saved_case",
        "Identificador protegido",
        "Caso activo protegido",
        "WM_DELETE_WINDOW",
        "_capture_saved_snapshot",
        "_poll_update_queue",
    ):
        assert marker in source
