# src/backend/app.py
import os, sys, time
from flask import Flask, request, jsonify
from flask_cors import CORS

# Ensure we can import src.NLP_components.*
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from NLP_components.MT_Inference import translate as mt_translate, info as mt_info

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173"]}})

@app.get("/healthz")
def healthz():
    return jsonify({"ok": True, **mt_info()})

@app.post("/translate")
def translate():
    try:
        data = request.get_json(force=True) or {}
    except Exception:
        return jsonify({"detail": "Invalid JSON"}), 400

    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"detail": "Empty text"}), 400

    try:
        beams   = int(data.get("beams") or 6)
        max_len = int(data.get("max_len") or 160)
        len_pen = float(data.get("len_pen") or 1.0)
    except Exception:
        return jsonify({"detail": "Invalid parameter types"}), 400

    t0 = time.time()
    try:
        out = mt_translate(text, beams=beams, max_len=max_len, len_pen=len_pen)
    except Exception as e:
        return jsonify({"detail": f"Inference error: {e}"}), 500

    return jsonify({
        "translation": out,
        "runtime_ms": int((time.time() - t0) * 1000),
        **mt_info()
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
