<template>
  <section class="json-input-section">
    <div class="input-card">
      <div class="input-header">
        <label class="input-label">
          <span class="label-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="16 18 22 12 16 6"/>
              <polyline points="8 6 2 12 8 18"/>
            </svg>
          </span>
          JSON 数据输入
        </label>
        <span class="input-hint">支持数组格式、{notes: [...]} 或 {data: [...]}</span>
      </div>
      
      <textarea
        class="json-textarea"
        :value="modelValue"
        @input="$emit('update:modelValue', $event.target.value)"
        placeholder='{
  "notes": [
    {
      "summary": "本段课堂内容的摘要文本",
      "knowledge_points": ["知识点1", "知识点2", "知识点3"]
    }
  ]
}'
        spellcheck="false"
      ></textarea>
      
      <div class="input-actions">
        <button class="btn btn-primary" @click="$emit('render')">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polygon points="5 3 19 12 5 21 5 3"/>
          </svg>
          渲染笔记
        </button>
        <button class="btn btn-secondary" @click="$emit('clear')">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="3 6 5 6 21 6"/>
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
          </svg>
          清空
        </button>
      </div>
      
      <div v-if="error" class="error-message">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="8" x2="12" y2="12"/>
          <line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
        {{ error }}
      </div>
    </div>
  </section>
</template>

<script setup>
defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  error: {
    type: String,
    default: ''
  }
})

defineEmits(['update:modelValue', 'render', 'clear'])
</script>

<style scoped>
.json-input-section {
  margin-bottom: 32px;
}

.input-card {
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  border-radius: 16px;
  padding: 24px;
  box-shadow: var(--shadow-sm);
}

.input-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 8px;
}

.input-label {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-primary);
}

.label-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-tertiary);
  border-radius: 8px;
}

.label-icon svg {
  width: 16px;
  height: 16px;
  stroke: var(--text-secondary);
}

.input-hint {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.json-textarea {
  width: 100%;
  min-height: 180px;
  padding: 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-default);
  border-radius: 12px;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 0.9rem;
  line-height: 1.6;
  color: var(--text-primary);
  resize: vertical;
  transition: all var(--transition-fast);
}

.json-textarea:focus {
  outline: none;
  border-color: var(--text-primary);
  box-shadow: 0 0 0 3px rgba(0, 0, 0, 0.05);
}

[data-theme="dark"] .json-textarea:focus {
  box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.05);
}

.json-textarea::placeholder {
  color: var(--text-muted);
}

.input-actions {
  display: flex;
  gap: 12px;
  margin-top: 16px;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border-radius: 10px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
  border: none;
}

.btn svg {
  width: 16px;
  height: 16px;
}

.btn-primary {
  background: var(--text-primary);
  color: var(--bg-primary);
}

.btn-primary:hover {
  opacity: 0.9;
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.btn-secondary {
  background: transparent;
  color: var(--text-secondary);
  border: 1px solid var(--border-default);
}

.btn-secondary:hover {
  background: var(--hover-bg);
  color: var(--text-primary);
  border-color: var(--border-strong);
}

.error-message {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 16px;
  padding: 12px 16px;
  background: rgba(220, 38, 38, 0.08);
  border: 1px solid rgba(220, 38, 38, 0.2);
  border-radius: 10px;
  color: #dc2626;
  font-size: 0.9rem;
}

.error-message svg {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

@media (max-width: 640px) {
  .input-card {
    padding: 16px;
  }
  
  .input-actions {
    flex-direction: column;
  }
  
  .btn {
    justify-content: center;
  }
}
</style>
