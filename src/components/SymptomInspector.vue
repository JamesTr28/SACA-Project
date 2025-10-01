<template>
  <div class="insp card">
    <div class="head">
      <h3>Symptoms (structured)</h3>
      <div class="actions">
        <button class="btn small outline" @click="clearAll" :disabled="!local.length">Clear</button>
        <button class="btn small" @click="applySuggestions" :disabled="!suggestions?.length">Add suggestions</button>
      </div>
    </div>

    <div class="adder">
      <input v-model="draft" placeholder="Type a symptom (e.g., fever) and press Add" @keyup.enter="add" />
      <button class="btn" @click="add">Add</button>
    </div>

    <div class="chips">
      <span v-for="(s,idx) in local" :key="s+idx" class="chip">
        {{ s }}
        <button class="x" @click="remove(idx)" aria-label="remove">×</button>
      </span>
      <span v-if="!local.length" class="muted">No symptoms yet.</span>
    </div>

    <details v-if="suggestions?.length" class="sugg">
      <summary>Suggestions from report ({{ suggestions.length }})</summary>
      <div class="slist">
        <button
          v-for="s in suggestions"
          :key="s.name"
          class="sbtn"
          :title="'weight '+(s.weight ?? '-')"
          @click="quickAdd(s.name)"
        >
          {{ s.name }} <small>({{ pct(s.weight) }})</small>
        </button>
      </div>
    </details>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  modelValue: { type: Array, default: () => [] }, // ['fever','cough']
  // 传入报告里的 extractedSymptoms 以便建议
  extracted: { type: Array, default: () => [] },  // [{name, weight}]
})

const emit = defineEmits(['update:modelValue'])
const draft = ref('')
const local = ref([...props.modelValue])

watch(() => props.modelValue, (v)=> { local.value = [...v] })

const suggestions = computed(() => {
  if (!props.extracted?.length) return []
  // 去重：过滤掉已在列表中的
  const set = new Set(local.value.map(s => s.toLowerCase()))
  return props.extracted.filter(s => !set.has(s.name?.toLowerCase()))
})

function add(){
  const t = (draft.value || '').trim()
  if (!t) return
  if (!local.value.map(s=>s.toLowerCase()).includes(t.toLowerCase())) {
    local.value.push(t)
    emit('update:modelValue', [...local.value])
  }
  draft.value = ''
}
function quickAdd(name){
  draft.value = name
  add()
}
function remove(idx){
  local.value.splice(idx,1)
  emit('update:modelValue', [...local.value])
}
function clearAll(){
  local.value = []
  emit('update:modelValue', [])
}
function pct(v){ return v==null ? '-' : (v*100).toFixed(0)+'%' }
</script>

<style scoped>
.card{border:1px solid #eee;border-radius:12px;padding:14px;background:#fff}
.head{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px}
.actions{display:flex;gap:8px}
.btn{padding:6px 12px;border-radius:10px;background:#111;color:#fff}
.btn.small{padding:6px 10px}
.btn.small.outline,.btn.outline{background:#fff;color:#111;border:1px solid #111}
.adder{display:flex;gap:8px;margin-bottom:10px}
.adder input{flex:1;padding:8px;border:1px solid #ddd;border-radius:8px}
.chips{display:flex;gap:8px;flex-wrap:wrap;min-height:32px}
.chip{display:inline-flex;align-items:center;gap:6px;border:1px solid #ddd;border-radius:999px;padding:4px 8px}
.chip .x{background:none;border:none;cursor:pointer;font-size:14px;line-height:1}
.muted{color:#777}
.sugg{margin-top:8px}
.slist{display:flex;gap:8px;flex-wrap:wrap;margin-top:6px}
.sbtn{border:1px dashed #aaa;background:#fafafa;border-radius:999px;padding:4px 8px;cursor:pointer}
.sbtn small{color:#777}
</style>
