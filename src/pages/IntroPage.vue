<template>
  <section class="wrap">
    <h2>How this project works</h2>
    <div class="card">
      <p>Welcome! Please provide some basic information before starting the triage.</p>
      <p><strong>Note:</strong> This is a demo project. Do not use it for real medical decisions.</p>
      <ol>
        <li>You will be guided through a series of questions in a chat format.</li>
        <li>Your information will be used to create a summary for review.</li>
        <li>This information will be sent to the backend for a holistic judgement.</li>
      </ol>
      <div class="actions">
        <button class="btn primary" @click="go">I understand and agree to start</button>
      </div>
    </div>
  </section>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

// This is the one, correct function.
function go(){
  router.push('/chatbot')
}
</script>

<style scoped>
/* Basic styling to match the project */
.wrap { max-width: 720px; margin: 40px auto; padding: 20px; }
.card { border: 1px solid #e0e0e0; border-radius: 12px; padding: 24px; background: #fff; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
ol { margin-left: 20px; }
.actions { margin-top: 24px; text-align: center; }
.btn.primary { background: #2c5282; color: white; border: none; padding: 12px 20px; border-radius: 8px; cursor: pointer; font-size: 16px; }
.btn.primary:hover { background: #1a365d; }
</style>