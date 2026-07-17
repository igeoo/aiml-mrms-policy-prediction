# AIML-MRMS Version C: authoritative Antigravity implementation handoff

## 0. Status and authority

This document is the implementation handoff for continuing the AIML-MRMS Tables 8 and 9 remediation and Version C novelty work. Follow it in order. Do not revive superseded methods or silently reinterpret terminology.

The latest supervisor-style review has approved the next corrective phase with these conditions:

1. Treat the existing Version C report as **interim**, not submission-ready.
2. Retain Version C's construct separation and honest null-result reporting.
3. Add correlated-WGI-measurement-error sensitivity; this is required, not optional.
4. Show all six disaggregated WGI dimensions so the author-defined composite is never the reader's only evidence.
5. Reframe novelty as a rigor, validation, and transparency contribution rather than construct or algorithm novelty.
6. Never describe the audit-introduced FDI test as "pre-specified."
7. After revising the novelty, limitations, tables, and manuscript, rerun the complete manuscript-versus-repository consistency audit.
8. Return the revised novelty statement and limitations paragraph for supervisor/author review before submission.

The source review supplied by the user is at:

`C:\Users\USER\aiml_mrms_brief_claude.md`

## 1. Repository state

### Working directory

`C:\Users\USER\Documents\python_codes\super_project\AIML_MRMS\aiml_mrms_github_package\aiml_mrms_github_package`

### Active branch

`codex/version-c-novelty-extension`

### Locked commit chain

- `cc7648b` - Revised the FDI-mapping recommendation toward governance-only PCI.
- `f3437e4` - Implemented reproducible baseline Version C governance analysis.
- `d853914` - Built authoritative six-dimension WGI and WDI panels.
- `ccdbfc2` - Added leakage-free external-validation models.
- `b08f67e` - Added six-dimension measurement-uncertainty and weighting robustness analysis.
- `ec24cf0` - Packaged the current Version C evidence, candidate tables, and interim supervisor report.

Start from `ec24cf0`. Preserve the existing artifacts as the locked independent-error baseline. New work must go into new scripts or clearly versioned output directories. Do not overwrite the baseline without retaining an auditable comparison.

## 2. Terminology that must not be mixed up

The project used "Option B" in two different decision contexts.

### Earlier Option B: overall remediation strategy

This meant replacing hard-coded Tables 8 and 9 with genuine computational results and rewriting the methodology and claims accordingly. It led to the weighted PCI/RPCI investigation.

### Later Version B: FDI/EV mapping alternative

This meant splitting project-level Economic Viability into an unsupported 50/50 proxy allocation. This later Version B was rejected.

### Approved Version C

Version C means:

- Keep project-level EV, RC, EI/ESG, and OF inside the project AHP-TOPSIS layer.
- Do not project EV or FDI into country-level governance dimensions.
- Use all six official WGI dimensions for a separate country-governance screening layer.
- Treat Fraser PPI as an external mining-policy benchmark only.
- Treat general FDI as an explicitly reported falsification or construct-boundary test only.

Never call the FDI test "pre-specified." It was introduced during the audit.

## 3. Non-negotiable scientific conclusions

1. The original four-configuration numerical comparison is withdrawn.
2. The old `pci_gain_scenarios()` values were hard-coded and are not admissible performance evidence.
3. The historical configurations were not four independently executed architectures. They were predominantly alternative weighting states applied to substantially the same calculation.
4. The code did not implement a country-outcome-fed feedback loop.
5. The code did not implement a convergence test. The historical "three cycles" were an initial state plus two predefined convex updates.
6. The historical "Standalone AI" was not a separate AI decision pipeline; it was a model-derived weighting sensitivity.
7. Version C does not prove AIML-MRMS superiority, causality, investment prediction, convergence, or adaptive feedback.
8. PCI/RPCI are author-defined diagnostics. They are not official World Bank measures and must not be presented as a definitive overall governance score.
9. The six raw WGI dimensions must remain visible and interpretable alongside any composite diagnostic.
10. Negative or null results must remain in the record.

## 4. What has already been implemented and validated

### 4.1 Official WGI panel

- Six official dimensions: Voice and Accountability, Political Stability, Government Effectiveness, Regulatory Quality, Rule of Law, and Control of Corruption.
- Sixteen study countries.
- Twenty-three years, 2002-2024.
- 368 complete country-year observations.
- Official absolute 0-100 scores divided by 100.
- No within-sample min-max scaling.
- Official standard errors and confidence intervals retained.

