<template>
  <div class="replay-viewer">
    <div class="header">
      <h1>Replay: {{ replay?.name || id }}</h1>
      <router-link to="/sims" class="back-button">← Back to Simulations</router-link>
    </div>

    <div v-if="loading" class="loading">
      <div class="progress-wrapper">
        <div class="progress-label">Loading replay ({{ Math.min(100, Math.round(loadProgress)) }}%)</div>
        <div
          class="progress-bar"
          style="position: relative;"
          @click="onProgressBarClick($event)"
        >
          <div class="progress-fill" :style="{ width: Math.min(100, loadProgress) + '%' }"></div>
          <!-- Timeline markers for end of long actions -->
          <template v-for="marker in timelineMarkers" :key="marker">
            <div
              class="timeline-marker"
              :style="{
                left: ((marker / Math.max(1, totalFrames - 1)) * 100) + '%',
                position: 'absolute',
                top: '-4px',
                width: '8px',
                height: '22px',
                background: 'none',
                pointerEvents: 'auto',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: 'pointer',
                zIndex: 2,
              }"
              @click.stop="jumpToFrame(marker)"
              title="Jump to frame {{ marker + 1 }}"
            >
              <span style="display: block; width: 8px; height: 8px; border-radius: 50%; background: #eab308; border: 2px solid #fff; box-shadow: 0 0 2px #eab308; position: absolute; top: 8px;"></span>
            </div>
          </template>
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

        <div class="velocity-control" ref="speedControlRef">
          <button type="button" class="speed-button" @click="toggleSpeedPopover" :title="'Playback speed ('+playbackSpeed.toFixed(2)+'x)'">
            ⚡ {{ playbackSpeed }}x
          </button>
          <transition name="fade">
            <div v-if="showSpeedPopover" class="speed-popover minimal" @click.stop>
              <input
                v-model.number="sliderInternal"
                type="range"
                orient="vertical"
                class="speed-vertical-slider only"
                min="0"
                :max="speedSteps.length-1"
                step="1"
                @input="onSpeedSliderInput"
              />
            </div>
          </transition>
        </div>

        <div class="timeline">
          <input
            :value="sliderValue"
            @input="onTimelineSliderInput($event)"
            @change="onTimelineSliderChange($event)"
            type="range"
            :min="0"
            :max="Math.max(0, totalFrames - 1)"
            class="timeline-slider"
            :style="sliderGradientStyle"
          />
          <span class="frame-info">
            Frame {{ Math.min(currentFrame + 1, totalFrames || 0) }} / {{ totalFrames || 0 }}
            <span v-if="loadedFrames < totalFrames"> (loaded {{ loadedFrames }})</span>
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
          <div class="agents-rows-detailed">
            <div
              v-for="agent in currentFrameData?.agents"
              :key="agent.id"
              class="agent-row-detailed"
              @click="focusAgent(agent.id)"
              :style="{ cursor: usePhaser ? 'pointer' : undefined }"
            >
              <div class="agent-info-section">
                <div class="agent-basic-info">
                  <h4>{{ agent.name }}</h4>
                  <p class="persona">{{ agent.persona }}</p>
                </div>
                <div class="agent-status-info">
                  <p class="location">
                    <span v-if="agent.location.area && agent.location.area !== ''">📍 {{ agent.location.area }} </span>
                    <span>(x: {{ agent.location.x }}, y: {{ agent.location.y }})</span>
                  </p>
                  <p class="action"><strong>🎬 {{ agent.current_action }}</strong></p>
                </div>
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

              <!-- Agent Progress Line with Decision Points -->
              <div class="agent-progress-container" v-if="!loading && totalFrames > 0">
                <div class="agent-progress-label">Activity Timeline</div>
                <div class="agent-progress-bar" @click="onAgentProgressClick($event, agent.id)">
                  <div 
                    class="agent-progress-fill" 
                    :style="{ width: getAgentProgressPercent(agent.id) + '%' }"
                  ></div>
                  <!-- Decision point markers -->
                  <div
                    v-for="decisionPoint in agentDecisionPoints[agent.id] || []"
                    :key="decisionPoint"
                    class="decision-marker"
                    :style="{
                      left: ((decisionPoint / Math.max(1, totalFrames - 1)) * 100) + '%'
                    }"
                    @click.stop="jumpToFrame(decisionPoint)"
                    :title="`Decision at frame ${decisionPoint + 1}: ${getActionChange(agent.id, decisionPoint)}`"
                  >
                    <span class="decision-dot"></span>
                  </div>
                  <!-- Current position indicator -->
                  <div
                    class="current-position-marker"
                    :style="{
                      left: ((currentFrame / Math.max(1, totalFrames - 1)) * 100) + '%'
                    }"
                  >
                    <span class="current-position-dot"></span>
                  </div>
                </div>
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
import { ref, computed, onMounted, onUnmounted, watch, onBeforeUnmount } from 'vue'
import { getReplayChunk } from '@/services/api'
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


