from flask import Blueprint, request, jsonify, current_app

nlp_bp = Blueprint("nlp", __name__, url_prefix="/api/nlp")  # <-- add __name__

@nlp_bp.post("/predict")
def predict():
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"message": "text is required"}), 400
    return jsonify({"prediction": "flu", "confidence": 0.66})
