<template>
  <div class="picker">
    <div
      v-for="item in items"
      :key="item.key"
      class="card"
      :class="{ active: selectedSet.has(item.key) }"
      @click="toggle(item.key)"
      role="button"
      tabindex="0"
    >
      <img :src="item.src" :alt="item.label" />
      <div class="label">
        <strong>{{ item.label }}</strong>
        <small class="muted">{{ item.note }}</small>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: { type: Array, default: () => [] }, 
})
const emit = defineEmits(['update:modelValue'])

// 使用真实图片路径
const items = [
  { key: 'abdominal_pain', label: 'Abdominal pain', note: 'placeholder', src: new URL('@/assets/abdominal-pain.png', import.meta.url).href },
  { key: 'fever_high', label: 'High fever', note: 'placeholder', src: new URL('@/assets/fever_high.png', import.meta.url).href },
  { key: 'cough', label: 'Cough', note: 'placeholder', src: new URL('@/assets/cough.png', import.meta.url).href },
  { key: 'sore_throat', label: 'Sore throat', note: 'placeholder', src: new URL('@/assets/sore-throat.png', import.meta.url).href },
  { key: 'headache', label: 'Headache', note: 'placeholder', src: new URL('@/assets/headache.png', import.meta.url).href },
  { key: 'nausea', label: 'Nausea', note: 'placeholder', src: new URL('@/assets/nausea.png', import.meta.url).href },
  { key: 'vomit', label: 'Vomit', note: 'placeholder', src: new URL('@/assets/vomit.png', import.meta.url).href },
  { key: 'diarrhea', label: 'Diarrhea', note: 'placeholder', src: new URL('@/assets/diarrhea.png', import.meta.url).href },
  { key: 'chest_pain', label: 'Chest pain', note: 'placeholder', src: new URL('@/assets/chest-pain.png', import.meta.url).href },
  { key: 'short_breath', label: 'Shortness of breath', note: 'placeholder', src: new URL('@/assets/short_breath.png', import.meta.url).href },
  { key: 'rash', label: 'Rash', note: 'placeholder', src: new URL('@/assets/rash.png', import.meta.url).href },
  { key: 'fatigue', label: 'Fatigue', note: 'placeholder', src: new URL('@/assets/fatigue.png', import.meta.url).href },
]

const selectedSet = computed(() => new Set(props.modelValue))
function toggle(key){
  const set = new Set(selectedSet.value)
  if (set.has(key)) set.delete(key); else set.add(key)
  emit('update:modelValue', Array.from(set))
}
</script>

<style scoped>
.picker{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:12px}
.card{border:1px solid var(--border);border-radius:12px;background:var(--card);cursor:pointer;overflow:hidden;display:flex;flex-direction:column}
.card img{width:100%;height:120px;object-fit:cover}
.card .label{padding:8px}
.card.active{outline:2px solid #2563eb}
.muted{color:var(--muted)}
</style>
