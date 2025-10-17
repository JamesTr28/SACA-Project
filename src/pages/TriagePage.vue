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

          <!-- 性别二选一 -->
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
      <!-- ① 文本输入 + Send -->
      <div class="row input-row">
        <input
          v-model="draft"
          type="text"
          class="input"
          :placeholder="placeholder"
          :disabled="inputDisabled || busy"
          @keyup.enter="send"
        />
        <button class="btn primary send" :disabled="inputDisabled || busy" @click="send">Send</button>
      </div>

      <!-- ② 录音盒子 -->
      <div
        v-if="stage==='symptoms' && !inputDisabled"
        class="voice-box"
        aria-label="Voice input panel"
      >
        <AudioCapture
          :disabled="busy"
          @transcript="onTranscript"
          @recorded="onAudioRecorded"
        />
      </div>

      <!-- ③ Skip/Next -->
      <div class="row actions-row">
        <button class="btn outline skip" :disabled="busy" @click="skip">{{ skipText }}</button>
      </div>
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
import { useI18n } from '@/i18n'

const router = useRouter()
const store  = useTriageStore()
const busy   = ref(false)

const { t, lang, setLang } = useI18n()

/* ---------- 会话与阶段 ---------- */
const chat   = ref([])            // { role:'bot'|'user', text, _orig?, options?, type? }
const draft  = ref('')
const stage  = ref('greet')       // 'greet'|'collect_*'|'symptoms'|'ask_more'|'image_flow'
const optionMode = ref(false)
const imagesTmp = ref([])

function toLines(tk){ return String(tk).split('\n') }

/** pushBot：WEP 模式展示翻译；记录 _orig 供切换回 EN */
async function pushBot(text, options=null, type=null){
  optionMode.value = !!(options && options.length) || !!type
  let shown = text

  // 仅当 wep 且不是控件气泡时，尝试翻译 UI 固定文案
  if (lang.value === 'wep' && text && !type) {
    try {
      const r = await translate(text) // 后端：translate(text) → { translation }
      shown = r?.translation || r?.text || text
    } catch { /* ignore */ }
  }

  chat.value.push({ role:'bot', text: shown, _orig: text, options, type })
  await nextTick()
  const el = document.querySelector('.chat')
  if (el) el.scrollTop = el.scrollHeight
}
function pushUser(text){ chat.value.push({ role:'user', text }) }

/* 初始问候（防止热更新重复） */
onMounted(async () => {
  if (chat.value.length === 0) {
    await pushBot(t('chat.greet'), [
      { key:'text',  label: t('mode.text') },
      { key:'image', label: t('mode.image') }
    ])
  }
})

/* ---------- store 兜底工具 ---------- */
function safeSetProfileField(key, value){
  if (typeof store.setProfileField === 'function') store.setProfileField(key, value)
  else { store.profile = { ...(store.profile||{}), [key]: value } }
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
      pushBot(t('chat.askGender'), null, 'gender')
    } else {
      stage.value = 'image_flow'
      pushBot(t('chat.imagesPrompt'), null, 'images')
    }
    return
  }

  if (stage.value==='ask_more') {
    if (opt.key === 'no') router.push('/confirm')
    else { stage.value='symptoms'; pushBot(t('chat.askSymptoms')) }
  }
}

/* ---------- 性别专用选项 ---------- */
function selectGender(code){
  optionMode.value = false
  pushUser(code === 1 ? t('info.male') : t('info.female'))
  safeSetProfileField('gender', code)
  stage.value = 'collect_age'
  pushBot(t('chat.askAge'))
}

/* ---------- 图片路径确认 ---------- */
function confirmImages(){
  safeSetSelectedSymptoms(imagesTmp.value)
  router.push('/confirm')
}

/* ---------- 输入框联动 ---------- */
const inputDisabled = computed(()=> optionMode.value)
const placeholder = computed(()=>{
  if (inputDisabled.value) return t('chat.chooseFromOptions')
  switch(stage.value){
    case 'collect_age':     return t('chat.askAge')
    case 'collect_weight':  return t('chat.askWeight')
    case 'collect_cond':    return t('chat.askCond')
    case 'collect_allergy': return t('chat.askAllergy')
    case 'collect_meds':    return t('chat.askMeds')
    case 'symptoms':        return t('chat.enPh')
    default:                return t('chat.typeHere')
  }
})
const skipText = computed(()=> stage.value==='symptoms' ? t('common.skip') : t('common.next'))

/* ---------- NLP & 翻译封装 ---------- */
async function translateToEnglishIfNeeded(text){
  if (!text) return ''
  if (lang.value !== 'wep') return text
  try{
    const res = await translate(text)   // 后端 translate(text) 默认 Warlpiri→English
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
    stage.value='collect_weight'; return pushBot(t('chat.askWeight'))
  }
  if (stage.value==='collect_weight') {
    safeSetProfileField('weight', text)
    stage.value='collect_cond'; return pushBot(t('chat.askCond'))
  }
  if (stage.value==='collect_cond') {
    safeSetProfileField('conditions', text)
    stage.value='collect_allergy'; return pushBot(t('chat.askAllergy'))
  }
  if (stage.value==='collect_allergy') {
    safeSetProfileField('allergies', text)
    stage.value='collect_meds'; return pushBot(t('chat.askMeds'))
  }
  if (stage.value==='collect_meds') {
    safeSetProfileField('medications', text)
    stage.value='symptoms'; return pushBot(t('chat.askSymptoms'))
  }

  if (stage.value==='symptoms') {
    busy.value = true
    try{
      const forNlp = await translateToEnglishIfNeeded(text) // wep→en
      const found  = await safeNlp(forNlp)
      if (lang.value==='wep' && forNlp !== text) pushBot(`${t('chat.translatedPrefix')} ${forNlp}`)
      if (found.length){
        safeAddSymptoms(found)
        pushBot(`${t('chat.capturedPrefix')}${found.map(labelOf).join(', ')}.`)
      }else{
        pushBot(t('chat.noDetect'))
      }
      stage.value='ask_more'
      pushBot(t('chat.askMore'), [
        { key:'yes', label:t('chat.yes') }, { key:'no', label:t('chat.no') }
      ])
    } finally { busy.value = false }
  }
}

