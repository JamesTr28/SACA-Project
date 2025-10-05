# src/backend/app.py
import os, sys, time, tempfile
import torch
from flask import Flask, request, jsonify
from flask_cors import CORS

# Ensure we can import src.NLP_components.*
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from NLP_components.MT_Inference import translate as mt_translate, info as mt_info
from NLP_components.ASR_Inference import transcribe as asr_transcribe

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173"]}})
ALLOWED_EXTS = {".wav", ".flac", ".mp3", ".m4a", ".ogg", ".opus"}

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

    # Save to a temp file, run ASR, clean up
    t0 = time.time()
    tmp = None
    try:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
        f.save(tmp.name)
        tmp.flush()

        text = asr_transcribe(tmp.name)  # <- your MMS transcribe() function
        ms = int((time.time() - t0) * 1000)
        return jsonify({"text": text, "runtime_ms": ms, "device": "cuda" if torch.cuda.is_available() else ("mps" if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available() else "cpu")})
    except FileNotFoundError:
        return jsonify({"detail": "File not found after upload."}), 500
    except Exception as e:
        return jsonify({"detail": f"Transcription failed: {e}"}), 500
    finally:
        try:
            if tmp is not None:
                os.unlink(tmp.name)
        except Exception:
            pass
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
