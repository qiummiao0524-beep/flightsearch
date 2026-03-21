<script setup lang="ts">
import { ref, computed } from 'vue'
import { useChatStore } from './stores/chat'
import ChatBox from './components/ChatBox.vue'
import TripCard from './components/TripCard.vue'
import FlightList from './components/FlightList.vue'
import MockDataDialog from './components/MockDataDialog.vue'
import GuideDialog from './components/GuideDialog.vue'

const chatStore = useChatStore()

const showTripCard = computed(() => chatStore.tripInfo !== null)
const showFlights = computed(() => chatStore.flights.length > 0)

// Mock 数据对话框状态
const showMockDialog = ref(false)

function openMockDialog() {
  showMockDialog.value = true
}

function closeMockDialog() {
  showMockDialog.value = false
}

// 指南对话框状态
const showGuideDialog = ref(false)

function openGuideDialog() {
  showGuideDialog.value = true
}

function closeGuideDialog() {
  showGuideDialog.value = false
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
      <div class="header-actions">
        <button class="guide-btn" @click="openGuideDialog">
          使用指南
        </button>
        <button class="reset-btn" @click="chatStore.reset" v-if="chatStore.messages.length > 0">
          重新开始
        </button>
      </div>
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
        
        <!-- 航班列表 -->
        <FlightList 
          v-if="showFlights"
          :flights="chatStore.flights"
          :is-mocked="chatStore.isMocked"
          :debug-info="chatStore.debugInfo"
          @show-mock-data="openMockDialog"
        />
        
        <!-- 空状态 -->
        <div v-if="!showTripCard && !showFlights" class="empty-info">
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
    
    <!-- 功能指南对话框 -->
    <GuideDialog
      :visible="showGuideDialog"
      @close="closeGuideDialog"
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

/* 统一滚动条样式优化 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.4);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: rgba(102, 126, 234, 0.4);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(102, 126, 234, 0.7);
}
</style>

<style scoped>
.app {
  height: 100vh;
  padding: 20px;
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
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
  flex-shrink: 0;
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

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.guide-btn {
  padding: 8px 16px;
  border: 1px solid #667eea;
  border-radius: 20px;
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.guide-btn:hover {
  background: #667eea;
  color: white;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
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
  grid-template-columns: minmax(0, 1fr) 480px;
  gap: 24px;
  max-width: 1400px;
  margin: 0 auto;
  flex: 1;
  min-height: 0;
  width: 100%;
  position: relative;
  z-index: 1;
}

.chat-section {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
}

.chat-section > * {
  flex: 1;
  min-height: 0;
}

.info-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow-y: auto;
  padding-right: 4px;
  min-height: 0;
  height: 100%;
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
