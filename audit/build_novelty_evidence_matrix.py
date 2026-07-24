"""Build the novelty evidence matrix comparing AIML-MRMS Version C
against identified prior art.

Outputs a CSV that can be embedded in the supervisor report and manuscript.
"""

from __future__ import annotations

import csv
from pathlib import Path


FEATURES = [
    "Country-level governance screening separated from project-level MCDM",
    "Uses all six official WGI dimensions (not a subset or ad hoc selection)",
    "Propagates published WGI measurement uncertainty (standard errors)",
    "Tests correlated measurement-error sensitivity (equicorrelation scenarios)",
    "Alternative weighting robustness (PCA, entropy, Fraser-correlation, Dirichlet perturbation)",
    "Temporal rank stability analysis (2002-2024)",
    "Leakage-free convergent validation against mining-specific benchmark (Fraser PPI)",
    "Nested leave-one-country-out cross-validation design",
    "Explicit null-result reporting (general FDI construct-boundary test)",
    "Reproducible open-source pipeline with deterministic seeds",
    "Country-cluster bootstrap confidence intervals",
    "Construct diagnostics (Cronbach alpha, PCA, VIF) reported transparently",
]

PRIOR_ART = {
    "Tafur et al. (2022)\nAHP-TOPSIS petroleum\ninvestment risk, S. America": [
        "No", "No (uses ad hoc criteria)", "No", "No", "No", "No",
        "No", "No", "No", "Not reported", "No", "No",
    ],
    "Tang et al. (2023)\nAHP/entropy-TOPSIS-GRA\noil & gas, Belt & Road": [
        "No", "No (uses composite indices)", "No", "No",
        "Partial (AHP + entropy comparison)", "No",
        "No", "No", "No", "Not reported", "No", "No",
    ],
    "Li et al. (2020)\nEntropy-TOPSIS\nresources, Belt & Road": [
        "No", "No (uses composite indices)", "No", "No",
        "No (entropy only)", "No",
        "No", "No", "No", "Not reported", "No", "No",
    ],
    "MineHutte / Mining IQ\nWorld Risk Insights\n(commercial)": [
        "Yes (partially)", "Not disclosed", "Not disclosed", "Not disclosed",
        "Not disclosed", "Not disclosed",
        "Proprietary", "Not disclosed", "No", "No (proprietary)", "Not disclosed", "Not disclosed",
    ],
    "AIML-MRMS Version C\n(this study)": [
        "Yes", "Yes", "Yes", "Yes", "Yes", "Yes",
        "Yes", "Yes", "Yes", "Yes", "Yes", "Yes",
    ],
}


def main() -> None:
    out = Path(r"c:\Users\USER\Documents\python_codes\super_project\AIML_MRMS"
               r"\aiml_mrms_github_package\aiml_mrms_github_package"
               r"\results\tables")
    out.mkdir(parents=True, exist_ok=True)

    filepath = out / "novelty_evidence_matrix.csv"
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        header = ["Feature / Capability"] + list(PRIOR_ART.keys())
        writer.writerow(header)
        for i, feature in enumerate(FEATURES):
            row = [feature] + [PRIOR_ART[study][i] for study in PRIOR_ART]
            writer.writerow(row)

    print(f"Novelty evidence matrix written to {filepath}")
    print(f"  {len(FEATURES)} features x {len(PRIOR_ART)} studies")


if __name__ == "__main__":
    main()
