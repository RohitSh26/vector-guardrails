from __future__ import annotations

from collections.abc import Mapping

from vector_guardrails.models import ComparisonConfig


def compute_identity_metrics(
    baseline: Mapping[str, list[str]],
    candidate: Mapping[str, list[str]],
    config: ComparisonConfig,
):
    raise NotImplementedError