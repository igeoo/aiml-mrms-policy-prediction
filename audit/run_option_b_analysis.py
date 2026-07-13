"""Generate a non-invasive Option B evidence package for Tables 8 and 9.

The package is deliberately written below ``audit_artifacts/``.  It does not
overwrite legacy or working results, and it does not make architecture,
feedback-loop, or convergence claims.  It documents a *criterion-weighting
scenario* analysis based on the current weighted PCI prototype.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from aiml_mrms.data_utils import load_feature_matrix
from aiml_mrms.mcdm import weight_evolution
from aiml_mrms.svm_validation import linear_svc_feature_weights
from aiml_mrms.weighted_pci import (
    PCI_DIMENSIONS,
    build_configuration_weights,
    criterion_weights_to_dimension_weights,
    weighted_gini,
    weighted_pci,
    weighted_rpci,
)


CRITERIA = ["EV", "RC", "EI", "OF"]
BASE_WEIGHTS = [0.350, 0.300, 0.200, 0.150]
ALPHAS = [0.25, 0.50, 0.65, 0.75]
CYCLES = [1, 2, 3, 4, 5]


def write_markdown(path: Path, text: str) -> None:
    path.write_text(text.strip() + "\n", encoding="utf-8")


def rank_desc(values: pd.Series) -> pd.Series:
    return values.rank(ascending=False, method="average")


def diagnostic_row(iso3: str, scenario: str, x: np.ndarray, criterion_weights: dict) -> dict:
    v = criterion_weights_to_dimension_weights(criterion_weights)
    mean = float(np.sum(v * x))
    variance = float(np.sum(v * (x - mean) ** 2))
    cv = float(np.sqrt(variance) / mean) if mean > 0 else 0.0
    gini = weighted_gini(x, v)
    pci_value = weighted_pci(x, v)
    rpci_value = weighted_rpci(x, v)
    return {
        "iso3": iso3,
        "scenario": scenario,
        **{f"criterion_weight_{key}": criterion_weights[key] for key in CRITERIA},
        **{f"dimension_weight_{name}": value for name, value in zip(PCI_DIMENSIONS, v)},
        "weighted_mean": mean,
        "weighted_sd": float(np.sqrt(variance)),
        "weighted_cv": cv,
        "cv_penalty_multiplier": 1 - cv,
        "weighted_gini": gini,
        "gini_penalty_multiplier": 1 - gini,
        "pci_weighted": pci_value,
        "rpci_weighted": rpci_value,
    }


def main() -> None:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = ROOT / "audit_artifacts" / f"{stamp}_option_b"
    out.mkdir(parents=True, exist_ok=False)

    pci_input = pd.read_csv(ROOT / "data" / "processed" / "pci_input_vectors.csv")
    metrics = pd.read_csv(ROOT / "results" / "tables" / "table5_svm_loo_metrics.csv")
    modal_c = float(metrics.loc[0, "modal_C"])
    _, X, y = load_feature_matrix()
    _, criterion_signal_df = linear_svc_feature_weights(X, y, C=modal_c)
    ai_signal = criterion_signal_df.set_index("criterion")["svm_signal"].to_dict()
    signal_array = [ai_signal[c] for c in CRITERIA]

    # Main scenario analysis: exactly the four explicitly defined weight sources.
    evolution = weight_evolution(BASE_WEIGHTS, signal_array, alpha=0.65, cycles=3)
    scenarios = build_configuration_weights(evolution, ai_signal)
    # This is the direct implementation of the manuscript's original
    # unweighted equations and is retained as a reference, not described as a
    # fifth architecture or weighting configuration.
    uniform_reference = {"original_unweighted_reference": {name: 1.0 for name in CRITERIA}}
    diagnostics = []
    for _, row in pci_input.iterrows():
        x = row[PCI_DIMENSIONS].to_numpy(dtype=float)
        for scenario, weights in {**uniform_reference, **scenarios}.items():
            diagnostics.append(diagnostic_row(row["iso3"], scenario, x, weights))
    diagnostic_df = pd.DataFrame(diagnostics)

    original_reference = diagnostic_df[diagnostic_df["scenario"] == "original_unweighted_reference"][
        ["iso3", "pci_weighted", "rpci_weighted"]
    ].rename(columns={"pci_weighted": "pci_original_unweighted", "rpci_weighted": "rpci_original_unweighted"})
    baseline = diagnostic_df[diagnostic_df["scenario"] == "standalone_mcdm"][
        ["iso3", "pci_weighted", "rpci_weighted"]
    ].rename(columns={"pci_weighted": "pci_base_ahp", "rpci_weighted": "rpci_base_ahp"})
    table8 = diagnostic_df.merge(original_reference, on="iso3", validate="many_to_one").merge(baseline, on="iso3", validate="many_to_one")
    table8["comparison_role"] = np.where(table8["scenario"] == "original_unweighted_reference", "original manuscript reference", "criterion-weighting scenario")
    table8["delta_pci_from_original_unweighted"] = table8["pci_weighted"] - table8["pci_original_unweighted"]
    table8["delta_rpci_from_original_unweighted"] = table8["rpci_weighted"] - table8["rpci_original_unweighted"]
    table8["delta_pci_from_base_ahp"] = table8["pci_weighted"] - table8["pci_base_ahp"]
    table8["delta_rpci_from_base_ahp"] = table8["rpci_weighted"] - table8["rpci_base_ahp"]
    table8["pci_rank_within_scenario"] = table8.groupby("scenario")["pci_weighted"].rank(ascending=False, method="min").astype(int)
    table8["rpci_rank_within_scenario"] = table8.groupby("scenario")["rpci_weighted"].rank(ascending=False, method="min").astype(int)
    table8.to_csv(out / "candidate_table8_weighted_scenario_results.csv", index=False)
    diagnostic_df.to_csv(out / "metric_decomposition_by_country_and_scenario.csv", index=False)
    scenario_order = ["original_unweighted_reference", "standalone_mcdm", "standalone_ai", "static_ai_mcdm", "aiml_mrms_full_adaptive"]
    manuscript_table8 = table8.pivot(index="iso3", columns="scenario", values=["pci_weighted", "rpci_weighted"])
    manuscript_table8 = manuscript_table8.reindex(columns=pd.MultiIndex.from_product([["pci_weighted", "rpci_weighted"], scenario_order]))
    manuscript_table8.columns = [
        f"{'PCI' if metric == 'pci_weighted' else 'RPCI'}_{scenario}"
        for metric, scenario in manuscript_table8.columns
    ]
    manuscript_table8.reset_index().to_csv(out / "table8_manuscript_matrix.csv", index=False)

    # Sensitivity: alpha controls persistence of the prior; cycle is a fixed
    # iteration count.  These are not treated as convergence experiments.
    weight_rows = []
    sensitivity_rows = []
    for alpha in ALPHAS:
        evolution_alpha = weight_evolution(BASE_WEIGHTS, signal_array, alpha=alpha, cycles=max(CYCLES))
        for cycle in CYCLES:
            criterion_weights = evolution_alpha.loc[evolution_alpha["cycle"] == cycle, CRITERIA].iloc[0].to_dict()
            weight_rows.append({"alpha": alpha, "cycle": cycle, **criterion_weights})
            for _, row in pci_input.iterrows():
                details = diagnostic_row(row["iso3"], "adaptive_weight_state", row[PCI_DIMENSIONS].to_numpy(dtype=float), criterion_weights)
                sensitivity_rows.append({"alpha": alpha, "cycle": cycle, **details})
    weight_states = pd.DataFrame(weight_rows)
    sensitivity = pd.DataFrame(sensitivity_rows)
    baseline_alpha = sensitivity[sensitivity["cycle"] == 1][["alpha", "iso3", "pci_weighted", "rpci_weighted"]].rename(
        columns={"pci_weighted": "pci_cycle1", "rpci_weighted": "rpci_cycle1"}
    )
    sensitivity = sensitivity.merge(baseline_alpha, on=["alpha", "iso3"], validate="many_to_one")
    sensitivity["delta_pci_from_cycle1"] = sensitivity["pci_weighted"] - sensitivity["pci_cycle1"]
    sensitivity["delta_rpci_from_cycle1"] = sensitivity["rpci_weighted"] - sensitivity["rpci_cycle1"]
    weight_states.to_csv(out / "candidate_table9a_weight_states.csv", index=False)
    sensitivity.to_csv(out / "candidate_table9b_pci_rpci_sensitivity.csv", index=False)

    rank_rows = []
    reference = table8[table8["scenario"] == "standalone_mcdm"].set_index("iso3")
    for (alpha, cycle), group in sensitivity.groupby(["alpha", "cycle"], sort=True):
        indexed = group.set_index("iso3").loc[reference.index]
        rank_rows.append({
            "alpha": alpha,
            "cycle": cycle,
            "pci_spearman_vs_cycle1": rank_desc(reference["pci_weighted"]).corr(rank_desc(indexed["pci_weighted"]), method="pearson"),
            "rpci_spearman_vs_cycle1": rank_desc(reference["rpci_weighted"]).corr(rank_desc(indexed["rpci_weighted"]), method="pearson"),
            "mean_abs_delta_pci": float(np.mean(np.abs(indexed["delta_pci_from_cycle1"]))),
            "mean_abs_delta_rpci": float(np.mean(np.abs(indexed["delta_rpci_from_cycle1"]))),
        })
    ranking_stability = pd.DataFrame(rank_rows)
    ranking_stability.to_csv(out / "candidate_table9c_ranking_stability.csv", index=False)
    manuscript_table9 = weight_states.merge(ranking_stability, on=["alpha", "cycle"], validate="one_to_one")
    manuscript_table9.to_csv(out / "table9_manuscript_sensitivity_summary.csv", index=False)

    pd.DataFrame([
        {"scenario": "standalone_mcdm", "implemented_weight_source": "base AHP criterion weights", "adaptive_updates": 0, "separate_ai_decision_pipeline": "No", "feedback_from_topsis_or_optimisation": "No", "convergence_test": "No"},
        {"scenario": "standalone_ai", "implemented_weight_source": "aggregate SVM-derived criterion signal", "adaptive_updates": 0, "separate_ai_decision_pipeline": "No", "feedback_from_topsis_or_optimisation": "No", "convergence_test": "No"},
        {"scenario": "static_ai_mcdm", "implemented_weight_source": "one convex blend of AHP prior and SVM signal", "adaptive_updates": 1, "separate_ai_decision_pipeline": "No", "feedback_from_topsis_or_optimisation": "No", "convergence_test": "No"},
        {"scenario": "aiml_mrms_full_adaptive", "implemented_weight_source": "second convex blend of the same AHP prior and SVM signal", "adaptive_updates": 2, "separate_ai_decision_pipeline": "No", "feedback_from_topsis_or_optimisation": "No", "convergence_test": "No"},
    ]).to_csv(out / "configuration_execution_manifest.csv", index=False)

    summary = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "Non-invasive Option B evidence package; no production results were overwritten.",
        "countries": int(pci_input.shape[0]),
        "main_scenarios": list(scenarios),
        "alpha_values": ALPHAS,
        "fixed_iteration_counts": CYCLES,
        "interpretation": [
            "The outputs quantify sensitivity of PCI/RPCI to alternative criterion-weighting scenarios.",
            "They do not compare four independently executed decision architectures.",
            "They do not establish a feedback loop or convergence because no TOPSIS, investment, or country outcome is fed back to the weights and no stopping criterion is implemented.",
            "Metric-decomposition columns permit the contribution of the weighted mean, CV penalty, and Gini penalty to be examined rather than assumed.",
        ],
    }
    (out / "analysis_manifest.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_markdown(out / "README.md", """
