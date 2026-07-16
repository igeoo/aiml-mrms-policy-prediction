from __future__ import annotations

import numpy as np
import pandas as pd
import unittest

from aiml_mrms.governance_pci import (
    GOVERNANCE_DIMENSIONS,
    compute_governance_pci_table,
    governance_dimension_weights,
    governance_metric_components,
    governance_scoring_criterion_weights,
)
from aiml_mrms.mcdm import weight_evolution
from aiml_mrms.pci import pci, rpci
from aiml_mrms.weighted_pci import weighted_pci, weighted_rpci


def sample_inputs() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "iso3": "AAA",
                "regulatory_quality": 0.8,
                "control_of_corruption": 0.6,
                "fdi_index": 0.2,
                "rule_of_law": 0.7,
                "government_effectiveness": 0.5,
                "political_stability": 0.4,
            }
        ]
    )


class GovernancePciTests(unittest.TestCase):
    def test_governance_projection_excludes_ev_and_sums_to_one(self):
        first = governance_scoring_criterion_weights({"EV": 0.10, "RC": 0.45, "EI": 0.25, "OF": 0.20})
        second = governance_scoring_criterion_weights({"EV": 0.70, "RC": 0.15, "EI": 0.083333333333, "OF": 0.066666666667})
        self.assertTrue(np.isclose(sum(first.values()), 1.0))
        self.assertTrue(np.isclose(sum(second.values()), 1.0))
        self.assertTrue(np.allclose(list(first.values()), list(second.values()), atol=1e-12))

    def test_governance_dimension_weights_sum_to_one(self):
        weights = governance_dimension_weights({"EV": 0.35, "RC": 0.30, "EI": 0.20, "OF": 0.15})
        self.assertEqual(weights.shape, (5,))
        self.assertTrue(np.isclose(weights.sum(), 1.0))

    def test_uniform_five_dimension_reference_matches_original_formula(self):
        values = sample_inputs().loc[0, GOVERNANCE_DIMENSIONS].to_numpy(dtype=float)
        uniform = np.ones(5) / 5
        self.assertTrue(np.isclose(weighted_pci(values, uniform), pci(values), atol=1e-12))
        self.assertTrue(np.isclose(weighted_rpci(values, uniform), rpci(values), atol=1e-12))

    def test_fdi_changes_do_not_change_governance_scores(self):
        data = sample_inputs()
        data_changed = data.copy()
        data_changed["fdi_index"] = 0.99
        ai_signal = {"EV": 0.25, "RC": 0.40, "EI": 0.15, "OF": 0.20}
        evolution = weight_evolution([0.35, 0.30, 0.20, 0.15], list(ai_signal.values()), alpha=0.65, cycles=3)
        first = compute_governance_pci_table(data, evolution, ai_signal)
        second = compute_governance_pci_table(data_changed, evolution, ai_signal)
        self.assertTrue(np.allclose(first["pci"], second["pci"], atol=1e-12))
        self.assertTrue(np.allclose(first["rpci"], second["rpci"], atol=1e-12))
        self.assertFalse(np.allclose(first["fdi_index_context"], second["fdi_index_context"]))

    def test_governance_scoring_does_not_require_fdi(self):
        data = sample_inputs().drop(columns="fdi_index")
        ai_signal = {"EV": 0.25, "RC": 0.40, "EI": 0.15, "OF": 0.20}
        evolution = weight_evolution([0.35, 0.30, 0.20, 0.15], list(ai_signal.values()), alpha=0.65, cycles=3)
        result = compute_governance_pci_table(data, evolution, ai_signal)
        self.assertEqual(len(result), 4)
        self.assertTrue(result["fdi_index_context"].isna().all())

    def test_high_dispersion_can_produce_negative_pci(self):
        values = np.array([1.0, 0.0, 0.0, 0.0, 0.0])
        weights = np.ones(5) / 5
        components = governance_metric_components(values, weights)
        self.assertGreater(components["weighted_cv"], 1.0)
        self.assertLess(components["pci"], 0.0)
        self.assertTrue(
            np.isclose(
                components["pci"],
                components["weighted_mean"] * components["cv_penalty_multiplier"],
                atol=1e-12,
            )
        )

    def test_invalid_inputs_are_rejected(self):
        with self.assertRaises(ValueError):
            governance_scoring_criterion_weights({"EV": 0.5, "RC": -0.1, "EI": 0.3, "OF": 0.3})
        with self.assertRaises(ValueError):
            governance_metric_components([0.1, 0.2, np.nan, 0.4, 0.5], np.ones(5))
        duplicate = pd.concat([sample_inputs(), sample_inputs()], ignore_index=True)
        ai_signal = {"EV": 0.25, "RC": 0.40, "EI": 0.15, "OF": 0.20}
        evolution = weight_evolution([0.35, 0.30, 0.20, 0.15], list(ai_signal.values()), alpha=0.65, cycles=3)
        with self.assertRaises(ValueError):
            compute_governance_pci_table(duplicate, evolution, ai_signal)


if __name__ == "__main__":
    unittest.main()
