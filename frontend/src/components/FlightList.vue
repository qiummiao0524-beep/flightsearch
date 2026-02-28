<script setup lang="ts">
import { ref, computed } from 'vue'
import type { FlightInfo, DebugInfo } from '../types'

const props = defineProps<{
  flights: FlightInfo[]
  isMocked?: boolean
  debugInfo?: DebugInfo | null
}>()

const emit = defineEmits<{
  showMockData: []
}>()

// 排序类型：time (时间从早到晚), price (价格从低到高)
const sortType = ref<'time' | 'price'>('price')

const sortedFlights = computed(() => {
  const result = [...props.flights]
  
  if (sortType.value === 'price') {
    return result.sort((a, b) => {
      const priceA = parseFloat(a.price.total.toString())
      const priceB = parseFloat(b.price.total.toString())
      return priceA - priceB
    })
  } else if (sortType.value === 'time') {
    return result.sort((a, b) => {
      // 提取首个航段的出发时间
      const timeStrA = a.segments[0]?.departure.time || ''
      const timeStrB = b.segments[0]?.departure.time || ''
      
      // 简单的字符串比较即可，因为 ISO 或 YYYY-MM-DD HH:mm 格式字符串比较与时间先后一致
      return timeStrA.localeCompare(timeStrB)
    })
  }
  
  return result
})


function formatTime(dateStr?: string): string {
  if (!dateStr) return '--:--'
  
  let hours = ''
  let minutes = ''

  // 1. 尝试从字符串中提取时间部分 (格式如: 10:5, 10:05, 10:5:00)
  // 匹配类似 HH:mm[:ss] 的部分
  const timeRegex = /(\d{1,2}):(\d{1,2})(?::\d{1,2})?/
  const match = dateStr.match(timeRegex)

  if (match) {
    hours = match[1]
    minutes = match[2]
  } else if (dateStr.length >= 12 && /^\d+$/.test(dateStr)) {
    // 2. 处理纯数字紧凑格式: 202602231005
    hours = dateStr.substring(8, 10)
    minutes = dateStr.substring(10, 12)
  } else {
    // 3. 兜底逻辑：如果无法匹配，尝试查找最后一部分可能的时间
    const parts = dateStr.split(' ')
    const lastPart = parts[parts.length - 1]
    if (lastPart.includes(':')) {
      const timeParts = lastPart.split(':')
      hours = timeParts[0]
      minutes = timeParts[1]
    } else {
      return dateStr
    }
  }

  const pad = (s: string) => s.toString().padStart(2, '0').substring(0, 2)
  return `${pad(hours)}:${pad(minutes)}`
}


function formatDuration(minutes?: string | number): string {
  if (minutes === undefined || minutes === null) return '--'
  const m = typeof minutes === 'string' ? parseInt(minutes) : minutes
  if (isNaN(m) || m <= 0) return '--'
  const h = Math.floor(m / 60)
  const min = m % 60
  return `${h}h${min > 0 ? min + 'm' : ''}`
}

function getTransferStops(segments: any[]): string {
  if (!segments || segments.length <= 1) return ''
  return `${segments.length - 1}转`
}

function getTransferDetails(segments: any[]): string {
  if (!segments || segments.length <= 1) return ''
  const stops = segments.length - 1
  
  const details = []
  for (let i = 0; i < stops; i++) {
    const prevArrStr = segments[i].arrival?.time || ''
    const currDepStr = segments[i+1].departure?.time || ''
    const code = segments[i].arrival?.code || segments[i+1].departure?.code || ''
    
    let durationStr = ''
    if (prevArrStr && currDepStr) {
      const arrTime = new Date(prevArrStr.replace(/-/g, '/')).getTime()
      const depTime = new Date(currDepStr.replace(/-/g, '/')).getTime()
      if (!isNaN(arrTime) && !isNaN(depTime) && depTime > arrTime) {
        const diffMins = Math.floor((depTime - arrTime) / 60000)
        const h = Math.floor(diffMins / 60)
        const m = diffMins % 60
        durationStr = `${h}h${m > 0 ? m + 'm' : ''}`
      }
    }
    details.push(`${code}${durationStr ? '(' + durationStr + ')' : ''}`)
  }
  
  return `经 ${details.join(', ')}`
}

function getRTSegments(segments: any[]) {
  if (!segments || segments.length <= 1) return { outbound: segments || [], inbound: [] }
  if (segments.length === 2) return { outbound: [segments[0]], inbound: [segments[1]] }
  
  let splitIndex = 1
  let maxGap = -1
  
  for (let i = 1; i < segments.length; i++) {
    const prevArr = new Date(segments[i-1].arrival.time.replace(/-/g, '/')).getTime()
    const currDep = new Date(segments[i].departure.time.replace(/-/g, '/')).getTime()
    if (!isNaN(prevArr) && !isNaN(currDep)) {
      const gap = currDep - prevArr
      if (gap > maxGap) {
        maxGap = gap
        splitIndex = i
      }
    }
  }
  
  return {
    outbound: segments.slice(0, splitIndex),
    inbound: segments.slice(splitIndex)
  }
}



function formatPrice(price: string | number): string {
  const p = typeof price === 'string' ? parseFloat(price) : price
  return `¥${p.toLocaleString()}`
}

