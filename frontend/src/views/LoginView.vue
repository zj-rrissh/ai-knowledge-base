<template>
  <div class="login-wrapper">
    <!-- Animated Background Shapes -->
    <div class="bg-shape shape-1"></div>
    <div class="bg-shape shape-2"></div>
    <div class="bg-shape shape-3"></div>

    <div class="login-card glass-panel slide-up">
      <div class="card-header">
        <div class="logo">
          <svg width="40" height="40" viewBox="0 0 48 48" fill="none">
            <rect width="48" height="48" rx="14" fill="url(#loginGrad)" />
            <path d="M16 20c0-2.21 1.79-4 4-4h8c2.21 0 4 1.79 4 4v12.3c0 1.54-1.85 2.55-3.05 1.54l-3.08-2.59a2 2 0 00-1.26-.43H20c-2.21 0-4-1.79-4-4V20z" fill="white" />
            <defs>
              <linearGradient id="loginGrad" x1="0" y1="0" x2="48" y2="48">
                <stop stop-color="#6366f1" />
                <stop offset="1" stop-color="#ec4899" />
              </linearGradient>
            </defs>
          </svg>
        </div>
        <h2>欢迎来到 AI 知识库</h2>
        <p class="subtitle">{{ isRegister ? '创建您的账号以开始使用' : '登录以继续探索您的知识' }}</p>
      </div>

      <form @submit.prevent="handleSubmit" class="login-form">
        <div class="input-group fade-in" style="animation-delay: 0.1s">
          <label>用户名</label>
          <div class="input-wrapper">
            <svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
              <circle cx="12" cy="7" r="4"></circle>
            </svg>
            <input v-model="username" placeholder="输入您的用户名" required />
          </div>
        </div>

        <div class="input-group fade-in" style="animation-delay: 0.2s">
          <label>密码</label>
          <div class="input-wrapper">
            <svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
              <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
            </svg>
            <input v-model="password" type="password" placeholder="输入您的密码" required />
          </div>
        </div>

        <button type="submit" class="submit-btn fade-in" style="animation-delay: 0.3s" :disabled="loading">
          <span v-if="!loading">{{ isRegister ? '注册账号' : '立即登录' }}</span>
          <svg v-else class="spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10" stroke-opacity="0.25"></circle>
            <path d="M12 2a10 10 0 0 1 10 10"></path>
          </svg>
        </button>
      </form>

      <p class="toggle fade-in" style="animation-delay: 0.4s" @click="isRegister = !isRegister">
        {{ isRegister ? '已有账号？去登录' : '没有账号？去注册' }}
      </p>

      <div v-if="error" class="error-toast fade-in">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="8" x2="12" y2="12"></line>
          <line x1="12" y1="16" x2="12.01" y2="16"></line>
        </svg>
        {{ error }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { auth } from '../api/index.js'

const username = ref('')
const password = ref('')
const isRegister = ref(false)
const error = ref('')
const loading = ref(false)
const router = useRouter()

async function handleSubmit() {
  error.value = ''
  loading.value = true
  try {
    const fn = isRegister.value ? auth.register : auth.login
    const { data } = await fn(username.value, password.value)
    localStorage.setItem('token', data.accessToken)
    localStorage.setItem('username', data.username)
    router.push('/chat')
  } catch (e) {
    error.value = e.response?.data?.message || '操作失败，请检查您的输入'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-wrapper {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background: var(--bg);
  padding: 20px;
}

/* Background Animations */
.bg-shape {
  position: absolute;
  filter: blur(80px);
  z-index: 0;
  opacity: 0.6;
  border-radius: 50%;
  animation: float 20s infinite alternate;
}
.shape-1 {
  width: 400px;
  height: 400px;
  background: rgba(99, 102, 241, 0.4);
  top: -100px;
  left: -100px;
  animation-delay: 0s;
}
.shape-2 {
  width: 500px;
  height: 500px;
  background: rgba(236, 72, 153, 0.3);
  bottom: -200px;
  right: -100px;
  animation-delay: -5s;
}
.shape-3 {
  width: 300px;
  height: 300px;
  background: rgba(168, 85, 247, 0.3);
  top: 40%;
  left: 50%;
  animation-delay: -10s;
}

@keyframes float {
  0% { transform: translate(0, 0) rotate(0deg) scale(1); }
  50% { transform: translate(50px, 30px) rotate(180deg) scale(1.1); }
  100% { transform: translate(-30px, -50px) rotate(360deg) scale(0.9); }
}

/* Card */
.login-card {
  position: relative;
  z-index: 10;
  width: 100%;
  max-width: 420px;
  padding: 48px 40px;
  border-radius: 24px;
  text-align: center;
}

.card-header {
  margin-bottom: 32px;
}

.logo {
  display: inline-flex;
  margin-bottom: 16px;
  animation: pulseLogo 3s infinite alternate ease-in-out;
}

@keyframes pulseLogo {
  from { filter: drop-shadow(0 4px 12px rgba(99, 102, 241, 0.3)); }
  to { filter: drop-shadow(0 8px 24px rgba(236, 72, 153, 0.4)); transform: translateY(-2px); }
}

.card-header h2 {
  font-size: 26px;
  margin: 0 0 8px;
  background: var(--accent-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  color: var(--text);
  font-size: 14.5px;
  margin: 0;
}

/* Form */
.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
  text-align: left;
}

.input-group label {
  display: block;
  font-size: 13.5px;
  font-weight: 600;
  color: var(--text-h);
  margin-bottom: 8px;
  padding-left: 4px;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 14px;
  width: 18px;
  height: 18px;
  color: #94a3b8;
  pointer-events: none;
  transition: color 0.3s;
}

.input-wrapper input {
  width: 100%;
  padding: 12px 16px 12px 42px;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid var(--border);
  border-radius: 12px;
  font-family: inherit;
  font-size: 15px;
  color: var(--text-h);
  transition: all 0.3s;
  outline: none;
}

.input-wrapper input:focus {
  background: #fff;
  border-color: var(--accent);
  box-shadow: 0 0 0 4px var(--accent-light);
}

.input-wrapper input:focus + .input-icon,
.input-wrapper input:not(:placeholder-shown) + .input-icon {
  color: var(--accent);
}

.input-wrapper input::placeholder {
  color: #94a3b8;
}

.submit-btn {
  margin-top: 8px;
  width: 100%;
  padding: 14px;
  background: var(--accent-gradient);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  font-family: var(--display);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  overflow: hidden;
}

.submit-btn::before {
  content: '';
  position: absolute;
  top: 0; left: -100%;
  width: 100%; height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
  transition: all 0.5s;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: var(--shadow-glow);
}

.submit-btn:hover:not(:disabled)::before {
  left: 100%;
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.spinner {
  width: 20px;
  height: 20px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  100% { transform: rotate(360deg); }
}

.toggle {
  margin-top: 24px;
  font-size: 14px;
  color: var(--text);
  cursor: pointer;
  transition: color 0.2s;
  font-weight: 500;
}
.toggle:hover {
  color: var(--accent);
}

.error-toast {
  position: absolute;
  bottom: -60px;
  left: 50%;
  transform: translateX(-50%);
  background: #fee2e2;
  color: #dc2626;
  padding: 10px 16px;
  border-radius: 8px;
  font-size: 13.5px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: var(--shadow-sm);
  white-space: nowrap;
}
</style>
