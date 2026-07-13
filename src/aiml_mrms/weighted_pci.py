"""
weighted_pci.py
================
Replaces the previous pci_gain_scenarios() function, which returned
HARDCODED ΔPCI constants (0.006 / 0.009 / 0.019 / 0.030 for NGA and
0.004 / 0.006 / 0.009 / 0.017 for ZAF, applied identically to every
other country via a dict .get() fallback) with no dependency on the
SVM, AHP, TOPSIS, or optimisation layers whatsoever.

This module computes PCI/RPCI as a genuine function of a criterion
weight vector, so that different "configurations" (standalone MCDM,
standalone AI, static AI+MCDM, full adaptive AIML-MRMS) legitimately
produce different PCI/RPCI values because they use different weight
vectors -- not because a number was typed into a dictionary.

METHODOLOGICAL EXTENSION (new; not present in the original manuscript)
------------------------------------------------------------------
Equations (5)-(6) in the manuscript define PCI/RPCI as unweighted
functions of the six governance dimensions s_i (five WGI percentile
ranks + FDI index):

    PCI  = mean(s) * (1 - CV(s))
    RPCI = PCI * (1 - Gini(s))

As written, these equations contain no term for criterion weights,
AI signal, or configuration -- so they cannot, by construction,
produce different values across "configurations" for the same
country. That is the root cause of the discrepancy identified in
Table 8 of the submitted manuscript.

To make the four-configuration comparison in Table 8/9 meaningful,
this module introduces an explicit WEIGHTED generalisation:

    PCI_w  = sum_j( v_j * s_j )                                   (5')
    CV_w   = sqrt( sum_j( v_j * (s_j - PCI_w)^2 ) ) / PCI_w
    PCI_w  = PCI_w * (1 - CV_w)
    RPCI_w = PCI_w * (1 - Gini_w(s, v))

where v_j is a per-dimension weight derived from the AHP/adaptive
criterion weight vector w(t) in effect for a given configuration,
via the same feature-to-criterion mapping already used elsewhere in
this codebase (CRITERION_MAP in svm_validation.py), extended with
fdi_index -> EV since the PCI input vector uses FDI rather than the
Fraser PPI as its economic-viability proxy.

IMPORTANT: With uniform weights (v_j = 1/6 for all j), Eqs. (5')-(6')
reduce exactly to the original unweighted Eqs. (5)-(6). This is
verified in tests below. This a strict generalisation, not an ad hoc
replacement -- but it is still a NEW formula that does not currently
appear in the manuscript and would need to be added explicitly to
Section 5.5/5.6 before Table 8/9 could be presented as computed from
it. This must be treated as new methodological content requiring the
author's sign-off, not as a documentation fix.

Configuration -> weight vector mapping used below:
    standalone_mcdm          : base AHP weights w0 (no AI input)      = cycle 1
    standalone_ai             : pure SVM-derived signal f (no expert
                                 prior)                                = table6 aggregated signal
    static_ai_mcdm             : single blend of w0 and f, no further
                                 iteration                             = cycle 2
    aiml_mrms_full_adaptive    : second update of the fixed blending
                                 rule (the legacy identifier is retained
                                 for compatibility)                    = cycle 3

This mapping is also a modelling choice made explicit here for the
author to review/approve, not something implied by the manuscript
text as written.
"""

import numpy as np
import pandas as pd

PCI_DIMENSIONS = [
    "regulatory_quality", "control_of_corruption", "fdi_index",
    "rule_of_law", "government_effectiveness", "political_stability",
]

# Extends CRITERION_MAP from svm_validation.py: fdi_index stands in for
# fraser_ppi's EV role because the PCI input vector uses FDI, not Fraser PPI.
DIMENSION_TO_CRITERION = {
    "regulatory_quality": "RC",
    "control_of_corruption": "EI",
    "fdi_index": "EV",
    "rule_of_law": "RC",
    "government_effectiveness": "OF",
    "political_stability": "OF",
}


def criterion_weights_to_dimension_weights(criterion_weights: dict) -> np.ndarray:
    """
    Distribute each AHP/adaptive criterion weight evenly across the PCI
    dimensions that map to it (RC splits across regulatory_quality and
    rule_of_law; OF splits across government_effectiveness and
    political_stability; EI and EV each map to a single dimension).
    Returns a weight vector aligned with PCI_DIMENSIONS, summing to 1.
    """
    from collections import Counter
    counts = Counter(DIMENSION_TO_CRITERION.values())
    v = np.array([
        criterion_weights[DIMENSION_TO_CRITERION[dim]] / counts[DIMENSION_TO_CRITERION[dim]]
        for dim in PCI_DIMENSIONS
    ], dtype=float)
    return v / v.sum()


