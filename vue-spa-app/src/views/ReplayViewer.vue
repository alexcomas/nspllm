<template>
  <div class="replay-viewer">
    <div class="header">
      <h1>Replay: {{ replay?.name || id }}</h1>
      <router-link to="/sims" class="back-button">← Back to Simulations</router-link>
    </div>

    <div v-if="loading" class="loading">
      <div class="progress-wrapper">
        <div class="progress-label">Loading replay ({{ Math.min(100, Math.round(loadProgress)) }}%)</div>
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: Math.min(100, loadProgress) + '%' }"></div>
        </div>
        <div class="progress-eta" v-if="loadProgress < 100">ETA ~ {{ remainingSeconds }}s</div>
      </div>
    </div>
    
    <div v-else-if="replay" class="replay-content">
      <div class="replay-controls">
        <button @click="playPause" class="control-btn">
          {{ isPlaying ? '⏸️' : '▶️' }}
        </button>
        <button @click="stepBackward" class="control-btn">⏮️</button>
        <button @click="stepForward" class="control-btn">⏭️</button>

        <div class="velocity-control">
          <label for="velocity" class="velocity-label">Speed:</label>
          <select id="velocity" v-model.number="playbackSpeed" class="velocity-select">
            <option :value="0.25">0.25x</option>
            <option :value="0.5">0.5x</option>
            <option :value="1">1x</option>
            <option :value="2">2x</option>
            <option :value="4">4x</option>
          </select>
        </div>

        <div class="timeline">
          <input 
            v-model.number="currentFrame" 
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
        <!-- Left sidebar: Agents list in one column -->
        <div class="agents-sidebar">
          <h3>Agents ({{ currentFrameData?.agents.length || 0 }})</h3>
          <div class="agents-list">
            <div
              v-for="agent in currentFrameData?.agents"
              :key="agent.id"
              class="agent-card-compact"
              @click="focusAgent(agent.id)"
              :style="{ cursor: usePhaser ? 'pointer' : undefined }"
            >
              <h4>{{ agent.name }}</h4>
              <p class="location">
                <span v-if="agent.location.area && agent.location.area !== ''">📍 {{ agent.location.area }}</span>
                <span class="coords">({{ agent.location.x }}, {{ agent.location.y }})</span>
              </p>
              <p class="action">🎬 {{ agent.current_action }}</p>
            </div>
          </div>
        </div>

        <!-- Main area: Map -->
        <div class="visual-pane">
          <div class="visual-header">
            <h3>Spatial Replay</h3>
            <label>
              <input type="checkbox" v-model="usePhaser" />
              Use Phaser (tilemap/assets)
            </label>
          </div>
          <div class="map-container">
            <component
              :is="usePhaser ? PhaserReplay : ReplayMap"
              v-if="currentFrameData"
              :replay="replay"
              :frameIndex="currentFrame"
              :frame="currentFrameData"
              :focusedAgentId="usePhaser ? focusedAgentId : undefined"
              ref="phaserReplayRef"
            />
          </div>
        </div>
      </div>

      <!-- Bottom area: Environment info and detailed agent info -->
      <div class="details-section">
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
        
        <div class="detailed-agents">
          <h3>Agent Details</h3>
          <div class="agents-grid-detailed">
            <div
              v-for="agent in currentFrameData?.agents"
              :key="agent.id"
              class="agent-card-detailed"
              @click="focusAgent(agent.id)"
              :style="{ cursor: usePhaser ? 'pointer' : undefined }"
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
// (removed duplicate focus agent logic)
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { getReplay } from '@/services/api'
import type { Replay, ReplayFrame } from '@/types'
import ReplayMap from '@/components/ReplayMap.vue'
import PhaserReplay from '@/components/PhaserReplay.vue'
// Toggle for Phaser/DOM map
const usePhaser = ref(true)

// --- FOCUS AGENT CAMERA LOGIC ---
const phaserReplayRef = ref<any>(null)
const focusedAgentId = ref<string | null>(null)
function focusAgent(agentId: string) {
  if (usePhaser.value) {
    focusedAgentId.value = agentId
    // Call exposed method to re-enable camera follow
    phaserReplayRef.value?.focusAgent?.()
  }
}

