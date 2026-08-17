# CWE-787 length-guard fixture

This is a small, safe-to-run C fixture that demonstrates a boundary-check repair problem.

- The `reference/` program rejects an input whose length equals a 16-byte payload capacity, because copying the NUL terminator would require a 17th byte.
- The `candidate/` program has an intentional off-by-one condition (`>` instead of `>=`) and emits the control-flow event `copy_would_overflow`.
- The candidate deliberately **does not perform the unsafe copy**. It models the security-relevant state/control-flow difference without executing a memory corruption primitive.

Build and analyze:

```bash
python3 build.py
cd ../..
python3 -m acsa_repair analyze \
  --metadata benchmarks/cwe787_length_guard/metadata.json \
  --output results/cwe787_length_guard
```
