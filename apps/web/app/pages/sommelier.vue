<script setup lang="ts">
import { MessageCircle, RefreshCw, Send, ShieldCheck, Trash2, Wine } from '@lucide/vue'

definePageMeta({ middleware: 'sommelier-enabled' })

const config = useRuntimeConfig()
const { clear, errorMessage, isSubmitting, messages, retry, send } = useSommelierChat()
const draft = ref('')
const conversationEnd = useTemplateRef<HTMLElement>('conversationEnd')
const suggestions = [
  'Подбери вино к запечённой рыбе',
  'Что выбрать для праздничного аперитива?',
  'Нужно насыщенное красное к мясу',
]
const isMock = computed(() => config.public.sommelierMode === 'mock')

watch(() => messages.value.length, async () => {
  await nextTick()
  const behavior = window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth'
  conversationEnd.value?.scrollIntoView({ behavior, block: 'nearest' })
})

async function handleSubmit() {
  const content = draft.value
  if (!content.trim()) return
  draft.value = ''
  await send(content)
}

function handleSuggestion(suggestion: string) {
  if (!isSubmitting.value) void send(suggestion)
}
</script>

<template>
  <div class="page-container sommelier-page">
    <aside class="sommelier-intro">
      <p class="eyebrow">Подбор из каталога</p>
      <h1>Цифровой сомелье</h1>
      <p>Вино к блюду, событию и вашему вкусу — только из российского каталога.</p>

      <div class="sommelier-trust">
        <ShieldCheck :size="22" aria-hidden="true" />
        <p>Рекомендации привязаны к карточкам каталога. Медицинских советов здесь нет.</p>
      </div>

      <div class="sommelier-suggestions" aria-label="Быстрые темы">
        <button
          v-for="suggestion in suggestions"
          :key="suggestion"
          type="button"
          :disabled="isSubmitting"
          @click="handleSuggestion(suggestion)"
        >
          {{ suggestion }}
        </button>
      </div>
    </aside>

    <section class="sommelier-chat" aria-labelledby="sommelier-chat-title">
      <header class="sommelier-chat__header">
        <div>
          <MessageCircle :size="22" aria-hidden="true" />
          <h2 id="sommelier-chat-title">Диалог</h2>
        </div>
        <button
          class="icon-button"
          type="button"
          aria-label="Очистить диалог"
          title="Очистить диалог"
          :disabled="!messages.length || isSubmitting"
          @click="clear"
        >
          <Trash2 :size="19" aria-hidden="true" />
        </button>
      </header>

      <p v-if="isMock" class="sommelier-demo-note">
        Демо-режим: ответы воспроизводятся без обращения к AI и живому каталогу.
      </p>

      <div class="sommelier-messages" aria-live="polite" aria-relevant="additions">
        <div v-if="!messages.length" class="sommelier-empty">
          <Wine :size="38" aria-hidden="true" />
          <h2>С чего начнём?</h2>
          <p>Назовите блюдо, повод или желаемый стиль вина.</p>
        </div>

        <article
          v-for="message in messages"
          :key="message.id"
          class="sommelier-message"
          :class="`sommelier-message--${message.role}`"
        >
          <p class="sommelier-message__label">{{ message.role === 'user' ? 'Вы' : 'Сомелье' }}</p>
          <p class="sommelier-message__bubble" :class="{ 'sommelier-message__bubble--blocked': message.status === 'blocked' }">
            {{ message.content }}
          </p>
          <div v-if="message.recommendations.length" class="sommelier-recommendations">
            <SommelierWineCard
              v-for="wine in message.recommendations"
              :key="wine.slug"
              :wine="wine"
            />
          </div>
        </article>

        <div v-if="isSubmitting" class="sommelier-typing" role="status">
          <RefreshCw class="spin" :size="19" aria-hidden="true" />
          <span>Сомелье сверяется с каталогом…</span>
        </div>

        <div v-if="errorMessage" class="sommelier-chat-error" role="alert">
          <p>{{ errorMessage }}</p>
          <button class="button button--secondary" type="button" @click="retry">Повторить</button>
        </div>
        <div ref="conversationEnd" aria-hidden="true" />
      </div>

      <form class="sommelier-composer" @submit.prevent="handleSubmit">
        <label class="sommelier-composer__label" for="sommelier-message">Ваш запрос</label>
        <textarea
          id="sommelier-message"
          v-model="draft"
          rows="2"
          maxlength="800"
          placeholder="Например: сухое белое к рыбе"
          :disabled="isSubmitting"
          @keydown.enter.exact.prevent="handleSubmit"
        />
        <button class="button button--primary" type="submit" :disabled="isSubmitting || !draft.trim()">
          <Send :size="18" aria-hidden="true" />
          <span>Отправить</span>
        </button>
      </form>
    </section>
  </div>
</template>