// --- PARALLEL, OUT-OF-ORDER CHUNK LOADING ---
const replay = ref<Replay | null>(null)
const loading = ref(true)
const loadProgress = ref(0)
const targetDurationMs = 120000
let progressInterval: ReturnType<typeof setInterval> | null = null
const remainingSeconds = computed(() => {
  if (loadProgress.value >= 100) return 0
  const frac = Math.max(0.01, loadProgress.value / 100)
  const elapsed = targetDurationMs * frac
  const remainMs = Math.max(0, targetDurationMs - elapsed)
  return Math.ceil(remainMs / 1000)
})
const currentFrame = ref(0)
const isPlaying = ref(false)
const playbackSpeed = ref(1)
let playInterval: ReturnType<typeof setInterval> | null = null
// Advanced speed control UI state
// Playback speed popover (minimal slider-only)
const showSpeedPopover = ref(false)
const speedSteps = [0.25,0.5,1,2,4,8,16,32,64]
const sliderInternal = ref(speedSteps.indexOf(playbackSpeed.value))
const speedControlRef = ref<HTMLElement|null>(null)
function toggleSpeedPopover(){
  showSpeedPopover.value = !showSpeedPopover.value
  sliderInternal.value = speedSteps.indexOf(playbackSpeed.value)
}
function onSpeedSliderInput(){
  const idx = Math.min(speedSteps.length-1, Math.max(0, sliderInternal.value))
  playbackSpeed.value = speedSteps[idx]
}
function onGlobalClick(e:MouseEvent){
  if(!showSpeedPopover.value) return
  if(!speedControlRef.value) return
  if(!speedControlRef.value.contains(e.target as Node)) showSpeedPopover.value = false
}
document.addEventListener('click', onGlobalClick)
onBeforeUnmount(()=>document.removeEventListener('click', onGlobalClick))

// Instead of a dense array, use a sparse array for frames
const frames = ref<(ReplayFrame | undefined)[]>([])
const totalFrames = ref(0)
const loadedFrames = computed(() => frames.value.filter(f => f !== undefined).length)
const sliderGradientStyle = computed(() => {
  const total = Math.max(1, (totalFrames.value || 0) - 1)
  const playedPct = total > 0 ? Math.min(100, Math.max(0, (currentFrame.value / total) * 100)) : 0
  const loadedPct = total > 0 ? Math.min(100, Math.max(playedPct, ((loadedFrames.value - 1) / total) * 100)) : playedPct
  const playedColor = '#42b883'
  const loadedColor = '#6b7280'
  const remainingColor = '#e5e7eb'
  return {
    background: `linear-gradient(90deg,
      ${playedColor} 0% ${playedPct}%,
      ${loadedColor} ${playedPct}% ${loadedPct}%,
      ${remainingColor} ${loadedPct}% 100%
    )`
  }
})
const currentFrameData = computed((): ReplayFrame | null => {
  return frames.value[currentFrame.value] || null
})

