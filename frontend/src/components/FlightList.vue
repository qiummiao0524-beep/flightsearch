<script setup lang="ts">

import { ref, computed } from 'vue'

// 控制 popover 显示状态的映射：flight id -> boolean
const activePopover = ref<string | null>(null)

function togglePopover(id: string, event: Event) {
  event.stopPropagation()
  if (activePopover.value === id) {
    activePopover.value = null
  } else {
    activePopover.value = id
  }
}

function handleOutsideClick() {
  activePopover.value = null
}

// 映射乘客类型到中文展示
const PASSENGER_TYPE_MAP: Record<string, string> = {
  'ADT': '成人',
  'CHD': '儿童',
  'INF': '婴儿'
}

function getPassengerTypeName(type: string): string {
  return PASSENGER_TYPE_MAP[type] || type
}

function hasMultiplePassengers(flight: FlightInfo): boolean {
  if (!flight.price?.passenger_prices || flight.price.passenger_prices.length === 0) return false;
  
  // 计算总人数
  const totalCount = flight.price.passenger_prices.reduce((sum, p) => sum + Number(p.count), 0);
  if (totalCount > 1) return true;
  
  // 检查是否有非成人的类型 (比如: 1 CHD)
  const passengerTypes = flight.price.passenger_prices.map(p => p.type);
  if (passengerTypes.includes('CHD') || passengerTypes.includes('INF')) return true;
  
  return false;
}

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
    hours = match[1] || '00'
    minutes = match[2] || '00'
  } else if (dateStr.length >= 12 && /^\d+$/.test(dateStr)) {
    // 2. 处理纯数字紧凑格式: 202602231005
    hours = dateStr.substring(8, 10)
    minutes = dateStr.substring(10, 12)
  } else {
    // 3. 兜底逻辑：如果无法匹配，尝试查找最后一部分可能的时间
    const parts = dateStr.split(' ')
    const lastPart = parts[parts.length - 1]
    if (lastPart && lastPart.includes(':')) {
      const timeParts = lastPart.split(':')
      hours = timeParts[0] || '00'
      minutes = timeParts[1] || '00'
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
  if (!price) return '¥0'
  return `¥${parseInt(price.toString()).toLocaleString()}`
}

function getPassengerSubTypeName(type: string): string {
  const map: Record<string, string> = {
    'ADT': '成人',
    'CHD': '儿童',
    'INF': '婴儿'
  }
  return map[type] || type
}

function getFlightNos(segments: any[]): string {
  if (!segments || segments.length === 0) return ''
  const nos = segments.map(s => s.flight_no).filter(Boolean)
  return Array.from(new Set(nos)).join(' / ')
}
</script>

<template>
  <div class="flight-list" @mousedown="handleOutsideClick">
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
              <span v-if="flight.cabin_name" class="cabin-info">{{ flight.cabin_name }}({{ flight.cabin_class }})</span>
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
                  <span v-if="flight.cabin_name" class="cabin-info">{{ flight.cabin_name }}({{ flight.cabin_class }})</span>
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
                  <span v-if="flight.cabin_name" class="cabin-info">{{ flight.cabin_name }}({{ flight.cabin_class }})</span>
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
            <div class="price-main">
              <span class="price">{{ formatPrice(flight.price.total) }}</span>
              <span class="price-label">总价</span>
            </div>
            
            <!-- 乘客价格明细悬浮/展示 -->
            <div class="price-breakdown" v-if="flight.price.passengers && flight.price.passengers.length > 0">
              <div class="breakdown-toggle">
                明细 <span class="arrow">▼</span>
              </div>
              <div class="breakdown-dropdown">
                <div v-for="(p, i) in flight.price.passengers" :key="'p-'+i" class="breakdown-item">
                  <span class="p-name">{{ getPassengerSubTypeName(p.type) }} x {{ p.count }}</span>
                  <span class="p-val">{{ formatPrice(p.total) }}</span>
                </div>
              </div>
            </div>
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
  align-items: center;
  gap: 16px;
}

.flight-info {
  flex: 1;
  min-width: 0;
}

.airline {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
  width: 100%;
  overflow: hidden;
}

.airline-logo {
  font-size: 16px;
}

.flight-no {
  font-size: 13px;
  color: #666;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 0 1 auto;
  min-width: 0;
}

.cabin-info {
  font-size: 11px;
  color: #888;
  background-color: #f5f5f5;
  padding: 2px 6px;
  border-radius: 4px;
  margin-left: auto;
  font-weight: 500;
  white-space: nowrap;
  flex-shrink: 0;
}