Official workbook source:

`https://www.worldbank.org/content/dam/sites/govindicators/doc/wgidataset_with_sourcedata-2025.xlsx`

Recorded workbook SHA256:

`25a2f9eabb90b0092973392c0b31571aa58b691cc5786292e504b52f693e1eb8`

Authoritative files:

- `audit/build_wgi_six_dimension_panel.py`
- `audit_artifacts/20260716_novelty_wgi_panel/wgi_2002_2024_six_dimension_panel.csv`
- `audit_artifacts/20260716_novelty_wgi_panel/wgi_2002_2024_six_dimension_long.csv`
- `audit_artifacts/20260716_novelty_wgi_panel/wgi_panel_validation.json`

### 4.2 External WDI panel and general-FDI boundary test

The external panel contains FDI inflow percentage of GDP, FDI current USD, mineral rents percentage of GDP, GDP per capita, and GDP current USD.

Validation design:

- Governance and controls at year `t` predict general FDI at `t+1`.
- Nested leave-one-country-out validation.
- Temporal holdout trained through 2018 and evaluated on 2019-2023.
- Country-cluster bootstrap.
- No causal claim.

Locked result:

- Incremental combined-model MAE improvement over controls: `-0.0067`.
- Country-cluster bootstrap 95% interval: `-0.0301` to `0.0160`.
- Bootstrap probability of improvement: `0.291`.

Interpretation: governance did not provide reliable incremental prediction of general FDI. General FDI is rejected as a success target for the governance layer.

Files:

- `audit/build_external_validation_panel.py`
- `audit/run_novelty_modeling.py`
- `audit_artifacts/20260716_novelty_external_panel/`
- `audit_artifacts/20260717_novelty_modeling/`

### 4.3 Fraser mining-policy convergent validation

- 70 country-year observations.
- 14 countries.
- 2019-2024.
- Nigeria and Sierra Leone have no Fraser observations and are not imputed.
- Fraser PPI is not both a feature and target.

Locked results:

- Uniform six-dimension governance mean versus Fraser PPI Spearman rho: `0.7147`.
- Country-cluster bootstrap 95% interval: `0.4370` to `0.8479`.
- Nested leave-one-country-out Ridge: R2 `0.3360`, MAE `15.70`, Spearman rho `0.6016`.

Interpretation: this is convergent association with a mining-policy perception benchmark. It is not causal validation and Fraser PPI is not ground truth.

Files:

- `audit/run_fraser_convergent_validation.py`
- `data/external/fraser_ppi_2019_2024_study_countries.csv`
- `data/external/fraser_ppi_2019_2024_sources.md`
- `audit_artifacts/20260717_fraser_convergent_validation/`

### 4.4 Construct diagnostics

- Cronbach alpha: `0.9685`.
- PC1 explained variance: `0.8858`.
- First two PCs cumulative variance: `0.9359`.
- Maximum VIF: `23.12`.

Interpretation: the six dimensions share a strong governance signal and are highly collinear. This does not prove unidimensionality. Correlation can reflect conceptual overlap and WGI shared-source mechanics. Multivariate coefficient signs are unstable and must not be used as causal or primary weights.

### 4.5 Primary weights and robustness

Primary weights are uniform: `1/6` for each WGI dimension.

Sensitivity schemes:

- PCA absolute-loading weights.
- Entropy weights.
- Normalized positive bivariate Fraser-correlation weights.

Locked rank stability versus uniform:

- PCA PCI/RPCI Spearman: `1.000 / 1.000`.
- Entropy PCI/RPCI Spearman: `0.994 / 0.994`.
- Fraser-weight PCI/RPCI Spearman: `1.000 / 1.000`.

Weight perturbation:

- 10,000 draws from `Dirichlet(10,10,10,10,10,10)`.
- PCI rank rho median `0.9971`; lower 2.5% `0.9912`.
- RPCI rank rho median `0.9941`; lower 2.5% `0.9882`.

Files:

- `audit/run_six_dimension_robustness.py`
- `audit_artifacts/20260717_six_dimension_robustness_final/`

### 4.6 Current candidate tables and report

- `results/tables/table8_version_c_governance_coherence_2024.csv`
- `results/tables/table9_version_c_validation_robustness.csv`
- `output/doc/AIML_MRMS_Version_C_Comprehensive_Supervisor_Report.docx`
- `output/peer_review/AIML_MRMS_Version_C_Peer_Review_Package.zip`

