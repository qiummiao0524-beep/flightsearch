<script setup lang="ts">
import { ref, nextTick, watch } from 'vue'
import { useChatStore } from '../stores/chat'

const chatStore = useChatStore()
const inputText = ref('')
const messagesContainer = ref<HTMLElement | null>(null)

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
  () => chatStore.messages.length,
  async () => {
    await nextTick()
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  }
)
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
          <div class="tip">例如：2月15日北京飞东京，两个大人</div>
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
            {{ msg.content }}
          </div>
        </div>
      </div>
      
      <!-- 加载状态 -->
      <div v-if="chatStore.isLoading" class="message assistant loading">
        <div class="message-content">
          <div class="avatar">🤖</div>
          <div class="bubble">
            <div class="typing">
              <span></span>
              <span></span>
              <span></span>
            </div>
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

/* 打字动画 */
.typing {
  display: flex;
  gap: 4px;
  padding: 4px 0;
}

.typing span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ccc;
  animation: typing 1.4s infinite ease-in-out both;
}

.typing span:nth-child(1) {
  animation-delay: -0.32s;
}

.typing span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes typing {
  0%, 80%, 100% {
    transform: scale(0.6);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
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
