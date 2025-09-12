<template>
  <div class="demo-runner">
    <div class="header">
      <h1>Live Demo: {{ simulation?.name || id }}</h1>
      <router-link to="/sims" class="back-button">← Back to Simulations</router-link>
    </div>

    <div v-if="loading" class="loading">Loading simulation...</div>
    
    <div v-else-if="simulation" class="demo-content">
      <div class="demo-controls">
        <div class="control-group">
          <button 
            @click="runSteps"
            :disabled="simulation.status === 'running'"
            class="control-btn primary"
          >
            {{ simulation.status === 'running' ? 'Running...' : 'Run 10 Steps' }}
          </button>
          <button 
            @click="pauseDemo"
            :disabled="simulation.status !== 'running'"
            class="control-btn secondary"
          >
            Pause
          </button>
        </div>
        
        <div class="status-info">
          <span class="status-badge" :class="simulation.status">
            {{ simulation.status }}
          </span>
          <span class="step-info">
            Step: {{ simulationState?.step || simulation.current_step }}
          </span>
        </div>
      </div>

      <div class="demo-display">
        <div class="environment-panel">
          <h3>Environment</h3>
          <div v-if="simulationState" class="env-details">
            <p>Time: {{ simulationState.environment.time }}</p>
            <p>Weather: {{ simulationState.environment.weather }}</p>
            <div v-if="simulationState.environment.events.length" class="recent-events">
              <h4>Recent Events:</h4>
              <ul>
                <li v-for="event in simulationState.environment.events" :key="event">
                  {{ event }}
                </li>
              </ul>
            </div>
          </div>
        </div>

        <div class="agents-panel">
          <h3>Active Agents ({{ simulationState?.agents.length || 0 }})</h3>
          <div class="agents-grid">
            <div 
              v-for="agent in simulationState?.agents" 
              :key="agent.id"
              class="agent-card"
            >
              <div class="agent-header">
                <h4>{{ agent.name }}</h4>
                <div class="agent-location">
                  📍 {{ agent.location.area }}
                </div>
              </div>
              
              <p class="agent-persona">{{ agent.persona }}</p>
              <p class="agent-action">🎬 {{ agent.current_action }}</p>
              
              <div class="agent-emotions">
                <div 
                  v-for="(value, emotion) in agent.emotions" 
                  :key="emotion"
                  class="emotion-bar"
                >
                  <span class="emotion-label">{{ emotion }}</span>
                  <div class="emotion-progress">
                    <div 
                      class="emotion-fill" 
                      :style="{ width: `${value * 100}%` }"
                    ></div>
                  </div>
                  <span class="emotion-value">{{ Math.round(value * 100) }}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="demo-log">
        <h3>Activity Log</h3>
        <div class="log-entries">
          <div v-for="(log, index) in activityLog" :key="index" class="log-entry">
            <span class="log-time">{{ log.timestamp }}</span>
            <span class="log-message">{{ log.message }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { getSimulationState, runSimulation, pauseSimulation, createSimulationSocket } from '@/services/api'
import type { Simulation, SimulationState } from '@/types'

interface Props {
  id: string
}

const props = defineProps<Props>()

const simulation = ref<Simulation | null>(null)
const simulationState = ref<SimulationState | null>(null)
const loading = ref(true)
const activityLog = ref<Array<{timestamp: string, message: string}>>([])
let websocket: WebSocket | null = null

const loadSimulationState = async () => {
  try {
    simulationState.value = await getSimulationState(props.id)
    
    // Mock simulation object if not provided
    if (!simulation.value) {
      simulation.value = {
        id: props.id,
        name: `Demo ${props.id}`,
        base_id: 'demo',
        status: 'paused',
        created_at: new Date().toISOString(),
        current_step: simulationState.value.step
      }
    }
  } catch (error) {
    console.error('Failed to load simulation state:', error)
    addLog('Failed to load simulation state')
  } finally {
    loading.value = false
  }
}

const runSteps = async () => {
  if (!simulation.value) return
  
  try {
    simulation.value.status = 'running'
    await runSimulation(props.id, 10)
    addLog('Running 10 steps...')
    
    // Refresh state after running
    setTimeout(() => {
      loadSimulationState()
    }, 2000)
  } catch (error) {
    console.error('Failed to run simulation:', error)
    addLog('Failed to run simulation')
    if (simulation.value) simulation.value.status = 'paused'
  }
}

const pauseDemo = async () => {
  if (!simulation.value) return
  
  try {
    await pauseSimulation(props.id)
    simulation.value.status = 'paused'
    addLog('Simulation paused')
  } catch (error) {
    console.error('Failed to pause simulation:', error)
    addLog('Failed to pause simulation')
  }
}

const addLog = (message: string) => {
  activityLog.value.unshift({
    timestamp: new Date().toLocaleTimeString(),
    message
  })
  
  // Keep only last 20 log entries
  if (activityLog.value.length > 20) {
    activityLog.value = activityLog.value.slice(0, 20)
  }
}

const setupWebSocket = () => {
  try {
    websocket = createSimulationSocket(props.id)
    
    websocket.onopen = () => {
      addLog('Connected to live updates')
    }
    
    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.type === 'state_update') {
        simulationState.value = data.state
        addLog(`State updated: Step ${data.state.step}`)
      } else if (data.type === 'event') {
        addLog(data.message)
      }
    }
    
    websocket.onclose = () => {
      addLog('Disconnected from live updates')
    }
    
    websocket.onerror = () => {
      addLog('WebSocket connection error')
    }
  } catch (error) {
    console.warn('WebSocket not available:', error)
  }
}

