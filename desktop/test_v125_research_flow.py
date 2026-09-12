import math

import yomceph_scientific_catalog as catalog
from yomceph_desktop_v125_research_flow import (
    AUTO_START,
    DEFAULT_EXCLUSION_REASONS,
    automatic_protocol_criteria,
    merge_automatic_criteria,
    research_case_decision,
)
from yomceph_v125_extended_analyses import extended_values


def test_protocol_criteria_are_generated_from_age_and_country():
    inclusion, exclusion = automatic_protocol_criteria(6, 15, "México")
    assert AUTO_START in inclusion
    assert "6 a 15" in inclusion
    assert "México" in inclusion
    assert "fuera del rango" in exclusion
    assert "Landmarks" in exclusion
    assert "calibración" in exclusion


def test_regeneration_preserves_researcher_custom_criteria_without_duplication():
    auto_a, _ = automatic_protocol_criteria(6, 15, "México")
    auto_b, _ = automatic_protocol_criteria(7, 14, "Colombia")
    first = merge_automatic_criteria("Excluir síndromes craneofaciales.", auto_a)
    second = merge_automatic_criteria(first, auto_b)
    assert second.count(AUTO_START) == 1
    assert "7 a 14" in second
    assert "Colombia" in second
    assert "Excluir síndromes craneofaciales." in second


def test_missing_required_landmarks_excludes_after_attempted_analysis():
    study = {"age_min": 6, "age_max": 15, "country": "México"}
    status, reasons, pending = research_case_decision(
        study, "10", "4", "México", ["S", "N", "A", "B"], ["S", "N", "A"]
    )
    assert status == "not_eligible"
    assert any("B" in reason and "Landmarks" in reason for reason in reasons)
    assert not pending


def test_country_and_age_are_automatic_exclusion_rules():
    study = {"age_min": 8, "age_max": 15, "country": "México"}
    status, reasons, _ = research_case_decision(
        study, "7", "11", "Argentina", ["S", "N"], ["S", "N"]
    )
    assert status == "not_eligible"
    assert any("mínimo" in reason for reason in reasons)
    assert any("Argentina" in reason and "México" in reason for reason in reasons)


def test_valid_case_is_eligible_only_after_required_geometry_is_complete():
    study = {"age_min": 0, "age_max": 15, "country": "México"}
    status, reasons, pending = research_case_decision(
        study, "15", "11", "méxico", ["S", "N", "A"], ["S", "N", "A"]
    )
    assert status == "eligible"
    assert reasons == []
    assert pending == []


def test_linear_study_requires_calibration_before_inclusion():
    study = {"age_min": 0, "age_max": 15, "country": ""}
    status, reasons, _ = research_case_decision(
        study,
        "12",
        "0",
        "",
        ["Co", "A"],
        ["Co", "A"],
        linear_calibration_required=True,
        calibrated=False,
    )
    assert status == "not_eligible"
    assert any("calibración" in reason for reason in reasons)


def test_manual_radiograph_reason_excludes_but_is_structured():
    study = {"age_min": 0, "age_max": 15, "country": ""}
    reason = DEFAULT_EXCLUSION_REASONS[0]
    status, reasons, _ = research_case_decision(
        study, "9", "0", "", ["S"], ["S"], manual_reasons=[reason]
    )
    assert status == "not_eligible"
    assert reasons == [reason]


def test_reproducible_analyses_are_unlocked_and_noncanonical_ones_stay_blocked():
    for analysis_id in ("tweed", "mcnamara", "airway", "rocabado", "downs"):
        assert catalog.ANALYSES[analysis_id]["status"] == catalog.STATUS_ACTIVE
        assert catalog.measurements_for_analysis(analysis_id, active_only=True)
    for analysis_id in ("ricketts", "cogs", "sassouni", "bimler", "g_triangle"):
        assert catalog.ANALYSES[analysis_id]["status"] != catalog.STATUS_ACTIVE
    assert catalog.ANALYSES["ritucci"]["status"] == catalog.STATUS_OTHER_PROJECTION
    assert catalog.ANALYSES["alexander"]["status"] == catalog.STATUS_REFERENCE_ONLY


def _reflect(points):
    return {key: (-x, y) for key, (x, y) in points.items()}


def test_tweed_and_mcnamara_geometry_is_independent_of_reference_norms_and_mirror():
    p = {
        "Po": (0.0, 0.0),
        "Or": (10.0, 0.0),
        "Go": (0.0, 5.0),
        "Me": (10.0, 10.0),
        "L1a": (2.0, 9.0),
        "L1i": (7.0, 19.0),
        "N": (5.0, 1.0),
        "A": (7.0, 5.0),
        "Pg": (8.0, 10.0),
        "Co": (0.0, 1.0),
        "Gn": (10.0, 11.0),
        "ANS": (6.0, 3.0),
        "Ba": (0.0, 2.0),
        "Ptm": (3.0, 4.0),
    }
    a = extended_values(p, 0.5)
    b = extended_values(_reflect(p), 0.5)
    for key in (
        "Tweed · FMA",
        "Tweed · FMIA",
        "Tweed · IMPA",
        "McNamara · A–N⊥",
        "McNamara · Pg–N⊥",
        "McNamara · Co–A",
        "McNamara · Co–Gn",
        "McNamara · ANS–Me",
        "McNamara · FH–GoMe",
        "McNamara · eje facial BaN–PtmGn",
    ):
        assert key in a and key in b
        assert math.isclose(a[key], b[key], rel_tol=1e-9, abs_tol=1e-9)
    assert math.isclose(a["McNamara · A–N⊥"], 1.0, abs_tol=1e-9)


def test_rocabado_and_airway_linear_geometry_needs_calibration():
    p = {
        "UPhA": (0.0, 0.0), "UPhP": (4.0, 0.0),
        "LPhA": (0.0, 2.0), "LPhP": (6.0, 2.0),
        "PNS": (0.0, 0.0), "C0": (10.0, 0.0), "C1sp": (2.0, 3.0),
        "C1ip": (2.0, 4.0), "C2sp": (2.0, 9.0),
        "C3ai": (0.0, 10.0), "RGn": (10.0, 10.0), "H": (5.0, 14.0),
    }
    assert "Vía aérea · faringe superior" not in extended_values(p, None)
    values = extended_values(p, 0.5)
    assert math.isclose(values["Vía aérea · faringe superior"], 2.0)
    assert math.isclose(values["Vía aérea · faringe inferior"], 3.0)
    assert math.isclose(values["Rocabado · C0–C1"], 1.5)
    assert math.isclose(values["Rocabado · C1–C2"], 2.5)
    assert math.isclose(values["Rocabado · H a C3–RGn"], 2.0)
