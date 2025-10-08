<template>
  <section class="wrap">
    <h2>Fill in basic information</h2>
    <form class="card" @submit.prevent="go">
      
      <div class="row">
        <label>Gender</label>
        <CustomSelect
        v-model="form.gender"
        :options="[{label:'Male',value:1},{label:'Female',value:0}]"
        placeholder="Select gender"
        />
      </div>


      <div class="row">
        <label>Age</label>
        <input type="number" v-model="form.age" min="0" />
      </div>

      <div class="row">
        <label>Weight(kg)</label>
        <input type="number" v-model="form.weight" min="0" />
      </div>

      <div class="row col">
        <label>Current situation</label>
        <textarea v-model="form.conditions" rows="2" placeholder="e.g. high blood pressure, diabetes"></textarea>
      </div>

      <div class="row col">
        <label>Allergies</label>
        <textarea v-model="form.allergies" rows="2" placeholder="e.g. gluten, lactose"></textarea>
      </div>

      <div class="row col">
        <label>Medications in use</label>
        <textarea v-model="form.medications" rows="2" placeholder="For example: metformin, amlodipine"></textarea>
      </div>

      <div class="actions">
        <button class="btn primary" type="submit">Next step</button>
      </div>
    </form>
  </section>
</template>

<script setup>
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useTriageStore } from '@/store/triageStore'
import CustomSelect from '@/components/CustomSelect.vue'   /* +++ */

const store = useTriageStore()
const router = useRouter()

const form = reactive({ ...store.profile })
function go(){
  store.updateProfile({ ...form })
  router.push('/triage')
}
</script>

<style scoped>
.wrap{max-width:720px;margin:0 auto}
.card{border:1px solid var(--border);border-radius:12px;padding:14px;background:var(--card)}
.row{display:flex;gap:12px;align-items:center;margin:8px 0}
.col{flex-direction:column;align-items:stretch}
textarea,input,select{width:100%;padding:8px;border:1px solid var(--border);border-radius:8px;background:transparent;color:inherit}
.actions{margin-top:8px}
.btn.primary{background:var(--btn-bg);color:var(--btn-fg);border:none;padding:10px 14px;border-radius:10px}
</style>
