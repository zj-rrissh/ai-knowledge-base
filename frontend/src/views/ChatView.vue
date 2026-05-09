<template>
  <div class="chat-layout">
    <!-- 侧边栏遮罩（移动端） -->
    <div v-if="sidebarOpen && isMobile" class="sidebar-overlay" @click="sidebarOpen = false" />

    <!-- 可折叠侧边栏 -->
    <aside :class="['sidebar', { collapsed: !sidebarOpen }]">
      <div class="sidebar-header">
        <button class="sidebar-toggle" @click="sidebarOpen = !sidebarOpen" title="收起侧边栏">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M4 4L16 10L4 16" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
        </button>
        <button v-show="sidebarOpen" class="new-chat-btn" @click="createSession">
          <svg width="16" height="16" viewBox="0 0 20 20" fill="none">
            <path d="M10 4V16M4 10H16" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
          </svg>
          <span>新对话</span>
        </button>
      </div>

      <div v-show="sidebarOpen" class="session-list">
        <div class="session-list-label">对话历史</div>
        <div
          v-for="s in sessions"
          :key="s.id"
          :class="['session-item', { active: currentSession === s.id }]"
          @click="selectSession(s.id)"
        >
          <svg class="session-icon" width="16" height="16" viewBox="0 0 20 20" fill="none">
            <path d="M4 5.5C4 4.119 5.12 3 6.5 3h7C14.88 3 16 4.119 16 5.5v10.33c0 1.208-1.45 2.001-2.39 1.209l-2.8-2.365a1.5 1.5 0 00-.987-.36H6.5A2.5 2.5 0 014 11.814V5.5z" stroke="currentColor" stroke-width="1.5"/>
          </svg>
          <span class="session-title">{{ s.title }}</span>
          <button
            v-show="sidebarOpen"
            class="session-delete"
            @click.stop="handleDeleteSession(s.id)"
          >
            <svg width="14" height="14" viewBox="0 0 20 20" fill="none">
              <path d="M6 6L14 14M14 6L6 14" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
            </svg>
          </button>
        </div>
        <div v-if="sessions.length === 0 && !loadingSessions" class="session-empty">
          暂无对话，点击上方按钮开始
        </div>
        <div v-if="loadingSessions" class="session-loading">
          <span class="loading-spinner" /> 加载中...
        </div>
      </div>

      <!-- 折叠态显示图标按钮 -->
      <div v-show="!sidebarOpen" class="collapsed-actions">
        <button class="collapsed-new-chat" @click="createSession" title="新对话">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M10 4V16M4 10H16" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
          </svg>
        </button>
      </div>
    </aside>

    <!-- 主聊天区域 -->
    <main class="chat-main">
      <!-- 欢迎页 / 空状态 -->
      <div v-if="!currentSession" class="welcome-area">
        <div class="welcome-logo">
          <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
            <rect width="48" height="48" rx="14" fill="url(#logoGrad)" />
            <path d="M16 20c0-2.21 1.79-4 4-4h8c2.21 0 4 1.79 4 4v12.3c0 1.54-1.85 2.55-3.05 1.54l-3.08-2.59a2 2 0 00-1.26-.43H20c-2.21 0-4-1.79-4-4V20z" fill="white" />
            <defs>
              <linearGradient id="logoGrad" x1="0" y1="0" x2="48" y2="48">
                <stop stop-color="#6366f1" />
                <stop offset="1" stop-color="#06b6d4" />
              </linearGradient>
            </defs>
          </svg>
        </div>
        <h1 class="welcome-title">AI 知识库助手</h1>
        <p class="welcome-subtitle">选择已有对话或创建新对话，开始探索你的知识库</p>
        <div class="welcome-actions">
          <button class="welcome-btn" @click="createSession">
            <svg width="18" height="18" viewBox="0 0 20 20" fill="none">
              <path d="M10 4V16M4 10H16" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
            </svg>
            开始新对话
          </button>
        </div>
      </div>

      <!-- 消息列表 -->
      <div v-else class="messages" ref="msgBox">
        <div v-if="messages.length === 0" class="msg-empty">
          <div class="msg-empty-icon">
            <svg width="40" height="40" viewBox="0 0 48 48" fill="none">
              <rect width="48" height="48" rx="14" fill="url(#logoGrad)" />
              <path d="M16 20c0-2.21 1.79-4 4-4h8c2.21 0 4 1.79 4 4v12.3c0 1.54-1.85 2.55-3.05 1.54l-3.08-2.59a2 2 0 00-1.26-.43H20c-2.21 0-4-1.79-4-4V20z" fill="white" />
            </svg>
          </div>
          <p>开始一段新对话，提出你的问题</p>
        </div>
        <div
          v-for="(m, idx) in messages"
          :key="m.id"
          :class="['msg-bubble', m.role]"
        >
          <div class="msg-avatar">
            <template v-if="m.role === 'user'">
              <div class="avatar-user">{{ username.charAt(0).toUpperCase() }}</div>
            </template>
            <template v-else>
              <svg width="28" height="28" viewBox="0 0 48 48" fill="none">
                <rect width="48" height="48" rx="14" fill="url(#logoGrad)" />
                <path d="M16 20c0-2.21 1.79-4 4-4h8c2.21 0 4 1.79 4 4v12.3c0 1.54-1.85 2.55-3.05 1.54l-3.08-2.59a2 2 0 00-1.26-.43H20c-2.21 0-4-1.79-4-4V20z" fill="white" />
              </svg>
            </template>
          </div>
          <div class="msg-body">
            <div class="msg-content" v-text="m.content" />
            <div v-if="idx === messages.length - 1 && m.role === 'assistant' && sending" class="typing-dots">
              <span /><span /><span />
            </div>
          </div>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="input-area" :class="{ 'has-session': currentSession }">
        <!-- 已选文件标签 -->
        <div v-if="selectedFiles.length > 0" class="file-chips">
          <div v-for="(f, idx) in selectedFiles" :key="idx" class="file-chip">
            <svg width="14" height="14" viewBox="0 0 20 20" fill="none">
              <path d="M6 2.5v15l4.5-3.5L15 17.5v-15a1 1 0 00-1-1H7a1 1 0 00-1 1z" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
            <span>{{ f.name }}</span>
            <button class="chip-remove" @click="removeFile(idx)">
              <svg width="12" height="12" viewBox="0 0 20 20" fill="none">
                <path d="M6 6L14 14M14 6L6 14" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
              </svg>
            </button>
          </div>
        </div>

        <!-- 输入框 -->
        <div class="input-row">
          <div class="input-wrapper">
            <textarea
              ref="inputEl"
              v-model="query"
              class="chat-input"
              :placeholder="currentSession ? '输入你的问题...' : '输入问题，开始新对话...'"
              rows="1"
              :disabled="sending"
              @keydown.enter.exact.prevent="send"
              @input="autoResize"
            />
          </div>
          <button
            class="send-btn"
            :disabled="!query.trim() || sending"
            @click="send"
          >
            <svg v-if="!sending" width="18" height="18" viewBox="0 0 20 20" fill="none">
              <path d="M3 3L17 10L3 17L3 11L11 10L3 9V3Z" fill="currentColor" />
            </svg>
            <span v-else class="loading-spinner" />
          </button>
        </div>

        <!-- 底部操作栏 -->
        <div class="input-actions">
          <label class="action-btn upload-btn" title="上传文档">
            <svg width="16" height="16" viewBox="0 0 20 20" fill="none">
              <path d="M10 13V3M6 7l4-4 4 4M17 13v3a1 1 0 01-1 1H4a1 1 0 01-1-1v-3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
            <span>上传文档</span>
            <input
              type="file"
              accept=".pdf,.md,.txt,.xlsx,.pptx"
              multiple
              hidden
              @change="handleFileSelect"
            />
          </label>
          <span class="input-hint">
            {{ currentSession ? 'Enter 发送 · 支持 PDF / Word / Markdown / TXT' : '选择或创建对话即可发送消息' }}
          </span>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted, onUnmounted, watch } from 'vue'
