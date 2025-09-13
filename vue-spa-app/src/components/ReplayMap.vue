<template>
  <div class="replay-map" ref="mapEl">
    <div v-if="!frame || frame.agents.length === 0" class="empty">No agent positions</div>
    <template v-else>
      <div
        v-for="agent in frame.agents"
        :key="agent.id"
        class="agent-node"
        :style="agentStyle(agent)"
        :title="agent.name + ' — ' + agent.current_action"
      >
        <div class="avatar" :class="'color-' + colorIndex(agent)">
          <span>{{ initials(agent.name) }}</span>
        </div>
        <div class="label">{{ agent.name }}</div>
      </div>
    </template>
    <div v-if="showLegend" class="legend">
      <div class="legend-item" v-for="agent in frame?.agents || []" :key="agent.id">
        <span class="legend-swatch" :class="'color-' + colorIndex(agent)"></span>{{ agent.name }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import type { ReplayFrame, Agent } from '@/types'

interface Props {
  frame: ReplayFrame | null
  padding?: number
  showLegend?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  padding: 20,
  showLegend: true,
})

const mapEl = ref<HTMLElement | null>(null)
const width = ref(800)
const height = ref(500)

const bbox = computed(() => {
  if (!props.frame || props.frame.agents.length === 0) {
    return { minX: 0, maxX: 1, minY: 0, maxY: 1 }
  }
  let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity
  for (const a of props.frame.agents) {
    if (a.location.x < minX) minX = a.location.x
    if (a.location.x > maxX) maxX = a.location.x
    if (a.location.y < minY) minY = a.location.y
    if (a.location.y > maxY) maxY = a.location.y
  }
  if (minX === maxX) { maxX = minX + 1 }
  if (minY === maxY) { maxY = minY + 1 }
  return { minX, maxX, minY, maxY }
})

const scale = computed(() => {
  const { minX, maxX, minY, maxY } = bbox.value
  const innerW = width.value - props.padding * 2
  const innerH = height.value - props.padding * 2
  return {
    x: (x: number) => props.padding + ((x - minX) / (maxX - minX)) * innerW,
    y: (y: number) => props.padding + ((y - minY) / (maxY - minY)) * innerH,
  }
})

function colorIndex(agent: Agent) {
  // Stable hash based on id
  let h = 0
  for (let i = 0; i < agent.id.length; i++) {
    h = (h * 31 + agent.id.charCodeAt(i)) >>> 0
  }
  return (h % 8) + 1
}

function initials(name: string) {
  return name.split(/\s+/).map(p => p[0]).join('').slice(0,2).toUpperCase()
}

function agentStyle(agent: Agent) {
  const x = scale.value.x(agent.location.x)
  const y = scale.value.y(agent.location.y)
  return {
    transform: `translate(${x}px, ${y}px)`
  }
}

function updateSize() {
  if (!mapEl.value) return
  const rect = mapEl.value.getBoundingClientRect()
  width.value = rect.width
  height.value = rect.height
}

let resizeObs: ResizeObserver | null = null
onMounted(() => {
  updateSize()
  resizeObs = new ResizeObserver(() => updateSize())
  if (mapEl.value) resizeObs.observe(mapEl.value)
  window.addEventListener('resize', updateSize)
})

onUnmounted(() => {
  if (resizeObs && mapEl.value) resizeObs.unobserve(mapEl.value)
  window.removeEventListener('resize', updateSize)
})
</script>

<style scoped>
.replay-map {
  position: relative;
  width: 100%;
  height: 420px;
  background: repeating-conic-gradient(#f7f9fa 0% 25%, #eef2f4 0% 50%) 50% / 40px 40px;
  border: 1px solid #d9e1e5;
  border-radius: 8px;
  overflow: hidden;
  font-family: system-ui, sans-serif;
}
.empty {
  position: absolute;
  top: 50%; left: 50%; transform: translate(-50%, -50%);
  color: #888;
  font-size: 0.9rem;
}
.agent-node {
  position: absolute;
  transform: translate(-50%, -50%);
  cursor: pointer;
  text-align: center;
  white-space: nowrap;
}
.agent-node .avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 600;
  color: #fff;
  box-shadow: 0 2px 4px rgba(0,0,0,0.15);
  margin-bottom: 2px;
  user-select: none;
}
.agent-node .label {
  font-size: 0.65rem;
  background: rgba(0,0,0,0.55);
  color: #fff;
  padding: 2px 4px;
  border-radius: 4px;
  backdrop-filter: blur(2px);
}
.legend {
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgba(255,255,255,0.9);
  padding: 6px 8px;
  border-radius: 6px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  max-width: 160px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 0.65rem;
}
.legend-item { display: flex; align-items: center; gap: 4px; }
.legend-swatch { width: 10px; height: 10px; border-radius: 2px; }
/* Color palette */
.color-1 { background: #42b883; }
.color-2 { background: #2f9d95; }
.color-3 { background: #3a6fd9; }
.color-4 { background: #d46b08; }
.color-5 { background: #845ec2; }
.color-6 { background: #ff9671; }
.color-7 { background: #0081cf; }
.color-8 { background: #4d8076; }
</style>
