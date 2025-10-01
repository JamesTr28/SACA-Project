<template>
  <section class="grid">
    <!-- 左侧：三种输入 -->
    <div class="left">
      <h2>Input</h2>

      <!-- 文本输入 -->
      <section class="card">
        <h3>Text input</h3>
        <textarea
          v-model="text"
          placeholder="Describe your symptoms in English..."
          rows="6"
        ></textarea>
      </section>

      <!-- 结构化输入 -->
      <section class="card">
        <h3>Structured input</h3>

        <div class="row">
          <label>Age</label>
          <input type="number" v-model="structured.age" min="0" />
        </div>

        <div class="row">
          <label>Gender</label>
          <select v-model="structured.gender">
            <option value="">-</option>
            <option>F</option>
            <option>M</option>
            <option>Other</option>
          </select>
        </div>

        <div class="row">
          <label>Severity</label>
          <div class="flex-1">
            <SeverityInput v-model="structured.severity" />
          </div>
        </div>

        <div class="row col">
          <SymptomInspector
            v-model="structured.topSymptoms"
            :extracted="report?.extractedSymptoms || []"
          />
        </div>
      </section>

      <!-- 语音输入 -->
      <section class="card">
        <h3>Voice input</h3>
        <AudioCapture @recorded="onRecorded" />
        <small class="muted"
          >Tip: recording up to 60s. Audio is uploaded on submit.</small
        >
      </section>

      <!-- 提交与状态 -->
      <div class="actions">
        <button class="btn primary" :disabled="submitting" @click="submit">
          {{ submitting ? 'Submitting...' : 'Submit for triage' }}
        </button>
        <button class="btn outline" :disabled="submitting" @click="resetForm">
          Reset
        </button>
      </div>

      <p v-if="error" class="err">⚠ {{ error }}</p>
      <ul class="logs" v-if="logs.length">
        <li v-for="(l, i) in logs" :key="i">{{ l }}</li>
      </ul>
    </div>

    <!-- 右侧：结果报告 -->
    <div class="right">
      <h2>Report</h2>
      <ResultsPanel :report="report" :loading="submitting" :error="error" />
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useTriageStore } from '@/store/triageStore'
import AudioCapture from '@/components/AudioCapture.vue'
import ResultsPanel from '@/components/ResultsPanel.vue'
import SeverityInput from '@/components/SeverityInput.vue'
import SymptomInspector from '@/components/SymptomInspector.vue'

const store = useTriageStore()
const { submitting, error, logs, report, structuredInput } = storeToRefs(store)

// 与 Pinia 双向绑定
const text = computed({
  get: () => store.textInput,
  set: (v) => store.setText(v),
})
const structured = computed({
  get: () => structuredInput.value,
  set: (v) => store.setStructured(v),
})

// 语音回传
function onRecorded(blob) {
  store.setAudio(blob) // null 表示重录清空
}

// 提交
function submit() {
  store.submitAll()
}

// 重置表单（不动登录态、历史报告）
function resetForm() {
  store.setText('')
  store.setStructured({ age: '', gender: '', topSymptoms: [], severity: 0 })
  store.setAudio(null)
}
</script>

<style scoped>
.grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}
.left .card {
  margin-bottom: 16px;
}
.card {
  border: 1px solid #eee;
  border-radius: 12px;
  padding: 14px;
  background: #fff;
}
.row {
  display: flex;
  gap: 12px;
  align-items: center;
  margin: 8px 0;
}
.col {
  flex-direction: column;
  align-items: stretch;
}
.flex-1 {
  flex: 1;
}
textarea,
input,
select {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 8px;
}
.actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}
.btn.primary {
  background: #111;
  color: #fff;
  border: none;
  padding: 10px 14px;
  border-radius: 10px;
}
.btn.outline {
  background: #fff;
  color: #111;
  border: 1px solid #111;
  padding: 10px 14px;
  border-radius: 10px;
}
.err {
  color: #c0392b;
  margin-top: 6px;
}
.logs {
  margin-top: 8px;
  color: #666;
  font-size: 12px;
}
.muted {
  color: #6b7280;
}
@media (max-width: 980px) {
  .grid {
    grid-template-columns: 1fr;
  }
}
</style>
