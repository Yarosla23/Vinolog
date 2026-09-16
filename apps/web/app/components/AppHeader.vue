<script setup lang="ts">
import { Bookmark, Database, ScanLine } from '@lucide/vue'
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
        <NuxtLink class="site-nav__link" to="/">
          <ScanLine :size="19" aria-hidden="true" />
          <span>Сканер</span>
        </NuxtLink>
        <NuxtLink class="site-nav__link" to="/pairings">
          <Bookmark :size="19" aria-hidden="true" />
          <span>Мои сочетания</span>
        </NuxtLink>
        <NuxtLink class="site-nav__link" to="/admin">
          <Database :size="19" aria-hidden="true" />
          <span>Каталог</span>
        </NuxtLink>
      </nav>
    </div>
  </header>
</template>