.route {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 12px;
  max-width: 400px;
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
  position: relative;
  cursor: pointer;
}

.transfer-details:hover {
  overflow: visible;
  white-space: normal;
  z-index: 10;
  background: white;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  padding: 4px;
  border-radius: 4px;
  border: 1px solid #eee;
  left: 50%;
  transform: translateX(-50%);
  width: max-content;
  max-width: 200px;
}


.price-block-wrapper {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  position: relative;
}

.price-block {
  text-align: right;
  min-width: 130px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  position: relative;
}

.price-main {
  display: flex;
  align-items: baseline;
<<<<<<< HEAD
  gap: 4px;
}

.price-label-group {
  display: flex;
  align-items: center;
  gap: 2px;
=======
  justify-content: flex-end;
>>>>>>> develop
}

.price {
  font-size: 20px;
  font-weight: 700;
  color: #ff5a5f;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  letter-spacing: -0.5px;
}

.price-label {
  font-size: 12px;
  color: #999;
  margin-left: 4px;
}

<<<<<<< HEAD
.price-subtext {
=======
.price-breakdown {
  position: absolute;
  right: 0;
  bottom: -24px;
  cursor: pointer;
}

.breakdown-toggle {
  font-size: 12px;
  color: #666;
  text-decoration: underline dashed;
  text-underline-offset: 3px;
  transition: color 0.2s;
}

.breakdown-toggle:hover {
  color: #333;
}

.breakdown-toggle .arrow {
  font-size: 10px;
  display: inline-block;
  transform: scale(0.8);
}

.breakdown-dropdown {
  display: none;
  position: absolute;
  right: 0;
  top: 100%;
  margin-top: 8px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
  padding: 12px;
  width: max-content;
  min-width: 150px;
  z-index: 100;
  border: 1px solid #f0f0f0;
}

.price-breakdown:hover .breakdown-dropdown {
  display: block;
}

.breakdown-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 13px;
  color: #666;
  border-bottom: 1px dashed #f0f0f0;
  padding-bottom: 8px;
}

.breakdown-item:last-child {
  margin-bottom: 0;
  border-bottom: none;
  padding-bottom: 0;
}

.p-name {
  color: #333;
}

.p-val {
  color: #ff5a5f;
  font-weight: 500;
}
.flight-services {
  display: flex;
  gap: 6px;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px dashed #eee;
}

.service-tag {
>>>>>>> develop
  font-size: 11px;
  color: #999;
  margin-top: 4px;
}

.price-detail-container {
  position: relative;
  display: flex;
  align-items: center;
}

.detail-icon-btn {
  background: none;
  border: none;
  font-size: 16px;
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.6;
  transition: opacity 0.2s;
}

.detail-icon-btn:hover {
  opacity: 1;
}

.price-popover {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 8px;
  width: 200px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
  border: 1px solid #ebeef5;
  z-index: 100;
  overflow: hidden;
  animation: fadeIn 0.2s ease-out;
}

/* 小箭头 */
.price-popover::before {
  content: '';
  position: absolute;
  top: -6px;
  right: 14px;
  border-width: 0 6px 6px 6px;
  border-style: solid;
  border-color: transparent transparent white transparent;
  filter: drop-shadow(0 -2px 2px rgba(0,0,0,0.05));
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-5px); }
  to { opacity: 1; transform: translateY(0); }
}

.popover-header {
  padding: 10px 12px;
  font-size: 13px;
  font-weight: 600;
  color: #333;
  border-bottom: 1px solid #f0f0f0;
  background: #fafafa;
}

.popover-body {
  padding: 8px 12px;
}

.passenger-price-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 0;
  font-size: 12px;
}

.p-type {
  color: #666;
  font-weight: 500;
}

.p-calc {
  color: #333;
}

.popover-footer {
  padding: 10px 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid #f0f0f0;
  font-size: 13px;
  font-weight: 600;
  color: #ff5722;
}

/* 往返程航班展示的间隔控制 */
.rt-flight-info {
  display: flex;
  flex-direction: column;
  gap: 16px;
  flex: 1;
}

.rt-segment {
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 8px;
  padding: 12px;
  border: 1px solid #f0f0f0;
  box-shadow: 0 1px 3px rgba(0,0,0,0.02);
}

.rt-segment-header {
  display: flex;
  align-items: center;
  gap: 6px;
<<<<<<< HEAD
  margin-bottom: 8px;
}

=======
  margin-bottom: 6px;
  width: 100%;
  overflow: hidden;
}

.segment-tag {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
  color: white;
  font-weight: 500;
  white-space: nowrap;
  flex-shrink: 0;
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
>>>>>>> develop
</style>
