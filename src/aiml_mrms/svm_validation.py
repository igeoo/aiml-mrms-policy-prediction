import numpy as np
import pandas as pd
from sklearn.model_selection import LeaveOneOut, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC, LinearSVC
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score, precision_score, recall_score, roc_auc_score, confusion_matrix
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from .data_utils import FEATURE_COLUMNS

CRITERION_MAP = {
    "control_of_corruption": "EI",
    "government_effectiveness": "OF",
    "fraser_ppi": "EV",
    "rule_of_law": "RC",
    "regulatory_quality": "RC",
    "political_stability": "OF",
}

def loo_grid_search_predictions(X, y, c_grid=(0.1, 1, 10, 100)):
    loo = LeaveOneOut()
    y_pred = np.zeros(len(y), dtype=int)
    y_score = np.zeros(len(y), dtype=float)
    best_cs = []
    for train_idx, test_idx in loo.split(X):
        pipe = Pipeline([
            ("scaler", StandardScaler()),
            ("svc", SVC(kernel="linear", class_weight="balanced", probability=True, random_state=42)),
        ])
        grid = GridSearchCV(pipe, {"svc__C": list(c_grid)}, scoring="balanced_accuracy", cv=3)
        grid.fit(X.iloc[train_idx], y.iloc[train_idx])
        y_pred[test_idx] = grid.predict(X.iloc[test_idx])
        y_score[test_idx] = grid.predict_proba(X.iloc[test_idx])[:, 1]
        best_cs.append(grid.best_params_["svc__C"])
    return y_pred, y_score, best_cs

def svm_metrics(X, y):
    y_pred, y_score, best_cs = loo_grid_search_predictions(X, y)
    out = {
        "accuracy": accuracy_score(y, y_pred),
        "balanced_accuracy": balanced_accuracy_score(y, y_pred),
        "f1": f1_score(y, y_pred, zero_division=0),
        "precision": precision_score(y, y_pred, zero_division=0),
        "recall": recall_score(y, y_pred, zero_division=0),
        "roc_auc": roc_auc_score(y, y_score),
        "confusion_matrix": confusion_matrix(y, y_pred).tolist(),
        "modal_C": pd.Series(best_cs).mode().iloc[0],
    }
    return out, y_pred, y_score

def permutation_test_loo_accuracy(X, y, n_permutations=1000, random_state=42):
    rng = np.random.default_rng(random_state)
    observed, _, _ = svm_metrics(X, y)
    observed_acc = observed["accuracy"]
    accs = []
    for _ in range(n_permutations):
        y_perm = pd.Series(rng.permutation(y.values), index=y.index)
        try:
            metrics, _, _ = svm_metrics(X, y_perm)
            accs.append(metrics["accuracy"])
        except Exception:
            pass
    accs = np.asarray(accs)
    p_value = (np.sum(accs >= observed_acc) + 1) / (len(accs) + 1)
    return {
        "observed_accuracy": observed_acc,
        "n_permutations": int(len(accs)),
        "max_permuted_accuracy": float(np.max(accs)) if len(accs) else np.nan,
        "mean_permuted_accuracy": float(np.mean(accs)) if len(accs) else np.nan,
        "p_value": float(p_value),
    }, accs

def linear_svc_feature_weights(X, y, C=1.0):
    model = Pipeline([
        ("scaler", StandardScaler()),
        ("svc", LinearSVC(C=C, class_weight="balanced", dual=False, random_state=42, max_iter=20000)),
    ])
    model.fit(X, y)
    coefs = np.abs(model.named_steps["svc"].coef_[0])
    weights = coefs / coefs.sum()
    feature_weights = pd.DataFrame({
        "feature": FEATURE_COLUMNS,
        "raw_abs_coef": coefs,
        "normalised_weight": weights,
        "mapped_criterion": [CRITERION_MAP[f] for f in FEATURE_COLUMNS],
    })
    criterion_weights = (
        feature_weights.groupby("mapped_criterion")["normalised_weight"]
        .sum().reindex(["EV", "RC", "EI", "OF"]).reset_index()
        .rename(columns={"mapped_criterion": "criterion", "normalised_weight": "svm_signal"})
    )
    return feature_weights, criterion_weights

def alternative_classifier_weights(X, y):
    rows = []
    logit = Pipeline([
        ("scaler", StandardScaler()),
        ("logit", LogisticRegression(class_weight="balanced", max_iter=10000, random_state=42)),
    ])
    logit.fit(X, y)
    coef = np.abs(logit.named_steps["logit"].coef_[0])
    coef = coef / coef.sum()
    for f, w in zip(FEATURE_COLUMNS, coef):
        rows.append({"model": "logistic_regression", "feature": f, "weight": w, "criterion": CRITERION_MAP[f]})
    rf = RandomForestClassifier(n_estimators=500, class_weight="balanced_subsample", random_state=42)
    rf.fit(X, y)
    imp = rf.feature_importances_ / rf.feature_importances_.sum()
    for f, w in zip(FEATURE_COLUMNS, imp):
        rows.append({"model": "random_forest", "feature": f, "weight": w, "criterion": CRITERION_MAP[f]})
    df = pd.DataFrame(rows)
    agg = df.groupby(["model", "criterion"])["weight"].sum().reset_index().pivot(index="model", columns="criterion", values="weight").reset_index()
    return df, agg
