import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'

vi.mock('@/api', () => ({
  knowledge: {
    list: vi.fn(),
    upload: vi.fn(),
    delete: vi.fn(),
  },
}))

import { knowledge } from '@/api'
import KnowledgeView from '../../views/KnowledgeView.vue'

const mockRouter = createRouter({ history: createWebHistory(), routes: [] })

/** Helper: wait for Vue reactivity and pending promises to settle */
function settle() {
  return new Promise((resolve) => setTimeout(resolve, 0))
}

describe('KnowledgeView', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    knowledge.list.mockResolvedValue({ data: { content: [] } })

    wrapper = mount(KnowledgeView, {
      global: { plugins: [mockRouter] },
    })
  })

  describe('on mount', () => {
    it('calls knowledge.list', () => {
      expect(knowledge.list).toHaveBeenCalledTimes(1)
    })

    it('shows empty state when no documents', async () => {
      await wrapper.vm.$nextTick()
      expect(wrapper.text()).toContain('暂无文档')
    })
  })

  describe('document list', () => {
    it('renders documents when list returns data', async () => {
      knowledge.list.mockResolvedValue({
        data: {
          content: [
            {
              id: 1,
              title: '测试文档',
              filename: 'test.pdf',
              fileSize: 2048,
              status: 'indexed',
              uploaderName: 'Alice',
              tags: '技术,文档',
              createdAt: '2025-01-15T10:00:00',
            },
          ],
        },
      })

      wrapper = mount(KnowledgeView, {
        global: { plugins: [mockRouter] },
      })
      await settle()
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('测试文档')
      expect(wrapper.text()).toContain('Alice')
      expect(wrapper.text()).toContain('已索引')
      expect(wrapper.text()).toContain('技术')
      expect(wrapper.text()).toContain('文档')
    })

    it('displays file size in human-readable format', async () => {
      knowledge.list.mockResolvedValue({
        data: {
          content: [
            { id: 1, title: 'Small', fileSize: 500, status: 'indexed', uploaderName: 'U', tags: '', createdAt: '' },
            { id: 2, title: 'Medium', fileSize: 2048, status: 'indexed', uploaderName: 'U', tags: '', createdAt: '' },
            { id: 3, title: 'Large', fileSize: 3145728, status: 'indexed', uploaderName: 'U', tags: '', createdAt: '' },
          ],
        },
      })

      wrapper = mount(KnowledgeView, {
        global: { plugins: [mockRouter] },
      })
      await settle()
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('500 B')
      expect(wrapper.text()).toContain('2.0 KB')
      expect(wrapper.text()).toContain('3.0 MB')
    })

    it('displays status labels correctly', async () => {
      knowledge.list.mockResolvedValue({
        data: {
          content: [
            { id: 1, title: 'A', fileSize: 0, status: 'pending', uploaderName: 'U', tags: '', createdAt: '' },
            { id: 2, title: 'B', fileSize: 0, status: 'indexing', uploaderName: 'U', tags: '', createdAt: '' },
            { id: 3, title: 'C', fileSize: 0, status: 'indexed', uploaderName: 'U', tags: '', createdAt: '' },
            { id: 4, title: 'D', fileSize: 0, status: 'failed', uploaderName: 'U', tags: '', createdAt: '' },
          ],
        },
      })

      wrapper = mount(KnowledgeView, {
        global: { plugins: [mockRouter] },
      })
      await settle()
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('待处理')
      expect(wrapper.text()).toContain('索引中')
      expect(wrapper.text()).toContain('已索引')
      expect(wrapper.text()).toContain('失败')
    })
  })

  describe('upload', () => {
    it('calls knowledge.upload on form submit and refreshes list', async () => {
      knowledge.upload.mockResolvedValue({ data: { id: 1 } })
      knowledge.list.mockResolvedValue({ data: { content: [] } })

      const file = new File(['content'], 'mydoc.pdf', { type: 'application/pdf' })
      const fileInput = wrapper.find('input[type="file"]')
      Object.defineProperty(fileInput.element, 'files', { value: [file] })
      await fileInput.trigger('change')

      const titleInput = wrapper.find('#doc-title')
      await titleInput.setValue('我的文档')

      await wrapper.find('form').trigger('submit')
      await settle()
      await wrapper.vm.$nextTick()

      expect(knowledge.upload).toHaveBeenCalledWith(file, '我的文档', '', '')
      expect(knowledge.list).toHaveBeenCalledTimes(2)
    })

    it('does not submit without title', async () => {
      // File selected but no title set
      const file = new File(['content'], 'doc.pdf', { type: 'application/pdf' })
      const fileInput = wrapper.find('input[type="file"]')
      Object.defineProperty(fileInput.element, 'files', { value: [file] })
      await fileInput.trigger('change')

      // Clear the auto-filled title
      const titleInput = wrapper.find('#doc-title')
      await titleInput.setValue('')

      await wrapper.find('form').trigger('submit')
      await settle()

      expect(knowledge.upload).not.toHaveBeenCalled()
    })

    it('does not submit without file', async () => {
      const titleInput = wrapper.find('#doc-title')
      await titleInput.setValue('无文件文档')

      await wrapper.find('form').trigger('submit')
      await settle()

      expect(knowledge.upload).not.toHaveBeenCalled()
    })

    it('shows upload error on failure', async () => {
      knowledge.upload.mockRejectedValue(new Error('Network error'))

      const file = new File(['content'], 'doc.pdf', { type: 'application/pdf' })
      const fileInput = wrapper.find('input[type="file"]')
      Object.defineProperty(fileInput.element, 'files', { value: [file] })
      await fileInput.trigger('change')

      const titleInput = wrapper.find('#doc-title')
      await titleInput.setValue('我的文档')

      await wrapper.find('form').trigger('submit')
      await settle()
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('上传失败')
    })
  })

  describe('delete', () => {
    it('calls knowledge.delete when confirm is accepted', async () => {
      knowledge.list.mockResolvedValue({
        data: {
          content: [
            { id: 42, title: 'To Delete', filename: 'del.pdf', fileSize: 100, status: 'indexed', uploaderName: 'U', tags: '', createdAt: '' },
          ],
        },
      })
      knowledge.delete.mockResolvedValue({ data: {} })

      vi.spyOn(window, 'confirm').mockReturnValue(true)

      wrapper = mount(KnowledgeView, {
        global: { plugins: [mockRouter] },
      })
      await settle()
      await wrapper.vm.$nextTick()

      await wrapper.find('.delete-btn').trigger('click')
      await settle()
      await wrapper.vm.$nextTick()

      expect(window.confirm).toHaveBeenCalled()
      expect(knowledge.delete).toHaveBeenCalledWith(42)
    })

    it('does not call knowledge.delete when confirm is cancelled', async () => {
      knowledge.list.mockResolvedValue({
        data: {
          content: [
            { id: 42, title: 'To Delete', filename: 'del.pdf', fileSize: 100, status: 'indexed', uploaderName: 'U', tags: '', createdAt: '' },
          ],
        },
      })

      vi.spyOn(window, 'confirm').mockReturnValue(false)

      wrapper = mount(KnowledgeView, {
        global: { plugins: [mockRouter] },
      })
      await settle()
      await wrapper.vm.$nextTick()

      await wrapper.find('.delete-btn').trigger('click')
      await settle()

      expect(knowledge.delete).not.toHaveBeenCalled()
    })
  })
})
