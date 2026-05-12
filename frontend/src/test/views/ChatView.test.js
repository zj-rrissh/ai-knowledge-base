import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'

vi.mock('@/api', () => ({
  chat: {
    listSessions: vi.fn(),
    createSession: vi.fn(),
    deleteSession: vi.fn(),
    sendMessage: vi.fn(),
    sendMessageWithFiles: vi.fn(),
    listMessages: vi.fn(),
  },
  knowledge: {
    upload: vi.fn(),
  },
}))

import { chat } from '@/api'
import ChatView from '../../views/ChatView.vue'

const mockRouter = createRouter({ history: createWebHistory(), routes: [] })

function settle() {
  return new Promise((resolve) => setTimeout(resolve, 0))
}

describe('ChatView', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.setItem('username', '测试用户')

    chat.listSessions.mockResolvedValue({ data: [] })
    chat.createSession.mockResolvedValue({ data: { id: 1, title: '新对话' } })
    chat.listMessages.mockResolvedValue({ data: [] })
    chat.sendMessage.mockResolvedValue({ data: { id: 100, role: 'assistant', content: 'AI 回复' } })

    wrapper = mount(ChatView, {
      global: { plugins: [mockRouter] },
    })
  })

  describe('on mount', () => {
    it('loads sessions', () => {
      expect(chat.listSessions).toHaveBeenCalledTimes(1)
    })

    it('shows welcome screen when no session selected', () => {
      expect(wrapper.text()).toContain('AI 知识库助手')
    })
  })

  describe('session management', () => {
    it('creates a new session and selects it', async () => {
      await wrapper.find('.new-chat-btn').trigger('click')
      await settle()
      await wrapper.vm.$nextTick()

      expect(chat.createSession).toHaveBeenCalledWith('新对话')
      expect(chat.listMessages).toHaveBeenCalledWith(1)
    })

    it('selects a session from the sidebar', async () => {
      chat.listSessions.mockResolvedValue({
        data: [{ id: 5, title: '已有对话' }],
      })

      wrapper = mount(ChatView, {
        global: { plugins: [mockRouter] },
      })
      await settle()
      await wrapper.vm.$nextTick()

      await wrapper.find('.session-item').trigger('click')
      await settle()
      await wrapper.vm.$nextTick()

      expect(chat.listMessages).toHaveBeenCalledWith(5)
    })

    it('deletes a session', async () => {
      chat.listSessions.mockResolvedValue({
        data: [{ id: 3, title: '待删除' }],
      })

      wrapper = mount(ChatView, {
        global: { plugins: [mockRouter] },
      })
      await settle()
      await wrapper.vm.$nextTick()

      await wrapper.find('.session-delete').trigger('click')
      await settle()
      await wrapper.vm.$nextTick()

      expect(chat.deleteSession).toHaveBeenCalledWith(3)
    })
  })

  describe('sending messages', () => {
    it('sends a message in an existing session', async () => {
      // First create a session
      await wrapper.find('.new-chat-btn').trigger('click')
      await settle()
      await wrapper.vm.$nextTick()

      // Type and send a message
      const textarea = wrapper.find('textarea')
      await textarea.setValue('你好，AI')
      await wrapper.find('.send-btn').trigger('click')
      await settle()
      await wrapper.vm.$nextTick()

      expect(chat.sendMessage).toHaveBeenCalled()
    })

    it('disables send button when query is empty', () => {
      const sendBtn = wrapper.find('.send-btn')
      expect(sendBtn.attributes('disabled')).toBe('')
    })

    it('disables send button while sending', async () => {
      // Make sendMessage never resolve to keep sending=true
      chat.sendMessage.mockReturnValue(new Promise(() => {}))

      await wrapper.find('.new-chat-btn').trigger('click')
      await settle()

      const textarea = wrapper.find('textarea')
      await textarea.setValue('test message')
      await wrapper.find('.send-btn').trigger('click')
      await settle()

      const sendBtn = wrapper.find('.send-btn')
      expect(sendBtn.attributes('disabled')).toBe('')
    })
  })

  describe('file selection', () => {
    it('handles file selection', async () => {
      await wrapper.find('.new-chat-btn').trigger('click')
      await settle()

      const file = new File(['content'], 'report.pdf', { type: 'application/pdf' })
      const fileInput = wrapper.find('input[type="file"][multiple]')
      Object.defineProperty(fileInput.element, 'files', { value: [file] })
      await fileInput.trigger('change')
      await settle()
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('report.pdf')
    })

    it('removes a selected file', async () => {
      await wrapper.find('.new-chat-btn').trigger('click')
      await settle()

      const file = new File(['content'], 'temp.pdf', { type: 'application/pdf' })
      const fileInput = wrapper.find('input[type="file"][multiple]')
      Object.defineProperty(fileInput.element, 'files', { value: [file] })
      await fileInput.trigger('change')
      await settle()
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('temp.pdf')

      await wrapper.find('.chip-remove').trigger('click')
      await settle()
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).not.toContain('temp.pdf')
    })
  })
})
