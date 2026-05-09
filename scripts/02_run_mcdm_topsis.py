import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from aiml_mrms.data_utils import load_feature_matrix, load_project_scores, ensure_results_dirs
from aiml_mrms.svm_validation import linear_svc_feature_weights
from aiml_mrms.mcdm import weight_evolution, run_country_topsis

tables_dir, _ = ensure_results_dirs()
_, X, y = load_feature_matrix()
projects = load_project_scores()
_, crit = linear_svc_feature_weights(X, y, C=1.0)
signal = crit.set_index("criterion").loc[["EV","RC","EI","OF"], "svm_signal"].to_numpy()
weights = weight_evolution([0.350, 0.300, 0.200, 0.150], signal, alpha=0.65, cycles=3)
weights.to_csv(tables_dir / "adaptive_weight_evolution_alpha_065.csv", index=False)
topsis = run_country_topsis(projects, weights)
topsis.to_csv(tables_dir / "table7_topsis_results.csv", index=False)
print("MCDM/TOPSIS complete.")
