// src/i18n/useI18n.js
import { computed } from 'vue'
import { messages } from '@/i18n/messages.js'   // ← 改成别名路径，带 .js
import { useUiStore } from '@/store/uiStore'

export function useI18n() {
  const ui = useUiStore()

  const t = (path) => {
    const parts = String(path).split('.')
    let cur = messages[ui.locale] || messages.en
    for (const p of parts) {
      if (cur && Object.prototype.hasOwnProperty.call(cur, p)) {
        cur = cur[p]
      } else {
        return path // 找不到就回退 key
      }
    }
    return cur
  }

  const tc = (path) => computed(() => t(path))
  return { t, tc, ui }
}
