<template>
  <div class="notes-viewer" :data-theme="theme">
    <Sidebar
      :notes="notes"
      :current-index="currentNoteIndex"
      :is-collapsed="sidebarCollapsed"
      :is-mobile="isMobile"
      @toggle="toggleSidebar"
      @navigate="scrollToNote"
    />

    <main class="main-content" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
      <Header
        :theme="theme"
        @toggle-theme="toggleTheme"
      />

      <div class="content-wrapper">
        <!-- <div class="page-actions">
          <button class="back-btn" @click="goBack">
            返回任务台
          </button>
        </div> -->

        <div v-if="isLoading" class="loading-state">
          正在加载笔记...
        </div>

        <div v-else-if="error" class="error-state">
          {{ error }}
        </div>

        <template v-else>
          <!-- 关键词展示区域 -->
          <div v-if="keywords.length > 0" class="keywords-section">
            <div class="keywords-label">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/>
                <line x1="7" y1="7" x2="7.01" y2="7"/>
              </svg>
              关键词
            </div>
            <div class="keywords-list">
              <span
                v-for="(keyword, index) in keywords"
                :key="index"
                class="keyword-tag"
              >
                {{ keyword }}
              </span>
            </div>
          </div>

          <StatsPanel
            v-if="notes.length > 0"
            :notes="notes"
          />

          <NotesList
            :notes="notes"
            @note-ref="registerNoteRef"
          />

          <div v-if="notes.length === 0" class="empty-state">
            暂无笔记结果
          </div>
        </template>
      </div>
    </main>

    <MobileOverlay
      :show="showMobileOverlay"
      @click="closeMobileOverlay"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'

import Sidebar from '../components/Sidebar.vue'
import Header from '../components/Header.vue'
import StatsPanel from '../components/StatsPanel.vue'
import NotesList from '../components/NotesList.vue'
import MobileOverlay from '../components/MobileOverlay.vue'

import { parseNotesJSON, validateNotes } from '../utils/parser'
import { getNoteByTaskIdApi } from '../api/note.js'

const route = useRoute()
// const router = useRouter()

// 主题状态
const theme = ref('light')
const sidebarCollapsed = ref(false)
const showMobileOverlay = ref(false)
const isMobile = ref(false)

// 数据状态
const jsonInput = ref('')
const notes = ref([])
const keywords = ref([])
const error = ref('')
const isLoading = ref(false)
const currentNoteIndex = ref(-1)
const noteRefs = ref(new Map())

// 切换主题
const toggleTheme = () => {
  theme.value = theme.value === 'light' ? 'dark' : 'light'
  document.documentElement.setAttribute('data-theme', theme.value)
  localStorage.setItem('theme', theme.value)
}

// 切换 Sidebar
const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value

  if (window.innerWidth <= 1024) {
    showMobileOverlay.value = !sidebarCollapsed.value
  }
}

// 关闭移动端遮罩
const closeMobileOverlay = () => {
  showMobileOverlay.value = false
  sidebarCollapsed.value = true
}

// 注册笔记引用
const registerNoteRef = (el, index) => {
  if (el) {
    noteRefs.value.set(index, el)
  }
}

// 滚动到指定笔记
const scrollToNote = (index) => {
  const noteEl = noteRefs.value.get(index)

  if (noteEl) {
    const headerOffset = 100
    const elementPosition = noteEl.getBoundingClientRect().top
    const offsetPosition = elementPosition + window.pageYOffset - headerOffset

    window.scrollTo({
      top: offsetPosition,
      behavior: 'smooth'
    })

    currentNoteIndex.value = index

    if (window.innerWidth <= 1024) {
      closeMobileOverlay()
    }
  }
}

// 提取关键词（最多5个）
const extractKeywords = (data) => {
  const json_data = JSON.parse(data)
  console.log(json_data.keywords)
  if (!json_data) return []

  // 尝试从不同位置获取关键词
  let rawKeywords = json_data.keywords

  // 限制最多5个关键词
  if (rawKeywords && rawKeywords.length > 0) {
    return rawKeywords.slice(0, 5).map(k => String(k).trim()).filter(k => k)
  }

  return []
}

// 根据 JSON 字符串渲染笔记
const renderNotesFromJSON = (rawJson) => {
  error.value = ''

  if (!rawJson || !rawJson.trim()) {
    error.value = '笔记结果为空'
    return
  }

  try {
    const rawData = parseNotesJSON(rawJson)
    notes.value = validateNotes(rawData)
    keywords.value = extractKeywords(rawJson)
    currentNoteIndex.value = notes.value.length > 0 ? 0 : -1

    nextTick(() => {
      setupScrollSpy()
    })
  } catch (err) {
    console.error('解析笔记 JSON 失败:', err)
    error.value = err.message || '解析笔记 JSON 失败'
  }
}

