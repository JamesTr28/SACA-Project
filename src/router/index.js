import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '@/pages/HomePage.vue'
import LoginPage from '@/pages/LoginPage.vue'
import RegisterPage from '@/pages/RegisterPage.vue'
import ProfilePage from '@/pages/ProfilePage.vue'
import { useTriageStore } from '@/store/triageStore'

const routes = [
  { path: '/', name: 'home', component: HomePage },
  { path: '/login', name: 'login', component: LoginPage },
  { path: '/register', name: 'register', component: RegisterPage },
  { path: '/profile', name: 'profile', component: ProfilePage, meta: { requiresAuth: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const store = useTriageStore()
  if (to.meta.requiresAuth && !store.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
})

export default router
