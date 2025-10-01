<template>
  <div class="profile">
    <h2>Profile</h2>
    <div class="card">
      <div class="row"><label>Name</label><span>{{ user?.name }}</span></div>
      <div class="row"><label>Email</label><span>{{ user?.email }}</span></div>
      <div class="row"><label>User ID</label><span>{{ user?.id }}</span></div>
    </div>

    <h3>Consent & data</h3>
    <p class="muted">Your audio/text may be used to improve the models if you consent via backend settings.</p>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useTriageStore } from '@/store/triageStore'
const store = useTriageStore()
const { user } = storeToRefs(store)
onMounted(()=> store.fetchProfile())
</script>

<style scoped>
.profile{max-width:720px;margin:0 auto}
.card{border:1px solid #eee;border-radius:12px;padding:14px;margin-bottom:16px}
.row{display:flex;gap:12px;align-items:center;margin:6px 0}
.row label{width:120px;color:#666}
.muted{color:#777}
</style>
