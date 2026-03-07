import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '@/pages/Dashboard.vue'
import Settings from '@/pages/Settings.vue'
import Transactions from '@/pages/Transactions.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/dashboard',
    },
    {
      path: '/dashboard',
      component: Dashboard,
    },
    {
      path: '/transactions',
      component: Transactions,
    },
    {
      path: '/settings',
      component: Settings,
    },
  ],
})

export default router
