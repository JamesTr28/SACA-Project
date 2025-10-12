<template>
  <div class="card">
    <template v-if="loading">
      <div class="empty">Generating report...</div>
    </template>

    <template v-else-if="error">
      <div class="empty err">{{ error }}</div>
    </template>

    <template v-else-if="!report">
      <div class="empty">No report yet. Submit from the left.</div>
    </template>

    <template v-else>
      <header class="header">
        <h3>Disease Prediction: {{ report.disease ?? "" }}</h3>
        <small>Job: {{ report.jobId }}</small>
        <div class="tools">
          <button class="btn small" @click="downloadJson">Download JSON</button>
          <button class="btn small outline" @click="copyJson">Copy</button>
        </div>
      </header>

      <section class="grid">
        <!-- <div class="block">
          <h4>Extracted Symptoms</h4>
          <ul class="chips">
            <li v-for="s in report.extractedSymptoms" :key="s.name">
              {{ s.name }} <small>({{ pct(s.weight) }})</small>
            </li>
          </ul>
        </div> -->

        <div class="block" v-if="report.modelVotes">
          <h4>Model Votes</h4>
          <table class="table">
            <thead>
              <tr>
                <th>Model</th>
                <th>Severity</th>
                <th>Confidence</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="m in report.modelVotes" :key="m.model">
                <td>{{ m.model }}</td>
                <td>{{ m.severity }}</td>
                <td>{{ pct(m.confidence) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup>
const props = defineProps({
  report: Object,
  loading: { type: Boolean, default: false },
  error: { type: String, default: "" },
});

function formatTime(t) {
  try {
    return new Date(t).toLocaleString();
  } catch {
    return t;
  }
}
function pct(v) {
  return v == null ? "-" : (v * 100).toFixed(1) + "%";
}

function downloadJson() {
  const blob = new Blob([JSON.stringify(props.report, null, 2)], {
    type: "application/json",
  });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `triage_report_${props.report?.jobId || "unknown"}.json`;
  a.click();
  URL.revokeObjectURL(url);
}
async function copyJson() {
  try {
    await navigator.clipboard.writeText(JSON.stringify(props.report, null, 2));
  } catch {}
}
</script>

<style scoped>
.card {
  border: 1px solid #eee;
  border-radius: 12px;
  padding: 14px;
  background: #fff;
}
.empty {
  color: #888;
}
.empty.err {
  color: #b91c1c;
}
.header {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 6px 12px;
  align-items: center;
}
.header h3 {
  margin: 0;
}
.muted {
  color: #6b7280;
}
.tools {
  display: flex;
  gap: 8px;
}
.btn.small {
  padding: 6px 10px;
  border-radius: 10px;
  background: #111;
  color: #fff;
}
.btn.small.outline {
  background: #fff;
  color: #111;
  border: 1px solid #111;
}
.grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
  margin-top: 12px;
}
.table {
  width: 100%;
  border-collapse: collapse;
}
.table th,
.table td {
  border-bottom: 1px solid #f0f0f0;
  padding: 8px;
  text-align: left;
}
.chips {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  padding: 0;
  margin: 0;
  list-style: none;
}
.chips li {
  padding: 4px 8px;
  border: 1px solid #ddd;
  border-radius: 999px;
}
</style>
