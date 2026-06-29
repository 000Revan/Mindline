import { createRouter, createWebHistory } from 'vue-router'
import AppLayout from '@/layouts/AppLayout.vue'
import AuthView from '@/views/AuthView.vue'
import BranchesView from '@/views/BranchesView.vue'
import ChatView from '@/views/ChatView.vue'
import DashboardView from '@/views/DashboardView.vue'
import EmotionView from '@/views/EmotionView.vue'
import GoalsView from '@/views/GoalsView.vue'
import NotesView from '@/views/NotesView.vue'
import ReviewsView from '@/views/ReviewsView.vue'
import SessionsView from '@/views/SessionsView.vue'
import TasksView from '@/views/TasksView.vue'
import { isTokenExpiredOrInvalid } from '@/api/client'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/auth',
      name: 'auth',
      component: AuthView,
    },
    {
      path: '/',
      component: AppLayout,
      redirect: '/dashboard',
      children: [
        { path: 'dashboard', name: 'dashboard', component: DashboardView },
        { path: 'chat', name: 'chat', component: ChatView },
        { path: 'goals', name: 'goals', component: GoalsView },
        { path: 'tasks', name: 'tasks', component: TasksView },
        { path: 'sessions', name: 'sessions', component: SessionsView },
        { path: 'branches', name: 'branches', component: BranchesView },
        { path: 'notes', name: 'notes', component: NotesView },
        { path: 'reviews', name: 'reviews', component: ReviewsView },
        { path: 'emotion', name: 'emotion', component: EmotionView },
      ],
    },
  ],
})

router.beforeEach((to) => {
  const token = localStorage.getItem('mindline_token')
  const tokenInvalid = isTokenExpiredOrInvalid(token)

  if (tokenInvalid) {
    localStorage.removeItem('mindline_token')
    localStorage.removeItem('mindline_user')
    localStorage.removeItem('mindline_avatar_data_url')
  }

  if (to.name === 'auth' && !tokenInvalid) {
    return { name: 'dashboard' }
  }

  if (to.name !== 'auth' && tokenInvalid) {
    return {
      name: 'auth',
      query: {
        redirect: to.fullPath,
      },
    }
  }

  return true
})

export default router
