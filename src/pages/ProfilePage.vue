<template>
  <section class="wrap">
    <h2>Results History</h2>
    <div v-if="!list.length" class="muted">No records yet</div>

    <div class="items">
      <article v-for="it in list" :key="it.id" class="card item">
        <header>
          <strong>{{ new Date(it.at).toLocaleString() }}</strong>
          <span class="muted">ID: {{ it.id }}</span>
        </header>

        <div class="row">
          <label>User</label>
          <code class="mono">
            gender={{ it.payload?.profile?.gender }} age={{ it.payload?.profile?.age }}
          </code>
        </div>

        <div class="row">
          <label>Input</label>
          <code class="mono">
            {{ it.payload?.text ? 'text' : '' }}
            {{ it.payload?.symptoms?.length ? (' symptoms['+it.payload.symptoms.join(',')+']') : '' }}
          </code>
        </div>

        <div class="row">
          <label>Result</label>
          <span>Severity: {{ it.report?.finalDecision?.severity ?? '-' }}</span>
        </div>

        <div class="row" v-if="it.selfAssessment">
          <label>Self-Assessment</label>
          <span>Severe {{ it.selfAssessment.severity }} / Feeling {{ it.selfAssessment.feeling }}</span>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useTriageStore } from '@/store/triageStore'

const store = useTriageStore()
const { history } = storeToRefs(store)
const list = computed(()=> history.value)
</script>

<style scoped>
.wrap{max-width:1000px;margin:0 auto}
.items{display:grid;grid-template-columns:1fr;gap:12px;margin-top:12px}
.item header{display:flex;gap:12px;justify-content:space-between}
.row{display:flex;gap:8px;align-items:center;margin:6px 0}
.row label{width:60px;color:var(--muted)}
.mono{font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; font-size:12px}
.card{border:1px solid var(--border);border-radius:12px;padding:14px;background:var(--card)}
.muted{color:var(--muted)}
</style>
