<script setup lang="ts">
import {
  Sparkles,
  ZodiacAquarius,
  ZodiacAries,
  ZodiacCancer,
  ZodiacCapricorn,
  ZodiacGemini,
  ZodiacLeo,
  ZodiacLibra,
  ZodiacPisces,
  ZodiacSagittarius,
  ZodiacScorpio,
  ZodiacTaurus,
  ZodiacVirgo,
} from '@lucide/vue'
import type { Component } from 'vue'

const props = withDefaults(defineProps<{
  symbol: string
  size?: 'compact' | 'regular' | 'large'
}>(), {
  size: 'regular',
})

const zodiacIcons: Record<string, Component> = {
  '♈': ZodiacAries,
  '♉': ZodiacTaurus,
  '♊': ZodiacGemini,
  '♋': ZodiacCancer,
  '♌': ZodiacLeo,
  '♍': ZodiacVirgo,
  '♎': ZodiacLibra,
  '♏': ZodiacScorpio,
  '♐': ZodiacSagittarius,
  '♑': ZodiacCapricorn,
  '♒': ZodiacAquarius,
  '♓': ZodiacPisces,
}

const zodiacIcon = computed(() => zodiacIcons[props.symbol] ?? Sparkles)
</script>

<template>
  <span
    class="zodiac-mark"
    :class="`zodiac-mark--${size}`"
    aria-hidden="true"
  >
    <span class="zodiac-mark__orbit" />
    <component :is="zodiacIcon" class="zodiac-mark__symbol" :stroke-width="1.45" />
    <span class="zodiac-mark__accent" />
  </span>
</template>

<style scoped>
.zodiac-mark {
  position: relative;
  display: inline-grid;
  flex: 0 0 auto;
  place-items: center;
  color: var(--color-wine-dark);
  border: 1px solid rgb(170 133 80 / 72%);
  border-radius: 50%;
  background: linear-gradient(145deg, var(--color-paper), rgb(248 238 238 / 58%));
}

.zodiac-mark--compact {
  width: 46px;
  height: 46px;
}

.zodiac-mark--regular {
  width: 54px;
  height: 54px;
}

.zodiac-mark--large {
  width: 74px;
  height: 74px;
}

.zodiac-mark__orbit {
  position: absolute;
  inset: 4px;
  border: 1px solid rgb(158 11 15 / 18%);
  border-radius: 50%;
  transform: rotate(-11deg);
}

.zodiac-mark__accent {
  position: absolute;
  top: 5%;
  right: 15%;
  width: 5px;
  height: 5px;
  background: var(--color-antique-gold);
  transform: rotate(45deg);
}

.zodiac-mark__symbol {
  position: relative;
  z-index: 1;
  width: 52%;
  height: 52%;
  fill: none;
  stroke: currentcolor;
  stroke-linecap: round;
  stroke-linejoin: round;
}
</style>
