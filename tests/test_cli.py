from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def _run_cli(args: list[str]) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable, "-m", "vector_guardrails"] + args
    return subprocess.run(cmd, capture_output=True, text=True)


def test_cli_compare_text_success(tmp_path: Path):
    baseline = {"A1": ["X", "Y", "Z"], "A2": ["M", "N", "O"]}
    candidate = {"A1": ["Y", "X", "Z"], "A3": ["P", "Q", "R"]}

    b = tmp_path / "baseline.json"
    c = tmp_path / "candidate.json"
    b.write_text(json.dumps(baseline), encoding="utf-8")
    c.write_text(json.dumps(candidate), encoding="utf-8")

    res = _run_cli(["compare", "--baseline", str(b), "--candidate", str(c), "--format", "text"])
    assert res.returncode in (0, 1, 2)
    assert "SUMMARY:" in res.stdout


def test_cli_compare_writes_output(tmp_path: Path):
    baseline = {"A1": ["X", "Y", "Z"]}
    candidate = {"A1": ["X", "Y", "Z"]}

    b = tmp_path / "baseline.json"
    c = tmp_path / "candidate.json"
    out = tmp_path / "report.json"
    b.write_text(json.dumps(baseline), encoding="utf-8")
    c.write_text(json.dumps(candidate), encoding="utf-8")

    res = _run_cli(
        [
            "compare",
            "--baseline",
            str(b),
            "--candidate",
            str(c),
            "--k",
            "3",
            "--output",
            str(out),
            "--format",
            "json",
        ]
    )
    assert res.returncode == 0
    assert out.exists()

    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["overall_risk_level"] in ("SAFE", "INFO", "WARNING", "CRITICAL")


def test_cli_error_on_missing_file(tmp_path: Path):
    missing = tmp_path / "nope.json"
    res = _run_cli(["compare", "--baseline", str(missing), "--candidate", str(missing)])
    assert res.returncode == 3
    assert "ERROR:" in res.stderr
