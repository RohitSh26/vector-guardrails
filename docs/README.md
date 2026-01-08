# Vector Guardrails Documentation

Comprehensive guides for understanding and using Vector Guardrails in production.

---

## New to Vector Guardrails?

Start here to understand the fundamentals:

### 1. [Understanding Anchors and Neighbors](./anchor-terminology.md)
**5 min read** · Clarifies the "anchor" and "neighbor" terminology with concrete examples for search, recommendations, and RAG systems.

**Read this if:** You're confused about what "anchor" means, or unsure if this tool applies to your use case.

---

### 2. [How to Generate Snapshots](./generating-snapshots.md)
**15 min read** · Architecture-agnostic guide with pseudocode for generating snapshots from your retrieval system.

**Read this if:** You understand the concepts but need practical guidance on creating snapshots from your vector store, search engine, or recommendation system.

**Includes examples for:**
- Text search (query → documents)
- Item-to-item recommendations (item → similar items)
- User-based recommendations (user → recommended items)
- Integration with FAISS, Pinecone, Elasticsearch

---

### 3. [When to Use Vector Guardrails](./when-to-use.md)
**10 min read** · Explains exactly when to run comparisons, with 7 concrete scenarios and clear guidance on what NOT to use it for.

**Read this if:** You understand how the tool works but aren't sure when to integrate it into your workflow.

**Covers:**
- Before deploying a new embedding model
- After rebuilding your vector index
- Regression testing for determinism
- A/B test validation
- CI/CD integration patterns

---

## Ready to Use in Production?

### 4. [Threshold Philosophy & Calibration Guide](./thresholds-and-tuning.md)
**20 min read** · Explains why default thresholds exist, how to interpret results, and how to tune for your specific use case and risk tolerance.

**Read this if:** You're getting too many false alarms (or missing real issues), and need to adjust thresholds.

**Covers:**
- Why defaults are conservative by design
- How to measure your system's noise baseline
- Calibration workflow (4 steps)
- Common tuning scenarios (too strict, too loose, non-deterministic systems)
- Red flags to never ignore

---

## Quick Reference

| Question | Answer |
|----------|--------|
| **What is an anchor?** | The input to your retrieval system (query, item, user) |
| **What is a neighbor?** | The output from your retrieval system (results, recommendations) |
| **How do I generate a snapshot?** | See [generating-snapshots.md](./generating-snapshots.md) |
| **When should I run comparisons?** | See [when-to-use.md](./when-to-use.md) |
| **Why did I get a WARNING?** | See [thresholds-and-tuning.md](./thresholds-and-tuning.md) |
| **Can I customize thresholds?** | Yes, via `ThresholdPreset`. See calibration guide. |
| **Is this ready for production?** | v0.1 is functional but early-stage. Use with caution and manual review. |

---

## Recommended Reading Order

### For First-Time Users:
1. [Understanding Anchors and Neighbors](./anchor-terminology.md) ← Start here
2. [How to Generate Snapshots](./generating-snapshots.md)
3. Run the [examples](../examples/)
4. [When to Use Vector Guardrails](./when-to-use.md)

### For Production Integration:
1. [When to Use Vector Guardrails](./when-to-use.md)
2. [Threshold Philosophy & Calibration Guide](./thresholds-and-tuning.md)
3. Generate baseline snapshots from your system
4. Run regression tests (compare system to itself)
5. Integrate into CI/CD with manual review gates

---

## Still Have Questions?

- **Examples:** See [`examples/`](../examples/) for runnable code
- **API Reference:** See [`src/vector_guardrails/models.py`](../src/vector_guardrails/models.py) for data models
- **Design Philosophy:** See [`DESIGN.md`](../DESIGN.md) for the original design document

---

## Contributing to Documentation

Found an error or want to improve these guides? Contributions welcome:

1. Fork the repository
2. Edit the relevant markdown file in `docs/`
3. Submit a pull request

**Especially valuable:**
- Real-world usage examples
- Integration guides for specific vector stores
- Troubleshooting tips from your experience
