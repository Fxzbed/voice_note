<template>
  <div class="page">
    <div class="container">
      <h1>OSS 直传测试页面</h1>
      <p class="desc">流程：登录 → 获取 STS → 直传 OSS → 通知 Gin 落库</p>

      <section class="card">
        <h2>1. 登录</h2>
        <div class="form-grid">
          <div class="field">
            <label>用户名</label>
            <input v-model="username" type="text" placeholder="请输入用户名" />
          </div>
          <div class="field">
            <label>密码</label>
            <input v-model="password" type="password" placeholder="请输入密码" />
          </div>
        </div>

        <div class="actions">
          <button @click="handleLogin" :disabled="loading.login">
            {{ loading.login ? '登录中...' : '登录' }}
          </button>
          <button class="secondary" @click="clearToken">清除 Token</button>
        </div>

        <div class="status">
          当前状态：
          <span :class="token ? 'ok' : 'warn'">
            {{ token ? '已登录' : '未登录' }}
          </span>
        </div>

        <div class="field">
          <label>登录响应</label>
          <textarea :value="loginResult" readonly />
        </div>
      </section>

      <section class="card">
        <h2>2. 选择音频文件</h2>

        <div class="field">
          <label>音频文件</label>
          <input type="file" accept="audio/*,.mp3,.wav,.m4a,.aac,.flac" @change="handleFileChange" />
        </div>

        <div class="status">
          当前文件：
          <span :class="selectedFile ? 'ok' : 'warn'">
            {{ selectedFile ? selectedFile.name : '未选择文件' }}
          </span>
        </div>
      </section>

      <section class="card">
        <h2>3. 获取 STS 并上传 OSS</h2>

        <div class="actions">
          <button @click="handleGetSTS" :disabled="loading.sts || !selectedFile || !token">
            {{ loading.sts ? '获取中...' : '获取 STS' }}
          </button>

          <button
            class="success"
            @click="handleUploadToOSS"
            :disabled="loading.upload || !selectedFile || !stsData"
          >
            {{ loading.upload ? '上传中...' : '上传到 OSS' }}
          </button>

          <button
            class="warning"
            @click="handleCompleteUpload"
            :disabled="loading.complete || !selectedFile || !stsData || !uploaded"
          >
            {{ loading.complete ? '提交中...' : '通知 Gin 落库' }}
          </button>
        </div>

        <div class="field">
          <label>STS 返回结果</label>
          <textarea :value="stsResult" readonly />
        </div>

        <div class="field">
          <label>OSS 上传结果</label>
          <textarea :value="ossUploadResult" readonly />
        </div>

        <div class="field">
          <label>落库结果</label>
          <textarea :value="completeResult" readonly />
        </div>
      </section>

      <section class="card">
        <h2>4. 一键完整测试</h2>
        <div class="actions">
          <button
            class="success"
            @click="handleFullFlow"
            :disabled="loading.fullFlow || !selectedFile || !token"
          >
            {{ loading.fullFlow ? '执行中...' : '一键执行完整流程' }}
          </button>
        </div>
      </section>

      <section class="card">
        <h2>日志</h2>
        <textarea :value="logs.join('\n')" readonly />
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import OSS from 'ali-oss'

const username = ref('')
const password = ref('')
const token = ref(localStorage.getItem('demo_jwt_token') || '')

const selectedFile = ref(null)
const stsData = ref(null)
const uploaded = ref(false)

const loginResult = ref('')
const stsResult = ref('')
const ossUploadResult = ref('')
const completeResult = ref('')

const logs = ref([])

const loading = ref({
  login: false,
  sts: false,
  upload: false,
  complete: false,
  fullFlow: false
})

function log(message, data = null) {
  const time = new Date().toLocaleTimeString()
  const line = data ? `[${time}] ${message} ${JSON.stringify(data)}` : `[${time}] ${message}`
  logs.value = [line, ...logs.value]
}

function setToken(newToken) {
  token.value = newToken || ''
  if (token.value) {
    localStorage.setItem('demo_jwt_token', token.value)
  } else {
    localStorage.removeItem('demo_jwt_token')
  }
}

function clearToken() {
  setToken('')
  log('已清除 Token')
}

function handleFileChange(event) {
  const file = event.target.files?.[0]
  selectedFile.value = file || null
  stsData.value = null
  uploaded.value = false
  stsResult.value = ''
  ossUploadResult.value = ''
  completeResult.value = ''

  if (file) {
    log('已选择文件', { name: file.name, size: file.size })
  }
}

async function handleLogin() {
  if (!username.value || !password.value) {
    loginResult.value = '请输入用户名和密码'
    return
  }

  loading.value.login = true
  try {
    const res = await axios.post('/api/login', {
      username: username.value,
      password: password.value
    })

    const jwt = res.data.token || res.data.access_token || ''
    setToken(jwt)

    loginResult.value = JSON.stringify(res.data, null, 2)
    log('登录成功')
  } catch (error) {
    loginResult.value = formatError(error)
    log('登录失败')
  } finally {
    loading.value.login = false
  }
}

