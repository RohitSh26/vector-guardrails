# Example 2: Anchor Mismatch (Low Jaccard)

## Scenario

This example demonstrates a **WARNING** condition caused by low anchor overlap between baseline and candidate snapshots.

## Snapshots

**Baseline:**
- 3 anchors: `anchor_1`, `anchor_2`, `anchor_3`

**Candidate:**
- 2 anchors: `anchor_1`, `anchor_4`

**Overlap:**
- Only `anchor_1` appears in both snapshots
- `anchor_2` and `anchor_3` are baseline-only
- `anchor_4` is candidate-only

## Expected Outcome

**Exit Code:** `1` (WARNING)

**Why:**
- Anchor Jaccard = 1 / 4 = **0.25** (well below 0.90 threshold)
- Only 1 anchor can be compared
- Indicates significant mismatch in anchor sets
- The library warns about low anchor overlap but proceeds with comparison

## Run This Example

```bash
vector-guardrails compare \
  --baseline examples/02_anchor_mismatch/baseline.json \
  --candidate examples/02_anchor_mismatch/candidate.json \
  --k 3

echo "Exit code: $?"
```

## Expected Output

```
WARNING: Low anchor overlap detected

SUMMARY:
  Compared anchors: 1
  Mean overlap@3: 1.00
  Churn rate: 0.00
  Anchor jaccard: 0.25

DETAILS:
  CRITICAL anchors: 0
  WARNING anchors: 0
```

**Key observation:** Even though the single compared anchor (`anchor_1`) has perfect overlap, the **overall risk level is WARNING** due to the low anchor Jaccard score.

## Use Case

This scenario may occur when:
- The query/anchor set has changed significantly
- Different test queries are used in baseline vs candidate
- Document filtering or corpus changes affect which queries return results
- You're comparing snapshots from different evaluation datasets

## What To Do

1. Investigate why anchor sets differ
2. Ensure baseline and candidate use the same query set
3. Check for corpus changes that might affect query coverage
4. Consider whether the anchor mismatch is expected (e.g., intentional query set update)
