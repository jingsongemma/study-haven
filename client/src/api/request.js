import axios from 'axios'

// 创建统一的接口请求实例。
const request = axios.create({
  baseURL: 'http://127.0.0.1:5000/api',
  timeout: 120000,
})

// 请求前自动携带 JWT。
request.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应异常统一提取后端提示。
request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const message = error.response?.data?.message || error.message || '请求失败'
    return Promise.reject(new Error(message))
  },
)

export default request
