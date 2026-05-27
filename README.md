# AIML-MRMS Reproducibility Package

This repository supports the manuscript:

**AI-Driven Multi-Layer Systems Architecture for Mineral Resource Management: Integrating Decision Intelligence, Investment Optimisation, and Regulatory Alignment**

The package implements the computational proof-of-concept for the AIML-MRMS framework:

1. Input layer: WGI 2022 + Fraser Policy Perception Index feature matrix.
2. AI decision layer: Linear SVC with class balancing, grid search, LOO-CV, permutation testing, and feature-importance extraction.
3. MCDM layer: adaptive AHP-TOPSIS weight updating.
4. Investment intelligence layer: constrained allocation under governance penalty parameter λ.
5. Output/feedback layer: PCI/RPCI computation, benchmarking, and α/λ sensitivity analysis.

## Scope statement for reviewers

This repository supports **proof-of-concept reproducibility**, not broad predictive generalisation. The manuscript dataset contains 16 African mining jurisdictions. The SVM component is used primarily to extract feature-importance signals for adaptive MCDM weighting.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python scripts/05_run_full_pipeline.py
```

Generated CSV outputs are written to `results/tables/`.

## Repository structure

```text
data/
  raw/                         # place downloaded public-source files here
  processed/                   # processed CSV files used by the scripts
  external/data_sources.md
src/aiml_mrms/                 # reusable computation modules
scripts/                       # executable reproduction scripts
results/tables/                # generated outputs
docs/                          # reviewer checklist and data dictionary
supplementary/                 # supplementary material index
```

## Manuscript-to-code map

| Manuscript element | Script/module |
|---|---|
| Table 5: SVM LOO-CV classification | `scripts/01_run_svm_validation.py` |
| Table 6: SVM feature weights | `src/aiml_mrms/svm_validation.py` |
| Eq. 1: adaptive weight update | `src/aiml_mrms/mcdm.py` |
| Eqs. 1b–1c: TOPSIS | `src/aiml_mrms/mcdm.py` |
| Eqs. 3–4: investment optimisation | `src/aiml_mrms/investment.py` |
| Eqs. 5–6: PCI/RPCI | `src/aiml_mrms/pci.py` |
| Tables 9b–9c: α/λ sensitivity | `src/aiml_mrms/sensitivity.py` |

## Required public data sources

- World Bank Worldwide Governance Indicators, 2022.
- Fraser Institute Annual Survey of Mining Companies, 2022.
- UNCTAD World Investment Report 2023, Annex Table 1.
- Optional convergent-validity sources: Transparency International CPI 2022 and UNDP HDI 2021/2022.

## Data status

The processed CSV files in `data/processed/` have been generated from verified public sources using `scripts/00_build_processed_data.py`. No placeholder values remain. The raw source files (`wgi_2022_raw.csv`, `fraser_ppi_2022.csv`, `unctad_fdi_2022_clean.csv`) are included in `data/raw/` for full reproducibility. A complete end-to-end pipeline run log is available in `RUN_LOG.txt`.
