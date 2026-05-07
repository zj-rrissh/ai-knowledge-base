import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import KnowledgeView from '../views/KnowledgeView.vue'
import ChatView from '../views/ChatView.vue'

const routes = [
  { path: '/login', component: LoginView },
  { path: '/knowledge', component: KnowledgeView, meta: { requiresAuth: true } },
  { path: '/chat', component: ChatView, meta: { requiresAuth: true } },
  { path: '/', redirect: '/chat' },
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to) => {
  if (to.meta.requiresAuth && !localStorage.getItem('token')) return '/login'
})

export default router
