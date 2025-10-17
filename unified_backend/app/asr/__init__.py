from flask import Blueprint, request, jsonify

asr_bp = Blueprint("asr", __name__, url_prefix="/api/asr")

@asr_bp.post("/transcribe")
def transcribe():
    f = request.files.get("audio")
    if not f:
        return jsonify({"message": "audio missing"}), 400
    return jsonify({"text": "I have a fever and cough"})
