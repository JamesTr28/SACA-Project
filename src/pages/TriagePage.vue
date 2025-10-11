<template>
  <section class="wrap">
    <h2>{{ t('triage.title') }}</h2>

    <!-- Modify info button: Navigate to Info page -->
    <div class="back-info">
      <button class="btn outline" @click="goInfo">{{ t('triage.modifyInfo') }}</button>
    </div>

    <!-- Step indicator => pager -->
    <div class="pager">
      <button :class="{on: step===1}" @click="step=1">{{ t('triage.pager1') }}</button>
      <button :class="{on: step===2}" @click="step=2">{{ t('triage.pager2') }}</button>
      <button :class="{on: step===3}" @click="step=3">{{ t('triage.pager3') }}</button>
    </div>

    <!-- STEP 1: Image selection + Real-time Tags -->
    <div v-if="step===1" class="card">
      <h3>{{ t('triage.images_title') }}</h3>
      <SymptomImagePicker v-model="selected" />
      <div class="tags" v-if="selected.length">
        <button
          v-for="k in selected"
          :key="k"
          class="tag"
          @click="removeTag(k)"
        >
          {{ labelOf(k) }} <span class="x">×</span>
        </button>
      </div>
      <small class="muted" v-else>{{ t('triage.images_hint') }}</small>

      <div class="actions">
        <button class="btn outline" @click="skip()">{{ t('common.skip') }}</button>
        <button class="btn primary" @click="next()">{{ t('triage.next') }}</button>
      </div>
    </div>

    <!-- STEP 2: Text + Voice -->
    <div v-else-if="step===2" class="card">
      <h3>{{ t('triage.text_title') }}</h3>
      <textarea v-model="text" rows="6" :placeholder="t('triage.text_ph')"></textarea>
      <div class="actions">
        <AudioCapture @recorded="onRecorded" />
      </div>

      <div class="actions spaced">
        <button class="btn outline" @click="skip()">{{ t('common.skip') }}</button>
        <button class="btn primary" @click="next()">{{ t('triage.next') }}</button>
      </div>
    </div>

    <!-- STEP 3: Self-Assessment (1-10) -->
    <div v-else-if="step===3" class="card">
      <h3>{{ t('triage.self_title') }}</h3>

      <!-- Severity -->
      <div class="row">
        <label>{{ t('triage.self_severity') }}: <strong>{{ sa.severity ?? '-' }}</strong></label>
        <input
          type="range"
          min="1"
          max="10"
          step="1"
          v-model.number="sa.severity"
          v-rangefill
        />
      </div>
      <p class="desc">{{ severityDesc(sa.severity) }}</p>
      <!-- 🔽 Severity scale image -->
      <img class="scale-img" src="@/assets/severity.png" :alt="t('alt.severity_scale')" loading="lazy" decoding="async" />

      <!-- Feeling -->
      <div class="row" style="margin-top:14px;">
        <label>{{ t('triage.self_feeling') }}: <strong>{{ sa.feeling ?? '-' }}</strong></label>
        <input
          type="range"
          min="1"
          max="10"
          step="1"
          v-model.number="sa.feeling"
          v-rangefill
        />
      </div>
      <p class="desc">{{ feelingDesc(sa.feeling) }}</p>
      <!-- 🔽 Feeling scale image -->
      <img class="scale-img" src="@/assets/feeling.png" :alt="t('alt.feeling_scale')" loading="lazy" decoding="async" />

      <div class="actions">
        <button class="btn primary" @click="goConfirm()">{{ t('triage.toConfirm') }}</button>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useTriageStore } from '@/store/triageStore'
import { useI18n } from '@/i18n/useI18n'
import SymptomImagePicker from '@/components/SymptomImagePicker.vue'
import AudioCapture from '@/components/AudioCapture.vue'

const { t } = useI18n()

const store = useTriageStore()
const router = useRouter()
const step = ref(1)

