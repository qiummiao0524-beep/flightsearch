<script setup lang="ts">
import { ref, computed } from 'vue'

const props = defineProps<{
  visible: boolean
  mockData: Record<string, any>
}>()

const emit = defineEmits<{
  close: []
}>()

const copySuccess = ref(false)

const formattedJson = computed(() => {
  try {
    return JSON.stringify(props.mockData, null, 2)
  } catch {
    return '{}'
  }
})

async function copyJson() {
  try {
    await navigator.clipboard.writeText(formattedJson.value)
    copySuccess.value = true
    setTimeout(() => {
      copySuccess.value = false
    }, 2000)
  } catch (err) {
    console.error('复制失败:', err)
  }
}

function handleOverlayClick(e: MouseEvent) {
  if (e.target === e.currentTarget) {
    emit('close')
  }
}
</script>

<template>
  <Teleport to="body">
    <div v-if="visible" class="dialog-overlay" @click="handleOverlayClick">
      <div class="dialog">
        <div class="dialog-header">
          <div class="header-left">
            <span class="dialog-icon">🔧</span>
            <span class="dialog-title">Mock 请求数据</span>
            <span class="badge">DEBUG</span>
          </div>
          <button class="close-btn" @click="emit('close')">×</button>
        </div>
        
        <div class="dialog-body">
          <div class="json-wrapper">
            <pre class="json-content">{{ formattedJson }}</pre>
          </div>
        </div>
        
        <div class="dialog-footer">
          <button class="copy-btn" @click="copyJson">
            {{ copySuccess ? '✓ 已复制' : '📋 复制 JSON' }}
          </button>
          <button class="close-btn-secondary" @click="emit('close')">关闭</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.dialog {
  background: white;
  border-radius: 16px;
  width: 90%;
  max-width: 700px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 16px 16px 0 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.dialog-icon {
  font-size: 20px;
}

.dialog-title {
  font-size: 16px;
  font-weight: 600;
}

.badge {
  font-size: 10px;
  padding: 2px 8px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  font-weight: 500;
}

.close-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border-radius: 8px;
  cursor: pointer;
  font-size: 20px;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.dialog-body {
  flex: 1;
  overflow: hidden;
  padding: 0;
}

.json-wrapper {
  max-height: 50vh;
  overflow: auto;
  background: #1e1e1e;
  margin: 0;
}

.json-content {
  margin: 0;
  padding: 16px 20px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 12px;
  line-height: 1.6;
  color: #d4d4d4;
  white-space: pre-wrap;
  word-break: break-all;
}

.dialog-footer {
  padding: 16px 20px;
  background: #f8f9fa;
  border-top: 1px solid #eee;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  border-radius: 0 0 16px 16px;
}

.copy-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.copy-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.close-btn-secondary {
  padding: 10px 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: white;
  color: #666;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.close-btn-secondary:hover {
  background: #f5f5f5;
  border-color: #ccc;
}

/* 滚动条样式 */
.json-wrapper::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.json-wrapper::-webkit-scrollbar-track {
  background: #2d2d2d;
}

.json-wrapper::-webkit-scrollbar-thumb {
  background: #555;
  border-radius: 4px;
}

.json-wrapper::-webkit-scrollbar-thumb:hover {
  background: #666;
}
</style>
