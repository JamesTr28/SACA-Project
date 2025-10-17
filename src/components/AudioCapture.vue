<template>
  <div class="ac-root">
    <div class="ac-controls">
      <button class="btn primary" :disabled="recording || disabled" @click="start">▶ Start recording</button>
      <button class="btn outline"  :disabled="!recording" @click="stop">■ Stop</button>

      <label class="btn outline file">
        ↰ Upload .wav (demo)
        <input type="file" accept=".wav,audio/wav" @change="onFile" hidden />
      </label>
    </div>

    <div class="ac-hint">
      <span v-if="statusText">{{ statusText }}</span>
      <span v-else-if="!recording">Select a local .wav file to transcribe</span>
      <span v-else>Recording… {{ mm }}:{{ ss }}</span>
    </div>

    <div class="ac-progress" v-if="recording">
      <div class="bar" :style="{ width: pct + '%' }"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted } from 'vue'
import { asrTranscribeFile } from '@/services/api'

const emit = defineEmits(['recorded','transcript'])

const MAX_SEC = 30
const MIN_SEC = 2
const elapsedSec = ref(0)
let timer = null
const mm = computed(() => String(Math.floor(elapsedSec.value/60)).padStart(2,'0'))
const ss = computed(() => String(elapsedSec.value%60).padStart(2,'0'))
const pct = computed(() => Math.min(100, Math.round(elapsedSec.value*100/MAX_SEC)))

const recording = ref(false)

let audioCtx = null, sourceNode = null, processor = null, stream = null
let chunks = []
const TARGET_SR = 16000

async function start(){
  if (recording.value) return
  console.log('[AudioCapture] start: requesting mic')
  try{
    stream = await navigator.mediaDevices.getUserMedia({ audio:true })
    audioCtx = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: TARGET_SR })
    console.log('[AudioCapture] using AudioContext sr=', audioCtx.sampleRate)
    sourceNode = audioCtx.createMediaStreamSource(stream)

    // 兼容方案：ScriptProcessor（简单稳定），后续可换 AudioWorklet
    processor = audioCtx.createScriptProcessor(4096, 1, 1)
    processor.onaudioprocess = (e) => {
      const ch0 = e.inputBuffer.getChannelData(0)
      chunks.push(new Float32Array(ch0))
    }
    sourceNode.connect(processor)
    processor.connect(audioCtx.destination)

    elapsedSec.value = 0
    timer = setInterval(() => {
      elapsedSec.value++
      if (elapsedSec.value >= MAX_SEC) stop()
    }, 1000)

    recording.value = true
  }catch(err){
    console.error('[AudioCapture] mic init failed:', err)
  }
}

function stop(){
  if (!recording.value) return
  console.log('[AudioCapture] stop')
  try{
    sourceNode && sourceNode.disconnect()
    processor && processor.disconnect()
    stream?.getTracks()?.forEach(t=>t.stop())
    audioCtx && audioCtx.close()
  }catch(e){}
  clearInterval(timer)
  recording.value = false

  if (elapsedSec.value < MIN_SEC || chunks.length === 0) {
    console.warn('[AudioCapture] recording too short:', elapsedSec.value, 's; discard.')
    chunks = []
    return
  }

  const pcm = mergeFloat32(chunks)
  const wav = toWav(pcm, TARGET_SR)
  console.log('[AudioCapture] wav ready. size=', wav.size)
  chunks = []
  emit('recorded', wav)
  transcribe(wav) // 这里一定会调到 api.asrTranscribeFile
}

async function onFile(e){
  const f = e.target.files?.[0]
  if (!f) return
  console.log('[AudioCapture] upload file:', f.name, f.type, f.size)
  emit('recorded', f)
  await transcribe(f)
  e.target.value = ''
}

async function transcribe(blob){
  try{
    console.log('[AudioCapture] transcribe()…')
    const res = await asrTranscribeFile(blob)
    const text = (res?.text || '').trim()
    console.log('[AudioCapture] transcribe <-', text)
    if (text) emit('transcript', text)
  }catch(err){
    console.error('[AudioCapture] transcribe failed:', err)
  }
}

onUnmounted(() => {
  try{ stream?.getTracks()?.forEach(t=>t.stop()) }catch(_){}
})

function mergeFloat32(arrs){
  let len = 0; for (const a of arrs) len += a.length
  const out = new Float32Array(len)
  let off = 0
  for (const a of arrs){ out.set(a, off); off += a.length }
  return out
}
function toWav(float32, rate){
  const bytesPerSample = 2, numCh = 1, blockAlign = numCh*bytesPerSample
  const buffer = new ArrayBuffer(44 + float32.length*bytesPerSample)
  const view = new DataView(buffer)
  writeStr(view,0,'RIFF'); view.setUint32(4,36+float32.length*bytesPerSample,true)
  writeStr(view,8,'WAVE'); writeStr(view,12,'fmt ')
  view.setUint32(16,16,true); view.setUint16(20,1,true)
  view.setUint16(22,numCh,true); view.setUint32(24,rate,true)
  view.setUint32(28,rate*blockAlign,true); view.setUint16(32,blockAlign,true)
  view.setUint16(34,16,true); writeStr(view,36,'data')
  view.setUint32(40,float32.length*bytesPerSample,true)
  floatTo16(view,44,float32)
  return new Blob([view],{type:'audio/wav'})
}
function writeStr(v,o,s){ for(let i=0;i<s.length;i++) v.setUint8(o+i,s.charCodeAt(i)) }
function floatTo16(v,o,inp){
  for(let i=0;i<inp.length;i++,o+=2){
    let s = Math.max(-1, Math.min(1, inp[i]))
    v.setInt16(o, s<0 ? s*0x8000 : s*0x7FFF, true)
  }
}
</script>


<style scoped>
.ac-root{
  width:100%;
  display:flex; align-items:center; gap:12px;
  border:2px solid #cfe6cf; border-radius:12px; background:#fff; padding:12px;
  box-shadow:0 2px 8px rgba(0,0,0,.04) inset; flex-wrap:wrap;
}
.ac-controls{ display:flex; gap:10px; align-items:center; flex-wrap:wrap; }
.ac-hint{ margin-left:auto; color:#555; font-size:.9em; white-space:nowrap; min-height:1em; }
.ac-progress{ width:100%; height:8px; border-radius:999px; background:#eaf6ea; overflow:hidden; }
.ac-progress .bar{ height:100%; background:#2e7d32; opacity:.85; transition:width .2s ease; }
.btn{ padding:10px 14px; border-radius:12px; cursor:pointer; }
.btn.primary{ background:linear-gradient(135deg,#2e7d32,#1f5f24); color:#fff; border:1px solid #215b2b; }
.btn.outline{ background:#fff; color:#2e7d32; border:2px solid #2e7d32; }
.btn:disabled{ opacity:.6; cursor:not-allowed; }
.file{ display:inline-flex; align-items:center; gap:6px; }
</style>
