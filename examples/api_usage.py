#!/usr/bin/env python3
"""
Demonstrates programmatic API usage of vector-guardrails.

This example shows how to:
- Import and use the compare() function
- Configure comparison parameters
- Access report fields
- Make programmatic decisions based on risk level
"""

from vector_guardrails import ComparisonConfig, RiskLevel, compare

# Example snapshots
baseline = {
    "query_1": ["doc_a", "doc_b", "doc_c"],
    "query_2": ["doc_x", "doc_y", "doc_z"],
}

candidate = {
    "query_1": ["doc_a", "doc_b", "doc_c"],
    "query_2": ["doc_x", "doc_y", "doc_z"],
}

# Run comparison with custom configuration
config = ComparisonConfig(k=3)
report = compare(baseline=baseline, candidate=candidate, config=config)

# Access report fields
print("=" * 60)
print("COMPARISON REPORT")
print("=" * 60)
print(f"\nOverall Risk Level: {report.overall_risk_level.value}")
print(f"Exit Code: {report.to_exit_code()}")
print(f"\nCompared Anchors: {report.alignment.compared_anchors}")
print(f"Mean Overlap@{config.k}: {report.overall_mean_overlap:.2f}")
print(f"Churn Rate: {report.overall_churn_rate:.2f}")
print(f"Anchor Jaccard: {report.alignment.anchor_jaccard:.2f}")

print(f"\nVerdict: {report.verdict_summary}")

# Programmatic decision logic
print("\n" + "=" * 60)
print("DECISION LOGIC")
print("=" * 60)

if report.overall_risk_level == RiskLevel.SAFE:
    print("✓ SAFE: Proceed with deployment")
    exit_code = 0

elif report.overall_risk_level == RiskLevel.INFO:
    print("ℹ INFO: Minor changes detected, safe to proceed")
    exit_code = 0

elif report.overall_risk_level == RiskLevel.WARNING:
    print("⚠ WARNING: Moderate changes detected")
    print(f"  - {len(report.get_warning_anchors())} anchors flagged as WARNING")
    print("  - Manual review recommended before deployment")
    exit_code = 1

elif report.overall_risk_level == RiskLevel.CRITICAL:
    print("✗ CRITICAL: High-risk changes detected")
    print(f"  - {len(report.get_critical_anchors())} anchors flagged as CRITICAL")
    print("  - Deployment NOT recommended")
    exit_code = 2

else:
    print("✗ ERROR: Unexpected risk level")
    exit_code = 3

# Access individual anchor metrics
if report.anchor_metrics:
    print("\n" + "=" * 60)
    print("PER-ANCHOR METRICS")
    print("=" * 60)
    for metric in report.anchor_metrics:
        print(f"\nAnchor: {metric.anchor_id}")
        print(f"  Risk Level: {metric.risk_level.value}")
        print(f"  Overlap: {metric.overlap:.2f}")
        print(f"  Shared: {metric.shared_count}, "
              f"Baseline-only: {metric.baseline_only_count}, "
              f"Candidate-only: {metric.candidate_only_count}")
        if metric.reasons:
            print(f"  Reasons: {', '.join(metric.reasons)}")

print("\n" + "=" * 60)
exit(exit_code)
