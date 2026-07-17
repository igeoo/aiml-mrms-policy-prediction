"""Leakage-free external validation for the Version C novelty extension."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.decomposition import PCA
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GridSearchCV, GroupKFold, LeaveOneGroupOut
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


DIMENSIONS = [
    "control_of_corruption",
    "government_effectiveness",
    "political_stability",
    "regulatory_quality",
    "rule_of_law",
    "voice_accountability",
]
GOVERNANCE = [f"{name}__score_0_1" for name in DIMENSIONS]
CONTROLS = ["mineral_rents_pct_gdp", "log_gdp_per_capita", "log_gdp"]
TARGET = "asinh_fdi_pct_gdp_t_plus_1"
ALPHAS = np.logspace(-4, 4, 33)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("panel", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--bootstrap-replicates", type=int, default=5000)
    return parser.parse_args()


def ridge_search(X: pd.DataFrame, y: pd.Series, groups: pd.Series) -> GridSearchCV:
    model = Pipeline([("scale", StandardScaler()), ("ridge", Ridge())])
    inner = GroupKFold(n_splits=min(5, groups.nunique()))
    search = GridSearchCV(
        model,
        {"ridge__alpha": ALPHAS},
        scoring="neg_mean_absolute_error",
        cv=inner,
        n_jobs=1,
    )
    search.fit(X, y, groups=groups)
    return search


def score_predictions(frame: pd.DataFrame, label: str, validation: str) -> dict:
    observed = frame["observed_asinh"].to_numpy()
    predicted = frame["predicted_asinh"].to_numpy()
    observed_raw = np.sinh(observed)
    predicted_raw = np.sinh(predicted)
    rho = spearmanr(observed, predicted).statistic
    return {
        "model": label,
        "validation": validation,
        "n": len(frame),
        "r2_asinh": r2_score(observed, predicted),
        "mae_asinh": mean_absolute_error(observed, predicted),
        "rmse_asinh": mean_squared_error(observed, predicted) ** 0.5,
        "spearman": float(rho),
        "mae_fdi_pct_gdp": mean_absolute_error(observed_raw, predicted_raw),
    }


def logo_predictions(data: pd.DataFrame, features: list[str], label: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    predictions = []
    coefficients = []
    logo = LeaveOneGroupOut()
    X = data[features]
    y = data[TARGET]
    groups = data["iso3"]
    for train, test in logo.split(X, y, groups):
        search = ridge_search(X.iloc[train], y.iloc[train], groups.iloc[train])
        fitted = search.best_estimator_
        held_out = groups.iloc[test].iloc[0]
        pred = fitted.predict(X.iloc[test])
        for row_index, observed, predicted in zip(data.index[test], y.iloc[test], pred):
            predictions.append(
                {
                    "row_index": row_index,
                    "iso3": data.loc[row_index, "iso3"],
                    "year": int(data.loc[row_index, "year"]),
                    "model": label,
                    "observed_asinh": observed,
                    "predicted_asinh": predicted,
                    "selected_alpha": search.best_params_["ridge__alpha"],
                }
            )
        for feature, coefficient in zip(features, fitted.named_steps["ridge"].coef_):
            coefficients.append(
                {
                    "held_out_country": held_out,
                    "model": label,
                    "feature": feature,
                    "standardised_coefficient": coefficient,
                    "selected_alpha": search.best_params_["ridge__alpha"],
                }
            )
    return pd.DataFrame(predictions), pd.DataFrame(coefficients)


def temporal_predictions(data: pd.DataFrame, features: list[str], label: str) -> pd.DataFrame:
    train = data[data["year"] <= 2018]
    test = data[data["year"].between(2019, 2023)]
    search = ridge_search(train[features], train[TARGET], train["iso3"])
    predicted = search.best_estimator_.predict(test[features])
    return pd.DataFrame(
        {
            "row_index": test.index,
            "iso3": test["iso3"].to_numpy(),
            "year": test["year"].astype(int).to_numpy(),
            "model": label,
            "observed_asinh": test[TARGET].to_numpy(),
            "predicted_asinh": predicted,
            "selected_alpha": search.best_params_["ridge__alpha"],
        }
    )


def cronbach_alpha(values: np.ndarray) -> float:
    item_variances = values.var(axis=0, ddof=1).sum()
    total_variance = values.sum(axis=1).var(ddof=1)
    k = values.shape[1]
    return float(k / (k - 1) * (1 - item_variances / total_variance))


def bootstrap_increment(predictions: pd.DataFrame, replicates: int) -> dict:
    wide = predictions.pivot(index=["iso3", "year", "observed_asinh"], columns="model", values="predicted_asinh").reset_index()
    wide["controls_abs_error"] = (wide["observed_asinh"] - wide["controls"]).abs()
    wide["combined_abs_error"] = (wide["observed_asinh"] - wide["governance_plus_controls"]).abs()
    country_delta = wide.groupby("iso3").apply(
        lambda group: group["controls_abs_error"].mean() - group["combined_abs_error"].mean(),
        include_groups=False,
    )
    rng = np.random.default_rng(42)
    draws = np.array([rng.choice(country_delta.to_numpy(), size=len(country_delta), replace=True).mean() for _ in range(replicates)])
    return {
        "quantity": "MAE(controls) - MAE(governance_plus_controls), equal country weighting",
        "estimate": float(country_delta.mean()),
        "ci95_lower": float(np.quantile(draws, 0.025)),
        "ci95_upper": float(np.quantile(draws, 0.975)),
        "bootstrap_probability_improvement": float((draws > 0).mean()),
        "replicates": replicates,
    }


def main() -> None:
    args = parse_args()
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=False)
    panel = pd.read_csv(args.panel)
    data = panel[panel["eligible_next_year_fdi_model"]].copy().reset_index(drop=True)

    specifications = {
        "controls": CONTROLS,
        "governance_only": GOVERNANCE,
        "governance_plus_controls": GOVERNANCE + CONTROLS,
    }
    logo_parts, temporal_parts, coefficient_parts = [], [], []
    for label, features in specifications.items():
        predictions, coefficients = logo_predictions(data, features, label)
        logo_parts.append(predictions)
        coefficient_parts.append(coefficients)
        temporal_parts.append(temporal_predictions(data, features, label))
    logo = pd.concat(logo_parts, ignore_index=True)
    temporal = pd.concat(temporal_parts, ignore_index=True)
    coefficients = pd.concat(coefficient_parts, ignore_index=True)

    metrics = []
    for validation, predictions in [("leave_one_country_out", logo), ("temporal_2019_2023", temporal)]:
        for label, group in predictions.groupby("model"):
            metrics.append(score_predictions(group, label, validation))
    metrics = pd.DataFrame(metrics)

    governance_coefficients = coefficients[
        (coefficients["model"] == "governance_plus_controls") & coefficients["feature"].isin(GOVERNANCE)
    ].copy()
    coefficient_summary = governance_coefficients.groupby("feature")["standardised_coefficient"].agg(
        mean_coefficient="mean",
        sd_coefficient="std",
        median_coefficient="median",
        positive_fraction=lambda values: float((values > 0).mean()),
        mean_absolute=lambda values: float(values.abs().mean()),
    ).reset_index()
    coefficient_summary["predictive_weight_abs"] = coefficient_summary["mean_absolute"] / coefficient_summary["mean_absolute"].sum()

    governance_values = panel[GOVERNANCE].dropna().to_numpy()
    standardised = StandardScaler().fit_transform(governance_values)
    pca = PCA().fit(standardised)
    correlation = pd.DataFrame(governance_values, columns=DIMENSIONS).corr()
    vif = pd.Series(np.diag(np.linalg.pinv(correlation.to_numpy())), index=DIMENSIONS, name="vif")
    construct = {
        "cronbach_alpha_pooled": cronbach_alpha(governance_values),
        "pca_pc1_explained_variance": float(pca.explained_variance_ratio_[0]),
        "pca_pc2_cumulative_variance": float(pca.explained_variance_ratio_[:2].sum()),
        "maximum_vif": float(vif.max()),
        "interpretation": "High internal consistency or PC1 dominance indicates shared governance signal, not proof of unidimensionality.",
    }
    increment = bootstrap_increment(logo, args.bootstrap_replicates)

    logo.to_csv(out / "logo_predictions.csv", index=False)
    temporal.to_csv(out / "temporal_holdout_predictions.csv", index=False)
    metrics.to_csv(out / "external_validation_metrics.csv", index=False)
    coefficients.to_csv(out / "logo_standardised_coefficients.csv", index=False)
    coefficient_summary.to_csv(out / "governance_predictive_weight_stability.csv", index=False)
    correlation.to_csv(out / "governance_dimension_correlation.csv")
    vif.reset_index().rename(columns={"index": "dimension"}).to_csv(out / "governance_dimension_vif.csv", index=False)
    (out / "construct_validity.json").write_text(json.dumps(construct, indent=2), encoding="utf-8")
    (out / "cluster_bootstrap_increment.json").write_text(json.dumps(increment, indent=2), encoding="utf-8")

    checks = {
        "eligible_rows": len(data) == 319,
        "six_governance_dimensions": len(GOVERNANCE) == 6,
        "logo_predictions_complete": len(logo) == len(data) * len(specifications),
        "each_country_held_out": logo["iso3"].nunique() == 16,
        "temporal_test_years": set(temporal["year"].unique()).issubset(set(range(2019, 2024))),
        "predictive_weights_sum_one": bool(np.isclose(coefficient_summary["predictive_weight_abs"].sum(), 1.0)),
    }
    failed = [name for name, passed in checks.items() if not passed]
    report = {
        "status": "PASS" if not failed else "FAIL",
        "checks": checks,
        "failed": failed,
        "target": "asinh of FDI inflow (% GDP) at t+1",
        "models": specifications,
        "validation": ["nested leave-one-country-out", "2019-2023 temporal holdout trained through 2018"],
        "causal_claim": "None",
    }
    (out / "modeling_manifest.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    if failed:
        raise AssertionError(f"Modeling validation failed: {failed}")
    print(f"Novelty modeling complete: {out}")


if __name__ == "__main__":
    main()