function getFlightNos(segments: any[]): string {
  if (!segments || segments.length === 0) return ''
  const nos = segments.map(s => s.flight_no).filter(Boolean)
  return Array.from(new Set(nos)).join(' / ')
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
      <button 
        class="tab" 
        :class="{ active: sortType === 'price' }"
        @click="sortType = 'price'"
      >
        价格最低
      </button>
      <button 
        class="tab" 
        :class="{ active: sortType === 'time' }"
        @click="sortType = 'time'"
      >
        起飞最早
      </button>
    </div>
    
    <div class="flights">
      <div 
        v-for="flight in sortedFlights" 
        :key="flight.id"
        class="flight-item"
      >
        <div class="flight-main">
          <!-- 航班信息 -->
          <!-- 单程/多程展示 -->
          <div class="flight-info" v-if="flight.travel_type !== 'RT'">
            <div class="airline">
              <span class="airline-logo">✈️</span>
              <span class="flight-no">{{ getFlightNos(flight.segments) }}</span>
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
                  <span class="transfer-info badge" v-if="flight.is_transfer">
                    {{ getTransferStops(flight.segments) }}
                  </span>
                  <span class="line"></span>
                </div>
                <div class="transfer-details" v-if="flight.is_transfer" :title="getTransferDetails(flight.segments)">
                  {{ getTransferDetails(flight.segments) }}
                </div>
              </div>
              
              <div class="time-block">
                <span class="time">{{ formatTime(flight.segments[flight.segments.length - 1]?.arrival.time) }}</span>
                <span class="airport">{{ flight.segments[flight.segments.length - 1]?.arrival.code }}</span>
              </div>
            </div>
          </div>

          <!-- 往返程展示 -->
          <div class="flight-info rt-flight-info" v-else>
            <template v-for="rt in [getRTSegments(flight.segments)]" :key="'rt-'+flight.id">
              <!-- 去程 -->
              <div class="rt-segment" v-if="rt.outbound.length > 0">
                <div class="rt-segment-header">
                  <span class="segment-tag outbound">去程</span>
                  <span class="airline-logo">✈️</span>
                  <span class="flight-no">{{ getFlightNos(rt.outbound) }}</span>
                </div>
                <div class="route small-route">
                  <div class="time-block">
                    <span class="time">{{ formatTime(rt.outbound[0]?.departure.time) }}</span>
                    <span class="airport">{{ rt.outbound[0]?.departure.code }}</span>
                  </div>
                  <div class="duration-block">
                    <span class="duration">{{ formatDuration(rt.outbound.reduce((acc, seg) => acc + parseInt(seg.duration || '0'), 0)) }}</span>
                    <div class="duration-line">
                      <span class="line"></span>
                      <span class="transfer-info badge" v-if="rt.outbound.length > 1">
                        {{ getTransferStops(rt.outbound) }}
                      </span>
                      <span class="line"></span>
                    </div>
                    <div class="transfer-details" v-if="rt.outbound.length > 1" :title="getTransferDetails(rt.outbound)">
                      {{ getTransferDetails(rt.outbound) }}
                    </div>
                  </div>
                  <div class="time-block">
                    <span class="time">{{ formatTime(rt.outbound[rt.outbound.length - 1]?.arrival.time) }}</span>
                    <span class="airport">{{ rt.outbound[rt.outbound.length - 1]?.arrival.code }}</span>
                  </div>
                </div>
              </div>

              <!-- 返程 -->
              <div class="rt-segment" v-if="rt.inbound.length > 0">
                <div class="rt-segment-header">
                  <span class="segment-tag inbound">返程</span>
                  <span class="airline-logo">✈️</span>
                  <span class="flight-no">{{ getFlightNos(rt.inbound) }}</span>
                </div>
                <div class="route small-route">
                  <div class="time-block">
                    <span class="time">{{ formatTime(rt.inbound[0]?.departure.time) }}</span>
                    <span class="airport">{{ rt.inbound[0]?.departure.code }}</span>
                  </div>
                  <div class="duration-block">
                    <span class="duration">{{ formatDuration(rt.inbound.reduce((acc, seg) => acc + parseInt(seg.duration || '0'), 0)) }}</span>
                    <div class="duration-line">
                      <span class="line"></span>
                      <span class="transfer-info badge" v-if="rt.inbound.length > 1">
                        {{ getTransferStops(rt.inbound) }}
                      </span>
                      <span class="line"></span>
                    </div>
                    <div class="transfer-details" v-if="rt.inbound.length > 1" :title="getTransferDetails(rt.inbound)">
                      {{ getTransferDetails(rt.inbound) }}
                    </div>
                  </div>
                  <div class="time-block">
                    <span class="time">{{ formatTime(rt.inbound[rt.inbound.length - 1]?.arrival.time) }}</span>
                    <span class="airport">{{ rt.inbound[rt.inbound.length - 1]?.arrival.code }}</span>
                  </div>
                </div>
              </div>
            </template>
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

.transfer-info {
  font-size: 10px;
  color: #ff9800;
  padding: 0 4px;
  white-space: nowrap;
  font-weight: 500;
}

.transfer-info.badge {
  background: #fff3e0;
  border-radius: 8px;
  padding: 2px 6px;
  color: #f57c00;
  border: 1px solid #ffe0b2;
}

.transfer-details {
  font-size: 10px;
  color: #999;
  margin-top: 4px;
  max-width: 120px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  text-align: center;
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

.rt-flight-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.rt-segment {
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 8px;
  padding: 8px 12px;
  border: 1px solid #f0f0f0;
}

.rt-segment-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 6px;
}

.segment-tag {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
  color: white;
  font-weight: 500;
}

.segment-tag.outbound {
  background-color: #4daaa7;
}

.segment-tag.inbound {
  background-color: #e58b68;
}

.small-route .time {
  font-size: 16px;
}
</style>
