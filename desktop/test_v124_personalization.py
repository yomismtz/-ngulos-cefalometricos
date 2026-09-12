import json
from pathlib import Path

import yomceph_desktop_v120_distribution as distribution
import yomceph_desktop_v123_hardening as hardening
from yomceph_desktop_v124_personalization import (
    DEFAULT_PREFERENCES,
    PALETTES,
    REQUIRED_COLOR_KEYS,
    contrast_ratio,
    normalize_preferences,
)

# El módulo v0.12.4 ajusta las constantes de versión heredadas porque será el
# siguiente entrypoint del EXE. Mientras v0.12.3 siga siendo la versión publicada,
# sus pruebas contractuales deben continuar comprobando 0.12.3 sin contaminación
# por el import de esta candidata.
hardening.APP_VERSION = "0.12.3"
distribution.APP_VERSION = "0.12.3"


def test_five_palettes_are_complete():
    assert len(PALETTES) == 5
    expected = set(REQUIRED_COLOR_KEYS)
    for name, palette in PALETTES.items():
        assert name.strip()
        assert set(palette) == expected
        assert all(value.startswith("#") and len(value) == 7 for value in palette.values())


def test_primary_text_contrast_is_accessible():
    for name, palette in PALETTES.items():
        assert contrast_ratio(palette["text"], palette["panel"]) >= 4.5, name
        assert contrast_ratio(palette["text"], palette["paper"]) >= 4.5, name
        assert contrast_ratio(palette["muted"], palette["panel"]) >= 3.0, name


def test_normalize_preferences_limits_untrusted_values():
    prefs = normalize_preferences(
        {"font_family": "  Arial  ", "font_size": 99, "palette": "desconocida"}
    )
    assert prefs["font_family"] == "Arial"
    assert prefs["font_size"] == 18
    assert prefs["palette"] == DEFAULT_PREFERENCES["palette"]

    prefs = normalize_preferences({"font_family": "", "font_size": "x", "palette": None})
    assert prefs == DEFAULT_PREFERENCES


def test_normalize_preferences_accepts_every_palette():
    for palette in PALETTES:
        prefs = normalize_preferences(
            {"font_family": "Verdana", "font_size": 12, "palette": palette}
        )
        assert prefs == {"font_family": "Verdana", "font_size": 12, "palette": palette}


def test_preferences_are_json_serializable(tmp_path: Path):
    prefs = normalize_preferences(
        {"font_family": "Segoe UI", "font_size": 11, "palette": "Azul clínico"}
    )
    path = tmp_path / "ui_preferences.json"
    path.write_text(json.dumps(prefs, ensure_ascii=False), encoding="utf-8")
    loaded = normalize_preferences(json.loads(path.read_text(encoding="utf-8")))
    assert loaded == prefs
