import { defineStore } from 'pinia'
import { submitSymptoms } from '@/services/api'

const LS_KEY = 'triage_history_v1'

export const useTriageStore = defineStore('triage', {
  state: () => ({
    // …你已有的状态…
    selectedSymptoms: [],
    textInput: '',
    audioText: '',

    lastReport: null,
    history: JSON.parse(localStorage.getItem(LS_KEY) || '[]'), // [{id,time,input,report}]
    isAuthenticated: false,
    user: null,
  }),

  actions: {
    setSelectedSymptoms(arr){ this.selectedSymptoms = Array.isArray(arr) ? arr : [] },
    addSymptoms(arr){ this.selectedSymptoms = Array.from(new Set([ ...this.selectedSymptoms, ...arr ])) },
    setText(t){ this.textInput = t || '' },
    setAudioText(t){ this.audioText = t || '' },

    _pushHistory(entry){
      this.history.unshift(entry)
      localStorage.setItem(LS_KEY, JSON.stringify(this.history.slice(0,100)))
    },

    async submitTriageFinal(){
      // 整理 payload
      const payload = {
        symptoms: this.selectedSymptoms,
        text: this.textInput,
        transcript: this.audioText,
      }

      const report = await submitSymptoms(payload) // 后端 /predict
      this.lastReport = report

      // 写入历史
      this._pushHistory({
        id: String(Date.now()),
        time: new Date().toISOString(),
        input: { ...payload },
        report,
      })

      return report
    },

    // 简易认证（如果你有就忽略）
    loginSuccess(user){
      this.isAuthenticated = true
      this.user = user
    },
    logout(){
      this.isAuthenticated = false
      this.user = null
    },
  },
})
