from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
DESKTOP = ROOT / "desktop"
WEBSITE = ROOT / "website"


def _read(path):
    return path.read_text(encoding="utf-8")


def test_version_is_consistent_across_distribution_and_installer():
    version = _read(DESKTOP / "VERSION").strip()
    assert re.fullmatch(r"\d+\.\d+\.\d+", version)

    personalization = _read(DESKTOP / "yomceph_desktop_v124_personalization.py")
    final_entry = _read(DESKTOP / "yomceph_desktop_v124_final.py")
    installer = _read(DESKTOP / "YomCeph_v0120.iss")
    assert f'APP_VERSION = "{version}"' in personalization
    assert "YomCephV124Final" in final_entry
    assert f'#define MyAppVersion "{version}"' in installer
    assert "OutputBaseFilename=YomCeph_Desktop_Setup_v{#MyAppVersion}" in installer


def test_installer_identity_stays_stable_for_in_place_updates():
    installer = _read(DESKTOP / "YomCeph_v0120.iss")
    assert "AppId={{B8F36D2E-02D1-4BAA-A580-4B188B1488E8}" in installer
    assert "DefaultDirName={localappdata}\\Programs\\YomCeph Desktop" in installer


def test_public_distribution_uses_verified_release_updater():
    final_entry = _read(DESKTOP / "yomceph_desktop_v124_final.py")
    updater = _read(DESKTOP / "yomceph_updater.py")
    assert "fetch_latest_update" in final_entry
    assert "download_verified_installer" in final_entry
    assert "sha256_file" in updater
    assert "YomCeph_Desktop_Setup.exe.sha256" in updater
    assert "https://api.github.com/repos/yomismtz/Cefalometria-/releases/latest" in updater


def test_website_download_is_version_independent_latest_release_link():
    js = _read(WEBSITE / "app.js")
    privacy = _read(WEBSITE / "privacy.html")
    stable = "https://github.com/yomismtz/Cefalometria-/releases/latest/download/YomCeph_Desktop_Setup.exe"
    assert stable in js
    assert stable in privacy


def test_privacy_discloses_update_network_behavior_and_integrity_check():
    root_policy = _read(ROOT / "PRIVACY_POLICY.md")
    web_policy = _read(WEBSITE / "privacy.html")
    for text in (root_policy, web_policy):
        folded = text.casefold()
        assert "github releases" in folded
        assert "sha-256" in folded
        assert "radiograf" in folded
        assert "no" in folded


def test_public_i18n_does_not_expose_institutional_profile():
    i18n = _read(DESKTOP / "yomceph_i18n.json").casefold()
    for forbidden in (
        "investigación uam",
        "uam research",
        "cuatro clínicas",
        "four clinics",
        "tepepan",
        "tláhuac",
        "nezahualcóyotl",
    ):
        assert forbidden not in i18n
