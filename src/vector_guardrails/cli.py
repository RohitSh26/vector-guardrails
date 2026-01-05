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
    # Minimal but readable; we’ll refine formatting later if needed
    print(report.verdict_summary)
    print()
    print("SUMMARY:")
    print(f"  Compared anchors: {report.alignment.compared_anchors}")
    print(f"  Mean overlap@{report.config.k}: {report.overall_mean_overlap:.2f}")
    print(f"  Churn rate: {report.overall_churn_rate:.2f}")
    print(f"  Anchor jaccard: {report.alignment.anchor_jaccard:.2f}")
    print()
    crit = report.get_critical_anchors()
    warn = report.get_warning_anchors()
    print("DETAILS:")
    print(f"  CRITICAL anchors: {len(crit)}")
    print(f"  WARNING anchors: {len(warn)}")


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
