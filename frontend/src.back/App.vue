<template>
  <div class="app" :data-theme="theme">
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
        <JsonInput
          v-model="jsonInput"
          :error="error"
          @render="renderNotes"
          @clear="clearAll"
        />

        <StatsPanel
          v-if="notes.length > 0"
          :notes="notes"
        />

        <NotesList
          :notes="notes"
          @note-ref="registerNoteRef"
        />
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
import Sidebar from './components/Sidebar.vue'
import Header from './components/Header.vue'
import JsonInput from './components/JsonInput.vue'
import StatsPanel from './components/StatsPanel.vue'
import NotesList from './components/NotesList.vue'
import MobileOverlay from './components/MobileOverlay.vue'
import { parseNotesJSON, validateNotes } from './utils/parser'

// 主题状态
const theme = ref('light')
const sidebarCollapsed = ref(false)
const showMobileOverlay = ref(false)
const isMobile = ref(false)

// 数据状态
const jsonInput = ref('')
const notes = ref([])
const error = ref('')
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

    // 移动端关闭遮罩
    if (window.innerWidth <= 1024) {
      closeMobileOverlay()
    }
  }
}

// 渲染笔记
const renderNotes = () => {
  error.value = ''

  if (!jsonInput.value.trim()) {
    error.value = '请输入 JSON 数据'
    return
  }

  try {
    const rawData = parseNotesJSON(jsonInput.value)
    notes.value = validateNotes(rawData)
    currentNoteIndex.value = notes.value.length > 0 ? 0 : -1

    nextTick(() => {
      setupScrollSpy()
    })
  } catch (err) {
    error.value = err.message
  }
}

// 清空所有
const clearAll = () => {
  jsonInput.value = ''
  notes.value = []
  error.value = ''
  currentNoteIndex.value = -1
  noteRefs.value.clear()
}

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
  // 恢复主题设置
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme) {
    theme.value = savedTheme
    document.documentElement.setAttribute('data-theme', theme.value)
  }

  // 初始化响应式
  handleResize()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (observer) {
    observer.disconnect()
  }
})
</script>

<style scoped>
.app {
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
}
</style>