// Track which chunks are being loaded
const chunkSize = 250
const loadingChunks = new Set<number>() // chunk start offsets
const loadedChunks = new Set<number>()

async function loadChunk(offset: number) {
  if (loadingChunks.has(offset) || loadedChunks.has(offset)) return
  loadingChunks.add(offset)
  try {
    const chunk = await getReplayChunk(props.id, offset, chunkSize)
    if (!replay.value) {
      // initialize replay container from metadata
      replay.value = {
        id: chunk.id,
        simulation_id: chunk.simulation_id,
        name: chunk.name,
        frames: [],
        metadata: {
          total_steps: chunk.metadata.total_steps,
          duration_seconds: chunk.metadata.duration_seconds,
          agent_count: chunk.metadata.agent_count,
        },
      }
      totalFrames.value = chunk.metadata.total_steps
      // Pre-allocate sparse array
      frames.value = Array(chunk.metadata.total_steps)
    }
    // Fill in the chunk
    for (let i = 0; i < chunk.frames.length; ++i) {
      frames.value[offset + i] = chunk.frames[i]
    }
    loadedChunks.add(offset)
    // Update progress
    loadProgress.value = totalFrames.value > 0 ? (loadedFrames.value / totalFrames.value) * 100 : 0
    if (loading.value && loadedFrames.value > 0) {
      loading.value = false
      if (progressInterval) {
        clearInterval(progressInterval)
        progressInterval = null
      }
    }
  } catch (e) {
    console.error('Failed to load chunk', offset, e)
  } finally {
    loadingChunks.delete(offset)
  }
}




// --- AGGRESSIVE PARALLEL CHUNK LOADING ---
const loadReplay = async () => {
  await loadChunk(0)
  // After first chunk, load all remaining chunks in parallel
  if (!replay.value || !replay.value.metadata.total_steps) return;
  const total = replay.value.metadata.total_steps;
  const maxChunk = Math.floor((total - 1) / chunkSize);
  for (let i = 1; i <= maxChunk; ++i) {
    loadChunk(i * chunkSize);
  }
}

// When user jumps to a frame, load the chunk if not loaded
watch(currentFrame, (val) => {
  const offset = Math.floor(val / chunkSize) * chunkSize
  if (!loadedChunks.has(offset)) {
    loadChunk(offset)
  }
})

// Allow manual jump to any frame
function jumpToFrame(idx: number) {
  if (idx < 0 || idx >= totalFrames.value) return
  currentFrame.value = idx
  const offset = Math.floor(idx / chunkSize) * chunkSize
  if (!loadedChunks.has(offset)) {
    loadChunk(offset)
  }
}

// (Removed duplicate autoplay watcher - single implementation kept below)

onMounted(() => {
  const start = performance.now()
  progressInterval = setInterval(() => {
    if (!loading.value) return
    const elapsed = performance.now() - start
    const t = Math.min(1, elapsed / targetDurationMs)
    loadProgress.value = t * (2 - t) * 100
  }, 300)
  loadReplay()
})

onUnmounted(() => {
  if (playInterval) clearInterval(playInterval)
  if (progressInterval) clearInterval(progressInterval)
})

const playPause = () => {
  isPlaying.value = !isPlaying.value
}

const stepForward = () => {
  const maxIdx = Math.max(0, Math.min(loadedFrames.value - 1, totalFrames.value - 1))
  if (currentFrame.value < maxIdx) currentFrame.value++
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
      const total = totalFrames.value
      const loaded = loadedFrames.value
      if (!total || total <= 1) return

      // If we can advance within loaded frames, do so
      if (currentFrame.value < Math.min(loaded - 1, total - 1)) {
        currentFrame.value++
        return
      }

      // If not fully loaded yet, wait for more chunks
      if (loaded < total) {
        return
      }

      // Fully loaded and at end => stop
      if (currentFrame.value >= total - 1) {
        isPlaying.value = false
      }
    }, 1000 / speed)
  }
})

