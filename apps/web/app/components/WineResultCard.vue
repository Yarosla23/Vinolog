<script setup lang="ts">
import type { ScanResponse } from '@vinolog/contracts'
import { ArrowRight, CircleAlert, Grape, MapPin, RotateCcw, ThermometerSun, Utensils } from '@lucide/vue'

const props = defineProps<{
  result: ScanResponse
}>()

const emit = defineEmits<{
  resetRequested: []
}>()

const pairingQuery = computed(() => ({
  slug: props.result.wine?.slug,
  name: props.result.wine?.name,
  producer: props.result.wine?.producer,
}))
</script>

<template>
  <section class="result-section" aria-live="polite">
    <div v-if="result.isMock" class="demo-banner">
      Демонстрационные данные — настоящее CV-распознавание ещё не подключено
    </div>

    <article v-if="result.status === 'matched' && result.wine" class="wine-card">
      <div class="wine-card__visual" aria-hidden="true">
        <span class="wine-card__bottle">
          <span>СВ</span>
        </span>
      </div>

      <div class="wine-card__content">
        <p class="eyebrow">Совпадение найдено</p>
        <p class="wine-card__producer">{{ result.wine.producer }}</p>
        <h2>{{ result.wine.name }}</h2>
        <p v-if="result.wine.year" class="wine-card__year">{{ result.wine.year }}</p>
        <p v-if="result.wine.description" class="wine-card__description">
          {{ result.wine.description }}
        </p>

        <dl class="wine-facts">
          <div v-if="result.wine.region">
            <dt><MapPin :size="17" aria-hidden="true" /> Регион</dt>
            <dd>{{ result.wine.region }}</dd>
          </div>
          <div v-if="result.wine.grapeVarieties.length">
            <dt><Grape :size="17" aria-hidden="true" /> Сорта</dt>
            <dd>{{ result.wine.grapeVarieties.join(', ') }}</dd>
          </div>
          <div v-if="result.wine.servingTemperature">
            <dt><ThermometerSun :size="17" aria-hidden="true" /> Подача</dt>
            <dd>{{ result.wine.servingTemperature }}</dd>
          </div>
        </dl>

        <div class="wine-card__actions">
          <NuxtLink class="button button--primary" :to="{ path: '/pairings/new', query: pairingQuery }">
            <Utensils :size="19" aria-hidden="true" />
            Подобрать к ужину
            <ArrowRight :size="18" aria-hidden="true" />
          </NuxtLink>
          <button class="button button--quiet" type="button" @click="emit('resetRequested')">
            <RotateCcw :size="18" aria-hidden="true" />
            Сканировать ещё
          </button>
        </div>
      </div>
    </article>

    <article v-else class="result-notice">
      <CircleAlert :size="28" aria-hidden="true" />
      <div>
        <p class="eyebrow">
          {{ result.status === 'uncertain' ? 'Нужно уточнить' : 'В каталоге не найдено' }}
        </p>
        <h2>
          {{ result.status === 'uncertain' ? 'Этикетка видна не полностью' : 'Мы не можем подтвердить совпадение' }}
        </h2>
        <p>{{ result.guidance || 'Попробуйте снять этикетку ближе и без бликов.' }}</p>
        <button class="button button--primary" type="button" @click="emit('resetRequested')">
          <RotateCcw :size="18" aria-hidden="true" />
          Сделать другое фото
        </button>
      </div>
    </article>
  </section>
</template>
