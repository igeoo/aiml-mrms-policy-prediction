"""Generate a non-invasive Version C evidence package.

Version C scores five WGI governance dimensions using the RC/EI/OF projection
of the four-criterion AIML-MRMS weight state. EV remains available to the
project-level architecture. FDI is excluded from PCI/RPCI and reported as a
separate descriptive investment-flow indicator.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from aiml_mrms.data_utils import load_feature_matrix
from aiml_mrms.governance_pci import (
    GOVERNANCE_DIMENSIONS,
    compute_governance_pci_table,
    governance_dimension_weights,
    governance_metric_components,
    governance_scoring_criterion_weights,
)
from aiml_mrms.mcdm import weight_evolution
from aiml_mrms.svm_validation import linear_svc_feature_weights


CRITERIA = ["EV", "RC", "EI", "OF"]
BASE_WEIGHTS = [0.350, 0.300, 0.200, 0.150]
ALPHAS = [0.25, 0.50, 0.65, 0.75]
STATES = [1, 2, 3, 4, 5]
SCENARIO_ORDER = ["standalone_mcdm", "standalone_ai", "static_ai_mcdm", "aiml_mrms_full_adaptive"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate the complete Version C evidence package.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--output-dir", type=Path, help="Exact new output directory to create.")
    group.add_argument("--run-id", help="Directory name created beneath audit_artifacts/.")
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def package_version(name: str) -> str:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return "not-installed"


def git_context() -> dict:
    def run(*args: str) -> str:
        try:
            return subprocess.check_output(["git", *args], cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
        except (OSError, subprocess.CalledProcessError):
            return "unavailable"

    return {
        "branch": run("branch", "--show-current"),
        "commit": run("rev-parse", "HEAD"),
        "working_tree_status": run("status", "--short"),
    }


def rank_correlation(left: pd.Series, right: pd.Series) -> float:
    """Spearman correlation implemented as Pearson correlation of ranks."""

    return float(left.rank(method="average").corr(right.rank(method="average"), method="pearson"))


def write_markdown(path: Path, text: str) -> None:
    path.write_text(text.strip() + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    if args.output_dir:
        out = args.output_dir.resolve()
    else:
        out = ROOT / "audit_artifacts" / (args.run_id or f"{stamp}_version_c")
    out.mkdir(parents=True, exist_ok=False)

    input_paths = {
        "pci_input_vectors": ROOT / "data" / "processed" / "pci_input_vectors.csv",
        "feature_matrix_normalised": ROOT / "data" / "processed" / "feature_matrix_normalised.csv",
        "svm_loo_metrics": ROOT / "results" / "tables" / "table5_svm_loo_metrics.csv",
    }
    pci_input = pd.read_csv(input_paths["pci_input_vectors"])
    metrics = pd.read_csv(input_paths["svm_loo_metrics"])
    modal_c = float(metrics.loc[0, "modal_C"])
    _, X, y = load_feature_matrix()
    feature_signal_df, criterion_signal_df = linear_svc_feature_weights(X, y, C=modal_c)
    feature_signal_df.to_csv(out / "svm_feature_signal_recomputed.csv", index=False)
    criterion_signal_df.to_csv(out / "svm_criterion_signal_recomputed.csv", index=False)
    ai_signal = criterion_signal_df.set_index("criterion")["svm_signal"].to_dict()
    signal_array = [ai_signal[key] for key in CRITERIA]

    # Main four scenario states (base AHP, pure aggregate SVM signal, one
    # blend, two blends) projected onto the governance scoring subspace.
    main_evolution = weight_evolution(BASE_WEIGHTS, signal_array, alpha=0.65, cycles=3)
    table8_long = compute_governance_pci_table(pci_input, main_evolution, ai_signal)
    table8_long["pci_rank_within_scenario"] = table8_long.groupby("scenario")["pci"].rank(ascending=False, method="min").astype(int)
    table8_long["rpci_rank_within_scenario"] = table8_long.groupby("scenario")["rpci"].rank(ascending=False, method="min").astype(int)
    table8_long.to_csv(out / "candidate_table8_version_c_long.csv", index=False)
    table8_long.to_csv(out / "metric_decomposition_by_country_and_scenario.csv", index=False)

    # Compact manuscript layout: the reference is the uniform five-WGI score,
    # not the former six-dimension WGI+FDI reference.
    reference = table8_long.drop_duplicates("iso3").set_index("iso3")
    pci_wide = table8_long.pivot(index="iso3", columns="scenario", values="pci").reindex(columns=SCENARIO_ORDER)
    rpci_wide = table8_long.pivot(index="iso3", columns="scenario", values="rpci").reindex(columns=SCENARIO_ORDER)
    manuscript8 = pd.DataFrame(index=pci_wide.index)
    manuscript8["PCI_uniform_governance_reference"] = reference["pci_uniform_governance_reference"]
    for scenario in SCENARIO_ORDER:
        manuscript8[f"PCI_{scenario}"] = pci_wide[scenario]
    manuscript8["RPCI_uniform_governance_reference"] = reference["rpci_uniform_governance_reference"]
    for scenario in SCENARIO_ORDER:
        manuscript8[f"RPCI_{scenario}"] = rpci_wide[scenario]
    manuscript8.reset_index().to_csv(out / "table8_version_c_manuscript_matrix.csv", index=False)

    # Alpha/state sensitivity retains the complete four-criterion state for
    # architectural traceability, then records the projected RC/EI/OF scoring
    # weights and five dimension weights used by PCI/RPCI.
    state_rows = []
    sensitivity_rows = []
    for alpha in ALPHAS:
        evolution = weight_evolution(BASE_WEIGHTS, signal_array, alpha=alpha, cycles=max(STATES))
        for state in STATES:
            full = evolution.loc[evolution["cycle"] == state, CRITERIA].iloc[0].to_dict()
            projected = governance_scoring_criterion_weights(full)
            dimensions = governance_dimension_weights(full)
            state_rows.append(
                {
                    "alpha": alpha,
                    "state": state,
                    **{f"full_{key}": full[key] for key in CRITERIA},
                    **{f"scoring_{key}": projected[key] for key in ("RC", "EI", "OF")},
                    **{f"dimension_{name}": value for name, value in zip(GOVERNANCE_DIMENSIONS, dimensions)},
                }
            )
            for _, country in pci_input.iterrows():
                values = country[GOVERNANCE_DIMENSIONS].to_numpy(dtype=float)
                components = governance_metric_components(values, dimensions)
                sensitivity_rows.append(
                    {
                        "alpha": alpha,
                        "state": state,
                        "iso3": country["iso3"],
                        "fdi_index_context": country["fdi_index"],
                        **components,
                    }
                )
    states = pd.DataFrame(state_rows)
    sensitivity = pd.DataFrame(sensitivity_rows)
    states.to_csv(out / "candidate_table9a_full_and_projected_weight_states.csv", index=False)

    state1 = sensitivity[sensitivity["state"] == 1][["alpha", "iso3", "pci", "rpci"]].rename(
        columns={"pci": "pci_state1", "rpci": "rpci_state1"}
    )
    sensitivity = sensitivity.merge(state1, on=["alpha", "iso3"], validate="many_to_one")
    sensitivity["delta_pci_from_state1"] = sensitivity["pci"] - sensitivity["pci_state1"]
    sensitivity["delta_rpci_from_state1"] = sensitivity["rpci"] - sensitivity["rpci_state1"]
    sensitivity.to_csv(out / "candidate_table9b_governance_score_sensitivity.csv", index=False)

    stability_rows = []
    for (alpha, state), group in sensitivity.groupby(["alpha", "state"], sort=True):
        stability_rows.append(
            {
                "alpha": alpha,
                "state": state,
                "pci_spearman_vs_state1": rank_correlation(group["pci_state1"], group["pci"]),
                "rpci_spearman_vs_state1": rank_correlation(group["rpci_state1"], group["rpci"]),
                "mean_abs_delta_pci": float(group["delta_pci_from_state1"].abs().mean()),
                "mean_abs_delta_rpci": float(group["delta_rpci_from_state1"].abs().mean()),
                "max_abs_delta_pci": float(group["delta_pci_from_state1"].abs().max()),
                "max_abs_delta_rpci": float(group["delta_rpci_from_state1"].abs().max()),
            }
        )
    stability = pd.DataFrame(stability_rows)
    stability.to_csv(out / "candidate_table9c_ranking_stability.csv", index=False)
    manuscript9 = states[["alpha", "state", "scoring_RC", "scoring_EI", "scoring_OF"]].merge(
        stability, on=["alpha", "state"], validate="one_to_one"
    )
    manuscript9.to_csv(out / "table9_version_c_manuscript_summary.csv", index=False)

    # Separate, descriptive FDI association. This is not included in PCI/RPCI
    # and is not treated as causal or independent external validation.
    fdi = pci_input.set_index("iso3")["fdi_index"].sort_index()
    association_rows = [
        {
            "score_specification": "uniform_governance_reference",
            "fdi_spearman_with_pci": rank_correlation(fdi, reference.loc[fdi.index, "pci_uniform_governance_reference"]),
            "fdi_spearman_with_rpci": rank_correlation(fdi, reference.loc[fdi.index, "rpci_uniform_governance_reference"]),
            "n_countries": len(fdi),
        }
    ]
    fdi_detail = pd.DataFrame({"iso3": fdi.index, "fdi_index": fdi.values, "fdi_rank_desc": fdi.rank(ascending=False, method="min").astype(int).values})
    for scenario in SCENARIO_ORDER:
        scenario_scores = table8_long[table8_long["scenario"] == scenario].set_index("iso3").loc[fdi.index]
        association_rows.append(
            {
                "score_specification": scenario,
                "fdi_spearman_with_pci": rank_correlation(fdi, scenario_scores["pci"]),
                "fdi_spearman_with_rpci": rank_correlation(fdi, scenario_scores["rpci"]),
                "n_countries": len(fdi),
            }
        )
        fdi_detail[f"pci_{scenario}"] = scenario_scores["pci"].values
        fdi_detail[f"rpci_{scenario}"] = scenario_scores["rpci"].values
    pd.DataFrame(association_rows).to_csv(out / "fdi_descriptive_association_summary.csv", index=False)
    fdi_detail.to_csv(out / "fdi_descriptive_country_detail.csv", index=False)

    pd.DataFrame(
        [
            {"analytical_level": "Country governance", "construct": "PCI/RPCI", "criteria_used": "RC, EI, OF (renormalised)", "dimensions": "Five WGI governance dimensions", "FDI_role": "Excluded"},
            {"analytical_level": "Project evaluation", "construct": "AHP/TOPSIS", "criteria_used": "EV, RC, EI, OF", "dimensions": "Project decision criteria", "FDI_role": "No change to existing project-level design"},
            {"analytical_level": "Country investment context", "construct": "FDI descriptive indicator", "criteria_used": "None", "dimensions": "Normalised FDI inflow", "FDI_role": "Reported separately"},
        ]
    ).to_csv(out / "version_c_construct_separation_manifest.csv", index=False)

    # Core invariants and independent formula checks.
    feature_iso = pd.read_csv(input_paths["feature_matrix_normalised"])["iso3"]
    checks = {
        "country_iso_unique": bool(pci_input["iso3"].is_unique and pci_input["iso3"].notna().all()),
        "country_sets_match_feature_matrix": set(pci_input["iso3"]) == set(feature_iso),
        "expected_scenario_rows": len(table8_long) == len(pci_input) * len(SCENARIO_ORDER),
        "each_country_has_all_scenarios": bool(table8_long.groupby("iso3")["scenario"].nunique().eq(len(SCENARIO_ORDER)).all()),
        "scoring_criterion_weights_sum_one": bool(np.allclose(states[["scoring_RC", "scoring_EI", "scoring_OF"]].sum(axis=1), 1.0, atol=1e-12)),
        "pci_formula_reproduces": bool(np.allclose(table8_long["pci"], table8_long["weighted_mean"] * table8_long["cv_penalty_multiplier"], atol=1e-12)),
        "rpci_formula_reproduces": bool(np.allclose(table8_long["rpci"], table8_long["pci"] * table8_long["gini_penalty_multiplier"], atol=1e-12)),
        "fdi_not_a_governance_dimension": "fdi_index" not in GOVERNANCE_DIMENSIONS,
        "no_missing_or_infinite_numeric_outputs": bool(np.isfinite(table8_long.select_dtypes(include=[np.number]).to_numpy()).all()),
    }
    dimension_columns = [f"dimension_{name}" for name in GOVERNANCE_DIMENSIONS]
    checks["dimension_weights_sum_one"] = bool(np.allclose(states[dimension_columns].sum(axis=1), 1.0, atol=1e-12))
    checks["fdi_context_constant_within_country"] = bool(table8_long.groupby("iso3")["fdi_index_context"].nunique().eq(1).all())
    checks["all_normalised_inputs_in_unit_interval"] = bool(
        pci_input[[*GOVERNANCE_DIMENSIONS, "fdi_index"]].apply(lambda col: col.between(0, 1).all()).all()
    )
    failed = [name for name, passed in checks.items() if not passed]
    validation = {
        "status": "PASS" if not failed else "FAIL",
        "checks": checks,
        "failed_checks": failed,
        "negative_pci_rows": int((table8_long["pci"] < 0).sum()),
        "note": "Negative PCI is mathematically possible when weighted CV exceeds one.",
    }
    (out / "validation_report.json").write_text(json.dumps(validation, indent=2), encoding="utf-8")
    if failed:
        raise AssertionError(f"Version C validation failed: {failed}")

    snapshot_dir = out / "input_snapshots"
    snapshot_dir.mkdir()
    for path in input_paths.values():
        shutil.copy2(path, snapshot_dir / path.name)

    write_markdown(
        out / "README.md",
        """
