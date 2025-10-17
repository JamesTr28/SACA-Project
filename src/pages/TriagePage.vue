<template>
  <section class="wrap">
    <h2>Intake (Chat)</h2>

    <!-- 语言切换 -->
    <div class="lang-switch">
      <button class="btn outline" :class="{on: lang==='en'}"  :disabled="busy" @click="setLang('en')">English</button>
      <button class="btn outline" :class="{on: lang==='wbp'}" :disabled="busy" @click="setLang('wbp')">Warlpiri</button>
    </div>

    <!-- 聊天窗口 -->
    <div class="card chat">
      <div v-for="(m, i) in chat" :key="i" :class="['bubble', m.role]">
        <div class="bubble-inner">
          <p v-for="(line, idx) in toLines(m.text)" :key="idx">{{ line }}</p>

          <!-- 通用选项 -->
          <div v-if="m.options?.length" class="opts">
            <button v-for="opt in m.options" :key="opt.key"
                    class="btn outline opt"
                    @click="onOption(opt)">
              {{ opt.label }}
            </button>
          </div>

          <!-- 性别二选一（禁用自由输入） -->
          <div v-if="m.type==='gender'" class="opts">
            <button class="btn outline opt" @click="selectGender(1)">Male</button>
            <button class="btn outline opt" @click="selectGender(0)">Female</button>
          </div>

          <!-- 图片多选路径 -->
          <div v-if="m.type==='images'" class="images">
            <SymptomImagePicker v-model="imagesTmp" />
            <div class="actions">
              <button class="btn primary" @click="confirmImages">Confirm</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 输入区：有选项/性别/图片时禁用自由输入 -->
    <div class="composer">
      <input
        v-model="draft"
        type="text"
        class="input"
        :placeholder="placeholder"
        :disabled="inputDisabled || busy"
        @keyup.enter="send"
      />
      <button class="btn primary send" :disabled="inputDisabled || busy" @click="send">Send</button>

      <!-- 仅在症状阶段展示语音 -->
      <AudioCapture v-if="stage==='symptoms' && !inputDisabled" :disabled="busy" @recorded="onAudioRecorded" />
      <button class="btn outline skip" :disabled="busy" @click="skip">{{ skipText }}</button>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, nextTick, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useTriageStore } from '@/store/triageStore'
import { translate, nlpProcessTexts, asrTranscribeFile } from '@/services/api'
import SymptomImagePicker from '@/components/SymptomImagePicker.vue'
import AudioCapture from '@/components/AudioCapture.vue'

const router = useRouter()
const store  = useTriageStore()
const busy   = ref(false)

/* ---------- 语言切换（保存到 localStorage） ---------- */
const lang = ref(localStorage.getItem('locale') || 'en')
function setLang(l){ lang.value = l; localStorage.setItem('locale', l) }

/* ---------- 会话与阶段 ---------- */
const chat   = ref([])            // { role:'bot'|'user', text, options?, type? }
const draft  = ref('')
const stage  = ref('greet')       // 'greet'|'collect_gender'|'collect_age'|'collect_weight'|'collect_cond'|'collect_allergy'|'collect_meds'|'symptoms'|'ask_more'|'image_flow'
const optionMode = ref(false)     // 显示选项/专用控件时禁用输入
const imagesTmp = ref([])

function toLines(t){ return String(t).split('\n') }
function pushBot(text, options=null, type=null){
  optionMode.value = !!(options && options.length) || !!type
  chat.value.push({ role:'bot', text, options, type })
  scroll()
}
function pushUser(text){ chat.value.push({ role:'user', text }); scroll() }
async function scroll(){ await nextTick(); const el=document.querySelector('.chat'); if(el) el.scrollTop=el.scrollHeight }

/* 初始问候：放到 onMounted，避免热更新重复注入 */
onMounted(() => {
  if (chat.value.length === 0) {
    pushBot("Hi, I'm your assistant. How would you like to describe your issue?", [
      { key:'text',  label:'Text NLP' },
      { key:'image', label:'Image selection' }
    ])
  }
})

/* ---------- store 兜底工具 ---------- */
function safeSetProfileField(key, value){
  if (typeof store.setProfileField === 'function') store.setProfileField(key, value)
  else {
    store.profile = { ...(store.profile||{}), [key]: value }
  }
}
function safeSetSelectedSymptoms(arr){
  const dedup = Array.from(new Set(arr||[]))
  if (typeof store.setSelectedSymptoms === 'function') store.setSelectedSymptoms(dedup)
  else store.selectedSymptoms = dedup
}
function safeAddSymptoms(keys){
  const current = store.selectedSymptoms || []
  safeSetSelectedSymptoms([ ...current, ...(keys||[]) ])
}

