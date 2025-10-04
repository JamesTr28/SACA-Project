<template>
  <section class="wrap">
    <h2>IMAGE INPUT</h2>
    <SymptomImagePicker v-model="selected" />

    <div class="text-add">
      <input v-model="note" placeholder="Additional notes (optional)" />
    </div>

    <div class="actions">
      <button class="btn primary" :disabled="submitting || !selected.length" @click="submit">
        {{ submitting ? '...' : 'SUBMIT (' + selected.length +' images in total)' }}
      </button>
      <button class="btn outline" :disabled="submitting" @click="clearAll">CLEAR</button>
    </div>

    <h3>RESULTS</h3>
    <ResultsPanel :report="report" :loading="submitting" :error="error" />
  </section>
</template>

<script setup>
import { computed, ref } from 'vue'
import { storeToRefs } from 'pinia'
import { useTriageStore } from '@/store/triageStore'
import SymptomImagePicker from '@/components/SymptomImagePicker.vue'
import ResultsPanel from '@/components/ResultsPanel.vue'

const store = useTriageStore()
const { submitting, error, lastReport: report } = storeToRefs(store)
const note = ref('') 

const selected = computed({
  get: () => store.selectedSymptoms,
  set: (v) => store.setSelectedSymptoms(v),
})

async function submit(){
  // 
  if (note.value) store.setText(note.value)
  await store.submitFromImages()
}
function clearAll(){
  store.setSelectedSymptoms([])
  note.value = ''
}
</script>

<style scoped>
.wrap{max-width:980px;margin:0 auto}
.text-add{margin:12px 0}
.text-add input{width:100%;padding:10px;border:1px solid var(--border);border-radius:10px;background:transparent;color:inherit}
.actions{display:flex;gap:8px;margin:12px 0}
.btn.primary{background:var(--btn-bg);color:var(--btn-fg);border:none;padding:10px 14px;border-radius:10px}
.btn.outline{background:var(--btn-outline-bg);color:var(--btn-outline-fg);border:1px solid var(--btn-outline-border);padding:10px 14px;border-radius:10px}
</style>
