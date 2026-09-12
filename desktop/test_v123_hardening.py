from pathlib import Path
import re

import yomceph_desktop_v120_distribution as distribution
import yomceph_desktop_v123_hardening as hardening


ROOT = Path(__file__).resolve().parents[1]
DESKTOP = ROOT / "desktop"


def _read(path):
    return path.read_text(encoding="utf-8")


def test_v123_version_contract_is_consistent():
    version = _read(DESKTOP / "VERSION").strip()
    assert version == "0.12.3"
    assert re.fullmatch(r"\d+\.\d+\.\d+", version)
    assert hardening.APP_VERSION == version
    assert distribution.APP_VERSION == version
    installer = _read(DESKTOP / "YomCeph_v0120.iss")
    assert f'#define MyAppVersion "{version}"' in installer


def test_ci_packages_hardened_entrypoint_and_smoke():
    for workflow_name in ("build-windows-exe.yml", "publish-release.yml"):
        workflow = _read(ROOT / ".github" / "workflows" / workflow_name)
        assert "desktop/yomceph_desktop_v123_hardening.py" in workflow
        assert "desktop/smoke_v123_windows.py" in workflow
    publish = _read(ROOT / ".github" / "workflows" / "publish-release.yml")
    assert "Get-Content desktop/yomceph_desktop_v123_hardening.py -Raw" in publish


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
