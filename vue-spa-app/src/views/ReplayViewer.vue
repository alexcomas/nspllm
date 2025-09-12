<template>
  <div class="replay-viewer">
    <div class="header">
      <h1>Replay: {{ replay?.name || id }}</h1>
      <router-link to="/sims" class="back-button">← Back to Simulations</router-link>
    </div>

    <div v-if="loading" class="loading">Loading replay...</div>
    
    <div v-else-if="replay" class="replay-content">
      <div class="replay-controls">
        <button @click="playPause" class="control-btn">
          {{ isPlaying ? '⏸️' : '▶️' }}
        </button>
        <button @click="stepBackward" class="control-btn">⏮️</button>
        <button @click="stepForward" class="control-btn">⏭️</button>
        
        <div class="timeline">
          <input 
            v-model="currentFrame" 
            type="range" 
            :min="0" 
            :max="replay.frames.length - 1"
            class="timeline-slider"
          />
          <span class="frame-info">
            Frame {{ currentFrame + 1 }} / {{ replay.frames.length }}
          </span>
        </div>
      </div>

      <div class="replay-display">
        <div class="environment-info">
          <h3>Environment</h3>
          <p>Time: {{ currentFrameData?.timestamp }}</p>
          <p>Step: {{ currentFrameData?.step }}</p>
          <div v-if="currentFrameData?.events.length" class="events">
            <h4>Events:</h4>
            <ul>
              <li v-for="event in currentFrameData.events" :key="event">{{ event }}</li>
            </ul>
          </div>
        </div>

        <div class="agents-display">
          <h3>Agents ({{ currentFrameData?.agents.length || 0 }})</h3>
          <div class="agents-grid">
            <div 
              v-for="agent in currentFrameData?.agents" 
              :key="agent.id"
              class="agent-card"
            >
              <h4>{{ agent.name }}</h4>
              <p class="persona">{{ agent.persona }}</p>
              <p class="location">
                <span v-if="agent.location.area && agent.location.area !== ''">📍 {{ agent.location.area }} </span>
                <span>(x: {{ agent.location.x }}, y: {{ agent.location.y }})</span>
              </p>
              <p class="action"><strong>🎬 {{ agent.current_action }}</strong></p>
              <div class="emotions">
                <span 
                  v-for="(value, emotion) in agent.emotions" 
                  :key="emotion"
                  class="emotion-badge"
                  :style="{ opacity: value }"
                >
                  {{ emotion }}: {{ Math.round(value * 100) }}%
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="replay-metadata">
        <h3>Replay Information</h3>
        <p>Duration: {{ replay.metadata.duration_seconds }}s</p>
        <p>Total Steps: {{ replay.metadata.total_steps }}</p>
        <p>Agents: {{ replay.metadata.agent_count }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { getReplay } from '@/services/api'
import type { Replay, ReplayFrame } from '@/types'

interface Props {
  id: string
}

const props = defineProps<Props>()

const replay = ref<Replay | null>(null)
const loading = ref(true)
const currentFrame = ref(0)
const isPlaying = ref(false)
let playInterval: number

const currentFrameData = computed((): ReplayFrame | null => {
  return replay.value?.frames[currentFrame.value] || null
})

const loadReplay = async () => {
  try {
    replay.value = await getReplay(props.id)
  } catch (error) {
    console.error('Failed to load replay:', error)
  } finally {
    loading.value = false
  }
}

const playPause = () => {
  isPlaying.value = !isPlaying.value
}

const stepForward = () => {
  if (replay.value && currentFrame.value < replay.value.frames.length - 1) {
    currentFrame.value++
  }
}

const stepBackward = () => {
  if (currentFrame.value > 0) {
    currentFrame.value--
  }
}

// Auto-play functionality
watch(isPlaying, (playing) => {
  if (playing) {
    playInterval = setInterval(() => {
      if (replay.value && currentFrame.value < replay.value.frames.length - 1) {
        currentFrame.value++
      } else {
        isPlaying.value = false
      }
    }, 1000) // 1 frame per second
  } else {
    if (playInterval) clearInterval(playInterval)
  }
})

onMounted(() => {
  loadReplay()
})

onUnmounted(() => {
  if (playInterval) clearInterval(playInterval)
})
</script>

<style scoped>
.replay-viewer {
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

.replay-controls {
  background: white;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 2rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.control-btn {
  padding: 0.5rem;
  background: #42b883;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1.2rem;
}

.control-btn:hover {
  background: #369870;
}

.timeline {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.timeline-slider {
  flex: 1;
}

.frame-info {
  font-size: 0.875rem;
  color: #666;
  white-space: nowrap;
}

.replay-display {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 2rem;
  margin-bottom: 2rem;
}

.environment-info {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.environment-info h3 {
  margin-top: 0;
  color: #2c3e50;
}

.events {
  margin-top: 1rem;
}

.events ul {
  margin: 0.5rem 0;
  padding-left: 1.5rem;
}

.agents-display {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.agents-display h3 {
  margin-top: 0;
  color: #2c3e50;
}

.agents-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
}

.agent-card {
  background: #f9f9f9;
  padding: 1rem;
  border-radius: 6px;
  border: 1px solid #e0e0e0;
}

.agent-card h4 {
  margin: 0 0 0.5rem 0;
  color: #2c3e50;
}

.persona {
  font-style: italic;
  color: #666;
  font-size: 0.875rem;
  margin: 0.25rem 0;
}

.location, .action {
  font-size: 0.875rem;
  margin: 0.25rem 0;
}

.emotions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
  margin-top: 0.5rem;
}

.emotion-badge {
  padding: 0.125rem 0.5rem;
  background: #42b883;
  color: white;
  border-radius: 12px;
  font-size: 0.75rem;
}

.replay-metadata {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.replay-metadata h3 {
  margin-top: 0;
  color: #2c3e50;
}
</style>