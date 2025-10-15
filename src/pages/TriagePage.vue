<template>
  <section class="wrap">
    <h2>Symptom Input</h2>

    <!-- 语言切换：选择 Warlpiri 后，用户的输入会先 translate 再 nlp -->
    <div class="lang-switch">
      <button class="btn outline" :class="{on: lang==='en'}"  :disabled="busy" @click="setLang('en')">English</button>
      <button class="btn outline" :class="{on: lang==='wbp'}" :disabled="busy" @click="setLang('wbp')">Warlpiri</button>
    </div>

    <!-- 分页器：1 图片；2 聊天 -->
    <div class="pager">
      <button :class="{on: step===1}" @click="goStep(1)">1 Images</button>
      <button :class="{on: step===2}" @click="goStep(2)">2 Chat</button>
    </div>

    <!-- STEP 1：图片输入 -->
    <div v-if="step===1" class="card">
      <h3>Select images (multi-select)</h3>
      <SymptomImagePicker v-model="images" />

      <div class="tags" v-if="images.length">
        <button v-for="k in images" :key="k" class="tag" @click="removeImg(k)">
          {{ labelOf(k) }} <span class="x">×</span>
        </button>
      </div>
      <small class="muted" v-else>Click images to select; click tag × to remove.</small>

      <div class="actions">
        <button class="btn primary" @click="goStep(2)">Next</button>
      </div>
    </div>

    <!-- STEP 2：聊天机器人 -->
    <div v-else-if="step===2" class="card">
      <h3>Chatbot Intake</h3>

      <!-- 聊天窗口 -->
      <div class="chat">
        <div v-for="(m, i) in chat" :key="i" :class="['bubble', m.role]">
          <div class="bubble-inner">
            <template v-if="m.role==='bot' && m.meta">
              <p v-if="m.meta.type==='summary'"><strong>Detected symptoms:</strong> {{ m.meta.pretty || '(none)' }}</p>
            </template>
            <p v-for="(line, idx) in toLines(m.text)" :key="idx">{{ line }}</p>
          </div>
        </div>
      </div>

      <!-- 输入区：文本 + 语音 + 控件 -->
      <div class="composer">
        <input
          v-model="draft"
          type="text"
          class="input"
          :placeholder="composerPlaceholder"
          :disabled="busy"
          @keyup.enter="send"
        />
        <button class="btn primary" :disabled="busy" @click="send">Send</button>

        <!-- 语音录制按钮：录完自动转写 +（若 wbp）翻译 + NLP -->
        <AudioCapture :disabled="busy" @recorded="onAudioRecorded" />
        <!-- 这里根据 readyToSubmit 切换文案：发送完就变成 Next -->
        <button class="btn outline" :disabled="busy" @click="onNextOrSkip">{{ readyToSubmit ? 'Next' : 'Skip' }}</button>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useTriageStore } from '@/store/triageStore'
import SymptomImagePicker from '@/components/SymptomImagePicker.vue'
import AudioCapture from '@/components/AudioCapture.vue'
import { translate, nlpProcessTexts, asrTranscribeFile, submitSymptoms } from '@/services/api'

/** ───────── 基础状态 ───────── */
const router = useRouter()
const store = useTriageStore()
const busy = ref(false)

const lang = ref(localStorage.getItem('locale') || 'en')
function setLang(l){ lang.value = l; localStorage.setItem('locale', l) }

const step = ref(1)
function goStep(n){
  step.value = n
  if (n === 2 && chat.value.length === 0) bootChat()
}

/** ───────── 图片输入 ───────── */
const images = computed({
  get: () => store.selectedSymptoms || [],
  set: (v) => store.setSelectedSymptoms?.(v),
})
function removeImg(k){
  if (typeof store.removeSymptom === 'function') store.removeSymptom(k)
  else images.value = (images.value || []).filter(x => x !== k)
}
const keyToLabel = {
  abdominal_pain:'Abdominal pain', fever_high:'Fever', cough:'Cough', sore_throat:'Sore throat',
  headache:'Headache', nausea:'Nausea', vomit:'Vomit', diarrhea:'Diarrhea',
  chest_pain:'Chest pain', short_breath:'Shortness of breath', rash:'Rash', fatigue:'Fatigue',
}
const labelOf = (k) => keyToLabel[k] || k

