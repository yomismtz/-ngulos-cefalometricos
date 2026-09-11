import hashlib
import io
import json

import pytest

import yomceph_updater as updater


class _Response(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
        return False


def test_version_comparison_is_numeric_not_lexicographic():
    assert updater.is_newer_version("v0.12.1", "0.12.0")
    assert updater.is_newer_version("0.13.0", "0.12.9")
    assert not updater.is_newer_version("0.12.0", "0.12.0")
    assert not updater.is_newer_version("0.11.9", "0.12.0")


def test_invalid_version_is_rejected():
    with pytest.raises(updater.UpdateError):
        updater.parse_version("latest")
    with pytest.raises(updater.UpdateError):
        updater.parse_version("0.12-beta")


def test_release_requires_verified_installer_assets(monkeypatch):
    payload = {
        "tag_name": "v0.12.1",
        "draft": False,
        "prerelease": False,
        "html_url": "https://github.com/example/release",
        "assets": [
            {"name": updater.INSTALLER_ASSET, "browser_download_url": "https://github.com/a.exe"},
        ],
    }
    monkeypatch.setattr(
        updater,
        "_request",
        lambda *a, **k: _Response(json.dumps(payload).encode("utf-8")),
    )
    with pytest.raises(updater.UpdateError):
        updater.fetch_latest_update("0.12.0")


def test_release_same_version_returns_none(monkeypatch):
    payload = {
        "tag_name": "v0.12.0",
        "draft": False,
        "prerelease": False,
        "assets": [],
    }
    monkeypatch.setattr(
        updater,
        "_request",
        lambda *a, **k: _Response(json.dumps(payload).encode("utf-8")),
    )
    assert updater.fetch_latest_update("0.12.0") is None


def test_downloaded_installer_must_match_sha256(tmp_path, monkeypatch):
    installer = b"fake-yomceph-installer-for-test"
    digest = hashlib.sha256(installer).hexdigest()
    update = updater.UpdateInfo(
        version="0.12.1",
        tag="v0.12.1",
        installer_url="https://github.com/installer",
        checksum_url="https://github.com/checksum",
        release_url="https://github.com/release",
    )

    def fake_request(url, *_args, **_kwargs):
        if url == update.checksum_url:
            return _Response(f"{digest}  {updater.INSTALLER_ASSET}\n".encode("ascii"))
        if url == update.installer_url:
            return _Response(installer)
        raise AssertionError(url)

    monkeypatch.setattr(updater, "_request", fake_request)
    path = updater.download_verified_installer(update, tmp_path, "0.12.0")
    assert path.read_bytes() == installer
    assert updater.sha256_file(path) == digest


def test_bad_checksum_deletes_partial_download(tmp_path, monkeypatch):
    update = updater.UpdateInfo(
        version="0.12.1",
        tag="v0.12.1",
        installer_url="https://github.com/installer",
        checksum_url="https://github.com/checksum",
        release_url="https://github.com/release",
    )

    def fake_request(url, *_args, **_kwargs):
        if url == update.checksum_url:
            return _Response(("0" * 64 + "  file.exe\n").encode("ascii"))
        return _Response(b"not-the-expected-installer")

    monkeypatch.setattr(updater, "_request", fake_request)
    with pytest.raises(updater.UpdateError):
        updater.download_verified_installer(update, tmp_path, "0.12.0")
    assert not list(tmp_path.glob("*.part"))
