import yomceph_desktop_v11_database as v11db
import yomceph_desktop_v120 as v120
from yomceph_desktop_v120_release import YomCephV120Release, _unique_spss_names


class DummyRelease:
    _measurement_unit = YomCephV120Release._measurement_unit
    _protocol_diagnosis = YomCephV120Release._protocol_diagnosis


def _dummy(reference):
    obj = object.__new__(DummyRelease)
    obj.steiner_reference = reference
    return obj


class _Var:
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value


class DummyEligibility:
    _evaluate_eligibility = YomCephV120Release._evaluate_eligibility


def _eligibility(years, months, minimum=0, maximum=15, manual="yes"):
    obj = object.__new__(DummyEligibility)
    obj.workflow_type = "research"
    obj.current_study = {"age_min": minimum, "age_max": maximum}
    obj.age_years_var = _Var(str(years))
    obj.age_months_var = _Var(str(months))
    obj.manual_eligibility = manual
    return obj._evaluate_eligibility()


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


def test_integer_age_max_includes_entire_last_year_of_age():
    assert _eligibility(15, 11, maximum=15)[0] == "eligible"
    assert _eligibility(16, 0, maximum=15)[0] == "not_eligible"


def test_spss_names_are_unique_ascii_and_bounded():
    names = _unique_spss_names(["Grupo Á", "Grupo-A", "Grupo A", "123 medida", "Grupo Á"])
    assert len(names) == len(set(name.casefold() for name in names))
    assert all(len(name) <= 64 for name in names)
    assert all(name[0].isalpha() or name[0] == "_" for name in names)
    assert names[3].startswith("v_")


def test_yen_w_landmarks_have_reproducible_circle_definitions():
    info = {point[0]: point[2].casefold() for point in v120.EXTRA_POINTS}
    assert "mayor círculo" in info["M"]
    assert "mayor círculo" in info["G"]
