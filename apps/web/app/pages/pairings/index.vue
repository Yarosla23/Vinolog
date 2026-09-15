<script setup lang="ts">
import { Bookmark, ChevronRight, ScanLine } from '@lucide/vue'

const { pairings, isLoaded } = useSavedPairings()
</script>

<template>
  <div class="page-container secondary-page">
    <header class="page-heading">
      <p class="eyebrow">Сохранено в этом браузере</p>
      <h1>Мои сочетания</h1>
      <p>Блюда и вина, к которым можно вернуться перед ужином.</p>
    </header>

    <div v-if="!isLoaded" class="saved-empty" role="status">Загружаем сохранённые сочетания…</div>

    <section v-else-if="pairings.length" class="saved-list" aria-label="Сохранённые сочетания">
      <article v-for="pairing in pairings" :key="pairing.id" class="saved-card">
        <Bookmark :size="23" aria-hidden="true" />
        <div>
          <p class="saved-card__dish">{{ pairing.dish }}</p>
          <h2>{{ pairing.wine.name }}</h2>
          <p>{{ pairing.wine.producer }}</p>
          <span>{{ pairing.verdict }}</span>
        </div>
        <ChevronRight :size="20" aria-hidden="true" />
      </article>
    </section>

    <section v-else class="saved-empty">
      <Bookmark :size="34" aria-hidden="true" />
      <h2>Пока ничего не сохранено</h2>
      <p>Сначала найдите вино, затем подберите его к блюду.</p>
      <NuxtLink class="button button--primary" to="/">
        <ScanLine :size="19" aria-hidden="true" />
        Открыть сканер
      </NuxtLink>
    </section>
  </div>
</template>
