# Data dictionary

## feature_matrix_normalised.csv
| Column | Meaning | Scale |
|---|---|---|
| country | Country name | text |
| iso3 | ISO-3 country code | text |
| rule_of_law | WGI Rule of Law percentile rank | [0,1] |
| regulatory_quality | WGI Regulatory Quality percentile rank | [0,1] |
| government_effectiveness | WGI Government Effectiveness percentile rank | [0,1] |
| control_of_corruption | WGI Control of Corruption percentile rank | [0,1] |
| political_stability | WGI Political Stability percentile rank | [0,1] |
| fraser_ppi | Fraser PPI / investment-attractiveness proxy | [0,1] |
| label | Investment label | Favourable/Unfavourable |

## project_scores.csv
EV = Economic Viability; RC = Regulatory Compliance; EI = ESG/Environmental Index; OF = Operational Feasibility.

## pci_input_vectors.csv
Country-level dimensional vectors used for PCI/RPCI computation.
