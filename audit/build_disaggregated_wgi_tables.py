"""Build disaggregated WGI reporting tables for the main manuscript.

Produces:
  - table8a: Wide 2024 table with all six WGI point scores, SEs, 90% CIs,
    plus PCI/RPCI and descriptive ranks.
  - table8b: Governance coherence diagnostics (PCI/RPCI with measurement
    uncertainty intervals from the locked baseline).
  - supplement_long: Long table with one row per country-dimension.

Uses only the locked WGI panel and robustness artifacts. Does not introduce
any new computation.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


DIMENSIONS = [
    "control_of_corruption", "government_effectiveness", "political_stability",
    "regulatory_quality", "rule_of_law", "voice_accountability",
]
DIMENSION_LABELS = {
    "control_of_corruption": "Control of Corruption",
    "government_effectiveness": "Government Effectiveness",
    "political_stability": "Political Stability",
    "regulatory_quality": "Regulatory Quality",
    "rule_of_law": "Rule of Law",
    "voice_accountability": "Voice and Accountability",
}
SCORES = [f"{name}__score_0_1" for name in DIMENSIONS]
STANDARD_ERRORS = [f"{name}__score_se_0_1" for name in DIMENSIONS]
CI_LOWER = [f"{name}__score_ci90_lower_0_1" for name in DIMENSIONS]
CI_UPPER = [f"{name}__score_ci90_upper_0_1" for name in DIMENSIONS]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build disaggregated WGI reporting tables."
    )
    parser.add_argument("--wgi-panel", type=Path, required=True)
    parser.add_argument("--robustness-dir", type=Path, required=True,
                        help="Locked robustness artifacts directory.")
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def pci_rpci(values: np.ndarray) -> tuple[float, float]:
    """Compute uniform-weighted PCI and RPCI for a single country."""
    mean = float(values.mean())
    if mean <= 0:
        return 0.0, 0.0
    cv = float(values.std(ddof=0) / mean)
    pci = mean * (1 - cv)
    n = len(values)
    diff = np.abs(values[:, None] - values[None, :])
    gini = float(diff.mean() / (2 * mean))
    rpci = pci * (1 - gini)
    return pci, rpci


def main() -> None:
    args = parse_args()
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)

    panel = pd.read_csv(args.wgi_panel)
    latest = panel[panel["year"] == 2024].sort_values("iso3").reset_index(drop=True)
    assert len(latest) == 16, f"Expected 16 countries, got {len(latest)}"

    # Load locked measurement uncertainty for uniform primary
    uncertainty = pd.read_csv(
        args.robustness_dir / "wgi_measurement_uncertainty_2024.csv"
    )
    uniform_uncertainty = uncertainty[
        uncertainty["scheme"] == "uniform_primary"
    ].set_index("iso3")

    # === Table 8A: Six-dimension profile with PCI/RPCI ===
    rows_8a = []
    for _, row in latest.iterrows():
        scores = row[SCORES].to_numpy(dtype=float)
        pci, rpci = pci_rpci(scores)
        entry = {
            "country": row["country"],
            "iso3": row["iso3"],
        }
        for dim in DIMENSIONS:
            label = DIMENSION_LABELS[dim]
            entry[f"{label}"] = row[f"{dim}__score_0_1"]
            entry[f"{label} SE"] = row[f"{dim}__score_se_0_1"]
            entry[f"{label} 90% CI Lower"] = row[f"{dim}__score_ci90_lower_0_1"]
            entry[f"{label} 90% CI Upper"] = row[f"{dim}__score_ci90_upper_0_1"]
        entry["governance_mean"] = float(scores.mean())
        entry["pci"] = pci
        entry["rpci"] = rpci
        rows_8a.append(entry)

    df_8a = pd.DataFrame(rows_8a)
    df_8a["pci_rank"] = df_8a["pci"].rank(ascending=False, method="min").astype(int)
    df_8a["rpci_rank"] = df_8a["rpci"].rank(ascending=False, method="min").astype(int)
    df_8a = df_8a.sort_values("pci_rank").reset_index(drop=True)
    df_8a.to_csv(out / "table8a_wgi_six_dimensions_2024.csv", index=False)

    # === Table 8B: Governance coherence diagnostics with uncertainty ===
    rows_8b = []
    for _, row in df_8a.iterrows():
        iso3 = row["iso3"]
        unc = uniform_uncertainty.loc[iso3]
        rows_8b.append({
            "rank": row["pci_rank"],
            "country": row["country"],
            "iso3": iso3,
            "governance_mean": row["governance_mean"],
            "pci": row["pci"],
            "pci_measurement_95_ci": f"{unc['pci_mc_lower95']:.4f}-{unc['pci_mc_upper95']:.4f}",
            "pci_rank_measurement_95_interval": f"{int(unc['pci_rank_lower95'])}-{int(unc['pci_rank_upper95'])}",
            "rpci": row["rpci"],
            "rpci_rank": row["rpci_rank"],
            "rpci_measurement_95_ci": f"{unc['rpci_mc_lower95']:.4f}-{unc['rpci_mc_upper95']:.4f}",
        })
    df_8b = pd.DataFrame(rows_8b)
    df_8b.to_csv(out / "table8b_governance_coherence_diagnostics_2024.csv", index=False)

    # === Supplement: Long format with one row per country-dimension ===
    long_rows = []
    for _, row in latest.iterrows():
        for dim in DIMENSIONS:
            long_rows.append({
                "country": row["country"],
                "iso3": row["iso3"],
                "dimension": DIMENSION_LABELS[dim],
                "dimension_code": dim,
                "score_0_1": row[f"{dim}__score_0_1"],
                "standard_error_0_1": row[f"{dim}__score_se_0_1"],
                "ci90_lower_0_1": row[f"{dim}__score_ci90_lower_0_1"],
                "ci90_upper_0_1": row[f"{dim}__score_ci90_upper_0_1"],
            })
    df_long = pd.DataFrame(long_rows)
    df_long = df_long.sort_values(["iso3", "dimension_code"]).reset_index(drop=True)
    df_long.to_csv(out / "supplement_wgi_dimension_intervals_2024_long.csv", index=False)

    # Validation checks
    assert len(df_8a) == 16, f"Table 8A: expected 16 rows, got {len(df_8a)}"
    assert len(df_8b) == 16, f"Table 8B: expected 16 rows, got {len(df_8b)}"
    assert len(df_long) == 96, f"Supplement: expected 96 rows (16x6), got {len(df_long)}"
    assert not df_8a.isna().any().any(), "Table 8A has missing values"
    assert not df_long.isna().any().any(), "Supplement has missing values"

    print(f"Disaggregated WGI tables written to {out}")
    print(f"  table8a_wgi_six_dimensions_2024.csv: {len(df_8a)} countries")
    print(f"  table8b_governance_coherence_diagnostics_2024.csv: {len(df_8b)} countries")
    print(f"  supplement_wgi_dimension_intervals_2024_long.csv: {len(df_long)} rows (16x6)")


if __name__ == "__main__":
    main()
