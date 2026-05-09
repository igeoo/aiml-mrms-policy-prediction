from pathlib import Path
import pandas as pd

FEATURE_COLUMNS = [
    "rule_of_law", "regulatory_quality", "government_effectiveness",
    "control_of_corruption", "political_stability", "fraser_ppi"
]
CRITERIA_COLUMNS = ["EV", "RC", "EI", "OF"]

def project_root() -> Path:
    return Path(__file__).resolve().parents[2]

def load_feature_matrix(path=None):
    if path is None:
        path = project_root() / "data" / "processed" / "feature_matrix_normalised.csv"
    df = pd.read_csv(path)
    X = df[FEATURE_COLUMNS].astype(float)
    y = df["label"].map({"Unfavourable": 0, "Favourable": 1})
    if y.isna().any():
        raise ValueError("Labels must be 'Favourable' or 'Unfavourable'.")
    return df, X, y.astype(int)

def load_project_scores(path=None):
    if path is None:
        path = project_root() / "data" / "processed" / "project_scores.csv"
    return pd.read_csv(path)

def ensure_results_dirs():
    root = project_root()
    tables = root / "results" / "tables"
    figures = root / "results" / "figures"
    tables.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)
    return tables, figures
