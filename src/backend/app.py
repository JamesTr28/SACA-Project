# src/backend/app.py
import os, sys, time, tempfile
import torch
from flask import Flask, request, jsonify
from flask_cors import CORS
import datetime
import subprocess

# Ensure we can import src.NLP_components.*
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from NLP_components.MT_Inference import translate as mt_translate, info as mt_info
from NLP_components.ASR_Inference import transcribe as asr_transcribe
from NLP_components.entext_train import process_texts, bootstrap_pipeline

from ML.LR import predict
NLP = bootstrap_pipeline()  # returns an object holding nlp, matchers, dictionaries, etc.


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173"]}})
ALLOWED_EXTS = {".wav", ".flac", ".mp3", ".m4a", ".ogg", ".opus"}
def convert_to_wav_16khz(input_path, output_path):
    subprocess.run([
        "ffmpeg", "-y", "-i", input_path,
        "-ar", "16000", "-ac", "1",  # 16kHz mono
        output_path
    ], check=True)

@app.post("/asr/transcribe")
def asr_transcribe_endpoint():
    """
    Accepts a single uploaded audio file under form field name 'audio'.
    Returns: { text, runtime_ms, device }
    """
    print("[/asr/transcribe] HIT")
    if "audio" not in request.files:
        return jsonify({"detail": "Missing file field 'audio'."}), 400

    f = request.files["audio"]
    if not f or f.filename is None or f.filename.strip() == "":
        return jsonify({"detail": "Empty filename."}), 400

    _, ext = os.path.splitext(f.filename.lower())
    if ext not in ALLOWED_EXTS:
        return jsonify({"detail": f"Unsupported file type: {ext}. Allowed: {sorted(ALLOWED_EXTS)}"}), 400

    # Run ASR, clean up
    try:
        text = asr_transcribe(f)  # <- your MMS transcribe() function
        return jsonify({"text": text, "device": "cuda" if torch.cuda.is_available() else ("mps" if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available() else "cpu")})
    except FileNotFoundError:
        return jsonify({"detail": "File not found after upload."}), 500
    except Exception as e:
        return jsonify({"detail": f"Transcription failed: {e}"}), 500

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
# @app.post("/nlp/process")
# def nlp_process():
#     """
#     Body (JSON):
#       { "texts": ["No fever but mild headache since yesterday", "HR 120"], "ndjson": false }
#     or:
#       { "text": "No fever but mild headache since yesterday", "ndjson": false }

#     Returns:
#       { "results": [ { ... }, { ... } ] }
#     """
#     try:
#         data = request.get_json(force=True) or {}
#     except Exception:
#         return jsonify({"detail": "Invalid JSON"}), 400

#     # Accept either 'texts' (list) or 'text' (single)
#     texts = data.get("texts")
#     if texts is None:
#         single = (data.get("text") or "").strip()
#         texts = [single] if single else None

#     if not texts or not isinstance(texts, list):
#         return jsonify({"detail": "Provide 'text' or 'texts' (array of strings)."}), 400

#     # Optional flags you already support in your script
#     ndjson = bool(data.get("ndjson") or False)

#     try:
#         t0 = time.time()
#         # Pass the prebuilt NLP pipeline/context if your process_texts supports it
#         results = process_texts(texts, nlp_ctx=NLP, ndjson=ndjson)  # adjust signature to your function
#         ms = int((time.time() - t0) * 1000)
#         return jsonify({"results": results, "runtime_ms": ms})
#     except Exception as e:
#         return jsonify({"detail": f"Processing failed: {e}"}), 500
from flask import request, jsonify
import time

@app.post("/nlp/process")
def nlp_process():
    """
    Accepts only plain text input:
      Content-Type: text/plain
      Body: "No fever but mild headache since yesterday"

    Returns:
      { "results": [ { ... } ], "runtime_ms": <int> }
    """
    if request.content_type != 'text/plain':
        return jsonify({"detail": "Only 'text/plain' is accepted."}), 415

    raw_text = request.data.decode('utf-8').strip()
    if not raw_text:
        return jsonify({"detail": "Empty text body."}), 400

    texts = [raw_text]

    try:
        t0 = time.time()
        results = process_texts(texts)  # remove nlp_ctx and ndjson if not needed
        ms = int((time.time() - t0) * 1000)
        return jsonify({"results": results, "runtime_ms": ms})
    except Exception as e:
        return jsonify({"detail": f"Processing failed: {e}"}), 500

@app.post("/predict")
def predict_disease():
    try:
        data = request.get_json(force=True) or {}
    except Exception:
        return jsonify({"detail": "Invalid JSON"}), 400

    text = data.get("symptoms")
    print(text)
    if not text:
        return jsonify({"detail": "No sympyoms provided"}), 400

    disease = predict(text)

    return jsonify({
        "jobId": datetime.datetime.now(),
        "disease": disease
    })
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
