import math

from yomceph_v120_geometry import (
    acute_line_angle,
    directed_line_angle,
    jarabak_values,
    legacy_active_angles,
    obtuse_line_angle,
    w_angle,
    wits_ao_bo,
    yen_angle,
)


def _polar(degrees, radius=1.0):
    rad = math.radians(degrees)
    return radius * math.cos(rad), radius * math.sin(rad)


def test_line_angle_helpers_define_sector_without_norm():
    origin = (0.0, 0.0)
    x_axis = (1.0, 0.0)
    ray120 = _polar(120.0)
    assert math.isclose(directed_line_angle(origin, x_axis, origin, ray120), 120.0, abs_tol=1e-9)
    assert math.isclose(acute_line_angle(origin, x_axis, origin, ray120), 60.0, abs_tol=1e-9)
    assert math.isclose(obtuse_line_angle(origin, x_axis, origin, ray120), 120.0, abs_tol=1e-9)


def test_angle_helpers_are_invariant_when_entire_radiograph_is_mirrored():
    a, b = (1.0, 2.0), (8.0, 3.0)
    c, d = (3.0, 9.0), (5.0, 1.0)
    mirror = lambda p: (-p[0], p[1])
    assert math.isclose(
        directed_line_angle(a, b, c, d),
        directed_line_angle(mirror(a), mirror(b), mirror(c), mirror(d)),
        abs_tol=1e-9,
    )
    assert math.isclose(
        acute_line_angle(a, b, c, d),
        acute_line_angle(mirror(a), mirror(b), mirror(c), mirror(d)),
        abs_tol=1e-9,
    )
    assert math.isclose(
        obtuse_line_angle(a, b, c, d),
        obtuse_line_angle(mirror(a), mirror(b), mirror(c), mirror(d)),
        abs_tol=1e-9,
    )


def test_legacy_active_angles_use_explicit_sectors_not_reference_targets():
    # S-N horizontal. Po-Or and Go-Gn are 7°/32° and therefore use acute sectors.
    # U1 axis is 76° to SN, so U1-SN must report its conventional obtuse sector 104°.
    points = {
        "S": (0.0, 0.0),
        "N": (10.0, 0.0),
        "Po": (0.0, 2.0),
        "Or": _polar(7.0, 10.0),
        "Go": (0.0, 4.0),
        "Gn": _polar(32.0, 10.0),
        "A": (0.0, 0.0),
        "B": (0.0, 10.0),
        "U1a": (0.0, 0.0),
        "U1i": _polar(76.0, 10.0),
    }
    values = legacy_active_angles(points)
    assert math.isclose(values["SN–PoOr"], 7.0, abs_tol=1e-9)
    assert math.isclose(values["SN–GoGn"], 32.0, abs_tol=1e-9)
    assert math.isclose(values["IS–SN"], 104.0, abs_tol=1e-9)


def test_solow_and_rocabado_angles_use_obtuse_sector_explicitly():
    # Si la tangente forma 80° con SN, SN-OPT/CVT debe ser el sector inferior de 100°.
    # Si OP forma 79° con McGregor, el CCA de Rocabado debe ser 101°.
    points = {
        "S": (0.0, 0.0),
        "N": (10.0, 0.0),
        "cv2tg": (0.0, 0.0),
        "cv2ip": _polar(80.0, 10.0),
        "cv4ip": _polar(81.0, 10.0),
        "PNS": (0.0, 0.0),
        "C0": (10.0, 0.0),
        "Ops": (0.0, 0.0),
        "Opi": _polar(79.0, 10.0),
    }
    values = legacy_active_angles(points)
    assert math.isclose(values["SN–OPT"], 100.0, abs_tol=1e-9)
    assert math.isclose(values["SN–CVT"], 99.0, abs_tol=1e-9)
    assert math.isclose(values["MGP–OP"], 101.0, abs_tol=1e-9)


