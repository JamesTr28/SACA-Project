<template>
  <div class="audio">
    <div class="row">
      <button class="btn" :disabled="recording" @click="start">
        ▶ Start recording
      </button>
      <button class="btn outline" :disabled="!recording" @click="stop">
        ■ Stop
      </button>

      <span v-if="recording" class="rec">● recording {{ mm }}:{{ ss }}</span>
      <span v-else-if="durationMs>0" class="dur">⏱ {{ mm }}:{{ ss }}</span>
    </div>

    <p v-if="err" class="err">{{ err }}</p>

    <div v-if="url" class="preview">
      <audio :src="url" controls></audio>
      <button class="link" @click="reset">Re-record</button>
      <small class="meta">~{{ prettySize }} • {{ mime }}</small>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onBeforeUnmount } from 'vue'

const emit = defineEmits(['recorded'])
const recording = ref(false)
const err = ref('')
const url = ref('')
const mime = ref('audio/webm')
const durationMs = ref(0)
const sizeBytes = ref(0)

let mediaRec, timer, startedAt = 0
const chunks = []

const MAX_MS = 60_000
const MAX_BYTES = 10 * 1024 * 1024

function tick() {
  durationMs.value = Date.now() - startedAt
  if (durationMs.value >= MAX_MS) stop()
}

async function start() {
  err.value = ''
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    const type = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
      ? 'audio/webm;codecs=opus'
      : 'audio/webm'
    mime.value = type

    mediaRec = new MediaRecorder(stream, { mimeType: type })
    chunks.length = 0
    mediaRec.ondataavailable = (e) => { if (e.data?.size) chunks.push(e.data) }
    mediaRec.onstop = () => {
      const blob = new Blob(chunks, { type })
      sizeBytes.value = blob.size
      url.value = URL.createObjectURL(blob)
      if (blob.size > MAX_BYTES) {
        err.value = 'Audio too large (>10MB). Please record again.'
        reset(false)
        return
      }
      emit('recorded', blob)
    }

    mediaRec.start()
    recording.value = true
    startedAt = Date.now()
    durationMs.value = 0
    clearInterval(timer)
    timer = setInterval(tick, 200)
  } catch (e) {
    err.value = e?.message || 'Cannot access microphone'
  }
}

function stop() {
  try { mediaRec?.stop() } catch {}
  recording.value = false
  clearInterval(timer)
  // 停止各 track
  mediaRec?.stream?.getTracks()?.forEach(t => t.stop())
}

function reset(clearEvent = true) {
  URL.revokeObjectURL(url.value)
  url.value = ''
  sizeBytes.value = 0
  durationMs.value = 0
  if (clearEvent) emit('recorded', null)
}

onBeforeUnmount(() => {
  try { mediaRec?.stop() } catch {}
  mediaRec?.stream?.getTracks()?.forEach(t => t.stop())
  clearInterval(timer)
})

const prettySize = computed(() => {
  if (!sizeBytes.value) return ''
  const mb = sizeBytes.value / (1024 * 1024)
  return mb >= 1 ? `${mb.toFixed(2)} MB` : `${(mb*1024).toFixed(0)} KB`
})
const mm = computed(() => String(Math.floor(durationMs.value / 60000)).padStart(2,'0'))
const ss = computed(() => String(Math.floor((durationMs.value % 60000) / 1000)).padStart(2,'0'))
</script>

<style scoped>
.audio{display:flex;flex-direction:column;gap:8px}
.row{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.btn{padding:6px 12px;border-radius:10px;background:#111;color:#fff}
.btn.outline{background:#fff;color:#111;border:1px solid #111}
.rec{color:#c0392b;font-weight:600}
.dur{color:#555}
.err{color:#c0392b;margin:4px 0}
.preview{display:flex;gap:12px;align-items:center;flex-wrap:wrap}
.link{background:none;border:none;padding:0;color:#2563eb;cursor:pointer}
.meta{color:#777}
</style>
