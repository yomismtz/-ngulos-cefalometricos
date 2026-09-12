"""Actualizador de YomCeph Desktop.

La aplicación consulta únicamente metadatos públicos de GitHub Releases. No se
incluyen radiografías, datos de pacientes, landmarks ni resultados en la
solicitud. El instalador se descarga por HTTPS y se verifica con SHA-256 antes
de ejecutarse.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

RELEASE_API_URL = "https://api.github.com/repos/yomismtz/-ngulos-cefalometricos/releases/latest"
INSTALLER_ASSET = "YomCeph_Desktop_Setup.exe"
CHECKSUM_ASSET = "YomCeph_Desktop_Setup.exe.sha256"
USER_AGENT_PREFIX = "YomCeph-Desktop"
MAX_METADATA_BYTES = 2_000_000
MAX_CHECKSUM_BYTES = 16_384


class UpdateError(RuntimeError):
    pass


@dataclass(frozen=True)
class UpdateInfo:
    version: str
    tag: str
    installer_url: str
    checksum_url: str
    release_url: str
    notes: str = ""


def parse_version(value: str) -> tuple[int, ...]:
    """Convierte v1.2.3 / 1.2.3 en una tupla comparable.

    Sólo se aceptan versiones numéricas estables. Esto evita que una etiqueta
    arbitraria pueda activar una actualización por accidente.
    """
    text = str(value or "").strip()
    if text.lower().startswith("v"):
        text = text[1:]
    if not re.fullmatch(r"\d+(?:\.\d+){1,3}", text):
        raise UpdateError(f"Versión no válida: {value!r}")
    parts = tuple(int(part) for part in text.split("."))
    return parts + (0,) * (4 - len(parts))


def is_newer_version(candidate: str, current: str) -> bool:
    return parse_version(candidate) > parse_version(current)


def _read_limited(response, limit: int) -> bytes:
    data = response.read(limit + 1)
    if len(data) > limit:
        raise UpdateError("La respuesta de actualización excede el tamaño esperado.")
    return data


def _request(url: str, current_version: str, timeout: float = 8.0):
    if not str(url).lower().startswith("https://"):
        raise UpdateError("YomCeph sólo acepta actualizaciones mediante HTTPS.")
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": f"{USER_AGENT_PREFIX}/{current_version}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        return urllib.request.urlopen(req, timeout=timeout)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            raise UpdateError("Todavía no hay una versión pública disponible.") from exc
        raise UpdateError(f"GitHub respondió con HTTP {exc.code}.") from exc
    except urllib.error.URLError as exc:
        raise UpdateError("No se pudo conectar al servicio de actualizaciones.") from exc


def fetch_latest_update(current_version: str, timeout: float = 8.0) -> UpdateInfo | None:
    """Devuelve la actualización más reciente o None si ya está al día."""
    with _request(RELEASE_API_URL, current_version, timeout) as response:
        try:
            payload = json.loads(_read_limited(response, MAX_METADATA_BYTES).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise UpdateError("La respuesta de actualización no es válida.") from exc

    if payload.get("draft") or payload.get("prerelease"):
        return None
    tag = str(payload.get("tag_name") or "").strip()
    if not tag:
        raise UpdateError("La publicación no contiene un número de versión.")
    if not is_newer_version(tag, current_version):
        return None

    assets = {
        str(asset.get("name") or ""): str(asset.get("browser_download_url") or "")
        for asset in payload.get("assets", [])
        if isinstance(asset, dict)
    }
    installer_url = assets.get(INSTALLER_ASSET, "")
    checksum_url = assets.get(CHECKSUM_ASSET, "")
    if not installer_url or not checksum_url:
        raise UpdateError("La versión publicada no contiene el instalador verificado de YomCeph.")
    if not installer_url.startswith("https://") or not checksum_url.startswith("https://"):
        raise UpdateError("Los archivos de actualización no usan HTTPS.")

    version = tag[1:] if tag.lower().startswith("v") else tag
    return UpdateInfo(
        version=version,
        tag=tag,
        installer_url=installer_url,
        checksum_url=checksum_url,
        release_url=str(payload.get("html_url") or ""),
        notes=str(payload.get("body") or "")[:4000],
    )


def parse_sha256(text: str) -> str:
    match = re.search(r"\b([0-9a-fA-F]{64})\b", str(text or ""))
    if not match:
        raise UpdateError("El archivo de verificación SHA-256 no es válido.")
    return match.group(1).lower()


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download_verified_installer(
    update: UpdateInfo,
    destination_dir: str | Path,
    current_version: str,
    timeout: float = 20.0,
) -> Path:
    """Descarga instalador + checksum y rechaza cualquier discrepancia."""
    destination = Path(destination_dir)
    destination.mkdir(parents=True, exist_ok=True)
    target = destination / f"YomCeph_Desktop_Setup_v{update.version}.exe"
    partial = target.with_suffix(target.suffix + ".part")

    with _request(update.checksum_url, current_version, timeout) as response:
        try:
            expected = parse_sha256(_read_limited(response, MAX_CHECKSUM_BYTES).decode("ascii", errors="strict"))
        except UnicodeDecodeError as exc:
            raise UpdateError("El checksum publicado no es texto ASCII válido.") from exc

    try:
        with _request(update.installer_url, current_version, timeout) as response, open(partial, "wb") as output:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                output.write(chunk)
        actual = sha256_file(partial)
        if actual != expected:
            raise UpdateError(
                "La verificación SHA-256 del instalador falló. El archivo descargado fue descartado."
            )
        partial.replace(target)
        return target
    except Exception:
        try:
            partial.unlink(missing_ok=True)
        except Exception:
            pass
        raise


def launch_installer(installer_path: str | Path) -> subprocess.Popen:
    path = Path(installer_path)
    if not path.is_file():
        raise UpdateError("No se encontró el instalador descargado.")
    # SILENT conserva una ventana de progreso; no se oculta completamente al
    # usuario. Inno cierra/reabre la aplicación y nunca reinicia Windows.
    return subprocess.Popen(
        [
            str(path),
            "/SILENT",
            "/SUPPRESSMSGBOXES",
            "/NORESTART",
            "/CLOSEAPPLICATIONS",
            "/RESTARTAPPLICATIONS",
        ],
        close_fds=True,
    )
