<template>
  <section class="wrap">
    <h2>{{ t('info.title') }}</h2>
    <form class="card" @submit.prevent="go">
      
      <div class="row">
        <label>{{ t('info.gender') }}</label>
        <CustomSelect
        v-model="form.gender"
        :options="genderOptions"
        :placeholder="t('select.placeholder')"
        />
      </div>


      <div class="row">
        <label>{{ t('info.age') }}</label>
        <input type="number" v-model="form.age" min="0" />
      </div>

      <div class="row">
        <label>{{ t('info.weight') }} (kg)</label>
        <input type="number" v-model="form.weight" min="0" />
      </div>

      <div class="row col">
        <label>{{ t('info.conditions') }}</label>
        <textarea v-model="form.conditions" rows="2" :placeholder="t('info.conditions_ph')"></textarea>
      </div>

      <div class="row col">
        <label>{{ t('info.allergies') }}</label>
        <textarea v-model="form.allergies" rows="2" :placeholder="t('info.allergies_ph')"></textarea>
      </div>

      <div class="row col">
        <label>{{ t('info.meds') }}</label>
        <textarea v-model="form.medications" rows="2" :placeholder="t('info.meds_ph')"></textarea>
      </div>

      <div class="actions">
        <button class="btn primary" type="submit">{{ t('info.next') }}</button>
      </div>
    </form>
  </section>
</template>

<script setup>
import { reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useTriageStore } from '@/store/triageStore'
import { useI18n } from '@/i18n/useI18n'
import CustomSelect from '@/components/CustomSelect.vue'   /* +++ */

const { t } = useI18n()

const store = useTriageStore()
const router = useRouter()

const form = reactive({ ...store.profile })

const genderOptions = computed(() => [
  { label: t('info.male'), value: 1 },
  { label: t('info.female'), value: 0 }
])

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