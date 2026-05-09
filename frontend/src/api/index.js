import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  res => res,
  err => {
    if (err.response?.status === 401 || err.response?.status === 403) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export const auth = {
  login: (username, password) => api.post('/auth/login', { username, password }),
  register: (username, password) => api.post('/auth/register', { username, password }),
}

export const knowledge = {
  upload: (file, title, description, tags) => {
    const fd = new FormData()
    fd.append('file', file)
    if (title) fd.append('title', title)
    if (description) fd.append('description', description)
    if (tags) fd.append('tags', tags)
    return api.post('/knowledge/documents', fd, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  list: (page = 0, size = 20) => api.get('/knowledge/documents', { params: { page, size } }),
  delete: (id) => api.delete(`/knowledge/documents/${id}`),
}

export const chat = {
  createSession: (title) => api.post('/chat/sessions', { title }),
  listSessions: () => api.get('/chat/sessions'),
  deleteSession: (id) => api.delete(`/chat/sessions/${id}`),
  sendMessage: (sessionId, query, fileIds) => api.post(`/chat/sessions/${sessionId}/messages`, { query, fileIds }),
  sendMessageWithFiles: (sessionId, query, files) => {
    const fd = new FormData()
    fd.append('query', query)
    files.forEach((f) => fd.append('files', f))
    return api.post(`/chat/sessions/${sessionId}/messages`, fd, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  listMessages: (sessionId) => api.get(`/chat/sessions/${sessionId}/messages`),
}

export default api
