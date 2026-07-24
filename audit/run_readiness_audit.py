"""Read-only reproducibility and table-readiness audit for AIML-MRMS.

This script deliberately writes only under audit_artifacts/. It does not run
or modify the production pipeline and does not overwrite results/ outputs.
"""

from __future__ import annotations

import csv
import hashlib
import json
import platform
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from aiml_mrms.data_utils import load_feature_matrix
from aiml_mrms.mcdm import weight_evolution
from aiml_mrms.pci import compute_pci_table, pci, rpci
from aiml_mrms.svm_validation import linear_svc_feature_weights
from aiml_mrms.weighted_pci import (
    PCI_DIMENSIONS,
    compute_weighted_pci_table,
    weighted_pci,
    weighted_rpci,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = ROOT / "audit_artifacts" / stamp
    out.mkdir(parents=True, exist_ok=False)

    paths = {
        "legacy_pci_module": ROOT / "src" / "aiml_mrms" / "pci.py",
        "legacy_pci_runner": ROOT / "scripts" / "03_run_pci_rpci.py",
        "weighted_pci_module": ROOT / "src" / "aiml_mrms" / "weighted_pci.py",
        "weighted_pci_runner": ROOT / "scripts" / "07_run_weighted_pci.py",
        "pci_inputs": ROOT / "data" / "processed" / "pci_input_vectors.csv",
        "svm_metrics": ROOT / "results" / "tables" / "table5_svm_loo_metrics.csv",
        "criterion_weights": ROOT / "results" / "tables" / "table6_aggregated_criterion_weights.csv",
    }
    hashes = [{"artifact": name, "path": str(path.relative_to(ROOT)), "sha256": sha256(path) if path.exists() else "MISSING"} for name, path in paths.items()]
    write_csv(out / "artifact_hashes.csv", hashes)

    legacy_module = paths["legacy_pci_module"].read_text(encoding="utf-8")
    legacy_runner = paths["legacy_pci_runner"].read_text(encoding="utf-8")
    hardcoded_gains = bool(re.search(r"gains\s*=\s*\{", legacy_module))
    legacy_output_active = "pci_gain_scenarios" in legacy_runner and "table8_pci_rpci_scenarios.csv" in legacy_runner
    legacy_rows = [{
        "check": "legacy_hard_coded_gain_function_present",
        "status": "FAIL" if hardcoded_gains else "PASS",
        "evidence": "pci_gain_scenarios() contains a literal gains dictionary" if hardcoded_gains else "No literal gain dictionary found",
    }, {
        "check": "legacy_comparison_output_active_in_pipeline_step_03",
        "status": "FAIL" if legacy_output_active else "PASS",
        "evidence": "03_run_pci_rpci.py calls pci_gain_scenarios() and writes table8_pci_rpci_scenarios.csv" if legacy_output_active else "Legacy scenario output call not found",
    }]
    write_csv(out / "legacy_path_checks.csv", legacy_rows)

    input_df = pd.read_csv(paths["pci_inputs"])
    baseline = compute_pci_table(input_df).set_index("iso3")
    uniform_rows = []
    uniform = np.ones(len(PCI_DIMENSIONS)) / len(PCI_DIMENSIONS)
    for _, row in input_df.iterrows():
        x = row[PCI_DIMENSIONS].to_numpy(dtype=float)
        iso = row["iso3"]
        uniform_rows.append({
            "iso3": iso,
            "pci_difference": weighted_pci(x, uniform) - pci(x),
            "rpci_difference": weighted_rpci(x, uniform) - rpci(x),
            "status": "PASS" if np.isclose(weighted_pci(x, uniform), baseline.loc[iso, "pci"], atol=1e-12) and np.isclose(weighted_rpci(x, uniform), baseline.loc[iso, "rpci"], atol=1e-12) else "FAIL",
        })
    write_csv(out / "uniform_formula_equivalence.csv", uniform_rows)

    metrics = pd.read_csv(paths["svm_metrics"])
    modal_c = float(metrics.loc[0, "modal_C"])
    _, X, y = load_feature_matrix()
    _, crit = linear_svc_feature_weights(X, y, C=modal_c)
    ai_signal = crit.set_index("criterion")["svm_signal"].to_dict()
    base_weights = [0.350, 0.300, 0.200, 0.150]
    evolution = weight_evolution(base_weights, [ai_signal[c] for c in ["EV", "RC", "EI", "OF"]], alpha=0.65, cycles=3)
    expected = compute_weighted_pci_table(input_df, evolution, ai_signal)
    expected.to_csv(out / "current_code_weighted_scenarios.csv", index=False)
    evolution.to_csv(out / "weight_states.csv", index=False)
    crit.to_csv(out / "current_code_criterion_signal.csv", index=False)

    config_rows = [
        {"scenario": "standalone_mcdm", "weight_source": "Base AHP criterion weights", "updates": "0", "feedback_or_convergence_claim_supported": "No"},
        {"scenario": "standalone_ai", "weight_source": "Pure aggregate SVM criterion signal", "updates": "0", "feedback_or_convergence_claim_supported": "No"},
        {"scenario": "static_ai_mcdm", "weight_source": "One blend of AHP and SVM signal", "updates": "1", "feedback_or_convergence_claim_supported": "No"},
        {"scenario": "aiml_mrms_full_adaptive", "weight_source": "Second blend of the same AHP and SVM signal", "updates": "2", "feedback_or_convergence_claim_supported": "No"},
    ]
    write_csv(out / "configuration_manifest.csv", config_rows)

    comparisons = []
    for candidate in sorted((ROOT / "results" / "tables").glob("table8_weighted*.csv")):
        saved = pd.read_csv(candidate)
        key = ["iso3", "configuration"]
        if not set(key + ["pci_c3", "rpci_c3"]).issubset(saved.columns):
            comparisons.append({"file": str(candidate.relative_to(ROOT)), "status": "FAIL", "reason": "Required columns are missing", "rows_compared": 0, "max_abs_pci_c3_difference": ""})
            continue
        joined = saved.merge(expected[key + ["pci_c3", "rpci_c3"]], on=key, how="outer", suffixes=("_saved", "_current"), indicator=True)
        comparable = joined[joined["_merge"] == "both"].copy()
        max_diff = float(np.max(np.abs(comparable["pci_c3_saved"] - comparable["pci_c3_current"]))) if not comparable.empty else float("inf")
        max_rpci_diff = float(np.max(np.abs(comparable["rpci_c3_saved"] - comparable["rpci_c3_current"]))) if not comparable.empty else float("inf")
        status = "PASS" if len(comparable) == len(expected) == len(saved) and max_diff <= 1e-12 and max_rpci_diff <= 1e-12 else "FAIL"
        comparisons.append({"file": str(candidate.relative_to(ROOT)), "status": status, "reason": "Matches current code and inputs" if status == "PASS" else "Saved values do not fully reproduce from current code and inputs", "rows_compared": len(comparable), "max_abs_pci_c3_difference": max_diff, "max_abs_rpci_c3_difference": max_rpci_diff})
    write_csv(out / "saved_weighted_output_reproducibility.csv", comparisons)

    report = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version,
        "platform": platform.platform(),
        "audit_scope": "Read-only audit; no production pipeline scripts or result files were modified.",
        "legacy_path_checks": legacy_rows,
        "uniform_formula_equivalence": {"countries_checked": len(uniform_rows), "passed": sum(r["status"] == "PASS" for r in uniform_rows), "failed": sum(r["status"] == "FAIL" for r in uniform_rows)},
        "weighted_output_reproducibility": comparisons,
        "key_interpretation": [
            "Uniform-weight equivalence validates the implementation relationship between the old and weighted equations; it does not validate the new weighted methodology.",
            "The configuration manifest describes weighting scenarios, not independently executed decision architectures.",
            "Any saved weighted output that does not reproduce from the current code and inputs should not be used as manuscript evidence until reconciled.",
        ],
    }
    (out / "audit_summary.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (ROOT / "audit_artifacts" / "LATEST.txt").write_text(str(out.relative_to(ROOT)), encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"\nAudit artifacts written to: {out}")


if __name__ == "__main__":
    main()
