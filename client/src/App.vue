<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

// 从浏览器缓存读取当前登录用户。
function readUser() {
  const raw = localStorage.getItem('user')
  return raw ? JSON.parse(raw) : null
}

const user = ref(readUser())

// 路由切换后重新读取用户信息，避免登录后菜单不刷新。
router.afterEach(() => {
  user.value = readUser()
})

// 判断是否处于登录页，用于控制整体布局。
const isLoginPage = computed(() => route.name === 'login')

// 退出登录并回到登录页。
function logout() {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  router.push('/login')
}
</script>

<template>
  <router-view v-if="isLoginPage" />
  <div v-else class="app-shell">
    <aside class="sidebar">
      <div class="brand">
        <span class="brand-mark">EQA</span>
        <div>
          <strong>企业知识库</strong>
          <small>RAG 问答 Agent</small>
        </div>
      </div>
      <nav class="nav-list">
        <router-link v-if="user?.role === 'admin'" to="/admin">后台首页</router-link>
        <router-link v-if="user?.role === 'admin'" to="/admin/history">对话历史</router-link>
        <router-link v-if="user?.role === 'admin'" to="/admin/knowledge">知识库管理</router-link>
        <router-link v-if="user?.role === 'admin'" to="/admin/users">用户管理</router-link>
        <router-link to="/chat">知识问答</router-link>
      </nav>
    </aside>
    <main class="main-area">
      <header class="topbar">
        <div>
          <h1>{{ route.meta.title }}</h1>
          <p>你好，{{ user?.real_name || user?.username }}</p>
        </div>
        <button class="ghost-button" @click="logout">退出登录</button>
      </header>
      <router-view />
    </main>
  </div>
</template>
