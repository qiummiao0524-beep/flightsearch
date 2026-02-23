// 类型定义

export interface AirportInfo {
  city: string
  code: string
  name?: string
}

export interface PassengerInfo {
  type: 'ADT' | 'CHD' | 'INF'
  count: number
}

export interface TripInfo {
  travel_type: 'OW' | 'RT' | 'OJ'
  departure?: AirportInfo
  arrival?: AirportInfo
  dep_date?: string
  return_date?: string
  passengers: PassengerInfo[]
  cabin_class: string
  cabin_name?: string
  airline_code?: string
  flight_no?: string
}

export interface ClarifyOption {
  label: string
  value: string
}

export interface ClarifyInfo {
  field: string
  question: string
  options: ClarifyOption[]
}

export interface FlightSegment {
  sequence: number
  flight_no: string
  airline: {
    code: string
    name: string
  }
  departure: {
    code: string
    city: string
    name: string
    terminal: string
    time: string
  }
  arrival: {
    code: string
    city: string
    name: string
    terminal: string
    time: string
  }
  duration: string
  equip?: string
  is_transfer: boolean
}

export interface FlightInfo {
  id: string
  type: string
  travel_type: 'OW' | 'RT'
  segments: FlightSegment[]
  is_transfer: boolean
  cabin_class: string
  cabin_num?: string
  price: {
    total: string
    base: string
    tax: string
    currency: string
  }
  services: string[]
  labels: any[]
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  type?: 'clarify' | 'result' | 'searching' | 'mocking' | 'error' | 'progress'
  trip_info?: TripInfo
  clarify?: ClarifyInfo
  flights?: FlightInfo[]
  is_mocked?: boolean
  timestamp: Date
  progressStatus?: string
}

export interface DebugInfo {
  mock_request?: Record<string, any>
  search_response?: Record<string, any>
}

export interface ChatResponse {
  session_id: string
  type: 'clarify' | 'result' | 'searching' | 'mocking' | 'error'
  message: string
  trip_info?: TripInfo
  clarify?: ClarifyInfo
  flights: FlightInfo[]
  is_mocked: boolean
  debug_info?: DebugInfo
}
