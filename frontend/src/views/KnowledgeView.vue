<template>
  <div class="knowledge-page">
    <header class="page-header">
      <div class="header-content">
        <div class="header-brand">
          <svg class="brand-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
            <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
          </svg>
          <h1>知识库</h1>
        </div>
        <nav>
          <router-link to="/chat" class="nav-link">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
            </svg>
            对话
          </router-link>
        </nav>
      </div>
    </header>

    <main class="page-body">
      <section class="upload-card">
        <div class="card-header">
          <h2>添加文档</h2>
          <p class="card-subtitle">一次最多选择 5 个文件，AI 将自动生成标题和标签</p>
        </div>
        <div class="upload-form">
          <div class="file-selector" :class="{ 'has-files': selectedFiles.length }">
            <input
              ref="fileInput"
              type="file"
              accept=".pdf,.md,.txt"
              multiple
              @change="onFilesChange"
              class="file-input-hidden"
            />
            <button type="button" @click="$refs.fileInput.click()" class="file-btn">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
                <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/>
              </svg>
              {{ selectedFiles.length ? '添加更多文件' : '选择文件' }}
            </button>
            <span v-if="!selectedFiles.length" class="file-hint">支持 PDF、Markdown、TXT</span>
            <button v-if="selectedFiles.length" type="button" @click="clearFiles" class="file-clear">清空</button>
          </div>

          <ul v-if="selectedFiles.length" class="file-list">
            <li v-for="(file, idx) in selectedFiles" :key="idx" class="file-item">
              <svg class="file-item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="16" height="16">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
              </svg>
              <span class="file-item-name">{{ file.name }}</span>
              <span class="file-item-size">{{ formatSize(file.size) }}</span>
            </li>
          </ul>

          <div class="form-actions">
            <button class="submit-btn" :disabled="uploading || !selectedFiles.length" @click="handleBatchSubmit">
              <svg v-if="uploading" class="spinner" viewBox="0 0 24 24" fill="none" width="16" height="16">
                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3" opacity="0.25"/>
                <path d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
              </svg>
              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="17 8 12 3 7 8"/>
                <line x1="12" y1="3" x2="12" y2="15"/>
              </svg>
              {{ uploading ? '上传中...' : `上传全部 (${selectedFiles.length}/5)` }}
            </button>
            <p v-if="uploadError" class="form-error">{{ uploadError }}</p>
          </div>
        </div>
      </section>

      <section class="docs-section">
        <div class="section-header">
          <h2>文档列表</h2>
          <span v-if="documents.length" class="count-badge">{{ documents.length }} 个文档</span>
        </div>

        <div v-if="loading" class="state-box">
          <svg class="state-spinner" viewBox="0 0 24 24" fill="none" width="32" height="32">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3" opacity="0.15"/>
            <path d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
          </svg>
          <p>加载中...</p>
        </div>

        <div v-else-if="!documents.length" class="state-box empty-state">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" width="48" height="48" opacity="0.3">
            <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
            <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
            <line x1="12" y1="6" x2="12" y2="14"/>
            <line x1="9" y1="10" x2="15" y2="10"/>
          </svg>
          <p>知识库中暂无文档</p>
          <span class="empty-hint">上传您的第一个文档开始构建知识库</span>
        </div>

        <div v-else class="docs-table-wrap">
          <table class="docs-table">
            <thead>
              <tr>
                <th class="col-title">标题</th>
                <th class="col-uploader">上传者</th>
                <th class="col-size">大小</th>
                <th class="col-status">状态</th>
                <th class="col-tags">标签</th>
                <th class="col-time">时间</th>
                <th class="col-action">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="doc in documents" :key="doc.id">
                <td class="col-title">
                  <span class="doc-name">{{ doc.title || doc.filename }}</span>
                  <span class="doc-filename">{{ doc.title ? doc.filename : '' }}</span>
                </td>
                <td class="col-uploader">{{ doc.uploaderName }}</td>
                <td class="col-size">{{ formatSize(doc.fileSize) }}</td>
                <td class="col-status">
                  <span class="status-badge" :class="'status-' + doc.status">{{ statusLabel(doc.status) }}</span>
                </td>
                <td class="col-tags">
                  <span v-if="doc.tags" class="tag-chip" v-for="tag in doc.tags.split(',')" :key="tag">{{ tag.trim() }}</span>
                  <span v-else class="no-tags">-</span>
                </td>
                <td class="col-time">{{ doc.createdAt?.substring(0, 10) }}</td>
                <td class="col-action">
                  <button class="delete-btn" @click="handleDelete(doc.id)" :disabled="deleting === doc.id">
                    {{ deleting === doc.id ? '...' : '删除' }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { knowledge } from '../api/index.js'

const documents = ref([])
const fileInput = ref(null)
const loading = ref(false)
const uploading = ref(false)
const uploadError = ref('')
const deleting = ref(null)
const selectedFiles = ref([])

async function loadDocs() {
  loading.value = true
  try {
    const { data } = await knowledge.list()
    documents.value = data.content || data
  } catch {
    documents.value = []
  } finally {
    loading.value = false
  }
}

function onFilesChange(e) {
  const files = Array.from(e.target.files || [])
  if (files.length > 5) {
    uploadError.value = '一次最多选择 5 个文件'
    return
  }
  uploadError.value = ''
  selectedFiles.value = files
}

function clearFiles() {
  selectedFiles.value = []
  if (fileInput.value) fileInput.value.value = ''
}

async function handleBatchSubmit() {
  if (!selectedFiles.value.length) return
  uploading.value = true
  uploadError.value = ''
  try {
    await knowledge.batchUpload(selectedFiles.value)
    clearFiles()
    await loadDocs()
  } catch {
    uploadError.value = '上传失败，请重试'
  } finally {
    uploading.value = false
  }
}

async function handleDelete(id) {
  if (!confirm('确定要删除该文档吗？')) return
  deleting.value = id
  try {
    await knowledge.delete(id)
    await loadDocs()
  } catch {
    alert('删除失败，请重试')
  } finally {
    deleting.value = null
  }
}

function formatSize(bytes) {
  if (!bytes) return '-'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

function statusLabel(status) {
  const map = { pending: '待处理', indexing: '索引中', indexed: '已索引', failed: '失败' }
  return map[status] || status
}

onMounted(loadDocs)
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;0,600;0,700;1,500&family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600&display=swap');
</style>

<style scoped>
.knowledge-page {
  min-height: 100vh;
  background: #f9f7f4;
  background-image:
    radial-gradient(ellipse at 20% 50%, rgba(99, 102, 241, 0.03) 0%, transparent 60%),
    radial-gradient(ellipse at 80% 20%, rgba(26, 26, 46, 0.02) 0%, transparent 50%);
  font-family: 'DM Sans', system-ui, -apple-system, sans-serif;
  color: #2d2d3a;
  -webkit-font-smoothing: antialiased;
}

/* ── Header ── */
.page-header {
  background: #1a1a2e;
  background-image:
    linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, transparent 50%),
    linear-gradient(to bottom, rgba(255,255,255,0.02), transparent);
  border-bottom: 1px solid rgba(255,255,255,0.06);
  position: sticky;
  top: 0;
  z-index: 10;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 32px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #fff;
}

.brand-icon {
  width: 22px;
  height: 22px;
  opacity: 0.7;
}

.header-brand h1 {
  font-family: 'Playfair Display', Georgia, serif;
  font-size: 1.35rem;
  font-weight: 600;
  letter-spacing: -0.01em;
  margin: 0;
}

.nav-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: rgba(255,255,255,0.7);
  text-decoration: none;
  font-size: 0.9rem;
  font-weight: 500;
  padding: 6px 16px;
  border-radius: 6px;
  transition: all 0.2s;
}
.nav-link:hover {
  color: #fff;
  background: rgba(255,255,255,0.08);
}

