import axios from 'axios'
import type { Simulation, SimulationState, Replay, HealthStatus } from '@/types'

// Determine API base URL precedence:
// 1. VITE_API_BASE_URL (new preferred)
// 2. VITE_API_BASE (legacy)
// 3. If running dev on :5173 and no env var, force explicit 127.0.0.1 to avoid localhost origin confusion
// 4. Fallback to relative '/api' (works in production when served behind same host)
const explicitEnvBase = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_BASE
let resolvedBase: string
if (explicitEnvBase) {
  resolvedBase = explicitEnvBase.replace(/\/$/, '') // trim trailing slash
} else if (window.location.port === '5173') {
  // Dev fallback if not explicitly configured
  resolvedBase = 'http://127.0.0.1:8000/api'
} else {
  // Production / same-origin fallback
  resolvedBase = '/api'
}

const api = axios.create({
  baseURL: resolvedBase,
  timeout: 120*1000,
  withCredentials: true,
})

// Debug interceptors (can be toggled off later)
api.interceptors.request.use(cfg => {
  // eslint-disable-next-line no-console
  const method = (cfg.method || 'GET').toUpperCase()
  const fullUrl = `${cfg.baseURL || ''}${cfg.url || ''}`
  console.debug('[api][request]', method, fullUrl)
  return cfg
})
api.interceptors.response.use(
  resp => resp,
  err => {
    // eslint-disable-next-line no-console
    const eCfg = err.config || {}
    const fullUrl = `${eCfg.baseURL || ''}${eCfg.url || ''}`
    console.error('[api][error]', err.message, {
      url: fullUrl,
      status: err.response?.status,
      data: err.response?.data,
    })
    return Promise.reject(err)
  }
)

export const API_BASE = resolvedBase

// Health check
export const getHealth = async (): Promise<HealthStatus> => {
  return null
  const response = await api.get('/health/')
  return response.data
}

// Simulations
export const getSimulations = async (): Promise<Simulation[]> => {
  const response = await api.get('/simulations/')
  return response.data
}

export const createSimulation = async (baseId: string): Promise<Simulation> => {
  const response = await api.post('/simulations/', { base_id: baseId })
  return response.data
}

export const runSimulation = async (id: string, steps: number): Promise<void> => {
  await api.post(`/simulations/${id}/run/`, { steps })
}

export const pauseSimulation = async (id: string): Promise<void> => {
  await api.post(`/simulations/${id}/pause/`)
}

export const getSimulationState = async (id: string): Promise<SimulationState> => {
  const response = await api.get(`/simulations/${id}/state/`)
  return response.data
}

// Replays
export const getReplay = async (id: string): Promise<Replay> => {
  const response = await api.get(`/replays/${id}/`)
  return response.data
}

// WebSocket connection for live updates
export const createSimulationSocket = (id: string) => {
  const wsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws/simulations/${id}`
  return new WebSocket(wsUrl)
}
