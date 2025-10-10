<template>
  <div class="audio">
    <div class="row">

      <button class="btn" :disabled="recording" @click="start">
        ▶ Start recording
      </button>
      <button class="btn outline" :disabled="!recording" @click="stop">
        ■ Stop
      </button>
      <!-- Add near your existing preview area -->
      <div class="uploadWav">
        <input
          ref="fileInput"
          type="file"
          accept=".wav,audio/wav"
          @change="onPickWav"
          style="display: none"
        />
        <button class="btn outline" :disabled="asrLoading" @click="chooseWav">
          ⤴ Upload .wav (demo)
        </button>
        <small class="meta">Select a local .wav file to transcribe</small>
      </div>

      <span v-if="recording" class="rec">● recording {{ mm }}:{{ ss }}</span>
      <span v-else-if="durationMs > 0" class="dur">⏱ {{ mm }}:{{ ss }}</span>
    </div>

    <p v-if="err" class="err">{{ err }}</p>

    <div v-if="url" class="preview">
      <audio :src="url" controls></audio>
      <button class="link" @click="reset">Re-record</button>
      <small class="meta">~{{ prettySize }} • {{ mime }}</small>
    </div>

    <div v-if="asrLoading" class="asrStatus">Transcribing…</div>
    <p v-if="asrError" class="err">{{ asrError }}</p>
    <div v-if="asrText" class="asrOut">
      <strong>Transcript</strong>
      <pre>{{ asrText }}</pre>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onBeforeUnmount } from "vue";
import { asrTranscribeFile } from "@/services/api"; // POST /asr/transcribe expects field 'audio' (.wav)

const emit = defineEmits(["recorded"]);

const recording = ref(false);
const err = ref("");
const url = ref("");
const mime = ref("audio/wav"); // final upload type is .wav
const durationMs = ref(0);
const sizeBytes = ref(0);

const asrLoading = ref(false);
const asrText = ref("");
const asrError = ref("");

let mediaRec,
  timer,
  startedAt = 0;
const chunks = [];

const MAX_MS = 60_000;
const MAX_BYTES = 25 * 1024 * 1024; // WAV is larger; cap at 25MB

// --- Translation wiring ---
const transLoading = ref(false);
const transError = ref(null);


function tick() {
  durationMs.value = Date.now() - startedAt;
  if (durationMs.value >= MAX_MS) stop();
}

async function start() {
  err.value = "";
  asrError.value = "";
  asrText.value = "";
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

    // We can record in whatever browser supports (usually webm/opus); we'll convert to WAV after stop.
    const type = MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
      ? "audio/webm;codecs=opus"
      : MediaRecorder.isTypeSupported("audio/webm")
      ? "audio/webm"
      : "";
    if (!type) throw new Error("This browser does not support WebM recording.");

    mediaRec = new MediaRecorder(stream, { mimeType: type });

    chunks.length = 0;
    mediaRec.ondataavailable = (e) => {
      if (e.data?.size) chunks.push(e.data);
    };
    mediaRec.onstop = async () => {
      const rawBlob = new Blob(chunks, { type });
      try {
        const wavFile = await toWavFile(rawBlob); // convert to 16-bit PCM WAV
        sizeBytes.value = wavFile.size;
        mime.value = wavFile.type || "audio/wav";
        url.value = URL.createObjectURL(wavFile);

        if (wavFile.size > MAX_BYTES) {
          err.value = "Audio too large (>25MB). Please record again.";
          reset(false);
          return;
        }

        emit("recorded", wavFile); // emit the WAV file upstream if needed
        await transcribeWav(wavFile); // upload to backend
      } catch (convErr) {
        console.error(convErr);
        err.value = "Failed to convert recording to WAV.";
      }
    };

    mediaRec.start();
    recording.value = true;
    startedAt = Date.now();
    durationMs.value = 0;
    clearInterval(timer);
    timer = setInterval(tick, 200);
  } catch (e) {
    err.value = e?.message || "Cannot access microphone";
  }
}

function stop() {
  try {
    mediaRec?.stop();
  } catch {}
  recording.value = false;
  clearInterval(timer);
  mediaRec?.stream?.getTracks()?.forEach((t) => t.stop());
}

function reset(clearEvent = true) {
  try {
    URL.revokeObjectURL(url.value);
  } catch {}
  url.value = "";
  sizeBytes.value = 0;
  durationMs.value = 0;
  asrText.value = "";
  asrError.value = "";
  if (clearEvent) emit("recorded", null);
}

async function transcribeWav(wavFile) {
  asrLoading.value = true;
  asrError.value = "";
  asrText.value = "";
  try {
    const r = await asrTranscribeFile(wavFile); // server sees .wav only
    asrText.value = `${r.text}\n\n(${r.runtime_ms} ms on ${r.device})`;
  } catch (e) {
    asrError.value = e?.message || "Transcription failed";
  } finally {
    asrLoading.value = false;
  }
}

/**
 * Convert an arbitrary audio Blob (e.g., webm/opus) to a 16-bit PCM WAV File.
 * - Uses Web Audio API to decode to an AudioBuffer, then encodes WAV manually.
 * - Output sample rate: original buffer.sampleRate (commonly 48k); ASR backend will resample to 16k.
 */
