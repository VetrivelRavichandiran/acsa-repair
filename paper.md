---
title: 'ACSA-Repair: A Deterministic, Auditable Trace-Divergence Evidence Layer for Program-Repair Workflows'
tags:
  - Python
  - automated program repair
  - differential execution
  - execution traces
  - trace alignment
  - runtime state analysis
  - software testing
  - vulnerability analysis
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

ACSA-Repair is an open-source software layer for deterministic trace-divergence analysis in program-repair workflows. It compares executions of a known-good reference program and a candidate program, converts their runtime behavior into structured JSONL traces, deterministically aligns corresponding events, extracts typed runtime-state differences, prioritizes the resulting divergences, and produces structured feedback for downstream repair workflows.

The system is designed around an explicit separation between observed execution evidence and heuristic interpretation. Reference and candidate executions are captured as JSONL traces and validated before analysis. Events are aligned using a stable execution identity together with source-location proximity, allowing the analysis to tolerate the tested form of source-line drift. Runtime differences are represented as a Typed State-Delta Matrix, including explicit control-flow deltas when corresponding branch labels differ.

ACSA-Repair optionally incorporates analyst-provided security metadata as a prioritization signal through variable-name matching. It then applies a transparent, additively decomposed heuristic score and produces a heuristic `REJECT` or `REPAIR` policy output based on the severity labels of the highest-ranked divergences. Intermediate artifacts are materialized throughout the pipeline so that users can inspect the evidence, alignment, state deltas, scores, and final feedback independently.

ACSA-Repair does not generate patches, perform taint analysis, infer static data flow, provide formal verification, or sandbox executed programs. Its purpose is to provide a deterministic and auditable evidence layer that can be integrated with automated, human-assisted, or LLM-assisted program-repair workflows.

# Statement of need

Automated program repair (APR) and differential testing frequently compare the behavior of a candidate program against a reference execution [@LeGoues2012; @McKeeman1998]. Raw execution differences, however, are difficult to use directly inside repair workflows. Source locations may change between program versions, different versions may expose different runtime variables or types, and a small behavioral change can generate many low-level differences that require prioritization.

These challenges are particularly relevant to modern repair systems that incorporate dynamic execution evidence into automated or LLM-assisted workflows [@Bouzenia2025; @Huang2025; @Liu2026]. A downstream repair system needs to distinguish what was directly observed during execution from what is inferred to be relevant and from what should be done next. Without such a distinction, heuristic evidence can be unintentionally treated as a security verdict, a correctness proof, or a causal explanation.

ACSA-Repair addresses this problem as an independent evidence-processing layer. Its target users are software-engineering researchers and developers working on automated program repair, differential testing, dynamic analysis, and agentic software-engineering systems.

The software operationalizes four requirements: deterministic correspondence under modest source-location drift, typed representation of heterogeneous runtime differences, transparent prioritization of potentially important divergences, and explicit separation between observed evidence and downstream repair guidance. The resulting artifacts are designed to be inspectable by researchers or consumed by subsequent repair components.

# State of the field

Automated program repair has developed from search-based approaches such as GenProg [@LeGoues2012] to semantics-based methods such as SemFix [@Nguyen2013] and Angelix [@Mechtaev2016]. Differential testing and debugging research has likewise established the value of comparing executions and isolating behavioral differences [@Zeller2002; @McKeeman1998].

Recent systems increasingly incorporate dynamic evidence into LLM-assisted or agentic repair. RepairAgent uses an autonomous LLM-based repair workflow [@Bouzenia2025], while DynaFix incorporates execution-level dynamic information into iterative repair [@Huang2025]. ContraFix uses differential runtime evidence for agentic vulnerability repair [@Liu2026]. Interactive runtime comparison has also been investigated by iFix [@Wang2025], while SWE-bench demonstrates the broader importance of executable feedback in evaluating software-engineering agents [@Jimenez2024].

ACSA-Repair is complementary to these systems rather than a replacement for them. It does not generate patches or operate as an autonomous repair agent. Instead, it focuses on the intermediate representation between paired executions and downstream repair decisions.

The software's distinguishing design contribution is the combination of deterministic trace alignment, typed state and control-flow divergence representation, transparent heuristic prioritization, and an explicitly separated feedback structure. Each reported divergence distinguishes **Observed Fact**, **Supported Relevance**, and **Repair Guidance (Hypothesis)**. This separation is an architectural property of the generated evidence rather than merely a presentation convention.

ACSA-Repair therefore follows a build-rather-than-reimplement rationale: existing APR and agentic systems address patch generation, repair reasoning, or runtime comparison, whereas ACSA-Repair provides a reusable evidence layer that can potentially supply structured and auditable dynamic evidence to such systems.

# Software design

ACSA-Repair implements a staged pipeline.

First, reference and candidate commands are executed under timeout control. Their standard output is captured as JSONL traces and an execution record is produced. The timeout limits execution duration but does not provide sandboxing or isolation.

Second, trace events are validated for required fields and normalized by runtime type. This creates a consistent representation for subsequent comparison.

Third, reference and candidate events are deterministically aligned. The alignment mechanism uses a stable identity based on execution context, including function, call-stack information, iteration, and event identity, together with a source-location proximity component. Exact line-number equality is not used as the sole correspondence criterion. Candidate-event reuse is prevented during alignment.

Fourth, aligned events are converted into a Typed State-Delta Matrix. Runtime value differences are represented explicitly according to their observed types. When corresponding branch labels differ, a synthetic `control_flow` delta is emitted so that path divergence is represented directly rather than being hidden within missing or mismatched state observations.

Fifth, divergences are prioritized using an explicit additive heuristic. The score can incorporate divergence magnitude, control-flow relevance, source-location proximity, and analyst-provided security metadata. Security metadata is matched by variable name and is therefore treated as trusted analyst input rather than as inferred program semantics.

Finally, the highest-ranked deltas are rendered into structured feedback and a heuristic policy output. The policy is deterministic:

- `REJECT` if a top-ranked delta has `HIGH` or `CRITICAL` heuristic severity.
- `REPAIR` otherwise.

This policy is explicitly not a verification result and does not prove that a patch is incorrect.

The pipeline materializes intermediate artifacts including `execution.json`, `reference_trace.jsonl`, `candidate_trace.jsonl`, `aligned_pairs.json`, `state_delta_matrix.json`, `prioritized_deltas.json`, and `feedback.md`. This artifact-oriented design allows individual processing stages to be inspected independently and supports reproducible testing.

# Research impact statement

The current evaluation provides artifact-grounded prototype validation rather than benchmark-scale effectiveness evaluation.

The authoritative regression suite consists of eight tests and was executed twice using the same command:

```text
python -m unittest discover -s tests -v
