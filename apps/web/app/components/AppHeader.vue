<script setup lang="ts">
import { Bookmark, Database, ScanLine, Sparkles, Wine } from '@lucide/vue'
import { isFeatureEnabled } from '#shared/utils/feature-flags'

const config = useRuntimeConfig()
const isAstroEnabled = computed(() => isFeatureEnabled(config.public.astroEnabled))
const isSommelierEnabled = computed(() => config.public.sommelierMode !== 'off')
</script>

<template>
  <header class="site-header">
    <div class="page-container site-header__inner">
      <NuxtLink
        class="brand"
        to="/"
        aria-label="Сканер российских вин — на главную"
      >
        <span class="brand__mark" aria-hidden="true">СВ</span>
        <span class="brand__text">
          <strong>Своё вино</strong>
          <small>сканер этикеток</small>
        </span>
      </NuxtLink>

      <nav class="site-nav" aria-label="Основная навигация">
        <NuxtLink class="site-nav__link" to="/" aria-label="Сканер">
          <ScanLine :size="19" aria-hidden="true" />
          <span>Сканер</span>
        </NuxtLink>
        <NuxtLink class="site-nav__link" to="/pairings" aria-label="Мои сочетания">
          <Bookmark :size="19" aria-hidden="true" />
          <span>Мои сочетания</span>
        </NuxtLink>
        <NuxtLink v-if="isSommelierEnabled" class="site-nav__link" to="/sommelier" aria-label="Цифровой сомелье">
          <Wine :size="19" aria-hidden="true" />
          <span>Сомелье</span>
        </NuxtLink>
        <NuxtLink v-if="isAstroEnabled" class="site-nav__link" to="/astro-sommelier" aria-label="Астро-сомелье">
          <Sparkles :size="19" aria-hidden="true" />
          <span>Астро-сомелье</span>
        </NuxtLink>
        <NuxtLink class="site-nav__link" to="/admin" aria-label="Каталог">
          <Database :size="19" aria-hidden="true" />
          <span>Каталог</span>
        </NuxtLink>
      </nav>
    </div>
  </header>
</template>
