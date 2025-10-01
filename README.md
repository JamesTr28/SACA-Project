# Indigenous Triage — Voice Input (Local Only)

This is a **multi-file web frontend** that supports **voice input** (microphone capture + waveform) and provides **placeholders** for **on-device ML/NLP** (no external APIs).

> ✅ No data leaves the browser. Audio is recorded locally and can be exported to WAV.  
> ⚠️ The STT and NLP are placeholders — replace them with your own on-device (WASM) models.

## Files
- `index.html` — main UI
- `css/styles.css` — styles
- `js/components.js` — UI helpers (chat bubbles, download, etc.)
- `js/audio.js` — microphone recording + waveform + WAV export
- `js/stt.js` — **placeholder** speech-to-text (local stub)
- `js/nlp.js` — **placeholder** triage/NLP (local stub)
- `js/app.js` — app wiring
- `assets/icon.svg` — favicon

## Run
Just open `index.html` in a modern browser (Chrome/Edge/Firefox).  
If the browser blocks mic over `file://`, serve locally:
```bash
# Python 3
python -m http.server 8080
# then visit http://localhost:8080
```

## Replace placeholders
- STT: Replace `stt.transcribeAudio()` in `js/stt.js` with WASM STT (e.g., Vosk WASM, whisper.cpp-wasm).
- NLP: Replace `runLocalNLP()` in `js/nlp.js` with your triage model or rule engine.