/* ── Body ── */
.page-body {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px;
}

/* ── Upload Card ── */
.upload-card {
  background: #fff;
  border: 1px solid rgba(0,0,0,0.06);
  border-radius: 12px;
  box-shadow:
    0 1px 3px rgba(0,0,0,0.03),
    0 4px 16px rgba(0,0,0,0.04);
  overflow: hidden;
}

.card-header {
  padding: 24px 28px 0;
}

.card-header h2 {
  font-family: 'Playfair Display', Georgia, serif;
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0 0 4px;
  color: #1a1a2e;
}

.card-subtitle {
  margin: 0;
  font-size: 0.875rem;
  color: #8c8c9a;
}

.upload-form {
  padding: 20px 28px 24px;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.span-full { grid-column: 1 / -1; }

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 0.8rem;
  font-weight: 600;
  color: #5b5b6e;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.required { color: #e04e5a; }

.form-input,
.form-textarea {
  font-family: inherit;
  font-size: 0.9rem;
  padding: 10px 14px;
  border: 1px solid #e2e2ea;
  border-radius: 8px;
  background: #fafafc;
  color: #2d2d3a;
  transition: all 0.2s;
  outline: none;
}
.form-input:focus,
.form-textarea:focus {
  border-color: #6366f1;
  background: #fff;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.08);
}
.form-input::placeholder,
.form-textarea::placeholder {
  color: #b8b8c6;
}

.form-textarea {
  resize: vertical;
  min-height: 60px;
}

/* File selector */
.file-group label {
  /* same as others */
}

.file-selector {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border: 1px dashed #d4d4de;
  border-radius: 8px;
  background: #fafafc;
  transition: all 0.2s;
  min-height: 44px;
}
.file-selector.has-files {
  border-color: #6366f1;
  border-style: solid;
  background: rgba(99, 102, 241, 0.02);
}

.file-input-hidden { display: none; }

.file-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  background: #f0f0f5;
  border: 1px solid #e2e2ea;
  border-radius: 6px;
  color: #5b5b6e;
  font-size: 0.85rem;
  font-family: inherit;
  cursor: pointer;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 320px;
  transition: all 0.15s;
}
.file-btn:hover {
  background: #e8e8f0;
  border-color: #6366f1;
}

