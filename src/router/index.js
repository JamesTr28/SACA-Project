// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'

// Pages
import TriagePage     from '@/pages/TriagePage.vue'
import ConfirmPage    from '@/pages/ConfirmPage.vue'
import ProfilePage    from '@/pages/ProfilePage.vue'
import LoginPage      from '@/pages/LoginPage.vue'
import RegisterPage   from '@/pages/RegisterPage.vue'
import PredictionPage from '@/pages/PredictionPage.vue' // ← 文件名要和你的实际文件一致

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/triage' },

    { path: '/triage',  name: 'triage',  component: TriagePage },
    { path: '/confirm', name: 'confirm', component: ConfirmPage },

    // 结果页（如果暂时不用，可以注释掉下面这一行和上面的 import）
    { path: '/predict', name: 'predict', component: PredictionPage },

    { path: '/profile', name: 'profile', component: ProfilePage },

    { path: '/login',    name: 'login',    component: LoginPage },
    { path: '/register', name: 'register', component: RegisterPage },

    // 兜底
    { path: '/:pathMatch(.*)*', redirect: '/triage' },
  ],
})

export default router
