import yomceph_desktop_v11_database as v11db
import yomceph_desktop_v120 as v120
from yomceph_desktop_v120_release import YomCephV120Release


class DummyRelease:
    _measurement_unit = YomCephV120Release._measurement_unit
    _protocol_diagnosis = YomCephV120Release._protocol_diagnosis


def _dummy(reference):
    obj = object.__new__(DummyRelease)
    obj.steiner_reference = reference
    return obj


def test_public_catalog_has_no_institutional_steiner_affiliation():
    summary = v120.ANALYSES["steiner"]["summary"].casefold()
    for forbidden in ("uam", "universidad", "escuela", "clínica"):
        assert forbidden not in summary


def test_none_reference_never_injects_legacy_norms():
    obj = _dummy("none")
    state, diagnosis, diff, norm, sd, unit = obj._protocol_diagnosis("SNA", 86.0)
    assert state == ""
    assert diagnosis == ""
    assert diff is None
    assert norm is None
    assert sd is None
    assert unit == "°"


def test_classic_reference_is_explicit_and_separate():
    obj = _dummy("classic")
    state, diagnosis, diff, norm, sd, unit = obj._protocol_diagnosis("SNA", 86.0)
    assert state == "AUMENTADO"
    assert "clásica" in diagnosis
    assert diff == 4.0
    assert norm == 82.0
    assert sd == 2.0
    assert unit == "°"


def test_classic_reference_does_not_classify_measure_without_classic_entry():
    obj = _dummy("classic")
    state, diagnosis, diff, norm, sd, unit = obj._protocol_diagnosis("SND", 78.0)
    assert (state, diagnosis, diff, norm, sd) == ("", "", None, None, None)
    assert unit == "°"


def test_legacy_imported_reference_is_internal_and_reproducible():
    obj = _dummy("legacy_imported")
    value = 86.0
    state, diagnosis, diff, norm, sd, unit = obj._protocol_diagnosis("SNA", value)
    expected = v11db.STEINER_PROTOCOL["SNA"]
    assert state == "AUMENTADO"
    assert diagnosis == expected[5]
    assert norm == expected[0]
    assert sd == expected[1]
    assert diff == value - expected[0]
    assert unit == expected[2]
