import math

import yomceph_scientific_catalog as catalog
from yomceph_v120_geometry import acute_line_angle, distance
from yomceph_v126_remaining_analyses import (
    bimler_values,
    burstone_hp_direction,
    cogs_values,
    g_triangle_frame,
    g_triangle_values,
    install_remaining_analyses,
    remaining_values,
    xi_point,
)


def _reflect(points):
    return {key: (-x, y) for key, (x, y) in points.items()}


def test_new_reproducible_blocks_are_active_but_nonlateral_methods_are_not():
    install_remaining_analyses()
    for analysis_id in ("ricketts", "cogs", "sassouni", "bimler", "g_triangle"):
        assert catalog.ANALYSES[analysis_id]["status"] == catalog.STATUS_ACTIVE
        assert catalog.analysis_measurements(analysis_id, active_only=True)
    assert catalog.ANALYSES["alexander"]["status"] == catalog.STATUS_REFERENCE_ONLY
    assert catalog.ANALYSES["ritucci"]["status"] == catalog.STATUS_OTHER_PROJECTION


def test_incorrect_ptm_facial_axis_is_not_selectable_in_v126():
    install_remaining_analyses()
    old = catalog.MEASUREMENTS["McNamara · eje facial BaN–PtmGn"]
    assert old["status"] == catalog.STATUS_VALIDATION
    assert "Pt ≠ Ptm" in old["label"]
    assert "McNamara · eje facial BaN–PtmGn" not in catalog.analysis_measurements("mcnamara", active_only=True)


def test_ricketts_xi_is_constructed_from_ramus_rectangle_and_mirror_invariant():
    points = {
        "Po": (0.0, 0.0), "Or": (10.0, 0.0),
        "N": (0.0, -5.0), "Me": (10.0, 10.0),
        "R1": (2.0, 4.0), "R2": (8.0, 4.0),
        "R3": (5.0, 2.0), "R4": (5.0, 10.0),
    }
    xi = xi_point(points)
    assert xi is not None
    assert math.isclose(xi[0], 5.0, abs_tol=1e-9)
    assert math.isclose(xi[1], 6.0, abs_tol=1e-9)
    mirrored = xi_point(_reflect(points))
    assert mirrored is not None
    assert math.isclose(mirrored[0], -5.0, abs_tol=1e-9)
    assert math.isclose(mirrored[1], 6.0, abs_tol=1e-9)


def test_burstone_hp_is_exactly_seven_degrees_from_sn_and_mirror_invariant():
    points = {
        "S": (0.0, 0.0), "N": (10.0, 0.0),
        "Po": (0.0, 0.0), "Or": (10.0, math.tan(math.radians(7.0)) * 10.0),
    }
    hp = burstone_hp_direction(points)
    assert hp is not None
    angle = acute_line_angle((0.0, 0.0), (1.0, 0.0), (0.0, 0.0), hp)
    assert math.isclose(angle, 7.0, abs_tol=1e-9)
    mirrored = burstone_hp_direction(_reflect(points))
    assert mirrored is not None
    assert math.isclose(abs(mirrored[0]), abs(hp[0]), abs_tol=1e-9)
    assert math.isclose(mirrored[1], hp[1], abs_tol=1e-9)


def test_cogs_linear_values_require_calibration_but_angles_do_not():
    points = {
        "S": (0.0, 0.0), "N": (10.0, 0.0),
        "Po": (0.0, 0.0), "Or": (10.0, 1.0),
        "A": (10.5, 5.0), "Pg": (11.0, 15.0),
        "Go": (1.0, 12.0), "Me": (10.0, 15.0),
        "Ar": (0.0, 4.0), "Ptm": (3.0, 4.0), "Gn": (10.5, 15.0),
    }
    raw = cogs_values(points, None)
    calibrated = cogs_values(points, 0.5)
    assert "COGS · MP–HP" in raw
    assert "COGS · N–A–Pg" in raw
    assert "COGS · Ptm–N // HP" not in raw
    assert "COGS · Ptm–N // HP" in calibrated
    assert calibrated["COGS · Ptm–N // HP"] > 0