onMounted(() => {
  loadSimulationState()
  setupWebSocket()
})

onUnmounted(() => {
  if (websocket) {
    websocket.close()
  }
})
</script>

<style scoped>
.demo-runner {
  max-width: 1400px;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.header h1 {
  color: #2c3e50;
}

.back-button {
  color: #42b883;
  text-decoration: none;
  font-weight: 500;
}

.back-button:hover {
  text-decoration: underline;
}

.loading {
  text-align: center;
  padding: 2rem;
  color: #666;
}

.demo-controls {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.control-group {
  display: flex;
  gap: 1rem;
}

.control-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.control-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.control-btn.primary {
  background: #42b883;
  color: white;
}

.control-btn.primary:hover:not(:disabled) {
  background: #369870;
}

.control-btn.secondary {
  background: #f59e0b;
  color: white;
}

.control-btn.secondary:hover:not(:disabled) {
  background: #d97706;
}

.status-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
}

.status-badge.created {
  background: #e0e7ff;
  color: #3730a3;
}

.status-badge.running {
  background: #dcfce7;
  color: #166534;
}

.status-badge.paused {
  background: #fef3c7;
  color: #92400e;
}

.step-info {
  font-weight: 500;
  color: #2c3e50;
}

.demo-display {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 2rem;
  margin-bottom: 2rem;
}

.environment-panel, .agents-panel {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.environment-panel h3, .agents-panel h3 {
  margin-top: 0;
  color: #2c3e50;
}

.env-details p {
  margin: 0.5rem 0;
  color: #666;
}

.recent-events {
  margin-top: 1rem;
}

.recent-events ul {
  margin: 0.5rem 0;
  padding-left: 1.5rem;
}

.agents-grid {
  display: grid;
  gap: 1rem;
}

.agent-card {
  background: #f9f9f9;
  padding: 1rem;
  border-radius: 6px;
  border: 1px solid #e0e0e0;
}

.agent-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.agent-header h4 {
  margin: 0;
  color: #2c3e50;
}

.agent-location {
  font-size: 0.75rem;
  color: #666;
}

.agent-persona, .agent-action {
  font-size: 0.875rem;
  margin: 0.25rem 0;
}

.agent-persona {
  font-style: italic;
  color: #666;
}

.agent-emotions {
  margin-top: 0.75rem;
}

.emotion-bar {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0.25rem 0;
}

.emotion-label {
  font-size: 0.75rem;
  min-width: 60px;
  color: #666;
}

.emotion-progress {
  flex: 1;
  height: 8px;
  background: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}

.emotion-fill {
  height: 100%;
  background: #42b883;
  transition: width 0.3s ease;
}

.emotion-value {
  font-size: 0.75rem;
  min-width: 30px;
  text-align: right;
  color: #666;
}

.demo-log {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.demo-log h3 {
  margin-top: 0;
  color: #2c3e50;
}

.log-entries {
  max-height: 200px;
  overflow-y: auto;
}

.log-entry {
  display: flex;
  gap: 1rem;
  padding: 0.5rem 0;
  border-bottom: 1px solid #f0f0f0;
  font-size: 0.875rem;
}

.log-time {
  color: #666;
  min-width: 80px;
}

.log-message {
  flex: 1;
}
</style>