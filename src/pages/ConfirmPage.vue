<template>
  <section class="wrap">
    <h2>{{ t("confirm.title") }}</h2>
    <p>{{ profile }}</p>
    <!-- Basic information -->
    <div class="card">
      <h3>{{ t("confirm.basic") }}</h3>
      <ul class="list">
        <li>
          {{ t("info.gender") }}:
          {{ profile.gender === 1 ? t("info.male") : t("info.female") }}
        </li>
        <li>{{ t("info.age") }}: {{ profile.age || "-" }}</li>
        <li>{{ t("info.conditions") }}: {{ profile.conditions || "-" }}</li>
        <li>{{ t("info.allergies") }}: {{ profile.allergies || "-" }}</li>
        <li>{{ t("info.meds") }}: {{ profile.medications || "-" }}</li>
      </ul>
    </div>


    <!-- Symptoms -->
    <div class="card">
      <h3>{{ t("confirm.symptoms") }}</h3>
      <div v-if="profile.symptoms.length" >
        <span>{{ profile.symptoms }}</span>
      </div>
      <div v-else class="muted">{{ t("confirm.noneSymptoms") }}</div>
    </div>

    <!-- Text / Voice + model results -->
    <div class="card">
      <h3>{{ t("confirm.textVoice") }}</h3>
      <p>
        <strong>{{ t("confirm.text") }}:</strong>
        {{ profile.nlp_text || text || t("confirm.voiceNo") }}
      </p>
      <p>
        <strong>{{ t("confirm.voice") }}:</strong>
        {{
          profile.voice_text ||
          (audioBlob ? t("confirm.voiceYes") : t("confirm.voiceNo"))
        }}
      </p>
      <p v-if="profile.nlp_assessment">
        <strong>NLP:</strong>
        {{ profile.nlp_assessment }}
        <span v-if="profile.nlp_confidence != null">
          ({{ profile.nlp_confidence }}%)</span
        >
      </p>
      <p v-if="profile.skin_analysis">
        <strong>Skin:</strong>
        {{ profile.skin_analysis }}
        <span v-if="profile.skin_confidence != null">
          ({{ profile.skin_confidence }}%)</span
        >
      </p>
    </div>

    <!-- Self assessment -->
    <div class="card">
      <h3>{{ t("confirm.self") }}</h3>
      <p>
        {{ t("triage.self_severity") }}:
        {{ sa.severity ?? t("confirm.voiceNo") }}
      </p>
      <p>
        {{ t("triage.self_feeling") }}: {{ sa.feeling ?? t("confirm.voiceNo") }}
      </p>
    </div>

    <!-- Actions -->
    <div class="actions">
      <button class="btn outline" @click="$router.back()">
        {{ t("common.back") }}
      </button>
      <button class="btn primary" :disabled="submitting" @click="submitSummary">
        {{ submitting ? t("common.loading") : t("common.submit") }}
      </button>
    </div>

    <!-- Result -->
    <div class="card">
      <h3>{{ t("confirm.result") }}</h3>
      <p v-if="error" class="muted" style="color: #d93025">{{ error }}</p>
      <pre v-else class="result">{{ result || "—" }}</pre>
    </div>
  </section>
</template>

<script setup>
import { ref, computed } from "vue";
import axios from "axios";
import { storeToRefs } from "pinia";
import { useTriageStore } from "@/store/triageStore";
import { useI18n } from "@/i18n/useI18n";

const { t } = useI18n();
const store = useTriageStore();
const { profile: storeProfile } = storeToRefs(store);

const profile = computed(() => storeProfile.value || {});
const symptoms = computed(() => store.selectedSymptoms || []);
const text = computed(() => store.textInput || "");
const audioBlob = computed(() => store.audioBlob || null);
const sa = computed(() => store.selfAssessment || {});

const submitting = ref(false);
const error = ref("");
const result = ref("");

// API
const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:5000";
const TRIAGE_URL = `${API_BASE}/api/triage/summary`;

async function submitSummary() {
  error.value = "";
  result.value = "";
  submitting.value = true;
  try {
    const { data } = await axios.post(TRIAGE_URL, { profile: profile.value });
    // render summary + next steps plainly
    const next =
      data.next_steps && data.next_steps.length
        ? `\n\nNext steps:\n• ${data.next_steps.join("\n• ")}`
        : "";
    result.value = `${data.summary || ""}${next}`;
  } catch (e) {
    error.value =
      e?.response?.data?.message ||
      e.message ||
      "NetworkError when attempting to fetch resource.";
  } finally {
    submitting.value = false;
  }
}

// symptom label mapping
const { t: tt } = useI18n();
const keyToLabel = {
  abdominal_pain: tt("symptom.abdominal_pain"),
  fever_high: tt("symptom.fever_high"),
  cough: tt("symptom.cough"),
  sore_throat: tt("symptom.sore_throat"),
  headache: tt("symptom.headache"),
  nausea: tt("symptom.nausea"),
  vomit: tt("symptom.vomit"),
  diarrhea: tt("symptom.diarrhea"),
  chest_pain: tt("symptom.chest_pain"),
  short_breath: tt("symptom.short_breath"),
  rash: tt("symptom.rash"),
  fatigue: tt("symptom.fatigue"),
};
function labelOf(k) {
  return keyToLabel[k] || k;
}
</script>

<style scoped>
.wrap {
  max-width: 980px;
  margin: 0 auto;
}
.card {
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 14px;
  background: var(--card);
  margin-bottom: 16px;
}
.list {
  line-height: 1.8;
}
.actions {
  display: flex;
  gap: 8px;
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
.tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.tag {
  border: 1px solid var(--btn-outline-border);
  padding: 4px 8px;
  border-radius: 999px;
}
.muted {
  color: var(--muted);
}
.result {
  white-space: pre-wrap;
  background: #fff;
  border: 1px solid var(--border);
  padding: 10px;
  border-radius: 8px;
  margin: 0;
}
</style>
