<template>
  <section class="wrap card">
    <h2>Prediction Result</h2>
    <div v-if="report">
      <p><strong>Disease:</strong> {{ report.disease }}</p>
      <p class="muted">Job: {{ report.jobId }}</p>
    </div>
    <p v-else class="muted">No result yet.</p>
  </section>
</template>

<script setup>
import { storeToRefs } from 'pinia'
import { useTriageStore } from '@/store/triageStore'
const { lastReport: report } = storeToRefs(useTriageStore())
</script>

<style scoped>
.wrap{max-width:980px;margin:0 auto}
.card{border:1px solid var(--border);border-radius:12px;padding:16px;background:var(--card)}
.muted{color:var(--muted)}
</style>
