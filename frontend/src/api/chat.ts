import axios from 'axios'
import type { ChatResponse } from '../types'

// API 基础配置
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
  timeout: 60000, // LLM 调用可能较慢
  headers: {
    'Content-Type': 'application/json'
  }
})

// 发送对话消息
export async function sendMessage(
  message: string,
  sessionId?: string,
  selectedOption?: string
): Promise<ChatResponse> {
  const response = await api.post<ChatResponse>('/chat', {
    session_id: sessionId,
    message,
    selected_option: selectedOption
  })
  return response.data
}

// 获取会话信息
export async function getSession(sessionId: string) {
  const response = await api.get(`/session/${sessionId}`)
  return response.data
}

// 创建新会话
export async function createSession() {
  const response = await api.post<{ session_id: string }>('/session/new')
  return response.data
}

export default api
