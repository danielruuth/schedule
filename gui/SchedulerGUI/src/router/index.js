import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'hem',
      component: () => import('../views/HomeView.vue')
    },
    {
      path: '/om',
      name: 'om',
      component: () => import('../views/AboutView.vue')
    }
  ]
})

export default router