import { chat, knowledge } from '../api/index.js'

const sessions = ref([])
const messages = ref([])
const currentSession = ref(null)
const query = ref('')
const sending = ref(false)
const loadingSessions = ref(false)
const sidebarOpen = ref(true)
const selectedFiles = ref([])
const uploadingFiles = ref(false)
const msgBox = ref(null)
const inputEl = ref(null)
const isMobile = ref(window.innerWidth < 768)

const username = computed(() => localStorage.getItem('username') || '用户')

function onResize() {
  isMobile.value = window.innerWidth < 768
  if (isMobile.value) sidebarOpen.value = false
}

onMounted(() => {
  loadSessions()
  window.addEventListener('resize', onResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', onResize)
})

async function loadSessions() {
  loadingSessions.value = true
  try {
    const { data } = await chat.listSessions()
    sessions.value = data
  } catch (e) { console.error('加载会话列表失败:', e) }
  finally { loadingSessions.value = false }
}

async function createSession() {
  try {
    const { data } = await chat.createSession('新对话')
    sessions.value.unshift(data)
    selectSession(data.id)
    if (isMobile.value) sidebarOpen.value = false
  } catch (e) { console.error('创建会话失败:', e) }
}

async function selectSession(id) {
  currentSession.value = id
  try {
    const { data } = await chat.listMessages(id)
    messages.value = data
    await nextTick()
    scrollToBottom()
  } catch (e) { console.error('加载消息失败:', e) }
  if (isMobile.value) sidebarOpen.value = false
}

async function send() {
  const text = query.value.trim()
  if ((!text && selectedFiles.value.length === 0) || sending.value) return

  // 如果没有当前会话，先创建
  if (!currentSession.value) {
    try {
      const { data } = await chat.createSession('新对话')
      sessions.value.unshift(data)
      currentSession.value = data.id
    } catch (e) { console.error('自动创建会话失败:', e); return }
  }

  const userMsg = text || '[上传了文档]'
  query.value = ''
  sending.value = true

  // 先上传文件到知识库
  const fileIds = []
  if (selectedFiles.value.length > 0) {
    uploadingFiles.value = true
    for (const f of selectedFiles.value) {
      try {
        const { data } = await knowledge.upload(f)
        if (data?.id) fileIds.push(data.id)
      } catch (e) { console.error('文件上传失败:', e) }
    }
    uploadingFiles.value = false
    selectedFiles.value = []
  }

  messages.value.push({ id: Date.now(), role: 'user', content: userMsg })
  await nextTick()
  scrollToBottom()

  try {
    const { data } = await chat.sendMessage(currentSession.value, userMsg, fileIds.length > 0 ? fileIds : undefined)
    messages.value.push(data)
    await nextTick()
    scrollToBottom()
  } catch (e) {
    console.error('发送消息失败:', e)
    messages.value.push({ id: Date.now(), role: 'assistant', content: '抱歉，请求失败，请重试。' })
  } finally {
    sending.value = false
    focusInput()
  }
}

function handleFileSelect(e) {
  const files = Array.from(e.target.files || [])
  selectedFiles.value.push(...files)
  e.target.value = ''
  if (!currentSession.value) {
    createSession()
  }
}

function removeFile(idx) {
  selectedFiles.value.splice(idx, 1)
}

function autoResize() {
  const el = inputEl.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 200) + 'px'
}

