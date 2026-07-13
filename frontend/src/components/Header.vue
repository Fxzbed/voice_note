<template>
  <header class="header">
    <div class="header-content">
      <button 
        class="mobile-menu-btn"
        @click="$emit('toggle-sidebar')"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M3 12h18M3 6h18M3 18h18"/>
        </svg>
      </button>
      
      <div class="header-left">
        <router-link to="/dashboard" class="brand-link">
          <svg class="brand-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
          </svg>
          <span>NoteGen</span>
        </router-link>
      </div>
      
      <div class="header-actions">
        <router-link to="/dashboard" class="nav-link">任务台</router-link>
        <span v-if="user.isLoggedIn" class="user-name">{{ user.username }}</span>
        <button 
          class="theme-toggle"
          @click="$emit('toggle-theme')"
          :title="theme === 'light' ? '切换到暗色模式' : '切换到亮色模式'"
        >
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
    </div>
  </header>
</template>

<script setup>
import { useUser } from '../store/user.js'

const { user } = useUser()

defineProps({
  theme: {
    type: String,
    default: 'light'
  }
})

defineEmits(['toggle-theme', 'toggle-sidebar'])
</script>

<style scoped>
.header {
  height: var(--header-height);
  background: var(--bg-primary);
  border-bottom: 1px solid var(--border-subtle);
  position: sticky;
  top: 0;
  z-index: 50;
}

.header-content {
  max-width: 900px;
  height: 100%;
  margin: 0 auto;
  padding: 0 48px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.mobile-menu-btn {
  display: none;
  width: 40px;
  height: 40px;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 1px solid var(--border-default);
  border-radius: 8px;
  cursor: pointer;
  color: var(--text-primary);
  transition: all var(--transition-fast);
}

.mobile-menu-btn:hover {
  background: var(--hover-bg);
}

.mobile-menu-btn svg {
  width: 20px;
  height: 20px;
}

.header-left {
  display: flex;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 32px;
}

.brand-link {
  display: flex;
  align-items: center;
  gap: 6px;
  text-decoration: none;
  color: var(--text-primary);
  font-weight: 700;
  font-size: 1.1rem;
  transition: opacity var(--transition-fast);
}

.brand-link:hover {
  opacity: 0.7;
}

.brand-icon {
  width: 22px;
  height: 22px;
}

.nav-link {
  font-size: 0.95rem;
  color: var(--text-secondary);
  text-decoration: none;
  transition: color var(--transition-fast);
}

.nav-link:hover {
  color: var(--text-primary);
}

.header-title h1 {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.02em;
}

.header-subtitle {
  font-size: 0.9rem;
  color: var(--text-muted);
  font-weight: 400;
}

.theme-toggle {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-secondary);
  border: 1px solid var(--border-default);
  border-radius: 10px;
  cursor: pointer;
  color: var(--text-secondary);
  transition: all var(--transition-fast);
}

.theme-toggle:hover {
  background: var(--hover-bg);
  border-color: var(--border-strong);
  color: var(--text-primary);
}

.theme-toggle svg {
  width: 22px;
  height: 22px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-name {
  font-size: 0.9rem;
  color: var(--text-primary);
  font-weight: 600;
  padding: 8px 16px;
  background: var(--bg-secondary);
  border-radius: 8px;
}

@media (max-width: 1024px) {
  .header-content {
    padding: 0 24px;
  }
  
  .mobile-menu-btn {
    display: flex;
  }
}

@media (max-width: 640px) {
  .header-content {
    padding: 0 16px;
  }
  
  .header-title h1 {
    font-size: 1.25rem;
  }
  
  .header-subtitle {
    display: none;
  }
}
</style>
