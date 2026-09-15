<script setup lang="ts">
import { Camera, ImagePlus, LoaderCircle, RotateCcw, ScanLine } from '@lucide/vue'

const emit = defineEmits<{
  fileSelected: [file: File]
  scanRequested: []
  resetRequested: []
}>()

defineProps<{
  status: 'idle' | 'ready' | 'processing' | 'success' | 'error'
  previewUrl?: string
  error?: string
}>()

const cameraInput = useTemplateRef<HTMLInputElement>('cameraInput')
const galleryInput = useTemplateRef<HTMLInputElement>('galleryInput')

function handleFileChange(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]

  if (file) {
    emit('fileSelected', file)
  }
}

function handleReset() {
  if (cameraInput.value) {
    cameraInput.value.value = ''
  }

  if (galleryInput.value) {
    galleryInput.value.value = ''
  }

  emit('resetRequested')
}
</script>

<template>
  <section class="scanner" aria-labelledby="scanner-heading">
    <div class="scanner__copy">
      <p class="eyebrow">Поиск по каталогу российских вин</p>
      <h1 id="scanner-heading">Покажите этикетку — найдём точную карточку</h1>
      <p>
        Снимайте бутылку прямо или выберите готовое фото. Год и мелкие надписи должны быть видны.
      </p>
    </div>

    <div class="scanner__stage">
      <div
        class="viewfinder"
        :class="{ 'viewfinder--filled': previewUrl, 'viewfinder--loading': status === 'processing' }"
      >
        <img
          v-if="previewUrl"
          class="viewfinder__preview"
          :src="previewUrl"
          alt="Выбранная фотография винной этикетки"
        >
        <div v-else class="viewfinder__empty" aria-hidden="true">
          <span class="viewfinder__bottle" />
          <ScanLine :size="34" stroke-width="1.4" />
        </div>

        <span class="viewfinder__corner viewfinder__corner--tl" />
        <span class="viewfinder__corner viewfinder__corner--tr" />
        <span class="viewfinder__corner viewfinder__corner--bl" />
        <span class="viewfinder__corner viewfinder__corner--br" />

        <div v-if="status === 'processing'" class="viewfinder__progress" role="status">
          <LoaderCircle class="spin" :size="28" aria-hidden="true" />
          <strong>Сверяем этикетку</strong>
          <span>Ищем точный год и позицию каталога</span>
        </div>
      </div>

      <div v-if="status === 'idle'" class="scanner__actions">
        <label class="button button--primary" for="wine-camera">
          <Camera :size="20" aria-hidden="true" />
          Снять этикетку
        </label>
        <label class="button button--secondary" for="wine-gallery">
          <ImagePlus :size="20" aria-hidden="true" />
          Выбрать фото
        </label>
      </div>

      <div v-else-if="status === 'ready'" class="scanner__actions">
        <button class="button button--primary" type="button" @click="emit('scanRequested')">
          <ScanLine :size="20" aria-hidden="true" />
          Найти вино
        </button>
        <button class="button button--quiet" type="button" @click="handleReset">
          <RotateCcw :size="19" aria-hidden="true" />
          Другое фото
        </button>
      </div>

      <button
        v-else-if="status === 'error'"
        class="button button--primary scanner__retry"
        type="button"
        @click="handleReset"
      >
        <RotateCcw :size="19" aria-hidden="true" />
        Выбрать другое фото
      </button>

      <input
        id="wine-camera"
        ref="cameraInput"
        class="sr-only"
        type="file"
        name="image"
        accept="image/jpeg,image/png,image/webp"
        capture="environment"
        :disabled="status === 'processing'"
        @change="handleFileChange"
      >
      <input
        id="wine-gallery"
        ref="galleryInput"
        class="sr-only"
        type="file"
        name="image"
        accept="image/jpeg,image/png,image/webp"
        :disabled="status === 'processing'"
        @change="handleFileChange"
      >

      <p v-if="error" class="scanner__error" role="alert">{{ error }}</p>
      <p v-else class="scanner__hint">JPEG, PNG или WebP до 10 МБ</p>
    </div>
  </section>
</template>
