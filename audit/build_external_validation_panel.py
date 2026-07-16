"""Build a leakage-free country-year validation panel from World Bank data."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


INDICATORS = {
    "wdi_fdi_pct_gdp_2002_2024.json": "fdi_pct_gdp",
    "wdi_fdi_current_usd_2002_2024.json": "fdi_current_usd",
    "wdi_mineral_rents_pct_gdp_2002_2024.json": "mineral_rents_pct_gdp",
    "wdi_gdp_per_capita_2002_2024.json": "gdp_per_capita_usd",
    "wdi_gdp_current_usd_2002_2024.json": "gdp_current_usd",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wgi-panel", type=Path, required=True)
    parser.add_argument("--json-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def load_indicator(path: Path, name: str) -> pd.DataFrame:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, list) or len(payload) < 2 or payload[1] is None:
        raise ValueError(f"Unexpected World Bank API response in {path}")
    rows = [
        {"iso3": item["countryiso3code"], "year": int(item["date"]), name: item["value"]}
        for item in payload[1]
    ]
    frame = pd.DataFrame(rows)
    if frame.duplicated(["iso3", "year"]).any():
        raise ValueError(f"Duplicate country-years in {path}")
    return frame


def main() -> None:
    args = parse_args()
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=False)
    wgi = pd.read_csv(args.wgi_panel)
    panel = wgi.copy()
    hashes = {}
    for filename, indicator in INDICATORS.items():
        path = args.json_dir / filename
        hashes[filename] = sha256_file(path)
        panel = panel.merge(load_indicator(path, indicator), on=["iso3", "year"], how="left", validate="one_to_one")

    panel = panel.sort_values(["iso3", "year"]).reset_index(drop=True)
    panel["fdi_pct_gdp_t_plus_1"] = panel.groupby("iso3")["fdi_pct_gdp"].shift(-1)
    panel["asinh_fdi_pct_gdp_t_plus_1"] = np.arcsinh(panel["fdi_pct_gdp_t_plus_1"])
    panel["log_gdp_per_capita"] = np.log(panel["gdp_per_capita_usd"].where(panel["gdp_per_capita_usd"] > 0))
    panel["log_gdp"] = np.log(panel["gdp_current_usd"].where(panel["gdp_current_usd"] > 0))
    panel["eligible_next_year_fdi_model"] = panel[
        ["asinh_fdi_pct_gdp_t_plus_1", "mineral_rents_pct_gdp", "log_gdp_per_capita", "log_gdp"]
    ].notna().all(axis=1)

    checks = {
        "unique_country_year": not panel.duplicated(["iso3", "year"]).any(),
        "wgi_rows_preserved": len(panel) == len(wgi),
        "all_five_indicators_have_observations": all(panel[name].notna().any() for name in INDICATORS.values()),
        "future_target_is_within_country": bool(
            panel.loc[panel["year"] == panel["year"].max(), "fdi_pct_gdp_t_plus_1"].isna().all()
        ),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise AssertionError(f"External panel validation failed: {failed}")

    panel.to_csv(out / "wgi_wdi_external_validation_panel.csv", index=False)
    missingness = panel[[*INDICATORS.values(), "fdi_pct_gdp_t_plus_1"]].isna().sum().rename("missing_rows").reset_index()
    missingness = missingness.rename(columns={"index": "variable"})
    missingness.to_csv(out / "external_panel_missingness.csv", index=False)
    report = {
        "status": "PASS",
        "rows": len(panel),
        "countries": int(panel["iso3"].nunique()),
        "years": [int(panel["year"].min()), int(panel["year"].max())],
        "eligible_next_year_fdi_rows": int(panel["eligible_next_year_fdi_model"].sum()),
        "outcome_definition": "Governance and controls at year t predict FDI inflow (% GDP) at t+1; target transformed with asinh.",
        "causal_claim": "None. Predictive and convergent-validity analysis only.",
        "source_sha256": hashes,
        "checks": checks,
    }
    (out / "external_panel_validation.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Validated external-outcome panel written to {out}")


if __name__ == "__main__":
    main()
