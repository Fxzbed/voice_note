<template>
  <div class="dashboard-page" :data-theme="theme">
    <!-- 导航栏 -->
    <nav class="dashboard-nav">
      <router-link to="/dashboard" class="nav-brand">
        <svg class="brand-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
          <polyline points="14 2 14 8 20 8"/>
        </svg>
        <span class="brand-text">NoteGen</span>
      </router-link>
      <div class="nav-right">
        <router-link to="/dashboard" class="nav-link active">任务台</router-link>
        <span class="nav-user">{{ user.username }}</span>
        <button class="theme-toggle" @click="toggleTheme">
          <svg v-if="theme === 'light'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="5"/>
            <line x1="12" y1="1" x2="12" y2="3"/>
            <line x1="12" y1="21" x2="12" y2="23"/>
            <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
            <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
            <line x1="1" y1="12" x2="3" y2="12"/>
            <line x1="21" y1="12" x2="23" y2="12"/>
            <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
            <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
          </svg>
          <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
          </svg>
        </button>
      </div>
    </nav>

    <!-- 主内容区 -->
    <main class="dashboard-content">
      <div class="dashboard-container">
        <!-- 上传区域 -->
        <section class="upload-section">
          <h2 class="section-title">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="17 8 12 3 7 8"/>
              <line x1="12" y1="3" x2="12" y2="15"/>
            </svg>
            上传音频
          </h2>

          <div
            class="upload-area"
            :class="{ dragging: isDragging, uploading: isUploading }"
            @dragenter.prevent="isDragging = true"
            @dragleave.prevent="isDragging = false"
            @dragover.prevent
            @drop.prevent="handleDrop"
          >
            <input
              ref="fileInput"
              type="file"
              accept="audio/*,video/*,.mp3,.wav,.m4a,.flac,.aac,.mp4"
              class="file-input"
              @change="handleFileSelect"
            />
            <div class="upload-content">
              <div class="upload-icon">
                <svg v-if="!isUploading" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                  <polyline points="17 8 12 3 7 8"/>
                  <line x1="12" y1="3" x2="12" y2="15"/>
                </svg>
                <div v-else class="upload-spinner"></div>
              </div>
              <p class="upload-text">
                <span v-if="!isUploading">点击或拖拽音频文件至此处</span>
                <span v-else>正在上传...</span>
              </p>
              <p class="upload-hint">支持 MP3、WAV、M4A、FLAC、AAC、MP4 格式</p>
            </div>
          </div>
        </section>

        <!-- 历史任务 -->
        <section class="tasks-section">
          <div class="section-header">
            <h2 class="section-title">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
                <line x1="16" y1="13" x2="8" y2="13"/>
                <line x1="16" y1="17" x2="8" y2="17"/>
                <polyline points="10 9 9 9 8 9"/>
              </svg>
              历史任务
              <span class="task-count">({{ tasks.length }})</span>
            </h2>
            <button class="refresh-btn" @click="fetchTasks" :disabled="isLoading">
              <svg :class="{ spinning: isLoading }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="23 4 23 10 17 10"/>
                <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
              </svg>
              刷新
            </button>
          </div>

          <div v-if="isLoading && tasks.length === 0" class="loading-state">
            <div class="loading-spinner"></div>
            <p>加载中...</p>
          </div>

          <div v-else-if="tasks.length === 0" class="empty-state">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
            </svg>
            <p>暂无任务</p>
            <span>上传音频文件开始创建任务</span>
          </div>

          <div v-else class="tasks-list">
            <div
              v-for="task in tasks"
              :key="task.id"
              class="task-card"
              :class="`status-${task.status}`"
            >
              <div class="task-info">
                <h3 class="task-title">{{ task.title || task.file_name || task.filename || task.original_name || '未命名任务' }}</h3>
                <p class="task-meta">
                  <span class="task-date">{{ formatDate(task.createdAt || task.created_at) }}</span>
                  <span class="task-duration">{{ task.duration || '待计算' }}</span>
                </p>
              </div>

              <div class="task-status">
                <span :class="['status-badge', normalizeStatus(task.status)]">
                  {{ getStatusText(task.status) }}
                </span>
              </div>

              <div class="task-actions">
                <button
                  v-if="canViewTask(task.status)"
                  class="action-btn view"
                  @click="viewTask(task)"
                >
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                    <circle cx="12" cy="12" r="3"/>
                  </svg>
                  查看
                </button>

                <button
                  v-if="canStartTask(task.status)"
                  class="action-btn retry"
                  @click="retryTask(task)"
                >
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="23 4 23 10 17 10"/>
                    <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
                  </svg>
                  开始
                </button>

                <button
                  v-if="canRefreshTask(task.status)"
                  class="action-btn retry"
                  @click="refreshTask(task)"
                >
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="23 4 23 10 17 10"/>
                    <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
                  </svg>
                  刷新
                </button>

                <button class="action-btn delete" @click="deleteTask(task)">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="3 6 5 6 21 6"/>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                  </svg>
                  删除
                </button>
              </div>
            </div>
          </div>
        </section>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import OSS from 'ali-oss'