/** ───────── 聊天逻辑 ───────── */
const chat = ref([])            // { role:'bot'|'user', text:string, meta?:any }[]
const draft = ref('')
const audioText = ref('')       // 语音转写留存
const stage = ref('askFeeling') // 'askFeeling' | 'askSymptoms'
const extracted = ref([])       // 从文本/语音抽取到的症状（key）
const readyToSubmit = ref(false) // 只要做过一次 NLP，就把 Skip 变成 Next

function bootChat(){
  pushBot('How are you feeling right now? (e.g., worried, okay, very unwell)')
  stage.value = 'askFeeling'
}
function pushBot(text, meta){ chat.value.push({ role:'bot', text, meta }) }
function pushUser(text){ chat.value.push({ role:'user', text }) }
function toLines(t){ return String(t).split('\n') }

const composerPlaceholder = computed(()=>{
  return stage.value === 'askSymptoms'
    ? 'Please describe your symptoms (e.g., fever, sore throat, cough)…'
    : 'Type your feeling (e.g., worried / okay / very unwell)…'
})

/** ───────── 安全封装（不改 api.js）───────── */
async function translateToEnglishIfNeeded(text){
  if (!text) return ''
  if (lang.value !== 'wbp') return text
  try{
    const res = await translate(text) // Warlpiri -> English
    return res?.translation || res?.text || text
  }catch(e){
    console.error('translate error:', e)
    return text
  }
}
function normalizeSymptomsShape(data){
  if (Array.isArray(data?.symptoms)) return data.symptoms.map(String)
  if (Array.isArray(data?.results)) {
    const arr = data.results
    if (arr.every(x => typeof x === 'string')) return arr
    const f = arr[0]
    if (Array.isArray(f?.symptoms)) return f.symptoms.map(String)
    if (Array.isArray(f?.entities)) return f.entities.map(String)
  }
  if (Array.isArray(data?.entities)) return data.entities.map(String)
  return null
}
function regexFallback(raw){
  const t = String(raw).toLowerCase()
  const map = [
    ['fever_high',      /(fever|high temperature)/],
    ['sore_throat',     /(sore throat|throat pain)/],
    ['cough',           /\bcough(ing)?\b/],
    ['headache',        /\bheadache\b/],
    ['nausea',          /\bnausea|nauseous\b/],
    ['vomit',           /\bvomit(ing)?\b/],
    ['diarrhea',        /\bdiarrh?ea\b/],
    ['chest_pain',      /(chest pain|tight chest)/],
    ['short_breath',    /(short(ness)? of breath|breath(ing)? difficulty)/],
    ['rash',            /\brash\b/],
    ['fatigue',         /\bfatigue|tired(ness)?\b/],
    ['abdominal_pain',  /(abdominal|stomach|belly) (pain|ache)/],
  ]
  return map.filter(([k,re]) => re.test(t)).map(([k])=>k)
}
async function extractByNlp(rawText){
  try{
    const data = await nlpProcessTexts(rawText || '')
    const arr = normalizeSymptomsShape(data)
    return Array.isArray(arr) ? arr : regexFallback(rawText)
  }catch(e){
    console.error('nlpProcessTexts error:', e)
    return regexFallback(rawText)
  }
}
async function transcribeAndMaybeTranslate(blob){
  try{
    const out = await asrTranscribeFile(blob) // { text }
    const raw = out?.text || ''
    const translated = await translateToEnglishIfNeeded(raw)
    return { raw, translated }
  }catch(e){
    console.error('asrTranscribeFile error:', e)
    return { raw:'', translated:'' }
  }
}

