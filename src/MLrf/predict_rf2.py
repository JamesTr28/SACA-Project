import pandas as pd
import joblib

def predict(input_symptoms: []):
    """
    Predict disease from a list of underscore symptoms using the trained Random Forest model.
    Example input: ['fever', 'shortness_of_breath', 'cough']
    """

    #  Load model bundle
    bundle = joblib.load('model_rf_compressed2.joblib')     
    #model_rf_light2.joblib for lighter model
    # src/MLrf/
    rf_model = bundle["model"]
    le = bundle["label_encoder"]
    feature_cols = bundle["feature_cols"]
    bin_cols = bundle.get("bin_cols", [])
    precautions_map = bundle.get("precautions_map", {})

    # Build input DataFrame
    # All features initialized to 0
    input_data = {col: [1 if col in input_symptoms else 0] for col in feature_cols}

    # Compute derived features if expected
    if "symptom_sum" in feature_cols:
        input_data["symptom_sum"] = [sum(input_data.get(c, [0])[0] for c in bin_cols)]
    if "symptom_ratio" in feature_cols and len(bin_cols) > 0:
        total = len(bin_cols)
        input_data["symptom_ratio"] = [input_data["symptom_sum"][0] / total]

    # Keep consistent feature order
    X_input = pd.DataFrame(input_data)[feature_cols]

    # Predict disease 
    try:
        pred_probs = rf_model.predict_proba(X_input)[0]
        pred_idx = pred_probs.argmax()
        predicted_disease = le.inverse_transform([pred_idx])[0]
        probability = float(pred_probs[pred_idx])
    except Exception:
        pred_label = rf_model.predict(X_input)[0]
        predicted_disease = le.inverse_transform([pred_label])[0]
        probability = None

    #  Get precautions if available 
    precautions = precautions_map.get(predicted_disease, "")

    print(f"Predicted Disease: {predicted_disease}")
    print(f"Probability: {probability:.2%}" if probability else "Probability: N/A")
    if precautions:
        print(f"Precautions: {precautions}")

    return {
        "disease": predicted_disease,
        "probability": probability,
        "precautions": precautions
    }


# --- Quick test example ---
if __name__ == "__main__":
    example_symptoms = ['fever', 'sore_throat', 'cough']
    result = predict(example_symptoms)
    print(result)