async function handleGetSTS() {
  if (!token.value) {
    stsResult.value = '请先登录'
    return
  }
  if (!selectedFile.value) {
    stsResult.value = '请先选择文件'
    return
  }

  loading.value.sts = true
  try {
    const res = await axios.post(
      '/api/oss/sts',
      {
        original_name: selectedFile.value.name
      },
      {
        headers: {
          Authorization: `Bearer ${token.value}`
        }
      }
    )

    stsData.value = res.data
    stsResult.value = JSON.stringify(res.data, null, 2)
    uploaded.value = false
    log('获取 STS 成功', {
      objectKey: res.data.objectKey,
      bucket: res.data.bucket
    })
  } catch (error) {
    stsResult.value = formatError(error)
    log('获取 STS 失败')
  } finally {
    loading.value.sts = false
  }
}

async function handleUploadToOSS() {
  if (!stsData.value) {
    ossUploadResult.value = '请先获取 STS'
    return
  }
  if (!selectedFile.value) {
    ossUploadResult.value = '请先选择文件'
    return
  }

  loading.value.upload = true
  try {
    const client = new OSS({
      region: stsData.value.region,
      accessKeyId: stsData.value.accessKeyId,
      accessKeySecret: stsData.value.accessKeySecret,
      stsToken: stsData.value.securityToken,
      bucket: stsData.value.bucket,
      endpoint: `https://${stsData.value.endpoint}`
    })

    const result = await client.put(stsData.value.objectKey, selectedFile.value)

    uploaded.value = true
    ossUploadResult.value = JSON.stringify(
      {
        message: '上传成功',
        name: result.name,
        url: result.url
      },
      null,
      2
    )

    log('OSS 上传成功', {
      objectKey: stsData.value.objectKey
    })
  } catch (error) {
    uploaded.value = false
    ossUploadResult.value = formatError(error)
    log('OSS 上传失败')
  } finally {
    loading.value.upload = false
  }
}

async function handleCompleteUpload() {
  if (!uploaded.value || !stsData.value || !selectedFile.value) {
    completeResult.value = '请先成功上传到 OSS'
    return
  }

  loading.value.complete = true
  try {
    const ossUrl = `${stsData.value.baseUrl}/${stsData.value.objectKey}`

    const res = await axios.post(
      '/api/upload/complete',
      {
        original_name: selectedFile.value.name,
        object_key: stsData.value.objectKey,
        oss_url: ossUrl,
        file_size: selectedFile.value.size
      },
      {
        headers: {
          Authorization: `Bearer ${token.value}`
        }
      }
    )

    completeResult.value = JSON.stringify(res.data, null, 2)
    log('Gin 落库成功', {
      task_id: res.data.task_id
    })
  } catch (error) {
    completeResult.value = formatError(error)
    log('Gin 落库失败')
  } finally {
    loading.value.complete = false
  }
}

async function handleFullFlow() {
  if (!token.value) {
    completeResult.value = '请先登录'
    return
  }
  if (!selectedFile.value) {
    completeResult.value = '请先选择文件'
    return
  }

  loading.value.fullFlow = true
  try {
    await handleGetSTS()
    if (!stsData.value) return

    await handleUploadToOSS()
    if (!uploaded.value) return

    await handleCompleteUpload()
  } finally {
    loading.value.fullFlow = false
  }
}

function formatError(error) {
  if (error?.response?.data) {
    return JSON.stringify(error.response.data, null, 2)
  }
  return String(error)
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #f6f8fb;
  padding: 24px;
}

.container {
  max-width: 960px;
  margin: 0 auto;
}

h1 {
  margin-bottom: 8px;
  color: #111827;
}

.desc {
  margin-bottom: 20px;
  color: #6b7280;
}

.card {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
}

h2 {
  margin-top: 0;
  margin-bottom: 16px;
  color: #1f2937;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.field {
  margin-bottom: 14px;
}

label {
  display: block;
  margin-bottom: 6px;
  color: #6b7280;
  font-size: 14px;
}

input,
textarea,
button {
  width: 100%;
  box-sizing: border-box;
  border-radius: 12px;
  font-size: 14px;
}

input,
textarea {
  border: 1px solid #d1d5db;
  padding: 12px 14px;
}

textarea {
  min-height: 130px;
  resize: vertical;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
}

.actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.actions button {
  flex: 1;
  min-width: 180px;
  border: none;
  padding: 12px 14px;
  background: #2563eb;
  color: #fff;
  cursor: pointer;
}

.actions button:hover {
  background: #1d4ed8;
}

.actions button.secondary {
  background: #64748b;
}

.actions button.secondary:hover {
  background: #475569;
}

.actions button.success {
  background: #059669;
}

.actions button.success:hover {
  background: #047857;
}

.actions button.warning {
  background: #d97706;
}

.actions button.warning:hover {
  background: #b45309;
}

.actions button:disabled {
  background: #cbd5e1;
  cursor: not-allowed;
}

.status {
  margin-bottom: 12px;
  color: #374151;
  font-size: 14px;
}

.ok {
  color: #059669;
  font-weight: 600;
}

.warn {
  color: #d97706;
  font-weight: 600;
}

@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
