from __future__ import annotations

import argparse
import json
import sys

from vector_guardrails.compare import compare
from vector_guardrails.io import dump_json, ensure_snapshot_shape, load_json
from vector_guardrails.models import ComparisonConfig, ExitCode


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="vector-guardrails", description="Vector Guardrails CLI")
    sub = p.add_subparsers(dest="command", required=True)

    c = sub.add_parser("compare", help="Compare two retrieval snapshots")
    c.add_argument("--baseline", required=True, help="Path to baseline snapshot JSON")
    c.add_argument("--candidate", required=True, help="Path to candidate snapshot JSON")
    c.add_argument("--k", type=int, default=None, help="Top-K neighbors to compare")
    c.add_argument("--strict", action="store_true", help="Require exact anchor_id match")
    c.add_argument("--min-anchors", type=int, default=None, help="Minimum anchors required")
    c.add_argument("--output", default=None, help="Write full report JSON to this path")
    c.add_argument("--format", choices=["text", "json"], default="text", help="Stdout format")
    return p


def _print_text_report(report) -> None:
    """Print human-readable comparison report with explanations."""
    # Header with verdict
    print("=" * 70)
    print(report.verdict_summary)
    print("=" * 70)
    print()

    # Anchor alignment section
    print("ANCHOR ALIGNMENT:")
    print(f"  Compared: {report.alignment.compared_anchors} anchors present in both snapshots")

    if report.alignment.anchor_jaccard < 1.0:
        print(f"  Baseline only: {report.alignment.baseline_only_anchor_count} anchors")
        print(f"  Candidate only: {report.alignment.candidate_only_anchor_count} anchors")

    jaccard_pct = report.alignment.anchor_jaccard * 100
    print(f"  Jaccard similarity: {report.alignment.anchor_jaccard:.2f} ({jaccard_pct:.0f}% anchor set overlap)")

    if report.alignment.anchor_jaccard < report.config.thresholds.anchor_jaccard_warning:
        print(f"    ⚠ Low anchor overlap may indicate query set mismatch")
    print()

    # Retrieval quality metrics
    print("RETRIEVAL METRICS:")

    # Overlap
    overlap_pct = report.overall_mean_overlap * 100
    print(f"  Mean Overlap@{report.config.k}: {report.overall_mean_overlap:.2f} ({overlap_pct:.0f}%)")
    print(f"    → Average fraction of neighbors that remained in top-{report.config.k}")

    if report.overall_mean_overlap >= 0.90:
        print(f"    ✓ Excellent stability")
    elif report.overall_mean_overlap >= report.config.thresholds.overlap_warning:
        print(f"    ✓ Good stability")
    elif report.overall_mean_overlap >= report.config.thresholds.overlap_critical:
        print(f"    ⚠ Moderate changes detected")
    else:
        print(f"    ✗ Significant semantic drift detected")
    print()

    # Churn rate
    churn_pct = report.overall_churn_rate * 100
    print(f"  Churn Rate: {report.overall_churn_rate:.2f} ({churn_pct:.0f}% of anchors)")
    print(f"    → Fraction of anchors with overlap < {report.config.thresholds.overlap_warning:.2f}")

    if report.overall_churn_rate == 0.0:
        print(f"    ✓ No anchors showing degradation")
    elif report.overall_churn_rate < report.config.thresholds.churn_warning:
        print(f"    ✓ Low churn, isolated changes")
    elif report.overall_churn_rate < report.config.thresholds.churn_critical:
        print(f"    ⚠ Moderate churn, review recommended")
    else:
        print(f"    ✗ High churn, widespread changes")
    print()

    # Rank displacement (if available)
    if report.overall_mean_displacement > 0.0:
        print(f"  Mean Rank Displacement: {report.overall_mean_displacement:.1f} positions")
        print(f"    → Average position change for shared neighbors")

        if report.overall_mean_displacement < report.config.thresholds.displacement_warning:
            print(f"    ✓ Stable ranking")
        elif report.overall_mean_displacement < report.config.thresholds.displacement_critical:
            print(f"    ⚠ Moderate rank shifts")
        else:
            print(f"    ✗ Significant rank instability")
        print()

    # Risk breakdown
    crit = report.get_critical_anchors()
    warn = report.get_warning_anchors()

    print("RISK BREAKDOWN:")
    print(f"  CRITICAL: {len(crit)} anchors (overlap < {report.config.thresholds.overlap_critical:.2f})")
    print(f"  WARNING:  {len(warn)} anchors (overlap < {report.config.thresholds.overlap_warning:.2f})")
    print(f"  SAFE:     {report.alignment.compared_anchors - len(crit) - len(warn)} anchors")
    print()

    # Actionable guidance
    print("RECOMMENDATION:")
    if report.overall_risk_level.value == "SAFE":
        print("  ✓ Safe to proceed — no significant changes detected")
    elif report.overall_risk_level.value == "INFO":
        print("  ✓ Safe to proceed — minor changes within acceptable range")
    elif report.overall_risk_level.value == "WARNING":
        print("  ⚠ Review recommended — moderate changes detected")
        print("    Consider manual validation before deploying to production")
    elif report.overall_risk_level.value == "CRITICAL":
        print("  ✗ Deployment NOT recommended — significant semantic drift")
        print("    High-risk changes require investigation and validation")

    print("=" * 70)


def _print_json_summary(report) -> None:
    payload = {
        "overall_risk_level": report.overall_risk_level.value,
        "exit_code": report.to_exit_code(),
        "compared_anchors": report.alignment.compared_anchors,
        "mean_overlap": report.overall_mean_overlap,
        "mean_displacement": report.overall_mean_displacement,
        "churn_rate": report.overall_churn_rate,
        "anchor_jaccard": report.alignment.anchor_jaccard,
    }
    print(json.dumps(payload, ensure_ascii=False))


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command != "compare":
            raise ValueError(f"unknown command: {args.command}")

        baseline_obj = load_json(args.baseline)
        candidate_obj = load_json(args.candidate)

        baseline = ensure_snapshot_shape(baseline_obj)
        candidate = ensure_snapshot_shape(candidate_obj)

        cfg = ComparisonConfig()
        if args.k is not None:
            cfg = cfg.model_copy(update={"k": args.k})
        if args.min_anchors is not None:
            cfg = cfg.model_copy(update={"min_anchors": args.min_anchors})
        if args.strict:
            cfg = cfg.model_copy(update={"require_exact_match": True})

        report = compare(baseline=baseline, candidate=candidate, config=cfg)

        if args.output:
            dump_json(args.output, report.model_dump())

        if args.format == "text":
            _print_text_report(report)
        else:
            _print_json_summary(report)

        return report.to_exit_code()

    except Exception as e:
        # Keep errors user-friendly, but don’t swallow details
        print(f"ERROR: {e}", file=sys.stderr)
        return int(ExitCode.ERROR)


if __name__ == "__main__":
    raise SystemExit(main())