/** ───────── 发送/流程控制 ───────── */
async function send(){
  const userText = (draft.value || '').trim()
  if (!userText || busy.value) return
  pushUser(userText)
  draft.value = ''
  busy.value = true

  try{
    if (stage.value === 'askFeeling') {
      // 记录 feeling 备注（可合并进 textInput）
      store.setText?.([store.textInput, `Feeling: ${userText}`].filter(Boolean).join('\n'))
      pushBot('Please describe your symptoms. You can list multiple items.')
      stage.value = 'askSymptoms'
      await scrollToBottom()
      return
    }

    if (stage.value === 'askSymptoms') {
      // 若为 wbp，先翻成英文，再抽取
      const textForNlp = await translateToEnglishIfNeeded(userText)
      const found = await extractByNlp(textForNlp)

      // 累加/去重
      const set = new Set([...(extracted.value||[]), ...found])
      extracted.value = Array.from(set)

      // 反馈 + 摘要
      if (userText !== textForNlp) {
        pushBot(`Translated: ${textForNlp}`)
      }
      if (found.length) {
        pushBot(`Got it. I captured: ${found.map(labelOf).join(', ')}.`)
      } else {
        pushBot('Thanks. I did not detect specific symptom keywords.')
      }
      pushBot('', { type:'summary', pretty: prettySymptoms.value })

      // 关键：已具备提交条件，切换按钮为 Next
      readyToSubmit.value = true
      await scrollToBottom()
      return
    }
  } finally {
    busy.value = false
  }
}

// Skip / Next 的统一点击
function onNextOrSkip(){
  if (!readyToSubmit.value) {
    // 仍在初期流程：按原 Skip 行为
    if (stage.value === 'askFeeling') {
      pushBot('OK. Please describe your symptoms.')
      stage.value = 'askSymptoms'
    } else if (stage.value === 'askSymptoms') {
      pushBot('No problem. You can still add more later.')
      pushBot('', { type:'summary', pretty: prettySymptoms.value })
      readyToSubmit.value = true
    }
    nextTick(scrollToBottom)
  } else {
    // 已经完成一次提取：点击即提交并跳结果页
    submitAndGo()
  }
}

async function onAudioRecorded(blob){
  if (busy.value) return
  busy.value = true
  try{
    // 1) 语音转写
    const { raw, translated } = await transcribeAndMaybeTranslate(blob)
    if (!raw) { pushBot('Audio transcription failed.'); return }
    pushUser(`[Voice] ${raw}`)
    if (translated && translated !== raw) pushBot(`Translated: ${translated}`)

    // 2) NLP 抽取
    const textForNlp = translated || raw
    const found = await extractByNlp(textForNlp)
    const set = new Set([...(extracted.value||[]), ...found])
    extracted.value = Array.from(set)

    // 3) 反馈 + 摘要 + 切换按钮
    if (found.length) pushBot(`Got it. I captured: ${found.map(labelOf).join(', ')}.`)
    pushBot('', { type:'summary', pretty: prettySymptoms.value })
    readyToSubmit.value = true
    await scrollToBottom()
  } finally {
    busy.value = false
  }
}

/** ───────── 提交后端并跳结果页 ───────── */
async function submitAndGo(){
  if (busy.value) return
  busy.value = true
  try{
    const merged = Array.from(new Set([...(images.value||[]), ...(extracted.value||[])]))
    store.setSelectedSymptoms?.(merged)

    const payload = {
      language: lang.value,
      symptoms: merged,
      text: store.textInput || '',
      transcript: audioText.value || ''
    }
    const resp = await submitSymptoms(payload)
    if (store.setLastReport) store.setLastReport(resp)
    else store.lastReport = resp
    router.push('/predict')
  }catch(e){
    console.error(e)
    pushBot('Submit failed. Please try again later.')
  }finally{
    busy.value = false
  }
}

const prettySymptoms = computed(() => {
  const merged = Array.from(new Set([...(images.value||[]), ...(extracted.value||[])]))
  return merged.length ? merged.map(labelOf).join(', ') : '(none)'
})

async function scrollToBottom(){
  await nextTick()
  const box = document.querySelector('.chat')
  if (box) box.scrollTop = box.scrollHeight
}

onMounted(() => {
  if (step.value === 2) bootChat()
})
</script>

