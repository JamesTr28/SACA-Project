<template>
  <div class="sev">
    <label class="lab">
      Severity (self-rated)
      <span class="val">{{ modelValue }}</span>
    </label>
    <input
      :disabled="disabled"
      type="range" min="0" max="5" step="1"
      :value="modelValue"
      @input="onInput"
    />
    <div class="ticks">
      <span v-for="i in 6" :key="i-1">{{ i-1 }}</span>
    </div>
    <small class="hint">0 = none, 5 = extreme</small>
  </div>
</template>

<script setup>
const props = defineProps({
  modelValue: { type: Number, default: 0 },
  disabled: { type: Boolean, default: false },
})
const emit = defineEmits(['update:modelValue'])
function onInput(e){ emit('update:modelValue', Number(e.target.value)) }
</script>

<style scoped>
.sev{display:flex;flex-direction:column;gap:6px}
.lab{display:flex;justify-content:space-between;align-items:center}
.val{font-weight:600}
input[type="range"]{width:100%}
.ticks{display:flex;justify-content:space-between;color:#777;font-size:12px}
.hint{color:#777}
</style>
