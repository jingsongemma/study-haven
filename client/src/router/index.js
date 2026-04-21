import { createRouter, createWebHistory } from 'vue-router'

import Chat from '../views/Chat.vue'
import Dashboard from '../views/Dashboard.vue'
import History from '../views/History.vue'
import Knowledge from '../views/Knowledge.vue'
import Login from '../views/Login.vue'
import Users from '../views/Users.vue'

const routes = [
  { path: '/', redirect: '/chat' },
  { path: '/login', name: 'login', component: Login, meta: { title: '登录' } },
  { path: '/chat', name: 'chat', component: Chat, meta: { title: '知识问答' } },
  { path: '/admin', name: 'admin', component: Dashboard, meta: { title: '后台首页', admin: true } },
  { path: '/admin/history', name: 'history', component: History, meta: { title: '对话历史', admin: true } },
  { path: '/admin/knowledge', name: 'knowledge', component: Knowledge, meta: { title: '知识库管理', admin: true } },
  { path: '/admin/users', name: 'users', component: Users, meta: { title: '用户管理', admin: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫负责登录态和管理员权限控制。
router.beforeEach((to) => {
  const token = localStorage.getItem('token')
  const user = JSON.parse(localStorage.getItem('user') || 'null')
  if (to.name !== 'login' && !token) {
    return '/login'
  }
  if (to.meta.admin && user?.role !== 'admin') {
    return '/chat'
  }
  if (to.name === 'login' && token) {
    return user?.role === 'admin' ? '/admin' : '/chat'
  }
  return true
})

export default router
