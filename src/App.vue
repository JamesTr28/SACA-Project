<template>
  <div class="app">
    <div class="bg-floating">
      <img v-for="n in bgImages" :key="n" :src="`/src/assets/bg/${n}.png`" class="float" />
    </div>
    
    <header class="navbar">
      <div class="brand" @click="$router.push('/')">
        <img src="/src/assets/logo.jpg" alt="logo" />
        <span>{{ t('brand') }}</span>
      </div>

      <nav class="links">
        <RouterLink to="/" class="nav-btn">{{ t('nav.home') }}</RouterLink>
        <RouterLink to="/profile" class="nav-btn outline">{{ t('nav.history') }}</RouterLink>
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
import { onMounted, nextTick, onBeforeUnmount, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useTriageStore } from '@/store/triageStore'
import { useI18n } from '@/i18n/useI18n'

// 背景图片编号（/src/assets/bg/{n}.png）
const bgImages = [1, 2, 3, 4, 5, 6, 7]

// ========== 随机不重叠漂浮算法 ==========
const MIN_SIZE = 64
const MAX_SIZE = 140
const GAP = 12
const MAX_TRIES_PER_IMG = 120

function rand(min, max) {
  return Math.random() * (max - min) + min
}
function clamp(v, lo, hi) {
  return Math.max(lo, Math.min(hi, v))
}
function radiusOf(size) {
  return size / 2
}

function placeNonOverlapping(vw, vh, elements) {
  const placed = []
  for (let i = 0; i < elements.length; i++) {
    let tries = 0
    const size = rand(MIN_SIZE, MAX_SIZE)
    const r = radiusOf(size)
    let found = false

    while (tries++ < MAX_TRIES_PER_IMG && !found) {
      const x = rand(r + GAP, vw - (r + GAP))
      const y = rand(r + GAP, vh - (r + GAP))

      let ok = true
      for (const p of placed) {
        const dx = x - p.x
        const dy = y - p.y
        const dist2 = dx * dx + dy * dy
        const minDist = r + p.r + GAP
        if (dist2 < minDist * minDist) {
          ok = false
          break
        }
      }

      if (ok) {
        const driftMax = 80
        const driftX = rand(-driftMax, driftMax)
        const driftY = rand(-driftMax, driftMax)
        const duration = 28 + Math.random() * 18
        const delay = Math.random() * 8
        placed.push({ x, y, r, size, driftX, driftY, duration, delay })
        found = true
      }
    }

    if (!found) {
      const size = rand(MIN_SIZE, MAX_SIZE)
      const r = radiusOf(size)
      const x = clamp(rand(r + GAP, vw - (r + GAP)), r, vw - r)
      const y = clamp(rand(r + GAP, vh - (r + GAP)), r, vh - r)
      const driftX = rand(-60, 60)
      const driftY = rand(-60, 60)
      const duration = 28 + Math.random() * 18
      const delay = Math.random() * 8
      placed.push({ x, y, r, size, driftX, driftY, duration, delay })
    }
  }
  return placed
}

let resizeTimer = null
function initFloating() {
  const els = Array.from(document.querySelectorAll('.bg-floating .float'))
  if (!els.length) return
  const vw = window.innerWidth
  const vh = window.innerHeight
  const placed = placeNonOverlapping(vw, vh, els)

  els.forEach((el, idx) => {
    const p = placed[idx]
    el.style.left = `${p.x - p.r}px`
    el.style.top = `${p.y - p.r}px`
    el.style.width = `${p.size}px`
    el.style.setProperty('--dx', `${p.driftX}px`)
    el.style.setProperty('--dy', `${p.driftY}px`)
    el.style.animationDuration = `${p.duration}s`
    el.style.animationDelay = `${p.delay}s`
    el.style.opacity = String(0.15 + Math.random() * 0.15)
    el.style.transform = `scale(${0.7 + Math.random() * 0.8})`
  })
}

// ========== 页面挂载 ==========
onMounted(async () => {
  await nextTick()
  initFloating()
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimer)
    resizeTimer = setTimeout(initFloating, 150)
  })
})

onBeforeUnmount(() => {
  if (resizeTimer) clearTimeout(resizeTimer)
  window.removeEventListener('resize', initFloating)
})

// ========== 夜间模式 & 多语言 ==========
const triage = useTriageStore()
const { isAuthenticated, user } = storeToRefs(triage)
const { t, ui } = useI18n()
const logout = () => triage.logout()
const year = new Date().getFullYear()

function toggleTheme() {
  ui.toggleTheme()
  applyTheme()
}
function toggleLocale() {
  ui.toggleLocale()
}
function applyTheme() {
  const root = document.documentElement
  root.classList.toggle('dark', ui.theme === 'dark')
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

