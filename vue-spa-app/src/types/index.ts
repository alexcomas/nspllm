export interface HealthStatus {
  env_server: boolean
  sim_server: boolean
  timestamp: string
}

export interface Simulation {
  id: string
  name: string
  base_id: string
  status: 'created' | 'running' | 'paused' | 'completed' | 'error'
  created_at: string
  current_step: number
  total_steps?: number
}

export interface Agent {
  id: string
  name: string
  persona: string
  location: {
    x: number
    y: number
    area: string
  }
  current_action: string
  emotions: Record<string, number>
}

export interface SimulationState {
  step: number
  agents: Agent[]
  environment: {
    time: string
    weather: string
    events: string[]
  }
}

export interface ReplayFrame {
  step: number
  timestamp: string
  agents: Agent[]
  events: string[]
}

export interface Replay {
  id: string
  simulation_id: string
  name: string
  frames: ReplayFrame[]
  metadata: {
    total_steps: number
    duration_seconds: number
    agent_count: number
  }
}