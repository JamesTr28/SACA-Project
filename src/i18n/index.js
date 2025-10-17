// src/i18n/index.js
import { ref } from 'vue'
import messages from './messages'

const LANG_KEY = 'locale'
const lang = ref(localStorage.getItem(LANG_KEY) || 'en')

function setLang(next) {
  lang.value = next || 'en'
  localStorage.setItem(LANG_KEY, lang.value)
}

// 简单路径取值：t('chat.greet')
function t(path) {
  const dict = messages[lang.value] || messages.en
  return path.split('.').reduce((acc, k) => (acc && acc[k] != null ? acc[k] : null), dict) ?? path
}

export function useI18n() {
  return { t, lang, setLang }
}
