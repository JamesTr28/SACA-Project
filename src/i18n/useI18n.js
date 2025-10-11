// src/i18n/useI18n.js
import { computed } from 'vue'
import messages from '@/i18n/messages'     // ✅ 统一默认导入（不带 .js）
import { useUiStore } from '@/store/uiStore'

export function useI18n() {
  const ui = useUiStore()

  const t = (path) => {
    const parts = String(path).split('.')
    const lang = messages[ui.locale] ? ui.locale : 'en'   // ✅ 兜底语言
    let cur = messages[lang] || messages.en

    for (const p of parts) {
      if (cur && Object.prototype.hasOwnProperty.call(cur, p)) {
        cur = cur[p]
      } else {
        // 找不到就回退 key，便于定位问题
        return path
      }
    }
    return cur
  }

  const tc = (path) => computed(() => t(path))
  return { t, tc, ui }
}
