# Reviewer reproducibility checklist

## Data
- [ ] `feature_matrix_normalised.csv` contains the final verified 16-country WGI + Fraser values.
- [ ] `project_scores.csv` contains documented project score assumptions and provenance.
- [ ] `pci_input_vectors.csv` contains the final WGI + FDI vectors used in PCI/RPCI.
- [ ] Raw public-source downloads or download instructions are stored in `data/raw/`.

## Scripts
- [ ] `python scripts/05_run_full_pipeline.py` runs without error.
- [ ] SVM LOO-CV metrics reproduce Table 5.
- [ ] Permutation test output supports the reported p-value.
- [ ] Feature weights reproduce Table 6.
- [ ] Alternative classifier outputs are deposited.
- [ ] Adaptive weights reproduce the manuscript weight evolution.
- [ ] TOPSIS outputs reproduce Table 7.
- [ ] PCI/RPCI outputs reproduce Table 8.
- [ ] Investment optimisation reproduces the reported x* allocation.
- [ ] α and λ sensitivity outputs reproduce Tables 9b and 9c.

## Manuscript readiness
- [ ] No internal author/editorial notes remain.
- [ ] Figures 1–3 are inserted as actual graphics.
- [ ] All Section 6 claims are backed by deposited code and output files.
- [ ] The manuscript frames validation as proof-of-concept.
