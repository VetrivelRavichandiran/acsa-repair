# ⚡ ACSA-Repair — Titan Evidence Edition

### **Deterministic, Auditable Trace-Divergence Analysis for Program Repair**

> **From Reference + Candidate Executions → Structured Evidence → Prioritized Divergences → Repair Feedback.**

---

## 🚀 Features

### 🔗 Deterministic Trace Alignment

- 🔍 Aligns reference and candidate execution traces
- 📍 Robust to tested source-line drift
- ⚙️ Explicit, non-probabilistic alignment scoring
- 🔒 Deterministic and reproducible behavior

### 🧬 Typed Divergence Analysis

- 🔢 Numeric / Boolean / String / Pointer / Type deltas
- 🌳 Explicit control-flow divergence detection
- 📊 Generates a structured **Typed State-Delta Matrix**
- 🔎 Converts raw trace differences into interpretable evidence

### 🎯 Transparent Prioritization

- 📈 Additively decomposed heuristic scoring
- 🛡️ Optional analyst-provided security metadata
- 📍 Vulnerable-location proximity awareness
- 🚦 `LOW → MEDIUM → HIGH → CRITICAL` severity

### 🧠 Epistemically Separated Feedback

- 👁️ **Observed:** What actually happened
- 📊 **Relevant:** Why the divergence was prioritized
- 💡 **Hypothesis:** What it may suggest for repair

> Prevents heuristic analysis from being presented as verified security or correctness claims.

### 📦 Artifact-First Reproducibility

Generates auditable intermediate artifacts:

```text
execution.json
reference_trace.jsonl
candidate_trace.jsonl
aligned_pairs.json
state_delta_matrix.json
prioritized_deltas.json
feedback.md
