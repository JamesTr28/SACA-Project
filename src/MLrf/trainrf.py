# train_rf.py
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split, StratifiedKFold, GridSearchCV
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, f1_score, classification_report, top_k_accuracy_score
from sklearn.ensemble import RandomForestClassifier
import joblib
import warnings

CSV_PATH = Path(__file__).with_name("dataset2.csv")  # 你的0/1症状数据
MODEL_PATH = Path(__file__).with_name("model_rf.joblib")
RANDOM_SEED = 42
TEST_BASE_RATIO = 0.20
CV_K_MAX = 5

def is_yes_no_col(s: pd.Series) -> bool:
    if s.dtype != "object":
        return False
    vals = set(s.dropna().unique().tolist())
    return vals.issubset({"Yes", "No"})

def main():
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"Missing {CSV_PATH}")

    df = pd.read_csv(CSV_PATH)
    df.columns = [c.strip().replace(" ", "_") for c in df.columns]
    assert "Disease" in df.columns, "Expect a 'Disease' column"
    df = df.dropna(subset=["Disease"]).reset_index(drop=True)

    # Yes/No → 0/1  
    feature_cols = [c for c in df.columns if c != "Disease"]
    yn_cols = [c for c in feature_cols if is_yes_no_col(df[c])]
    if yn_cols:
        df[yn_cols] = df[yn_cols].replace({"Yes": 1, "No": 0}).astype("int8")

    X = df[feature_cols].copy()
    # 补充衍生特征 add summary features
    bin_cols = [c for c in X.columns if X[c].dropna().isin([0,1]).all()]
    X["symptom_sum"] = X[bin_cols].sum(axis=1).astype("int16")
    X["symptom_ratio"] = (X["symptom_sum"] / max(len(bin_cols),1)).astype("float32")
    X = X.fillna(0)

    # 删掉全零列、重复列 remove const and duplicate cols
    const_mask = (X.sum(axis=0) == 0)
    if const_mask.any():
        X = X.loc[:, ~const_mask]
    dup_mask = X.T.duplicated(keep="first")
    if dup_mask.any():
        X = X.loc[:, ~dup_mask]

    feature_names = X.columns.tolist()

    # 目标 target
    y_raw = df["Disease"].astype(str)
    le = LabelEncoder()
    y = le.fit_transform(y_raw)

    # 自适应测试集占比（保证每类至少能进测试集） self-adaptive test set ratio
    n_classes = len(np.unique(y))
    n_samples = len(y)
    need_ratio = (n_classes + 2) / max(n_samples, 1)
    test_ratio = min(0.5, max(TEST_BASE_RATIO, need_ratio))

    try:
        X_tr, X_te, y_tr, y_te = train_test_split(
            X, y, test_size=test_ratio, random_state=RANDOM_SEED, stratify=y
        )
    except ValueError:
        X_tr, X_te, y_tr, y_te = train_test_split(
            X, y, test_size=test_ratio, random_state=RANDOM_SEED, stratify=None
        )

    print(f"[INFO] samples={n_samples}, classes={n_classes}, test_ratio={test_ratio:.3f}")
    print(f"[INFO] train={X_tr.shape[0]}, test={X_te.shape[0]}, features={X_tr.shape[1]}")

    # RF + 网格 (rf + grid search)
    rf = RandomForestClassifier(
        n_estimators=300,
        max_depth=None,
        min_samples_split=2,
        class_weight="balanced",
        random_state=RANDOM_SEED,
        n_jobs=-1
    )

    min_count = int(np.min(np.bincount(y_tr)))
    k = int(max(2, min(CV_K_MAX, min_count)))
    cv = StratifiedKFold(n_splits=k, shuffle=True, random_state=RANDOM_SEED)
    print(f"[INFO] CV folds = {k} (min_count_in_train={min_count})")

    param_grid = [{
        "n_estimators": [300, 500],
        "max_depth": [None, 10, 20],
        "min_samples_split": [2, 5],
        "min_samples_leaf": [1, 2]
    }]

    grid = GridSearchCV(
        estimator=rf,
        param_grid=param_grid,
        scoring="f1_macro",
        cv=cv,
        n_jobs=-1,
        verbose=0
    )
    grid.fit(X_tr, y_tr)

    print("\n== Best CV params ==")
    print(grid.best_params_)
    print(f"best_macroF1_CV = {grid.best_score_:.4f}")

    best_model = grid.best_estimator_

    # 测试集评估 test set evaluation
    try:
        proba = best_model.predict_proba(X_te)
        y_pred = proba.argmax(axis=1)
        top3 = top_k_accuracy_score(y_te, proba, k=3)
    except Exception:
        y_pred = best_model.predict(X_te)
        proba = None
        top3 = float("nan")

    acc = accuracy_score(y_te, y_pred)
    macro_f1 = f1_score(y_te, y_pred, average="macro", zero_division=0)
    weighted_f1 = f1_score(y_te, y_pred, average="weighted", zero_division=0)

    print("\n== Test metrics ==")
    print(f"Accuracy       : {acc:.3f}")
    print(f"Macro F1       : {macro_f1:.3f}")
    print(f"Weighted F1    : {weighted_f1:.3f}")
    print(f"Top-3 Accuracy : {top3:.3f}")
    print("\n== Classification report ==")
    print(classification_report(y_te, y_pred, zero_division=0, target_names=le.classes_))

    # 保存bundle save bundle
    bundle = {
        "model": best_model,
        "label_encoder": le,
        "feature_cols": feature_names,
        "disease_classes": list(le.classes_),
    }
    joblib.dump(bundle, MODEL_PATH)
    print(f"\n[INFO] Saved RF model bundle to: {MODEL_PATH.resolve()}")

if __name__ == "__main__":
    warnings.filterwarnings("ignore")
    main()