function scrollToBottom() {
  if (msgBox.value) msgBox.value.scrollTop = msgBox.value.scrollHeight
}

function focusInput() {
  nextTick(() => inputEl.value?.focus())
}

async function handleDeleteSession(id) {
  try {
    await chat.deleteSession(id)
    if (currentSession.value === id) {
      currentSession.value = null
      messages.value = []
    }
    await loadSessions()
  } catch (e) { console.error('删除会话失败:', e) }
}
</script>

<style scoped>
/* ===== 布局 ===== */
.chat-layout {
  display: flex;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  background: #f8fafc;
  color: #1e293b;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

/* ===== 侧边栏 ===== */
.sidebar {
  position: relative;
  width: 280px;
  min-width: 280px;
  background: #f1f5f9;
  border-right: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  transition: width 0.28s cubic-bezier(0.4, 0, 0.2, 1),
              min-width 0.28s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  z-index: 20;
}

.sidebar.collapsed {
  width: 60px;
  min-width: 60px;
}

.sidebar-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
  z-index: 15;
}

/* 侧边栏头部 */
.sidebar-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  border-bottom: 1px solid #e2e8f0;
}

.sidebar-toggle {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  color: #64748b;
  border-radius: 8px;
  cursor: pointer;
  flex-shrink: 0;
  transition: all 0.15s;
}
.sidebar-toggle:hover {
  background: #e2e8f0;
  color: #334155;
}
.sidebar.collapsed .sidebar-toggle svg {
  transform: rotate(180deg);
}
.sidebar-toggle svg {
  transition: transform 0.28s cubic-bezier(0.4, 0, 0.2, 1);
}

