import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.mock('@/api', () => ({}))

describe('Router', () => {
  let router

  beforeEach(async () => {
    localStorage.clear()
    const routerModule = await import('../../router/index.js')
    router = routerModule.default
  })

  it('has a route for /login', () => {
    const routes = router.getRoutes()
    expect(routes.some((r) => r.path === '/login')).toBe(true)
  })

  it('has a route for /knowledge', () => {
    const routes = router.getRoutes()
    expect(routes.some((r) => r.path === '/knowledge')).toBe(true)
  })

  it('has a route for /chat', () => {
    const routes = router.getRoutes()
    expect(routes.some((r) => r.path === '/chat')).toBe(true)
  })

  it('redirects / to /chat when token exists', async () => {
    localStorage.setItem('token', 'valid-token')
    await router.push('/')
    expect(router.currentRoute.value.path).toBe('/chat')
  })

  it('redirects /knowledge to /login when no token', async () => {
    localStorage.removeItem('token')
    await router.push('/knowledge')
    expect(router.currentRoute.value.path).toBe('/login')
  })

  it('redirects /chat to /login when no token', async () => {
    localStorage.removeItem('token')
    await router.push('/chat')
    expect(router.currentRoute.value.path).toBe('/login')
  })

  it('allows access to /login without token', async () => {
    localStorage.removeItem('token')
    await router.push('/login')
    expect(router.currentRoute.value.path).toBe('/login')
  })

  it('allows access to /knowledge with token', async () => {
    localStorage.setItem('token', 'valid-token')
    await router.push('/knowledge')
    expect(router.currentRoute.value.path).toBe('/knowledge')
  })

  it('allows access to /chat with token', async () => {
    localStorage.setItem('token', 'valid-token')
    await router.push('/chat')
    expect(router.currentRoute.value.path).toBe('/chat')
  })
})
