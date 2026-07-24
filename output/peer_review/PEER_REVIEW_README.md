# AIML-MRMS Version C peer-review package

## Review target

This package contains the computational evidence proposed to replace the disputed manuscript Tables 8 and 9. The historical table must not be treated as a valid comparison of four independently executed architectures. Version C instead presents a construct-separated, six-dimensional country-governance coherence analysis with uncertainty, robustness, mining-specific convergent validation, and a reported null general-FDI test.

Repository branch: `codex/version-c-novelty-extension`

Locked package commit: `ec24cf0`

## Start here

1. Read `output/doc/AIML_MRMS_Version_C_Comprehensive_Supervisor_Report.docx`.
2. Compare every reported number with the two CSV files in `results/tables/`.
3. Inspect the validation manifests in the dated `audit_artifacts/` directories.
4. Review the analysis code in `audit/` and the historical/core metric code in `src/aiml_mrms/`.
5. Review the novelty boundary in `audit_artifacts/20260717_version_c_acceptance_package/novelty_evidence_matrix.csv`.

## Central claims to verify

- All six official WGI dimensions are used on the official absolute scale divided by 100.
- Country governance is kept separate from project-level EV/RC/EI/OF AHP-TOPSIS criteria.
- Uniform six-dimension weighting is primary; PCA, entropy, and Fraser-correlation weights are sensitivities.
- Published WGI standard errors are propagated with 10,000 Monte Carlo draws under a disclosed independent-error approximation.
- Weight sensitivity uses 10,000 Dirichlet draws.
- Fraser PPI is used only as an external mining-policy benchmark, without feature-target leakage.
- General FDI provides no reliable predictive validation and is retained as a null/falsification result.
- The implementation does not demonstrate a closed feedback loop, convergence, causality, or empirical architecture superiority.

## Candidate publication tables

- `results/tables/table8_version_c_governance_coherence_2024.csv`
- `results/tables/table9_version_c_validation_robustness.csv`

## Authoritative inputs and locked outputs

- `audit_artifacts/20260716_novelty_wgi_panel/`: 2002-2024 official six-dimension WGI panel and validation record.
- `audit_artifacts/20260716_novelty_external_panel/`: WGI/WDI panel used for the general-FDI falsification test.
- `data/external/`: Fraser PPI observations and source notes.
- `audit_artifacts/20260717_fraser_convergent_validation/`: mining-specific validation outputs.
- `audit_artifacts/20260717_novelty_modeling/`: construct diagnostics and general-FDI validation outputs.
- `audit_artifacts/20260717_six_dimension_robustness_final/`: primary scores, alternative weights, uncertainty, temporal stability, and rank probabilities.
- `audit_artifacts/20260717_version_c_acceptance_package/`: consolidated evidence matrix, Markdown report, and output hashes.

## Relevant code

- `audit/build_wgi_six_dimension_panel.py`
- `audit/build_external_validation_panel.py`
- `audit/run_novelty_modeling.py`
- `audit/run_fraser_convergent_validation.py`
- `audit/run_six_dimension_robustness.py`
- `audit/generate_version_c_acceptance_package.py`
- `audit/run_version_c_analysis.py`
- `src/aiml_mrms/governance_pci.py`
- `src/aiml_mrms/weighted_pci.py`
- `src/aiml_mrms/pci.py`
- `src/aiml_mrms/mcdm.py`
- `src/aiml_mrms/svm_validation.py`
- `tests/test_governance_pci.py`

## Environment

Install packages from `requirements.txt`. Run scripts from the package root with `PYTHONPATH=src` where required.

The original official WGI workbook is not redistributed in this ZIP. Its source URL and SHA256 are recorded in `audit_artifacts/20260716_novelty_wgi_panel/wgi_panel_validation.json`. The derived panel required for reviewing and rerunning downstream analyses is included.

## Suggested independent review questions

1. Can every number in the supervisor report be reproduced from the included CSV/JSON artifacts?
2. Are the PCI and RPCI dispersion penalties mathematically and substantively justified?
3. Is uniform weighting defensible as the primary specification?
4. Is the WGI independent-error approximation acceptable when disclosed?
5. Is Fraser PPI an appropriate convergent benchmark, given its perception and coverage limitations?
6. Are the country-cluster bootstrap and leave-one-country-out designs implemented correctly?
7. Does the null general-FDI result receive an appropriately limited interpretation?
8. Is the country-governance/project-MCDM construct boundary sufficiently clear?
9. Is the proposed novelty genuinely differentiated from existing mining MCDM and composite-governance work?
10. What claims or table labels should be weakened before manuscript integration?

## Scope warning

This is a computational peer-review package, not the revised manuscript. Final table numbering, terminology, equations, contribution wording, and adoption remain subject to supervisor/author approval.
