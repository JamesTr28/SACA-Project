<template>
  <div class="app">
    <header class="navbar">
      <div class="brand" @click="$router.push('/')">
        <img src="/src/assets/logo.jpg" alt="logo" />
        <span>{{ t('brand') }}</span>
      </div>

      <nav class="links">
        <RouterLink to="/">{{ t('nav.home') }}</RouterLink>
        <RouterLink to="/history">History</RouterLink>
        <RouterLink to="/profile">{{ t('nav.profile') }}</RouterLink>
      </nav>


      <div class="right-tools">
        <!-- 语言切换 -->
        <button class="btn outline small" @click="toggleLocale">
          {{ ui.locale.toUpperCase() }}
        </button>
        <!--  -->
        <button class="btn outline small" @click="toggleTheme">
          {{ ui.theme === 'dark' ? '☾' : '☀' }}
        </button>

        <!-- 登录状态 -->
        <div class="auth">
          <template v-if="isAuthenticated">
            <span class="hello">{{ t('auth.hi') }}, {{ user?.name || user?.email }}</span>
            <button class="btn outline" @click="logout">{{ t('auth.logout') }}</button>
          </template>
          <template v-else>
            <RouterLink to="/login" class="btn">{{ t('auth.login') }}</RouterLink>
            <RouterLink to="/register" class="btn outline">{{ t('auth.register') }}</RouterLink>
          </template>
        </div>
      </div>
    </header>

    <main class="container">
      <RouterView />
    </main>

    <footer class="footer">© {{ year }} Triage Demo</footer>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useTriageStore } from '@/store/triageStore'
import { useUiStore } from '@/store/uiStore'
import { useI18n } from '@/i18n/useI18n'

const triage = useTriageStore()
const { isAuthenticated, user } = storeToRefs(triage)
const { t, ui } = useI18n()

const logout = () => triage.logout()
const year = new Date().getFullYear()

function toggleTheme() { ui.toggleTheme() }
function toggleLocale() { ui.toggleLocale() }

onMounted(() => {
  // 初始化主题类到 <html>
  ui.setTheme(ui.theme)
})
</script>

<style scoped>
.navbar{display:flex;align-items:center;justify-content:space-between;padding:12px 20px;border-bottom:1px solid var(--border);background:var(--card);position:sticky;top:0;z-index:10}
.brand{display:flex;gap:8px;align-items:center;cursor:pointer}
.brand img{width:28px;height:28px}
.links{display:flex;gap:16px}
.right-tools{display:flex;gap:8px;align-items:center}
.auth{display:flex;gap:8px;align-items:center}
.btn{padding:6px 12px;border-radius:10px}
.btn.outline{border:1px solid var(--btn-outline-border)}
.btn.small{padding:4px 8px}
.container{max-width:1100px;margin:0 auto;padding:20px}
.footer{padding:24px 0;color:var(--muted);text-align:center}
.hello{margin-right:6px}
</style>

