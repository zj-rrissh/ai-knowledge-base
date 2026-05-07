<template>
  <div class="chat-container">
    <aside class="sidebar">
      <button @click="createSession">+ 新对话</button>
      <div v-for="s in sessions" :key="s.id" class="session-item" @click="selectSession(s.id)">
        {{ s.title }}
        <span class="delete-session" @click.stop="handleDeleteSession(s.id)">x</span>
      </div>
    </aside>
    <main class="chat-main">
      <div class="messages" ref="msgBox">
        <div v-for="m in messages" :key="m.id" :class="['message', m.role]">
          <div class="content">{{ m.content }}</div>
        </div>
      </div>
      <div class="input-area">
        <input v-model="query" @keyup.enter="send" placeholder="输入问题..." :disabled="!currentSession" />
        <button @click="send" :disabled="!currentSession">发送</button>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import { chat } from '../api/index.js'

const sessions = ref([])
const messages = ref([])
const currentSession = ref(null)
const query = ref('')

async function loadSessions() {
  const { data } = await chat.listSessions()
  sessions.value = data
}

async function createSession() {
  const { data } = await chat.createSession('新对话')
  sessions.value.unshift(data)
  selectSession(data.id)
}

async function selectSession(id) {
  currentSession.value = id
  const { data } = await chat.listMessages(id)
  messages.value = data
}

async function send() {
  if (!query.value.trim()) return
  const userQuery = query.value
  query.value = ''
  messages.value.push({ id: Date.now(), role: 'user', content: userQuery })
  const { data } = await chat.sendMessage(currentSession.value, userQuery)
  messages.value.push(data)
  await nextTick()
  const box = document.querySelector('.messages')
  if (box) box.scrollTop = box.scrollHeight
}

async function handleDeleteSession(id) {
  await chat.deleteSession(id)
  await loadSessions()
  if (currentSession.value === id) { currentSession.value = null; messages.value = [] }
}

onMounted(loadSessions)
</script>

<style scoped>
.chat-container { display: flex; height: 100vh; }
.sidebar { width: 260px; background: #fafafa; border-right: 1px solid #e8e8e8; padding: 16px; overflow-y: auto; }
.sidebar button { width: 100%; padding: 8px; margin-bottom: 8px; background: #1a1a2e; color: white; border: none; border-radius: 4px; cursor: pointer; }
.session-item { padding: 8px; cursor: pointer; border-radius: 4px; display: flex; justify-content: space-between; }
.session-item:hover { background: #e6f7ff; }
.delete-session { color: #999; cursor: pointer; }
.chat-main { flex: 1; display: flex; flex-direction: column; }
.messages { flex: 1; overflow-y: auto; padding: 20px; }
.message { margin-bottom: 16px; }
.message.user .content { background: #e6f7ff; padding: 10px 14px; border-radius: 8px; display: inline-block; }
.message.assistant .content { background: #f5f5f5; padding: 10px 14px; border-radius: 8px; display: inline-block; max-width: 80%; }
.input-area { display: flex; padding: 16px; border-top: 1px solid #e8e8e8; }
.input-area input { flex: 1; padding: 10px; border: 1px solid #d9d9d9; border-radius: 4px; }
.input-area button { margin-left: 8px; padding: 10px 24px; background: #1a1a2e; color: white; border: none; border-radius: 4px; cursor: pointer; }
</style>
