import { route } from 'quasar/wrappers'
import { createRouter, createMemoryHistory, createWebHistory, createWebHashHistory } from 'vue-router'
import routes from './routes'
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8005/api/v1'

export default route(function (/* { store, ssrContext } */) {
  const createHistory = process.env.SERVER
    ? createMemoryHistory
    : (process.env.VUE_ROUTER_MODE === 'history' ? createWebHistory : createWebHashHistory)

  const Router = createRouter({
    scrollBehavior: () => ({ left: 0, top: 0 }),
    routes,
    history: createHistory(process.env.VUE_ROUTER_BASE)
  })

  // Helper untuk membersihkan query SSO dari search dan hash URL browser
  const cleanSsoUrl = (to) => {
    if (typeof window !== 'undefined' && window.location.search) {
      const cleanPath = window.location.pathname + (window.location.hash || '#/')
      window.history.replaceState(null, '', cleanPath)
    }
    const cleanQuery = { ...to.query }
    delete cleanQuery.sso_ticket
    delete cleanQuery.ticket
    delete cleanQuery.sso_token
    delete cleanQuery.token
    delete cleanQuery.nip
    delete cleanQuery.username
    delete cleanQuery.user
    delete cleanQuery.kd_pegawai
    return cleanQuery
  }

  // Listener untuk postMessage SSO dari window parent SIMRS (jika di-embed di <iframe> atau modal)
  if (typeof window !== 'undefined') {
    window.addEventListener('message', async (event) => {
      if (event.data && (event.data.type === 'SIMRS_SSO_AUTH' || event.data.sso_token || event.data.nip || event.data.sso_ticket)) {
        const ssoToken = event.data.sso_token || event.data.token
        const ssoTicket = event.data.sso_ticket || event.data.ticket
        const nip = event.data.nip || event.data.username || event.data.user
        try {
          const res = await axios.post(`${API_BASE_URL}/auth/sso-login`, {
            sso_token: ssoToken,
            sso_ticket: ssoTicket,
            nip: nip
          })
          if (res.data && res.data.access_token) {
            localStorage.setItem('access_token', res.data.access_token)
            localStorage.setItem('user', JSON.stringify(res.data.user))
            if (Router.currentRoute.value.path === '/login') {
              Router.push('/')
            }
          }
        } catch (e) {
          console.warn('Gagal memproses postMessage SSO dari SIMRS:', e)
        }
      }
    })
  }

  Router.beforeEach(async (to, from, next) => {
    // 1. Ekstrak parameter SSO dari Hash Query (to.query) maupun Window Search (?param di luar hash)
    let searchParams = null
    if (typeof window !== 'undefined' && window.location.search) {
      searchParams = new URLSearchParams(window.location.search)
    }

    const ssoTicket = to.query.sso_ticket || to.query.ticket || searchParams?.get('sso_ticket') || searchParams?.get('ticket')
    const ssoToken = to.query.sso_token || to.query.token || searchParams?.get('sso_token') || searchParams?.get('token')
    const ssoNip = to.query.nip || to.query.username || to.query.user || to.query.kd_pegawai ||
                   searchParams?.get('nip') || searchParams?.get('username') || searchParams?.get('user') || searchParams?.get('kd_pegawai')

    if (ssoTicket || ssoToken || ssoNip) {
      try {
        const res = await axios.post(`${API_BASE_URL}/auth/sso-login`, {
          sso_ticket: typeof ssoTicket === 'string' ? ssoTicket : undefined,
          sso_token: typeof ssoToken === 'string' ? ssoToken : undefined,
          nip: typeof ssoNip === 'string' ? ssoNip : undefined
        })
        if (res.data && res.data.access_token) {
          localStorage.setItem('access_token', res.data.access_token)
          localStorage.setItem('user', JSON.stringify(res.data.user))

          const query = cleanSsoUrl(to)
          return next({ path: to.path === '/login' ? '/' : to.path, query, replace: true })
        }
      } catch (err) {
        console.error('SSO SIMRS Authentication failed:', err)
      }
    }

    const token = localStorage.getItem('access_token')
    const user = JSON.parse(localStorage.getItem('user') || 'null')
    const isAuthenticated = !!(token && user)
    
    // Logic Admin
    const isAdmin = user?.role === 'admin' || user?.is_admin === 1

    // Route yang butuh login
    if (to.matched.some(record => record.meta.requiresAuth)) {
      if (!isAuthenticated) {
        // Belum login & tidak ada SSO → wajib ke halaman login
        next('/login')
      } else if (to.matched.some(record => record.meta.requiresAdmin) && !isAdmin) {
        // Sudah login tapi bukan admin → ke dashboard root
        next('/')
      } else {
        next()
      }
    }
    // Route khusus tamu (login page)
    else if (to.matched.some(record => record.meta.guestOnly)) {
      if (isAuthenticated) {
        // Sudah login → langsung ke dashboard root
        next('/')
      } else {
        next()
      }
    }
    // Route publik atau lainnya
    else {
      next()
    }
  })

  return Router
})