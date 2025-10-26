<template>
  <section class="wrap">
    <h2>How this project works</h2>
    <div class="card">
  <p>
    <strong>English:</strong><br>
    Welcome! Please provide some basic information before starting the triage.
  </p>
  <p>
    <strong>Warlpiri:</strong><br>
    Yapa! Kurdu watiya nyampu yapa‐kurlu majja yapa­kurlu murnu marnku, nyinami triage‐warra wangkayarla.
  </p>

  <p>
    <strong>English Note:</strong> This is a demo project. Do not use it for real medical decisions.<br>
    <strong>Warlpiri Note:</strong> Nyinami: Pina‐yapa proyekti karrijikarla. Yapa-kurlu yaninjaku mirnlaku wangkami “real” wita­mi ­marnu ­warninjaku.
  </p>

  <ol>
    <li>
      <strong>English:</strong> You will be guided through a series of questions in a chat format.<br>
      <strong>Warlpiri:</strong> Yapa-kurlu kurlu chat format­ku wangkami yirrarni nyanungu watiya yawulyurrpa jurnarda.
    </li>
    <li>
      <strong>English:</strong> Your information will be used to create a summary for review.<br>
      <strong>Warlpiri:</strong> Yapa-kurlu nyanungu marnu wangkami summary-kurlu yangka review­jarra.
    </li>
    <li>
      <strong>English:</strong> This information will be sent to the backend for a holistic judgement.<br>
      <strong>Warlpiri:</strong> Yapa-kurlu nyanungu marnu wangkami backend­kurlu karnalu holistic judgement kura­kurlu.
    </li>
  </ol>

  <div class="actions">
    <button class="btn primary" @click="go">I understand and agree to start / Nyinami-ngarni karnalu yaninja</button>
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