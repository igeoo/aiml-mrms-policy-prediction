"""Version C governance-only PCI/RPCI scoring.

This module deliberately separates three analytical roles:

* Economic Viability (EV) remains part of the four-criterion AIML-MRMS
  architecture and project-level AHP/TOPSIS evaluation.
* Country-level PCI/RPCI measures governance coherence using five WGI
  dimensions and the RC/EI/OF projection of each criterion-weight state.
* Normalised FDI is excluded from PCI/RPCI and reported separately as an
  observed investment-flow indicator.

No FDI-to-EV proxy is used in the governance score.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .weighted_pci import build_configuration_weights, weighted_gini, weighted_pci, weighted_rpci


GOVERNANCE_DIMENSIONS = [
    "regulatory_quality",
    "control_of_corruption",
    "rule_of_law",
    "government_effectiveness",
    "political_stability",
]


def governance_scoring_criterion_weights(criterion_weights: dict) -> dict:
    """Project a four-criterion state onto RC/EI/OF and renormalise.

    EV is not reassigned.  Its project-level role is preserved outside the
    country-level governance score.
    """

    required = {"EV", "RC", "EI", "OF"}
    missing = required.difference(criterion_weights)
    if missing:
        raise KeyError(f"Missing criterion weights: {sorted(missing)}")
    numeric = {key: float(criterion_weights[key]) for key in required}
    if not all(np.isfinite(value) for value in numeric.values()):
        raise ValueError("Criterion weights must be finite")
    if any(value < 0 for value in numeric.values()):
        raise ValueError("Criterion weights must be non-negative")
    governance_total = float(sum(numeric[key] for key in ("RC", "EI", "OF")))
    if governance_total <= 0:
        raise ValueError("RC + EI + OF must be positive for governance-only scoring")
    return {key: numeric[key] / governance_total for key in ("RC", "EI", "OF")}


def governance_dimension_weights(criterion_weights: dict) -> np.ndarray:
    """Return five dimension weights aligned with GOVERNANCE_DIMENSIONS."""

    projected = governance_scoring_criterion_weights(criterion_weights)
    weights = np.array(
        [
            projected["RC"] / 2,
            projected["EI"],
            projected["RC"] / 2,
            projected["OF"] / 2,
            projected["OF"] / 2,
        ],
        dtype=float,
    )
    if not np.isclose(weights.sum(), 1.0, atol=1e-12):
        raise AssertionError("Governance dimension weights must sum to one")
    return weights


def governance_metric_components(values, weights) -> dict:
    """Return the complete weighted-PCI/RPCI calculation trail."""

    x = np.asarray(values, dtype=float)
    v = np.asarray(weights, dtype=float)
    if x.shape != (len(GOVERNANCE_DIMENSIONS),):
        raise ValueError(f"Expected {len(GOVERNANCE_DIMENSIONS)} governance values")
    if v.shape != x.shape:
        raise ValueError("Governance values and weights must have the same shape")
    if not np.isfinite(x).all() or not np.isfinite(v).all():
        raise ValueError("Governance values and weights must be finite")
    if (x < 0).any():
        raise ValueError("Governance values must be non-negative")
    if (v < 0).any() or float(v.sum()) <= 0:
        raise ValueError("Governance weights must be non-negative and sum to a positive value")
    v = v / v.sum()
    mean = float(np.sum(v * x))
    variance = float(np.sum(v * (x - mean) ** 2))
    standard_deviation = float(np.sqrt(variance))
    coefficient_of_variation = standard_deviation / mean if mean > 0 else 0.0
    gini = weighted_gini(x, v)
    pci_value = weighted_pci(x, v)
    rpci_value = weighted_rpci(x, v)
    return {
        "weighted_mean": mean,
        "weighted_sd": standard_deviation,
        "weighted_cv": coefficient_of_variation,
        "cv_penalty_multiplier": 1 - coefficient_of_variation,
        "weighted_gini": gini,
        "gini_penalty_multiplier": 1 - gini,
        "pci": pci_value,
        "rpci": rpci_value,
    }


def compute_governance_pci_table(
    pci_input_df: pd.DataFrame,
    weight_evolution_df: pd.DataFrame,
    ai_signal: dict,
) -> pd.DataFrame:
    """Compute Version C scores and diagnostics for all weighting scenarios."""

    required_columns = {"iso3", *GOVERNANCE_DIMENSIONS}
    missing = required_columns.difference(pci_input_df.columns)
    if missing:
        raise KeyError(f"Missing PCI input columns: {sorted(missing)}")
    if pci_input_df["iso3"].isna().any() or pci_input_df["iso3"].duplicated().any():
        raise ValueError("ISO3 identifiers must be present and unique")
    numeric_columns = [*GOVERNANCE_DIMENSIONS]
    if "fdi_index" in pci_input_df.columns:
        numeric_columns.append("fdi_index")
    numeric = pci_input_df[numeric_columns].apply(pd.to_numeric, errors="coerce")
    if not np.isfinite(numeric.to_numpy(dtype=float)).all():
        raise ValueError("PCI inputs must be finite numeric values")
    if ((numeric < 0) | (numeric > 1)).any().any():
        raise ValueError("Normalised governance and FDI inputs must lie in [0, 1]")

    configurations = build_configuration_weights(weight_evolution_df, ai_signal)
    uniform = np.ones(len(GOVERNANCE_DIMENSIONS), dtype=float) / len(GOVERNANCE_DIMENSIONS)
    rows = []
    for _, country in pci_input_df.iterrows():
        values = country[GOVERNANCE_DIMENSIONS].to_numpy(dtype=float)
        reference = governance_metric_components(values, uniform)
        for scenario, full_weights in configurations.items():
            projected = governance_scoring_criterion_weights(full_weights)
            dimension_weights = governance_dimension_weights(full_weights)
            metrics = governance_metric_components(values, dimension_weights)
            rows.append(
                {
                    "iso3": country["iso3"],
                    "scenario": scenario,
                    "fdi_index_context": float(country["fdi_index"]) if "fdi_index" in country.index else np.nan,
                    **{f"full_weight_{key}": float(full_weights[key]) for key in ("EV", "RC", "EI", "OF")},
                    **{f"scoring_weight_{key}": projected[key] for key in ("RC", "EI", "OF")},
                    **{f"dimension_weight_{name}": value for name, value in zip(GOVERNANCE_DIMENSIONS, dimension_weights)},
                    **metrics,
                    "pci_uniform_governance_reference": reference["pci"],
                    "rpci_uniform_governance_reference": reference["rpci"],
                    "delta_pci_from_uniform_governance": metrics["pci"] - reference["pci"],
                    "delta_rpci_from_uniform_governance": metrics["rpci"] - reference["rpci"],
                }
            )
    return pd.DataFrame(rows)
