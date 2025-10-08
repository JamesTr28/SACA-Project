<template>
  <div class="cselect" @keydown.escape="open=false" ref="root">
    <button type="button" class="trigger" @click="open=!open">
      <span>{{ currentLabel }}</span>
      <svg viewBox="0 0 20 20" width="16" height="16" aria-hidden="true"><path d="M5 7l5 6 5-6H5z" fill="currentColor"/></svg>
    </button>

    <ul v-if="open" class="menu">
      <li v-for="opt in options" :key="opt.value"
          :class="{on: modelValue===opt.value}"
          @click="choose(opt.value)">
        {{ opt.label }}
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
const props = defineProps({
  modelValue: [String, Number, null],
  options: { type: Array, default: () => [] }, // [{label,value}]
  placeholder: { type: String, default: 'Select...' }
})
const emit = defineEmits(['update:modelValue'])
const open = ref(false)
const root = ref(null)

const currentLabel = computed(()=>{
  const f = props.options.find(o => o.value === props.modelValue)
  return f ? f.label : props.placeholder
})

function choose(v){ emit('update:modelValue', v); open.value=false }
function onDoc(e){ if (!root.value?.contains(e.target)) open.value=false }

onMounted(()=> document.addEventListener('click', onDoc))
onBeforeUnmount(()=> document.removeEventListener('click', onDoc))
</script>

<style scoped>
.cselect{ position:relative; width:100% }
.trigger{
  width:100%; display:flex; justify-content:space-between; align-items:center;
  padding:10px 12px; border-radius:10px;
  background: rgba(255, 255, 255, 0.293); color:#0b3320;
  border:2px solid rgba(0,0,0,.18);
}
.trigger:focus{ outline:none; border-color:#2e7d32; box-shadow:0 0 0 3px color-mix(in srgb, #2e7d32 22%, transparent) }
.menu{
  position:absolute; left:0; right:0; margin-top:6px; z-index:20;
  background:#e8f7e889; border:2px solid #2e7d32; border-radius:12px; padding:6px;
  max-height:240px; overflow:auto; box-shadow:0 10px 24px rgba(0,0,0,.08);
}
.menu li{
  list-style:none; padding:10px 12px; border-radius:8px; cursor:pointer; color:#0b3320;
}
.menu li:hover{ background:#5ab85fa5 }
.menu li.on{ background:#5ab85f; color:#ffffffd3 }
</style>
