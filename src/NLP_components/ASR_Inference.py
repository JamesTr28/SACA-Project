#!/usr/bin/env python3
"""
mms_transcribe.py — Transcribe audio using the base MMS-1B model (facebook/mms-1b-all).

Usage (CLI):
    python mms_transcribe.py /path/to/audio.wav

Programmatic use:
    from mms_transcribe import transcribe
    text = transcribe("/path/to/audio.wav")
"""

import argparse
import sys
from typing import Optional

import torch
import torchaudio

from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor

# --------------------
# Config
# --------------------
BASE_ID = "facebook/mms-1b-all"

# Prefer CUDA, then MPS (Apple), else CPU
if torch.cuda.is_available():
    DEVICE = "cuda"
elif getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
    DEVICE = "mps"
else:
    DEVICE = "cpu"

# Lazy singletons (loaded on first call)
_MODEL: Optional[Wav2Vec2ForCTC] = None
_PROCESSOR: Optional[Wav2Vec2Processor] = None


# --------------------
# Helpers
# --------------------
def _ensure_loaded():
    """Load the base model/processor exactly once."""
    global _MODEL, _PROCESSOR
    if _MODEL is None or _PROCESSOR is None:
        _PROCESSOR = Wav2Vec2Processor.from_pretrained(BASE_ID)
        # Use float16 on CUDA to save memory; float32 elsewhere
        torch_dtype = torch.float16 if DEVICE == "cuda" else torch.float32
        _MODEL = Wav2Vec2ForCTC.from_pretrained(BASE_ID, torch_dtype=torch_dtype)
        _MODEL.to(DEVICE)
        _MODEL.eval()


def load_audio(audio_path: str, target_sr: int = 16000) -> torch.Tensor:
    """
    Load an audio file and return a mono waveform tensor at target_sr (shape: [T]).
    """
    waveform, sample_rate = torchaudio.load(audio_path)  # [C, T]
    # Convert to mono (mean across channels) if needed
    if waveform.dim() == 2 and waveform.size(0) > 1:
        waveform = waveform.mean(dim=0, keepdim=True)
    # Resample if necessary
    if sample_rate != target_sr:
        resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=target_sr)
        waveform = resampler(waveform)
    # Squeeze to [T]
    return waveform.squeeze(0)


# --------------------
# Core API
# --------------------
@torch.inference_mode()
def transcribe(audio_path: str) -> str:
    """
    Transcribe a single audio file to text using the base MMS-1B model.

    Args:
        audio_path: Path to an audio file readable by torchaudio (e.g., .wav, .flac).

    Returns:
        The decoded transcription string (greedy CTC), with '|' replaced by spaces.
    """
    _ensure_loaded()

    # Load & preprocess audio
    wav_16k = load_audio(audio_path, target_sr=16000)

    # MMS expects 16k PCM in the processor
    # (Use the feature extractor part; tokenizer is not used for inputs.)
    fe = _PROCESSOR.feature_extractor(
        wav_16k.numpy(), sampling_rate=16000, return_tensors="pt", padding=False
    )

    inputs = {"input_values": fe["input_values"].to(DEVICE)}
    if "attention_mask" in fe:
        inputs["attention_mask"] = fe["attention_mask"].to(DEVICE)

    # Forward pass
    logits = _MODEL(**inputs).logits  # [B, T, V]

    # Greedy decode (CTC)
    pred_ids = torch.argmax(logits, dim=-1)  # [B, T]
    # batch_decode returns a list[str]; replace '|' with spaces for readability
    text = _PROCESSOR.batch_decode(pred_ids)[0].replace("|", " ").strip()
    return text


# --------------------
# CLI
# --------------------
def main():
    parser = argparse.ArgumentParser(description="Transcribe audio with base MMS-1B (no adapters).")
    parser.add_argument("audio_path", type=str, help="Path to audio file (e.g., *.wav, *.flac)")
    args = parser.parse_args()

    try:
        text = transcribe(args.audio_path)
        print(text)
    except FileNotFoundError:
        print(f"Error: file not found at {args.audio_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Transcription failed: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
