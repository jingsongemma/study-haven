<script setup>
import * as echarts from 'echarts'
import { nextTick, onMounted, ref } from 'vue'

import request from '../api/request'

const stats = ref({ cards: { users: 0, documents: 0, qa: 0 }, roles: [], daily_qa: [] })
const roleChart = ref(null)
const qaChart = ref(null)
const error = ref('')

// 加载管理员首页统计并绘制图表。
async function loadStats() {
  try {
    stats.value = await request.get('/admin/stats')
    await nextTick()
    renderCharts()
  } catch (err) {
    error.value = err.message
  }
}

// 渲染角色分布和最近问答趋势图。
function renderCharts() {
  if (roleChart.value) {
    echarts.init(roleChart.value).setOption({
      tooltip: {},
      series: [{
        type: 'pie',
        radius: ['42%', '70%'],
        data: stats.value.roles.map((item) => ({ name: item.role, value: item.total })),
      }],
    })
  }
  if (qaChart.value) {
    echarts.init(qaChart.value).setOption({
      tooltip: {},
      xAxis: { type: 'category', data: stats.value.daily_qa.map((item) => item.day) },
      yAxis: { type: 'value', minInterval: 1 },
      series: [{ type: 'bar', data: stats.value.daily_qa.map((item) => item.total), itemStyle: { color: '#1f8a70' } }],
    })
  }
}

onMounted(loadStats)
</script>

<template>
  <section class="page-stack">
    <p v-if="error" class="error-text">{{ error }}</p>
    <div class="stat-grid">
      <article class="stat-card">
        <span>用户总数</span>
        <strong>{{ stats.cards.users }}</strong>
      </article>
      <article class="stat-card">
        <span>知识文档</span>
        <strong>{{ stats.cards.documents }}</strong>
      </article>
      <article class="stat-card">
        <span>问答次数</span>
        <strong>{{ stats.cards.qa }}</strong>
      </article>
    </div>
    <div class="chart-grid">
      <section class="panel">
        <h2>角色分布</h2>
        <div ref="roleChart" class="chart"></div>
      </section>
      <section class="panel">
        <h2>最近问答趋势</h2>
        <div ref="qaChart" class="chart"></div>
      </section>
    </div>
  </section>
</template>
