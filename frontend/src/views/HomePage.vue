<template>
  <div class="home-page" :data-theme="theme">
    <!-- 导航栏 -->
    <nav class="home-nav">
      <router-link to="/" class="nav-brand">
        <svg class="brand-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
          <polyline points="14 2 14 8 20 8"/>
          <line x1="16" y1="13" x2="8" y2="13"/>
          <line x1="16" y1="17" x2="8" y2="17"/>
          <polyline points="10 9 9 9 8 9"/>
        </svg>
        <span class="brand-text">NoteGen</span>
      </router-link>
      <div class="nav-right">
        <div class="nav-links">
          <router-link v-if="!user.isLoggedIn" to="/login" class="nav-link">登录</router-link>
          <template v-else>
            <!-- <router-link to="/dashboard" class="nav-link">任务台</router-link>
            <router-link to="/notes" class="nav-link">笔记系统</router-link> -->
            <span class="nav-user">{{ user.username }}</span>
          </template>
        </div>
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

    <!-- Hero 区域 -->
    <section class="hero">
      <div class="hero-content">
        <h1 class="hero-title">
          智能课堂笔记
          <span class="highlight">自动生成</span>
        </h1>
        <p class="hero-subtitle">
          将课堂内容转化为结构化的知识要点，智能提取摘要与知识点，让学习更高效。
        </p>
        <div class="hero-actions">
          <router-link to="/dashboard" class="btn btn-primary">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polygon points="5 3 19 12 5 21 5 3"/>
            </svg>
            开始使用
          </router-link>
          <router-link to="/login" class="btn btn-secondary">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/>
              <polyline points="10 17 15 12 10 7"/>
              <line x1="15" y1="12" x2="3" y2="12"/>
            </svg>
            登录账户
          </router-link>
        </div>
      </div>
      <div class="hero-visual">
        <div class="note-card-preview">
          <div class="preview-header">
            <span class="preview-dot"></span>
            <span class="preview-dot"></span>
            <span class="preview-dot"></span>
          </div>
          <div class="preview-content">
            <div class="preview-line"></div>
            <div class="preview-line short"></div>
            <div class="preview-badges">
              <span class="preview-badge"></span>
              <span class="preview-badge"></span>
              <span class="preview-badge"></span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 特性区域 -->
    <section class="features">
      <h2 class="section-title">核心功能</h2>
      <div class="features-grid">
        <div class="feature-card">
          <div class="feature-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="16 18 22 12 16 6"/>
              <polyline points="8 6 2 12 8 18"/>
            </svg>
          </div>
          <h3 class="feature-title">多格式支持</h3>
          <p class="feature-desc">支持直接数组、{notes: [...]}、{data: [...]} 三种 JSON 格式，自动识别解析</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
            </svg>
          </div>
          <h3 class="feature-title">智能提取</h3>
          <p class="feature-desc">自动提取摘要和知识点，结构化展示，支持侧边栏快速导航</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="3"/>
              <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
            </svg>
          </div>
          <h3 class="feature-title">主题切换</h3>
          <p class="feature-desc">支持亮色/暗色主题切换，自动保存偏好设置，适配不同使用场景</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
              <line x1="3" y1="9" x2="21" y2="9"/>
              <line x1="9" y1="21" x2="9" y2="9"/>
            </svg>
          </div>
          <h3 class="feature-title">响应式设计</h3>
          <p class="feature-desc">完美适配桌面、平板、手机等多种设备，随时随地查看笔记</p>
        </div>
      </div>
    </section>

    <!-- 页脚 -->
    <footer class="home-footer">
      <p>&copy; 2024 NoteGen. 课堂笔记自动生成系统</p>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUser } from '../store/user.js'

const { user, initUser } = useUser()
const theme = ref('light')

const toggleTheme = () => {
  theme.value = theme.value === 'light' ? 'dark' : 'light'
  document.documentElement.setAttribute('data-theme', theme.value)
  localStorage.setItem('theme', theme.value)
}

onMounted(() => {
  initUser()
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme) {
    theme.value = savedTheme
    document.documentElement.setAttribute('data-theme', theme.value)
  }
})
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background: var(--bg-primary);
  color: var(--text-primary);
}