# Option B evidence package

These candidate tables support a revised manuscript claim: the proposed framework provides an interpretable, reproducible analysis of how an expert AHP prior and an aggregate SVM-derived signal alter criterion weights, PCI/RPCI values, and country rankings.

They do **not** support a claim that four independently executed architectures were benchmarked, that the second blend is a feedback loop, that the process converged, or that adaptive weighting uniformly improves PCI/RPCI.

Use `table8_manuscript_matrix.csv` as the compact, manuscript-ready Table 8 layout. Its `original_unweighted_reference` columns are the original manuscript equation, not a fifth architecture. Use `table9_manuscript_sensitivity_summary.csv` as the compact, manuscript-ready Table 9 layout. The candidate Table 9 files retain the full score sensitivity and ranking-stability audit trail. The metric-decomposition file is the audit trail needed to explain individual score movements.
""")
    write_markdown(out / "manuscript_revision_blueprint.md", """
# Option B manuscript-revision blueprint

## Replacement contribution statement

This study develops and evaluates an interpretable governance-aware decision-support framework that combines an expert AHP prior with an aggregate SVM-derived criterion signal. The empirical analysis quantifies how alternative, explicitly defined criterion-weighting scenarios affect PCI/RPCI values and country rankings, and reports robustness to the blending parameter and fixed update count.

