<template>
  <aside 
    class="sidebar" 
    :class="{ 
      'collapsed': isCollapsed,
      'mobile-open': !isCollapsed && isMobile
    }"
  >
    <div class="sidebar-header">
      <div class="sidebar-brand" v-show="!isCollapsed || isMobile">
        <span class="brand-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
            <line x1="16" y1="13" x2="8" y2="13"/>
            <line x1="16" y1="17" x2="8" y2="17"/>
            <polyline points="10 9 9 9 8 9"/>
          </svg>
        </span>
        <span class="brand-text">笔记导航</span>
      </div>
      <button 
        class="toggle-btn" 
        @click="$emit('toggle')"
        :title="isCollapsed ? '展开' : '收起'"
      >
        <svg 
          viewBox="0 0 24 24" 
          fill="none" 
          stroke="currentColor" 
          stroke-width="2"
          :class="{ 'rotated': isCollapsed }"
        >
          <path d="M15 18l-6-6 6-6"/>
        </svg>
      </button>
    </div>

    <div class="sidebar-content" v-show="!isCollapsed || isMobile">
      <!-- 笔记段落导航 -->
      <div class="nav-section" v-if="notes.length > 0">
        <div class="nav-section-title">笔记段落</div>
        <div class="nav-list">
          <div
            v-for="(note, index) in notes"
            :key="note.id"
            class="nav-item"
            :class="{ 'active': currentIndex === index }"
            @click="$emit('navigate', index)"
          >
            <div class="nav-item-header">
              <span class="nav-number">#{{ index + 1 }}</span>
              <span class="nav-kp-count">{{ note.knowledge_points.length }} 知识点</span>
            </div>
            <div class="nav-summary">{{ truncateSummary(note.summary) }}</div>
          </div>
        </div>
      </div>

      <!-- 知识点快速跳转 -->
      <div class="nav-section" v-if="allKnowledgePoints.length > 0">
        <div class="nav-section-title">知识点索引</div>
        <div class="kp-list">
          <div
            v-for="(kp, idx) in allKnowledgePoints"
            :key="idx"
            class="kp-item"
            @click="$emit('navigate', kp.noteIndex)"
          >
            <span class="kp-bullet"></span>
            <span class="kp-text">{{ truncateText(kp.text, 30) }}</span>
            <span class="kp-ref">#{{ kp.noteIndex + 1 }}</span>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div class="empty-nav" v-if="notes.length === 0">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
          <polyline points="14 2 14 8 20 8"/>
        </svg>
        <p>暂无笔记数据</p>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  notes: {
    type: Array,
    default: () => []
  },
  currentIndex: {
    type: Number,
    default: -1
  },
  isCollapsed: {
    type: Boolean,
    default: false
  },
  isMobile: {
    type: Boolean,
    default: false
  }
})

defineEmits(['toggle', 'navigate'])

// 收集所有知识点用于索引
const allKnowledgePoints = computed(() => {
  const points = []
  props.notes.forEach((note, noteIndex) => {
    note.knowledge_points.forEach((text, kpIndex) => {
      points.push({
        text,
        noteIndex,
        kpIndex,
        id: `${noteIndex}-${kpIndex}`
      })
    })
  })
  return points
})

// 截断摘要
function truncateSummary(text) {
  if (!text) return '无摘要'
  return text.length > 50 ? text.substring(0, 50) + '...' : text
}

// 截断文本
function truncateText(text, maxLength) {
  if (!text) return ''
  return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
}
</script>

<style scoped>
.sidebar {
  position: fixed;
  left: 0;
  top: 0;
  height: 100vh;
  width: var(--sidebar-width);
  background-color: var(--bg-secondary);
  border-right: 1px solid var(--border-subtle);
  display: flex;
  flex-direction: column;
  transition: width var(--transition-base), transform var(--transition-base);
  z-index: 100;
}

.sidebar.collapsed {
  width: var(--sidebar-collapsed);
}

.sidebar-header {
  height: var(--header-height);
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--border-subtle);
  flex-shrink: 0;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  overflow: hidden;
}

.brand-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-tertiary);
  border-radius: 8px;
  flex-shrink: 0;
}

.brand-icon svg {
  width: 20px;
  height: 20px;
  stroke: var(--text-primary);
}

.brand-text {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
}

.toggle-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 1px solid var(--border-default);
  border-radius: 6px;
  cursor: pointer;
  transition: all var(--transition-fast);
  flex-shrink: 0;
}

.toggle-btn:hover {
  background: var(--hover-bg);
  border-color: var(--border-strong);
}

.toggle-btn svg {
  width: 16px;
  height: 16px;
  stroke: var(--text-secondary);
  transition: transform var(--transition-base);
}

.toggle-btn svg.rotated {
  transform: rotate(180deg);
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px 12px;
}

.nav-section {
  margin-bottom: 24px;
}

.nav-section-title {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted);
  padding: 0 12px;
  margin-bottom: 8px;
}

.nav-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-item {
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all var(--transition-fast);
  border-left: 2px solid transparent;
}

.nav-item:hover {
  background: var(--hover-bg);
}

.nav-item.active {
  background: var(--highlight-bg);
  border-left-color: var(--text-primary);
}

.nav-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.nav-number {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-primary);
  font-family: 'JetBrains Mono', monospace;
}

.nav-kp-count {
  font-size: 0.7rem;
  color: var(--text-muted);
  background: var(--bg-tertiary);
  padding: 2px 6px;
  border-radius: 4px;
}

.nav-summary {
  font-size: 0.85rem;
  color: var(--text-secondary);
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.nav-item.active .nav-summary {
  color: var(--text-primary);
}

/* 知识点索引 */
.kp-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.kp-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.kp-item:hover {
  background: var(--hover-bg);
}

.kp-bullet {
  width: 6px;
  height: 6px;
  background: var(--text-muted);
  border-radius: 50%;
  flex-shrink: 0;
}

.kp-text {
  flex: 1;
  font-size: 0.8rem;
  color: var(--text-secondary);
  line-height: 1.4;
}

.kp-ref {
  font-size: 0.7rem;
  color: var(--text-muted);
  font-family: 'JetBrains Mono', monospace;
}

/* 空状态 */
.empty-nav {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  color: var(--text-muted);
  text-align: center;
}

.empty-nav svg {
  width: 48px;
  height: 48px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-nav p {
  font-size: 0.9rem;
}

/* 移动端适配 */
@media (max-width: 1024px) {
  .sidebar {
    transform: translateX(-100%);
    width: var(--sidebar-width) !important;
  }
  
  .sidebar.mobile-open {
    transform: translateX(0);
  }
  
  .sidebar-header {
    padding: 0 16px;
  }
  
  .sidebar-brand {
    display: flex !important;
  }
}

/* 滚动条 */
.sidebar-content::-webkit-scrollbar {
  width: 4px;
}

.sidebar-content::-webkit-scrollbar-track {
  background: transparent;
}

.sidebar-content::-webkit-scrollbar-thumb {
  background: var(--border-default);
  border-radius: 2px;
}
</style>
