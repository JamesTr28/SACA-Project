<template>
  <div class="auth-card">
    <h2>{{ t('auth.register') }}</h2>
    <form @submit.prevent="go">
      <input v-model="name" :placeholder="t('auth.name')" required />
      <input v-model="email" type="email" :placeholder="t('auth.email')" required />
      <input v-model="password" type="password" :placeholder="t('auth.password')" required />
      <button class="btn primary" :disabled="loading">{{ loading ? t('common.loading') : t('auth.register') }}</button>
    </form>
    <p class="hint">{{ t('auth.haveAccount') }} <RouterLink to="/login">{{ t('auth.login') }}</RouterLink></p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useTriageStore } from '@/store/triageStore'
import { useI18n } from '@/i18n/useI18n'

const { t } = useI18n()

const store = useTriageStore()
const router = useRouter()
const name = ref(''), email = ref(''), password = ref('')
const loading = ref(false)

async function go(){
  loading.value = true
  await store.register({ name: name.value, email: email.value, password: password.value })
    .catch(e=> alert(e.message))
  loading.value = false
  router.replace('/')
}
</script>

<style scoped>
.auth-card{max-width:420px;margin:40px auto;padding:20px;border:1px solid #eee;border-radius:12px}
input{width:100%;padding:10px;margin:8px 0;border:1px solid #ddd;border-radius:8px}
.btn.primary{background:#111;color:#fff;border:none;padding:10px 14px;border-radius:10px;width:100%}
.hint{margin-top:8px}
</style>