<template>
  <div class="page-wrapper">
    <Chatbot />
  </div>
</template>

<script setup>
import Chatbot from '@/components/Chatbot.vue';
</script>

<style scoped>
.page-wrapper {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding-top: 40px;
  min-height: 80vh;
}
</style>