import { useUser } from '../store/user.js'
import { getNoteByTaskIdApi } from '@/api/note'
import {
  getTasksApi,
  createPythonTaskApi,
  getOssStsApi,
  completeUploadApi,
  deleteTaskApi,
  getPythonTaskApi
} from '@/api/task'

const router = useRouter()
const { user, initUser } = useUser()

const theme = ref('light')
const isDragging = ref(false)
const isUploading = ref(false)
const isLoading = ref(false)
const fileInput = ref(null)
const tasks = ref([])

const toggleTheme = () => {
  theme.value = theme.value === 'light' ? 'dark' : 'light'
  document.documentElement.setAttribute('data-theme', theme.value)
  localStorage.setItem('theme', theme.value)
}

const isSupportedMediaFile = (file) => {
  if (!file) return false
  const name = file.name.toLowerCase()

  return (
    file.type.startsWith('audio/') ||
    file.type.startsWith('video/') ||
    name.endsWith('.mp3') ||
    name.endsWith('.wav') ||
    name.endsWith('.m4a') ||
    name.endsWith('.flac') ||
    name.endsWith('.aac') ||
    name.endsWith('.mp4')
  )
}

const handleFileSelect = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  if (!isSupportedMediaFile(file)) {
    alert('仅支持音频或课堂视频文件')
    if (fileInput.value) fileInput.value.value = ''
    return
  }

  await uploadFile(file)
}

const handleDrop = async (event) => {
  isDragging.value = false
  const file = event.dataTransfer.files[0]

  if (!file) return

  if (!isSupportedMediaFile(file)) {
    alert('仅支持音频或课堂视频文件')
    return
  }

  await uploadFile(file)
}

const uploadFile = async (file) => {
  isUploading.value = true

  try {
    // 1. 获取 STS 临时凭证
    const sts = await getOssStsApi(file.name)
    console.log('STS 返回：', sts)

    // 2. 直传 OSS
    const client = new OSS({
      region: sts.region,
      accessKeyId: sts.accessKeyId,
      accessKeySecret: sts.accessKeySecret,
      stsToken: sts.securityToken,
      bucket: sts.bucket,
      endpoint: `https://${sts.endpoint}`
    })

    const putResult = await client.put(sts.objectKey, file)
    console.log('OSS 上传返回：', putResult)

    // 3. 通知 Gin 落库
    const ossUrl = `${sts.baseUrl}/${sts.objectKey}`
    const res = await completeUploadApi({
      original_name: file.name,
      object_key: sts.objectKey,
      oss_url: ossUrl,
      file_size: file.size
    })

    console.log('落库返回：', res)

    alert('上传成功')
    await fetchTasks()
  } catch (error) {
    console.error('上传失败:', error)
    alert(error?.error || error?.message || '上传失败')
  } finally {
    isUploading.value = false

    if (fileInput.value) {
      fileInput.value.value = ''
    }
  }
}

const fetchTasks = async () => {
  isLoading.value = true

  try {
    const res = await getTasksApi()
    console.log('任务列表返回：', res)

    tasks.value = res.tasks || res.data || []
  } catch (error) {
    console.error('获取任务失败:', error)
    tasks.value = []
  } finally {
    isLoading.value = false
  }
}

const refreshTask = async (task) => {
  try {
    const res = await getPythonTaskApi(task.id)
    console.log('查Python任务:', res)

    await fetchTasks()
  } catch (error) {
    console.error('任务更新失败', error)
    alert(error?.error || error?.message || 'Python 任务更新失败')
  }
}

