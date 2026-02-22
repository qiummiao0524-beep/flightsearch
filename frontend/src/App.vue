<script setup lang="ts">
import { ref, computed } from 'vue'
import { useChatStore } from './stores/chat'
import ChatBox from './components/ChatBox.vue'
import TripCard from './components/TripCard.vue'
import ClarifyCard from './components/ClarifyCard.vue'
import FlightList from './components/FlightList.vue'
import MockDataDialog from './components/MockDataDialog.vue'

const chatStore = useChatStore()

const showTripCard = computed(() => chatStore.tripInfo !== null)
const showClarify = computed(() => chatStore.currentClarify !== null)
const showFlights = computed(() => chatStore.flights.length > 0)

// Mock 数据对话框状态
const showMockDialog = ref(false)

function openMockDialog() {
  showMockDialog.value = true
}

function closeMockDialog() {
  showMockDialog.value = false
}
</script>

<template>
  <div class="app">
    <!-- 背景装饰 -->
    <div class="bg-decoration">
      <div class="cloud cloud-1">☁️</div>
      <div class="cloud cloud-2">☁️</div>
      <div class="plane">✈️</div>
    </div>
    
    <!-- 头部 -->
    <header class="header">
      <div class="logo">
        <span class="logo-icon">🛫</span>
        <span class="logo-text">AI 航班搜索</span>
      </div>
      <button class="reset-btn" @click="chatStore.reset" v-if="chatStore.messages.length > 0">
        重新开始
      </button>
    </header>
    
    <!-- 主内容区 -->
    <main class="main">
      <!-- 左侧：对话框 -->
      <section class="chat-section">
        <ChatBox />
      </section>
      
      <!-- 右侧：信息卡片 -->
      <aside class="info-section">
        <!-- 行程卡片 -->
        <TripCard 
          v-if="showTripCard" 
          :trip-info="chatStore.tripInfo!" 
        />
        
        <!-- 澄清卡片 -->
        <ClarifyCard 
          v-if="showClarify"
          :clarify="chatStore.currentClarify!"
          @select="chatStore.selectOption"
        />
        
        <!-- 航班列表 -->
        <FlightList 
          v-if="showFlights"
          :flights="chatStore.flights"
          :is-mocked="chatStore.isMocked"
          :debug-info="chatStore.debugInfo"
          @show-mock-data="openMockDialog"
        />
        
        <!-- 空状态 -->
        <div v-if="!showTripCard && !showClarify && !showFlights" class="empty-info">
          <div class="empty-icon">🌤️</div>
          <div class="empty-text">
            在左侧对话框输入您的出行需求<br>
            AI 助手会帮您搜索航班
          </div>
        </div>
      </aside>
    </main>
    
    <!-- Mock 数据对话框 -->
    <MockDataDialog 
      :visible="showMockDialog"
      :mock-data="chatStore.debugInfo?.mock_request || {}"
      @close="closeMockDialog"
    />
  </div>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background: linear-gradient(180deg, #fce4ec 0%, #e3f2fd 50%, #fff9c4 100%);
  min-height: 100vh;
}

#app {
  min-height: 100vh;
}
</style>

<style scoped>
.app {
  min-height: 100vh;
  padding: 20px;
  position: relative;
  overflow: hidden;
}

/* 背景装饰 */
.bg-decoration {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 0;
}

.cloud {
  position: absolute;
  font-size: 60px;
  opacity: 0.3;
}

.cloud-1 {
  top: 10%;
  left: 5%;
  animation: float 6s ease-in-out infinite;
}

.cloud-2 {
  top: 15%;
  right: 10%;
  animation: float 8s ease-in-out infinite;
  animation-delay: -2s;
}

.plane {
  position: absolute;
  top: 8%;
  left: 15%;
  font-size: 40px;
  animation: fly 10s linear infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-20px);
  }
}

@keyframes fly {
  0% {
    transform: translate(0, 0) rotate(-10deg);
  }
  50% {
    transform: translate(100px, -30px) rotate(-10deg);
  }
  100% {
    transform: translate(0, 0) rotate(-10deg);
  }
}

/* 头部 */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 20px;
  margin-bottom: 20px;
  position: relative;
  z-index: 1;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  font-size: 32px;
}

.logo-text {
  font-size: 24px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.reset-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.8);
  color: #666;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.reset-btn:hover {
  background: white;
  color: #333;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 主内容 */
.main {
  display: grid;
  grid-template-columns: 1fr 380px;
  gap: 24px;
  max-width: 1400px;
  margin: 0 auto;
  height: calc(100vh - 120px);
  position: relative;
  z-index: 1;
}

.chat-section {
  height: 100%;
}

.info-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow-y: auto;
  padding-right: 4px;
}

/* 空状态 */
.empty-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 20px;
  text-align: center;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-text {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
}

/* 响应式 */
@media (max-width: 900px) {
  .main {
    grid-template-columns: 1fr;
    grid-template-rows: 1fr auto;
  }
  
  .info-section {
    max-height: 300px;
  }
}
</style>
