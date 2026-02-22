<script setup lang="ts">
import type { FlightInfo, DebugInfo } from '../types'

defineProps<{
  flights: FlightInfo[]
  isMocked?: boolean
  debugInfo?: DebugInfo | null
}>()

const emit = defineEmits<{
  showMockData: []
}>()

function formatTime(dateStr?: string): string {
  if (!dateStr) return '--:--'
  // 处理多种时间格式
  if (dateStr.includes('T')) {
    const timePart = dateStr.split('T')[1]
    return timePart ? timePart.substring(0, 5) : '--:--'
  }
  if (dateStr.length >= 12) {
    // yyyyMMddHHmm 格式
    return `${dateStr.substring(8, 10)}:${dateStr.substring(10, 12)}`
  }
  return dateStr
}

function formatDuration(minutes?: string | number): string {
  if (minutes === undefined || minutes === null) return '--'
  const m = typeof minutes === 'string' ? parseInt(minutes) : minutes
  if (isNaN(m) || m <= 0) return '--'
  const h = Math.floor(m / 60)
  const min = m % 60
  return `${h}h${min > 0 ? min + 'm' : ''}`
}

function formatPrice(price: string | number): string {
  const p = typeof price === 'string' ? parseFloat(price) : price
  return `¥${p.toLocaleString()}`
}
</script>

<template>
  <div class="flight-list">
    <div class="list-header">
      <span class="header-icon">🔍</span>
      <span class="header-title">为您找到的航班</span>
      <button v-if="isMocked && debugInfo?.mock_request" class="mock-badge" @click="emit('showMockData')">
        Mock数据
      </button>
    </div>
    
    <div class="list-tabs">
      <button class="tab active">直飞</button>
      <button class="tab">起飞时间段</button>
    </div>
    
    <div class="flights">
      <div 
        v-for="flight in flights" 
        :key="flight.id"
        class="flight-item"
      >
        <div class="flight-main">
          <!-- 航班信息 -->
          <div class="flight-info">
            <div class="airline">
              <span class="airline-logo">✈️</span>
              <span class="flight-no">{{ flight.segments[0]?.flight_no }}</span>
            </div>
            
            <div class="route">
              <div class="time-block">
                <span class="time">{{ formatTime(flight.segments[0]?.departure.time) }}</span>
                <span class="airport">{{ flight.segments[0]?.departure.code }}</span>
              </div>
              
              <div class="duration-block">
                <span class="duration">{{ formatDuration(flight.segments[0]?.duration) }}</span>
                <div class="duration-line">
                  <span class="line"></span>
                  <span class="dot" v-if="flight.is_transfer">经停</span>
                </div>
              </div>
              
              <div class="time-block">
                <span class="time">{{ formatTime(flight.segments[flight.segments.length - 1]?.arrival.time) }}</span>
                <span class="airport">{{ flight.segments[flight.segments.length - 1]?.arrival.code }}</span>
              </div>
            </div>
          </div>
          
          <!-- 价格 -->
          <div class="price-block">
            <span class="price">{{ formatPrice(flight.price.total) }}</span>
            <span class="price-label">起</span>
          </div>
        </div>
        
        <!-- 服务标签 -->
        <div class="flight-services" v-if="flight.labels && flight.labels.length > 0">
          <span 
            v-for="(label, idx) in flight.labels.slice(0, 3)" 
            :key="idx"
            class="service-tag"
          >
            {{ label.name || label }}
          </span>
        </div>
      </div>
      
      <!-- 空状态 -->
      <div v-if="flights.length === 0" class="empty-state">
        <span class="empty-icon">🛫</span>
        <span class="empty-text">暂无航班数据</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.flight-list {
  background: white;
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.list-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.header-icon {
  font-size: 18px;
}

.header-title {
  font-weight: 600;
  color: #333;
  flex: 1;
}

.mock-badge {
  font-size: 11px;
  padding: 4px 10px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
}

.mock-badge:hover {
  transform: scale(1.05);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.4);
}

.list-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.tab {
  padding: 6px 16px;
  border: none;
  background: #f5f5f5;
  border-radius: 20px;
  font-size: 13px;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
}

.tab.active {
  background: #333;
  color: white;
}

.flights {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 400px;
  overflow-y: auto;
}

.flight-item {
  background: #fafafa;
  border-radius: 12px;
  padding: 12px;
  transition: all 0.2s;
}

.flight-item:hover {
  background: #f0f0f0;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.flight-main {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.flight-info {
  flex: 1;
}

.airline {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
}

.airline-logo {
  font-size: 16px;
}

.flight-no {
  font-size: 13px;
  color: #666;
  font-weight: 500;
}

.route {
  display: flex;
  align-items: center;
  gap: 16px;
}

.time-block {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.time {
  font-size: 20px;
  font-weight: 600;
  color: #333;
}

.airport {
  font-size: 12px;
  color: #999;
}

.duration-block {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 80px;
}

.duration {
  font-size: 12px;
  color: #666;
}

.duration-line {
  display: flex;
  align-items: center;
  width: 100%;
  margin-top: 4px;
}

.line {
  flex: 1;
  height: 1px;
  background: #ddd;
}

.dot {
  font-size: 10px;
  color: #ff9800;
  padding: 0 4px;
}

.price-block {
  display: flex;
  align-items: baseline;
  gap: 2px;
}

.price {
  font-size: 20px;
  font-weight: 600;
  color: #ff5722;
}

.price-label {
  font-size: 12px;
  color: #999;
}

.flight-services {
  display: flex;
  gap: 6px;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px dashed #eee;
}

.service-tag {
  font-size: 11px;
  padding: 2px 8px;
  background: #e3f2fd;
  color: #1976d2;
  border-radius: 10px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px;
  color: #999;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.empty-text {
  font-size: 14px;
}
</style>
