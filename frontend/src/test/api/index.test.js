import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.mock('axios', () => {
  const mockAxios = {
    create: vi.fn(() => mockAxios),
    get: vi.fn(() => Promise.resolve({ data: {} })),
    post: vi.fn(() => Promise.resolve({ data: {} })),
    delete: vi.fn(() => Promise.resolve({ data: {} })),
    interceptors: {
      request: { use: vi.fn() },
      response: { use: vi.fn() },
    },
  }
  return { default: mockAxios }
})

import axios from 'axios'
import { auth, knowledge, chat } from '../../api/index.js'

describe('API Module', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('auth', () => {
    it('login sends POST /api/auth/login', async () => {
      const res = { data: { accessToken: 'token', username: 'user' } }
      axios.post.mockResolvedValue(res)

      const result = await auth.login('testuser', 'testpass')

      expect(axios.post).toHaveBeenCalledWith('/auth/login', {
        username: 'testuser',
        password: 'testpass',
      })
      expect(result).toBe(res)
    })

    it('register sends POST /api/auth/register', async () => {
      const res = { data: { accessToken: 'token', username: 'newuser' } }
      axios.post.mockResolvedValue(res)

      const result = await auth.register('newuser', 'newpass')

      expect(axios.post).toHaveBeenCalledWith('/auth/register', {
        username: 'newuser',
        password: 'newpass',
      })
      expect(result).toBe(res)
    })
  })

  describe('knowledge', () => {
    it('upload creates FormData and sends POST /api/knowledge/documents', async () => {
      const file = new File(['test'], 'test.txt', { type: 'text/plain' })
      const res = { data: { id: 1 } }
      axios.post.mockResolvedValue(res)

      const result = await knowledge.upload(file, 'Test Title', 'Test Description', 'tag1,tag2')

      expect(axios.post).toHaveBeenCalledWith(
        '/knowledge/documents',
        expect.any(FormData),
      )
      const fd = axios.post.mock.calls[0][1]
      expect(fd.get('file')).toBe(file)
      expect(fd.get('title')).toBe('Test Title')
      expect(fd.get('description')).toBe('Test Description')
      expect(fd.get('tags')).toBe('tag1,tag2')
      expect(result).toBe(res)
    })

    it('upload omits optional fields', async () => {
      const file = new File(['test'], 'test.txt', { type: 'text/plain' })
      axios.post.mockResolvedValue({ data: {} })

      await knowledge.upload(file)

      const fd = axios.post.mock.calls[0][1]
      expect(fd.get('file')).toBe(file)
      expect(fd.get('title')).toBeNull()
      expect(fd.get('description')).toBeNull()
      expect(fd.get('tags')).toBeNull()
    })

    it('list sends GET /api/knowledge/documents with default pagination', async () => {
      await knowledge.list()

      expect(axios.get).toHaveBeenCalledWith('/knowledge/documents', {
        params: { page: 0, size: 20 },
      })
    })

    it('list sends GET /api/knowledge/documents with custom pagination', async () => {
      await knowledge.list(1, 50)

      expect(axios.get).toHaveBeenCalledWith('/knowledge/documents', {
        params: { page: 1, size: 50 },
      })
    })

    it('delete sends DELETE /api/knowledge/documents/:id', async () => {
      await knowledge.delete(1)

      expect(axios.delete).toHaveBeenCalledWith('/knowledge/documents/1')
    })
  })

  describe('chat', () => {
    it('createSession sends POST /api/chat/sessions', async () => {
      await chat.createSession('新对话')

      expect(axios.post).toHaveBeenCalledWith('/chat/sessions', { title: '新对话' })
    })

    it('listSessions sends GET /api/chat/sessions', async () => {
      await chat.listSessions()

      expect(axios.get).toHaveBeenCalledWith('/chat/sessions')
    })

    it('deleteSession sends DELETE /api/chat/sessions/:id', async () => {
      await chat.deleteSession(5)

      expect(axios.delete).toHaveBeenCalledWith('/chat/sessions/5')
    })

    it('sendMessage sends POST /api/chat/sessions/:id/messages', async () => {
      await chat.sendMessage(1, 'Hello', [1, 2])

      expect(axios.post).toHaveBeenCalledWith('/chat/sessions/1/messages', {
        query: 'Hello',
        fileIds: [1, 2],
      })
    })

    it('sendMessage sends POST without fileIds when not provided', async () => {
      await chat.sendMessage(1, 'Hello')

      expect(axios.post).toHaveBeenCalledWith('/chat/sessions/1/messages', {
        query: 'Hello',
        fileIds: undefined,
      })
    })

    it('sendMessageWithFiles sends POST with FormData', async () => {
      const file = new File(['test'], 'test.pdf', { type: 'application/pdf' })
      await chat.sendMessageWithFiles(1, 'Hello', [file])

      expect(axios.post).toHaveBeenCalledWith(
        '/chat/sessions/1/messages',
        expect.any(FormData),
        { headers: { 'Content-Type': 'multipart/form-data' } },
      )
      const fd = axios.post.mock.calls[0][1]
      expect(fd.get('query')).toBe('Hello')
      expect(fd.get('files')).toBe(file)
    })

    it('listMessages sends GET /api/chat/sessions/:id/messages', async () => {
      await chat.listMessages(1)

      expect(axios.get).toHaveBeenCalledWith('/chat/sessions/1/messages')
    })
  })
})
