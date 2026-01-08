# Example 3: High Churn (Low Overlap)

## Scenario

This example demonstrates a **CRITICAL** condition caused by high neighbor churn (low overlap) between baseline and candidate snapshots.

## Snapshots

**Baseline:**
- 2 anchors, 5 neighbors each
- `anchor_1`: `[a, b, c, d, e]`
- `anchor_2`: `[f, g, h, i, j]`

**Candidate:**
- Same 2 anchors, 5 neighbors each
- `anchor_1`: `[a, x, y, z, w]` — only 1/5 shared with baseline
- `anchor_2`: `[f, p, q, r, s]` — only 1/5 shared with baseline

## Expected Outcome

**Exit Code:** `2` (CRITICAL)

**Why:**
- Mean overlap = 0.20 (well below 0.50 critical threshold)
- Churn rate is very high (most neighbors changed)
- Indicates significant semantic drift in retrieval results
- Both anchors flagged as CRITICAL

## Run This Example

```bash
vector-guardrails compare \
  --baseline examples/03_high_churn/baseline.json \
  --candidate examples/03_high_churn/candidate.json \
  --k 5

echo "Exit code: $?"
```

## Expected Output

```
CRITICAL: Significant changes detected

SUMMARY:
  Compared anchors: 2
  Mean overlap@5: 0.20
  Churn rate: 1.00
  Anchor jaccard: 1.00

DETAILS:
  CRITICAL anchors: 2
  WARNING anchors: 0
```

## Use Case

This scenario may occur when:
- Embedding model has changed significantly
- Vector index configuration was modified
- Document corpus has been substantially updated
- Retrieval algorithm or ranking logic changed
- Distance metric or similarity threshold adjusted

## What To Do

1. **Do NOT deploy** — this level of churn indicates major semantic drift
2. Investigate the root cause:
   - What changed in your retrieval pipeline?
   - Was the embedding model retrained or swapped?
   - Did the document corpus change significantly?
3. Manually inspect affected queries to understand the impact
4. Consider A/B testing if the change is intentional
5. Adjust thresholds only if you've validated that the new results are better

## Why This Matters

High churn means your retrieval system is returning fundamentally different results. Even if the new results are "better" by some metric, this level of change:
- May surprise or confuse users
- Could break downstream systems that depend on specific documents
- Requires careful validation before production deployment