/* 导航栏 */
.home-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 48px;
  height: 72px;
  border-bottom: 1px solid var(--border-subtle);
  background: var(--bg-primary);
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 0;
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
  gap: 24px;
}

.nav-links {
  display: flex;
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

/* Hero 区域 */
.hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 80px 48px;
  max-width: 1200px;
  margin: 0 auto;
  gap: 64px;
}

.hero-content {
  flex: 1;
}

.hero-title {
  font-size: 3.5rem;
  font-weight: 700;
  line-height: 1.2;
  margin-bottom: 24px;
  color: var(--text-primary);
}

.hero-title .highlight {
  background: linear-gradient(135deg, var(--text-primary) 0%, var(--text-muted) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  font-size: 1.1rem;
  color: var(--text-secondary);
  line-height: 1.8;
  margin-bottom: 40px;
  max-width: 500px;
}

.hero-actions {
  display: flex;
  gap: 16px;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 14px 28px;
  border-radius: 10px;
  font-size: 0.95rem;
  font-weight: 500;
  text-decoration: none;
  transition: all var(--transition-fast);
  border: none;
  cursor: pointer;
}

.btn svg {
  width: 18px;
  height: 18px;
}

.btn-primary {
  background: var(--text-primary);
  color: var(--bg-primary);
}

.btn-primary:hover {
  opacity: 0.9;
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
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

/* Hero 视觉 */
.hero-visual {
  flex: 0 0 400px;
}

.note-card-preview {
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  border-radius: 16px;
  padding: 24px;
  box-shadow: var(--shadow-xl);
  transform: rotate(-3deg);
  transition: transform var(--transition-base);
}

.note-card-preview:hover {
  transform: rotate(0deg) translateY(-10px);
}

.preview-header {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
}

.preview-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--border-strong);
}

.preview-dot:first-child {
  background: #ff5f57;
}

.preview-dot:nth-child(2) {
  background: #febc2e;
}

.preview-dot:nth-child(3) {
  background: #28c840;
}

.preview-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.preview-line {
  height: 12px;
  background: var(--bg-tertiary);
  border-radius: 6px;
  width: 100%;
}

.preview-line.short {
  width: 60%;
}

.preview-badges {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.preview-badge {
  height: 24px;
  width: 60px;
  background: var(--highlight-bg);
  border-radius: 12px;
}

/* 特性区域 */
.features {
  padding: 80px 48px;
  background: var(--bg-secondary);
}

.section-title {
  text-align: center;
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 48px;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.feature-card {
  background: var(--bg-elevated);
  border: 1px solid var(--border-subtle);
  border-radius: 16px;
  padding: 32px 24px;
  text-align: center;
  transition: all var(--transition-fast);
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
  border-color: var(--border-default);
}

.feature-icon {
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-tertiary);
  border-radius: 14px;
  margin: 0 auto 20px;
}

.feature-icon svg {
  width: 28px;
  height: 28px;
  stroke: var(--text-primary);
}

.feature-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.feature-desc {
  font-size: 0.9rem;
  color: var(--text-secondary);
  line-height: 1.6;
}

/* 页脚 */
.home-footer {
  text-align: center;
  padding: 40px 48px;
  border-top: 1px solid var(--border-subtle);
  color: var(--text-muted);
  font-size: 0.9rem;
}

/* 响应式 */
@media (max-width: 1024px) {
  .hero {
    flex-direction: column;
    text-align: center;
    padding: 60px 24px;
  }

  .hero-title {
    font-size: 2.5rem;
  }

  .hero-subtitle {
    margin-left: auto;
    margin-right: auto;
  }

  .hero-actions {
    justify-content: center;
  }

  .hero-visual {
    flex: none;
    width: 100%;
    max-width: 400px;
  }

  .features-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .home-nav {
    padding: 0 24px;
  }

  .nav-links {
    gap: 16px;
  }

  .hero-title {
    font-size: 2rem;
  }

  .hero-actions {
    flex-direction: column;
  }

  .features-grid {
    grid-template-columns: 1fr;
  }

  .features {
    padding: 60px 24px;
  }
}
</style>
