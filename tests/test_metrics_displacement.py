from vector_guardrails.metrics import rank_displacement


def test_displacement_identical_lists():
    baseline = ["A", "B", "C", "D"]
    candidate = ["A", "B", "C", "D"]

    assert rank_displacement(baseline, candidate, k=4) == 0.0


def test_displacement_simple_swap():
    baseline = ["A", "B", "C"]
    candidate = ["B", "A", "C"]

    # A: |0 - 1| = 1
    # B: |1 - 0| = 1
    # C: |2 - 2| = 0
    # Mean = (1 + 1 + 0) / 3
    assert rank_displacement(baseline, candidate, k=3) == 2 / 3


def test_displacement_partial_overlap():
    baseline = ["A", "B", "C", "D"]
    candidate = ["B", "A", "X", "Y"]

    # Shared: A, B
    # A: |0 - 1| = 1
    # B: |1 - 0| = 1
    assert rank_displacement(baseline, candidate, k=4) == 1.0


def test_displacement_no_overlap():
    baseline = ["A", "B", "C"]
    candidate = ["X", "Y", "Z"]

    assert rank_displacement(baseline, candidate, k=3) is None