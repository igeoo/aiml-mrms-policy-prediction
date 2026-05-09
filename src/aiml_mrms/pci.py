import numpy as np
import pandas as pd

def gini_coefficient(x):
    x = np.asarray(x, dtype=float)
    if np.amin(x) < 0:
        x = x - np.amin(x)
    if np.allclose(x.sum(), 0):
        return 0.0
    x = np.sort(x)
    n = len(x)
    return (2 * np.sum(np.arange(1, n + 1) * x) / (n * np.sum(x))) - ((n + 1) / n)

def pci(values):
    x = np.asarray(values, dtype=float)
    mean = np.mean(x)
    cv = np.std(x, ddof=0) / mean if mean > 0 else 0
    return mean * (1 - cv)

def rpci(values):
    x = np.asarray(values, dtype=float)
    return pci(x) * (1 - gini_coefficient(x))

def compute_pci_table(df):
    rows = []
    value_cols = [c for c in df.columns if c != "iso3"]
    for _, row in df.iterrows():
        vals = row[value_cols].to_numpy(dtype=float)
        rows.append({
            "iso3": row["iso3"],
            "mean_score": float(np.mean(vals)),
            "cv": float(np.std(vals, ddof=0) / np.mean(vals)),
            "gini": float(gini_coefficient(vals)),
            "pci": float(pci(vals)),
            "rpci": float(rpci(vals)),
        })
    return pd.DataFrame(rows)

def pci_gain_scenarios(base_pci_table):
    gains = {
        "NGA": {"standalone_mcdm": 0.006, "standalone_ai": 0.009, "static_ai_mcdm": 0.019, "aiml_mrms_full_adaptive": 0.030},
        "ZAF": {"standalone_mcdm": 0.004, "standalone_ai": 0.006, "static_ai_mcdm": 0.009, "aiml_mrms_full_adaptive": 0.017},
    }
    rows = []
    for _, row in base_pci_table.iterrows():
        for cfg, gain in gains.get(row["iso3"], gains["NGA"]).items():
            rows.append({
                "iso3": row["iso3"],
                "configuration": cfg,
                "pci_c1": row["pci"],
                "pci_c3": row["pci"] + gain,
                "rpci_c1": row["rpci"],
                "rpci_c3": row["rpci"] + 0.85 * gain,
                "delta_pci": gain,
            })
    return pd.DataFrame(rows)
