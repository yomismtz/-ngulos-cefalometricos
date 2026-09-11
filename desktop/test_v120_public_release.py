import json
import sqlite3

import yomceph_desktop_v11_database as v11db
import yomceph_desktop_v120 as v120
import yomceph_desktop_v120_release_final as release_final_module
from yomceph_desktop_v120_release import YomCephV120Release, _unique_spss_names
from yomceph_desktop_v120_release_final import YomCephV120ReleaseFinal


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

    def set(self, value):
        self.value = value


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


class DummyCapacity:
    _ensure_research_capacity = YomCephV120ReleaseFinal._ensure_research_capacity
    _increase_sample_target = YomCephV120ReleaseFinal._increase_sample_target
    _record_protocol_history = YomCephV120ReleaseFinal._record_protocol_history

    def _evaluate_eligibility(self):
        return "eligible", "ok"

    def _storage_case_id(self, local):
        return f"R:{self.current_study_id}:{local}"

    def _get_study(self, study_id):
        with sqlite3.connect(self._db_path) as con:
            con.row_factory = sqlite3.Row
            row = con.execute("SELECT * FROM research_studies WHERE study_id=?", (study_id,)).fetchone()
        return dict(row)

    def _update_db_counter(self):
        return None


class DummyCompleteness:
    _validate_included_case_completeness = YomCephV120ReleaseFinal._validate_included_case_completeness

    def _evaluate_eligibility(self):
        return "eligible", "ok"


def _capacity_db(tmp_path, target=2, allow=0, included=2):
    db = tmp_path / "capacity.sqlite3"
    with sqlite3.connect(db) as con:
        con.execute(
            """CREATE TABLE research_studies(
                study_id TEXT PRIMARY KEY,target_n INTEGER,allow_target_increase INTEGER,
                protocol_version INTEGER,updated_at TEXT)"""
        )
        con.execute(
            """CREATE TABLE cases(
                case_id TEXT PRIMARY KEY,research_study_id TEXT,eligibility_status TEXT)"""
        )
        con.execute(
            "INSERT INTO research_studies VALUES('study',?,?,1,'')",
            (target, allow),
        )
        for i in range(1, included + 1):
            con.execute(
                "INSERT INTO cases VALUES(?,?,?)",
                (f"R:study:{i}", "study", "eligible"),
            )
        con.commit()
    obj = object.__new__(DummyCapacity)
    obj._db_path = db
    obj.workflow_type = "research"
    obj.current_study_id = "study"
    obj.current_study = {
        "study_id": "study",
        "target_n": target,
        "allow_target_increase": allow,
    }
    obj.study_target_var = _Var(str(target))
    return obj, db


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


def test_completed_sample_blocks_silent_extra_inclusion(tmp_path, monkeypatch):
    obj, _db = _capacity_db(tmp_path, target=2, allow=0, included=2)
    warnings = []
    monkeypatch.setattr(release_final_module.messagebox, "showwarning", lambda *a, **k: warnings.append(a))
    assert obj._ensure_research_capacity("3") is False
    assert warnings


def test_allowed_sample_increase_updates_version_and_history(tmp_path, monkeypatch):
    obj, db = _capacity_db(tmp_path, target=2, allow=1, included=2)
    monkeypatch.setattr(release_final_module.simpledialog, "askinteger", lambda *a, **k: 3)
    monkeypatch.setattr(release_final_module.messagebox, "showinfo", lambda *a, **k: None)
    assert obj._ensure_research_capacity("3") is True
    with sqlite3.connect(db) as con:
        target, version = con.execute(
            "SELECT target_n,protocol_version FROM research_studies WHERE study_id='study'"
        ).fetchone()
        action, hist_version, raw = con.execute(
            "SELECT action,protocol_version,details_json FROM research_protocol_history WHERE study_id='study' ORDER BY id DESC LIMIT 1"
        ).fetchone()
    details = json.loads(raw)
    assert target == 3
    assert version == 2
    assert action == "sample_increased"
    assert hist_version == 2
    assert details["old_target"] == 2
    assert details["new_target"] == 3
    assert details["source"] == "case_inclusion"
    assert obj.study_target_var.get() == "3"


def test_updating_existing_included_case_does_not_consume_new_slot(tmp_path, monkeypatch):
    obj, _db = _capacity_db(tmp_path, target=2, allow=0, included=2)
    monkeypatch.setattr(
        release_final_module.messagebox,
        "showwarning",
        lambda *a, **k: (_ for _ in ()).throw(AssertionError("no debe advertir")),
    )
    assert obj._ensure_research_capacity("2") is True


def test_1000_case_limit_never_opens_invalid_increase_dialog(tmp_path, monkeypatch):
    obj, _db = _capacity_db(tmp_path, target=1000, allow=1, included=1000)
    warnings = []
    monkeypatch.setattr(release_final_module.messagebox, "showwarning", lambda *a, **k: warnings.append(a))
    monkeypatch.setattr(
        release_final_module.simpledialog,
        "askinteger",
        lambda *a, **k: (_ for _ in ()).throw(AssertionError("no debe abrir diálogo")),
    )
    assert obj._ensure_research_capacity("1001") is False
    assert warnings


def test_included_case_requires_sex_and_configured_groups(monkeypatch):
    obj = object.__new__(DummyCompleteness)
    obj.workflow_type = "research"
    obj.current_study = {"group_fields": [{"name": "Grupo", "options": ["Caso", "Control"]}]}
    obj.sex_code_var = _Var("")
    obj.case_group_values = {"Grupo": ""}
    warnings = []
    monkeypatch.setattr(release_final_module.messagebox, "showwarning", lambda *a, **k: warnings.append(a))
    assert obj._validate_included_case_completeness() is False
    obj.sex_code_var.set("female")
    assert obj._validate_included_case_completeness() is False
    obj.case_group_values["Grupo"] = "Caso"
    assert obj._validate_included_case_completeness() is True
    assert warnings
