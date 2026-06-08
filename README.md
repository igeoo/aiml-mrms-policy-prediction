# AIML-MRMS: AI-Driven Multi-Layer Systems Architecture for Mineral Resource Management

**Reproducibility package for the manuscript:**

> *AI-Driven Multi-Layer Systems Architecture for Mineral Resource Management: Integrating Decision Intelligence, Investment Optimisation, and Regulatory Alignment*

This repository provides the full computational implementation of the AIML-MRMS framework — a five-layer decision-support architecture that integrates machine learning classification, adaptive multi-criteria ranking, constrained investment optimisation, and policy-coherence scoring with closed-loop feedback. The package is designed for complete end-to-end reproducibility of all quantitative results reported in the manuscript.

---

## Table of contents

1. [Framework overview](#framework-overview)
2. [Repository structure](#repository-structure)
3. [Installation](#installation)
4. [Data](#data)
5. [Running the pipeline](#running-the-pipeline)
6. [Manuscript-to-code map](#manuscript-to-code-map)
7. [Generated outputs](#generated-outputs)
8. [Key results](#key-results)
9. [Validation](#validation)
10. [Supplementary material](#supplementary-material)
11. [License](#license)

---

## Framework overview

The AIML-MRMS framework comprises five computational layers:

| Layer | Function | Implementation |
|---|---|---|
| **1. Input** | Data acquisition and min-max normalisation of governance and investment indicators | `scripts/00_build_processed_data.py` |
| **2. AI Decision** | Linear SVC classification with class balancing, grid-search, LOO-CV, permutation testing, and feature-importance extraction | `src/aiml_mrms/svm_validation.py` |
| **3. MCDM** | Adaptive AHP-TOPSIS weight updating driven by SVM feature-importance signals | `src/aiml_mrms/mcdm.py` |
| **4. Investment Intelligence** | Multi-objective constrained optimisation (continuous fractional LP) with governance penalty parameter λ | `src/aiml_mrms/investment.py` |
| **5. Output & Feedback** | Policy Coherence Index (PCI) and Regulatory Policy Coherence Index (RPCI) computation, benchmarking across four configurations, and α/λ sensitivity analysis | `src/aiml_mrms/pci.py`, `src/aiml_mrms/sensitivity.py` |

The study applies this framework to **16 African mining jurisdictions** using publicly available 2022 governance and FDI data, with in-depth case studies for Nigeria (NGA) and South Africa (ZAF).

---

## Repository structure

```
.
├── data/
│   ├── raw/                        # Verified public-source input files
│   │   ├── wgi_2022_raw.csv        # World Bank WGI 2022 (long-format export)
│   │   ├── fraser_ppi_2022.csv     # Fraser Institute PPI 2022 (16 countries)
│   │   ├── unctad_fdi_2022_clean.csv  # UNCTAD FDI inflows 2022
│   │   └── README.md               # Data provenance notes
│   ├── processed/                  # Normalised inputs used by scripts
│   │   ├── feature_matrix_normalised.csv
│   │   ├── pci_input_vectors.csv
│   │   └── project_scores.csv
│   └── external/
│       └── data_sources.md         # Full citation and download instructions
├── src/aiml_mrms/                  # Reusable Python modules
│   ├── svm_validation.py           # SVM training, LOO-CV, permutation test, feature weights
│   ├── mcdm.py                     # AHP weight initialisation, adaptive update (Eq. 1), TOPSIS (Eqs. 1b–1c)
│   ├── investment.py               # Constrained LP optimisation (Eqs. 3–4)
│   ├── pci.py                      # PCI/RPCI computation (Eqs. 5–6)
│   ├── sensitivity.py              # α and λ sweep functions
│   └── data_utils.py               # Shared data loading helpers
├── scripts/
│   ├── 00_build_processed_data.py  # Build processed CSVs from raw sources
│   ├── 01_run_svm_validation.py    # AI decision layer — Table 5 & Table 6
│   ├── 02_run_mcdm_topsis.py       # MCDM layer — Table 7
│   ├── 03_run_pci_rpci.py          # PCI/RPCI baseline
│   ├── 04_run_investment_optimisation.py  # Investment layer
│   ├── 05_run_full_pipeline.py     # End-to-end pipeline including sensitivity analysis
│   ├── 06_validate_manuscript_match.py    # Numerical comparison against manuscript values
│   └── run_pipeline_and_log.py     # Pipeline runner with full environment capture
├── results/tables/                 # All generated CSV outputs (pre-computed)
├── docs/
│   ├── data_dictionary.md          # Column definitions for all processed files
│   ├── manuscript_results_map.md   # Map from manuscript tables to output files
│   └── reviewer_reproducibility_checklist.md
├── supplementary/
│   └── supplementary_index.md      # Index of supplementary sections S1–S5
├── RUN_LOG.txt                     # Full execution log from verified local run
├── terminal_output.txt             # Terminal output from pipeline execution
├── requirements.txt
└── environment.yml
```

---

## Installation

### Option A — pip (recommended for quick start)

```bash
git clone https://github.com/igeoo/aiml-mrms-policy-prediction.git
cd aiml-mrms-policy-prediction

python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux / macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

### Option B — conda

```bash
conda env create -f environment.yml
conda activate aiml-mrms
```

**Dependencies:** Python ≥ 3.11, numpy ≥ 1.24, pandas ≥ 2.0, scipy ≥ 1.10, scikit-learn ≥ 1.3, matplotlib ≥ 3.7, openpyxl ≥ 3.1.

---

## Data

### Sources

| File | Source | Year | Access |
|---|---|---|---|
| `wgi_2022_raw.csv` | World Bank Worldwide Governance Indicators | 2022 | [databank.worldbank.org](https://databank.worldbank.org/source/worldwide-governance-indicators) |
| `fraser_ppi_2022.csv` | Fraser Institute Annual Survey of Mining Companies | 2022 | [fraserinstitute.org](https://www.fraserinstitute.org/mining-survey) |
| `unctad_fdi_2022_clean.csv` | UNCTAD World Investment Report 2025, Annex Table 1 | 2022 values | [unctad.org](https://unctad.org/topic/investment/world-investment-report) |

All three raw files are included in `data/raw/`. Detailed provenance and download instructions are in `data/external/data_sources.md`.

### Pre-processing

Raw files are processed by `scripts/00_build_processed_data.py`, which:
- Filters to the 16-country study set
- Applies min-max normalisation within the subset for each WGI indicator and Fraser PPI
- Merges WGI, Fraser PPI, and UNCTAD FDI into the three processed CSV files

To rebuild from raw sources:

```bash
python scripts/00_build_processed_data.py
# With cross-validation against Supplementary Table S2.1:
python scripts/00_build_processed_data.py --validate
```

### Feature matrix

`data/processed/feature_matrix_normalised.csv` — 16 rows × 9 columns:

| Column | Description | Range |
|---|---|---|
| `country` | Country name | — |
| `iso3` | ISO 3166-1 alpha-3 code | — |
| `rule_of_law` | WGI Rule of Law (normalised) | [0, 1] |
| `regulatory_quality` | WGI Regulatory Quality (normalised) | [0, 1] |
| `government_effectiveness` | WGI Government Effectiveness (normalised) | [0, 1] |
| `control_of_corruption` | WGI Control of Corruption (normalised) | [0, 1] |
| `political_stability` | WGI Political Stability (normalised) | [0, 1] |
| `fraser_ppi` | Fraser PPI investment-attractiveness proxy (normalised) | [0, 1] |
| `label` | Binary investment environment label | Favourable / Unfavourable |

---

## Running the pipeline

### Full pipeline (recommended)

```bash
python scripts/05_run_full_pipeline.py --permutations 1000
```

### With execution log and environment capture

```bash
python scripts/run_pipeline_and_log.py --permutations 1000
```

This produces `RUN_LOG.txt` containing Python version, platform, package versions, per-script stdout/stderr, and pass/fail summary.

### Individual scripts

```bash
python scripts/01_run_svm_validation.py --permutations 1000  # Table 5 & 6
python scripts/02_run_mcdm_topsis.py                          # Table 7
python scripts/03_run_pci_rpci.py                             # Table 8 baseline
python scripts/04_run_investment_optimisation.py              # Investment allocation
python scripts/06_validate_manuscript_match.py                # Numerical validation report
```

All outputs are written to `results/tables/`.

---

## Manuscript-to-code map

### Scripts

| Script | Manuscript element |
|---|---|
| `00_build_processed_data.py` | Supplementary S1, S2.1 — data provenance and feature matrix |
| `01_run_svm_validation.py` | Table 5 (SVM LOO-CV metrics), Table 6 (feature weights), permutation test |
| `02_run_mcdm_topsis.py` | Table 7 (TOPSIS closeness coefficients, Cycle 1 and Cycle 3) |
| `03_run_pci_rpci.py` | Table 8 (PCI/RPCI scenario benchmarking) |
| `04_run_investment_optimisation.py` | Section 6.6 (investment allocation, λ = 0.15) |
| `05_run_full_pipeline.py` | Tables 9b–9c (α and λ sensitivity analysis) |
| `06_validate_manuscript_match.py` | Full numerical comparison report |

### Source modules

| Module | Equations implemented |
|---|---|
| `src/aiml_mrms/svm_validation.py` | SVC decision function, LOO-CV, permutation test |
| `src/aiml_mrms/mcdm.py` | Eq. 1 (adaptive weight update), Eqs. 1b–1c (TOPSIS) |
| `src/aiml_mrms/investment.py` | Eqs. 3–4 (constrained LP) |
| `src/aiml_mrms/pci.py` | Eqs. 5–6 (PCI / RPCI) |
| `src/aiml_mrms/sensitivity.py` | α sweep (Table 9b), λ sweep (Table 9c) |

### Generated outputs

| Output file | Manuscript table / figure |
|---|---|
| `table5_svm_loo_metrics.csv` | Table 5 — SVM LOO-CV metrics |
| `table5_confusion_matrix.csv` | Table 5 — confusion matrix |
| `permutation_test_summary.csv` | Table 5 — permutation test p-value |
| `permutation_test_distribution.csv` | Supplementary S2.2 |
| `table6_svm_feature_weights.csv` | Table 6 — raw and normalised feature weights |
| `table6_aggregated_criterion_weights.csv` | Table 6 — aggregated AHP criterion weights |
| `alternative_classifier_feature_weights.csv` | Supplementary S2.3 |
| `alternative_classifier_criterion_weights.csv` | Supplementary S2.3 |
| `adaptive_weight_evolution_alpha_065.csv` | Table 7 header — weight evolution (α = 0.65) |
| `table7_topsis_results.csv` | Table 7 — TOPSIS closeness coefficients |
| `table8_pci_rpci_scenarios.csv` | Table 8 — PCI/RPCI four-configuration benchmarking |
| `baseline_pci_rpci.csv` | Table 8 — Cycle 1 baseline |
| `investment_allocation_lambda_015.csv` | Section 6.6 — optimal allocation x* |
| `table9b_alpha_sensitivity.csv` | Table 9b — α sensitivity |
| `table9c_lambda_sensitivity.csv` | Table 9c — λ sensitivity |
| `manuscript_validation_report.txt` | Full computed-vs-manuscript comparison |

---

## Key results

| Result | Value |
|---|---|
| SVM LOO-CV Accuracy | 1.000 |
| SVM LOO-CV Balanced Accuracy | 1.000 |
| SVM LOO-CV F1-score | 1.000 |
| Permutation test p-value (n = 1000) | 0.002 |
| Top-ranked project (NGA) | NG-B: FDI-compliant open-pit (C₁ = 0.716, C₃ = 0.784) |
| Top-ranked project (ZAF) | ZA-B: ESG-certified open-cast (C₁ = 0.734, C₃ = 0.800) |
| ΔPCI — AIML-MRMS full adaptive (NGA) | +0.030 |
| ΔPCI — AIML-MRMS full adaptive (ZAF) | +0.017 |

ΔPCI values are consistent across all model configurations, confirming the robustness of the core policy-coherence conclusions.

---

## Validation

`scripts/06_validate_manuscript_match.py` performs a systematic numerical comparison between the computed outputs and the manuscript's reported values for Tables 5–8. The report is written to `results/tables/manuscript_validation_report.txt`.

Key notes on numerical differences:
- Feature weights and TOPSIS closeness coefficients reflect **local min-max normalisation** within the 16-country subset, whereas the manuscript's originally reported values used a global normalisation range (Supplementary S2.1). All ΔPCI values — the paper's core quantitative claim — match exactly across both normalisation conventions.
- The SVM achieves perfect linear separability on this dataset, yielding LOO-CV ROC-AUC = 1.000. This is expected for a 16-country proof-of-concept study with a well-separated feature space.
- All results are fully reproducible with `random_state=42` fixed in all `LinearSVC` calls.

---

## Supplementary material

The complete compiled supplementary document (including narratives, corrected tables, and full formatting) can be found at: [`supplementary/AIML_MRMS_Supplementary_Material.docx`](supplementary/AIML_MRMS_Supplementary_Material.docx).

Supplementary sections referenced in the manuscript also correspond to the following raw repository resources:

| Section | Content | Location |
|---|---|---|
| S1 | Data provenance and extraction protocol | `data/external/data_sources.md`, `data/raw/README.md` |
| S2.1 | Feature matrix with country-level normalised scores | `data/processed/feature_matrix_normalised.csv` |
| S2.2 | SVM LOO-CV and permutation test distribution | `results/tables/permutation_test_distribution.csv` |
| S2.3 | Alternative classifier comparison | `results/tables/alternative_classifier_*.csv` |
| S2.4 | α sensitivity | `results/tables/table9b_alpha_sensitivity.csv` |
| S2.5 | λ sensitivity and investment allocation | `results/tables/table9c_lambda_sensitivity.csv`, `results/tables/investment_allocation_lambda_015.csv` |
| S2.6 | PCI/RPCI and convergent validity | `results/tables/table8_pci_rpci_scenarios.csv` |
| S3 | AHP pairwise matrix and consistency ratio | Manuscript appendix |
| S4 | PCI/RPCI derivation and robustness | `src/aiml_mrms/pci.py` |
| S5 | Code availability | This repository |

---

## License

See [LICENSE](LICENSE) for terms of use.
