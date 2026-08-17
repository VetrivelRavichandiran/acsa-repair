# ACSA Verification Report

**Patch status:** REJECT

This report separates direct observations from hypotheses. It does not establish causality by itself.

## 1. CRITICAL — `length`

**Observed fact**
- Aligned execution: `parse_input` at reference `parser.c:183` and candidate `parser.c:187`.
- `length` changed from `24` to `1024` (numeric; difference: `1000`).
- Alignment confidence: `0.97`; priority score: `86.33`.

**Supported relevance**
- typed divergence: numeric.
- security flow: length → buffer_size → memcpy.
- control-flow path differs.
- near reported vulnerable location.

**Repair guidance (hypothesis)**
- Re-examine how `length` is computed or propagated before preserving the candidate behavior.
- Preserve intended functionality; do not suppress the affected operation merely to remove the signal.

## 2. CRITICAL — `length`

**Observed fact**
- Aligned execution: `parse_input` at reference `parser.c:184` and candidate `parser.c:188`.
- `length` changed from `24` to `1024` (numeric; difference: `1000`).
- Alignment confidence: `0.97`; priority score: `85.36`.

**Supported relevance**
- typed divergence: numeric.
- security flow: length → buffer_size → memcpy.
- control-flow path differs.
- near reported vulnerable location.

**Repair guidance (hypothesis)**
- Re-examine how `length` is computed or propagated before preserving the candidate behavior.
- Preserve intended functionality; do not suppress the affected operation merely to remove the signal.

## 3. CRITICAL — `length`

**Observed fact**
- Aligned execution: `parse_input` at reference `parser.c:180` and candidate `parser.c:180`.
- `length` changed from `24` to `1024` (numeric; difference: `1000`).
- Alignment confidence: `1.00`; priority score: `74.00`.

**Supported relevance**
- typed divergence: numeric.
- security flow: length → buffer_size → memcpy.
- near reported vulnerable location.

**Repair guidance (hypothesis)**
- Re-examine how `length` is computed or propagated before preserving the candidate behavior.
- Preserve intended functionality; do not suppress the affected operation merely to remove the signal.

## 4. CRITICAL — `index`

**Observed fact**
- Aligned execution: `parse_input` at reference `parser.c:183` and candidate `parser.c:187`.
- `index` changed from `23` to `1023` (numeric; difference: `1000`).
- Alignment confidence: `0.97`; priority score: `55.29`.

**Supported relevance**
- typed divergence: numeric.
- control-flow path differs.
- near reported vulnerable location.

**Repair guidance (hypothesis)**
- Re-examine how `index` is computed or propagated before preserving the candidate behavior.
- Preserve intended functionality; do not suppress the affected operation merely to remove the signal.

## 5. HIGH — `__control_flow__`

**Observed fact**
- Aligned execution: `parse_input` at reference `parser.c:183` and candidate `parser.c:187`.
- `__control_flow__` changed from `{'branch': 'within_bounds'}` to `{'branch': 'out_of_bounds'}` (control_flow; difference: `{'reference': {'branch': 'within_bounds'}, 'candidate': {'branch': 'out_of_bounds'}}`).
- Alignment confidence: `0.97`; priority score: `47.53`.

**Supported relevance**
- typed divergence: control_flow.
- control-flow path differs.
- near reported vulnerable location.

**Repair guidance (hypothesis)**
- Re-examine how `__control_flow__` is computed or propagated before preserving the candidate behavior.
- Preserve intended functionality; do not suppress the affected operation merely to remove the signal.

## 6. HIGH — `__control_flow__`

**Observed fact**
- Aligned execution: `parse_input` at reference `parser.c:184` and candidate `parser.c:188`.
- `__control_flow__` changed from `{'branch': 'copy_allowed'}` to `{'branch': 'copy_attempted'}` (control_flow; difference: `{'reference': {'branch': 'copy_allowed'}, 'candidate': {'branch': 'copy_attempted'}}`).
- Alignment confidence: `0.97`; priority score: `46.56`.

**Supported relevance**
- typed divergence: control_flow.
- control-flow path differs.
- near reported vulnerable location.

**Repair guidance (hypothesis)**
- Re-examine how `__control_flow__` is computed or propagated before preserving the candidate behavior.
- Preserve intended functionality; do not suppress the affected operation merely to remove the signal.