## Methodology changes required before submission

1. Add the weighted PCI/RPCI equations, define the dimension weights, and state the criterion-to-dimension mapping (including the FDI-to-EV proxy).
2. State that the original unweighted PCI/RPCI is retained as a reference case and that uniform dimension weights reproduce it exactly.
3. Define each scenario by its actual weight source. Describe cycles as fixed weight states (0, 1, or 2 updates), not as a feedback loop or convergence result.
4. State the alpha grid, iteration-count grid, data inputs, model-selection value, and ranking-stability statistic in advance of the results.
5. Explain the scope: the SVM signal is aggregate; no country-specific model output, TOPSIS output, investment allocation, or observed outcome is returned to the weight update.

## Results and claims to remove or replace

Remove claims that the full AIML-MRMS configuration universally outperforms alternatives, that Table 8 proves a feedback loop, that the process converges, or that the scenarios are independently executed architectures.

Replace them with evidence-led wording: score movements are decomposed into changes in weighted mean, weighted coefficient-of-variation penalty, and weighted Gini penalty; sensitivity results show whether rankings remain stable under stated parameter choices. Report both improvements and reductions without treating either direction as automatic proof of method quality.

## Candidate table titles

* Table 8. PCI/RPCI under alternative expert- and SVM-informed criterion-weighting scenarios, with the original unweighted reference.
* Table 9a. Criterion-weight states across the alpha and fixed-iteration sensitivity grid.
* Table 9b. PCI/RPCI sensitivity to alpha and fixed update count.
* Table 9c. Country-ranking stability relative to the base-AHP weight state.

## Novelty that is defensible

The novelty is the transparent integration and empirical stress-testing of (i) expert AHP weights, (ii) an aggregate SVM-derived criterion signal, and (iii) inequality-aware PCI/RPCI scoring. The contribution is strengthened by exposing when score/rank changes are robust and by publishing the full calculation trail. It is not a claim of a new feedback-controlled learning system unless that feedback mechanism is separately implemented and evaluated.
""")
    print(f"Option B analysis complete: {out}")


if __name__ == "__main__":
    main()
