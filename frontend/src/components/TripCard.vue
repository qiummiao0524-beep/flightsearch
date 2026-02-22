<script setup lang="ts">
import { computed } from 'vue'
import type { TripInfo } from '../types'

const props = defineProps<{
  tripInfo: TripInfo
}>()

const travelTypeText = computed(() => {
  const map: Record<string, string> = {
    'OW': '单程',
    'RT': '往返',
    'OJ': '缺口程'
  }
  return map[props.tripInfo.travel_type] || props.tripInfo.travel_type
})

const cabinText = computed(() => {
  const map: Record<string, string> = {
    'Y': '经济舱',
    'S': '超值经济舱',
    'C': '公务舱',
    'F': '头等舱',
    'ALL': '全部舱位'
  }
  return props.tripInfo.cabin_name || map[props.tripInfo.cabin_class] || props.tripInfo.cabin_class
})

const passengerText = computed(() => {
  const types: Record<string, string> = {
    'ADT': '成人',
    'CHD': '儿童',
    'INF': '婴儿'
  }
  return props.tripInfo.passengers
    .filter(p => p.count > 0)
    .map(p => `${p.count}${types[p.type] || p.type}`)
    .join(' ')
})

function formatDate(dateStr?: string): string {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  const month = date.getMonth() + 1
  const day = date.getDate()
  const weekday = weekdays[date.getDay()]
  return `${month}月${day}日 (${weekday})`
}
</script>

<template>
  <div class="trip-card">
    <div class="trip-header">
      <span class="trip-icon">📋</span>
      <span class="trip-title">您的行程安排</span>
      <span class="trip-type-badge">{{ travelTypeText }}</span>
    </div>
    
    <div class="trip-content">
      <!-- 出发地 -->
      <div class="trip-item" v-if="tripInfo.departure">
        <span class="item-icon">✈️</span>
        <span class="item-label">出发地：</span>
        <span class="item-value">
          {{ tripInfo.departure.city }}
          <span class="code" v-if="tripInfo.departure.code">({{ tripInfo.departure.code }})</span>
        </span>
      </div>
      
      <!-- 到达地 -->
      <div class="trip-item" v-if="tripInfo.arrival">
        <span class="item-icon">📍</span>
        <span class="item-label">到达地：</span>
        <span class="item-value">
          {{ tripInfo.arrival.city }}
          <span class="code" v-if="tripInfo.arrival.code">({{ tripInfo.arrival.code }})</span>
        </span>
      </div>
      
      <!-- 出发日期 -->
      <div class="trip-item" v-if="tripInfo.dep_date">
        <span class="item-icon">📅</span>
        <span class="item-label">日期：</span>
        <span class="item-value">{{ formatDate(tripInfo.dep_date) }}</span>
      </div>
      
      <!-- 返程日期 -->
      <div class="trip-item" v-if="tripInfo.return_date">
        <span class="item-icon">🔄</span>
        <span class="item-label">返程：</span>
        <span class="item-value">{{ formatDate(tripInfo.return_date) }}</span>
      </div>
      
      <!-- 乘客 -->
      <div class="trip-item">
        <span class="item-icon">👤</span>
        <span class="item-label">乘客：</span>
        <span class="item-value">{{ passengerText }}</span>
      </div>
      
      <!-- 舱位 -->
      <div class="trip-item">
        <span class="item-icon">💺</span>
        <span class="item-label">舱位：</span>
        <span class="item-value">{{ cabinText }}</span>
      </div>
      
      <!-- 航司 -->
      <div class="trip-item" v-if="tripInfo.airline_code">
        <span class="item-icon">🏷️</span>
        <span class="item-label">航司：</span>
        <span class="item-value">{{ tripInfo.airline_code }}</span>
      </div>
      
      <!-- 航班号 -->
      <div class="trip-item" v-if="tripInfo.flight_no">
        <span class="item-icon">🔢</span>
        <span class="item-label">航班：</span>
        <span class="item-value">{{ tripInfo.flight_no }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.trip-card {
  background: linear-gradient(135deg, #fff9f0 0%, #fff5f5 100%);
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.trip-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px dashed #f0d0d0;
}

.trip-icon {
  font-size: 18px;
}

.trip-title {
  font-weight: 600;
  color: #333;
  flex: 1;
}

.trip-type-badge {
  font-size: 12px;
  padding: 2px 8px;
  background: #ff9a9e;
  color: white;
  border-radius: 10px;
}

.trip-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.trip-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.item-icon {
  width: 20px;
  text-align: center;
}

.item-label {
  color: #666;
  min-width: 60px;
}

.item-value {
  color: #333;
  font-weight: 500;
}

.code {
  color: #999;
  font-weight: normal;
}
</style>
