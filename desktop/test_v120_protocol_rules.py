"""Reglas metodológicas puras de v0.12.

Estas pruebas documentan decisiones que no deben depender de la interfaz.
"""


def eligibility(age_years, age_min, age_max, criteria_confirmation):
    if age_years is None:
        return "pending"
    if age_min is not None and age_years < age_min:
        return "not_eligible"
    if age_max is not None and age_years > age_max:
        return "not_eligible"
    if criteria_confirmation == "no":
        return "not_eligible"
    if criteria_confirmation == "yes":
        return "eligible"
    return "pending"


def can_change_protocol(case_count_included, field, allow_target_increase=False, old_target=None, new_target=None):
    if case_count_included == 0:
        return True
    if field == "target_n" and allow_target_increase and old_target is not None and new_target is not None:
        return new_target > old_target
    return False


def test_age_below_study_range_is_not_eligible():
    assert eligibility(7, 8, 15, "yes") == "not_eligible"


def test_age_above_study_range_is_not_eligible():
    assert eligibility(16, 0, 15, "yes") == "not_eligible"


def test_case_inside_age_range_still_needs_criteria_confirmation():
    assert eligibility(10, 0, 15, "pending") == "pending"
    assert eligibility(10, 0, 15, "yes") == "eligible"
    assert eligibility(10, 0, 15, "no") == "not_eligible"


def test_locked_protocol_cannot_silently_change_analysis_or_age_range():
    assert not can_change_protocol(1, "measurements")
    assert not can_change_protocol(1, "age_min")
    assert not can_change_protocol(103, "groups")


def test_sample_can_only_increase_when_protocol_explicitly_allows_it():
    assert can_change_protocol(1, "target_n", True, 103, 150)
    assert not can_change_protocol(1, "target_n", True, 103, 80)
    assert not can_change_protocol(1, "target_n", False, 103, 150)


def test_protocol_is_editable_before_first_included_case():
    assert can_change_protocol(0, "age_min")
    assert can_change_protocol(0, "measurements")
