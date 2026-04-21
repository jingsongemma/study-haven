<script setup>
import { onMounted, reactive, ref } from 'vue'

import request from '../api/request'

const users = ref([])
const message = ref('')
const form = reactive({ username: '', real_name: '', role: 'user' })

// 查询用户列表。
async function loadUsers() {
  const data = await request.get('/admin/users')
  users.value = data.items
}

// 创建新用户，默认密码为 123456。
async function createUser() {
  message.value = ''
  try {
    await request.post('/admin/users', form)
    message.value = '创建成功，默认密码为 123456'
    form.username = ''
    form.real_name = ''
    form.role = 'user'
    await loadUsers()
  } catch (err) {
    message.value = err.message
  }
}

// 保存用户角色、姓名和状态。
async function saveUser(user) {
  await request.put(`/admin/users/${user.id}`, user)
  message.value = '更新成功'
  await loadUsers()
}

// 删除指定用户。
async function deleteUser(id) {
  if (!confirm('确定删除该用户吗？')) return
  await request.delete(`/admin/users/${id}`)
  await loadUsers()
}

onMounted(loadUsers)
</script>

<template>
  <section class="page-stack">
    <form class="panel inline-form" @submit.prevent="createUser">
      <label>账号<input v-model="form.username" required /></label>
      <label>姓名<input v-model="form.real_name" /></label>
      <label>角色
        <select v-model="form.role">
          <option value="user">普通用户</option>
          <option value="admin">管理员</option>
        </select>
      </label>
      <button class="primary-button">新增用户</button>
    </form>
    <p v-if="message" class="tip-text">{{ message }}</p>
    <section class="panel">
      <h2>用户列表</h2>
      <table>
        <thead>
          <tr><th>账号</th><th>姓名</th><th>角色</th><th>状态</th><th>操作</th></tr>
        </thead>
        <tbody>
          <tr v-for="item in users" :key="item.id">
            <td>{{ item.username }}</td>
            <td><input v-model="item.real_name" /></td>
            <td>
              <select v-model="item.role">
                <option value="user">普通用户</option>
                <option value="admin">管理员</option>
              </select>
            </td>
            <td>
              <select v-model.number="item.status">
                <option :value="1">启用</option>
                <option :value="0">禁用</option>
              </select>
            </td>
            <td class="table-actions">
              <button class="ghost-button" @click="saveUser(item)">保存</button>
              <button class="danger-button" @click="deleteUser(item.id)">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </section>
  </section>
</template>