interface Props {
  id: string
}

const props = defineProps<Props>()

const replay = ref<Replay | null>(null)
const loading = ref(true) // overall loading gate for template
const loadProgress = ref(0) // 0 - 100 simulated
const targetDurationMs = 120000
// Use ReturnType<typeof setInterval> to be compatible with both browser & Node typings
let progressInterval: ReturnType<typeof setInterval> | null = null
const remainingSeconds = computed(() => {
  if (loadProgress.value >= 100) return 0
  const frac = loadProgress.value / 100
  const elapsed = targetDurationMs * frac
  const remainMs = Math.max(0, targetDurationMs - elapsed)
  return Math.ceil(remainMs / 1000)
})
const currentFrame = ref(0)

const isPlaying = ref(false)
const playbackSpeed = ref(1)
let playInterval: ReturnType<typeof setInterval> | null = null

const currentFrameData = computed((): ReplayFrame | null => {
  return replay.value?.frames[currentFrame.value] || null
})

const loadReplay = async () => {
  try {
    replay.value = await getReplay(props.id)
  } catch (error) {
    console.error('Failed to load replay:', error)
  } finally {
    // Immediately finish loading UI
    loadProgress.value = 100
    if (progressInterval) {
      clearInterval(progressInterval)
      progressInterval = null
    }
    // Short timeout lets the bar visually snap to 100% before removal
    setTimeout(() => { loading.value = false }, 100)
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
watch([isPlaying, playbackSpeed], ([playing, speed]) => {
  if (playInterval) clearInterval(playInterval)
  if (playing) {
    playInterval = setInterval(() => {
      if (replay.value && currentFrame.value < replay.value.frames.length - 1) {
        currentFrame.value++
      } else {
        isPlaying.value = false
      }
    }, 1000 / speed)
  }
})

onMounted(() => {
  // Simulated progress ramp: update every 300ms using ease-out curve
  const start = performance.now()
  progressInterval = setInterval(() => {
    const elapsed = performance.now() - start
    const t = Math.min(1, elapsed / targetDurationMs)
    // Ease-out (quadratic)
    loadProgress.value = t * (2 - t) * 100
    if (t >= 1) {
      if (progressInterval) {
        clearInterval(progressInterval)
        progressInterval = null
      }
      // If data already fetched earlier we'll already be transitioning out.
    }
  }, 300)
  loadReplay()
})

onUnmounted(() => {
  if (playInterval) clearInterval(playInterval)
  if (progressInterval) clearInterval(progressInterval)
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

.progress-wrapper {
  max-width: 480px;
  margin: 0 auto;
  background: #fff;
  border: 1px solid #e2e2e2;
  padding: 1.25rem 1.5rem 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.06);
}

.progress-label {
  font-size: 0.95rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 0.5rem;
  text-align: left;
}

.progress-bar {
  position: relative;
  width: 100%;
  height: 14px;
  background: linear-gradient(90deg,#f5f7fa,#eef1f5);
  border-radius: 7px;
  overflow: hidden;
  border: 1px solid #d8dfe6;
  margin-bottom: 0.5rem;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg,#42b883,#2fa36e);
  transition: width 0.28s cubic-bezier(.4,.0,.2,1);
  box-shadow: inset 0 0 4px rgba(255,255,255,0.5);
}

.progress-eta {
  font-size: 0.75rem;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  color: #888;
  text-align: right;
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
  grid-template-columns: 250px 1fr; /* Narrow left sidebar, wide main area */
  gap: 1rem;
  margin-bottom: 1rem;
}

.agents-sidebar {
  background: white;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  max-height: 600px;
  overflow-y: auto;
}

.agents-sidebar h3 {
  margin-top: 0;
  margin-bottom: 1rem;
  color: #2c3e50;
  font-size: 1rem;
}

.agents-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.agent-card-compact {
  background: #f9f9f9;
  padding: 0.75rem;
  border-radius: 6px;
  border: 1px solid #e0e0e0;
  cursor: pointer;
  transition: background-color 0.2s;
}

.agent-card-compact:hover {
  background: #f0f0f0;
}

.agent-card-compact h4 {
  margin: 0 0 0.25rem 0;
  color: #2c3e50;
  font-size: 0.9rem;
}

.agent-card-compact .location,
.agent-card-compact .action {
  font-size: 0.75rem;
  margin: 0.125rem 0;
  color: #666;
}

.agent-card-compact .coords {
  color: #888;
  font-size: 0.7rem;
}

.visual-pane {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  height: 600px;
  display: flex;
  flex-direction: column;
}

.visual-pane h3 {
  margin-top: 0;
  color: #2c3e50;
}

.visual-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.5rem;
  flex-shrink: 0;
}

.visual-header h3 {
  margin: 0;
}

.visual-header label {
  font-size: 0.95rem;
}

.visual-header input[type="checkbox"] {
  vertical-align: middle;
  margin-right: 0.4em;
}

.map-container {
  flex: 1;
  min-height: 0;
}

.details-section {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 1rem;
  margin-bottom: 2rem;
}

.environment-info {
  background: white;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  max-height: 300px;
}

.environment-info h3 {
  margin-top: 0;
  color: #2c3e50;
  font-size: 1rem;
}

.detailed-agents {
  background: white;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  max-height: 300px;
  overflow-y: auto;
}

.detailed-agents h3 {
  margin-top: 0;
  margin-bottom: 1rem;
  color: #2c3e50;
  font-size: 1rem;
}

.agents-grid-detailed {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 0.75rem;
}

.agent-card-detailed {
  background: #f9f9f9;
  padding: 0.75rem;
  border-radius: 6px;
  border: 1px solid #e0e0e0;
  cursor: pointer;
  transition: background-color 0.2s;
}

.agent-card-detailed:hover {
  background: #f0f0f0;
}

.agent-card-detailed h4 {
  margin: 0 0 0.25rem 0;
  color: #2c3e50;
  font-size: 0.9rem;
}

.persona {
  font-style: italic;
  color: #666;
  font-size: 0.75rem;
  margin: 0.125rem 0;
}

.location, .action {
  font-size: 0.75rem;
  margin: 0.125rem 0;
}

.emotions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.125rem;
  margin-top: 0.25rem;
}

.emotion-badge {
  padding: 0.0625rem 0.25rem;
  background: #42b883;
  color: white;
  border-radius: 8px;
  font-size: 0.625rem;
}

.replay-metadata {
  background: white;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.replay-metadata h3 {
  margin-top: 0;
  color: #2c3e50;
  font-size: 1rem;
}

/* Responsive design */
@media (max-width: 1024px) {
  .replay-display {
    grid-template-columns: 200px 1fr;
  }
  
  .details-section {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .agents-grid-detailed {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  }
}

@media (max-width: 768px) {
  .replay-display {
    grid-template-columns: 1fr;
  }
  
  .agents-sidebar {
    max-height: 200px;
  }
}
/* Velocity control styles */
.velocity-control {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: #f9f9f9;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 0.5rem 1rem;
  margin-right: 1.5rem;
  margin-left: 0.5rem;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
  height: 2.5rem;
}
.velocity-label {
  font-size: 0.98rem;
  color: #2c3e50;
  font-weight: 500;
  margin-right: 0.25rem;
}
.velocity-select {
  padding: 0.35rem 1.2rem 0.35rem 0.7rem;
  border-radius: 6px;
  border: 1px solid #cfd8dc;
  font-size: 1.05rem;
  background: #fff;
  color: #2c3e50;
  box-shadow: 0 1px 2px rgba(0,0,0,0.03);
  transition: border 0.2s, box-shadow 0.2s;
}
.velocity-select:focus {
  outline: none;
  border: 1.5px solid #42b883;
  box-shadow: 0 0 0 2px #42b88322;
}
</style>