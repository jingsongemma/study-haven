<script setup>
import { onMounted, ref } from 'vue'

import request from '../api/request'

const records = ref([])
const error = ref('')

// 加载管理员可见的全部对话历史。
async function loadRecords() {
  error.value = ''
  try {
    const data = await request.get('/admin/qa-records')
    records.value = data.items
  } catch (err) {
    error.value = err.message
  }
}

// 将后端返回的引用 JSON 转换为数组。
function parseReferences(value) {
  if (!value) return []
  if (Array.isArray(value)) return value
  try {
    return JSON.parse(value)
  } catch {
    return []
  }
}

onMounted(loadRecords)
</script>

<template>
  <section class="page-stack">
    <p v-if="error" class="error-text">{{ error }}</p>
    <section class="panel">
      <h2>全部对话历史</h2>
      <div v-if="!records.length" class="empty-box">暂无问答记录</div>
      <article v-for="item in records" :key="item.id" class="record-card">
        <div class="record-meta">
          <strong>{{ item.real_name || item.username || '未知用户' }}</strong>
          <span>{{ item.created_at }}</span>
        </div>
        <h3>问题</h3>
        <p>{{ item.question }}</p>
        <h3>回答</h3>
        <p>{{ item.answer }}</p>
        <h3>引用资料</h3>
        <ul v-if="parseReferences(item.references_json).length">
          <li v-for="refItem in parseReferences(item.references_json)" :key="`${item.id}-${refItem.doc_id}-${refItem.chunk_index}`">
            {{ refItem.title || '未命名资料' }}
          </li>
        </ul>
        <p v-else class="muted-text">无引用资料</p>
      </article>
    </section>
  </section>
</template>