.file-size {
  font-size: 0.8rem;
  color: #8c8c9a;
  white-space: nowrap;
}

.file-clear {
  background: none;
  border: none;
  font-size: 1.2rem;
  color: #b8b8c6;
  cursor: pointer;
  padding: 0 4px;
  line-height: 1;
  flex-shrink: 0;
}
.file-clear:hover { color: #e04e5a; }

/* File list */
.file-list {
  list-style: none;
  margin: 12px 0 0;
  padding: 0;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #fafafc;
  border: 1px solid #f0f0f5;
  border-radius: 6px;
  margin-bottom: 6px;
  font-size: 0.85rem;
}

.file-item:last-child { margin-bottom: 0; }

.file-item-icon { color: #6366f1; flex-shrink: 0; }

.file-item-name {
  flex: 1;
  color: #2d2d3a;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-item-size {
  color: #8c8c9a;
  flex-shrink: 0;
  font-variant-numeric: tabular-nums;
}

.file-hint {
  font-size: 0.8rem;
  color: #b8b8c6;
  white-space: nowrap;
}

.form-actions {
  margin-top: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.submit-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 24px;
  background: #1a1a2e;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-family: inherit;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}
.submit-btn:hover:not(:disabled) {
  background: #2a2a44;
  box-shadow: 0 4px 12px rgba(26, 26, 46, 0.2);
}
.submit-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.form-error {
  margin: 0;
  font-size: 0.85rem;
  color: #e04e5a;
}

.spinner {
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Docs Section ── */
.docs-section {
  margin-top: 32px;
}

.section-header {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 16px;
}

.section-header h2 {
  font-family: 'Playfair Display', Georgia, serif;
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0;
  color: #1a1a2e;
}

.count-badge {
  font-size: 0.8rem;
  color: #8c8c9a;
  background: rgba(0,0,0,0.04);
  padding: 3px 10px;
  border-radius: 20px;
  font-weight: 500;
}

/* States */
.state-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 64px 24px;
  text-align: center;
}

.state-box p {
  font-size: 0.95rem;
  color: #5b5b6e;
  margin: 0;
}

.state-spinner {
  animation: spin 1s linear infinite;
  color: #6366f1;
}

.empty-state svg {
  color: #b8b8c6;
}

.empty-state p {
  font-weight: 500;
  color: #5b5b6e;
}

.empty-hint {
  font-size: 0.85rem;
  color: #b8b8c6;
}

/* Table */
.docs-table-wrap {
  background: #fff;
  border: 1px solid rgba(0,0,0,0.06);
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.03), 0 4px 16px rgba(0,0,0,0.04);
  overflow: hidden;
}

.docs-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.docs-table thead {
  background: #fafafc;
  border-bottom: 2px solid #f0f0f5;
}

.docs-table th {
  padding: 12px 16px;
  text-align: left;
  font-size: 0.75rem;
  font-weight: 600;
  color: #8c8c9a;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  white-space: nowrap;
}

.docs-table td {
  padding: 14px 16px;
  border-bottom: 1px solid #f5f5f8;
  vertical-align: middle;
}

.docs-table tbody tr:last-child td {
  border-bottom: none;
}

.docs-table tbody tr:hover {
  background: rgba(99, 102, 241, 0.015);
}

.col-title {
  min-width: 200px;
}

.doc-name {
  display: block;
  font-weight: 600;
  color: #1a1a2e;
}

.doc-filename {
  display: block;
  font-size: 0.78rem;
  color: #b8b8c6;
  margin-top: 2px;
}

.col-uploader {
  color: #5b5b6e;
  white-space: nowrap;
}

.col-size {
  color: #8c8c9a;
  white-space: nowrap;
  font-variant-numeric: tabular-nums;
}

/* Status badges */
.status-badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 0.78rem;
  font-weight: 600;
  letter-spacing: 0.02em;
}

.status-pending {
  background: #fef3c7;
  color: #92400e;
}
.status-indexing {
  background: #dbeafe;
  color: #1e40af;
}
.status-indexed {
  background: #d1fae5;
  color: #065f46;
}
.status-failed {
  background: #fee2e2;
  color: #991b1b;
}

/* Tags */
.col-tags {
  max-width: 180px;
}

.tag-chip {
  display: inline-block;
  padding: 2px 8px;
  margin: 1px 3px 1px 0;
  border-radius: 4px;
  font-size: 0.75rem;
  background: rgba(99, 102, 241, 0.06);
  color: #4f46e5;
  white-space: nowrap;
}

.no-tags {
  color: #d4d4de;
}

.col-time {
  color: #8c8c9a;
  white-space: nowrap;
  font-variant-numeric: tabular-nums;
}

/* Delete */
.delete-btn {
  padding: 5px 14px;
  background: none;
  border: 1px solid #e2e2ea;
  border-radius: 6px;
  color: #8c8c9a;
  font-size: 0.8rem;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.15s;
}
.delete-btn:hover:not(:disabled) {
  border-color: #e04e5a;
  color: #e04e5a;
  background: rgba(224, 78, 90, 0.04);
}
.delete-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
