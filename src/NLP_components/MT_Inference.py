from transformers import MT5ForConditionalGeneration, T5TokenizerFast
import torch
from huggingface_hub import list_repo_files
print(list_repo_files("Widewingz/MT_model"))


from huggingface_hub import login; login("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")
REPO_ID = "Widewingz/MT_model"   # your HF model
device = "mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu")

tok = T5TokenizerFast.from_pretrained(REPO_ID)
dtype = torch.float16 if device == "cuda" else None
model = MT5ForConditionalGeneration.from_pretrained(REPO_ID, torch_dtype=dtype).to(device).eval()

def translate(text, beams=6, max_len=160, len_pen=1.0):
    prompt = "translate Warlpiri to English: " + text.strip()
    enc = tok([prompt], return_tensors="pt").to(device)
    with torch.no_grad():
        out = model.generate(**enc, num_beams=beams, max_length=max_len, length_penalty=len_pen)
    return tok.batch_decode(out, skip_special_tokens=True)[0].strip()

print(translate("ngula kurdu purlapa ..."))