def test_bimler_primary_sign_conventions_survive_horizontal_reflection():
    points = {
        "Po": (0.0, 0.0), "Or": (10.0, 0.0),
        "N": (0.0, 0.0), "A": (1.0, 10.0), "B": (0.0, 20.0),
        "PNS": (0.0, 5.0), "ANS": (10.0, 6.0),
        "GoA": (0.0, 10.0), "Me": (10.0, 15.0),
        "Cls": (0.0, 0.0), "Cli": (5.0, 10.0),
        "S": (-1.0, 0.0),
    }
    first = bimler_values(points)
    second = bimler_values(_reflect(points))
    assert first["Bimler · F1 perfil superior"] > 0
    assert first["Bimler · F2 perfil inferior"] > 0
    assert first["Bimler · F4 inclinación maxilar"] > 0
    for key in first:
        assert key in second
        assert math.isclose(first[key], second[key], rel_tol=1e-9, abs_tol=1e-9), key


def test_g_triangle_frame_is_equilateral_and_signed_angles_are_mirror_invariant():
    base = {
        "Po": (0.0, 0.0), "Or": (10.0, 0.0),
        "Ba": (0.0, -5.0), "Bo": (0.0, 0.0), "Gtri": (10.0, 5.0),
    }
    frame = g_triangle_frame(base)
    assert frame is not None
    _i, x, k = frame
    side = distance(base["Bo"], x)
    assert side > 0
    assert math.isclose(distance(x, k), side, rel_tol=1e-9, abs_tol=1e-9)
    assert math.isclose(distance(k, base["Bo"]), side, rel_tol=1e-9, abs_tol=1e-9)

    points = dict(base)
    points["A"] = (k[0] + 0.5, k[1])
    points["B"] = (k[0] - 0.5, k[1])
    values = g_triangle_values(points)
    mirrored = g_triangle_values(_reflect(points))
    assert values["G-triangle · AXK"] > 0
    assert values["G-triangle · BXK"] < 0
    for key in ("G-triangle · AXK", "G-triangle · BXK"):
        assert math.isclose(values[key], mirrored[key], rel_tol=1e-9, abs_tol=1e-9)


def test_combined_remaining_geometry_is_reference_independent_and_finite():
    points = {
        "Po": (0.0, 0.0), "Or": (10.0, 0.0),
        "N": (5.0, -2.0), "S": (0.0, -1.0), "A": (6.0, 4.0), "B": (5.0, 8.0),
        "Pg": (7.0, 12.0), "Go": (0.0, 10.0), "Me": (8.0, 14.0), "Gn": (8.0, 13.0),
        "Ba": (-2.0, -3.0), "Pt": (1.0, 3.0), "Pm": (7.0, 11.0), "DC": (-1.0, 3.0),
        "R1": (1.0, 5.0), "R2": (4.0, 5.0), "R3": (2.5, 3.0), "R4": (2.5, 9.0),
        "ANS": (6.0, 3.0), "PNS": (1.0, 3.0), "Ar": (-1.0, 5.0), "Ptm": (1.0, 2.0),
        "U1a": (5.0, 2.0), "U1i": (7.0, 7.0), "L1a": (5.0, 11.0), "L1i": (7.0, 8.0),
        "U6": (2.0, 7.0), "L6": (2.0, 8.0),
        "GoA": (1.0, 10.0), "Cls": (-1.0, -2.0), "Cli": (1.0, 2.0),
        "SasCl": (-1.0, -2.0), "SasRo": (5.0, -1.0), "SasSi": (0.0, 0.0), "SasMbP": (0.0, 10.0),
        "Bo": (-2.0, -1.0), "Gtri": (8.0, -5.0),
    }
    values = remaining_values(points, 0.5)
    assert values
    assert all(math.isfinite(v) for v in values.values())
    assert "Ricketts · eje facial" in values
    assert "COGS · MP–HP" in values
    assert "Sassouni · basal–palatino" in values
    assert "Bimler · F1 perfil superior" in values
    assert "Downs · convexidad N–A–Pg" in values
