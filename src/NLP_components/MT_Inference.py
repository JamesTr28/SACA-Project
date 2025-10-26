# src/NLP_components/MT_Inference.py
# PURPOSE: Load mT5 once and expose translate(), with HF token baked in.

import os
import torch
from transformers import MT5ForConditionalGeneration, T5TokenizerFast
from huggingface_hub import login

# ----------------- HARD-CODED CREDENTIALS (PRIVATE ONLY) -----------------
HF_TOKEN = ""  # <-- put your token here
REPO_ID  = "Widewingz/MT_model1"                           # <-- your model repo
# -------------------------------------------------------------------------

# Optional: don’t write token to git credentials on the machine
try:
    login(token=HF_TOKEN, add_to_git_credential=False)
except Exception:
    # Not fatal; if login fails, Transformers may still use cached auth
    pass

# Device & dtype
device = (
    "mps" if torch.backends.mps.is_available()
    else ("cuda" if torch.cuda.is_available() else "cpu")
)
dtype = torch.float16 if device == "cuda" else None

# Load model & tokenizer once at import time
print(f"[MT_Inference] Loading '{REPO_ID}' on device={device} ...")
_tok = T5TokenizerFast.from_pretrained(REPO_ID)  # token now provided by login()
_model = MT5ForConditionalGeneration.from_pretrained(REPO_ID, torch_dtype=dtype).to(device).eval()
print("[MT_Inference] Loaded.")

def translate(text: str, beams: int = 6, max_len: int = 160, len_pen: float = 1.0) -> str:
    prompt = "translate Warlpiri to English: " + text.strip()
    enc = _tok([prompt], return_tensors="pt").to(device)
    with torch.no_grad():
        out = _model.generate(
            **enc,
            num_beams=beams,
            max_length=max_len,
            length_penalty=len_pen
        )
    return _tok.batch_decode(out, skip_special_tokens=True)[0].strip()

def info() -> dict:
    return {"device": device, "repo": REPO_ID}

if __name__ == "__main__":
    print(info())
    print("Sample:", translate("ngula kurdu purlapa ..."))