# Version C evidence package

This package implements a five-WGI governance-only PCI/RPCI. EV remains part of project-level AIML-MRMS evaluation; it is not reassigned to a country-level proxy. RC, EI and OF are renormalised for governance scoring. FDI is excluded from PCI/RPCI and reported separately as a descriptive investment-flow indicator.

`table8_version_c_manuscript_matrix.csv` and `table9_version_c_manuscript_summary.csv` are the compact manuscript sources. Full calculation trails, projected weights, score sensitivity, ranking stability, recomputed SVM signals, validation checks, input snapshots and FDI descriptive associations are retained alongside them.

Reproduction command from the repository root:

`python audit/run_version_c_analysis.py --run-id <new-run-name>`
""",
    )

    code_paths = [
        ROOT / "audit" / "run_version_c_analysis.py",
        ROOT / "src" / "aiml_mrms" / "governance_pci.py",
        ROOT / "src" / "aiml_mrms" / "weighted_pci.py",
        ROOT / "src" / "aiml_mrms" / "mcdm.py",
        ROOT / "src" / "aiml_mrms" / "svm_validation.py",
    ]
    output_hashes = {
        str(path.relative_to(out)).replace("\\", "/"): sha256_file(path)
        for path in sorted(out.rglob("*"))
        if path.is_file()
    }
    summary = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "method": "Version C governance-only PCI/RPCI",
        "countries": len(pci_input),
        "governance_dimensions": GOVERNANCE_DIMENSIONS,
        "architectural_criteria": CRITERIA,
        "pci_scoring_criteria": ["RC", "EI", "OF"],
        "fdi_role": "Separate descriptive investment-flow indicator; excluded from PCI/RPCI.",
        "alpha_values": ALPHAS,
        "fixed_states": STATES,
        "input_sha256": {name: sha256_file(path) for name, path in input_paths.items()},
        "code_sha256": {str(path.relative_to(ROOT)).replace("\\", "/"): sha256_file(path) for path in code_paths},
        "output_sha256": output_hashes,
        "software": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": package_version("numpy"),
            "pandas": package_version("pandas"),
            "scikit_learn": package_version("scikit-learn"),
        },
        "git": git_context(),
        "validation": validation,
        "interpretation_limits": [
            "FDI association is descriptive and non-causal.",
            "The analysis does not establish closed-loop feedback or convergence.",
            "The four scenarios are criterion-weight states, not independently executed architectures.",
        ],
    }
    (out / "analysis_manifest.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Version C analysis complete: {out}")


if __name__ == "__main__":
    main()
