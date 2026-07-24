# AIML-MRMS non-invasive audit package

This folder is separate from the active pipeline. It does not modify existing
scripts, manuscript files, or files under `results/`.

Run the audit from the repository root:

```powershell
python audit/run_readiness_audit.py
```

It writes dated, traceable evidence under `audit_artifacts/`. The audit checks:

- whether the legacy hard-coded PCI comparison path remains active;
- whether uniform weighted PCI/RPCI reproduces the original unweighted formulas;
- whether saved weighted-comparison files reproduce from the current code and
  current inputs;
- the implemented weighting-scenario definitions; and
- hashes for the relevant code, inputs, and result files.

The audit reports evidence only. It does not make comparative-performance
claims or change the project pipeline.
