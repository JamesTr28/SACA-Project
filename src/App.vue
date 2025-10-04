<template>
  <div class="app">
    <header class="navbar">
      <div class="brand" @click="$router.push('/')">
        <img src="/src/assets/logo.svg" alt="logo" />
        <span>Intelligent Triage</span>
      </div>

      <nav class="links">
        <RouterLink to="/">Home</RouterLink>
        <RouterLink to="/profile">Profile</RouterLink>
      </nav>

      <div class="auth">
        <template v-if="isAuthenticated">
          <span class="hello">Hi, {{ user?.name || user?.email }}</span>
          <button class="btn outline" @click="logout">Logout</button>
        </template>
        <template v-else>
          <RouterLink to="/login" class="btn">Login</RouterLink>
          <RouterLink to="/register" class="btn outline">Register</RouterLink>
        </template>
      </div>
    </header>

    <main class="container">
      <RouterView />
    </main>

    <footer class="footer">© {{ year }} Triage Demo</footer>
  </div>
</template>

<script setup>
import { storeToRefs } from 'pinia'
import { useTriageStore } from '@/store/triageStore'
const store = useTriageStore()
const { isAuthenticated, user } = storeToRefs(store)
const logout = () => store.logout()
const year = new Date().getFullYear()
</script>

<style scoped>
.navbar{display:flex;align-items:center;justify-content:space-between;padding:12px 20px;border-bottom:1px solid #eee;background:#fff;position:sticky;top:0;z-index:10}
.brand{display:flex;gap:8px;align-items:center;cursor:pointer}
.brand img{width:28px;height:28px}
.links{display:flex;gap:16px}
.auth{display:flex;gap:8px;align-items:center}
.btn{padding:6px 12px;border-radius:10px;background:#111;color:#fff}
.btn.outline{background:#fff;color:#111;border:1px solid #111}
.container{max-width:1100px;margin:0 auto;padding:20px}
.footer{padding:24px 0;color:#888;text-align:center}
.hello{margin-right:6px}
</style>

<template>
  <Translator />
</template>
<script setup>
import Translator from '@/components/Translator.vue'
</script>