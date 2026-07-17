"""Six-dimension WGI composite robustness and uncertainty analysis."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


DIMENSIONS = [
    "control_of_corruption", "government_effectiveness", "political_stability",
    "regulatory_quality", "rule_of_law", "voice_accountability",
]
SCORES = [f"{name}__score_0_1" for name in DIMENSIONS]
STANDARD_ERRORS = [f"{name}__score_se_0_1" for name in DIMENSIONS]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wgi-panel", type=Path, required=True)
    parser.add_argument("--fraser-correlations", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--mc-draws", type=int, default=10000)
    parser.add_argument("--weight-draws", type=int, default=10000)
    return parser.parse_args()


def metric_batch(values: np.ndarray, weights: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Calculate weighted mean, PCI and RPCI for rows in values."""
    weights = np.asarray(weights, dtype=float)
    weights = weights / weights.sum()
    mean = values @ weights
    variance = ((values - mean[:, None]) ** 2 * weights).sum(axis=1)
    cv = np.divide(np.sqrt(variance), mean, out=np.zeros_like(mean), where=mean > 0)
    pci = mean * (1 - cv)
    differences = np.abs(values[:, :, None] - values[:, None, :])
    gini = np.einsum("nij,i,j->n", differences, weights, weights)
    gini = np.divide(gini, 2 * mean, out=np.zeros_like(mean), where=mean > 0)
    return mean, pci, pci * (1 - gini)