// Image selection (synced with Tags in real-time)
const selected = computed({
  get: () => store.selectedSymptoms,
  set: (v) => store.setSelectedSymptoms(v),
});
function removeTag(k) {
  store.removeSymptom(k);
}

// Text & Voice
const text = computed({
  get: () => store.textInput,
  set: (v) => store.setText(v),
});
function onRecorded(blob) {
  store.setAudio(blob);
}

// Self-Assessment
const sa = computed({
  get:()=> store.selfAssessment,
  set:(v)=> (store.selfAssessment = v),
})
function severityDesc(v){ return v ? t(`scales.severity.${v-1}`) : t('triage.self_help') }
function feelingDesc(v){ return v ? t(`scales.feeling.${v-1}`) : t('triage.self_help') }

// Navigation
function next() {
  step.value = Math.min(3, step.value + 1);
}
function skip() {
  step.value = Math.min(3, step.value + 1);
}
function goConfirm() {
  router.push("/confirm");
}
function goInfo() {
  router.push("/info");
} // Added: Navigate to Info page
// Translation
const transLoading = ref(false)
const transError = ref(null)
async function translateAndFill() {
  console.log(text.value);
  transError.value = null;
  if (!text.value.trim()) return;
  transLoading.value = true;
  try {
    const r = await translate(text.value, 6, 160, 1.0); // beams, max_len, len_pen
    // Replace the textarea content with the translation
    store.setText(r.translation);
  } catch (e) {
    transError.value = e?.message || String(e);
  } finally {
    transLoading.value = false;
  }
}
// Display tag labels
const keyToLabel = {
  abdominal_pain: t('symptom.abdominal_pain'), fever_high: t('symptom.fever_high'), cough: t('symptom.cough'), sore_throat: t('symptom.sore_throat'),
  headache: t('symptom.headache'), nausea: t('symptom.nausea'), vomit: t('symptom.vomit'), diarrhea: t('symptom.diarrhea'),
  chest_pain: t('symptom.chest_pain'), short_breath: t('symptom.short_breath'), rash: t('symptom.rash'), fatigue: t('symptom.fatigue'),
}
function labelOf(k){ return keyToLabel[k] || k }
</script>

<style>
.wrap {
  max-width: 980px;
  margin: 0 auto;
}

/* Top: Back to info button */
.back-info {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 12px;
}
.back-info .btn {
  font-size: 14px;
  padding: 6px 14px;
}

/* Pager (aligned with .pager in template) */
.pager {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 10px;
}
.pager button {
  border-radius: 999px;
  padding: 6px 12px;
  cursor: pointer;
  border: 1px solid #2e7d32;
  background: transparent;
  color: #2e7d32;
}
.pager button.on {
  background: #2e7d32;
  color: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.card {
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 14px;
  background: var(--card);
  margin-bottom: 16px;
}
.actions {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-top: 8px;
  flex-wrap: wrap;
}
.actions.spaced {
  justify-content: space-between;
}
.btn.primary {
  background: var(--btn-bg);
  color: var(--btn-fg);
  border: none;
  padding: 10px 14px;
  border-radius: 10px;
}
.btn.outline {
  background: var(--btn-outline-bg);
  color: var(--btn-outline-fg);
  border: 1px solid var(--btn-outline-border);
  padding: 10px 14px;
  border-radius: 10px;
}
.muted {
  color: var(--muted);
}
.tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 10px;
}
.tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border: 1px solid var(--btn-outline-border);
  background: transparent;
  color: inherit;
  border-radius: 999px;
  padding: 6px 10px;
  cursor: pointer;
}
.tag .x {
  font-weight: 700;
}
.row {
  display: flex;
  gap: 12px;
  align-items: center;
  margin: 8px 0;
}
.row input[type="range"] {
  flex: 1;
}
.desc {
  color: var(--muted);
  margin-top: 4px;
}
textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid var(--border);
  border-radius: 10px;
  background: transparent;
  color: inherit;
}
</style>
