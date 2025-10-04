<template>
  <section class="home">
    <h2>Select input method</h2>
    <div class="tiles">
      <button class="tile" @click="$router.push('/input/text')">
        Text input
        <small>Type/paste symptoms description</small>
      </button>
      <button class="tile" @click="$router.push('/input/voice')">
        Voice input
        <small>Record and upload automatically</small>
      </button>
      <button class="tile" @click="$router.push('/input/images')">
        Image input
        <small>Click on the symptom image to select multiple</small>
      </button>
    </div>
  </section>
</template>

<script setup>
</script>

<style scoped>
.home{max-width:900px;margin:0 auto}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px;margin-top:16px}
.tile{padding:20px;border:1px solid var(--border);border-radius:16px;background:var(--card);text-align:left;font-size:18px;cursor:pointer}
.tile small{display:block;color:var(--muted);margin-top:8px}
.tile:hover{transform:translateY(-2px)}
</style>