def metric_weight_draws(values: np.ndarray, weights: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Calculate PCI/RPCI for every weight draw and country."""
    mean = np.einsum("wd,cd->wc", weights, values)
    difference = values[None, :, :] - mean[:, :, None]
    variance = (weights[:, None, :] * difference**2).sum(axis=2)
    cv = np.divide(np.sqrt(variance), mean, out=np.zeros_like(mean), where=mean > 0)
    pci = mean * (1 - cv)
    pairwise = np.abs(values[:, :, None] - values[:, None, :])
    gini = np.einsum("wi,wj,cij->wc", weights, weights, pairwise)
    gini = np.divide(gini, 2 * mean, out=np.zeros_like(mean), where=mean > 0)
    return pci, pci * (1 - gini)


def descending_ranks(scores: np.ndarray) -> np.ndarray:
    return np.argsort(np.argsort(-scores, axis=1), axis=1) + 1


def entropy_weights(values: np.ndarray) -> np.ndarray:
    proportions = values / values.sum(axis=0, keepdims=True)
    entropy = -(np.where(proportions > 0, proportions * np.log(proportions), 0)).sum(axis=0) / np.log(len(values))
    divergence = 1 - entropy
    return divergence / divergence.sum()


def main() -> None:
    args = parse_args()
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=False)
    panel = pd.read_csv(args.wgi_panel)
    values_all = panel[SCORES].to_numpy(dtype=float)

    pca = PCA().fit(StandardScaler().fit_transform(values_all))
    pca_weights = np.abs(pca.components_[0])
    pca_weights /= pca_weights.sum()
    entropy = entropy_weights(values_all)
    correlations = pd.read_csv(args.fraser_correlations).set_index("measure")["spearman"]
    mining = np.array([max(float(correlations[f"{name}__score_0_1"]), 0) for name in DIMENSIONS])
    mining /= mining.sum()
    schemes = {
        "uniform_primary": np.ones(6) / 6,
        "pca_sensitivity": pca_weights,
        "entropy_sensitivity": entropy,
        "fraser_bivariate_sensitivity": mining,
    }

    weight_rows = []
    for scheme, weights in schemes.items():
        for dimension, weight in zip(DIMENSIONS, weights):
            weight_rows.append({"scheme": scheme, "dimension": dimension, "weight": weight, "role": "primary" if scheme == "uniform_primary" else "sensitivity"})
    pd.DataFrame(weight_rows).to_csv(out / "governance_weight_schemes.csv", index=False)

    score_rows = []
    for scheme, weights in schemes.items():
        mean, pci, rpci = metric_batch(values_all, weights)
        for index, row in panel.iterrows():
            score_rows.append({"country": row["country"], "iso3": row["iso3"], "year": int(row["year"]), "scheme": scheme, "weighted_mean": mean[index], "pci": pci[index], "rpci": rpci[index]})
    scores = pd.DataFrame(score_rows)
    scores["pci_rank"] = scores.groupby(["year", "scheme"])["pci"].rank(ascending=False, method="min").astype(int)
    scores["rpci_rank"] = scores.groupby(["year", "scheme"])["rpci"].rank(ascending=False, method="min").astype(int)
    scores.to_csv(out / "six_dimension_scores_2002_2024.csv", index=False)

    latest = panel[panel["year"] == 2024].sort_values("iso3").reset_index(drop=True)
    latest_scores = scores[scores["year"] == 2024].copy()
    latest_scores.to_csv(out / "candidate_table8_six_dimension_2024_long.csv", index=False)
    table8 = latest_scores.pivot(index=["country", "iso3"], columns="scheme", values=["pci", "rpci", "pci_rank", "rpci_rank"])
    table8.columns = [f"{metric}__{scheme}" for metric, scheme in table8.columns]
    table8.reset_index().to_csv(out / "candidate_table8_six_dimension_2024_matrix.csv", index=False)

    # WGI measurement uncertainty: independent normal approximation using the
    # published dimension standard errors, clipped to the official 0--1 scale.
    rng = np.random.default_rng(42)
    centres = latest[SCORES].to_numpy(dtype=float)
    standard_errors = latest[STANDARD_ERRORS].to_numpy(dtype=float)
    simulated = rng.normal(centres[None, :, :], standard_errors[None, :, :], size=(args.mc_draws, len(latest), 6))
    simulated = np.clip(simulated, 0, 1)
    uncertainty_rows = []
    rank_probability_rows = []
    for scheme, weights in schemes.items():
        flat = simulated.reshape(-1, 6)
        _, pci_flat, rpci_flat = metric_batch(flat, weights)
        pci_draws = pci_flat.reshape(args.mc_draws, len(latest))
        rpci_draws = rpci_flat.reshape(args.mc_draws, len(latest))
        pci_ranks = descending_ranks(pci_draws)
        rpci_ranks = descending_ranks(rpci_draws)
        for country_index, row in latest.iterrows():
            uncertainty_rows.append({
                "iso3": row["iso3"], "scheme": scheme,
                "pci_mc_mean": pci_draws[:, country_index].mean(),
                "pci_mc_lower95": np.quantile(pci_draws[:, country_index], 0.025),
                "pci_mc_upper95": np.quantile(pci_draws[:, country_index], 0.975),
                "rpci_mc_mean": rpci_draws[:, country_index].mean(),
                "rpci_mc_lower95": np.quantile(rpci_draws[:, country_index], 0.025),
                "rpci_mc_upper95": np.quantile(rpci_draws[:, country_index], 0.975),
                "pci_rank_median": np.median(pci_ranks[:, country_index]),
                "pci_rank_lower95": np.quantile(pci_ranks[:, country_index], 0.025),
                "pci_rank_upper95": np.quantile(pci_ranks[:, country_index], 0.975),
            })
            for rank in range(1, len(latest) + 1):
                rank_probability_rows.append({"iso3": row["iso3"], "scheme": scheme, "rank": rank, "pci_probability": (pci_ranks[:, country_index] == rank).mean(), "rpci_probability": (rpci_ranks[:, country_index] == rank).mean()})
    uncertainty = pd.DataFrame(uncertainty_rows)
    uncertainty.to_csv(out / "wgi_measurement_uncertainty_2024.csv", index=False)
    pd.DataFrame(rank_probability_rows).to_csv(out / "wgi_rank_probabilities_2024.csv", index=False)

    # Weight uncertainty around the uniform primary specification.
    weight_draws = rng.dirichlet(np.ones(6) * 10, size=args.weight_draws)
    pci_weight, rpci_weight = metric_weight_draws(centres, weight_draws)
    pci_ranks = descending_ranks(pci_weight)
    rpci_ranks = descending_ranks(rpci_weight)
    uniform_latest = latest_scores[latest_scores["scheme"] == "uniform_primary"].sort_values("iso3")
    uniform_pci_ranks = uniform_latest["pci_rank"].to_numpy()
    uniform_rpci_ranks = uniform_latest["rpci_rank"].to_numpy()
    pci_rho = np.array([spearmanr(uniform_pci_ranks, row).statistic for row in pci_ranks])
    rpci_rho = np.array([spearmanr(uniform_rpci_ranks, row).statistic for row in rpci_ranks])
    perturbation = {
        "weight_distribution": "Dirichlet(10,10,10,10,10,10)",
        "draws": args.weight_draws,
        "pci_rank_spearman_median": float(np.median(pci_rho)),
        "pci_rank_spearman_lower95": float(np.quantile(pci_rho, 0.025)),
        "rpci_rank_spearman_median": float(np.median(rpci_rho)),
        "rpci_rank_spearman_lower95": float(np.quantile(rpci_rho, 0.025)),
    }
    (out / "weight_perturbation_summary.json").write_text(json.dumps(perturbation, indent=2), encoding="utf-8")
    perturbation_country = pd.DataFrame({
        "iso3": latest["iso3"],
        "pci_rank_median": np.median(pci_ranks, axis=0),
        "pci_rank_lower95": np.quantile(pci_ranks, 0.025, axis=0),
        "pci_rank_upper95": np.quantile(pci_ranks, 0.975, axis=0),
        "rpci_rank_median": np.median(rpci_ranks, axis=0),
        "rpci_rank_lower95": np.quantile(rpci_ranks, 0.025, axis=0),
        "rpci_rank_upper95": np.quantile(rpci_ranks, 0.975, axis=0),
    })
    perturbation_country.to_csv(out / "weight_perturbation_country_ranks.csv", index=False)

    # Cross-scheme and temporal rank stability.
    scheme_rows = []
    primary = latest_scores[latest_scores["scheme"] == "uniform_primary"].set_index("iso3")
    for scheme in schemes:
        comparison = latest_scores[latest_scores["scheme"] == scheme].set_index("iso3").loc[primary.index]
        scheme_rows.append({"scheme": scheme, "pci_spearman_vs_uniform": spearmanr(primary["pci"], comparison["pci"]).statistic, "rpci_spearman_vs_uniform": spearmanr(primary["rpci"], comparison["rpci"]).statistic, "mean_abs_pci_difference": (primary["pci"] - comparison["pci"]).abs().mean(), "mean_abs_rpci_difference": (primary["rpci"] - comparison["rpci"]).abs().mean()})
    pd.DataFrame(scheme_rows).to_csv(out / "candidate_table9_weight_scheme_stability.csv", index=False)

    temporal_primary = scores[scores["scheme"] == "uniform_primary"]
    rank_2024 = temporal_primary[temporal_primary["year"] == 2024].set_index("iso3")
    temporal_rows = []
    for year, group in temporal_primary.groupby("year"):
        current = group.set_index("iso3").loc[rank_2024.index]
        temporal_rows.append({"year": int(year), "pci_spearman_vs_2024": spearmanr(current["pci"], rank_2024["pci"]).statistic, "rpci_spearman_vs_2024": spearmanr(current["rpci"], rank_2024["rpci"]).statistic, "mean_pci": current["pci"].mean(), "mean_rpci": current["rpci"].mean()})
    pd.DataFrame(temporal_rows).to_csv(out / "temporal_rank_stability_vs_2024.csv", index=False)

    checks = {
        "six_dimensions": bool(len(DIMENSIONS) == 6),
        "all_weight_schemes_sum_one": bool(all(np.isclose(weights.sum(), 1) for weights in schemes.values())),
        "official_scores_not_sample_rescaled": bool(values_all.min() > 0 and values_all.max() < 1),
        "complete_2024_cross_section": bool(len(latest) == 16),
        "no_negative_2024_pci": bool((latest_scores[["pci", "rpci"]].to_numpy() >= 0).all()),
        "uncertainty_rows_complete": bool(len(uncertainty) == len(latest) * len(schemes)),
    }
    failed = [name for name, passed in checks.items() if not passed]
    manifest = {
        "status": "PASS" if not failed else "FAIL",
        "checks": checks,
        "failed": failed,
        "primary_specification": "Uniform weighting across all six official WGI dimensions.",
        "sensitivity_specifications": [name for name in schemes if name != "uniform_primary"],
        "uncertainty_assumption": "Published WGI dimension standard errors sampled independently; this is an approximation because cross-dimension error covariance is unavailable.",
        "construct_boundary": "Country-governance weighting is independent of project-level EV/RC/EI/OF AHP weights.",
    }
    (out / "six_dimension_robustness_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    if failed:
        raise AssertionError(f"Six-dimension robustness checks failed: {failed}")
    print(f"Six-dimension robustness complete: {out}")


if __name__ == "__main__":
    main()