/* ---------- Skip / Next ---------- */
function skip(){
  if (stage.value==='symptoms') {
    router.push('/confirm')
  } else {
    if (stage.value==='collect_age'){ stage.value='collect_weight'; pushBot(t('chat.askWeight')); return }
    if (stage.value==='collect_weight'){ stage.value='collect_cond'; pushBot(t('chat.askCond')); return }
    if (stage.value==='collect_cond'){ stage.value='collect_allergy'; pushBot(t('chat.askAllergy')); return }
    if (stage.value==='collect_allergy'){ stage.value='collect_meds'; pushBot(t('chat.askMeds')); return }
    if (stage.value==='collect_meds'){ stage.value='symptoms'; pushBot(t('chat.askSymptoms')); return }
  }
}

/* ---------- 语音事件 ---------- */
async function onAudioRecorded(blob){
  // 如果仍需在父组件内直接调用 asr，可保留；你也可以只监听子组件 @transcript
  try{
    const out = await asrTranscribeFile(blob)
    const raw = out?.text || ''
    if (!raw) return
    pushUser(`[Voice] ${raw}`)
    const forNlp = await translateToEnglishIfNeeded(raw)
    if (lang.value==='wep' && forNlp !== raw) pushBot(`${t('chat.translatedPrefix')} ${forNlp}`)
    const found = await safeNlp(forNlp)
    if (found.length){
      safeAddSymptoms(found)
      pushBot(`${t('chat.capturedPrefix')}${found.map(labelOf).join(', ')}.`)
    }
    stage.value='ask_more'
    pushBot(t('chat.askMore'), [
      { key:'yes', label:t('chat.yes') }, { key:'no', label:t('chat.no') }
    ])
  }catch{}
}
function onTranscript(text){
  const s = (text||'').trim()
  if (!s) return
  draft.value = draft.value ? `${draft.value} ${s}` : s
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
  background: linear-gradient(180deg, rgba(255,255,255,.92), rgba(245,255,245,.86));
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

/* ===== 输入区（重构为三行：输入/录音盒子/Skip） ===== */
.composer{
  display:flex;
  flex-direction:column;
  gap:10px;
  margin-top:12px;
}
.row{width:100%}

/* ① 文本输入 + Send（横排） */
.input-row{
  display:flex;
  gap:10px;
  align-items:center;
}
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

/* Send 更醒目 */
.btn{padding:10px 14px;border-radius:12px;cursor:pointer}
.btn.primary.send{
  background: linear-gradient(135deg, #2e7d32, #1f5f24);
  color:#fff; border:1px solid #215b2b;
  box-shadow:0 4px 10px rgba(33,91,43,.18);
}
.btn.primary.send:hover{ transform:translateY(-1px); box-shadow:0 6px 14px rgba(33,91,43,.25) }

/* ② 录音盒子：三个按钮横排，Upload 靠右，右侧提示文字 */
.voice-box {
  width: 100%;
  border: 2px solid #cfe6cf;
  border-radius: 12px;
  background: #ffffff2e;
  padding: 10px 14px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) inset;

  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

/* 深度定制 AudioCapture 内部结构 */
.voice-box :deep(.ac-root) {
  display: flex;
  align-items: center;
  width: 100%;
  gap: 10px;
}
.voice-box :deep(.ac-controls) {
  display: flex;
  flex: 1;
  gap: 10px;
  align-items: center;
}
/* Start + Stop 靠左，Upload 靠右 */
.voice-box :deep(.ac-controls .btn:nth-child(1)),
.voice-box :deep(.ac-controls .btn:nth-child(2)) {
  flex: 0 0 auto;
}
.voice-box :deep(.ac-controls .btn:nth-child(3)) {
  margin-left: auto;
}
/* 提示文字在 Upload 右侧 */
.voice-box :deep(.ac-hint) {
  margin-left: 12px;
  text-align: right;
  font-size: 0.9em;
  color: #555;
  white-space: nowrap;
}
/* 小屏幕下竖排 */
@media (max-width: 680px){
  .voice-box :deep(.ac-root){ flex-direction: column; align-items: stretch; }
  .voice-box :deep(.ac-controls){ flex-direction: column; align-items: stretch; }
  .voice-box :deep(.ac-controls .btn:nth-child(3)){ margin-left: 0; }
  .voice-box :deep(.ac-hint){ text-align: center; margin-left: 0; white-space: normal; }
}

/* ③ Skip/Next 独占一行，靠右 */
.actions-row{
  display:flex;
  justify-content:flex-end;
}
.btn.outline.skip{
  background:#ffffff96; color:#2e7d32; border:2px solid #2e7d32;
  box-shadow:0 2px 8px rgba(0,0,0,.05);
}
.btn.outline.skip:hover{ background:#e9f7ea }

.actions{margin-top:8px}
</style>