onMounted(() => {
  // Simulated ramp only until first chunk updates real progress
  const start = performance.now()
  progressInterval = setInterval(() => {
    if (!loading.value) return // real progress now drives UI
    const elapsed = performance.now() - start
    const t = Math.min(1, elapsed / targetDurationMs)
    loadProgress.value = t * (2 - t) * 100
  }, 300)
  loadReplay()
})

onUnmounted(() => {
  if (playInterval) clearInterval(playInterval)
  if (progressInterval) clearInterval(progressInterval)
})

// --- TIMELINE MARKERS FOR END OF LONG ACTIONS ---
// Markers for frames where at least one agent stops a long action after all 3 have done it for 100+ frames
const timelineMarkers = ref<number[]>([])
const LONG_ACTIONS = ['sleeping', 'asleep', 'resting', 'nap', 'sleep'] // extend as needed

// --- AGENT DECISION POINTS ---
// Track decision points (action changes) for each agent
const agentDecisionPoints = ref<Record<string, number[]>>({})

// Analyze agent action changes to find decision points
function updateAgentDecisionPoints() {
  if (!frames.value.length || totalFrames.value === 0) return
  
  const decisionPoints: Record<string, number[]> = {}
  const lastActions: Record<string, string> = {}
  
  for (let i = 0; i < frames.value.length; ++i) {
    const frame = frames.value[i]
    if (!frame || !frame.agents) continue
    
    for (const agent of frame.agents) {
      // Initialize tracking for this agent
      if (!decisionPoints[agent.id]) {
        decisionPoints[agent.id] = []
        lastActions[agent.id] = agent.current_action
        continue
      }
      
      // Check if action changed
      if (agent.current_action !== lastActions[agent.id]) {
        decisionPoints[agent.id].push(i)
        lastActions[agent.id] = agent.current_action
      }
    }
  }
  
  agentDecisionPoints.value = decisionPoints
}

// Analyze loaded frames for marker points
function updateTimelineMarkers() {
  if (!frames.value.length || totalFrames.value === 0) return
  const minRun = 100
  const agentCount = replay.value?.metadata.agent_count || 3
  // Track for each agent the current long action run
  const runs: Record<string, {action: string, start: number, length: number}> = {}
  let lastAllSame: {action: string, start: number, end: number} | null = null
  let markers: number[] = []
  for (let i = 0; i < frames.value.length; ++i) {
    const frame = frames.value[i]
    if (!frame || !frame.agents) continue
    // For each agent, update their run
    for (const agent of frame.agents) {
      const isLong = LONG_ACTIONS.includes(agent.current_action.toLowerCase())
      if (!runs[agent.id]) {
        runs[agent.id] = {action: agent.current_action, start: i, length: isLong ? 1 : 0}
      } else {
        if (isLong && agent.current_action === runs[agent.id].action) {
          runs[agent.id].length++
        } else {
          runs[agent.id] = {action: agent.current_action, start: i, length: isLong ? 1 : 0}
        }
      }
    }
    // Check if all agents are in the same long action for minRun
    const allLong = Object.values(runs).length === agentCount && Object.values(runs).every(r => LONG_ACTIONS.includes(r.action.toLowerCase()) && r.length >= minRun)
    if (allLong) {
      if (!lastAllSame) {
        lastAllSame = {action: frame.agents[0].current_action, start: i, end: i}
      } else {
        lastAllSame.end = i
      }
    } else if (lastAllSame) {
      // At least one agent stopped the long action
      markers.push(i)
      lastAllSame = null
    }
  }
  timelineMarkers.value = markers
}

