import numpy as np
import pandas as pd
from scipy.optimize import linprog

def solve_allocation(project_df, lambda_penalty=0.15, budget=1.0, e_max=0.35, p_max=0.35):
    df = project_df.copy()
    returns = df["topsis_closeness"].to_numpy(dtype=float) * 100
    penalties = df["regulatory_penalty"].to_numpy(dtype=float)
    c = -(returns - lambda_penalty * penalties * 100)
    A_ub = [
        np.ones(len(df)),
        df["environmental_impact"].to_numpy(dtype=float),
        df["regulatory_penalty"].to_numpy(dtype=float),
    ]
    b_ub = [budget, e_max, p_max]
    res = linprog(c=c, A_ub=A_ub, b_ub=b_ub, bounds=[(0, 1)] * len(df), method="highs")
    out = df[["country_iso3", "project_id", "project_name"]].copy()
    out["lambda"] = lambda_penalty
    if res.success:
        out["allocation"] = res.x
        out["objective_value"] = -res.fun
        out["optimisation_status"] = "optimal"
    else:
        out["allocation"] = np.nan
        out["objective_value"] = np.nan
        out["optimisation_status"] = res.message
    return out

def solve_by_country(topsis_df, cycle=3, lambda_penalty=0.15):
    outputs = []
    selected = topsis_df[topsis_df["cycle"] == cycle]
    for iso, sub in selected.groupby("country_iso3"):
        outputs.append(solve_allocation(sub, lambda_penalty=lambda_penalty))
    return pd.concat(outputs, ignore_index=True)
