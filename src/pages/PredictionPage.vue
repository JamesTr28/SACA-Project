<template>
  <section class="wrap">
    <h2>{{ tt('Disease Prediction (Demo)') }}</h2>

    <div class="card">
      <h3>{{ tt('Your input') }}</h3>
      <p><strong>{{ tt('Symptoms') }}:</strong> {{ prettySymptoms || tt('(none)') }}</p>
      <p v-if="text"><strong>{{ tt('Text') }}:</strong> {{ text }}</p>
      <p v-if="audioText"><strong>{{ tt('Transcript') }}:</strong> {{ audioText }}</p>
    </div>

    <div class="card">
      <h3>{{ tt('Prediction') }}</h3>
      <p>{{ tt('The results are for reference only. If you feel any discomfort, please consult a doctor') }}</p>
      <ul class="list">
        <li>{{ tt('Possible condition') }}: {{ tt('Common cold') }}</li>
        <li>{{ tt('Urgency') }}: {{ tt('Low') }}</li>
        <li>{{ tt('Advice') }}: {{ tt('Rest, hydrate, and monitor symptoms.') }}</li>
      </ul>
    </div>

    <div class="actions">
      <button class="btn outline" @click="$router.push('/triage')">{{ tt('Back to Triage') }}</button>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { useTriageStore } from '@/store/triageStore'
import { translate } from '@/services/api'

const store = useTriageStore()
// 简单从 localStorage 或 store 推断语言（也可以从 uiStore 读）
const lang = localStorage.getItem('locale') || 'en'
const tt = (s) => (lang === 'wbp' ? translate(s) : s)

const images = computed(()=> store.selectedSymptoms || [])
const text = computed(()=> store.textInput || '')
const audioText = computed(()=> store.audioText || store.audioBlobText || '')

const keyToLabel = {
  abdominal_pain:'Abdominal pain', fever_high:'Fever', cough:'Cough', sore_throat:'Sore throat',
  headache:'Headache', nausea:'Nausea', vomit:'Vomit', diarrhea:'Diarrhea',
  chest_pain:'Chest pain', short_breath:'Shortness of breath', rash:'Rash', fatigue:'Fatigue',
}
const prettySymptoms = computed(()=>{
  return images.value.length ? images.value.map(k => keyToLabel[k]||k).join(', ') : ''
})
</script>

<style scoped>
.wrap{max-width:980px;margin:0 auto}
.card{border:1px solid var(--border);border-radius:12px;padding:14px;background:var(--card);margin-bottom:16px}
.list{line-height:1.8}
.actions{display:flex;gap:8px;margin-top:8px}
</style>
