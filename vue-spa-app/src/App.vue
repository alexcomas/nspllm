<template>
  <div id="app">
    <nav class="navbar">
      <div class="nav-brand">
        <router-link to="/" class="brand-link">NSPLLM<span v-if="breadcrumbLabel" class="breadcrumb"> / {{ breadcrumbLabel }}</span></router-link>
      </div>
      <div class="nav-links">
        <router-link to="/sims" class="nav-link">Simulations</router-link>
        <HealthBadge />
      </div>
    </nav>
    
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import HealthBadge from '@/components/HealthBadge.vue'

const breadcrumbLabel = ref<string>('')
const route = useRoute()

function handleReplayNameEvent(e: CustomEvent) {
  breadcrumbLabel.value = e.detail?.name || ''
}

function updateFromRoute() {
  if (route.name === 'replay' && !breadcrumbLabel.value) {
    // Show placeholder until event arrives
    breadcrumbLabel.value = route.params.id ? `Replay ${route.params.id}` : ''
  } else if (route.name !== 'replay') {
    breadcrumbLabel.value = ''
  }
}

onMounted(() => {
  window.addEventListener('replay-name', handleReplayNameEvent as EventListener)
  updateFromRoute()
})
onBeforeUnmount(() => {
  window.removeEventListener('replay-name', handleReplayNameEvent as EventListener)
})
</script>

<style scoped>
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background: #1a1a1a;
  color: white;
}

.nav-brand .brand-link {
  font-size: 1.5rem;
  font-weight: bold;
  color: #42b883;
  text-decoration: none;
}

.breadcrumb {
  font-size: 0.9rem;
  font-weight: 500;
  color: #ccc;
  margin-left: 0.5rem;
}

.nav-links {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.nav-link {
  color: white;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.nav-link:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.main-content {
  padding: 2rem;
}
</style>