# Issue: Empty Anchor Intersection Returns INFO Instead of WARNING

## Current Behavior

When `compared_anchors == 0` (i.e., baseline and candidate have zero overlapping anchors), the system currently returns `RiskLevel.INFO`.

## Expected Behavior (Question)

Should zero anchor overlap be treated as:
1. **INFO** (current) — "We can't compare anything, but no error occurred"
2. **WARNING** — "Zero overlap suggests a significant mismatch that warrants attention"

## Example Scenario

```json
// baseline.json
{
  "anchor_1": ["neighbor_a", "neighbor_b"],
  "anchor_2": ["neighbor_c", "neighbor_d"]
}

// candidate.json
{
  "anchor_3": ["neighbor_e", "neighbor_f"],
  "anchor_4": ["neighbor_g", "neighbor_h"]
}
```

**Current result:** `RiskLevel.INFO`, exit code `0`

## Arguments for INFO (Current)

- No data was actually compared, so we can't assess risk
- The comparison is technically valid (no errors occurred)
- Distinguishes "no comparison possible" from "comparison shows issues"
- Allows users to decide how to handle this case in their workflows

## Arguments for WARNING

- Zero overlap likely indicates a configuration error or major system change
- Anchor Jaccard = 0.00 already triggers a WARNING
- Users might not notice INFO-level alerts in CI/CD pipelines
- "No comparison possible" is itself a risky situation

## Decision Needed

Should we:
1. Keep current behavior (INFO)
2. Change to WARNING
3. Make it configurable via `ComparisonConfig`
4. Return ERROR instead (invalid input)

## Related Code

- `src/vector_guardrails/compare.py` — risk classification logic
- `src/vector_guardrails/alignment.py` — `anchor_mismatch_warning()` function
- `src/vector_guardrails/models.py` — `RiskLevel`, `ExitCode` enums

## Additional Context

Note that `anchor_jaccard < 0.90` already triggers a WARNING via `anchor_mismatch_warning()`. However, when `compared_anchors == 0`, the overall risk level is set to INFO in the final rollup logic.