/* ---------- 选项处理 ---------- */
function onOption(opt){
  optionMode.value = false
  pushUser(opt.label)

  if (stage.value==='greet' || stage.value==='greet_done') {
    if (opt.key === 'text') {
      stage.value = 'collect_gender'
      pushBot('Please select your gender.', null, 'gender')
    } else {
      stage.value = 'image_flow'
      pushBot('Please select symptom images (multi-select).', null, 'images')
    }
    return
  }

  if (stage.value==='ask_more') {
    if (opt.key === 'no') router.push('/confirm')
    else { stage.value='symptoms'; pushBot('Please describe additional symptoms (text or voice).') }
  }
}

/* ---------- 性别专用选项 ---------- */
function selectGender(code){
  optionMode.value = false
  pushUser(code === 1 ? 'Male' : 'Female')
  safeSetProfileField('gender', code)
  stage.value = 'collect_age'
  pushBot('Your age? (years)')
}

/* ---------- 图片路径确认 ---------- */
function confirmImages(){
  safeSetSelectedSymptoms(imagesTmp.value)
  router.push('/confirm')
}

/* ---------- 输入框联动 ---------- */
const inputDisabled = computed(()=> optionMode.value)
const placeholder = computed(()=>{
  if (inputDisabled.value) return 'Please choose from options above'
  switch(stage.value){
    case 'collect_age': return 'Enter your age (e.g., 32)'
    case 'collect_weight': return 'Enter your weight (kg)'
    case 'collect_cond': return 'Any past medical conditions?'
    case 'collect_allergy': return 'Any allergies?'
    case 'collect_meds': return 'Current medications?'
    case 'symptoms': return lang.value==='wbp'
      ? 'Type in Warlpiri or English… (voice supported)'
      : 'Please describe your symptoms… (voice supported)'
    default: return 'Type here…'
  }
})
const skipText = computed(()=> stage.value==='symptoms' ? 'Skip' : 'Next')

/* ---------- NLP & 翻译封装（保留语言切换） ---------- */
async function translateToEnglishIfNeeded(text){
  if (!text) return ''
  if (lang.value !== 'wbp') return text
  try{
    const res = await translate(text)   // Warlpiri -> English
    return res?.translation || res?.text || text
  }catch{ return text }
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
    ['fever_high',/(fever|high temperature)/],
    ['sore_throat',/(sore throat|throat pain)/],
    ['cough',/\bcough(ing)?\b/],
    ['headache',/\bheadache\b/],
    ['nausea',/\bnausea|nauseous\b/],
    ['vomit',/\bvomit(ing)?\b/],
    ['diarrhea',/\bdiarrh?ea\b/],
    ['chest_pain',/(chest pain|tight chest)/],
    ['short_breath',/(short(ness)? of breath|breath(ing)? difficulty)/],
    ['rash',/\brash\b/],
    ['fatigue',/\bfatigue|tired(ness)?\b/],
    ['abdominal_pain',/(abdominal|stomach|belly) (pain|ache)/],
  ]
  return map.filter(([k,re])=>re.test(t)).map(([k])=>k)
}
async function safeNlp(text){
  try{
    const r = await nlpProcessTexts(text || '')
    const arr = normalizeSymptomsShape(r)
    return Array.isArray(arr) ? arr : regexFallback(text)
  }catch{
    return regexFallback(text)
  }
}

/* ---------- 文本发送 ---------- */
async function send(){
  const text = (draft.value || '').trim()
  if (!text || busy.value || inputDisabled.value) return
  pushUser(text); draft.value=''

  if (stage.value==='collect_age') {
    safeSetProfileField('age', text)
    stage.value='collect_weight'; return pushBot('Your weight? (kg)')
  }
  if (stage.value==='collect_weight') {
    safeSetProfileField('weight', text)
    stage.value='collect_cond'; return pushBot('Any past medical conditions?')
  }
  if (stage.value==='collect_cond') {
    safeSetProfileField('conditions', text)
    stage.value='collect_allergy'; return pushBot('Any allergies?')
  }
  if (stage.value==='collect_allergy') {
    safeSetProfileField('allergies', text)
    stage.value='collect_meds'; return pushBot('Any current medications?')
  }
  if (stage.value==='collect_meds') {
    safeSetProfileField('medications', text)
    stage.value='symptoms'; return pushBot('Thanks. Now please describe your symptoms (text or voice).')
  }

  if (stage.value==='symptoms') {
    busy.value = true
    try{
      const forNlp = await translateToEnglishIfNeeded(text)
      const found  = await safeNlp(forNlp)
      if (lang.value==='wbp' && forNlp !== text) pushBot(`Translated: ${forNlp}`)
      if (found.length){
        safeAddSymptoms(found)
        pushBot(`Got it. I captured: ${found.map(labelOf).join(', ')}.`)
      }else{
        pushBot('Thanks. I did not detect specific symptom keywords.')
      }
      stage.value='ask_more'
      pushBot('Do you want to add more info?', [
        { key:'yes', label:'Yes' }, { key:'no', label:'No' }
      ])
    } finally { busy.value = false }
  }
}

