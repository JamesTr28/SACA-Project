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
</script>

<style scoped>
.wrap{max-width:900px;margin:0 auto}
.actions{display:flex;gap:8px;margin:12px 0}
.btn.primary{background:var(--btn-bg);color:var(--btn-fg);border:none;padding:10px 14px;border-radius:10px}
.btn.outline{background:var(--btn-outline-bg);color:var(--btn-outline-fg);border:1px solid var(--btn-outline-border);padding:10px 14px;border-radius:10px}
</style>
