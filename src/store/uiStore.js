import { defineStore } from 'pinia'

export const useUiStore = defineStore('ui', {
  state: () => ({
    theme: localStorage.getItem('theme') || 'light', // 'light' | 'dark'
    locale: localStorage.getItem('locale') || 'en',  // 'en' | 'wbp'
  }),
  actions: {
    setTheme(t) {
      this.theme = t
      localStorage.setItem('theme', t)
      // 将主题类挂到 <html>，便于全局样式控制
      const el = document.documentElement
      el.classList.remove('light', 'dark')
      el.classList.add(t)
    },
    toggleTheme() { this.setTheme(this.theme === 'dark' ? 'light' : 'dark') },
    setLocale(l) {
      this.locale = l
      localStorage.setItem('locale', l)
    },
    toggleLocale() { this.setLocale(this.locale === 'en' ? 'wbp' : 'en') },
  },
})