/* ---------- Skip / Next ---------- */
function skip(){
  if (stage.value==='symptoms') {
    router.push('/confirm')
  } else {
    if (stage.value==='collect_age'){ stage.value='collect_weight'; pushBot('Your weight? (kg)'); return }
    if (stage.value==='collect_weight'){ stage.value='collect_cond'; pushBot('Any past medical conditions?'); return }
    if (stage.value==='collect_cond'){ stage.value='collect_allergy'; pushBot('Any allergies?'); return }
    if (stage.value==='collect_allergy'){ stage.value='collect_meds'; pushBot('Any current medications?'); return }
    if (stage.value==='collect_meds'){ stage.value='symptoms'; pushBot('Please describe your symptoms (text or voice).'); return }
  }
}

/* ---------- 语音（ASR→可选翻译→NLP） ---------- */
async function onAudioRecorded(blob){
  if (busy.value) return
  busy.value = true
  try{
    const out = await asrTranscribeFile(blob) // { text }
    const raw = out?.text || ''
    if (!raw) { pushBot('Audio transcription failed.'); return }
    pushUser(`[Voice] ${raw}`)

    const forNlp = await translateToEnglishIfNeeded(raw)
    if (lang.value==='wbp' && forNlp !== raw) pushBot(`Translated: ${forNlp}`)
    const found = await safeNlp(forNlp)
    if (found.length){
      safeAddSymptoms(found)
      pushBot(`Got it. I captured: ${found.map(labelOf).join(', ')}.`)
    }
    stage.value='ask_more'
    pushBot('Do you want to add more info?', [
      { key:'yes', label:'Yes' }, { key:'no', label:'No' }
    ])
  } finally { busy.value=false }
}

/* 标签名展示 */
const keyToLabel = {
  abdominal_pain:'Abdominal pain', fever_high:'Fever', cough:'Cough', sore_throat:'Sore throat',
  headache:'Headache', nausea:'Nausea', vomit:'Vomit', diarrhea:'Diarrhea',
  chest_pain:'Chest pain', short_breath:'Shortness of breath', rash:'Rash', fatigue:'Fatigue',
}
function labelOf(k){ return keyToLabel[k] || k }
</script>

<style scoped>
/* 布局 */
.wrap{max-width:980px;margin:0 auto}

/* 语言切换 */
.lang-switch{display:flex;gap:8px;margin-bottom:10px}
.lang-switch .btn{padding:6px 12px;border-radius:999px}
.lang-switch .btn.on{background:#2e7d32;color:#fff;border-color:#2e7d32}

/* 聊天窗口：奶白渐变背景 + 清晰边框 + 内阴影 */
.card.chat{
  border:1px solid #cfe6cf;
  border-radius:16px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.579), rgba(245,255,245,.86));
  box-shadow: inset 0 6px 18px rgba(0,0,0,.06);
  padding:12px; height:420px; overflow:auto;
}

/* 气泡 */
.bubble{display:flex;margin:12px 0}
.bubble .bubble-inner{
  max-width:80%;
  padding:10px 14px; border-radius:14px;
  white-space:pre-wrap; word-break:break-word;
  border:1px solid #dbeed8; background:#f7fff6; color:#183a2b;
  box-shadow:0 2px 6px rgba(0,0,0,.06);
}
.bubble.user{justify-content:flex-end}
.bubble.user .bubble-inner{
  background: linear-gradient(135deg, #2e7d32, #1f5f24);
  color:#fff; border:1px solid #215b2b;
  box-shadow:0 4px 12px rgba(33,91,43,.25);
}

/* 选项按钮组 */
.opts{display:flex;gap:8px;flex-wrap:wrap;margin-top:8px}
.opt{border-width:2px}

/* 图片区域微分隔 */
.images{margin-top:8px}

/* 输入区 */
.composer{display:flex;gap:10px;align-items:center;margin-top:12px}
.input{
  flex:1; padding:10px 12px;
  border:2px solid #cfe6cf; border-radius:12px;
  background:#fff; outline:none;
  transition:border-color .12s ease, box-shadow .12s ease;
}
.input:focus{
  border-color:#2e7d32;
  box-shadow:0 0 0 3px color-mix(in srgb, #2e7d32 22%, transparent);
}
.input:disabled{opacity:.6}

/* 按钮（更清晰的对比） */
.btn{padding:10px 14px;border-radius:12px;cursor:pointer}
.btn.primary.send{
  background: linear-gradient(135deg, #2e7d32, #1f5f24);
  color:#fff; border:1px solid #215b2b;
  box-shadow:0 4px 10px rgba(33,91,43,.18);
}
.btn.primary.send:hover{ transform:translateY(-1px); box-shadow:0 6px 14px rgba(33,91,43,.25) }
.btn.outline.skip{
  background:#fff; color:#2e7d32; border:2px solid #2e7d32;
  box-shadow:0 2px 8px rgba(0,0,0,.05);
}
.btn.outline.skip:hover{ background:#e9f7ea }
.actions{margin-top:8px}
</style>
