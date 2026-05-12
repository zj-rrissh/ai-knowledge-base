import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'

const mockPush = vi.fn()

vi.mock('vue-router', async () => {
  const actual = await vi.importActual('vue-router')
  return { ...actual, useRouter: () => ({ push: mockPush }) }
})

vi.mock('@/api', () => ({
  auth: {
    login: vi.fn(),
    register: vi.fn(),
  },
}))

import { auth } from '@/api'
import LoginView from '../../views/LoginView.vue'

describe('LoginView', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
    wrapper = mount(LoginView)
  })

  it('renders the login form', () => {
    expect(wrapper.find('form').exists()).toBe(true)
    expect(wrapper.find('input').exists()).toBe(true)
    expect(wrapper.find('input[type="password"]').exists()).toBe(true)
    expect(wrapper.find('button[type="submit"]').exists()).toBe(true)
  })

  it('shows login mode by default', () => {
    expect(wrapper.find('button').text()).toBe('登录')
    expect(wrapper.text()).not.toContain('已有账号？去登录')
    expect(wrapper.text()).toContain('没有账号？去注册')
  })

  it('toggles to register mode', async () => {
    await wrapper.find('.toggle').trigger('click')

    expect(wrapper.find('button').text()).toBe('注册')
    expect(wrapper.text()).toContain('已有账号？去登录')
    expect(wrapper.text()).not.toContain('没有账号？去注册')
  })

  it('toggles back to login mode', async () => {
    await wrapper.find('.toggle').trigger('click')
    await wrapper.find('.toggle').trigger('click')

    expect(wrapper.find('button').text()).toBe('登录')
  })

  it('calls auth.login with credentials on login submit', async () => {
    auth.login.mockResolvedValue({ data: { accessToken: 'test-token', username: 'testuser' } })

    const inputs = wrapper.findAll('input')
    await inputs[0].setValue('testuser')
    await inputs[1].setValue('password123')
    await wrapper.find('form').trigger('submit')

    expect(auth.login).toHaveBeenCalledWith('testuser', 'password123')
  })

  it('stores token on successful login and redirects to /chat', async () => {
    auth.login.mockResolvedValue({ data: { accessToken: 'test-token', username: 'testuser' } })

    const inputs = wrapper.findAll('input')
    await inputs[0].setValue('testuser')
    await inputs[1].setValue('password123')
    await wrapper.find('form').trigger('submit')

    expect(localStorage.getItem('token')).toBe('test-token')
    expect(localStorage.getItem('username')).toBe('testuser')
    expect(mockPush).toHaveBeenCalledWith('/chat')
  })

  it('calls auth.register in register mode', async () => {
    auth.register.mockResolvedValue({ data: { accessToken: 'new-token', username: 'newuser' } })

    await wrapper.find('.toggle').trigger('click')

    const inputs = wrapper.findAll('input')
    await inputs[0].setValue('newuser')
    await inputs[1].setValue('newpass')
    await wrapper.find('form').trigger('submit')

    expect(auth.register).toHaveBeenCalledWith('newuser', 'newpass')
  })

  it('stores token on successful register and redirects to /chat', async () => {
    auth.register.mockResolvedValue({ data: { accessToken: 'new-token', username: 'newuser' } })

    await wrapper.find('.toggle').trigger('click')

    const inputs = wrapper.findAll('input')
    await inputs[0].setValue('newuser')
    await inputs[1].setValue('newpass')
    await wrapper.find('form').trigger('submit')

    expect(localStorage.getItem('token')).toBe('new-token')
    expect(localStorage.getItem('username')).toBe('newuser')
    expect(mockPush).toHaveBeenCalledWith('/chat')
  })

  it('shows error message on login failure', async () => {
    auth.login.mockRejectedValue({ response: { data: { message: '用户名或密码错误' } } })

    const inputs = wrapper.findAll('input')
    await inputs[0].setValue('wrong')
    await inputs[1].setValue('wrong')
    await wrapper.find('form').trigger('submit')

    expect(wrapper.text()).toContain('用户名或密码错误')
  })

  it('shows generic error when response has no message', async () => {
    auth.login.mockRejectedValue({ response: { data: {} } })

    const inputs = wrapper.findAll('input')
    await inputs[0].setValue('test')
    await inputs[1].setValue('test')
    await wrapper.find('form').trigger('submit')

    expect(wrapper.text()).toContain('操作失败')
  })
})
