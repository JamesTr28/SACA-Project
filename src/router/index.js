import { createRouter, createWebHistory } from 'vue-router'
import IntroPage from '@/pages/IntroPage.vue'
import InfoPage from '@/pages/InfoPage.vue'
import TriagePage from '@/pages/TriagePage.vue'
import ConfirmPage from '@/pages/ConfirmPage.vue'
import LoginPage from '@/pages/LoginPage.vue'
import RegisterPage from '@/pages/RegisterPage.vue'
import ProfilePage from '@/pages/ProfilePage.vue'
import { useTriageStore } from '@/store/triageStore'

const routes = [
  { path: '/', name: 'intro', component: IntroPage },
  { path: '/info', name: 'info', component: InfoPage },
  { path: '/triage', name: 'triage', component: TriagePage },
  { path: '/confirm', name: 'confirm', component: ConfirmPage },
  { path: '/profile', name: 'profile', component: ProfilePage, meta: { requiresAuth: true } },
  { path: '/login', name: 'login', component: LoginPage },
  { path: '/register', name: 'register', component: RegisterPage },
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to) => {
  const store = useTriageStore()
  if (to.meta.requiresAuth && !store.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
})
export default router
