import torch
import torchaudio
import librosa
import numpy as np
import torch.nn.functional as F

# Function to load and resample audio (from previous cell)
def load_audio(audio_path, target_sr=16000):
    waveform, sample_rate = torchaudio.load(audio_path)
    if sample_rate != target_sr:
        waveform = torchaudio.transforms.Resample(sample_rate, target_sr)(waveform)
    # Assuming mono audio, take the first channel
    return waveform.squeeze().numpy()

# Replace with the path to your sample audio file
# You can upload one to your Colab environment or provide a path from Google Drive
SAMPLE_AUDIO_PATH = '/content/drive/MyDrive/Colab Notebooks/Sample2.wav' # Example path

# Load and process the sample audio
try:
    wav = load_audio(SAMPLE_AUDIO_PATH)
    print(f"Sample audio loaded from {SAMPLE_AUDIO_PATH} and processed.")
except FileNotFoundError:
     print(f"Error: Sample audio file not found at {SAMPLE_AUDIO_PATH}. Please check the path or upload the file.")
     wav = None # Set wav to None so the rest of the code doesn't run if file not found

if wav is not None:
    # Build inputs ONLY with feature_extractor (never tokenizer)
    # Assumes 'processor' is available from a previous cell
    fe  = processor.feature_extractor(wav, sampling_rate=16000, return_tensors="pt", padding=False)

    # Assumes 'DEVICE' is available from a previous cell
    inputs = {"input_values": fe["input_values"].to(DEVICE)}
    if "attention_mask" in fe:
        inputs["attention_mask"] = fe["attention_mask"].to(DEVICE)

    # Perform inference with the fresh base model (adapter OFF)
    # Assumes 'base_fresh' is available from a previous cell
    with torch.no_grad():
        logits_base = base_fresh(**inputs).logits # Use the base_fresh model

    # ---- Greedy decode ----
    # Assumes 'processor' is available
    predicted_ids_base = torch.argmax(logits_base, dim=-1)[0] # Greedy ids for the first sample
    transcription_base = processor.decode(predicted_ids_base).replace("|", " ") # Replace | with space

    print(transcription_base)

  