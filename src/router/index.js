import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '@/pages/HomePage.vue'
import TextInputPage from '@/pages/TextInputPage.vue'
import VoiceInputPage from '@/pages/VoiceInputPage.vue'
import ImageInputPage from '@/pages/ImageInputPage.vue'
import LoginPage from '@/pages/LoginPage.vue'
import RegisterPage from '@/pages/RegisterPage.vue'
import ProfilePage from '@/pages/ProfilePage.vue'
import HistoryPage from '@/pages/HistoryPage.vue'
import { useTriageStore } from '@/store/triageStore'

const routes = [
  { path: '/', name: 'home', component: HomePage },
  { path: '/input/text', name: 'text', component: TextInputPage },
  { path: '/input/voice', name: 'voice', component: VoiceInputPage },
  { path: '/input/images', name: 'images', component: ImageInputPage },
  { path: '/history', name: 'history', component: HistoryPage, meta: { requiresAuth: true } },

  { path: '/login', name: 'login', component: LoginPage },
  { path: '/register', name: 'register', component: RegisterPage },
  { path: '/profile', name: 'profile', component: ProfilePage, meta: { requiresAuth: true } },
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to) => {
  const store = useTriageStore()
  if (to.meta.requiresAuth && !store.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
})

export default router