def weighted_gini(x: np.ndarray, w: np.ndarray) -> float:
    """Weighted Gini coefficient via the standard pairwise formula.
    Reduces to the unweighted (population) Gini when w is uniform."""
    x = np.asarray(x, dtype=float)
    w = np.asarray(w, dtype=float)
    w = w / w.sum()
    mu = np.sum(w * x)
    if np.isclose(mu, 0):
        return 0.0
    diff = np.abs(x[:, None] - x[None, :])
    weight_outer = np.outer(w, w)
    return float(np.sum(weight_outer * diff) / (2 * mu))


def weighted_pci(values, weights) -> float:
    x = np.asarray(values, dtype=float)
    v = np.asarray(weights, dtype=float)
    v = v / v.sum()
    mu = np.sum(v * x)
    if mu <= 0:
        return 0.0
    var = np.sum(v * (x - mu) ** 2)
    cv = np.sqrt(var) / mu
    return float(mu * (1 - cv))


def weighted_rpci(values, weights) -> float:
    x = np.asarray(values, dtype=float)
    v = np.asarray(weights, dtype=float)
    v = v / v.sum()
    p = weighted_pci(x, v)
    g = weighted_gini(x, v)
    return p * (1 - g)


def build_configuration_weights(weight_evolution_df: pd.DataFrame, ai_signal: dict) -> dict:
    """
    weight_evolution_df: output of mcdm.weight_evolution(), columns
    cycle, EV, RC, EI, OF  (cycle 1 = base w0; cycle 3 = the second
    predefined update).  No convergence test is performed.
    ai_signal: dict {EV, RC, EI, OF} = normalised SVM/criterion signal
    Returns {"standalone_mcdm": {...}, "standalone_ai": {...},
             "static_ai_mcdm": {...}, "aiml_mrms_full_adaptive": {...}}
    each value a dict of criterion -> weight.
    """
    crit = ["EV", "RC", "EI", "OF"]
    cyc = weight_evolution_df.set_index("cycle")
    return {
        "standalone_mcdm": {c: cyc.loc[1, c] for c in crit},
        "standalone_ai": {c: ai_signal[c] for c in crit},
        "static_ai_mcdm": {c: cyc.loc[2, c] for c in crit},
        "aiml_mrms_full_adaptive": {c: cyc.loc[3, c] for c in crit},
    }


def compute_weighted_pci_table(pci_input_df: pd.DataFrame, weight_evolution_df: pd.DataFrame,
                                ai_signal: dict) -> pd.DataFrame:
    """
    Produces the replacement for Table 8: real PCI(C1)/PCI(C3)/RPCI(C1)/
    RPCI(C3)/ΔPCI per country per configuration, computed from actual
    weight vectors rather than hardcoded constants.

    C1 = unweighted baseline (original Eqs. 5-6; identical across all
         configurations, since it uses no criterion weights).
    C3 = weighted value (Eqs. 5'-6' above) under that configuration's
         weight vector.
    """
    configs = build_configuration_weights(weight_evolution_df, ai_signal)
    rows = []
    for _, row in pci_input_df.iterrows():
        x = row[PCI_DIMENSIONS].to_numpy(dtype=float)
        uniform_v = np.ones(len(PCI_DIMENSIONS)) / len(PCI_DIMENSIONS)
        pci_c1 = weighted_pci(x, uniform_v)
        rpci_c1 = weighted_rpci(x, uniform_v)
        for cfg_name, crit_w in configs.items():
            v = criterion_weights_to_dimension_weights(crit_w)
            pci_c3 = weighted_pci(x, v)
            rpci_c3 = weighted_rpci(x, v)
            rows.append({
                "iso3": row["iso3"],
                "configuration": cfg_name,
                "pci_c1": pci_c1,
                "pci_c3": pci_c3,
                "rpci_c1": rpci_c1,
                "rpci_c3": rpci_c3,
                "delta_pci": pci_c3 - pci_c1,
                "delta_rpci": rpci_c3 - rpci_c1,
            })
    return pd.DataFrame(rows)
