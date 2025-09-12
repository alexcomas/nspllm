<template>
  <div class="simulations">
    <div class="header">
      <h1>Simulations</h1>
      <button @click="createNewSim" class="create-button">
        Create New Simulation
      </button>
    </div>

    <div v-if="loading" class="loading">Loading simulations...</div>
    
    <div v-else class="simulation-grid">
      <div 
        v-for="sim in simulations" 
        :key="sim.id" 
        class="simulation-card"
        :class="{ running: sim.status === 'running' }"
      >
        <div class="sim-header">
          <h3>{{ sim.name }}</h3>
          <span class="status-badge" :class="sim.status">{{ sim.status }}</span>
        </div>
        
        <div class="sim-details">
          <p>Base: {{ sim.base_id }}</p>
          <p>Step: {{ sim.current_step }}{{ sim.total_steps ? `/${sim.total_steps}` : '' }}</p>
          <p>Created: {{ formatDate(sim.created_at) }}</p>
        </div>
        
        <div class="sim-actions">
          <button 
            v-if="sim.status === 'paused' || sim.status === 'created'" 
            @click="runSim(sim.id)"
            class="action-btn run"
          >
            Run
          </button>
          <button 
            v-if="sim.status === 'running'" 
            @click="pauseSim(sim.id)"
            class="action-btn pause"
          >
            Pause
          </button>
          <router-link 
            :to="`/demo/${sim.id}`" 
            class="action-btn demo"
          >
            Demo
          </router-link>
          <router-link 
            :to="`/replay/${sim.id}`" 
            class="action-btn replay"
          >
            Replay
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getSimulations, createSimulation, runSimulation, pauseSimulation } from '@/services/api'
import type { Simulation } from '@/types'

const simulations = ref<Simulation[]>([])
const loading = ref(true)

const loadSimulations = async () => {
  try {
    simulations.value = await getSimulations()
  } catch (error) {
    console.error('Failed to load simulations:', error)
  } finally {
    loading.value = false
  }
}

const createNewSim = async () => {
  try {
    const sim = await createSimulation('base_the_ville_isabella_maria_klaus')
    simulations.value.unshift(sim)
  } catch (error) {
    console.error('Failed to create simulation:', error)
  }
}

const runSim = async (id: string) => {
  try {
    await runSimulation(id, 10)
    // Update simulation status in the list
    const sim = simulations.value.find(s => s.id === id)
    if (sim) sim.status = 'running'
  } catch (error) {
    console.error('Failed to run simulation:', error)
  }
}

const pauseSim = async (id: string) => {
  try {
    await pauseSimulation(id)
    // Update simulation status in the list
    const sim = simulations.value.find(s => s.id === id)
    if (sim) sim.status = 'paused'
  } catch (error) {
    console.error('Failed to pause simulation:', error)
  }
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString()
}

onMounted(() => {
  loadSimulations()
})
</script>

<style scoped>
.simulations {
  max-width: 1200px;
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

.create-button {
  padding: 0.75rem 1.5rem;
  background: #42b883;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.2s;
}

.create-button:hover {
  background: #369870;
}

.loading {
  text-align: center;
  padding: 2rem;
  color: #666;
}

.simulation-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.simulation-card {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.2s;
}

.simulation-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.simulation-card.running {
  border-color: #42b883;
  background: #f0fff4;
}

.sim-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.sim-header h3 {
  margin: 0;
  color: #2c3e50;
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

.status-badge.completed {
  background: #f3f4f6;
  color: #374151;
}

.status-badge.error {
  background: #fee2e2;
  color: #991b1b;
}

.sim-details {
  margin-bottom: 1rem;
}

.sim-details p {
  margin: 0.25rem 0;
  color: #666;
  font-size: 0.875rem;
}

.sim-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
  text-decoration: none;
  text-align: center;
  transition: all 0.2s;
}

.action-btn.run {
  background: #22c55e;
  color: white;
}

.action-btn.run:hover {
  background: #16a34a;
}

.action-btn.pause {
  background: #f59e0b;
  color: white;
}

.action-btn.pause:hover {
  background: #d97706;
}

.action-btn.demo {
  background: #3b82f6;
  color: white;
}

.action-btn.demo:hover {
  background: #2563eb;
}

.action-btn.replay {
  background: #ef4444;
  color: white;
}

.action-btn.replay:hover {
  background: #dc2626;
}
</style>