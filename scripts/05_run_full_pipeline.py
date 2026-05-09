import sys
import argparse
import subprocess
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from aiml_mrms.data_utils import load_feature_matrix, load_project_scores, ensure_results_dirs
from aiml_mrms.svm_validation import linear_svc_feature_weights
from aiml_mrms.mcdm import weight_evolution
from aiml_mrms.sensitivity import alpha_sweep, lambda_sweep

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("--permutations", type=int, default=1000)
    args = parser.parse_args()

    # Step 1-4: Run sub-scripts via subprocess for isolated execution
    print("Executing sub-pipelines 01-04...")
    scripts = [
        ["01_run_svm_validation.py", "--permutations", str(args.permutations)],
        ["02_run_mcdm_topsis.py"],
        ["03_run_pci_rpci.py"],
        ["04_run_investment_optimisation.py"]
    ]
    
    for s in scripts:
        subprocess.check_call([sys.executable, str(ROOT / "scripts" / s[0])] + s[1:])

    # Step 5: Sensitivity Analysis and final reporting
    print("Executing final sensitivity analysis...")
    tables_dir, _ = ensure_results_dirs()
    _, X, y = load_feature_matrix()
    projects = load_project_scores()
    
    # Load modal_C from results to ensure consistency with script 01
    metrics_path = tables_dir / "table5_svm_loo_metrics.csv"
    if metrics_path.exists():
        modal_c = pd.read_csv(metrics_path)["modal_C"].iloc[0]
    else:
        modal_c = 1.0 # Fallback
        
    _, crit = linear_svc_feature_weights(X, y, C=modal_c)
    signal = crit.set_index("criterion").loc[["EV","RC","EI","OF"], "svm_signal"].to_numpy()
    base_weights = [0.350, 0.300, 0.200, 0.150]
    
    alpha_sweep(base_weights, signal).to_csv(tables_dir / "table9b_alpha_sensitivity.csv", index=False)
    weights = weight_evolution(base_weights, signal, alpha=0.65, cycles=3)
    lambda_sweep(projects, weights).to_csv(tables_dir / "table9c_lambda_sensitivity.csv", index=False)
    
    print("Full AIML-MRMS pipeline complete. Outputs written to results/tables/.")

if __name__ == "__main__":
    run()

