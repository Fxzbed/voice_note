// src/api/request.js
import axios from 'axios'

const request = axios.create({
  baseURL: '/api',
  timeout: 60000
})

// 请求前自动带 token
request.interceptors.request.use(config => {
  const token = localStorage.getItem('token')

  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }

  return config
})

// 返回时直接取 data
request.interceptors.response.use(
  response => response.data,
  error => {
    return Promise.reject(error.response?.data || error)
  }
)

export default request
