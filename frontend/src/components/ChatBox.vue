<script setup lang="ts">
import { ref, nextTick, watch } from 'vue'
import { useChatStore } from '../stores/chat'
import ClarifyCard from './ClarifyCard.vue'

const chatStore = useChatStore()
const inputText = ref('')
const messagesContainer = ref<HTMLElement | null>(null)

// 进度步骤定义（幽默风格 + Mock 节点）
const progressSteps = [
  { id: 'UNDERSTANDING', label: '🧠 正在读懂你的心思...' },
  { id: 'SEARCHING', label: '🔍 全球航线大搜罗中...' },
  { id: 'MOCKING', label: '⌛️ 未查询到航线正在Mock，请耐心等待' },
  { id: 'DONE', label: '🎉 搞定！结果已送达' }
]

// 判断步骤状态（根据消息自身的 progressStatus）
const getStepStatus = (stepId: string, msgProgress: string) => {
  if (!msgProgress) return 'pending'
  if (msgProgress === 'DONE') return 'completed'
  if (msgProgress === stepId) return 'active'

  const currentIndex = progressSteps.findIndex(s => s.id === msgProgress)
  const stepIndex = progressSteps.findIndex(s => s.id === stepId)

  // 特殊处理 UNDERSTANDING_DONE
  if (msgProgress === 'UNDERSTANDING_DONE' && stepId === 'UNDERSTANDING') return 'completed'
  if (msgProgress === 'UNDERSTANDING_DONE') {
    return stepIndex <= 0 ? 'completed' : 'pending'
  }

  if (currentIndex > stepIndex) return 'completed'
  return 'pending'
}

// 是否显示 MOCKING 步骤（只有实际触发了 Mock 才显示）
const shouldShowMocking = (msg: any) => {
  const p = msg.progressStatus || ''
  return p === 'MOCKING' || (p === 'DONE' && msg.is_mocked)
}

// 发送消息
async function handleSend() {
  const text = inputText.value.trim()
  if (!text || chatStore.isLoading) return
  
  inputText.value = ''
  await chatStore.send(text)
}

// 处理键盘事件
function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSend()
  }
}

// 自动滚动到底部
watch(
  () => [chatStore.messages.length, chatStore.currentProgress],
  async () => {
    await nextTick()
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  },
  { deep: true }
)
// 获取动态日期提示（当前时间 + 2天）
const getDynamicDate = () => {
  const date = new Date()
  date.setDate(date.getDate() + 2)
  return `${date.getMonth() + 1}月${date.getDate()}日`
}
</script>

