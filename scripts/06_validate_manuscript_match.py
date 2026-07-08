import os
import sys
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from aiml_mrms.data_utils import ensure_results_dirs

def validate():
    tables_dir, _ = ensure_results_dirs()
    report_lines = []
    
    report_lines.append("=======================================================================")
    report_lines.append("              AIML-MRMS Manuscript Validation Report")
    report_lines.append("=======================================================================\n")
    
    # 1. Validate Table 5 (SVM LOO-CV metrics)
    report_lines.append("--- 1. Table 5: SVM LOO-CV Metrics ---")
    metrics_path = tables_dir / "table5_svm_loo_metrics.csv"
    if metrics_path.exists():
        metrics = pd.read_csv(metrics_path).iloc[0].to_dict()
        report_lines.append(f"  Accuracy (Manuscript: 0.938, Computed: {metrics['accuracy']:.3f})")
        report_lines.append(f"  Balanced Accuracy (Manuscript: 0.955, Computed: {metrics['balanced_accuracy']:.3f})")
        report_lines.append(f"  F1-score (Manuscript: 0.909, Computed: {metrics['f1']:.3f})")
        report_lines.append(f"  ROC-AUC (Manuscript: 0.945, Computed: {metrics['roc_auc']:.3f})")
    else:
        report_lines.append("  [ERROR] table5_svm_loo_metrics.csv not found.")
    report_lines.append("")

    # 2. Validate Table 6 (Feature Weights)
    report_lines.append("--- 2. Table 6: SVM Feature Weights ---")
    weights_path = tables_dir / "table6_svm_feature_weights.csv"
    manuscript_weights = {
        "control_of_corruption": 0.0215,
        "government_effectiveness": 0.1820,
        "fraser_ppi": 0.2267,
        "rule_of_law": 0.2547,
        "regulatory_quality": 0.2887,
        "political_stability": 0.0264
    }
    if weights_path.exists():
        weights_df = pd.read_csv(weights_path).set_index("feature")
        for feat, m_val in manuscript_weights.items():
            comp_val = weights_df.loc[feat, "normalised_weight"]
            diff = comp_val - m_val
            report_lines.append(f"  {feat:25s} | Manuscript: {m_val:.4f} | Computed: {comp_val:.4f} | Diff: {diff:+.4f}")
    else:
        report_lines.append("  [ERROR] table6_svm_feature_weights.csv not found.")
    report_lines.append("")

    # 3. Validate Table 7 (TOPSIS Closeness)
    report_lines.append("--- 3. Table 7: TOPSIS Closeness Coefficients (C_i) ---")
    topsis_path = tables_dir / "table7_topsis_results.csv"
    # Manuscript values for C1 and C3
    manuscript_topsis = {
        ("NGA", "NG-A", 1): 0.392, ("NGA", "NG-A", 3): 0.425,
        ("NGA", "NG-B", 1): 0.716, ("NGA", "NG-B", 3): 0.832,
        ("NGA", "NG-C", 1): 0.284, ("NGA", "NG-C", 3): 0.168,
        ("ZAF", "ZA-A", 1): 0.475, ("ZAF", "ZA-A", 3): 0.508,
        ("ZAF", "ZA-B", 1): 0.734, ("ZAF", "ZA-B", 3): 0.844,
        ("ZAF", "ZA-C", 1): 0.214, ("ZAF", "ZA-C", 3): 0.123,
    }
    if topsis_path.exists():
        topsis_df = pd.read_csv(topsis_path)
        for (iso, proj, cycle), m_val in manuscript_topsis.items():
            row = topsis_df[(topsis_df["country_iso3"] == iso) & (topsis_df["project_id"] == proj) & (topsis_df["cycle"] == cycle)]
            if not row.empty:
                comp_val = row.iloc[0]["topsis_closeness"]
                diff = comp_val - m_val
                report_lines.append(f"  {iso} {proj} (Cycle {cycle}) | Manuscript: {m_val:.3f} | Computed: {comp_val:.3f} | Diff: {diff:+.3f}")
            else:
                report_lines.append(f"  [ERROR] No data found for {iso} {proj} (Cycle {cycle})")
    else:
        report_lines.append("  [ERROR] table7_topsis_results.csv not found.")
    report_lines.append("")

    # 4. Validate Table 8 (Baseline PCI/RPCI diagnostics)
    report_lines.append("--- 4. Table 8: Baseline PCI/RPCI Diagnostics ---")
    pci_rpci_path = tables_dir / "baseline_pci_rpci.csv"
    manuscript_pci_rpci = {
        "BWA": (0.847, 0.403, 0.150, 0.505, 0.429),
        "COD": (0.065, 1.352, 0.662, -0.023, -0.008),
        "NGA": (0.196, 0.414, 0.224, 0.115, 0.089),
        "ZAF": (0.742, 0.214, 0.121, 0.583, 0.513)
    }
    if pci_rpci_path.exists():
        pci_rpci_df = pd.read_csv(pci_rpci_path)
        for iso, (m_mean, m_cv, m_gini, m_pci, m_rpci) in manuscript_pci_rpci.items():
            row = pci_rpci_df[pci_rpci_df["iso3"] == iso]
            if not row.empty:
                comp_mean = row.iloc[0]["mean_score"]
                comp_cv = row.iloc[0]["cv"]
                comp_gini = row.iloc[0]["gini"]
                comp_pci = row.iloc[0]["pci"]
                comp_rpci = row.iloc[0]["rpci"]
                
                report_lines.append(f"  {iso} | Mean: Manuscript: {m_mean:.3f}, Computed: {comp_mean:.3f}, Diff: {comp_mean - m_mean:+.3f}")
                report_lines.append(f"      CV:   Manuscript: {m_cv:.3f}, Computed: {comp_cv:.3f}, Diff: {comp_cv - m_cv:+.3f}")
                report_lines.append(f"      Gini: Manuscript: {m_gini:.3f}, Computed: {comp_gini:.3f}, Diff: {comp_gini - m_gini:+.3f}")
                report_lines.append(f"      PCI:  Manuscript: {m_pci:.3f}, Computed: {comp_pci:.3f}, Diff: {comp_pci - m_pci:+.3f}")
                report_lines.append(f"      RPCI: Manuscript: {m_rpci:.3f}, Computed: {comp_rpci:.3f}, Diff: {comp_rpci - m_rpci:+.3f}")
            else:
                report_lines.append(f"  [ERROR] No baseline data found for {iso}")
    else:
        report_lines.append("  [ERROR] baseline_pci_rpci.csv not found.")
    report_lines.append("")

    report_text = "\n".join(report_lines)
    print(report_text)
    
    report_out = tables_dir / "manuscript_validation_report.txt"
    with open(report_out, "w", encoding="utf-8") as f:
        f.write(report_text)
    print(f"Validation complete. Report written to {report_out}")

if __name__ == "__main__":
    validate()
