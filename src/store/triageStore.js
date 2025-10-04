import { defineStore } from 'pinia'
import * as api from '@/services/api'

const LS_TOKEN = 'token'
const LS_USER  = 'user'
const LS_PROFILE = 'profile'
const LS_HISTORY = 'history'

export const useTriageStore = defineStore('triage', {
  state: () => ({
    token: localStorage.getItem(LS_TOKEN) || null,
    user: JSON.parse(localStorage.getItem(LS_USER) || 'null'),

    // 输入数据
    textInput: '',
    selectedSymptoms: [],       // 图片多选得到的症状数组（字符串）
    audioBlob: null,

    // 用户档案（会与每次请求一起发给后端）
    profile: JSON.parse(localStorage.getItem(LS_PROFILE) || 'null') || {
      gender: 1,                // 1 男, 0 女
      age: '',
      conditions: '',           // 既往病史
      allergies: '',            // 过敏史
      medications: '',          // 在用药物
    },

    // 状态 & 结果
    submitting: false,
    error: null,
    lastReport: null,

    // 历史记录（列表）
    history: JSON.parse(localStorage.getItem(LS_HISTORY) || '[]'),
  }),
  getters: {
    isAuthenticated: (s) => !!s.token,
  },
  actions: {
    // ------- Auth -------
    async login(email, password) {
      const { token, user } = await api.login(email, password)
      this.token = token; this.user = user
      localStorage.setItem(LS_TOKEN, token)
      localStorage.setItem(LS_USER, JSON.stringify(user))
    },
    async register(payload) {
      const { token, user } = await api.register(payload)
      this.token = token; this.user = user
      localStorage.setItem(LS_TOKEN, token)
      localStorage.setItem(LS_USER, JSON.stringify(user))
    },
    logout() {
      this.token = null; this.user = null
      localStorage.removeItem(LS_TOKEN)
      localStorage.removeItem(LS_USER)
    },

    // ------- Profile -------
    updateProfile(patch) {
      this.profile = { ...this.profile, ...patch }
      localStorage.setItem(LS_PROFILE, JSON.stringify(this.profile))
    },

    // ------- Inputs -------
    setText(v){ this.textInput = v }
    ,
    setSelectedSymptoms(list){ this.selectedSymptoms = list || [] }
    ,
    setAudio(blob){ this.audioBlob = blob },

    // ------- Submit to backend -------
    async submitFromText() {
      return this._submit({ text: this.textInput })
    },
    async submitFromImages() {
      return this._submit({ symptoms: this.selectedSymptoms })
    },
    async submitFromVoice() {
      // 语音先传；报告在 _submit 拉取
      if (this.audioBlob) {
        await api.uploadAudio(this.audioBlob, this.token).catch(()=>{})
      }
      return this._submit({ via: 'voice' })
    },

    async _submit(payload) {
      try {
        this.error = null
        this.submitting = true

        const full = { ...payload, profile: this.profile }
        const { jobId } = await api.submitSymptoms(full, this.token)
        const report = await api.fetchReport(jobId, this.token)

        this.lastReport = report
        // 写入历史
        const item = { id: jobId, at: new Date().toISOString(), input: payload, profile: this.profile, report }
        this.history.unshift(item)
        localStorage.setItem(LS_HISTORY, JSON.stringify(this.history.slice(0, 200))) // 最多存 200 条
        return report
      } catch (e) {
        this.error = e?.message || 'Submit failed'
        throw e
      } finally {
        this.submitting = false
      }
    },
  },
})
