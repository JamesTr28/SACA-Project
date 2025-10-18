# run_pipeline_rf.py
import json
import argparse
from pathlib import Path
import joblib
import numpy as np
import pandas as pd

# ==== 1) 导入你的NLP抽取 ====
from entext_train import extract_features, combine_features  # 确保同目录或已在PYTHONPATH

BUNDLE_PATHS = [
    Path(__file__).with_name("model_rf.joblib"),
    # 允许你把模型放统一目录，比如 E:\swinburne\2025_s2\
    Path(r"E:\swinburne\2025_s2\model_rf.joblib"),
]

def load_bundle():
    for p in BUNDLE_PATHS:
        if p.exists():
            return joblib.load(p)
    raise FileNotFoundError(f"Cannot find model bundle in: {BUNDLE_PATHS}")

def vectorize_from_nlp(nlp_json: dict, feature_cols: list[str]) -> pd.DataFrame:
    """
    将 combine_features() 的结果转为一行特征：
    - 症状名命中 → 1，否则 0
    - 自动补充 symptom_sum / symptom_ratio
    """
    present = set()
    if "symptoms" in nlp_json:
        for item in nlp_json["symptoms"]:
            name = (item.get("name") or "").strip().lower()
            if name:
                present.add(name)

    # 先全0
    row = {c: 0 for c in feature_cols}

    # 命中特征置1（仅对二进制症状列；衍生列稍后计算）
    bin_cols = [c for c in feature_cols if c not in ("symptom_sum", "symptom_ratio")]
    for col in bin_cols:
        # 特征列名和症状名通常一致（都为小写+下划线/空格处理后）
        # 保险起见做个宽松匹配：把列名里的下划线替换空格对比
        key = col.replace("_", " ").strip().lower()
        if key in present:
            row[col] = 1

    # 填充衍生特征
    bin_vals = [row[c] for c in bin_cols]
    ssum = int(sum(bin_vals))
    row["symptom_sum"] = ssum if "symptom_sum" in feature_cols else 0
    row["symptom_ratio"] = (ssum / max(len(bin_cols), 1)) if "symptom_ratio" in feature_cols else 0.0

    return pd.DataFrame([row], columns=feature_cols)

def predict_topk(model, X_row: pd.DataFrame, le, k: int = 3):
    proba = getattr(model, "predict_proba", None)
    if proba is None:
        # 一些模型未实现 predict_proba（RF有）
        preds = model.predict(X_row)
        labels = le.inverse_transform(preds)
        return [{"disease": labels[0], "prob": 1.0}]
    p = model.predict_proba(X_row)[0]
    idx = np.argsort(p)[::-1][:k]
    return [{"disease": le.classes_[i], "prob": float(p[i])} for i in idx]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", required=True, help="English sentence for inference")
    parser.add_argument("--topk", type=int, default=3, help="Top-K predictions")
    args = parser.parse_args()

    bundle = load_bundle()
    model = bundle["model"]
    le = bundle["label_encoder"]
    feature_cols = bundle["feature_cols"]

    nlp_feats = extract_features(args.text)
    nlp_json = combine_features(nlp_feats)

    X_row = vectorize_from_nlp(nlp_json, feature_cols)
    topk = predict_topk(model, X_row, le, k=args.topk)

    out = {
        "nlp_output": nlp_json,
        "topk_predictions": topk
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
