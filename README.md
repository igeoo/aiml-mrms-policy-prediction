# AIML-MRMS: AI-Driven Multi-Layer Systems for Mineral Resource Management

Reproducibility package for the manuscript:

> **AI-Driven Multi-Layer Systems Architecture for Mineral Resource Management: Integrating Decision Intelligence, Investment Optimisation, and Regulatory Alignment**

This repository provides the full computational implementation of the AIML-MRMS framework, covering five integrated layers: data input, AI-based classification, adaptive MCDM ranking, constrained investment optimisation, and policy-coherence scoring with feedback.

---

## Quick start

```bash
python -m venv .venv
.venv\Scripts\activate        # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt

python scripts/05_run_full_pipeline.py
```

All output tables are written to `results/tables/`. A full execution log is available in `RUN_LOG.txt`.

---

## Repository structure

```
data/
  raw/              # WGI 2022, Fraser PPI 2022, UNCTAD FDI 2022 source files
  processed/        # Normalised feature matrix and PCI input vectors
  external/         # Data source references
src/aiml_mrms/      # Core computation modules (SVM, MCDM, investment, PCI)
scripts/            # Numbered reproduction scripts (00–06)
results/tables/     # Generated CSV outputs
docs/               # Data dictionary and reviewer checklist
supplementary/      # Supplementary material index
```

---

## Reproducing from raw data

To rebuild the processed input files from the original public sources:

```bash
python scripts/00_build_processed_data.py
```

Raw source files are included in `data/raw/`:
- `wgi_2022_raw.csv` — World Bank Worldwide Governance Indicators, 2022
- `fraser_ppi_2022.csv` — Fraser Institute Policy Perception Index, 2022
- `unctad_fdi_2022_clean.csv` — UNCTAD World Investment Report, 2022 FDI inflows

---

## Manuscript-to-code map

| Manuscript element | Script / module |
|---|---|
| Table 5: SVM LOO-CV classification | `scripts/01_run_svm_validation.py` |
| Table 6: SVM feature weights | `src/aiml_mrms/svm_validation.py` |
| Eq. 1: adaptive weight update | `src/aiml_mrms/mcdm.py` |
| Eqs. 1b–1c: TOPSIS | `src/aiml_mrms/mcdm.py` |
| Eqs. 3–4: investment optimisation | `src/aiml_mrms/investment.py` |
| Eqs. 5–6: PCI / RPCI | `src/aiml_mrms/pci.py` |
| Tables 9b–9c: α / λ sensitivity | `src/aiml_mrms/sensitivity.py` |
| Manuscript validation report | `scripts/06_validate_manuscript_match.py` |

---

## Dataset

The study covers 16 African mining jurisdictions using publicly available governance and investment data for 2022. The SVM component extracts feature-importance signals to drive adaptive MCDM weight updating; it is not intended as a general-purpose predictive classifier.
