import pandas as pd
import joblib
import os
def get_local_path(filename):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
def predict(input_symptoms: []):
    # Load the model
    lr = joblib.load(get_local_path("logistic_model.pkl"))
    le = joblib.load(get_local_path("label_encoder.pkl"))

    # Load the original dataset just to get column names
    df = pd.read_csv(get_local_path("diseases_symptoms_sample_trim.csv"))
    df.columns = df.columns.str.replace(' ', '_')

    # Drop disease column
    symptom_columns = df.columns.drop('diseases')

    # Example input symptoms
    #input_symptoms = ['depression', 'shortness_of_breath']

    # Create input vector (1 for present symptoms, 0 otherwise)
    input_data = {col: [1 if col in input_symptoms else 0] for col in symptom_columns}
    X_input = pd.DataFrame(input_data)


    # Predict numeric label
    pred_label = lr.predict(X_input)[0]

    # Convert back to disease name
    predicted_disease = le.inverse_transform([pred_label])[0]

    print("Predicted disease:", predicted_disease)

    return predicted_disease

if __name__ == "__main__":
    predict(['depression', 'shortness_of_breath']);
    predict(['chest_pain', 'fatigue', 'high_fever']
);
