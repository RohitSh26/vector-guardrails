from vector_guardrails.metrics import overlap_at_k


def test_overlap_identical_lists():
    baseline = ["A", "B", "C", "D", "E"]
    candidate = ["A", "B", "C", "D", "E"]

    assert overlap_at_k(baseline, candidate, k=5) == 1.0


def test_overlap_no_overlap():
    baseline = ["A", "B", "C", "D", "E"]
    candidate = ["F", "G", "H", "I", "J"]

    assert overlap_at_k(baseline, candidate, k=5) == 0.0


def test_overlap_partial_overlap():
    baseline = ["A", "B", "C", "D", "E"]
    candidate = ["A", "C", "X", "Y", "Z"]

    # Shared: A, C → 2 / 5
    assert overlap_at_k(baseline, candidate, k=5) == 0.4


def test_overlap_candidate_shorter_than_k():
    baseline = ["A", "B", "C", "D", "E"]
    candidate = ["A", "B"]

    # Still divide by K (5), not by len(candidate)
    assert overlap_at_k(baseline, candidate, k=5) == 0.4