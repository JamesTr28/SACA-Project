<template>
  <section class="wrap">
    <h2>History</h2>
    <div v-if="!list.length" class="muted">No records yet</div>

    <div class="items">
      <article v-for="it in list" :key="it.id" class="card item">
        <header>
          <strong>{{ new Date(it.at).toLocaleString() }}</strong>
          <span class="muted">ID: {{ it.id }}</span>
        </header>

        <div class="row">
          <label>INPUT</label>
          <code class="mono">{{ previewInput(it.input) }}</code>
        </div>

        <div class="row">
          <label>PROFILE</label>
          <code class="mono">{{ previewProfile(it.profile) }}</code>
        </div>

        <div class="row">
          <label>REPORT</label>
          <span>Severity: {{ it.report?.finalDecision?.severity ?? '-' }}</span>
        </div>

        <div class="ops">
          <button class="btn outline small" @click="view(it)">View</button>
          <button class="btn small" @click="download(it)">Download JSON</button>
        </div>
      </article>
    </div>

    <dialog ref="dlg">
      <pre class="mono">{{ pretty(selected) }}</pre>
      <div style="text-align:right;margin-top:12px">
        <button class="btn outline small" @click="dlg.close()">Close</button>
      </div>
    </dialog>
  </section>
</template>

<script setup>
import { ref, computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useTriageStore } from '@/store/triageStore'

const store = useTriageStore()
const { history } = storeToRefs(store)

const list = computed(()=> history.value)
const selected = ref(null)
const dlg = ref()

function previewInput(input){
  if (input.text) return 'text: ' + input.text.slice(0,60)
  if (input.symptoms) return 'symptoms: [' + input.symptoms.join(',') + ']'
  if (input.via === 'voice') return 'via: voice'
  return JSON.stringify(input)
}
function previewProfile(p){ return `gender=${p.gender} age=${p.age} cond=${(p.conditions||'').slice(0,20)}` }
function view(it){ selected.value = it; dlg.value.showModal() }
function pretty(o){ return JSON.stringify(o, null, 2) }
function download(it){
  const blob = new Blob([JSON.stringify(it, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob); const a=document.createElement('a')
  a.href=url; a.download=`history_${it.id}.json`; a.click(); URL.revokeObjectURL(url)
}
</script>

<style scoped>
.wrap{max-width:1000px;margin:0 auto}
.items{display:grid;grid-template-columns:1fr;gap:12px;margin-top:12px}
.item header{display:flex;gap:12px;justify-content:space-between}
.row{display:flex;gap:8px;align-items:center;margin:6px 0}
.row label{width:60px;color:var(--muted)}
.mono{font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; font-size:12px}
.ops{display:flex;gap:8px;margin-top:8px}
.btn.small{padding:6px 10px;border-radius:10px;background:var(--btn-bg);color:var(--btn-fg)}
.btn.outline.small{background:var(--btn-outline-bg);color:var(--btn-outline-fg);border:1px solid var(--btn-outline-border)}
dialog{max-width:800px}
</style>
