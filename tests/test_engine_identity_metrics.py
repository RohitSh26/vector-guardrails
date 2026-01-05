from vector_guardrails.engine import compute_identity_metrics
from vector_guardrails.models import ComparisonConfig


def test_engine_computes_metrics_on_anchor_intersection():
    baseline = {
        "A1": ["X", "Y", "Z"],
        "A2": ["M", "N", "O"],
    }

    candidate = {
        "A1": ["Y", "X", "Z"],  # same anchor, reordered
        "A3": ["P", "Q", "R"],  # not in baseline
    }

    config = ComparisonConfig(k=3)

    alignment, anchor_metrics, overall = compute_identity_metrics(
        baseline=baseline,
        candidate=candidate,
        config=config,
    )

    # Only A1 should be compared
    assert alignment.compared_anchors == 1
    assert len(anchor_metrics) == 1
    assert anchor_metrics[0].anchor_id == "A1"

    # Overlap = 3/3
    assert anchor_metrics[0].overlap == 1.0

    # Displacement exists and is > 0
    assert anchor_metrics[0].rank_displacement is not None