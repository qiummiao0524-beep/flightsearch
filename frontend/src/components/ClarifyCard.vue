<script setup lang="ts">
import type { ClarifyInfo } from '../types'

const props = defineProps<{
  clarify: ClarifyInfo
  disabled?: boolean
}>()

const emit = defineEmits<{
  select: [option: { label: string; value: string }]
}>()

function handleSelect(option: { label: string; value: string }) {
  if (props.disabled) return
  emit('select', option)
}
</script>

<template>
  <div class="clarify-card" :class="{ 'is-disabled': disabled }">
    <div class="clarify-header">
      <span class="clarify-icon">❓</span>
      <span class="clarify-title">需要确认一下</span>
    </div>
    
    <div class="clarify-question">
      {{ clarify.question }}
    </div>
    
    <div class="clarify-options">
      <button
        v-for="option in clarify.options"
        :key="option.value"
        class="option-btn"
        @click="handleSelect(option)"
      >
        <span class="option-icon">✓</span>
        {{ option.label }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.clarify-card {
  margin-top: 12px;
  background: rgba(240, 247, 250, 0.6);
  border-radius: 12px;
  padding: 12px;
  border: 1px solid rgba(118, 75, 162, 0.1);
  transition: all 0.3s ease;
}

.clarify-card.is-disabled {
  opacity: 0.6;
  pointer-events: none;
  filter: grayscale(100%);
}

.clarify-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.clarify-icon {
  font-size: 18px;
}

.clarify-title {
  font-weight: 600;
  color: #333;
}

.clarify-question {
  color: #555;
  margin-bottom: 12px;
  line-height: 1.4;
  font-size: 13px;
}

.clarify-options {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.option-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: white;
  border: none;
  border-radius: 25px;
  cursor: pointer;
  font-size: 14px;
  color: #333;
  transition: all 0.2s;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.option-btn:hover {
  background: #f0f7fa;
  transform: translateX(4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.option-icon {
  color: #4dabf7;
  font-weight: bold;
}
</style>
