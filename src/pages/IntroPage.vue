<template>
  <section class="wrap">
    <h2>Welcome</h2>
    <p>This is a simple medical triage demo app that helps you make a preliminary assessment of the severity and urgency of your symptoms.</p>
    <p>This system cannot replace a real doctor and cannot prescribe medicine. It only provides advice to users. If you feel unwell, please consult a doctor.</p>
    <ol class="steps">
      <li>First fill in the basic information</li>
      <li>Then on the input page, describe your symptoms by text/voice/picture.</li>
      <li>Then, you will be asked to rate the severity and personal feelings on a scale of 1–10 (with explanations for each level)。</li>
      <li>The system will send all information to the backend for judgment, automatically analyze your symptoms, and give suggestions.</li>
    </ol>
    <p class="muted">Tip: Your personal information will be sent together with your symptoms to the backend for comprehensive judgment.</p>

    <button class="btn primary" @click="$router.push('/info')">I understand and agree to start</button>
  </section>
</template>

<script setup>
</script>

<style scoped>
.wrap{max-width:820px;margin:0 auto}
.steps{line-height:1.8}
.muted{color:var(--muted);margin:12px 0}
.btn.primary{background:var(--btn-bg);color:var(--btn-fg);border:none;padding:10px 14px;border-radius:10px}
</style>