async function toWavFile(inputBlob) {
  const arrayBuf = await inputBlob.arrayBuffer();

  // Decode with Web Audio API
  const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  const audioBuf = await audioCtx.decodeAudioData(arrayBuf.slice(0));

  // Mixdown to mono Float32
  const numCh = audioBuf.numberOfChannels;
  const len = audioBuf.length;
  const sampleRate = audioBuf.sampleRate;
  const tmp = new Float32Array(len);
  for (let ch = 0; ch < numCh; ch++) {
    tmp.set(audioBuf.getChannelData(ch), 0);
    if (ch === 0) continue;
    const chData = audioBuf.getChannelData(ch);
    for (let i = 0; i < len; i++) tmp[i] = (tmp[i] * ch + chData[i]) / (ch + 1);
  }

  const wavBuffer = encodeWavPCM16(tmp, sampleRate); // ArrayBuffer
  const wavBlob = new Blob([wavBuffer], { type: "audio/wav" });
  return new File([wavBlob], "recording.wav", { type: "audio/wav" });
}

/**
 * Encode Float32 PCM [-1,1] mono into 16-bit PCM WAV (little-endian).
 */
function encodeWavPCM16(float32Mono, sampleRate) {
  const numChannels = 1;
  const bytesPerSample = 2;
  const blockAlign = numChannels * bytesPerSample;
  const byteRate = sampleRate * blockAlign;
  const dataLen = float32Mono.length * bytesPerSample;
  const buffer = new ArrayBuffer(44 + dataLen);
  const view = new DataView(buffer);

  // RIFF header
  writeString(view, 0, "RIFF");
  view.setUint32(4, 36 + dataLen, true);
  writeString(view, 8, "WAVE");

  // fmt  subchunk
  writeString(view, 12, "fmt ");
  view.setUint32(16, 16, true); // Subchunk1Size (16 for PCM)
  view.setUint16(20, 1, true); // AudioFormat (1 = PCM)
  view.setUint16(22, numChannels, true);
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, byteRate, true);
  view.setUint16(32, blockAlign, true);
  view.setUint16(34, 16, true); // BitsPerSample

  // data subchunk
  writeString(view, 36, "data");
  view.setUint32(40, dataLen, true);

  // PCM samples
  let offset = 44;
  for (let i = 0; i < float32Mono.length; i++, offset += 2) {
    let s = Math.max(-1, Math.min(1, float32Mono[i]));
    view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7fff, true);
  }
  return buffer;
}

function writeString(view, offset, str) {
  for (let i = 0; i < str.length; i++)
    view.setUint8(offset + i, str.charCodeAt(i));
}

onBeforeUnmount(() => {
  try {
    mediaRec?.stop();
  } catch {}
  mediaRec?.stream?.getTracks()?.forEach((t) => t.stop());
  clearInterval(timer);
});

const prettySize = computed(() => {
  if (!sizeBytes.value) return "";
  const mb = sizeBytes.value / (1024 * 1024);
  return mb >= 1 ? `${mb.toFixed(2)} MB` : `${(mb * 1024).toFixed(0)} KB`;
});
const mm = computed(() =>
  String(Math.floor(durationMs.value / 60000)).padStart(2, "0")
);
const ss = computed(() =>
  String(Math.floor((durationMs.value % 60000) / 1000)).padStart(2, "0")
);
const fileInput = ref(null);

function chooseWav() {
  asrError.value = "";
  asrText.value = "";
  fileInput.value?.click();
}

async function onPickWav(e) {
  const file = e.target.files?.[0];
  if (!file) return;
  // Strict .wav checks: extension + mime (mime can be inconsistent across OS/browsers, so check both)
  const nameOk = file.name.toLowerCase().endsWith(".wav");
  const typeOk =
    (file.type || "").toLowerCase() === "audio/wav" ||
    (file.type || "").toLowerCase() === "audio/x-wav";
  if (!nameOk && !typeOk) {
    asrError.value = "Please select a .wav file.";
    e.target.value = "";
    return;
  }
  if (file.size > MAX_BYTES) {
    asrError.value = "WAV too large (>25MB).";
    e.target.value = "";
    return;
  }

  asrLoading.value = true;
  try {
    const r = await asrTranscribeFile(file);
    asrText.value = `${r.text}\n\n(${r.runtime_ms} ms on ${r.device})`;
  } catch (err) {
    asrError.value = err?.message || "Transcription failed";
  } finally {
    asrLoading.value = false;
    // reset input so selecting the same file again re-triggers change
    e.target.value = "";
  }
}
</script>

<style scoped>
.audio {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.row {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}
.btn {
  padding: 6px 12px;
  border-radius: 10px;
  background: #111;
  color: #fff;
}
.btn.outline {
  background: #fff;
  color: #111;
  border: 1px solid #111;
}
.rec {
  color: #c0392b;
  font-weight: 600;
}
.dur {
  color: #555;
}
.err {
  color: #c0392b;
  margin: 4px 0;
}
.preview {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}
.link {
  background: none;
  border: none;
  padding: 0;
  color: #2563eb;
  cursor: pointer;
}
.meta {
  color: #777;
}
.asrStatus {
  color: #555;
}
.asrOut pre {
  white-space: pre-wrap;
  background: #f7f7f7;
  padding: 8px;
  border-radius: 8px;
}
</style>
