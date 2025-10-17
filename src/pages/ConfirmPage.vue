<!-- src/pages/ConfirmPage.vue -->
<template>
  <section class="wrap">
    <h2>Confirm your input</h2>

    <div class="card">
      <h3>Symptoms (images + NLP)</h3>
      <div v-if="allSymptoms.length" class="tags">
        <span class="tag" v-for="k in allSymptoms" :key="k">{{ labelOf(k) }}</span>
      </div>
      <div class="muted" v-else>(No symptoms selected yet)</div>
    </div>

    <div class="card">
      <h3>Text / Transcript</h3>
      <p><strong>Text:</strong> <span class="muted" v-if="!textInput">(none)</span>{{ textInput }}</p>
      <p><strong>Voice transcript:</strong> <span class="muted" v-if="!transcript">(none)</span>{{ transcript }}</p>
    </div>

    <div class="actions">
      <button class="btn outline" @click="$router.back()">Back</button>
      <button class="btn primary" :disabled="submitting" @click="submit">
        {{ submitting ? 'Submitting…' : 'Submit' }}
      </button>
    </div>

    <div class="card" v-if="error">
      <h3>Error</h3>
      <p class="muted">{{ error }}</p>
    </div>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useTriageStore } from '@/store/triageStore'
import { submitSymptoms } from '@/services/api'

const router = useRouter()
const store  = useTriageStore()

// 已选图片 + NLP 提取：做一次去重合并，避免空数组导致整页空白
const images      = computed(()=> store.selectedSymptoms || [])
const nlpExtracts = computed(()=> store.extractedSymptoms || [] ) // 如果 store 没有这个字段也不报错
const allSymptoms = computed(()=> Array.from(new Set([...(images.value||[]), ...(nlpExtracts.value||[])])))

const textInput  = computed(()=> store.textInput || '')
const transcript = computed(()=> store.audioText || store.transcript || '')

const submitting = ref(false)
const error      = ref('')

// 标签名展示（英文）
const keyToLabel = {
  abdominal_pain:'Abdominal pain', fever_high:'Fever', cough:'Cough', sore_throat:'Sore throat',
  headache:'Headache', nausea:'Nausea', vomit:'Vomit', diarrhea:'Diarrhea',
  chest_pain:'Chest pain', short_breath:'Shortness of breath', rash:'Rash', fatigue:'Fatigue',
}
function labelOf(k){ return keyToLabel[k] || k }

// 提交到后端并跳结果页
async function submit(){
  if (submitting.value) return
  submitting.value = true
  error.value = ''
  try {
    const payload = {
      symptoms: allSymptoms.value,     // 后端 /predict 接受数组（你的日志里已验证）
      text: textInput.value,
      transcript: transcript.value,
      // 需要的话还可以带 language 等
    }
    const resp = await submitSymptoms(payload)
    // 结果存起来给 /predict 页用。兼容不同 store 实现：
    if (typeof store.setLastReport === 'function') store.setLastReport(resp)
    else store.lastReport = resp

    router.push('/predict')
  } catch (e) {
    console.error(e)
    error.value = e?.message || 'Submit failed'
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.wrap{max-width:980px;margin:0 auto}
.card{border:1px solid var(--border);border-radius:12px;padding:14px;background:var(--card);margin-bottom:16px}
.actions{display:flex;gap:8px;align-items:center}
.btn.primary{background:var(--btn-bg);color:var(--btn-fg);border:none;padding:10px 14px;border-radius:10px}
.btn.outline{background:var(--btn-outline-bg);color:var(--btn-outline-fg);border:1px solid var(--btn-outline-border);padding:10px 14px;border-radius:10px}
.tags{display:flex;gap:8px;flex-wrap:wrap}
.tag{border:1px solid var(--btn-outline-border);padding:4px 8px;border-radius:999px}
.muted{color:var(--muted)}
</style>
