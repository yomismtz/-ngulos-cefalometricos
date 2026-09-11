from yomceph_scientific_catalog import (
    ANALYSES, EXTRA_POINTS, MEASUREMENTS, STATUS_ACTIVE,
    analysis_measurements, required_landmarks,
)


def test_active_measurements_reference_known_analysis():
    for key, spec in MEASUREMENTS.items():
        assert spec['analysis'] in ANALYSES, (key, spec['analysis'])
        assert spec['required'], key
        assert spec['unit'] in {'°', 'mm', '%'}, key


def test_no_duplicate_new_landmarks():
    ids = [p[0] for p in EXTRA_POINTS]
    assert len(ids) == len(set(ids))


def test_active_analysis_has_executable_measurement_when_expected():
    for analysis_id, spec in ANALYSES.items():
        if spec['status'] == STATUS_ACTIVE:
            assert analysis_measurements(analysis_id, active_only=True), analysis_id


def test_landmark_union_is_stable_and_deduplicated():
    selected = ['SNA', 'SNB', 'ANB', 'YEN', 'W']
    points = required_landmarks(selected)
    assert points == ['S', 'N', 'A', 'B', 'M', 'G']


def test_research_core_measures_present():
    for key in (
        'SNA', 'SNB', 'ANB', 'SN–GoGn', 'SN–OPT', 'SN–CVT',
        'MGP–OP', 'Powell Nasofrontal', 'Wits AO–BO', 'YEN', 'W',
        'Jarabak ratio',
    ):
        assert key in MEASUREMENTS
