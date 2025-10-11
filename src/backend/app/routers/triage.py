from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import joblib
import pandas as pd
from .. import schemas, crud, dependencies, models

router = APIRouter(prefix="/api", tags=["Triage"])

# --- Load ML Models at Startup ---
MODEL_PATH = "./models_ml/logistic_model.pkl"
ENCODER_PATH = "./models_ml/label_encoder.pkl"

try:
    model = joblib.load(MODEL_PATH)
    label_encoder = joblib.load(ENCODER_PATH)
    MODEL_FEATURES = model.feature_names_in_
except Exception as e:
    model, label_encoder, MODEL_FEATURES = None, None, []
    print(f"Warning: Could not load ML models from {MODEL_PATH}. Endpoint will not work. Error: {e}")

@router.post("/triage-symptoms", response_model=schemas.TriageSymptomResponse)
def triage_symptoms(
    request: schemas.TriageSymptomRequest,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    if not all([model, label_encoder, MODEL_FEATURES]):
         raise HTTPException(status_code=503, detail="ML model is not available on the server.")

    input_data = pd.DataFrame(columns=MODEL_FEATURES)
    input_data.loc[0] = 0

    for symptom in request.symptoms:
        if symptom in MODEL_FEATURES:
            input_data.at[0, symptom] = 1

    probabilities = model.predict_proba(input_data)[0]
    prediction_idx = probabilities.argmax()

    predicted_disease = label_encoder.inverse_transform([prediction_idx])[0]
    confidence = float(probabilities[prediction_idx])

    crud.create_triage_session(
        db=db, user_id=current_user.id, symptoms=request.symptoms,
        disease=predicted_disease, probability=confidence
    )

    return {"predicted_disease": predicted_disease, "confidence_score": confidence}
