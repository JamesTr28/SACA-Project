<template>
  <div class="auth-card">
    <h2>Login</h2>
    <form @submit.prevent="go">
      <input v-model="email" type="email" placeholder="Email" required />
      <input v-model="password" type="password" placeholder="Password" required />
      <button class="btn primary" :disabled="loading">{{ loading ? '...' : 'Login' }}</button>
    </form>
    <p class="hint">No account? <RouterLink to="/register">Register</RouterLink></p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useTriageStore } from '@/store/triageStore'

const store = useTriageStore()
const router = useRouter()
const route = useRoute()
const email = ref('')
const password = ref('')
const loading = ref(false)

async function go(){
  loading.value = true
  await store.login(email.value, password.value).catch(e=> alert(e.message))
  loading.value = false
  const redirect = route.query.redirect || '/'
  router.replace(redirect)
}
</script>

<style scoped>
.auth-card{max-width:420px;margin:40px auto;padding:20px;border:1px solid #eee;border-radius:12px}
input{width:100%;padding:10px;margin:8px 0;border:1px solid #ddd;border-radius:8px}
.btn.primary{background:#111;color:#fff;border:none;padding:10px 14px;border-radius:10px;width:100%}
.hint{margin-top:8px}
</style>
