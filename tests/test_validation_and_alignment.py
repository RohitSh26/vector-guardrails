import pytest

from vector_guardrails import align_anchors, anchor_mismatch_warning, validate_and_truncate_snapshot


def test_validate_snapshot_rejects_bad_k():
    with pytest.raises(ValueError):
        validate_and_truncate_snapshot({}, k=0)


def test_validate_snapshot_rejects_non_mapping():
    with pytest.raises(ValueError):
        validate_and_truncate_snapshot(["not", "a", "mapping"], k=10)  # type: ignore[arg-type]


def test_validate_snapshot_rejects_bad_anchor_id():
    with pytest.raises(ValueError):
        validate_and_truncate_snapshot({123: ["a"]}, k=10)  # type: ignore[dict-item]


def test_validate_snapshot_rejects_non_list_neighbors():
    with pytest.raises(ValueError):
        validate_and_truncate_snapshot({"a1": ("x", "y")}, k=10)  # type: ignore[dict-item]


def test_validate_snapshot_truncates_to_k():
    snap = {"a1": ["n1", "n2", "n3", "n4"]}
    out = validate_and_truncate_snapshot(snap, k=2)
    assert out["a1"] == ["n1", "n2"]


def test_validate_snapshot_rejects_duplicates_in_topk():
    snap = {"a1": ["n1", "n1", "n2"]}
    with pytest.raises(ValueError):
        validate_and_truncate_snapshot(snap, k=3)


def test_align_anchors_counts_and_jaccard():
    baseline = {"a1": ["x"], "a2": ["y"], "a3": ["z"]}
    candidate = {"a2": ["y"], "a3": ["z"], "a4": ["w"]}

    alignment = align_anchors(baseline, candidate, sample_limit=10)
    assert alignment.total_baseline_anchors == 3
    assert alignment.total_candidate_anchors == 3
    assert alignment.compared_anchors == 2

    # |A∩B|=2, |A∪B|=4 => 0.5
    assert alignment.anchor_jaccard == 0.5

    assert alignment.baseline_only_anchor_count == 1
    assert alignment.candidate_only_anchor_count == 1
    assert alignment.baseline_only_anchor_sample == ["a1"]
    assert alignment.candidate_only_anchor_sample == ["a4"]


def test_anchor_mismatch_warning_triggers_below_threshold():
    baseline = {"a1": ["x"], "a2": ["y"], "a3": ["z"]}
    candidate = {"a2": ["y"], "a3": ["z"], "a4": ["w"]}

    alignment = align_anchors(baseline, candidate)
    msg = anchor_mismatch_warning(alignment, jaccard_warning_threshold=0.90)
    assert msg is not None
    assert "Significant anchor_id mismatch detected" in msg


def test_anchor_mismatch_warning_not_triggered_when_matching():
    baseline = {"a1": ["x"], "a2": ["y"]}
    candidate = {"a1": ["x"], "a2": ["y"]}

    alignment = align_anchors(baseline, candidate)
    msg = anchor_mismatch_warning(alignment, jaccard_warning_threshold=0.90)
    assert msg is None
