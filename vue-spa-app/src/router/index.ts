import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'
import Simulations from '@/views/Simulations.vue'
import ReplayViewer from '@/views/ReplayViewer.vue'
import DemoRunner from '@/views/DemoRunner.vue'

const router = createRouter({
  history: createWebHistory('/app/'),
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home,
    },
    {
      path: '/sims',
      name: 'simulations',
      component: Simulations,
    },
    {
      path: '/replay/:id',
      name: 'replay',
      component: ReplayViewer,
      props: true,
    },
    {
      path: '/demo/:id',
      name: 'demo',
      component: DemoRunner,
      props: true,
    },
  ],
})

export default router