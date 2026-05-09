import numpy as np
import pandas as pd

CRITERIA = ["EV", "RC", "EI", "OF"]

def adaptive_weight_update(previous_weights, svm_signal, alpha=0.65):
    prev = np.asarray(previous_weights, dtype=float)
    sig = np.asarray(svm_signal, dtype=float)
    prev = prev / prev.sum()
    sig = sig / sig.sum()
    return alpha * prev + (1 - alpha) * sig

def weight_evolution(base_weights, svm_signal, alpha=0.65, cycles=3):
    weights = [np.asarray(base_weights, dtype=float)]
    for _ in range(1, cycles):
        weights.append(adaptive_weight_update(weights[-1], svm_signal, alpha))
    return pd.DataFrame(weights, columns=CRITERIA).assign(cycle=range(1, cycles + 1))[["cycle"] + CRITERIA]

def topsis(df, weights, criteria=CRITERIA):
    X = df[criteria].astype(float).to_numpy()
    R = X / np.sqrt((X ** 2).sum(axis=0))
    w = np.asarray(weights, dtype=float)
    w = w / w.sum()
    V = R * w
    best = V.max(axis=0)
    worst = V.min(axis=0)
    d_plus = np.sqrt(((V - best) ** 2).sum(axis=1))
    d_minus = np.sqrt(((V - worst) ** 2).sum(axis=1))
    closeness = d_minus / (d_plus + d_minus + 1e-12)
    out = df.copy()
    out["topsis_closeness"] = closeness
    out["rank"] = out.groupby("country_iso3")["topsis_closeness"].rank(ascending=False, method="dense").astype(int)
    return out.sort_values(["country_iso3", "rank", "project_id"])

def run_country_topsis(project_df, weights_by_cycle):
    outputs = []
    for _, row in weights_by_cycle.iterrows():
        for iso, sub in project_df.groupby("country_iso3"):
            res = topsis(sub, row[CRITERIA].to_numpy(dtype=float))
            res["cycle"] = int(row["cycle"])
            outputs.append(res)
    return pd.concat(outputs, ignore_index=True)
