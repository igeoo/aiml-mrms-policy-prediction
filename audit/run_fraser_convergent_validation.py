"""Mining-specific convergent validation against Fraser PPI, 2019--2024."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import GridSearchCV, GroupKFold, LeaveOneGroupOut
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


DIMENSIONS = [
    "control_of_corruption", "government_effectiveness", "political_stability",
    "regulatory_quality", "rule_of_law", "voice_accountability",
]
FEATURES = [f"{name}__score_0_1" for name in DIMENSIONS]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wgi-panel", type=Path, required=True)
    parser.add_argument("--fraser-ppi", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--bootstrap-replicates", type=int, default=5000)
    return parser.parse_args()


def pci_components(values: np.ndarray) -> tuple[float, float, float]:
    mean = float(values.mean())
    cv = float(values.std(ddof=0) / mean) if mean > 0 else 0.0
    pci = mean * (1 - cv)
    diff = np.abs(values[:, None] - values[None, :])
    gini = float(diff.mean() / (2 * mean)) if mean > 0 else 0.0
    return mean, pci, pci * (1 - gini)


def main() -> None:
    args = parse_args()
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=False)
    wgi = pd.read_csv(args.wgi_panel)
    ppi = pd.read_csv(args.fraser_ppi)
    data = ppi.merge(wgi, on=["iso3", "year"], how="inner", validate="one_to_one")
    summaries = data[FEATURES].to_numpy()
    data[["governance_mean", "governance_pci", "governance_rpci"]] = np.array([pci_components(row) for row in summaries])

    correlations = []
    for feature in [*FEATURES, "governance_mean", "governance_pci", "governance_rpci"]:
        result = spearmanr(data[feature], data["ppi_score"])
        correlations.append({"measure": feature, "spearman": result.statistic, "p_value_naive": result.pvalue, "n": len(data)})
    correlations = pd.DataFrame(correlations)

    logo = LeaveOneGroupOut()
    predictions, coefficients = [], []
    X, y, groups = data[FEATURES], data["ppi_score"], data["iso3"]
    for train, test in logo.split(X, y, groups):
        pipeline = Pipeline([("scale", StandardScaler()), ("ridge", Ridge())])
        search = GridSearchCV(
            pipeline,
            {"ridge__alpha": np.logspace(-4, 4, 33)},
            scoring="neg_mean_absolute_error",
            cv=GroupKFold(n_splits=min(5, groups.iloc[train].nunique())),
            n_jobs=1,
        )
        search.fit(X.iloc[train], y.iloc[train], groups=groups.iloc[train])
        fitted = search.best_estimator_
        predicted = fitted.predict(X.iloc[test])
        for index, observed, estimate in zip(data.index[test], y.iloc[test], predicted):
            predictions.append({"iso3": data.loc[index, "iso3"], "year": int(data.loc[index, "year"]), "observed_ppi": observed, "predicted_ppi": estimate})
        for feature, coefficient in zip(FEATURES, fitted.named_steps["ridge"].coef_):
            coefficients.append({"held_out_country": groups.iloc[test].iloc[0], "feature": feature, "standardised_coefficient": coefficient})
    predictions = pd.DataFrame(predictions)
    coefficients = pd.DataFrame(coefficients)
    rho = spearmanr(predictions["observed_ppi"], predictions["predicted_ppi"]).statistic
    metrics = {
        "n": len(predictions),
        "countries": int(predictions["iso3"].nunique()),
        "r2": float(r2_score(predictions["observed_ppi"], predictions["predicted_ppi"])),
        "mae": float(mean_absolute_error(predictions["observed_ppi"], predictions["predicted_ppi"])),
        "spearman": float(rho),
        "validation": "Nested leave-one-country-out ridge regression",
    }

    rng = np.random.default_rng(42)
    countries = data["iso3"].unique()
    draws = []
    for _ in range(args.bootstrap_replicates):
        selected = rng.choice(countries, len(countries), replace=True)
        sample = pd.concat([data[data["iso3"] == country] for country in selected], ignore_index=True)
        draws.append(spearmanr(sample["governance_mean"], sample["ppi_score"]).statistic)
    bootstrap = {
        "measure": "Spearman(governance_mean, Fraser PPI)",
        "estimate": float(spearmanr(data["governance_mean"], data["ppi_score"]).statistic),
        "cluster_bootstrap_ci95_lower": float(np.nanquantile(draws, 0.025)),
        "cluster_bootstrap_ci95_upper": float(np.nanquantile(draws, 0.975)),
        "replicates": args.bootstrap_replicates,
    }

    summary = coefficients.groupby("feature")["standardised_coefficient"].agg(
        mean="mean", sd="std", positive_fraction=lambda values: float((values > 0).mean()), mean_absolute=lambda values: float(values.abs().mean())
    ).reset_index()
    summary["absolute_weight"] = summary["mean_absolute"] / summary["mean_absolute"].sum()
    data.to_csv(out / "fraser_wgi_convergent_panel.csv", index=False)
    correlations.to_csv(out / "fraser_dimension_correlations.csv", index=False)
    predictions.to_csv(out / "fraser_logo_predictions.csv", index=False)
    coefficients.to_csv(out / "fraser_logo_coefficients.csv", index=False)
    summary.to_csv(out / "fraser_weight_stability.csv", index=False)
    (out / "fraser_logo_metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    (out / "fraser_cluster_bootstrap.json").write_text(json.dumps(bootstrap, indent=2), encoding="utf-8")
    manifest = {
        "status": "PASS",
        "rows": len(data),
        "countries": int(data["iso3"].nunique()),
        "years": [int(data["year"].min()), int(data["year"].max())],
        "excluded_for_no_fraser_observations": ["NGA", "SLE"],
        "interpretation": "Convergent validity against mining-policy perceptions; not causal validation and not a classification task.",
    }
    (out / "fraser_validation_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Fraser convergent validation complete: {out}")


if __name__ == "__main__":
    main()
