<template>
  <div class="login-container">
    <div class="login-card">
      <h2>AI 知识库</h2>
      <form @submit.prevent="handleSubmit">
        <input v-model="username" placeholder="用户名" required />
        <input v-model="password" type="password" placeholder="密码" required />
        <button type="submit">{{ isRegister ? '注册' : '登录' }}</button>
      </form>
      <p class="toggle" @click="isRegister = !isRegister">
        {{ isRegister ? '已有账号？去登录' : '没有账号？去注册' }}
      </p>
      <p v-if="error" class="error">{{ error }}</p>
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
const router = useRouter()

async function handleSubmit() {
  error.value = ''
  try {
    const fn = isRegister.value ? auth.register : auth.login
    const { data } = await fn(username.value, password.value)
    localStorage.setItem('token', data.accessToken)
    localStorage.setItem('username', data.username)
    router.push('/chat')
  } catch (e) {
    error.value = e.response?.data?.message || '操作失败'
  }
}
</script>

<style scoped>
.login-container { display: flex; justify-content: center; align-items: center; min-height: 100vh; background: #f0f2f5; }
.login-card { background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 12px rgba(0,0,0,0.1); width: 360px; text-align: center; }
.login-card h2 { margin-bottom: 24px; color: #1a1a2e; }
input { width: 100%; padding: 10px; margin-bottom: 12px; border: 1px solid #d9d9d9; border-radius: 4px; box-sizing: border-box; }
button { width: 100%; padding: 10px; background: #1a1a2e; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
.toggle { margin-top: 12px; color: #1890ff; cursor: pointer; font-size: 14px; }
.error { color: red; margin-top: 8px; font-size: 14px; }
</style>
