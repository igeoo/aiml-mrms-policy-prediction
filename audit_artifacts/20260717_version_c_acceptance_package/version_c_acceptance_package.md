# Version C acceptance package

## Locked conclusion

The historical four-configuration table is not a valid comparison of independently executed architectures. The candidate replacement is an uncertainty-aware six-dimensional governance-coherence analysis.

## Defensible novelty

Construct-separated, uncertainty-aware governance screening for mineral-investment decision support, with mining-specific leakage-free validation, explicit falsification against general FDI, and reproducible temporal/rank/weight stress tests.

## Candidate Table 8

| rank | country | iso3 | pci | pci_measurement_95_ci | pci_rank_measurement_95_interval | rpci | rpci_rank | rpci_measurement_95_ci |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Botswana | BWA | 0.5646 | 0.5246-0.5963 | 1-2 | 0.534 | 1 | 0.4816-0.5686 |
| 2 | Namibia | NAM | 0.5212 | 0.4794-0.5555 | 1-4 | 0.4832 | 3 | 0.4315-0.5252 |
| 3 | Senegal | SEN | 0.5095 | 0.4709-0.5334 | 2-4 | 0.4889 | 2 | 0.4393-0.5177 |
| 4 | Ghana | GHA | 0.4878 | 0.4502-0.5165 | 2-5 | 0.454 | 4 | 0.4076-0.4902 |
| 5 | South Africa | ZAF | 0.4658 | 0.4224-0.4997 | 3-6 | 0.43 | 5 | 0.3783-0.4700 |
| 6 | Morocco | MAR | 0.4279 | 0.3883-0.4567 | 5-8 | 0.3944 | 7 | 0.3469-0.4288 |
| 7 | Tanzania | TZA | 0.4237 | 0.3846-0.4510 | 5-8 | 0.4003 | 6 | 0.3504-0.4329 |
| 8 | Zambia | ZMB | 0.3998 | 0.3610-0.4319 | 6-8 | 0.3641 | 8 | 0.3164-0.4032 |
| 9 | Sierra Leone | SLE | 0.3329 | 0.2940-0.3656 | 9-12 | 0.2945 | 10 | 0.2490-0.3343 |
| 10 | Mauritania | MRT | 0.3309 | 0.2891-0.3648 | 9-12 | 0.2963 | 9 | 0.2470-0.3369 |
| 11 | Mozambique | MOZ | 0.3133 | 0.2715-0.3428 | 9-14 | 0.2909 | 11 | 0.2410-0.3241 |
| 12 | Guinea | GIN | 0.2941 | 0.2555-0.3249 | 10-15 | 0.2625 | 12 | 0.2177-0.2993 |
| 13 | Nigeria | NGA | 0.2906 | 0.2482-0.3241 | 10-15 | 0.2587 | 13 | 0.2101-0.2971 |
| 14 | Zimbabwe | ZWE | 0.2743 | 0.2354-0.3052 | 11-15 | 0.2431 | 14 | 0.1977-0.2797 |
| 15 | Mali | MLI | 0.254 | 0.2079-0.2890 | 12-16 | 0.2234 | 15 | 0.1718-0.2644 |
| 16 | Congo, Dem. Rep. | COD | 0.202 | 0.1602-0.2348 | 15-16 | 0.173 | 16 | 0.1273-0.2099 |

## Candidate Table 9

