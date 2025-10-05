<template>
  <section class="wrap">
    <h2>VOICE INPUT</h2>
    <AudioCapture @recorded="onRecorded" />
    <div class="actions">
      <button class="btn primary" :disabled="submitting" @click="submit">{{ submitting ? 'Submitting…' : 'Submitted' }}</button>
      <button class="btn outline" :disabled="submitting" @click="clearAll">CLEAR</button>
    </div>

    <h3>RESULTS</h3>
    <ResultsPanel :report="report" :loading="submitting" :error="error" />
  </section>
  <div class="card">
    <h3>WAV Upload Demo</h3>
    <input ref="inp" type="file" accept=".wav,audio/wav,audio/x-wav" @change="onPick" />
    <p v-if="err" style="color:#b00020">{{ err }}</p>
    <p v-if="loading">Transcribing…</p>
    <pre v-if="out" style="white-space:pre-wrap">{{ out }}</pre>
  </div>
</template>

<script setup>
import { storeToRefs } from 'pinia'
import { useTriageStore } from '@/store/triageStore'
import AudioCapture from '@/components/AudioCapture.vue'
import ResultsPanel from '@/components/ResultsPanel.vue'

const store = useTriageStore()
const { submitting, error, lastReport: report } = storeToRefs(store)

function onRecorded(blob){ store.setAudio(blob) }
async function submit(){ await store.submitFromVoice() }
function clearAll(){ store.setAudio(null) }
// testing
import { ref } from "vue";
const loading = ref(false), out = ref(""), err = ref("");

async function onPick(e) {
  const file = e.target.files?.[0];
  console.log("[demo] picked:", file);
  err.value = ""; out.value = "";
  if (!file) return;

  const ok = file.name.toLowerCase().endsWith(".wav") ||
             (file.type || "").toLowerCase().includes("wav");
  if (!ok) { err.value = "Please select a .wav file."; return; }

  loading.value = true;
  try {
    console.log("[demo] sending fetch…");
    const fd = new FormData();
    fd.append("audio", file); // must be 'audio'
    const res = await fetch(`${import.meta.env.VITE_API_BASE || "http://localhost:8000"}/asr/transcribe`, {
      method: "POST",
      body: fd, // don't set Content-Type for FormData
    });
    console.log("[demo] status:", res.status);
    const j = await res.json().catch(() => ({}));
    console.log("[demo] json:", j);
    if (!res.ok) throw new Error(j?.detail || `HTTP ${res.status}`);
    out.value = `${j.text}\n\n(${j.runtime_ms} ms on ${j.device})`;
  } catch (e2) {
    console.error(e2);
    err.value = e2.message || String(e2);
  } finally {
    loading.value = false;
    e.target.value = ""; // allow re-selecting same file
  }
}
</script>

<style scoped>
.wrap{max-width:900px;margin:0 auto}
.actions{display:flex;gap:8px;margin:12px 0}
.btn.primary{background:var(--btn-bg);color:var(--btn-fg);border:none;padding:10px 14px;border-radius:10px}
.btn.outline{background:var(--btn-outline-bg);color:var(--btn-outline-fg);border:1px solid var(--btn-outline-border);padding:10px 14px;border-radius:10px}
</style>
