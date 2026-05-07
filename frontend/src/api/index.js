import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8080/api',
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
    if (err.response?.status === 401) {
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
  upload: (file) => { const fd = new FormData(); fd.append('file', file); return api.post('/knowledge/documents', fd) },
  list: (page = 0, size = 20) => api.get('/knowledge/documents', { params: { page, size } }),
  delete: (id) => api.delete(`/knowledge/documents/${id}`),
}

export const chat = {
  createSession: (title) => api.post('/chat/sessions', { title }),
  listSessions: () => api.get('/chat/sessions'),
  deleteSession: (id) => api.delete(`/chat/sessions/${id}`),
  sendMessage: (sessionId, query) => api.post(`/chat/sessions/${sessionId}/messages`, { query }),
  listMessages: (sessionId) => api.get(`/chat/sessions/${sessionId}/messages`),
}

export default api
