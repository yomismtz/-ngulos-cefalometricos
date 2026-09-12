import math

import fitz
import pytest
from PIL import Image

from yomceph_radiograph_loader import (
    RadiographLoadError,
    load_radiograph,
    materialize_as_png,
    radiograph_page_count,
)


def test_png_is_loaded_without_changing_geometry(tmp_path):
    path = tmp_path / "rx.png"
    Image.new("L", (123, 77), 128).save(path)
    imported = load_radiograph(path)
    assert imported.source_kind == "image"
    assert imported.page_count == 1
    assert imported.page_index == 0
    assert imported.image.mode == "RGB"
    assert imported.image.size == (123, 77)


def test_multipage_tiff_allows_explicit_page_selection(tmp_path):
    path = tmp_path / "multi.tiff"
    first = Image.new("L", (20, 10), 20)
    second = Image.new("L", (20, 10), 220)
    first.save(path, save_all=True, append_images=[second])

    assert radiograph_page_count(path) == 2
    imported = load_radiograph(path, page_index=1)
    assert imported.page_count == 2
    assert imported.page_number == 2
    assert imported.image.getpixel((5, 5)) == (220, 220, 220)


def test_pdf_page_is_rendered_at_high_resolution_without_distortion(tmp_path):
    path = tmp_path / "rx.pdf"
    document = fitz.open()
    page1 = document.new_page(width=72, height=36)  # 1 x 0.5 pulgadas
    page1.draw_rect(fitz.Rect(0, 0, 36, 36), fill=(0, 0, 0))
    page2 = document.new_page(width=72, height=36)
    page2.draw_rect(fitz.Rect(36, 0, 72, 36), fill=(0, 0, 0))
    document.save(path)
    document.close()

    assert radiograph_page_count(path) == 2
    imported = load_radiograph(path, page_index=1, pdf_dpi=300)
    assert imported.source_kind == "pdf"
    assert imported.page_number == 2
    assert imported.image.size == (300, 150)
    assert math.isclose(imported.effective_dpi, 300.0, abs_tol=0.1)


def test_pdf_or_selected_frame_can_be_materialized_as_lossless_png(tmp_path):
    path = tmp_path / "source.pdf"
    document = fitz.open()
    document.new_page(width=72, height=72)
    document.save(path)
    document.close()

    imported = load_radiograph(path, pdf_dpi=144)
    output = materialize_as_png(imported, tmp_path / "imports")
    assert output.suffix.lower() == ".png"
    assert output.exists()
    with Image.open(output) as restored:
        assert restored.size == imported.image.size


def test_invalid_page_and_unreadable_file_fail_cleanly(tmp_path):
    path = tmp_path / "single.png"
    Image.new("RGB", (10, 10), "white").save(path)
    with pytest.raises(RadiographLoadError):
        load_radiograph(path, page_index=1)

    bad = tmp_path / "broken.xyz"
    bad.write_text("not an image", encoding="utf-8")
    with pytest.raises(RadiographLoadError):
        radiograph_page_count(bad)
