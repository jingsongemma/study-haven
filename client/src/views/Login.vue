<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import request from '../api/request'

const router = useRouter()
const loading = ref(false)
const error = ref('')
const form = reactive({
  username: 'admin',
  password: '123456',
})

// 提交登录表单并根据角色进入对应首页。
async function submitLogin() {
  loading.value = true
  error.value = ''
  try {
    const data = await request.post('/auth/login', form)
    localStorage.setItem('token', data.token)
    localStorage.setItem('user', JSON.stringify(data.user))
    router.push(data.user.role === 'admin' ? '/admin' : '/chat')
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main class="login-page">
    <section class="login-panel">
      <div class="login-copy">
        <span class="eyebrow">EnterpriseQA</span>
        <h1>企业内部知识库问答 Agent</h1>
        <p>连接企业资料、Chroma 向量库与 Ollama 本地模型，快速完成可学习、可运行的 RAG 问答闭环。</p>
      </div>
      <form class="login-form" @submit.prevent="submitLogin">
        <label>
          用户名
          <input v-model="form.username" autocomplete="username" />
        </label>
        <label>
          密码
          <input v-model="form.password" type="password" autocomplete="current-password" />
        </label>
        <p v-if="error" class="error-text">{{ error }}</p>
        <button class="primary-button" :disabled="loading">{{ loading ? '登录中...' : '登录系统' }}</button>
        <small>测试账号：admin / user，密码均为 123456</small>
      </form>
    </section>
  </main>
</template>