<template>
  <div class="chat-box">
    <!-- 消息列表 -->
    <div class="messages" ref="messagesContainer">
      <!-- 欢迎消息 -->
      <div v-if="chatStore.messages.length === 0" class="welcome">
        <div class="welcome-icon">✈️</div>
        <div class="welcome-text">
          您好！我是航班搜索助手<br>
          告诉我您想去哪里，我来帮您找航班~
        </div>
        <div class="welcome-tips">
          <div class="tip">例如：帮我查明天上海到香港的机票</div>
          <div class="tip">例如：{{ getDynamicDate() }}北京飞东京，两个大人</div>
          <div class="tip">例如：查一下MU5101航班</div>
        </div>
      </div>
      
      <!-- 消息列表 -->
      <div 
        v-for="msg in chatStore.messages" 
        :key="msg.id"
        :class="['message', msg.role]"
      >
        <div class="message-content">
          <div class="avatar">
            {{ msg.role === 'user' ? '👤' : '🤖' }}
          </div>
          <div class="bubble">
            <!-- 进度步骤（有 progressStatus 的消息才显示） -->
            <div v-if="msg.progressStatus" class="progress-list">
              <template v-for="step in progressSteps" :key="step.id">
                <div
                  v-show="(step.id !== 'MOCKING' || shouldShowMocking(msg)) && getStepStatus(step.id, msg.progressStatus || '') !== 'pending'"
                  :class="['progress-item', getStepStatus(step.id, msg.progressStatus || '')]"
                >
                  <div class="step-icon">
                    <span v-if="getStepStatus(step.id, msg.progressStatus || '') === 'completed'" class="check-icon">✓</span>
                    <span v-else-if="getStepStatus(step.id, msg.progressStatus || '') === 'active'" class="spinner"></span>
                    <span v-else class="dot-icon"></span>
                  </div>
                  <span class="step-label">{{ step.label }}</span>
                </div>
                
                <!-- 嵌入：理解节点下方的说明文字 -->
                <!-- 如果已经走完了 UNDERSTANDING（此时 content 已经被前置下发），就将其展示 -->
                <div 
                  v-if="step.id === 'UNDERSTANDING' && msg.content && msg.type !== 'error' && msg.type !== 'clarify'" 
                  class="step-sub-text"
                >
                  └ {{ msg.content }}
                </div>
              </template>
            </div>

            <!-- 进度中的小动画 -->
            <div v-if="msg.progressStatus && msg.progressStatus !== 'DONE' && msg.progressStatus !== 'ERROR' && !msg.content" class="typing-small">
              <span></span><span></span><span></span>
            </div>

            <div v-if="msg.content && msg.type !== 'result' && msg.type !== 'searching'" :class="{ 'reply-text': !!msg.progressStatus }">
              {{ msg.content }}
            </div>

            <!-- 内嵌澄清卡片（如果当前消息是澄清类型） -->
            <ClarifyCard
              v-if="msg.type === 'clarify' && msg.clarify"
              :clarify="msg.clarify"
              :disabled="msg.id !== chatStore.messages[chatStore.messages.length - 1]?.id"
              @select="chatStore.selectOption"
            />
          </div>
        </div>
      </div>
    </div>
    
    <!-- 输入框 -->
    <div class="input-area">
      <div class="input-wrapper">
        <input
          v-model="inputText"
          type="text"
          placeholder="去哪里飞? 告诉我你的计划~"
          @keydown="handleKeydown"
          :disabled="chatStore.isLoading"
        />
        <button 
          class="send-btn" 
          @click="handleSend"
          :disabled="!inputText.trim() || chatStore.isLoading"
        >
          发送
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chat-box {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  overflow: hidden;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.welcome {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 20px;
  text-align: center;
}

.welcome-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.welcome-text {
  font-size: 16px;
  color: #333;
  line-height: 1.6;
  margin-bottom: 24px;
}

.welcome-tips {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.tip {
  font-size: 13px;
  color: #666;
  padding: 8px 16px;
  background: rgba(0, 0, 0, 0.03);
  border-radius: 20px;
}

.message {
  margin-bottom: 16px;
}

.message-content {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.message.user .message-content {
  flex-direction: row-reverse;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.bubble {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 16px;
  font-size: 14px;
  line-height: 1.5;
}

.message.user .bubble {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-bottom-right-radius: 4px;
}

.message.assistant .bubble {
  background: white;
  color: #333;
  border-bottom-left-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

/* 进度列表样式 */
.progress-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 4px 0;
}

.progress-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  color: #bbb;
  transition: all 0.3s ease;
  animation: fadeInUp 0.3s ease forwards;
}

.progress-item.active {
  color: #667eea;
  font-weight: 500;
  transform: translateX(4px);
}

.progress-item.completed {
  color: #764ba2;
}

.step-sub-text {
  padding-left: 28px;
  font-size: 12px;
  color: #888;
  margin-top: -6px;
  margin-bottom: 4px;
}

.step-icon {
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.check-icon {
  font-size: 13px;
  font-weight: 700;
  color: #764ba2;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.15), rgba(118, 75, 162, 0.15));
  display: flex;
  align-items: center;
  justify-content: center;
  animation: scaleIn 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.dot-icon {
  width: 6px;
  height: 6px;
  background: #ddd;
  border-radius: 50%;
}

.spinner {
  width: 12px;
  height: 12px;
  border: 2px solid #667eea;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.typing-small {
  display: flex;
  gap: 3px;
  margin-top: 6px;
  padding-left: 28px;
}

.typing-small span {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: #667eea;
  animation: typing 1s infinite ease-in-out both;
}

.typing-small span:nth-child(2) { animation-delay: 0.2s; }
.typing-small span:nth-child(3) { animation-delay: 0.4s; }

/* 回复文本（进度完成后出现在节点下方） */
.reply-text {
  margin-top: 12px;
  padding-top: 10px;
  border-top: 1px solid rgba(102, 126, 234, 0.1);
  animation: fadeInUp 0.4s ease;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@keyframes scaleIn {
  from { transform: scale(0); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}

@keyframes typing {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40% { transform: scale(1.2); opacity: 1; }
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.input-area {
  padding: 16px 20px;
  background: rgba(255, 255, 255, 0.8);
  border-top: 1px solid rgba(0, 0, 0, 0.05);
}

.input-wrapper {
  display: flex;
  gap: 12px;
  background: white;
  border-radius: 25px;
  padding: 4px 4px 4px 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.input-wrapper input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 14px;
  background: transparent;
}

.input-wrapper input::placeholder {
  color: #aaa;
}

.send-btn {
  padding: 10px 24px;
  border: none;
  border-radius: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.send-btn:hover:not(:disabled) {
  transform: scale(1.02);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
