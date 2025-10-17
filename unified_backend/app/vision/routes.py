from flask import Blueprint, request, jsonify

vision_bp = Blueprint("vision", __name__, url_prefix="/api/vision")

@vision_bp.post("/predict")
def predict():
    f = request.files.get("image")
    if not f:
        return jsonify({"message": "image missing"}), 400
    # stub so you can test end-to-end
    return jsonify({"predicted_class_name": "eczema", "confidence": 0.78})
