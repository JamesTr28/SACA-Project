<template>
  <section class="wrap">
    <h2>History</h2>

    <div v-if="!items.length" class="muted">No records yet.</div>

    <div v-else class="list">
      <article v-for="it in items" :key="it.id" class="card">
        <header class="row space">
          <strong>#{{ it.id }}</strong>
          <small>{{ new Date(it.time).toLocaleString() }}</small>
        </header>

        <div class="row">
          <div class="col">
            <h4>Input</h4>
            <p><b>Symptoms:</b> {{ (it.input?.symptoms || []).join(', ') || '(none)' }}</p>
            <p><b>Text:</b> {{ it.input?.text || '(none)' }}</p>
            <p><b>Transcript:</b> {{ it.input?.transcript || '(none)' }}</p>
          </div>
          <div class="col">
            <h4>Result</h4>
            <pre class="pre">{{ it.report ? it.report : '(no report)' }}</pre>
          </div>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup>
import { storeToRefs } from 'pinia'
import { useTriageStore } from '@/store/triageStore'
const store = useTriageStore()
const { history: items } = storeToRefs(store)
</script>

<style scoped>
.wrap{max-width:980px;margin:0 auto}
.muted{color:var(--muted)}
.list{display:grid;gap:12px}
.card{border:1px solid var(--border);background:var(--card);border-radius:12px;padding:12px}
.row{display:flex;gap:16px;flex-wrap:wrap}
.row.space{justify-content:space-between}
.col{flex:1;min-width:260px}
.pre{white-space:pre-wrap;background:rgba(255,255,255,.6);border:1px dashed var(--border);padding:8px;border-radius:8px}
</style>
