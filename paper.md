---
title: 'ACSA-Repair: A Deterministic, Auditable Trace-Divergence Evidence Layer for Program-Repair Workflows'
tags:
  - Python
  - program repair
  - differential execution
  - execution traces
  - runtime state deltas
  - CWE-787
authors:
  - name: R. Vetrivel
    affiliation: 1
affiliations:
 - name: Department of Electronics and Communication Engineering, Central University of Karnataka, Kalaburagi, Karnataka, India
   index: 1
date: 18 August 2026
bibliography: paper.bib
---

# Summary
ACSA-Repair is a deterministic, auditable, trace-driven divergence-analysis and structured-feedback software layer for program-repair workflows[cite: 2]. It addresses the challenge of comparing a patched candidate program against a known-good reference execution[cite: 2]. By capturing standard output as JSONL traces, it transforms raw paired executions into typed, prioritized divergences and issues a heuristic policy output (REJECT/REPAIR)[cite: 2].

# Statement of need
Automated program repair (APR) and differential testing frequently evaluate patches by comparing executions[cite: 2]. However, raw trace differences are difficult to operationalize within automated repair loops due to source-location drift across revisions, heterogeneous runtime states, and the explosion of low-level differences[cite: 2]. Furthermore, security-adjacent repair risks "epistemic collapse"—confusing observed trace facts with inferred vulnerability detection[cite: 2]. 

ACSA-Repair is designed for software engineering researchers and developers building LLM-assisted or agentic repair systems. It provides an epistemically separated evidence layer that distinguishes raw observed facts from heuristic relevance scores and repair hypotheses[cite: 2], ensuring automated decision loops do not silently ingest unverified inferences.

# State of the field
Recent dynamic-evidence and agentic repair tools—such as DynaFix [@Huang2025], ContraFix [@Liu2026], VRpilot, and RepairAgent [@Bouzenia2025]—couple dynamic execution data directly into LLM-driven patch-generation loops, while iFix [@Wang2025] provides interactive runtime comparisons for humans[cite: 2]. However, these systems do not foreground a strict structural separation between deterministic trace facts and heuristic vulnerability hypotheses[cite: 2]. 

ACSA-Repair fills this gap by acting strictly as an inspectable evidence layer. It provides deterministic alignment under source-line drift, control-flow divergence representation, and a transparent heuristic scoring system that stops firmly at the "Association" level of security claims, rather than generating patches or performing probabilistic synthesis[cite: 2].

# Software design
The ACSA-Repair pipeline executes reference and candidate commands under timeout control and validates JSONL traces for required fields and type normalization[cite: 2]. It aligns events deterministically using a stable identity key (function, call stack, iteration, event id) combined with a location-proximity bonus, intentionally excluding exact line numbers to tolerate location drift[cite: 2]. 

The tool extracts a Typed State-Delta Matrix, emitting synthetic control-flow deltas whenever branch labels differ[cite: 2]. Differences are prioritized using an explicit, additively decomposed heuristic score (incorporating divergence magnitude, control-flow bonuses, proximity, and analyst-provided security metadata matched by variable name)[cite: 2]. Finally, the system generates a closed-loop policy decision (REJECT/REPAIR) based on severity thresholds and emits auditable intermediate artifacts (`execution.json`, `aligned_pairs.json`, etc.) alongside an epistemically separated Markdown report[cite: 2].

# Research impact statement
ACSA-Repair enables researchers to incorporate robust dynamic execution evidence into their pipelines without sacrificing determinism. The prototype has been validated against a REAL C fixture exhibiting CWE-787-oriented behavior, successfully aligning events across line-number shifts and properly prioritizing control-flow divergences (e.g., `reject_oversized` vs. `copy_would_overflow`) with a HIGH severity label[cite: 2]. A secondary SYNTHETIC demonstration successfully extracted and ranked typed deltas, highlighting critical transitions in length variables[cite: 2]. By materializing every intermediate artifact, ACSA-Repair provides an auditable foundation for integrating dynamic trace analysis into next-generation automated software repair agents.

# AI usage disclosure
No generative AI tools were used in the creation of the software logic or the core theoretical manuscript. 

# Acknowledgements
This work was conducted at the Department of Electronics and Communication Engineering, Central University of Karnataka[cite: 2].

# References
