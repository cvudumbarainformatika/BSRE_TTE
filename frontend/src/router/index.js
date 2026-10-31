import { route } from 'quasar/wrappers'
import { createRouter, createMemoryHistory, createWebHistory, createWebHashHistory } from 'vue-router'
import routes from './routes'
import axios from 'axios'

export default route(function (/* { store, ssrContext } */) {
  const createHistory = process.env.SERVER
    ? createMemoryHistory
    : (process.env.VUE_ROUTER_MODE === 'history' ? createWebHistory : createWebHashHistory)

  const Router = createRouter({
    scrollBehavior: () => ({ left: 0, top: 0 }),
    routes,
    history: createHistory(process.env.VUE_ROUTER_BASE)
  })

  // Listener untuk postMessage SSO dari window parent SIMRS (jika dipasang di <iframe>)
  if (typeof window !== 'undefined') {
    window.addEventListener('message', async (event) => {
      if (event.data && (event.data.type === 'SIMRS_SSO_AUTH' || event.data.sso_token)) {
        const ssoToken = event.data.sso_token || event.data.token
        const nip = event.data.nip
        try {
          const res = await axios.post('/api/v1/auth/sso-login', {
            sso_token: ssoToken,
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
    // 1. Cek apakah ada parameter SSO dari query URL (misal: ?sso_token=... atau ?token=... atau ?nip=...)
    const ssoToken = to.query.sso_token || to.query.token
    const ssoNip = to.query.nip
    if (ssoToken || ssoNip) {
      try {
        const res = await axios.post('/api/v1/auth/sso-login', {
          sso_token: typeof ssoToken === 'string' ? ssoToken : undefined,
          nip: typeof ssoNip === 'string' ? ssoNip : undefined
        })
        if (res.data && res.data.access_token) {
          localStorage.setItem('access_token', res.data.access_token)
          localStorage.setItem('user', JSON.stringify(res.data.user))
          
          // Bersihkan query param sso_token dari URL agar rapi
          const query = { ...to.query }
          delete query.sso_token
          delete query.token
          delete query.nip
          return next({ path: to.path === '/login' ? '/' : to.path, query, replace: true })
        }
      } catch (err) {
        console.error('SSO SIMRS Authentication failed:', err)
      }
    }

    const token = localStorage.getItem('access_token')
    const user = JSON.parse(localStorage.getItem('user') || 'null')
    const isAuthenticated = !!(token && user)
    
    // Logic Admin sederhana
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