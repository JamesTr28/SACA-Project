import { defineStore } from 'pinia'
import * as api from '@/services/api'

export const useTriageStore = defineStore('triage', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    user: JSON.parse(localStorage.getItem('user') || 'null'),

    // 主页交互数据
    textInput: '',
    structuredInput: { age: '', gender: '', topSymptoms: [], severity: 0 },
    audioBlob: null,

    // 推理与结果
    submitting: false,
    lastJobId: null,
    report: null,          // 结果报告对象
    logs: [],              // 可视化/调试信息
    error: null,
  }),
  getters: {
    isAuthenticated: (s) => !!s.token,
  },
  actions: {
    async login(email, password) {
      const { token, user } = await api.login(email, password)
      this.token = token
      this.user = user
      localStorage.setItem('token', token)
      localStorage.setItem('user', JSON.stringify(user))
    },
    async register(payload) {
      const { token, user } = await api.register(payload)
      this.token = token
      this.user = user
      localStorage.setItem('token', token)
      localStorage.setItem('user', JSON.stringify(user))
    },
    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    },
    async fetchProfile() {
      if (!this.token) return
      this.user = await api.getMe(this.token)
      localStorage.setItem('user', JSON.stringify(this.user))
    },

    // ---- 主页三种输入 ----
    setText(v){ this.textInput = v },
    setStructured(v){ this.structuredInput = { ...this.structuredInput, ...v } },
    setAudio(blob){ this.audioBlob = blob },

    // ---- 调用后端：根据输入提交并获取结果（保持主页统一提交口）----
    async submitAll() {
      try {
        this.error = null
        this.submitting = true
        this.logs = []

        const payload = {
          text: this.textInput?.trim() || null,
          structured: this.structuredInput,
        }

        // 分步命中你的 REST API；语音独立上传
        if (this.audioBlob) {
          const { jobId: audioJobId, note } = await api.uploadAudio(this.audioBlob, this.token)
          this.logs.push(`Audio uploaded: job=${audioJobId}` + (note ? ` (${note})` : ''))
        }
        const { jobId } = await api.submitSymptoms(payload, this.token)
        this.lastJobId = jobId
        this.logs.push(`Symptoms submitted: job=${jobId}`)

        // 轮询/一次性拉取报告（按你后端实际修改为轮询）
        const report = await api.fetchReport(jobId, this.token)
        this.report = report
        this.logs.push('Report ready')
      } catch (e) {
        this.error = e?.message || 'Submit failed'
      } finally {
        this.submitting = false
      }
    },
  },
})
