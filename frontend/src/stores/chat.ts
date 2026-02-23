import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { ChatMessage, TripInfo, FlightInfo, ClarifyInfo, DebugInfo } from '../types'

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
  const currentProgress = ref<string>('')

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

  // 发送消息 (进度内嵌版 — 进度节点持久化保留在消息中)
  async function send(content: string, selectedOption?: string) {
    if (isLoading.value) return

    // 添加用户消息
    if (!selectedOption) {
      addUserMessage(content)
    }

    isLoading.value = true
    currentProgress.value = 'UNDERSTANDING'
    currentClarify.value = null

    // 立即创建一条助手消息用于展示进度（后续就地更新）
    const progressMsgId = generateId()
    messages.value.push({
      id: progressMsgId,
      role: 'assistant',
      content: '',
      type: 'progress' as any,
      timestamp: new Date(),
      progressStatus: 'UNDERSTANDING'
    })

    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          session_id: sessionId.value,
          message: content,
          selected_option: selectedOption
        })
      })

      if (!response.ok) throw new Error('网络请求失败')
      if (!response.body) throw new Error('响应正文为空')

      const reader = response.body.getReader()
      const decoder = new TextDecoder()

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value, { stream: true })
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = JSON.parse(line.substring(6))

            if (data.type === 'progress') {
              currentProgress.value = data.status
              // 就地更新进度消息的状态
              const idx = messages.value.findIndex(m => m.id === progressMsgId)
              if (idx !== -1) {
                const updatedMsg = {
                  ...messages.value[idx],
                  progressStatus: data.status
                }

                // 只在理解意图完成时，提取信息文本并展示。避免后期搜索/Mock的系统话术覆盖它
                if (data.status === 'UNDERSTANDING_DONE' && data.message) {
                  updatedMsg.content = data.message
                }

                messages.value[idx] = updatedMsg
              }
            } else if (data.type === 'final') {
              // 更新会话ID
              sessionId.value = data.session_id

              // 更新行程信息
              if (data.trip_info) {
                tripInfo.value = data.trip_info
              }

              // 更新航班列表
              if (data.flights && data.flights.length > 0) {
                flights.value = data.flights
                isMocked.value = data.is_mocked
              }

              // 更新调试信息
              if (data.debug_info) {
                debugInfo.value = data.debug_info
              }

              // 处理澄清请求
              if (data.response_type === 'clarify' && data.clarify) {
                currentClarify.value = data.clarify
              }

              // 就地更新同一条消息：保留进度步骤，追加回复文本
              currentProgress.value = 'DONE'
              const idx = messages.value.findIndex(m => m.id === progressMsgId)
              if (idx !== -1) {
                messages.value[idx] = {
                  ...messages.value[idx],
                  content: data.message,
                  type: data.response_type,
                  trip_info: data.trip_info,
                  clarify: data.clarify,
                  flights: data.flights,
                  is_mocked: data.is_mocked,
                  progressStatus: 'DONE'
                }
              }
            } else if (data.type === 'error') {
              throw new Error(data.message)
            }
          }
        }
      }

    } catch (error: any) {
      const errorMsg = error.message || '请求失败，请重试'
      currentProgress.value = 'ERROR'
      const idx = messages.value.findIndex(m => m.id === progressMsgId)
      if (idx !== -1) {
        messages.value[idx] = {
          ...messages.value[idx],
          content: errorMsg,
          type: 'error',
          progressStatus: 'ERROR'
        }
      }
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
    currentProgress.value = ''
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
    currentProgress,
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