These are interim because they do not yet include the correlated-error extension, the expanded prior-art landscape, or the explicit WGI non-aggregation response.

## 5. Verified novelty and prior-art correction

Do not claim novelty for AHP, TOPSIS, AHP-TOPSIS, WGI aggregation, Fraser PPI, PCA, entropy weights, Ridge regression, machine learning, Monte Carlo analysis, or extractive-sector country-risk ranking.

The following prior art must be added explicitly:

1. Tafur, Lilford, and Aguilera, petroleum investment-risk ranking in South America using AHP and TOPSIS: `https://doi.org/10.1007/s43546-022-00221-6`.
2. Tang et al., oil and gas investment-risk assessment across 76 Belt and Road countries using AHP/entropy and TOPSIS-GRA: `https://doi.org/10.1016/j.petsci.2023.10.009`.
3. Investment risk and natural-resource potential across 63 Belt and Road countries using entropy-TOPSIS: `https://doi.org/10.1016/j.scitotenv.2020.137981`.
4. Mining IQ / MineHutte World Risk Insights methodology: `https://www.mining-iq.com/focus-risk-methodology`.
5. World Bank WGI FAQ explaining why it does not publish one composite across the six dimensions: `https://www.worldbank.org/en/publication/worldwide-governance-indicators/frequently-asked-questions`.

World Bank's position must be represented accurately:

- It does not publish one overall six-dimension governance score for conceptual and statistical reasons.
- Shared source inputs mechanically contribute to cross-dimension correlation.
- Constructing margins of error for an overall composite is difficult.
- This is not a categorical prohibition on transparent author-defined exploration.
- Any author-defined index must not be represented as an official WGI measure or comprehensive governance truth.

MineHutte is commercial/practitioner competition, not necessarily peer-reviewed academic prior art. Treat it as part of the decision-support landscape.

## 6. Approved novelty direction

Use a narrow rigor-and-validation contribution. Recommended working statement:

> This study contributes a rigor-oriented governance screening protocol for mineral-investment decision support. It separates country-level governance diagnostics from project-level economic and operational evaluation, propagates published WGI measurement uncertainty, evaluates alternative weighting assumptions, conducts leakage-free convergent validation against a mining-policy benchmark, and transparently reports a null construct-boundary test against general FDI.

An alternative compact formulation is:

> An author-defined mineral-investment governance-coherence screening layer distinguished by construct separation, WGI uncertainty propagation, leakage-free mining-policy validation, explicit null-result reporting, and reproducible weighting and temporal stress tests.

Do not call it:

- A novel governance construct.
- A novel uncertainty method.
- A novel AHP-TOPSIS architecture.
- A mining-specific dataset, because the WGI inputs are general governance data; the application and external benchmark are mining-focused.
- A pre-specified FDI falsification test.
- A validated adaptive feedback loop.

## 7. Required implementation phase A: correlated WGI error sensitivity

### Goal

Determine whether PCI/RPCI intervals and ranks remain stable when the six WGI measurement errors are positively correlated rather than independent.

### Implementation rules

1. Preserve `audit_artifacts/20260717_six_dimension_robustness_final/` unchanged as the locked independent-error baseline.
2. Prefer a new script, e.g. `audit/run_correlated_wgi_uncertainty.py`, or a backward-compatible extension with explicit scenario arguments.
3. Use the same six official dimension point estimates and standard errors.
4. Use a multivariate normal draw for each country with covariance `D R D`, where `D` is the diagonal matrix of the six published standard errors and `R` is an assumed correlation matrix.
5. Use equicorrelation scenarios `rho = 0.00, 0.25, 0.50, 0.75`. These are sensitivity scenarios, not estimates of the true error covariance.
6. Verify every correlation matrix is positive semidefinite.
7. Use at least 10,000 draws per scenario and a fixed documented seed.
8. Clip simulated WGI scores to `[0, 1]`, consistently with the existing uncertainty engine.
9. Recalculate weighted mean, PCI, RPCI, PCI rank, and RPCI rank for every scenario.
10. Do not infer error covariance from the observed correlation of the WGI scores; observed construct correlation is not measurement-error correlation.

### Required outputs

Create a new dated/versioned artifact directory containing:

- `correlated_error_scenario_summary.csv`
- `correlated_error_country_intervals_2024.csv`
- `correlated_error_rank_intervals_2024.csv`
- `correlated_error_interval_width_ratios.csv`
- `correlated_error_rank_stability.csv`
- `correlated_error_manifest.json`

The summary must compare each positive-correlation scenario with the independent baseline and report:

- Mean and maximum PCI interval-width ratio.
- Mean and maximum RPCI interval-width ratio.
- PCI and RPCI rank Spearman correlations versus `rho=0`.
- Countries whose 95% rank interval changes materially.
- Whether any broad-tier conclusion changes.

### Interpretation rules

- Do not claim positive correlation is the true covariance.
- Do not automatically say independent sampling understates uncertainty. Positive error correlation will often widen mean-based aggregate intervals, but the effect on dispersion-penalized PCI/RPCI must be demonstrated.
- If conclusions are unstable, report instability and reconsider whether the composite belongs in the main text.
- If broad ranks remain stable but intervals widen, retain the composite only as an approximate screening diagnostic and use the widest/plausible scenario in the limitations discussion.

## 8. Required implementation phase B: disaggregated WGI reporting

Produce both machine-readable forms:

1. A wide 2024 table with country, ISO3, all six WGI point scores, standard errors or 90% intervals, PCI/RPCI, and descriptive ranks.
2. A long table with one row per country-dimension, point score, standard error, lower interval, and upper interval.

Suggested filenames:

- `results/tables/table8a_wgi_six_dimensions_2024.csv`
- `results/tables/table8b_governance_coherence_diagnostics_2024.csv`
- `results/tables/supplement_wgi_dimension_intervals_2024_long.csv`

Recommended presentation:

- Put the six-dimension profile table in the main manuscript or make it Table 8A.
- Put PCI/RPCI in Table 8B as supplementary screening diagnostics.
- Do not let a single rank be the only reported evidence.
- Describe overlapping intervals and avoid fine-grained league-table interpretation.

If page width makes one main table unreadable, split it into score and uncertainty panels rather than shrinking it beyond legibility.

## 9. Required implementation phase C: terminology, related work, novelty, and limitations

### Required WGI limitations paragraph

Use this as a working draft and update citations to the manuscript style:

> The World Bank does not publish a single composite across the six WGI dimensions because such an aggregate would be conceptually broad, correlations partly reflect shared source inputs, and aggregate margins of error are difficult to construct. The diagnostics developed here are therefore not presented as official WGI measures or comprehensive representations of governance. They are author-defined screening summaries for examining the level and balance of governance dimensions within the study context. All six dimensions remain reported separately, and any composite results are interpreted alongside dimension profiles, measurement uncertainty, correlated-error sensitivity, and alternative-weight analyses.

### Required FDI wording

Use:

> an explicitly reported falsification or construct-boundary test against general FDI

Do not use:

> a pre-specified falsification test

unless documentary evidence proves it was specified before results were examined. No such evidence currently exists.

### Required PCI/RPCI framing

Consider renaming to reduce confusion with historical claims:

- Governance Coherence Screening Index (`GCSI`).
- Robust Governance Coherence Screening Index (`RGCSI`).

Do not rename silently. If adopted, provide an explicit mapping from historical PCI/RPCI names, update equations and code/table labels consistently, and retain backwards-readable artifact notes.

At minimum, describe PCI/RPCI as author-defined governance-coherence screening diagnostics, never as an official overall governance index.

## 10. Required implementation phase D: report and review package

After phases A-C:

1. Generate a revised supervisor report under a new filename. Do not silently replace the interim report.
2. Include the correlated-error results, six-dimension table, expanded prior-art comparison, revised novelty statement, revised limitations, and remaining author decisions.
3. Render the DOCX through Microsoft Word or the repository document-rendering workflow.
4. Visually inspect every page for clipping, split headings, tiny tables, and missing continuation headers.
5. Generate a new peer-review ZIP with an updated README and manifest.
6. Verify the archive inventory and calculate a SHA256.

Suggested filenames:

- `output/doc/AIML_MRMS_Version_C_Revised_Supervisor_Report.docx`
- `output/peer_review/AIML_MRMS_Version_C_Revised_Peer_Review_Package.zip`

## 11. Required implementation phase E: manuscript update and final audit

Do not begin a blind manuscript rewrite. First identify the author-approved, current manuscript file. Do not assume an old DOCX or generated draft is authoritative.

Once the author/supervisor approves the revised novelty and limitations:

1. Update title/terminology only if required.
2. Rewrite the abstract and contribution statements.
3. Separate country governance from project EV/RC/EI/OF in the conceptual framework.
4. Update the data section with official WGI source/version, coverage, scale, uncertainty, Fraser coverage, and WDI boundary-test data.
5. Add exact equations and define every penalty and weight.
6. Insert the disaggregated WGI and governance-coherence tables.
7. Report the Fraser validation and null general-FDI result.
8. Add the correlated-error, weight, temporal, and construct sensitivity results.
9. Add the WGI non-aggregation caution and mining-risk prior art.
10. Remove feedback, convergence, architecture-superiority, causality, and guaranteed-improvement claims.
11. Update the conclusion so it matches the actual evidence.

Then rerun the full consistency audit:

- Every manuscript number versus the authoritative CSV/JSON output.
- Every table title, unit, year, sample size, and rank.
- Every equation versus code.
- Every dataset name, version, URL, and access statement.
- Every seed, resampling count, validation split, and uncertainty assumption.
- Every terminology occurrence: AI, adaptive, feedback, convergence, PCI/RPCI or GCSI/RGCSI.
- Every citation DOI/URL and bibliographic claim.
- Repository link and reproducibility instructions.
- Abstract, results, discussion, and conclusion consistency.

New prose must be treated as auditable output. Do not assume wording is harmless merely because the numbers are correct.

## 12. Acceptance gates

The continuation is complete only when all gates pass.

### Computational gates

- Correlated-error scenarios run with fixed seed and PASS manifest.
- Independent baseline remains unchanged.
- New run repeated independently; all deterministic outputs match byte-for-byte where expected.
- Six-dimension disaggregated tables contain 16 countries x 6 dimensions with no missing fields.
- Candidate table values trace to authoritative outputs.

### Scientific gates

- No claim of official WGI composite status.
- No claim of novel AHP-TOPSIS or novel uncertainty methodology.
- No use of "pre-specified" for the audit-introduced FDI test.
- No feedback/convergence/superiority/causality claim unsupported by code.
- MineHutte and resource-investment MCDM prior art explicitly located.
- WGI composite caution directly answered.

### Document gates

- Revised novelty and limitations approved by author/supervisor.
- Revised report renders cleanly on every page.
- Full manuscript-versus-repository audit passes.
- Peer-review ZIP inventory and SHA256 validation pass.

## 13. Files that are user-owned or unrelated and must not be swept into commits

The working tree contains pre-existing modified/untracked material. Do not stage, delete, rename, or overwrite it unless the user explicitly places it in scope. Current examples include:

- `results/tables/permutation_test_distribution.csv`
- `results/tables/permutation_test_summary.csv`
- `AIMR_MRML Coding Issue.docx`
- older `audit_artifacts/` runs
- legacy `table8_weighted*.csv` outputs
- miscellaneous scripts under `scripts/`
- current `tmp/` render directories

Always run `git status --short` before and after work. Stage only files created or deliberately modified for the active phase.

## 14. Version-control discipline

1. Stay on `codex/version-c-novelty-extension` unless the user explicitly requests a new branch.
2. Preserve locked artifact directories.
3. Use separate commits for correlated-error computation, disaggregated tables, report/package revision, and manuscript revision.
4. Run syntax checks, analysis manifests, table validation, document rendering, and `git diff --check` before each commit.
5. Never use destructive reset/checkout operations on the dirty working tree.

## 15. Recommended execution order

1. Read this handoff and the interim supervisor report.
2. Inspect the locked code and manifests; do not recompute until inputs and seeds are understood.
3. Implement correlated-error scenarios.
4. Repeat and validate the correlated-error run.
5. Produce disaggregated WGI tables.
6. Update the novelty evidence matrix and related-work references.
7. Draft the revised novelty statement and WGI limitations paragraph.
8. Generate and render the revised supervisor report.
9. Build and validate the revised peer-review ZIP.
10. Obtain author/supervisor approval.
11. Identify and update the authoritative manuscript.
12. Run the complete manuscript-versus-repository audit.
13. Commit only reviewed, scoped files.

## 16. Final instruction to the receiving agents

The objective is not to make Version C look superior. The objective is to make every claim traceable, every limitation explicit, every calculation reproducible, and the contribution narrow enough to survive an informed reviewer. If a new result weakens the argument, report it. Do not repair an inconvenient result by changing labels, weights, proxies, or targets after inspection.
