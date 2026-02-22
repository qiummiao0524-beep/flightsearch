import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { ChatMessage, TripInfo, FlightInfo, ClarifyInfo, DebugInfo } from '../types'
import { sendMessage } from '../api/chat'

export const useChatStore = defineStore('chat', () => {
  // 状态
  const sessionId = ref<string>('')
  const messages = ref<ChatMessage[]>([])
  const tripInfo = ref<TripInfo | null>(null)
  const flights = ref<FlightInfo[]>([])
  const currentClarify = ref<ClarifyInfo | null>(null)
  const isLoading = ref(false)
  const isMocked = ref(false)
  const debugInfo = ref<DebugInfo | null>(null)

  // 计算属性
  const hasTrip = computed(() => tripInfo.value !== null)
  const hasFlights = computed(() => flights.value.length > 0)
  const needsClarify = computed(() => currentClarify.value !== null)

  // 生成消息ID
  function generateId(): string {
    return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }

  // 添加用户消息
  function addUserMessage(content: string) {
    messages.value.push({
      id: generateId(),
      role: 'user',
      content,
      timestamp: new Date()
    })
  }

  // 添加助手消息
  function addAssistantMessage(
    content: string,
    type: ChatMessage['type'],
    extras?: {
      trip_info?: TripInfo
      clarify?: ClarifyInfo
      flights?: FlightInfo[]
      is_mocked?: boolean
    }
  ) {
    messages.value.push({
      id: generateId(),
      role: 'assistant',
      content,
      type,
      trip_info: extras?.trip_info,
      clarify: extras?.clarify,
      flights: extras?.flights,
      is_mocked: extras?.is_mocked,
      timestamp: new Date()
    })
  }

  // 发送消息
  async function send(content: string, selectedOption?: string) {
    if (isLoading.value) return

    // 添加用户消息
    if (!selectedOption) {
      addUserMessage(content)
    }

    isLoading.value = true
    currentClarify.value = null

    try {
      const response = await sendMessage(content, sessionId.value, selectedOption)

      // 更新会话ID
      sessionId.value = response.session_id

      // 更新行程信息
      if (response.trip_info) {
        tripInfo.value = response.trip_info
      }

      // 更新航班列表
      if (response.flights && response.flights.length > 0) {
        flights.value = response.flights
        isMocked.value = response.is_mocked
      }

      // 更新调试信息（Mock 数据）
      if (response.debug_info) {
        debugInfo.value = response.debug_info
      }

      // 处理澄清请求
      if (response.type === 'clarify' && response.clarify) {
        currentClarify.value = response.clarify
      }

      // 添加助手消息
      addAssistantMessage(response.message, response.type, {
        trip_info: response.trip_info,
        clarify: response.clarify,
        flights: response.flights,
        is_mocked: response.is_mocked
      })

    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || error.message || '请求失败，请重试'
      addAssistantMessage(errorMsg, 'error')
    } finally {
      isLoading.value = false
    }
  }

  // 选择澄清选项
  async function selectOption(option: { label: string; value: string }) {
    if (currentClarify.value) {
      addUserMessage(option.label)
      await send(option.value, option.value)
    }
  }

  // 重置对话
  function reset() {
    sessionId.value = ''
    messages.value = []
    tripInfo.value = null
    flights.value = []
    currentClarify.value = null
    isLoading.value = false
    isMocked.value = false
    debugInfo.value = null
  }

  return {
    // 状态
    sessionId,
    messages,
    tripInfo,
    flights,
    currentClarify,
    isLoading,
    isMocked,
    debugInfo,
    // 计算属性
    hasTrip,
    hasFlights,
    needsClarify,
    // 方法
    send,
    selectOption,
    reset
  }
})
