<template>
    <h3>Text</h3>
      <!-- Translate button -->
      <textarea
        v-model="text"
        rows="6"
        placeholder="You can enter additional descriptions (optional)"
      ></textarea>

      <button
        class="btn outline"
        :disabled="transLoading || !text.trim()"
        @click="translateAndFill"
        title="Translate Warlpiri → English and replace the textarea"
      >
        {{ transLoading ? "Translating..." : "TRANSLATE" }}
      </button>
</template>
<script setup>

import { ref } from 'vue'
import { translate } from './../services/api'
const transLoading = ref(false);
const transError = ref(null);
async function translateAndFill(text) {
  console.log(text.value);
  transError.value = null;
  if (!text.value.trim()) return;
  console.log("Translating...");
  transLoading.value = true;
  try {
    const r = await translate(text.value, 6, 160, 1.0); // beams, max_len, len_pen
    // Replace the textarea content with the translation
    console.log("Translation result:", r);
    store.setText(r.translation);
  } catch (e) {
    transError.value = e?.message || String(e);
  } finally {
    transLoading.value = false;
  }
}

</script>
<script>
export default{
  name: 'TranslateButton'
}
</script>