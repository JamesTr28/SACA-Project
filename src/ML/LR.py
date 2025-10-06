import pandas as pd
import joblib

def predict(input_symptoms: []):
    # Load the model
    lr = joblib.load('src/ML/logistic_model.pkl')
    le = joblib.load("src/ML/label_encoder.pkl")

    # Load the original dataset just to get column names
    df = pd.read_csv("src/ML/Final_Augmented_dataset_Diseases_and_Symptoms.csv")
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

if __name__ == "__main__":
    predict(['depression', 'shortness_of_breath']);
