const BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

async function req(path, { method='GET', token, json, form } = {}) {
  const headers = {}
  if (token) headers['Authorization'] = `Bearer ${token}`

  let body
  if (json) {
    headers['Content-Type'] = 'application/json'
    body = JSON.stringify(json)
  } else if (form) {
    body = form
  }

  const res = await fetch(`${BASE}${path}`, { method, headers, body })
  if (!res.ok) {
    const txt = await res.text().catch(()=>'')
    throw new Error(`HTTP ${res.status} ${txt}`)
  }
  // 某些接口可能204
  try { return await res.json() } catch { return {} }
}

/** ---------- Auth ---------- */
export async function login(email, password) {
  // 真实接口：return await req('/auth/login', { method:'POST', json:{email,password} })
  // 占位：本地伪登录
  return new Promise((r) => setTimeout(() => r({
    token: 'demo-token',
    user: { id: 'u1', email, name: email.split('@')[0] }
  }), 400))
}

export async function register({ name, email, password }) {
  // return await req('/auth/register', { method:'POST', json:{ name, email, password } })
  return new Promise((r) => setTimeout(() => r({
    token: 'demo-token',
    user: { id: 'u2', email, name }
  }), 500))
}

export async function getMe(token) {
  // return await req('/auth/me', { token })
  return { id: 'u1', email: 'demo@demo.com', name: 'Demo User' }
}

/** ---------- Triage Submissions ---------- */
export async function submitSymptoms(payload, token) {
  // return await req('/triage/submit', { method:'POST', token, json: payload })
  return new Promise((r)=> setTimeout(()=> r({ jobId: 'job_' + Date.now() }), 600))
}

export async function uploadAudio(blob, token) {
  const form = new FormData()
  form.append('file', blob, 'speech.wav')
  // return await req('/triage/audio', { method:'POST', token, form })
  return new Promise((r)=> setTimeout(()=> r({ jobId: 'audio_' + Date.now(), note:'mocked' }), 500))
}

export async function fetchReport(jobId, token) {
  // return await req(`/triage/report/${jobId}`, { token })
  // 占位报告结构，和你的 ResultsPanel 对齐
  return new Promise((r)=> setTimeout(()=> r({
    jobId,
    patient: { age: 31, gender: 'F' },
    extractedSymptoms: [
      { name: 'fever', weight: 0.86 },
      { name: 'cough', weight: 0.63 },
    ],
    modelVotes: [
      { model: 'LogReg', severity: 2, confidence: 0.71 },
      { model: 'RandomForest', severity: 3, confidence: 0.64 },
    ],
    finalDecision: { severity: 3, rationale: 'Consistent with RF + high temp.' },
    createdAt: new Date().toISOString()
  }), 800))
}

import axios from 'axios'

// If you added the Vite proxy, baseURL can be '' (same origin)
const api = axios.create({ baseURL: import.meta.env.VITE_API_URL || '' })

export async function translateText({ text, beams = 6, max_len = 160, len_pen = 1.0 }) {
  const { data } = await api.post('/api/translate', { text, beams, max_len, len_pen })
  return data.translation
}
