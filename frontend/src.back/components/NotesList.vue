<template>
  <section class="notes-section">
    <h2 class="section-title">
      <span class="title-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
          <polyline points="14 2 14 8 20 8"/>
          <line x1="16" y1="13" x2="8" y2="13"/>
          <line x1="16" y1="17" x2="8" y2="17"/>
          <polyline points="10 9 9 9 8 9"/>
        </svg>
      </span>
      课堂笔记
      <span v-if="notes.length > 0" class="title-count">({{ notes.length }})</span>
    </h2>
    
    <div v-if="notes.length > 0" class="notes-list">
      <article
        v-for="(note, index) in notes"
        :key="note.id"
        :id="note.id"
        :ref="(el) => setItemRef(el, index)"
        :data-index="index"
        class="note-card"
      >
        <div class="note-header">
          <div class="note-meta">
            <span class="note-number">段落 #{{ String(index + 1).padStart(2, '0') }}</span>
            <span class="note-divider"></span>
            <span class="note-kp-count">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                <polyline points="22 4 12 14.01 9 11.01"/>
              </svg>
              {{ note.knowledge_points.length }} 个知识点
            </span>
          </div>
        </div>
        
        <div class="note-summary">
          {{ note.summary || '暂无摘要' }}
        </div>
        
        <div class="note-knowledge">
          <div class="knowledge-header">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="16" x2="12" y2="12"/>
              <line x1="12" y1="8" x2="12.01" y2="8"/>
            </svg>
            知识点
          </div>
          <div class="knowledge-list">
            <div
              v-for="(kp, kpIndex) in note.knowledge_points"
              :key="kpIndex"
              class="knowledge-item"
            >
              <span class="knowledge-number">{{ kpIndex + 1 }}</span>
              <span class="knowledge-text">{{ kp }}</span>
            </div>
          </div>
        </div>
      </article>
    </div>
    
    <div v-else class="empty-state">
      <div class="empty-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
          <polyline points="14 2 14 8 20 8"/>
          <line x1="16" y1="13" x2="8" y2="13"/>
          <line x1="16" y1="17" x2="8" y2="17"/>
          <polyline points="10 9 9 9 8 9"/>
        </svg>
      </div>
      <h3 class="empty-title">暂无笔记</h3>
      <p class="empty-desc">在上方粘贴 JSON 数据并点击「渲染笔记」按钮开始</p>
    </div>
  </section>
</template>

<script setup>
const props = defineProps({
  notes: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['note-ref'])

// 设置元素引用
const setItemRef = (el, index) => {
  if (el) {
    emit('note-ref', el, index)
  }
}
</script>

<style scoped>
.notes-section {
  padding-top: 16px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-subtle);
}

.title-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-tertiary);
  border-radius: 8px;
}

.title-icon svg {
  width: 18px;
  height: 18px;
  stroke: var(--text-secondary);
}

.title-count {
  font-size: 0.9rem;
  color: var(--text-muted);
  font-weight: 400;
  font-family: 'JetBrains Mono', monospace;
}

.notes-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.note-card {
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  border-radius: 20px;
  padding: 32px;
  transition: all var(--transition-fast);
  position: relative;
}

.note-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--text-primary);
  opacity: 0;
  transition: opacity var(--transition-fast);
  border-radius: 20px 20px 0 0;
}

.note-card:hover {
  border-color: var(--border-default);
  box-shadow: var(--shadow-lg);
  transform: translateY(-2px);
}

.note-card:hover::before {
  opacity: 1;
}

.note-header {
  margin-bottom: 20px;
}

.note-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.note-number {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-primary);
  font-family: 'JetBrains Mono', monospace;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.note-divider {
  width: 4px;
  height: 4px;
  background: var(--text-muted);
  border-radius: 50%;
}

.note-kp-count {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.8rem;
  color: var(--text-muted);
}

.note-kp-count svg {
  width: 14px;
  height: 14px;
}

.note-summary {
  font-size: 1.1rem;
  line-height: 1.8;
  color: var(--text-primary);
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px dashed var(--border-subtle);
}

.note-knowledge {
  margin-top: 8px;
}

.knowledge-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 16px;
}

.knowledge-header svg {
  width: 14px;
  height: 14px;
}

.knowledge-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.knowledge-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px 16px;
  background: var(--bg-secondary);
  border-radius: 10px;
  border-left: 3px solid var(--border-strong);
  transition: all var(--transition-fast);
}

.knowledge-item:hover {
  background: var(--highlight-bg);
  border-left-color: var(--text-primary);
  transform: translateX(4px);
}

.knowledge-number {
  width: 22px;
  height: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--text-primary);
  color: var(--bg-primary);
  border-radius: 50%;
  font-size: 0.7rem;
  font-weight: 600;
  flex-shrink: 0;
  margin-top: 2px;
  font-family: 'JetBrains Mono', monospace;
}

.knowledge-text {
  flex: 1;
  font-size: 0.95rem;
  color: var(--text-secondary);
  line-height: 1.6;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 80px 40px;
  color: var(--text-muted);
}

.empty-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 24px;
  background: var(--bg-tertiary);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-icon svg {
  width: 36px;
  height: 36px;
  stroke: var(--border-strong);
}

.empty-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.empty-desc {
  font-size: 0.95rem;
}

@media (max-width: 640px) {
  .note-card {
    padding: 24px;
  }
  
  .note-summary {
    font-size: 1rem;
  }
  
  .knowledge-item {
    padding: 12px;
  }
}
</style>
