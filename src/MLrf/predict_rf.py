import joblib
import numpy as np
import pandas as pd
from entext_train import extract_features, combine_features  # Use  existing NLP extraction logic

# 1. Load the trained Random Forest model 
MODEL_PATH = "model_rf.joblib"  # or "model_rf.pkl" 
bundle = joblib.load(MODEL_PATH)

model = bundle["model"]                  # Extract the trained RandomForest model
label_encoder = bundle["label_encoder"]  # Extract label encoder for decoding predictions
feature_cols = bundle["feature_cols"]    # Feature column names used during training

print(f" Model loaded from {MODEL_PATH}")
print(f" Total features used: {len(feature_cols)}")


#  2 Define the prediction pipeline 
def predict_disease_from_text(text: str, topk: int = 3):
    # """
    # Predict the top-k possible diseases from a given English sentence.
    # Steps:
    #   1. Extract medical entities (symptoms, duration, etc.) from text using NLP.
    #   2. Convert extracted features into a 0/1 vector based on training features.
    #   3. Run the Random Forest model to predict probabilities.
    #   4. Return the top-k most probable diseases.
    # """

    # Step 1: Extract features from text using your NLP pipeline
    extracted = extract_features(text)
    combined = combine_features(extracted)

    # Step 2: Build a binary feature vector (1 = symptom present, 0 = absent)
    symptom_names = [s["name"] for s in combined.get("symptoms", [])]
    X_dict = {c: 0 for c in feature_cols}  # Initialize all features to 0
    for s in symptom_names:
        if s in X_dict:
            X_dict[s] = 1

    # Step 3: Create DataFrame for model input (keep same column order)
    X_df = pd.DataFrame([X_dict])[feature_cols]

    # Step 4: Predict with model
    try:
        probas = model.predict_proba(X_df)[0]
        top_idx = np.argsort(probas)[::-1][:topk]  # Sort probabilities (descending)
        top_preds = [
            {"disease": label_encoder.inverse_transform([i])[0], "probability": float(probas[i])}
            for i in top_idx
        ]
    except Exception:
        # Some models may not have predict_proba()
        pred = model.predict(X_df)[0]
        top_preds = [{"disease": label_encoder.inverse_transform([pred])[0], "probability": None}]

    # Step 5: Print readable results
    print("\n===============================")
    print(f" Input Text: {text}")
    print("Extracted Symptoms:", symptom_names)
    print("Predicted Diseases:")
    for i, p in enumerate(top_preds, 1):
        prob = f"{p['probability']*100:.1f}%" if p['probability'] else "N/A"
        print(f"  {i}. {p['disease']} ({prob})")
    print("===============================")

    return top_preds


# 3. Run a quick demo ------------------
if __name__ == "__main__":
    test_text = "I have had a high fever and sore throat for 3 days, with cough and fatigue."
    predict_disease_from_text(test_text, topk=3)