// 从后端获取笔记
const fetchNote = async () => {
  const taskId = route.query.taskId

  if (!taskId) {
    error.value = '缺少 taskId 参数'
    return
  }

  isLoading.value = true
  error.value = ''

  try {
    const res = await getNoteByTaskIdApi(taskId)

    console.log('笔记接口返回：', res)

    let rawJson = ''

    // 1. 兼容旧版：结果表直接返回 json_result 字符串
    if (typeof res?.json_result === 'string') {
      rawJson = res.json_result
    } else if (typeof res?.JsonResult === 'string') {
      rawJson = res.JsonResult
    } else if (typeof res?.note?.json_result === 'string') {
      rawJson = res.note.json_result
    } else if (typeof res?.note?.JsonResult === 'string') {
      rawJson = res.note.JsonResult

    // 2. 兼容新版：note 直接就是对象
    } else if (res?.note && typeof res.note === 'object') {
      rawJson = JSON.stringify(res.note)

    // 3. 兼容从 python 状态接口直接拿结构化结果
    } else if (res?.data?.structured_note_json && typeof res.data.structured_note_json === 'object') {
      rawJson = JSON.stringify(res.data.structured_note_json)

    // 4. 兼容最外层直接返回 notes
    } else if (Array.isArray(res?.notes)) {
      rawJson = JSON.stringify({ notes: res.notes })
    } else if (Array.isArray(res?.data?.notes)) {
      rawJson = JSON.stringify({ notes: res.data.notes })
    }

    jsonInput.value = rawJson

    renderNotesFromJSON(rawJson)
  } catch (err) {
    console.error('获取笔记失败:', err)
    error.value = err.error || err.message || '获取笔记失败'
  } finally {
    isLoading.value = false
  }
}

// 清空所有
// const clearAll = () => {
//   jsonInput.value = ''
//   notes.value = []
//   error.value = ''
//   currentNoteIndex.value = -1
//   noteRefs.value.clear()
// }

// 滚动监听
let observer = null

const setupScrollSpy = () => {
  if (observer) {
    observer.disconnect()
  }

  const options = {
    root: null,
    rootMargin: '-20% 0px -60% 0px',
    threshold: 0
  }

  observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const index = parseInt(entry.target.dataset.index)
        currentNoteIndex.value = index
      }
    })
  }, options)

  noteRefs.value.forEach((el) => {
    observer.observe(el)
  })
}

// 响应式处理
const handleResize = () => {
  isMobile.value = window.innerWidth <= 1024

  if (isMobile.value) {
    sidebarCollapsed.value = true
  } else {
    showMobileOverlay.value = false
  }
}

// 生命周期
onMounted(() => {
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme) {
    theme.value = savedTheme
    document.documentElement.setAttribute('data-theme', theme.value)
  }

  handleResize()
  window.addEventListener('resize', handleResize)

  fetchNote()
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)

  if (observer) {
    observer.disconnect()
  }
})
</script>

<style scoped>
.notes-viewer {
  display: flex;
  min-height: 100vh;
  background-color: var(--bg-primary);
}

.main-content {
  flex: 1;
  margin-left: var(--sidebar-width);
  transition: margin-left var(--transition-base);
  min-height: 100vh;
}

.main-content.sidebar-collapsed {
  margin-left: var(--sidebar-collapsed);
}

.content-wrapper {
  max-width: 900px;
  margin: 0 auto;
  padding: 0 48px 64px;
}

/* 关键词展示区域 */
.keywords-section {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  margin-bottom: 24px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 12px;
}

.keywords-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-secondary);
  flex-shrink: 0;
}

.keywords-label svg {
  width: 16px;
  height: 16px;
  stroke: var(--text-muted);
}

.keywords-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  flex: 1;
}

.keyword-tag {
  display: inline-flex;
  align-items: center;
  padding: 6px 14px;
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--text-primary);
  background: var(--bg-elevated);
  border: 1px solid var(--border-default);
  border-radius: 20px;
  transition: all var(--transition-fast);
}

.keyword-tag:hover {
  background: var(--highlight-bg);
  border-color: var(--text-primary);
  transform: translateY(-1px);
}

@media (max-width: 1024px) {
  .main-content {
    margin-left: 0;
  }

  .main-content.sidebar-collapsed {
    margin-left: 0;
  }

  .content-wrapper {
    padding: 0 24px 48px;
  }
}

@media (max-width: 640px) {
  .content-wrapper {
    padding: 0 16px 32px;
  }

  .keywords-section {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
    padding: 14px 16px;
  }

  .keywords-list {
    width: 100%;
  }
}
</style>
