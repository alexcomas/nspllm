<template>
  <div class="home">
    <div class="hero">
      <h1>NSPLLM Generative Agents</h1>
      <p class="subtitle">
        Interactive simulacra of human behavior with cognitive modules for planning, 
        perceiving, conversing, and reflecting.
      </p>
      
      <div class="quick-actions">
        <router-link to="/sims" class="action-button primary">
          View Simulations
        </router-link>
        <button @click="createDemo" class="action-button secondary">
          Quick Demo
        </button>
      </div>
    </div>

    <div class="features">
      <div class="feature-card">
        <h3>🧠 Cognitive Modules</h3>
        <p>Agents with planning, perception, conversation, and reflection capabilities</p>
      </div>
      
      <div class="feature-card">
        <h3>🎬 Replay System</h3>
        <p>Record and playback agent interactions for analysis</p>
      </div>
      
      <div class="feature-card">
        <h3>🎮 Live Demos</h3>
        <p>Interactive demonstrations of agent behavior</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { createSimulation } from '@/services/api'

const router = useRouter()

const createDemo = async () => {
  try {
    const sim = await createSimulation('demo')
    router.push(`/demo/${sim.id}`)
  } catch (error) {
    console.error('Failed to create demo:', error)
    // TODO: Show error toast
  }
}
</script>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
}

.hero {
  text-align: center;
  padding: 4rem 0;
}

.hero h1 {
  font-size: 3rem;
  margin-bottom: 1rem;
  background: linear-gradient(135deg, #42b883 0%, #35495e 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  font-size: 1.25rem;
  color: #666;
  max-width: 600px;
  margin: 0 auto 2rem;
  line-height: 1.6;
}

.quick-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.action-button {
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.2s;
  border: none;
  cursor: pointer;
  font-size: 1rem;
}

.action-button.primary {
  background: #42b883;
  color: white;
}

.action-button.primary:hover {
  background: #369870;
}

.action-button.secondary {
  background: transparent;
  color: #42b883;
  border: 2px solid #42b883;
}

.action-button.secondary:hover {
  background: #42b883;
  color: white;
}

.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-top: 4rem;
}

.feature-card {
  padding: 2rem;
  border-radius: 12px;
  background: #f9f9f9;
  border: 1px solid #e0e0e0;
}

.feature-card h3 {
  margin-bottom: 1rem;
  color: #2c3e50;
}

.feature-card p {
  color: #666;
  line-height: 1.6;
}
</style>