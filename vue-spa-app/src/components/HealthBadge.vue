<template>
  <div class="health-badge" :class="{ healthy: isHealthy, unhealthy: !isHealthy }">
    <span class="status-dot"></span>
    <span class="status-text">{{ statusText }}</span>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { getHealth } from '@/services/api'
import type { HealthStatus } from '@/types'

const health = ref<HealthStatus | null>(null)
const loading = ref(true)

const isHealthy = computed(() => {
  return health.value?.env_server && health.value?.sim_server
})

const statusText = computed(() => {
  if (loading.value) return 'Checking...'
  if (isHealthy.value) return 'Online'
  return 'Offline'
})

let intervalId: number

const checkHealth = async () => {
  try {
    health.value = await getHealth()
  } catch (error) {
    console.error('Health check failed:', error)
    health.value = null
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  checkHealth()
  intervalId = setInterval(checkHealth, 10000) // Check every 10 seconds
})

onUnmounted(() => {
  if (intervalId) clearInterval(intervalId)
})
</script>

<style scoped>
.health-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 500;
}

.healthy {
  background-color: rgba(34, 197, 94, 0.1);
  color: #22c55e;
}

.unhealthy {
  background-color: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: currentColor;
}
</style>