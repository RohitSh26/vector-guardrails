# Issue: min_anchors Config Exists But Is Never Enforced

## Current Behavior

`ComparisonConfig.min_anchors` exists (default: 10) but is **never validated or enforced** anywhere in the codebase.

## Discovery

While reviewing the config model:

```python
class ComparisonConfig(BaseModel):
    k: int = Field(10, ge=1)
    require_exact_match: bool = False
    min_anchors: int = Field(10, ge=1)  # ← Defined but unused
    thresholds: ThresholdPreset = Field(default_factory=ThresholdPreset)
    segment_keys: list[str] = Field(default_factory=list)
```

Searching for `min_anchors` usage in the codebase shows:
- Defined in `models.py`
- Passed through CLI `--min-anchors` flag
- **Never checked or enforced**

## Expected Behavior (Question)

What should happen when `compared_anchors < min_anchors`?

### Option 1: Raise Error (Strict)
```python
if alignment.compared_anchors < config.min_anchors:
    raise ValueError(
        f"Insufficient anchors for comparison: "
        f"{alignment.compared_anchors} < {config.min_anchors}"
    )
```

**Pros:** Clear failure mode, prevents unreliable comparisons
**Cons:** Breaks existing workflows, strict

### Option 2: Return WARNING
```python
if alignment.compared_anchors < config.min_anchors:
    overall_risk_level = max(overall_risk_level, RiskLevel.WARNING)
    verdict_summary += f" (Only {alignment.compared_anchors} anchors compared, minimum {config.min_anchors} recommended)"
```

**Pros:** Soft warning, allows comparison to proceed
**Cons:** Might be ignored in CI/CD

### Option 3: Return INFO with Note
```python
if alignment.compared_anchors < config.min_anchors:
    overall_risk_level = RiskLevel.INFO
    verdict_summary = f"Comparison completed with {alignment.compared_anchors} anchors (below minimum {config.min_anchors})"
```

**Pros:** Neutral signal, informational
**Cons:** Might defeat the purpose of having a minimum

### Option 4: Remove the Config Field

If we don't intend to enforce it, remove `min_anchors` entirely to avoid confusion.

## Decision Needed

1. Should `min_anchors` be enforced?
2. If yes, how (error, warning, info)?
3. If no, should we remove it from the config?
4. Where should the enforcement happen (`compare.py` or `alignment.py`)?

## Related Code

- `src/vector_guardrails/models.py:65` — config definition
- `src/vector_guardrails/cli.py:21` — CLI flag parsing
- `src/vector_guardrails/compare.py` — main comparison logic (no enforcement)
- `src/vector_guardrails/alignment.py` — alignment logic (no enforcement)

## Use Case

The original intent was likely:
> "Only trust comparisons with at least N anchors to ensure statistical reliability"

This makes sense for preventing false confidence from tiny sample sizes.

## Recommendation

Implement **Option 2** (WARNING):
- Non-breaking (allows comparison to proceed)
- Visible signal in CI/CD (exit code 1)
- Aligns with conservative-by-default principle
- Can be overridden by setting `min_anchors=1` if user wants

But this needs product/design decision.
