<script setup>
import { onMounted, ref } from 'vue'

import request from '../api/request'

const question = ref('')
const answer = ref('')
const references = ref([])
const history = ref([])
const loading = ref(false)
const error = ref('')

// 加载当前用户问答历史。
async function loadHistory() {
  const data = await request.get('/chat/history')
  history.value = data.items
}

// 提交问题并展示 RAG 回答。
async function askQuestion() {
  if (!question.value.trim()) return
  loading.value = true
  error.value = ''
  answer.value = ''
  references.value = []
  try {
    const data = await request.post('/chat/ask', { question: question.value })
    answer.value = data.answer
    references.value = data.references
    question.value = ''
    await loadHistory()
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

onMounted(loadHistory)
</script>

<template>
  <section class="chat-layout">
    <div class="chat-main panel">
      <h2>问企业知识库</h2>
      <form class="ask-box" @submit.prevent="askQuestion">
        <textarea v-model="question" rows="5" placeholder="例如：差旅报销需要哪些材料？"></textarea>
        <button class="primary-button" :disabled="loading">{{ loading ? '生成中...' : '发送问题' }}</button>
      </form>
      <p v-if="error" class="error-text">{{ error }}</p>
      <article v-if="answer" class="answer-box">
        <h3>回答</h3>
        <p>{{ answer }}</p>
        <h3>引用资料</h3>
        <ul>
          <li v-for="item in references" :key="`${item.doc_id}-${item.chunk_index}`">
            {{ item.title }} <span v-if="item.file_name">({{ item.file_name }})</span>
          </li>
        </ul>
      </article>
    </div>
    <aside class="panel history-panel">
      <h2>最近提问</h2>
      <article v-for="item in history" :key="item.id" class="history-item">
        <strong>{{ item.question }}</strong>
        <p>{{ item.answer }}</p>
      </article>
    </aside>
  </section>
</template>
