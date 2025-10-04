<template>
  <div class="profile">
    <h2>Personal Information</h2>

    <form class="card" @submit.prevent="save">
      <div class="row">
        <label>Gender</label>
        <select v-model.number="profile.gender">
          <option :value="1">Male</option>
          <option :value="0">Female</option>
        </select>
      </div>

      <div class="row">
        <label>Age</label>
        <input type="number" v-model="profile.age" min="0" />
      </div>

      <div class="row col">
        <label>Past medical history</label>
        <textarea v-model="profile.conditions" rows="2" placeholder="For example: high blood pressure, diabetes"></textarea>
      </div>

      <div class="row col">
        <label>History of allergies</label>
        <textarea v-model="profile.allergies" rows="2" placeholder="Example: Penicillin allergy"></textarea>
      </div>

      <div class="row col">
        <label>Medications in use</label>
        <textarea v-model="profile.medications" rows="2" placeholder="For example: metformin, amlodipine"></textarea>
      </div>

      <div class="actions">
        <button class="btn primary" type="submit">Save</button>
      </div>
    </form>

    <p class="muted">
      This information will be sent to the backend together with each submission for comprehensive judgment.
    </p>
  </div>
</template>

<script setup>
import { useTriageStore } from '@/store/triageStore'

const store = useTriageStore()
// 直接用 store.profile，本身是响应式的
const profile = store.profile

function save() {
  store.updateProfile({ ...profile })
  alert('Profile saved successfully')
}
</script>

<style scoped>
.profile{max-width:720px;margin:0 auto}
.card{border:1px solid var(--border);border-radius:12px;padding:14px;background:var(--card)}
.row{display:flex;gap:12px;align-items:center;margin:8px 0}
.col{flex-direction:column;align-items:stretch}
textarea,input,select{width:100%;padding:8px;border:1px solid var(--border);border-radius:8px;background:transparent;color:inherit}
.actions{margin-top:8px}
.btn.primary{background:var(--btn-bg);color:var(--btn-fg);border:none;padding:10px 14px;border-radius:10px}
</style>
