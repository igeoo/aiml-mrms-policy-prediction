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
        report_lines.append(f"  Accuracy (Manuscript: 1.000, Computed: {metrics['accuracy']:.3f})")
        report_lines.append(f"  Balanced Accuracy (Manuscript: 1.000, Computed: {metrics['balanced_accuracy']:.3f})")
        report_lines.append(f"  F1-score (Manuscript: 1.000, Computed: {metrics['f1']:.3f})")
        report_lines.append(f"  ROC-AUC (Manuscript: 0.727, Computed: {metrics['roc_auc']:.3f}) - [NOTE: Code achieves perfect separation, resulting in 1.000]")
    else:
        report_lines.append("  [ERROR] table5_svm_loo_metrics.csv not found.")
    report_lines.append("")

    # 2. Validate Table 6 (Feature Weights)
    report_lines.append("--- 2. Table 6: SVM Feature Weights ---")
    weights_path = tables_dir / "table6_svm_feature_weights.csv"
    manuscript_weights = {
        "control_of_corruption": 0.1982,
        "government_effectiveness": 0.1971,
        "fraser_ppi": 0.1745,
        "rule_of_law": 0.1504,
        "regulatory_quality": 0.1471,
        "political_stability": 0.1328
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
        ("NGA", "NG-A", 1): 0.393, ("NGA", "NG-A", 3): 0.388,
        ("NGA", "NG-B", 1): 0.716, ("NGA", "NG-B", 3): 0.751,
        ("NGA", "NG-C", 1): 0.284, ("NGA", "NG-C", 3): 0.249,
        ("ZAF", "ZA-A", 1): 0.475, ("ZAF", "ZA-A", 3): 0.414,
        ("ZAF", "ZA-B", 1): 0.734, ("ZAF", "ZA-B", 3): 0.768,
        ("ZAF", "ZA-C", 1): 0.215, ("ZAF", "ZA-C", 3): 0.242,
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

    # 4. Validate Table 8 (PCI/RPCI scenarios)
    report_lines.append("--- 4. Table 8: PCI/RPCI Scenarios (Cycle 3 vs Baseline Cycle 1) ---")
    scenarios_path = tables_dir / "table8_pci_rpci_scenarios.csv"
    # Manuscript values for C3 configuration PCI/RPCI and delta
    # configurations map to scenario names:
    cfg_map = {
        "standalone_mcdm": "Standalone MCDM",
        "standalone_ai": "Standalone AI",
        "static_ai_mcdm": "Static AI+MCDM (no feedback)",
        "aiml_mrms_full_adaptive": "AIML-MRMS (full adaptive)"
    }
    manuscript_scenarios = {
        ("NGA", "standalone_mcdm"): (0.090, 0.064, 0.006),
        ("NGA", "standalone_ai"): (0.092, 0.066, 0.009),
        ("NGA", "static_ai_mcdm"): (0.102, 0.075, 0.019),
        ("NGA", "aiml_mrms_full_adaptive"): (0.113, 0.084, 0.030),
        ("ZAF", "standalone_mcdm"): (0.534, 0.514, 0.004),
        ("ZAF", "standalone_ai"): (0.536, 0.516, 0.006),
        ("ZAF", "static_ai_mcdm"): (0.539, 0.519, 0.009),
        ("ZAF", "aiml_mrms_full_adaptive"): (0.547, 0.527, 0.017),
    }
    if scenarios_path.exists():
        scenarios_df = pd.read_csv(scenarios_path)
        for (iso, cfg), (m_pci_c3, m_rpci_c3, m_delta) in manuscript_scenarios.items():
            row = scenarios_df[(scenarios_df["iso3"] == iso) & (scenarios_df["configuration"] == cfg)]
            if not row.empty:
                comp_pci = row.iloc[0]["pci_c3"]
                comp_rpci = row.iloc[0]["rpci_c3"]
                comp_delta = row.iloc[0]["delta_pci"]
                
                diff_pci = comp_pci - m_pci_c3
                diff_rpci = comp_rpci - m_rpci_c3
                diff_delta = comp_delta - m_delta
                
                cfg_name = cfg_map[cfg]
                report_lines.append(f"  {iso} | {cfg_name:28s}")
                report_lines.append(f"    PCI C3  | Manuscript: {m_pci_c3:.3f} | Computed: {comp_pci:.3f} | Diff: {diff_pci:+.3f}")
                report_lines.append(f"    RPCI C3 | Manuscript: {m_rpci_c3:.3f} | Computed: {comp_rpci:.3f} | Diff: {diff_rpci:+.3f}")
                report_lines.append(f"    Delta   | Manuscript: {m_delta:.3f} | Computed: {comp_delta:.3f} | Diff: {diff_delta:+.3f}")
            else:
                report_lines.append(f"  [ERROR] No data found for {iso} {cfg}")
    else:
        report_lines.append("  [ERROR] table8_pci_rpci_scenarios.csv not found.")
    report_lines.append("")

    report_text = "\n".join(report_lines)
    print(report_text)
    
    report_out = tables_dir / "manuscript_validation_report.txt"
    with open(report_out, "w", encoding="utf-8") as f:
        f.write(report_text)
    print(f"Validation complete. Report written to {report_out}")

if __name__ == "__main__":
    validate()