<style scoped>
/* layout */
.wrap{max-width:980px;margin:0 auto}
.lang-switch{display:flex;gap:8px;margin-bottom:10px}
.lang-switch .btn.on{background:#2e7d32;color:#fff;border-color:#2e7d32}

.pager{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px}
.pager button{
  border-radius:999px;padding:6px 12px;cursor:pointer;
  border:1px solid #2e7d32;background:transparent;color:#2e7d32;
  transition:box-shadow .12s ease, transform .08s ease;
}
.pager button.on{background:#2e7d32;color:#fff;box-shadow:0 2px 8px rgba(0,0,0,.08)}
.pager button:hover{transform:translateY(-1px);box-shadow:0 2px 10px rgba(0,0,0,.1)}

.card{border:1px solid var(--border);border-radius:12px;padding:14px;background:var(--card);margin-bottom:16px}

/* Chat window (比背景更亮一点) */
.chat{
  height: 340px; overflow:auto; padding:12px;
  border:1px solid #cfe6cf; border-radius:16px;
  background: linear-gradient(180deg, rgba(255,255,255,.85), rgba(255,255,255,.75));
  box-shadow: 0 6px 18px rgba(0,0,0,.06) inset;
}

/* Bubbles */
.bubble{display:flex; margin:12px 0}
.bubble .bubble-inner{
  padding:10px 14px; border-radius:14px; max-width:80%;
  border:1px solid var(--border);
  white-space:pre-wrap; word-break:break-word;
  box-shadow:0 2px 6px rgba(0,0,0,.06);
  transition:transform .08s ease, box-shadow .12s ease;
}

/* Bot bubble：浅色奶白/薄荷，和页面背景明显区分 */
.bubble.bot .bubble-inner{
  background: linear-gradient(135deg, #ffffff, #f3fff1);
  border-color:#e2f3de;
  color:#183a2b;
}
.bubble.bot .bubble-inner:hover{ box-shadow:0 3px 10px rgba(0,0,0,.08) }

/* User bubble：深绿渐变，白字 */
.bubble.user{justify-content:flex-end}
.bubble.user .bubble-inner{
  background: linear-gradient(135deg, #2e7d32, #1f5f24);
  color:#fff; border-color:#236d28;
}
.bubble.user .bubble-inner:hover{ box-shadow:0 4px 12px rgba(46,125,50,.35) }

/* 输入区 */
.composer{display:flex; gap:10px; margin-top:12px; align-items:center}
.input{
  flex:1; padding:10px 12px; border:2px solid rgba(0,0,0,.18);
  border-radius:12px; background:rgba(255,255,255,.88); outline:none;
  transition:border-color .12s ease, box-shadow .12s ease, background .12s ease;
}
.input:focus{
  border-color:#2e7d32;
  box-shadow:0 0 0 3px color-mix(in srgb, #2e7d32 22%, transparent);
  background:#fff;
}
.muted{color:var(--muted)}

/* Buttons — 仅作用于聊天区域的 Send / Skip(Next) */
.composer .btn{
  padding:10px 14px;border-radius:12px;cursor:pointer;
  transition:transform .08s ease, box-shadow .12s ease, background .12s ease, color .12s ease, border-color .12s ease;
}

/* Send：更醒目的深绿渐变 */
.composer .btn.primary{
  background: linear-gradient(135deg, #2e7d32, #1f5f24);
  color:#fff;border:1px solid #215b2b;
  box-shadow:0 4px 10px rgba(33,91,43,.18);
}
.composer .btn.primary:hover{ transform:translateY(-1px); box-shadow:0 6px 14px rgba(33,91,43,.25) }
.composer .btn.primary:active{ transform:translateY(0) }

/* Skip/Next：浅色底 + 绿色描边，悬停填充淡绿以对比 */
.composer .btn.outline{
  background:#ffffff; color:#2e7d32; border:2px solid #2e7d32;
  box-shadow:0 2px 8px rgba(0,0,0,.05);
}
.composer .btn.outline:hover{
  background: #e9f7ea; /* 淡绿 */
}
.composer .btn.outline:active{ transform:translateY(0) }
</style>

