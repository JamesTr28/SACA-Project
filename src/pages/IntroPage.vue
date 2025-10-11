<template>
  <section class="wrap">
    <h2>{{ t('intro.title') }}</h2>
    <p>{{ t('intro.welcome') }}</p>
    <p>{{ t('intro.disclaimer') }}</p>
    <ol class="steps">
      <li>{{ t('intro.step1') }}</li>
      <li>{{ t('intro.step2') }}</li>
      <li>{{ t('intro.step3') }}</li>
      <li>{{ t('intro.step4') }}</li>
    </ol>
    <p class="muted">{{ t('intro.tip') }}</p>

    <button class="btn primary" @click="$router.push('/info')">{{ t('intro.start') }}</button>
  </section>
</template>

<script setup>
import { useI18n } from '@/i18n/useI18n'

const { t } = useI18n()
</script>

<style scoped>
.wrap{max-width:820px;margin:0 auto}
.steps{line-height:1.8}
.muted{color:var(--muted);margin:12px 0}
.btn.primary{background:var(--btn-bg);color:var(--btn-fg);border:none;padding:10px 14px;border-radius:10px}
</style>