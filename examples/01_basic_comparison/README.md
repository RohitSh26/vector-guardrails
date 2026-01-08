# Example 1: Basic Comparison (Identical Snapshots)

## Scenario

This example demonstrates the baseline case where retrieval results are **identical** between baseline and candidate snapshots.

## Snapshots

Both `baseline.json` and `candidate.json` contain:
- 2 anchors
- 3 neighbors per anchor
- Identical anchor IDs and neighbor lists

## Expected Outcome

**Exit Code:** `0` (SAFE/INFO)

**Why:**
- Perfect overlap (1.00) for all anchors
- No neighbor churn
- Anchor Jaccard = 1.00 (identical anchor sets)
- All metrics indicate no changes

## Run This Example

```bash
vector-guardrails compare \
  --baseline examples/01_basic_comparison/baseline.json \
  --candidate examples/01_basic_comparison/candidate.json \
  --k 3

echo "Exit code: $?"
```

## Expected Output

```
SAFE: No significant changes detected

SUMMARY:
  Compared anchors: 2
  Mean overlap@3: 1.00
  Churn rate: 0.00
  Anchor jaccard: 1.00

DETAILS:
  CRITICAL anchors: 0
  WARNING anchors: 0
```

## Use Case

This scenario represents:
- No changes to the retrieval system
- Regression testing (ensuring deterministic behavior)
- Sanity check before introducing changes