// Make progress bar clickable to jump to any frame
function onProgressBarClick(event: MouseEvent) {
  const bar = event.currentTarget as HTMLElement | null
  if (!bar) return
  const rect = bar.getBoundingClientRect()
  const x = event.clientX - rect.left
  const pct = Math.max(0, Math.min(1, x / rect.width))
  const frame = Math.round(pct * (totalFrames.value - 1))
  console.log('Jumping to frame', frame)
  jumpToFrame(frame)
}

// Agent progress bar click handler
function onAgentProgressClick(event: MouseEvent, agentId: string) {
  const bar = event.currentTarget as HTMLElement | null
  if (!bar) return
  const rect = bar.getBoundingClientRect()
  const x = event.clientX - rect.left
  const pct = Math.max(0, Math.min(1, x / rect.width))
  const frame = Math.round(pct * (totalFrames.value - 1))
  jumpToFrame(frame)
}

// Get current progress percentage for an agent (same as overall progress)
function getAgentProgressPercent(agentId: string): number {
  return totalFrames.value > 0 ? (currentFrame.value / Math.max(1, totalFrames.value - 1)) * 100 : 0
}

// Get the action of an agent at a specific frame
function getActionAtFrame(agentId: string, frameIndex: number): string {
  const frame = frames.value[frameIndex]
  if (!frame || !frame.agents) return 'Unknown'
  const agent = frame.agents.find(a => a.id === agentId)
  return agent?.current_action || 'Unknown'
}

// Get action change information for tooltip
function getActionChange(agentId: string, frameIndex: number): string {
  const currentAction = getActionAtFrame(agentId, frameIndex)
  const previousAction = frameIndex > 0 ? getActionAtFrame(agentId, frameIndex - 1) : ''
  
  if (previousAction && previousAction !== currentAction) {
    return `${previousAction} → ${currentAction}`
  }
  return currentAction
}

// Recompute markers when frames are loaded/updated
watch(frames, () => {
  updateTimelineMarkers()
  updateAgentDecisionPoints()
}, {deep: true})

// --- Timeline slider decoupling for smooth seeking ---
const sliderValue = ref(0)
function onTimelineSliderInput(event: Event) {
  const target = event.target as HTMLInputElement | null
  if (target && target.value !== undefined) {
    sliderValue.value = Number(target.value)
  }
}
function onTimelineSliderChange(event: Event) {
  const target = event.target as HTMLInputElement | null
  if (target && target.value !== undefined) {
    jumpToFrame(Number(target.value))
  }
}
watch(currentFrame, (val) => {
  sliderValue.value = val
})
</script>

