"""Extract the authoritative six-dimension WGI panel for the study countries.

The script uses the revised 2025 WGI workbook, retains the official absolute
0--100 scores and their uncertainty intervals, and never re-normalises values
within the 16-country sample.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


COUNTRIES = [
    "BWA", "COD", "GHA", "GIN", "MLI", "MRT", "MAR", "MOZ",
    "NAM", "NGA", "SEN", "SLE", "ZAF", "TZA", "ZMB", "ZWE",
]
DIMENSIONS = {
    "va": "voice_accountability",
    "pv": "political_stability",
    "ge": "government_effectiveness",
    "rq": "regulatory_quality",
    "rl": "rule_of_law",
    "cc": "control_of_corruption",
}
SOURCE_URL = "https://www.worldbank.org/content/dam/sites/govindicators/doc/wgidataset_with_sourcedata-2025.xlsx"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("workbook", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--start-year", type=int, default=2002)
    parser.add_argument("--end-year", type=int, default=2024)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    workbook = args.workbook.resolve()
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=False)

    columns = {
        "Economy (name)": "country",
        "Economy (code)": "iso3",
        "Year": "year",
        "Number of sources": "number_sources",
        "Governance estimate (approx. -2.5 to +2.5)": "estimate",
        "Standard error (estimate)": "estimate_se",
        "Governance score (0-100)": "score_0_100",
        "Standard error (gov. score)": "score_se_0_100",
        "Lower threshold (90% conf. int. score)": "score_ci90_lower_0_100",
        "Upper threshold (90% conf. int. score)": "score_ci90_upper_0_100",
    }
    frames = []
    for sheet, dimension in DIMENSIONS.items():
        frame = pd.read_excel(workbook, sheet_name=sheet, usecols=list(columns), engine="openpyxl")
        frame = frame.rename(columns=columns)
        frame = frame[
            frame["iso3"].isin(COUNTRIES)
            & frame["year"].between(args.start_year, args.end_year)
        ].copy()
        frame["dimension"] = dimension
        frames.append(frame)

    long = pd.concat(frames, ignore_index=True)
    long = long.sort_values(["iso3", "year", "dimension"]).reset_index(drop=True)
    for column in ["score_0_100", "score_se_0_100", "score_ci90_lower_0_100", "score_ci90_upper_0_100"]:
        long[column.replace("_0_100", "_0_1")] = long[column] / 100.0

    key = ["iso3", "year", "dimension"]
    expected_rows = len(COUNTRIES) * (args.end_year - args.start_year + 1) * len(DIMENSIONS)
    checks = {
        "workbook_exists": workbook.is_file(),
        "unique_country_year_dimension": not long.duplicated(key).any(),
        "all_countries_present": set(long["iso3"]) == set(COUNTRIES),
        "all_dimensions_present": set(long["dimension"]) == set(DIMENSIONS.values()),
        "expected_row_count": len(long) == expected_rows,
        "no_missing_scores": not long["score_0_100"].isna().any(),
        "scores_in_absolute_range": bool(long["score_0_100"].between(0, 100).all()),
        "valid_confidence_intervals": bool(
            (long["score_ci90_lower_0_100"] <= long["score_0_100"]).all()
            and (long["score_0_100"] <= long["score_ci90_upper_0_100"]).all()
        ),
        "positive_standard_errors": bool((long["score_se_0_100"] > 0).all()),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise AssertionError(f"WGI panel validation failed: {failed}")

    value_columns = [
        "score_0_1", "score_se_0_1", "score_ci90_lower_0_1", "score_ci90_upper_0_1", "number_sources"
    ]
    wide_parts = []
    for value in value_columns:
        part = long.pivot(index=["country", "iso3", "year"], columns="dimension", values=value)
        part.columns = [f"{dimension}__{value}" for dimension in part.columns]
        wide_parts.append(part)
    wide = pd.concat(wide_parts, axis=1).reset_index().sort_values(["iso3", "year"])

    long.to_csv(out / "wgi_2002_2024_six_dimension_long.csv", index=False)
    wide.to_csv(out / "wgi_2002_2024_six_dimension_panel.csv", index=False)
    summary = {
        "status": "PASS",
        "source_url": SOURCE_URL,
        "source_sha256": sha256_file(workbook),
        "years": [args.start_year, args.end_year],
        "countries": len(COUNTRIES),
        "country_years": len(wide),
        "dimensions": DIMENSIONS,
        "normalisation": "Official WGI absolute governance score divided by 100; no sample min-max scaling.",
        "checks": checks,
        "score_range_0_1": [float(long["score_0_1"].min()), float(long["score_0_1"].max())],
        "mean_standard_error_0_1": float(long["score_se_0_1"].mean()),
    }
    (out / "wgi_panel_validation.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Validated WGI panel written to {out}")


if __name__ == "__main__":
    main()