| evidence_block | test | result | interpretation |
| --- | --- | --- | --- |
| Alternative weighting | PCA absolute-loading weights vs uniform | PCI rho=1.000; RPCI rho=1.000; mean \|PCI diff\|=0.0010 | Rank ordering is highly stable; uniform weighting remains the transparent primary specification. |
| Alternative weighting | Entropy weights vs uniform | PCI rho=0.994; RPCI rho=0.994; mean \|PCI diff\|=0.0171 | Rank ordering is highly stable; uniform weighting remains the transparent primary specification. |
| Alternative weighting | Fraser-correlation weights vs uniform | PCI rho=1.000; RPCI rho=1.000; mean \|PCI diff\|=0.0012 | Rank ordering is highly stable; uniform weighting remains the transparent primary specification. |
| Weight uncertainty | 10,000 Dirichlet weight perturbations | PCI rank rho median=0.997 (2.5%=0.991); RPCI median=0.994 (2.5%=0.988) | Rank conclusions are robust to broad symmetric weight perturbation. |
| Mining convergent validity | WGI governance mean vs Fraser PPI, 2019-2024 | Spearman rho=0.715; country-cluster bootstrap 95% CI 0.437-0.848; n=70, 14 countries | Strong association with a mining-specific policy-perception benchmark; not causal validation. |
| Mining out-of-country validation | Nested leave-one-country-out Ridge prediction of Fraser PPI | R2=0.336; MAE=15.70; Spearman rho=0.602 | Moderate out-of-country generalisation; coefficients are not used as primary weights because dimensions are collinear. |
| Falsification / discriminant boundary | Governance plus controls vs controls for next-year general FDI | Incremental MAE improvement=-0.0067; country-cluster bootstrap 95% CI -0.0301 to 0.0160; P(improvement)=0.291 | No reliable predictive gain. General FDI is rejected as the success target for this governance layer. |
| Construct diagnostics | Six WGI dimensions, pooled 2002-2024 | Cronbach alpha=0.969; PC1=0.886; max VIF=23.12 | Strong shared governance signal and high collinearity; this supports parsimonious aggregation but not unidimensionality or causal attribution. |

## Novelty evidence matrix

| area | source | prior_art | boundary | url |
| --- | --- | --- | --- | --- |
| Composite indicators | OECD, European Union and EC-JRC (2008), Handbook on Constructing Composite Indicators | Weighting, aggregation, uncertainty and sensitivity analysis for country rankings are established practice. | Monte Carlo analysis alone is not the paper's novelty. | https://doi.org/10.1787/9789264043466-en |
| Governance measurement | Kaufmann and Kraay (2024), The Worldwide Governance Indicators: Methodology and 2024 Update | The WGI already estimate six governance dimensions and report measurement uncertainty. | The proposed PCI/RPCI aggregate is an author-defined analytical layer, not an official World Bank index. | https://doi.org/10.1596/1813-9450-10952 |
| Revised WGI data | World Bank (2025), Worldwide Governance Indicators documentation and revised methodology | The official series supplies six 0-100 dimension scores, standard errors and confidence intervals. | Short-run changes and overlapping intervals must not be over-interpreted. | https://www.worldbank.org/en/publication/worldwide-governance-indicators/documentation |
| Mining policy benchmark | Fraser Institute (2023/2024), Annual Survey of Mining Companies | PPI is an established perception-based mining-policy benchmark. | PPI is used only for convergent validation, never as both a feature and target. | https://www.fraserinstitute.org/studies/annual-survey-of-mining-companies-2023 |
| Mining ranking limitations | The perils of ranking mining countries and regions (Mineral Economics, 2024) | Mining jurisdiction rankings can obscure survey uncertainty and contested policy concepts. | Results are screening evidence, not precise prescriptions or causal effects. | https://doi.org/10.1007/s13563-023-00405-y |
| Governance in mining risk | Kuehnel et al. (2023), Correlation analysis of country governance indicators and mining incidents | Country governance indicators have been tested in mining contexts and can fail for specific outcomes. | Construct validity is outcome-specific; the paper reports its failed general-FDI test. | https://doi.org/10.1016/j.resourpol.2023.103762 |
| Mining MCDM | Support of mining investment choice decisions with the use of multi-criteria method | AHP-based mining investment choice is established. | AHP or TOPSIS alone cannot be claimed as novel. | https://www.sciencedirect.com/science/article/abs/pii/S0301420716303348 |
| Strategic-mineral indicators | Synthesized indicator for evaluating security of strategic minerals: lithium case study (2020) | WGI and Fraser PPI have already appeared in composite mineral-security indicators. | The contribution must be the validated integration and uncertainty discipline, not merely data-source combination. | https://www.sciencedirect.com/science/article/pii/S0301420720309466 |