.new-chat-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  height: 38px;
  border: 1px solid #e2e8f0;
  background: white;
  color: #334155;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.15s;
}
.new-chat-btn:hover {
  background: #6366f1;
  color: white;
  border-color: #6366f1;
}

/* 会话列表 */
.session-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.session-list-label {
  font-size: 11px;
  font-weight: 600;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  padding: 8px 10px 6px;
}

.session-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 9px 10px;
  border-radius: 8px;
  cursor: pointer;
  color: #475569;
  font-size: 14px;
  transition: all 0.12s;
  margin-bottom: 2px;
}
.session-item:hover {
  background: #e2e8f0;
}
.session-item.active {
  background: #e0e7ff;
  color: #4338ca;
}
.session-item.active .session-icon {
  color: #6366f1;
}

.session-icon {
  flex-shrink: 0;
  color: #94a3b8;
}

.session-title {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.session-delete {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  color: #94a3b8;
  border-radius: 4px;
  cursor: pointer;
  opacity: 0;
  transition: all 0.12s;
}
.session-item:hover .session-delete {
  opacity: 1;
}
.session-delete:hover {
  background: #fee2e2;
  color: #ef4444;
}

.session-empty,
.session-loading {
  padding: 24px 12px;
  text-align: center;
  font-size: 13px;
  color: #94a3b8;
}

/* 折叠态 */
.collapsed-actions {
  padding: 12px 12px 0;
  display: flex;
  justify-content: center;
}

.collapsed-new-chat {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: white;
  color: #334155;
  border-radius: 8px;
  cursor: pointer;
  border: 1px solid #e2e8f0;
  transition: all 0.15s;
}
.collapsed-new-chat:hover {
  background: #6366f1;
  color: white;
  border-color: #6366f1;
}

/* ===== 主聊天区 ===== */
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  background: #ffffff;
}

/* ===== 欢迎页 ===== */
.welcome-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  gap: 14px;
}

.welcome-logo svg {
  filter: drop-shadow(0 4px 12px rgba(99, 102, 241, 0.3));
}

.welcome-title {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
  letter-spacing: -0.5px;
}

.welcome-subtitle {
  font-size: 15px;
  color: #94a3b8;
  margin: 0;
  max-width: 400px;
  text-align: center;
  line-height: 1.6;
}

.welcome-actions {
  margin-top: 8px;
}

.welcome-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 28px;
  background: #6366f1;
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
}
.welcome-btn:hover {
  background: #4f46e5;
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(99, 102, 241, 0.35);
}

/* ===== 消息区 ===== */
.messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px 20px;
  scroll-behavior: smooth;
}

.msg-empty {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: #94a3b8;
  font-size: 14px;
}

.msg-empty-icon {
  opacity: 0.4;
}

.msg-bubble {
  display: flex;
  gap: 12px;
  margin-bottom: 28px;
  max-width: 820px;
  margin-left: auto;
  margin-right: auto;
}

.msg-bubble.user {
  flex-direction: row-reverse;
}

.msg-avatar {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
}

