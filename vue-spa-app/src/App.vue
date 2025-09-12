<template>
  <div id="app">
    <nav class="navbar">
      <div class="nav-brand">
        <router-link to="/" class="brand-link">NSPLLM</router-link>
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
import HealthBadge from '@/components/HealthBadge.vue'
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