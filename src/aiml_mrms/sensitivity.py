import pandas as pd
from .mcdm import weight_evolution, run_country_topsis
from .investment import solve_by_country

def alpha_sweep(base_weights, svm_signal, alphas=(0.10,0.30,0.50,0.65,0.80,0.90,0.99), cycles=3):
    rows = []
    for alpha in alphas:
        evo = weight_evolution(base_weights, svm_signal, alpha=alpha, cycles=cycles)
        last = evo[evo["cycle"] == cycles].iloc[0]
        rows.append({"alpha": alpha, "cycle": cycles, "EV": last["EV"], "RC": last["RC"], "EI": last["EI"], "OF": last["OF"]})
    return pd.DataFrame(rows)

def lambda_sweep(project_df, weights_by_cycle, lambdas=(0.05,0.10,0.15,0.20,0.25), cycle=3):
    topsis_df = run_country_topsis(project_df, weights_by_cycle)
    outputs = []
    for lam in lambdas:
        out = solve_by_country(topsis_df, cycle=cycle, lambda_penalty=lam)
        out["lambda"] = lam
        outputs.append(out)
    return pd.concat(outputs, ignore_index=True)
