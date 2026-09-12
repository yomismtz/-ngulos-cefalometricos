"""Carga robusta de radiografías para YomCeph Desktop.

El módulo mantiene la geometría de la imagen: no recorta, estira ni corrige la
radiografía. Los PDF se rasterizan de forma uniforme y las páginas seleccionadas
de documentos multipágina pueden materializarse como PNG sin pérdida para que el
resto del flujo histórico de YomCeph siga trabajando con una imagen convencional.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

import fitz  # PyMuPDF
from PIL import Image, ImageOps, UnidentifiedImageError


IMAGE_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".jfif", ".tif", ".tiff", ".bmp",
    ".webp", ".gif", ".pgm", ".ppm", ".pnm", ".pbm",
}
PDF_EXTENSIONS = {".pdf"}
SUPPORTED_EXTENSIONS = IMAGE_EXTENSIONS | PDF_EXTENSIONS

FILE_DIALOG_TYPES = [
    (
        "Radiografías e imágenes",
        "*.png *.jpg *.jpeg *.jfif *.tif *.tiff *.bmp *.webp *.gif *.pgm *.ppm *.pnm *.pbm *.pdf",
    ),
    ("PDF", "*.pdf"),
    ("JPEG", "*.jpg *.jpeg *.jfif"),
    ("PNG", "*.png"),
    ("TIFF", "*.tif *.tiff"),
    ("BMP", "*.bmp"),
    ("WebP", "*.webp"),
    ("Todos los archivos", "*.*"),
]


class RadiographLoadError(RuntimeError):
    """Error legible para el usuario al importar una radiografía."""


@dataclass(frozen=True)
class RadiographImport:
    image: Image.Image
    source_path: str
    source_kind: str
    page_index: int
    page_count: int
    effective_dpi: float | None = None

    @property
    def page_number(self) -> int:
        return self.page_index + 1


def _validate_page_index(page_index: int, page_count: int) -> None:
    if page_count < 1:
        raise RadiographLoadError("El archivo no contiene páginas o imágenes utilizables.")
    if page_index < 0 or page_index >= page_count:
        raise RadiographLoadError(
            f"La página solicitada ({page_index + 1}) está fuera del intervalo 1–{page_count}."
        )


def radiograph_page_count(path: str | Path) -> int:
    source = Path(path)
    suffix = source.suffix.lower()
    if not source.exists():
        raise RadiographLoadError("No se encontró el archivo seleccionado.")

    if suffix in PDF_EXTENSIONS:
        try:
            with fitz.open(str(source)) as document:
                if document.needs_pass:
                    raise RadiographLoadError(
                        "El PDF está protegido con contraseña. Quite la protección antes de importarlo."
                    )
                return int(document.page_count)
        except RadiographLoadError:
            raise
        except Exception as exc:
            raise RadiographLoadError(f"No se pudo leer el PDF: {exc}") from exc

    try:
        with Image.open(source) as image:
            return int(getattr(image, "n_frames", 1) or 1)
    except (UnidentifiedImageError, OSError) as exc:
        if suffix and suffix not in SUPPORTED_EXTENSIONS:
            raise RadiographLoadError(
                "Formato no reconocido. Use PNG, JPEG/JFIF, TIFF, BMP, WebP, GIF, PGM/PPM/PNM/PBM o PDF."
            ) from exc
        raise RadiographLoadError(f"No se pudo leer la imagen: {exc}") from exc


def _load_raster(path: Path, page_index: int) -> RadiographImport:
    try:
        with Image.open(path) as source:
            count = int(getattr(source, "n_frames", 1) or 1)
            _validate_page_index(page_index, count)
            if count > 1:
                source.seek(page_index)
            frame = ImageOps.exif_transpose(source).convert("RGB").copy()
        return RadiographImport(
            image=frame,
            source_path=str(path),
            source_kind="image",
            page_index=page_index,
            page_count=count,
            effective_dpi=None,
        )
    except RadiographLoadError:
        raise
    except (UnidentifiedImageError, OSError, EOFError) as exc:
        raise RadiographLoadError(f"No se pudo abrir la imagen: {exc}") from exc


def _render_pdf(
    path: Path,
    page_index: int,
    dpi: float = 300.0,
    max_dimension: int = 7000,
) -> RadiographImport:
    if dpi <= 0:
        raise RadiographLoadError("La resolución de importación del PDF debe ser mayor que cero.")
    try:
        with fitz.open(str(path)) as document:
            if document.needs_pass:
                raise RadiographLoadError(
                    "El PDF está protegido con contraseña. Quite la protección antes de importarlo."
                )
            count = int(document.page_count)
            _validate_page_index(page_index, count)
            page = document.load_page(page_index)
            rect = page.rect
            if rect.width <= 0 or rect.height <= 0:
                raise RadiographLoadError("La página PDF seleccionada no tiene dimensiones válidas.")

            scale = float(dpi) / 72.0
            predicted_max = max(float(rect.width), float(rect.height)) * scale
            if max_dimension and predicted_max > max_dimension:
                scale *= float(max_dimension) / predicted_max
            effective_dpi = scale * 72.0

            pixmap = page.get_pixmap(
                matrix=fitz.Matrix(scale, scale),
                colorspace=fitz.csRGB,
                alpha=False,
                annots=True,
            )
            image = Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples).copy()
        return RadiographImport(
            image=image,
            source_path=str(path),
            source_kind="pdf",
            page_index=page_index,
            page_count=count,
            effective_dpi=effective_dpi,
        )
    except RadiographLoadError:
        raise
    except Exception as exc:
        raise RadiographLoadError(f"No se pudo renderizar el PDF: {exc}") from exc


def load_radiograph(
    path: str | Path,
    page_index: int = 0,
    pdf_dpi: float = 300.0,
    max_pdf_dimension: int = 7000,
) -> RadiographImport:
    source = Path(path)
    if not source.exists():
        raise RadiographLoadError("No se encontró el archivo seleccionado.")
    if source.suffix.lower() in PDF_EXTENSIONS:
        return _render_pdf(source, page_index, pdf_dpi, max_pdf_dimension)
    return _load_raster(source, page_index)


def materialize_as_png(
    imported: RadiographImport,
    destination_dir: str | Path,
) -> Path:
    """Guarda una copia PNG reproducible del frame/página ya cargado.

    Se usa para PDF y para páginas distintas de la primera en archivos
    multipágina. PNG evita introducir compresión con pérdida antes del trazado.
    """
    destination = Path(destination_dir)
    destination.mkdir(parents=True, exist_ok=True)
    source = Path(imported.source_path)
    try:
        stat = source.stat()
        identity = f"{source.resolve()}|{stat.st_size}|{stat.st_mtime_ns}|{imported.page_index}"
    except OSError:
        identity = f"{source}|{imported.page_index}"
    digest = hashlib.sha256(identity.encode("utf-8", errors="replace")).hexdigest()[:12]
    stem = re.sub(r"[^A-Za-z0-9._-]+", "_", source.stem).strip("._-") or "radiografia"
    output = destination / f"{stem}_p{imported.page_number}_{digest}.png"
    imported.image.save(output, format="PNG", optimize=False)
    return output
