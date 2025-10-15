import { createRouter, createWebHistory } from 'vue-router'
import IntroPage from '@/pages/IntroPage.vue'
import InfoPage from '@/pages/InfoPage.vue'
import TriagePage from '@/pages/TriagePage.vue'
import ConfirmPage from '@/pages/ConfirmPage.vue'
import LoginPage from '@/pages/LoginPage.vue'
import RegisterPage from '@/pages/RegisterPage.vue'
import ProfilePage from '@/pages/ProfilePage.vue'
import PredictionPage from '@/pages/PredictionPage.vue'   // ✅ ★ 必须加这一行 ★
import { useTriageStore } from '@/store/triageStore'

const routes = [
  { path: '/', redirect: '/triage' },                     // ✅ 建议保留唯一根路由
  { path: '/intro', name: 'intro', component: IntroPage },
  { path: '/info', name: 'info', component: InfoPage },
  { path: '/triage', name: 'triage', component: TriagePage },
  { path: '/confirm', name: 'confirm', component: ConfirmPage },
  { path: '/predict', name: 'predict', component: PredictionPage },  // ✅ 现在可以用了
  { path: '/profile', name: 'profile', component: ProfilePage, meta: { requiresAuth: true } },
  { path: '/login', name: 'login', component: LoginPage },
  { path: '/register', name: 'register', component: RegisterPage },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 守卫逻辑：若目标需要登录且未认证，则跳转登录
router.beforeEach((to) => {
  const store = useTriageStore()
  if (to.meta.requiresAuth && !store.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
})

export default router
