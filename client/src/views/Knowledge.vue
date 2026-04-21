<script setup>
import { onMounted, reactive, ref } from 'vue'

import request from '../api/request'

const documents = ref([])
const loading = ref(false)
const message = ref('')
const textForm = reactive({ title: '', content: '' })
const uploadTitle = ref('')
const uploadFile = ref(null)

// 查询知识文档列表。
async function loadDocuments() {
  const data = await request.get('/admin/documents')
  documents.value = data.items
}

// 通过文本粘贴新增知识。
async function submitText() {
  loading.value = true
  message.value = ''
  try {
    const data = await request.post('/admin/documents/text', textForm)
    message.value = `${data.message}，切分 ${data.chunk_count} 段`
    textForm.title = ''
    textForm.content = ''
    await loadDocuments()
  } catch (err) {
    message.value = err.message
  } finally {
    loading.value = false
  }
}

// 保存用户选择的上传文件。
function handleFile(event) {
  uploadFile.value = event.target.files[0]
}

// 上传 txt、pdf、docx 文件并写入知识库。
async function submitUpload() {
  if (!uploadFile.value) {
    message.value = '请选择文件'
    return
  }
  loading.value = true
  message.value = ''
  const formData = new FormData()
  formData.append('title', uploadTitle.value)
  formData.append('file', uploadFile.value)
  try {
    const data = await request.post('/admin/documents/upload', formData)
    message.value = `${data.message}，切分 ${data.chunk_count} 段`
    uploadTitle.value = ''
    uploadFile.value = null
    await loadDocuments()
  } catch (err) {
    message.value = err.message
  } finally {
    loading.value = false
  }
}

// 删除知识文档和对应向量片段。
async function deleteDocument(id) {
  if (!confirm('确定删除该知识文档吗？')) return
  await request.delete(`/admin/documents/${id}`)
  await loadDocuments()
}

onMounted(loadDocuments)
</script>

<template>
  <section class="page-stack">
    <div class="form-grid">
      <form class="panel form-panel" @submit.prevent="submitText">
        <h2>文本入库</h2>
        <label>标题<input v-model="textForm.title" /></label>
        <label>正文<textarea v-model="textForm.content" rows="8"></textarea></label>
        <button class="primary-button" :disabled="loading">保存文本知识</button>
      </form>
      <form class="panel form-panel" @submit.prevent="submitUpload">
        <h2>文件入库</h2>
        <label>标题<input v-model="uploadTitle" placeholder="可为空，默认使用文件名" /></label>
        <label>文件<input type="file" accept=".txt,.pdf,.docx" @change="handleFile" /></label>
        <button class="primary-button" :disabled="loading">上传文件知识</button>
        <p>支持 txt、pdf、docx。</p>
      </form>
    </div>
    <p v-if="message" class="tip-text">{{ message }}</p>
    <section class="panel">
      <h2>知识文档</h2>
      <table>
        <thead>
          <tr><th>标题</th><th>类型</th><th>文件名</th><th>片段</th><th>创建人</th><th>操作</th></tr>
        </thead>
        <tbody>
          <tr v-for="item in documents" :key="item.id">
            <td>{{ item.title }}</td>
            <td>{{ item.source_type }}</td>
            <td>{{ item.file_name || '-' }}</td>
            <td>{{ item.chunk_count }}</td>
            <td>{{ item.creator || '-' }}</td>
            <td><button class="danger-button" @click="deleteDocument(item.id)">删除</button></td>
          </tr>
        </tbody>
      </table>
    </section>
  </section>
</template>