<style scoped>
.velocity-control { position: relative; display:flex; align-items:center; }
.speed-button { background:#fff; border:1px solid #bbb; border-radius:6px; padding:4px 10px; cursor:pointer; font-size:0.9rem; box-shadow:0 1px 3px rgba(0,0,0,0.08); }
.speed-button:hover { background:#f0f0f0; }
.speed-popover { position:absolute; top:40px; left:50%; transform:translateX(-50%); background:#fff; border:1px solid #d1d5db; border-radius:10px; padding:10px 16px; box-shadow:0 4px 18px rgba(0,0,0,0.15); z-index:200; width:auto; }
.speed-popover.minimal { padding:12px 8px; }
.speed-vertical-slider.only { writing-mode: bt-lr; appearance:none; -webkit-appearance: slider-vertical; width:40px; height:250px; transform:rotate(180deg); cursor:pointer; }
.fade-enter-active, .fade-leave-active { transition:opacity .15s ease; }
.fade-enter-from, .fade-leave-to { opacity:0; }
/* Slider styling (vertical) */
.speed-vertical-slider { background:linear-gradient(to top,#42b883,#42b883) no-repeat center/6px 100%; }
::-webkit-slider-thumb { -webkit-appearance:none; appearance:none; width:18px; height:18px; background:#fff; border:2px solid #42b883; border-radius:50%; box-shadow:0 0 0 2px #fff, 0 2px 4px rgba(0,0,0,0.2); }
::-webkit-slider-runnable-track { background:transparent; border:none; }
/* Firefox */
input[type=range].speed-vertical-slider { writing-mode: bt-lr; }
input[type=range].speed-vertical-slider::-moz-range-thumb { width:18px; height:18px; background:#fff; border:2px solid #42b883; border-radius:50%; box-shadow:0 0 0 2px #fff,0 2px 4px rgba(0,0,0,0.2); }
input[type=range].speed-vertical-slider::-moz-range-track { background:transparent; border:none; }
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
  appearance: none;
  -webkit-appearance: none;
  height: 8px;
  border-radius: 4px;
  outline: none;
  border: 1px solid #cfd8dc;
}

.timeline-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: #111827;
  border: 2px solid #fff;
  box-shadow: 0 0 0 1px #9ca3af;
  cursor: pointer;
  margin-top: -4px; /* align thumb vertically with track */
}

.timeline-slider::-moz-range-thumb {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: #111827;
  border: 2px solid #fff;
  box-shadow: 0 0 0 1px #9ca3af;
  cursor: pointer;
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

.agents-rows-detailed {
  display: flex;
  flex-direction: column;
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

.agent-row-detailed {
  background: #f9f9f9;
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  cursor: pointer;
  transition: background-color 0.2s;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.agent-row-detailed:hover {
  background: #f0f0f0;
}

.agent-info-section {
  display: grid;
  grid-template-columns: 1fr 1fr auto;
  gap: 1rem;
  align-items: start;
}

.agent-basic-info h4 {
  margin: 0 0 0.25rem 0;
  color: #2c3e50;
  font-size: 1rem;
  font-weight: 600;
}

.agent-basic-info .persona {
  font-style: italic;
  color: #666;
  font-size: 0.8rem;
  margin: 0;
  line-height: 1.3;
}

.agent-status-info .location,
.agent-status-info .action {
  font-size: 0.8rem;
  margin: 0.2rem 0;
  color: #555;
}

.agent-status-info .action {
  color: #2c3e50;
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

/* Agent Progress Bar Styles */
.agent-progress-container {
  margin: 0.5rem 0;
  min-width: 0; /* Allow flex shrinking */
}

.agent-progress-label {
  font-size: 0.7rem;
  color: #666;
  margin-bottom: 0.25rem;
  font-weight: 500;
}

.agent-progress-bar {
  position: relative;
  height: 14px;
  background: #e5e7eb;
  border-radius: 7px;
  cursor: pointer;
  overflow: visible;
  margin: 0.25rem 0;
  min-width: 200px; /* Ensure minimum width for progress bar */
}

.agent-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #42b883 0%, #369870 100%);
  border-radius: 6px;
  transition: width 0.2s ease;
}

.decision-marker {
  position: absolute;
  top: -2px;
  width: 16px;
  height: 16px;
  cursor: pointer;
  z-index: 3;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.decision-dot {
  display: block;
  width: 8px;
  height: 8px;
  background: #f59e0b;
  border: 2px solid #fff;
  border-radius: 50%;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
  transition: all 0.2s ease;
}

.decision-marker:hover .decision-dot {
  width: 10px;
  height: 10px;
  background: #d97706;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.4);
}

.current-position-marker {
  position: absolute;
  top: -4px;
  width: 20px;
  height: 20px;
  z-index: 4;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}

.current-position-dot {
  display: block;
  width: 12px;
  height: 12px;
  background: #dc2626;
  border: 3px solid #fff;
  border-radius: 50%;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.7;
    transform: scale(1.1);
  }
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
  
  .agent-info-section {
    grid-template-columns: 1fr;
    gap: 0.5rem;
  }
}

@media (max-width: 768px) {
  .replay-display {
    grid-template-columns: 1fr;
  }
  
  .agents-sidebar {
    max-height: 200px;
  }
  
  .agent-info-section {
    grid-template-columns: 1fr;
    gap: 0.5rem;
  }
  
  .agent-progress-bar {
    min-width: 150px;
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