.avatar-user {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: linear-gradient(135deg, #6366f1, #06b6d4);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
}

.msg-body {
  min-width: 0;
}

.msg-content {
  padding: 12px 18px;
  border-radius: 14px;
  font-size: 14.5px;
  line-height: 1.65;
  white-space: pre-wrap;
  word-break: break-word;
}

.msg-bubble.user .msg-content {
  background: #6366f1;
  color: white;
  border-bottom-right-radius: 4px;
}

.msg-bubble.assistant .msg-content {
  background: #f1f5f9;
  color: #1e293b;
  border-bottom-left-radius: 4px;
}

/* 打字动画 */
.typing-dots {
  display: flex;
  gap: 4px;
  padding: 8px 14px;
}
.typing-dots span {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #94a3b8;
  animation: blink 1.3s infinite;
}
.typing-dots span:nth-child(2) { animation-delay: 0.2s; }
.typing-dots span:nth-child(3) { animation-delay: 0.4s; }

@keyframes blink {
  0%, 60%, 100% { opacity: 0.2; transform: scale(0.8); }
  30% { opacity: 1; transform: scale(1); }
}

/* ===== 输入区 ===== */
.input-area {
  padding: 0 20px 16px;
  max-width: 860px;
  width: 100%;
  margin: 0 auto;
  box-sizing: border-box;
}

.input-area.has-session {
  border-top: 1px solid #f1f5f9;
  padding-top: 16px;
}

/* 文件标签 */
.file-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 10px;
}

.file-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 10px;
  background: #e0e7ff;
  color: #4338ca;
  border-radius: 6px;
  font-size: 12.5px;
  font-weight: 500;
}
.file-chip svg {
  flex-shrink: 0;
  color: #6366f1;
}
.file-chip span {
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.chip-remove {
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  color: #6366f1;
  border-radius: 4px;
  cursor: pointer;
  margin-left: 2px;
  flex-shrink: 0;
}
.chip-remove:hover {
  background: #c7d2fe;
  color: #4338ca;
}

/* 输入行 */
.input-row {
  display: flex;
  align-items: flex-end;
  gap: 8px;
}

.input-wrapper {
  flex: 1;
  background: #f8fafc;
  border: 1.5px solid #e2e8f0;
  border-radius: 14px;
  transition: border-color 0.15s;
}
.input-wrapper:focus-within {
  border-color: #6366f1;
  background: white;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.08);
}

.chat-input {
  width: 100%;
  border: none;
  background: transparent;
  padding: 10px 16px;
  font-size: 14.5px;
  font-family: inherit;
  color: #1e293b;
  resize: none;
  outline: none;
  line-height: 1.5;
  box-sizing: border-box;
}
.chat-input::placeholder {
  color: #cbd5e1;
}
.chat-input:disabled {
  opacity: 0.6;
}

.send-btn {
  width: 42px;
  height: 42px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: #6366f1;
  color: white;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.15s;
}
.send-btn:hover:not(:disabled) {
  background: #4f46e5;
  transform: scale(1.04);
}
.send-btn:disabled {
  background: #e2e8f0;
  color: #cbd5e1;
  cursor: not-allowed;
}

/* 底部操作栏 */
.input-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 4px 0;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 12.5px;
  color: #64748b;
  cursor: pointer;
  transition: all 0.15s;
  border: none;
  background: transparent;
}
.action-btn:hover {
  background: #f1f5f9;
  color: #6366f1;
}

.input-hint {
  font-size: 12px;
  color: #cbd5e1;
}

/* ===== 加载动画 ===== */
.loading-spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top-color: currentColor;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ===== 响应式 ===== */
@media (max-width: 767px) {
  .sidebar {
    position: fixed;
    left: 0;
    top: 0;
    bottom: 0;
    z-index: 20;
    box-shadow: 4px 0 24px rgba(0,0,0,0.15);
  }
  .sidebar.collapsed {
    display: none;
  }

  .welcome-title { font-size: 22px; }
  .welcome-subtitle { font-size: 14px; }

  .msg-bubble { max-width: 100%; }
  .msg-content { font-size: 14px; }

  .input-area { padding: 0 12px 12px; }
}
</style>
