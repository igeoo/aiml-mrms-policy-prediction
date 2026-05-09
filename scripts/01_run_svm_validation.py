import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import argparse
import pandas as pd
from aiml_mrms.data_utils import load_feature_matrix, ensure_results_dirs
from aiml_mrms.svm_validation import svm_metrics, permutation_test_loo_accuracy, linear_svc_feature_weights, alternative_classifier_weights

parser = argparse.ArgumentParser()
parser.add_argument("--permutations", type=int, default=1000)
args = parser.parse_args()

tables_dir, _ = ensure_results_dirs()
df, X, y = load_feature_matrix()

metrics, y_pred, y_score = svm_metrics(X, y)
pd.DataFrame([{k: v for k, v in metrics.items() if k != "confusion_matrix"}]).to_csv(tables_dir / "table5_svm_loo_metrics.csv", index=False)
pd.DataFrame(metrics["confusion_matrix"]).to_csv(tables_dir / "table5_confusion_matrix.csv", index=False)

preds = df[["country", "iso3", "label"]].copy()
preds["predicted_label"] = ["Favourable" if p == 1 else "Unfavourable" for p in y_pred]
preds["svm_score"] = y_score
preds.to_csv(tables_dir / "svm_loo_predictions.csv", index=False)

perm_summary, perm_accs = permutation_test_loo_accuracy(X, y, n_permutations=args.permutations, random_state=42)
pd.DataFrame([perm_summary]).to_csv(tables_dir / "permutation_test_summary.csv", index=False)
pd.DataFrame({"permuted_accuracy": perm_accs}).to_csv(tables_dir / "permutation_test_distribution.csv", index=False)

feature_weights, criterion_weights = linear_svc_feature_weights(X, y, C=metrics["modal_C"])
feature_weights.to_csv(tables_dir / "table6_svm_feature_weights.csv", index=False)
criterion_weights.to_csv(tables_dir / "table6_aggregated_criterion_weights.csv", index=False)

alt_feature, alt_agg = alternative_classifier_weights(X, y)
alt_feature.to_csv(tables_dir / "alternative_classifier_feature_weights.csv", index=False)
alt_agg.to_csv(tables_dir / "alternative_classifier_criterion_weights.csv", index=False)

print("SVM validation complete.")
