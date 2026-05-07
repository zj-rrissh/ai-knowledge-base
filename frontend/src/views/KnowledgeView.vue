<template>
  <div class="knowledge-container">
    <header>
      <h2>文档管理</h2>
      <nav><router-link to="/chat">对话</router-link></nav>
    </header>
    <div class="upload-area">
      <input type="file" ref="fileInput" accept=".pdf,.docx,.md,.txt" @change="handleUpload" />
      <button @click="$refs.fileInput.click()">上传文档</button>
    </div>
    <table v-if="documents.length">
      <thead><tr><th>文件名</th><th>大小</th><th>状态</th><th>时间</th><th>操作</th></tr></thead>
      <tbody>
        <tr v-for="doc in documents" :key="doc.id">
          <td>{{ doc.filename }}</td>
          <td>{{ formatSize(doc.fileSize) }}</td>
          <td>{{ doc.status }}</td>
          <td>{{ doc.createdAt?.substring(0, 10) }}</td>
          <td><button @click="handleDelete(doc.id)">删除</button></td>
        </tr>
      </tbody>
    </table>
    <p v-else>暂无文档，请上传</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { knowledge } from '../api/index.js'

const documents = ref([])
const fileInput = ref(null)

async function loadDocs() {
  const { data } = await knowledge.list()
  documents.value = data.content || data
}

async function handleUpload(e) {
  const file = e.target.files[0]
  if (!file) return
  await knowledge.upload(file)
  await loadDocs()
}

async function handleDelete(id) {
  await knowledge.delete(id)
  await loadDocs()
}

function formatSize(bytes) {
  if (!bytes) return '-'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

onMounted(loadDocs)
</script>

<style scoped>
header { display: flex; justify-content: space-between; align-items: center; padding: 16px 24px; background: #1a1a2e; color: white; }
header a { color: #1890ff; }
.upload-area { padding: 20px 24px; }
.upload-area input[type="file"] { display: none; }
.upload-area button { padding: 8px 20px; background: #1a1a2e; color: white; border: none; border-radius: 4px; cursor: pointer; }
table { width: 100%; border-collapse: collapse; padding: 0 24px; }
th, td { padding: 10px; border-bottom: 1px solid #f0f0f0; text-align: left; }
</style>
