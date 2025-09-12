import axios from 'axios'
import type { Simulation, SimulationState, Replay, HealthStatus } from '@/types'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || '/api',
  timeout: 30000,
})

// Health check
export const getHealth = async (): Promise<HealthStatus> => {
  const response = await api.get('/health')
  return response.data
}

// Simulations
export const getSimulations = async (): Promise<Simulation[]> => {
  const response = await api.get('/simulations')
  return response.data
}

export const createSimulation = async (baseId: string): Promise<Simulation> => {
  const response = await api.post('/simulations', { base_id: baseId })
  return response.data
}

export const runSimulation = async (id: string, steps: number): Promise<void> => {
  await api.post(`/simulations/${id}/run`, { steps })
}

export const pauseSimulation = async (id: string): Promise<void> => {
  await api.post(`/simulations/${id}/pause`)
}

export const getSimulationState = async (id: string): Promise<SimulationState> => {
  const response = await api.get(`/simulations/${id}/state`)
  return response.data
}

// Replays
export const getReplay = async (id: string): Promise<Replay> => {
  const response = await api.get(`/replays/${id}`)
  return response.data
}

// WebSocket connection for live updates
export const createSimulationSocket = (id: string) => {
  const wsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws/simulations/${id}`
  return new WebSocket(wsUrl)
}
