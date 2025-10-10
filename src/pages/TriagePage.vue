<template>
  <section class="wrap">
    <h2>Symptom Input Guide</h2>

    <!-- Modify info button: Navigate to Info page -->
    <div class="back-info">
      <button class="btn outline" @click="goInfo">
        Modify Personal Information
      </button>
    </div>

    <!-- Step indicator => pager -->
    <div class="pager">
      <button :class="{ on: step === 1 }" @click="step = 1">1 Images</button>
      <button :class="{ on: step === 2 }" @click="step = 2">
        2 Text/Voice
      </button>
      <button :class="{ on: step === 3 }" @click="step = 3">
        3 Self-Assessment
      </button>
    </div>

    <!-- STEP 1: Image selection + Real-time Tags -->
    <div v-if="step === 1" class="card">
      <h3>Select Images (Multiple Selection Allowed)</h3>
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
      <small class="muted" v-else
        >Click on images to select symptoms; click × on tags to cancel
        selection.</small
      >

      <div class="actions">
        <button class="btn outline" @click="skip()">Skip</button>
        <button class="btn primary" @click="next()">Next</button>
      </div>
    </div>

    <!-- STEP 2: Text + Voice -->
    <div v-else-if="step === 2" class="card">
      <h3>Text</h3>
      <!-- Translate button -->
      <textarea
        v-model="text"
        rows="6"
        placeholder="You can enter additional descriptions (optional)"
      ></textarea>

      <button
        class="btn outline"
        :disabled="submitting || transLoading || !text.trim()"
        @click="translateAndFill"
        title="Translate Warlpiri → English and replace the textarea"
      >
        {{ transLoading ? "Translating..." : "TRANSLATE" }}
      </button>
      <h3>Voice</h3>
      <textarea
        v-model="text"
        rows="6"
        placeholder="You can enter additional descriptions (optional)"
      ></textarea>
      <div class="actions">
        <AudioCapture @recorded="onRecorded" />
      </div>

      <div class="actions spaced">
        <button class="btn outline" @click="skip()">Skip</button>
        <button class="btn primary" @click="next()">Next</button>
      </div>
    </div>

    <!-- STEP 3: Self-Assessment (1-10) -->
    <div v-else-if="step === 3" class="card">
      <h3>Self-Assessment</h3>

      <!-- Severity -->
      <div class="row">
        <label
          >Self-assessed Severity:
          <strong>{{ sa.severity ?? "-" }}</strong></label
        >
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
      <img
        class="scale-img"
        src="@/assets/severity.png"
        alt="Severity scale"
        loading="lazy"
        decoding="async"
      />

      <!-- Feeling -->
      <div class="row" style="margin-top: 14px">
        <label
          >Personal Feeling: <strong>{{ sa.feeling ?? "-" }}</strong></label
        >
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
      <img
        class="scale-img"
        src="@/assets/feeling.png"
        alt="Feeling scale"
        loading="lazy"
        decoding="async"
      />

      <div class="actions">
        <button class="btn primary" @click="goConfirm()">Next</button>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed } from "vue";
import { useRouter } from "vue-router";
import severityImg from "@/assets/severity.png"; // 红色心形刻度图
import feelingImg from "@/assets/feeling.png"; // 表情刻度图
import { storeToRefs } from "pinia";
import { useTriageStore } from "@/store/triageStore";
import SymptomImagePicker from "@/components/SymptomImagePicker.vue";
import AudioCapture from "@/components/AudioCapture.vue";
import { translate } from "@/services/api";
const store = useTriageStore();
const router = useRouter();
const step = ref(1);

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
  get: () => store.selfAssessment,
  set: (v) => (store.selfAssessment = v),
});
const severityTexts = [
  "1 Very Mild: Almost no impact on daily life",
  "2 Mild: Slight discomfort",
  "3 Mild: Occasionally affects activities",
  "4 Mild-Moderate: Needs attention",
  "5 Moderate: Affects daily work/study",
  "6 Moderate-Severe: Noticeable discomfort",
  "7 Relatively Severe: Needs prompt handling",
  "8 Severe: Recommend seeking medical attention soon",
  "9 Very Severe: High concern",
  "10 Critical: Seek immediate medical/emergency care",
];
const feelingTexts = [
  "1 Very Reassured",
  "2 Fairly Reassured",
  "3 Okay",
  "4 A Bit Worried",
  "5 Moderately Worried",
  "6 Noticeably Worried",
  "7 Very Worried",
  "8 Extremely Worried",
  "9 Highly Anxious",
  "10 Panicked/Urgent Help Needed",
];
function severityDesc(v) {
  return v ? severityTexts[v - 1] : "Drag the slider to select (1-10)";
}
function feelingDesc(v) {
  return v ? feelingTexts[v - 1] : "Drag the slider to select (1-10)";
}

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
  abdominal_pain: "Abdominal Pain",
  fever_high: "High Fever",
  cough: "Cough",
  sore_throat: "Sore Throat ",
  headache: "Headache",
  nausea: "Nausea",
  vomit: "Vomiting ",
  diarrhea: "Diarrhea",
  chest_pain: "Chest Pain",
  short_breath: "Shortness of Breath",
  rash: "Rash",
  fatigue: "Fatigue",
};
function labelOf(k) {
  return keyToLabel[k] || k;
}
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
