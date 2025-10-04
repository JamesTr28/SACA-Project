<template>
  <section class="wrap">
    <h2>TEXT INPUT</h2>
    <textarea v-model="text" rows="8" placeholder="Enter symptom description here"></textarea>

    <div class="actions">
      <button class="btn primary" :disabled="submitting" @click="submit">{{ submitting ? '...' : 'SUBMITTED' }}</button>
      <button class="btn outline" :disabled="submitting" @click="clearAll"> CLEAR </button>
    </div>

    <h3>RESULTS</h3>
    <ResultsPanel :report="report" :loading="submitting" :error="error" />
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useTriageStore } from '@/store/triageStore'
import ResultsPanel from '@/components/ResultsPanel.vue'

const store = useTriageStore()
const { submitting, error, lastReport: report } = storeToRefs(store)

const text = computed({
  get: () => store.textInput,
  set: (v) => store.setText(v),
})

async function submit(){ await store.submitFromText() }
function clearAll(){ store.setText('') }
</script>

<style scoped>
.wrap{max-width:900px;margin:0 auto}
textarea{width:100%;padding:12px;border:1px solid var(--border);border-radius:10px;background:transparent;color:inherit}
.actions{display:flex;gap:8px;margin:12px 0}
.btn.primary{background:var(--btn-bg);color:var(--btn-fg);border:none;padding:10px 14px;border-radius:10px}
.btn.outline{background:var(--btn-outline-bg);color:var(--btn-outline-fg);border:1px solid var(--btn-outline-border);padding:10px 14px;border-radius:10px}
</style>
