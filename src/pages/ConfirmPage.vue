<template>
  <section class="wrap">
    <h2>Confirm Your Input</h2>

    <div class="card">
      <h3>Basic Information</h3>
      <ul class="list">
        <li>Gender: {{ profile.gender === 1 ? 'Male' : 'Female' }}</li>
        <li>Age: {{ profile.age || '-' }}</li>
        <li>Current Conditions: {{ profile.conditions || '-' }}</li>
        <li>Allergy History: {{ profile.allergies || '-' }}</li>
        <li>Current Medications: {{ profile.medications || '-' }}</li>
      </ul>
    </div>

    <div class="card">
      <h3>Symptoms</h3>
      <div v-if="symptoms.length" class="tags">
        <span class="tag" v-for="k in symptoms" :key="k">{{ labelOf(k) }}</span>
      </div>
      <div v-else class="muted">(No image symptoms selected)</div>
    </div>

    <div class="card">
      <h3>Text/Voice</h3>
      <p><strong>Text:</strong> {{ text || '(None)' }}</p>
      <p><strong>Voice:</strong> {{ audioBlob ? 'Recorded' : '(None)' }}</p>
    </div>

    <div class="card">
      <h3>Self-Assessment</h3>
      <p>Severity: {{ sa.severity ?? '(Not filled)' }}</p>
      <p>Personal Feeling: {{ sa.feeling ?? '(Not filled)' }}</p>
    </div>

    <div class="actions">
      <button class="btn outline" @click="$router.back()">Back</button>
      <button class="btn primary" :disabled="submitting" @click="submit">
        {{ submitting ? 'Submitting...' : 'Submit' }}
      </button>
    </div>

    <div class="card" v-if="report || error">
      <h3>Results</h3>
      <ResultsPanel :report="report" :loading="submitting" :error="error" />
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useTriageStore } from '@/store/triageStore'
import ResultsPanel from '@/components/ResultsPanel.vue'

const store = useTriageStore()
const { submitting, error, lastReport } = storeToRefs(store)

const profile = computed(()=> store.profile)
const symptoms = computed(()=> store.selectedSymptoms)
const text = computed(()=> store.textInput)
const audioBlob = computed(()=> store.audioBlob)
const sa = computed(()=> store.selfAssessment)
const report = computed(()=> lastReport.value)

async function submit(){ await store.submitTriageFinal() }

const keyToLabel = {
  abdominal_pain:'Abdominal Pain', fever_high:'High Fever', cough:'Cough', sore_throat:'Sore Throat',
  headache:'Headache', nausea:'Nausea', vomit:'Vomiting', diarrhea:'Diarrhea',
  chest_pain:'Chest Pain', short_breath:'Shortness of Breath', rash:'Rash', fatigue:'Fatigue',
}
function labelOf(k){ return keyToLabel[k] || k }
</script>

<style scoped>
.wrap{max-width:980px;margin:0 auto}
.card{border:1px solid var(--border);border-radius:12px;padding:14px;background:var(--card);margin-bottom:16px}
.list{line-height:1.8}
.actions{display:flex;gap:8px}
.btn.primary{background:var(--btn-bg);color:var(--btn-fg);border:none;padding:10px 14px;border-radius:10px}
.btn.outline{background:var(--btn-outline-bg);color:var(--btn-outline-fg);border:1px solid var(--btn-outline-border);padding:10px 14px;border-radius:10px}
.tags{display:flex;gap:8px;flex-wrap:wrap}
.tag{border:1px solid var(--btn-outline-border);padding:4px 8px;border-radius:999px}
.muted{color:var(--muted)}
</style>