def test_powell_angles_no_longer_choose_sector_by_closeness_to_norm():
    # Nasomental: 54° entre las líneas => sector anatómico obtuso 126°.
    # Mentocervical: el orden anatómico G'→Pg' y Me'→C define directamente 85°.
    points = {
        "Nsoft": (0.0, 0.0),
        "Dn": (10.0, 0.0),
        "Prn": (0.0, 0.0),
        "Pgsoft": _polar(54.0, 10.0),
        "Gsoft": (0.0, 0.0),
        "Mesoft": (0.0, 0.0),
        "Csoft": _polar(85.0, 10.0),
    }
    # Para mentocervical Gsoft->Pgsoft también debe ser horizontal en este sintético.
    points["Pgsoft"] = (10.0, 0.0)
    values = legacy_active_angles(points)
    # Reasignamos un conjunto separado para nasomental porque Pgsoft participa en ambas.
    nasomental_points = dict(points)
    nasomental_points["Pgsoft"] = _polar(54.0, 10.0)
    assert math.isclose(legacy_active_angles(nasomental_points)["Powell Nasomental"], 126.0, abs_tol=1e-9)
    assert math.isclose(values["Powell Mentocervical"], 85.0, abs_tol=1e-9)


def test_yen_angle_uses_s_m_g_with_vertex_m():
    assert math.isclose(yen_angle((0, 0), (0, 1), (1, 1)), 90.0, abs_tol=1e-9)


def test_w_angle_is_between_mg_and_perpendicular_to_sg():
    # S-G horizontal; la perpendicular desde M es vertical. M-G queda a 45°.
    assert math.isclose(w_angle((0, 0), (5, 5), (10, 0)), 45.0, abs_tol=1e-9)


def test_wits_sign_is_anatomical_posterior_to_anterior():
    # Plano oclusal posterior→anterior de x=0 a x=10. AO=8, BO=5 => +3 mm.
    value = wits_ao_bo((8, 3), (5, -2), (0, 0), (10, 0), 1.0)
    assert math.isclose(value, 3.0, abs_tol=1e-9)
    # La misma anatomía orientada hacia la izquierda debe conservar el signo.
    mirrored = wits_ao_bo((-8, 3), (-5, -2), (0, 0), (-10, 0), 1.0)
    assert math.isclose(mirrored, 3.0, abs_tol=1e-9)


def test_wits_requires_calibration_for_mm():
    assert wits_ao_bo((8, 3), (5, -2), (0, 0), (10, 0), None) is None


def test_jarabak_angles_lengths_and_ratio_are_reproducible():
    points = {
        "S": (0, 0),
        "N": (1, 0),
        "Ar": (0, 1),
        "Go": (1, 1),
        "Me": (2, 1),
    }
    values = jarabak_values(points, mm_per_pixel=0.5)
    assert math.isclose(values["Jarabak · Saddle"], 90.0, abs_tol=1e-9)
    assert math.isclose(values["Jarabak · Articular"], 90.0, abs_tol=1e-9)
    assert math.isclose(values["Jarabak · Gonial"], 180.0, abs_tol=1e-9)
    assert math.isclose(values["Jarabak · Sum"], 360.0, abs_tol=1e-9)
    assert math.isclose(values["Jarabak · S-N"], 0.5, abs_tol=1e-9)
    assert math.isclose(values["Jarabak · S-Go"], math.sqrt(2) * 0.5, abs_tol=1e-9)
    assert math.isclose(values["Jarabak ratio"], 100.0, abs_tol=1e-9)


def test_jarabak_ratio_does_not_need_linear_calibration():
    points = {"S": (0, 0), "Go": (0, 6), "N": (10, 0), "Me": (10, 10)}
    values = jarabak_values(points)
    assert math.isclose(values["Jarabak ratio"], 60.0, abs_tol=1e-9)
    assert "Jarabak · S-Go" not in values
