# ACSA-Repair

**Autonomous Cognitive State-Delta Alignment Feedback for LLM-Based Program Repair**

ACSA-Repair is a research prototype for comparing runtime behavior from a known-good **reference** program against an LLM-repaired **candidate**. It turns aligned trace differences into typed state deltas, ranks security-relevant mismatches, and produces structured repair feedback.

## What is implemented in this first MVP

The first vertical slice implements the proposed foundational milestone:

1. execute a reference and a candidate command under the same input/environment;
2. collect JSONL runtime state traces;
3. normalize and align execution states across changed source locations;
4. generate a typed **State-Delta Matrix**;
5. prioritize high-risk differences using vulnerability proximity, control-flow differences, and configured source-to-sink flows;
6. render a factual, clearly labelled feedback report.

It intentionally does **not** call an LLM yet. It now includes a local C fixture, a small candidate reset/fix workflow, and VS Code tasks so you can run the full state-delta feedback loop on your machine.

## Run locally in VS Code

1. Install **Python 3.10+**, a C compiler (**Clang** or **GCC**), and VS Code extensions **Python** and **C/C++**.
2. Open this project folder in VS Code.
3. Open **Terminal → Run Task** and run these tasks in order:
   - `ACSA: Reset C candidate`
   - `ACSA: Analyze C candidate`
   - `ACSA: Apply C guard fix`
   - `ACSA: Analyze C candidate` again
4. Inspect `results/cwe787_length_guard/feedback.md` after each analysis.

The first analysis rejects the intentionally flawed `length > buffer_size` guard. After applying the narrow `length >= buffer_size` correction, the reference and candidate traces agree and the report contains no state divergences.

You can also launch `ACSA: Debug C candidate trace` from VS Code's **Run and Debug** panel after the analysis task builds the executable.

## Analyze many inputs from CSV

The included CSV is `benchmarks/cwe787_length_guard/inputs.csv`. It has a required `input` column and optional `case_id`, `enabled`, and `description` columns:

```csv
case_id,input,enabled,description
safe_short,hello,true,Normal short input
boundary_16,1234567890123456,true,Off-by-one security boundary
skip_example,do-not-run,false,Disabled rows are ignored
```

To compare reference and candidate behavior for every enabled row, run:

```bash
python -m acsa_repair analyze-csv --csv benchmarks/cwe787_length_guard/inputs.csv
```

In VS Code, run the task **`ACSA: Analyze C candidate CSV inputs`**. The command builds the C fixture once, executes every CSV case, and writes:

- `results/cwe787_csv/summary.csv` — spreadsheet-friendly aggregate results;
- `results/cwe787_csv/batch_report.md` — readable result table and totals;
- `results/cwe787_csv/cases/<case>/` — trace files, delta matrix, feedback, and execution details for each individual input.

Use **`ACSA: Reset C candidate`** before batch analysis to see the boundary divergence. Use **`ACSA: Apply C guard fix`** and analyze the same CSV again to verify that the repaired candidate matches the reference across the enabled cases.

## Quick start (terminal)

```bash
cd /path/to/ACSA-Repair
python3 -m acsa_repair reset-c-fixture
python3 -m acsa_repair run-c-fixture
python3 -m acsa_repair fix-c-fixture
python3 -m acsa_repair run-c-fixture
python3 -m unittest discover -s tests -v
```

The synthetic trace-only demonstration remains available:

```bash
python3 -m acsa_repair run-demo
```

The demo writes inspectable artifacts under `results/demo/`:

- `reference_trace.jsonl`
- `candidate_trace.jsonl`
- `aligned_pairs.json`
- `state_delta_matrix.json`
- `prioritized_deltas.json`
- `feedback.md`

## Trace schema (JSON Lines)

Each line is a state observation. Required keys are `event_id`, `function`, `location`, and `variables`.

```json
{
  "event_id": 4,
  "function": "parse_input",
  "location": {"file": "parser.c", "line": 183},
  "iteration": 0,
  "call_stack": ["main", "parse_input"],
  "variables": {
    "length": {"type": "int", "value": 24},
    "buffer_size": {"type": "int", "value": 32}
  },
  "expressions": {"length <= buffer_size": true},
  "control_flow": {"branch": "within_bounds"}
}
```

The project includes both a deterministic synthetic tracer and a **real, compiled C fixture** at `benchmarks/cwe787_length_guard/`. That fixture emits the same schema directly at selected runtime observation points. It is safe by design: its flawed candidate reports that an overflow path would be reached but never performs an unsafe memory write.

## Run against your own trace-producing commands

Create a benchmark metadata file such as:

```json
{
  "id": "example_001",
  "language": "C",
  "cwe": "CWE-787",
  "vulnerable_file": "parser.c",
  "vulnerable_line": 183,
  "reference_command": ["./reference_binary", "input.txt"],
  "candidate_command": ["./candidate_binary", "input.txt"],
  "security_flows": [
    {"source": "length", "transforms": ["buffer_size"], "sink": "memcpy", "severity": "critical"}
  ]
}
```

Then run:

```bash
python3 -m acsa_repair analyze --metadata /absolute/path/to/metadata.json --output /absolute/path/to/results
```

Commands must emit trace JSONL to stdout. Execution results (exit status, stdout/stderr) are captured in `execution.json`. This initial executor has timeouts and a controlled working directory, but it is **not** a hardened security isolation boundary; run untrusted targets in an external sandbox before using this on real malicious inputs.

## Architecture mapping

| Blueprint component | MVP module |
|---|---|
| Reference/Candidate execution | `acsa_repair.executor` |
| Trace/state extraction contract | `acsa_repair.trace` |
| State alignment | `acsa_repair.alignment` |
| State-Delta Matrix | `acsa_repair.delta` |
| Security-aware ranking | `acsa_repair.prioritization` |
| Cognitive interpretation + feedback | `acsa_repair.feedback` |
| Pipeline orchestration | `acsa_repair.pipeline` |

## Current limitations and next increments

- The C fixture uses explicit, **selective trace statements** rather than an LLVM pass. This makes the contract executable now; LLVM/debug instrumentation is the next tracer implementation.
- The included patch workflow is deliberately narrow and fixture-specific. A general Patch Manager should use clean worktrees and record patch provenance.
- The executor controls commands and timeouts but is not a hardened isolation boundary. Use a dedicated sandbox for untrusted repositories.

Next increments:

1. LLVM-based selective instrumentation for C/C++ and a real benchmark corpus.
2. General Patch Manager with clean worktrees, candidate provenance, application/rollback checks.
3. Configurable LLM adapter and repair controller with baseline B/C/D modes.
4. Sanitizer/test feedback ingestion and experiment tracking.
5. Evaluation scripts, ablations, and statistical analysis.
