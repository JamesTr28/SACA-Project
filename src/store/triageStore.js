import { defineStore } from 'pinia'
import * as api from '@/services/api'

const LS_TOKEN='token', LS_USER='user', LS_PROFILE='profile', LS_HISTORY='history'

export const useTriageStore = defineStore('triage', {
  state: () => ({
    token: localStorage.getItem(LS_TOKEN) || null,
    user: JSON.parse(localStorage.getItem(LS_USER) || 'null'),

    // 资料（第二步）
    profile: JSON.parse(localStorage.getItem(LS_PROFILE) || 'null') || {
      gender: 1, age: '', conditions: '', allergies: '', medications: '',
    },

    // 第三步输入（向导中随时更新）
    textInput: '',
    audioBlob: null,
    selectedSymptoms: [],

    // 自评（第三步的最后一小节）
    selfAssessment: { severity: null, feeling: null },

    // 提交&结果
    submitting: false,
    error: null,
    lastReport: null,

    // 历史
    history: JSON.parse(localStorage.getItem(LS_HISTORY) || '[]'),
  }),
  getters: { isAuthenticated: (s) => !!s.token },
  actions: {
    // Auth
    async login(email, password){
      const { token, user } = await api.login(email, password)
      this.token = token; this.user = user
      localStorage.setItem(LS_TOKEN, token)
      localStorage.setItem(LS_USER, JSON.stringify(user))
    },
    async register(payload){
      const { token, user } = await api.register(payload)
      this.token = token; this.user = user
      localStorage.setItem(LS_TOKEN, token)
      localStorage.setItem(LS_USER, JSON.stringify(user))
    },
    logout(){ this.token=null; this.user=null; localStorage.removeItem(LS_TOKEN); localStorage.removeItem(LS_USER) },

    // Profile
    updateProfile(patch){
      this.profile = { ...this.profile, ...patch }
      localStorage.setItem(LS_PROFILE, JSON.stringify(this.profile))
    },

    // Inputs
    setText(v){ this.textInput = v },
    setAudio(b){ this.audioBlob = b },
    setSelectedSymptoms(v){ this.selectedSymptoms = v || [] },
    removeSymptom(key){ this.selectedSymptoms = (this.selectedSymptoms||[]).filter(k=>k!==key) },
    addSymptom(symptom) {
     if (!this.selectedSymptoms.includes(symptom)) {
    this.selectedSymptoms.push(symptom)
    }
    },
    // ---- 最终提交----
    async submitTriageFinal() {
      try{
        this.error = null
        this.submitting = true

        if (this.audioBlob) {
          await api.uploadAudio(this.audioBlob, this.token).catch(()=>{})
        }

        const payload = {
          text: this.textInput || null,
          symptoms: this.selectedSymptoms || [],
          profile: this.profile,
          selfAssessment: {
            severity: this.selfAssessment.severity,
            feeling: this.selfAssessment.feeling,
          },
        }

        const { jobId, disease } = await api.submitSymptoms(payload, this.token)
        const report = await api.fetchReport(jobId, disease)
        this.lastReport = report

        const item = { id: jobId, at: new Date().toISOString(), payload, report }
        this.history.unshift(item)
        localStorage.setItem(LS_HISTORY, JSON.stringify(this.history.slice(0, 300)))

        return report
      }catch(e){
        this.error = e?.message || 'Submit failed'
        throw e
      }finally{
        this.submitting = false
      }
    },
  },
})
