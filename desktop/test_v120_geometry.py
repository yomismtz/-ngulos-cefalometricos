import math

from yomceph_v120_geometry import jarabak_values, w_angle, wits_ao_bo, yen_angle


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