const retryTask = async (task) => {
  try {
    const res = await createPythonTaskApi(task.id)
    console.log('Python 任务提交成功：', res)

    alert('已重新提交处理任务')
    await fetchTasks()
  } catch (error) {
    console.error('提交 Python 任务失败:', error)
    alert(error?.error || error?.message || '提交 Python 任务失败')
  }
}

const deleteTask = async (task) => {
  const ok = window.confirm(`确认删除任务「${task.original_name || task.file_name || task.id}」吗？`)
  if (!ok) return

  try {
    const res = await deleteTaskApi(task.id)
    console.log('删除成功：', res)
    alert('删除成功')
    await fetchTasks()
  } catch (error) {
    console.error('删除失败:', error)
    alert(error?.error || error?.message || '删除失败')
  }
}

const viewTask = async (task) => {
  try {
    const res = await getNoteByTaskIdApi(task.id)
    console.log('笔记结果：', res.note)

    router.push(`/notes?taskId=${task.id}`)
  } catch (error) {
    console.error('获取笔记失败:', error)
    alert(error?.error || error?.message || '获取笔记失败')
  }
}

const formatDate = (dateString) => {
  if (!dateString) return '未知时间'
  const date = new Date(dateString)
  if (Number.isNaN(date.getTime())) return '未知时间'

  return date.toLocaleString('zh-CN', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const normalizeStatus = (status) => {
  const s = String(status || '').toLowerCase()

  if ([
    'completed',
    'note_done',
  ].includes(s)) return 'completed'

  if ([
    'uploaded',
    'submitted',
    'pending',
    'download_processing',
    'download_done',
    'vad_processing',
    'vad_done',
    'asr_processing',
    'asr_done',
    'note_generating',
    'processing'
  ].includes(s)) return 'processing'

  if ([
    'failed',
    'download_failed',
    'vad_failed',
    'asr_failed',
    'note_failed'
  ].includes(s)) return 'failed'

  return 'pending'
}

const getStatusText = (status) => {
  const statusMap = {
    pending: '等待中',
    uploaded: '已上传',
    submitted: '已提交',
    download_processing: '文件下载中',
    download_done: '文件下载完成',
    vad_processing: 'VAD处理中',
    vad_done: 'VAD完成',
    asr_processing: 'ASR处理中',
    asr_done: 'ASR完成',
    note_generating: '笔记生成中',
    note_done: '已完成',
    processing: '处理中',
    completed: '已完成',
    failed: '失败',
    download_failed: '文件下载失败',
    vad_failed: 'VAD失败',
    asr_failed: 'ASR失败',
    note_failed: '笔记失败'
  }

  return statusMap[String(status || '').toLowerCase()] || status
}

const canRefreshTask = (status) => {
  return ['submitted',
    'pending',
    'download_processing',
    'download_done',
    'vad_processing',
    'vad_done',
    'asr_processing',
    'asr_done',
    'note_generating',
    'processing'].includes(String(status || '').toLowerCase())
}

const canStartTask = (status) => {
  return ['uploaded', 'pending'].includes(String(status || '').toLowerCase())
}

const canViewTask = (status) => {
  return ['completed', 'note_done', 'asr_done'].includes(String(status || '').toLowerCase())
}

onMounted(() => {
  initUser()

  if (!user.value.isLoggedIn) {
    router.push('/login')
    return
  }

  const savedTheme = localStorage.getItem('theme')
  if (savedTheme) {
    theme.value = savedTheme
    document.documentElement.setAttribute('data-theme', theme.value)
  }

  fetchTasks()
})
</script>

<style scoped>
.dashboard-page {
  min-height: 100vh;
  background: var(--bg-primary);
  color: var(--text-primary);
}

/* 导航栏 */
.dashboard-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 48px;
  height: 72px;
  border-bottom: 1px solid var(--border-subtle);
  background: var(--bg-primary);
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  text-decoration: none;
  cursor: pointer;
}

.brand-icon {
  width: 32px;
  height: 32px;
  stroke: var(--text-primary);
}

.brand-text {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 32px;
}

.nav-link {
  font-size: 0.95rem;
  color: var(--text-secondary);
  text-decoration: none;
  transition: color var(--transition-fast);
}

.nav-link:hover,
.nav-link.active {
  color: var(--text-primary);
}

.nav-user {
  font-size: 0.95rem;
  color: var(--text-primary);
  font-weight: 600;
}

.theme-toggle {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-secondary);
  border: 1px solid var(--border-default);
  border-radius: 8px;
  cursor: pointer;
  color: var(--text-secondary);
  transition: all var(--transition-fast);
}

