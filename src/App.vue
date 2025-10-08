<template>
  <div class="app">
    <header class="navbar">
      <div class="brand" @click="$router.push('/')">
        <img src="/src/assets/logo.jpg" alt="logo" />
        <span>{{ t('brand') }}</span>
      </div>

      <nav class="links">
        <RouterLink to="/" class="nav-btn">Home</RouterLink>
        <RouterLink to="/profile" class="nav-btn outline">History</RouterLink>
      </nav>

      <div class="right-tools">
        <!-- 语言切换 -->
        <button class="btn outline small" @click="toggleLocale">
          {{ ui.locale.toUpperCase() }}
        </button>

        <!-- 夜间模式切换 -->
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
import { onMounted, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useTriageStore } from '@/store/triageStore'
import { useUiStore } from '@/store/uiStore'
import { useI18n } from '@/i18n/useI18n'

const triage = useTriageStore()
const { isAuthenticated, user } = storeToRefs(triage)
const { t, ui } = useI18n()
const logout = () => triage.logout()
const year = new Date().getFullYear()

function toggleTheme() {
  ui.toggleTheme()
  applyTheme()
}
function toggleLocale() { ui.toggleLocale() }

// 让 .dark 类加在 <html> 上，确保全页面都受影响
function applyTheme() {
  const root = document.documentElement
  if (ui.theme === 'dark') {
    root.classList.add('dark')
  } else {
    root.classList.remove('dark')
  }
}

onMounted(() => {
  applyTheme()
})
watch(() => ui.theme, applyTheme)
</script>

<style scoped>
.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  border-bottom: 1px solid var(--border);
  background: var(--card);
  position: sticky;
  top: 0;
  z-index: 10;
}
.brand { display: flex; gap: 8px; align-items: center; cursor: pointer; }
.brand img { width: 28px; height: 28px; }
.links { display: flex; gap: 16px; }
.right-tools { display: flex; gap: 8px; align-items: center; }
.auth { display: flex; gap: 8px; align-items: center; }
.btn { padding: 6px 12px; border-radius: 10px; }
.btn.outline { border: 1px solid var(--btn-outline-border); }
.btn.small { padding: 4px 8px; }
.container { max-width: 1100px; margin: 0 auto; padding: 20px; }
.footer { padding: 24px 0; color: var(--muted); text-align: center; }
.hello { margin-right: 6px; }

/* Nav buttons — scoped in App.vue to beat global styles */
.links .nav-btn {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 6px 12px; border-radius: 999px;
  text-decoration: none;
  background: #2e7d32; color: #fff;
  border: 1px solid transparent;
  transition: transform .08s ease, box-shadow .12s ease;
}
.links .nav-btn:hover { transform: translateY(-1px); box-shadow: 0 2px 10px rgba(0,0,0,.08) }
.links .nav-btn.outline {
  background: transparent; color: #2e7d32;
  border-color: #2e7d32;
}
.links .router-link-active.nav-btn { box-shadow: inset 0 0 0 2px rgba(255,255,255,.18); }
</style>

<!-- 🌙 夜间模式全局变暗效果 -->
<style>
html.dark, body.dark, #app.dark,
.dark html, .dark body, .dark #app {
  filter: brightness(0.65) contrast(1.05);
  transition: filter 0.4s ease;
}

/* 平滑切换 */
body {
  transition: filter 0.4s ease, background 0.4s ease;
}
</style>

