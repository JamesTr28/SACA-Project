<template>
  <section class="wrap">
    <h2>{{ t('confirm.title') }}</h2>

    <div class="card">
      <h3>{{ t('confirm.basic') }}</h3>
      <ul class="list">
        <li>{{ t('info.gender') }}: {{ profile.gender === 1 ? t('info.male') : t('info.female') }}</li>
        <li>{{ t('info.age') }}: {{ profile.age || '-' }}</li>
        <li>{{ t('info.conditions') }}: {{ profile.conditions || '-' }}</li>
        <li>{{ t('info.allergies') }}: {{ profile.allergies || '-' }}</li>
        <li>{{ t('info.meds') }}: {{ profile.medications || '-' }}</li>
      </ul>
    </div>

    <div class="card">
      <h3>{{ t('confirm.symptoms') }}</h3>
      <div v-if="symptoms.length" class="tags">
        <span class="tag" v-for="k in symptoms" :key="k">{{ labelOf(k) }}</span>
      </div>
      <div v-else class="muted">{{ t('confirm.noneSymptoms') }}</div>
    </div>

    <div class="card">
      <h3>{{ t('confirm.textVoice') }}</h3>
      <p><strong>{{ t('confirm.text') }}:</strong> {{ text || t('confirm.voiceNo') }}</p>
      <p><strong>{{ t('confirm.voice') }}:</strong> {{ audioBlob ? t('confirm.voiceYes') : t('confirm.voiceNo') }}</p>
    </div>

    <div class="card">
      <h3>{{ t('confirm.self') }}</h3>
      <p>{{ t('triage.self_severity') }}: {{ sa.severity ?? t('confirm.voiceNo') }}</p>
      <p>{{ t('triage.self_feeling') }}: {{ sa.feeling ?? t('confirm.voiceNo') }}</p>
    </div>

    <div class="actions">
      <button class="btn outline" @click="$router.back()">{{ t('common.back') }}</button>
      <button class="btn primary" :disabled="submitting" @click="submit">
        {{ submitting ? t('common.loading') : t('common.submit') }}
      </button>
    </div>

    <div class="card" v-if="report || error">
      <h3>{{ t('confirm.result') }}</h3>
      <ResultsPanel :report="report" :loading="submitting" :error="error" />
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useTriageStore } from '@/store/triageStore'
import { useI18n } from '@/i18n/useI18n'
import ResultsPanel from '@/components/ResultsPanel.vue'

const { t } = useI18n()

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
  abdominal_pain: t('symptom.abdominal_pain'),
  fever_high: t('symptom.fever_high'),
  cough: t('symptom.cough'),
  sore_throat: t('symptom.sore_throat'),
  headache: t('symptom.headache'),
  nausea: t('symptom.nausea'),
  vomit: t('symptom.vomit'),
  diarrhea: t('symptom.diarrhea'),
  chest_pain: t('symptom.chest_pain'),
  short_breath: t('symptom.short_breath'),
  rash: t('symptom.rash'),
  fatigue: t('symptom.fatigue'),
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