.theme-toggle:hover {
  background: var(--hover-bg);
  color: var(--text-primary);
}

.theme-toggle svg {
  width: 20px;
  height: 20px;
}

/* 主内容 */
.dashboard-content {
  padding: 40px 48px;
}

.dashboard-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 40px;
}

/* 区域标题 */
.section-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 20px;
}

.section-title svg {
  width: 24px;
  height: 24px;
  stroke: var(--text-secondary);
}

.task-count {
  font-size: 0.9rem;
  color: var(--text-muted);
  font-weight: 400;
}

/* 上传区域 */
.upload-section {
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  border-radius: 20px;
  padding: 32px;
}

.upload-area {
  border: 2px dashed var(--border-default);
  border-radius: 16px;
  padding: 60px 40px;
  text-align: center;
  cursor: pointer;
  transition: all var(--transition-fast);
  position: relative;
}

.upload-area:hover,
.upload-area.dragging {
  border-color: var(--text-primary);
  background: var(--highlight-bg);
}

.upload-area.uploading {
  pointer-events: none;
  opacity: 0.7;
}

.file-input {
  position: absolute;
  inset: 0;
  opacity: 0;
  cursor: pointer;
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.upload-icon {
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-tertiary);
  border-radius: 50%;
}

.upload-icon svg {
  width: 28px;
  height: 28px;
  stroke: var(--text-primary);
}

.upload-spinner {
  width: 28px;
  height: 28px;
  border: 3px solid var(--text-primary);
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.upload-text {
  font-size: 1.1rem;
  color: var(--text-primary);
  font-weight: 500;
}

.upload-hint {
  font-size: 0.85rem;
  color: var(--text-muted);
}

/* 任务区域 */
.tasks-section {
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  border-radius: 20px;
  padding: 32px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.refresh-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-default);
  border-radius: 8px;
  font-size: 0.9rem;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.refresh-btn:hover:not(:disabled) {
  background: var(--hover-bg);
  color: var(--text-primary);
}

.refresh-btn svg {
  width: 16px;
  height: 16px;
}

.refresh-btn svg.spinning {
  animation: spin 1s linear infinite;
}

/* 加载状态 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 60px;
  color: var(--text-muted);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-default);
  border-top-color: var(--text-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 60px;
  color: var(--text-muted);
  text-align: center;
}

.empty-state svg {
  width: 48px;
  height: 48px;
  stroke: var(--border-strong);
}

.empty-state p {
  font-size: 1.1rem;
  color: var(--text-secondary);
}

.empty-state span {
  font-size: 0.9rem;
}

/* 任务列表 */
.tasks-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.task-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: var(--bg-secondary);
  border-radius: 12px;
  border-left: 4px solid var(--border-default);
  transition: all var(--transition-fast);
}

.task-card:hover {
  background: var(--highlight-bg);
  transform: translateX(4px);
}

.task-card.status-processing {
  border-left-color: #f59e0b;
}

.task-card.status-completed {
  border-left-color: #10b981;
}

.task-card.status-failed {
  border-left-color: #ef4444;
}

.task-info {
  flex: 1;
  min-width: 0;
}

.task-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.task-meta {
  display: flex;
  gap: 12px;
  font-size: 0.8rem;
  color: var(--text-muted);
}

.task-status {
  flex-shrink: 0;
}

.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
}

.status-badge.pending {
  background: rgba(107, 114, 128, 0.1);
  color: #6b7280;
}

.status-badge.processing {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.status-badge.completed {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.status-badge.failed {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.task-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border: none;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.action-btn svg {
  width: 14px;
  height: 14px;
}

.action-btn.view {
  background: var(--text-primary);
  color: var(--bg-primary);
}

.action-btn.view:hover {
  opacity: 0.9;
}

.action-btn.retry {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.action-btn.retry:hover {
  background: rgba(245, 158, 11, 0.2);
}

.action-btn.delete {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.action-btn.delete:hover {
  background: rgba(239, 68, 68, 0.2);
}

/* 响应式 */
@media (max-width: 768px) {
  .dashboard-nav {
    padding: 0 24px;
  }

  .nav-right {
    gap: 16px;
  }

  .dashboard-content {
    padding: 24px;
  }

  .task-card {
    flex-wrap: wrap;
  }

  .task-actions {
    width: 100%;
    justify-content: flex-end;
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid var(--border-subtle);
  }
}
</style>
