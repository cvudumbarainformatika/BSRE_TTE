import { route } from 'quasar/wrappers'
import { createRouter, createMemoryHistory, createWebHistory, createWebHashHistory } from 'vue-router'
import routes from './routes'

export default route(function (/* { store, ssrContext } */) {
  const createHistory = process.env.SERVER
    ? createMemoryHistory
    : (process.env.VUE_ROUTER_MODE === 'history' ? createWebHistory : createWebHashHistory)

  const Router = createRouter({
    scrollBehavior: () => ({ left: 0, top: 0 }),
    routes,
    history: createHistory(process.env.VUE_ROUTER_BASE)
  })

  Router.beforeEach((to, from, next) => {
    const user = JSON.parse(localStorage.getItem('user'))
    
    // Logic Admin sederhana (bisa disesuaikan nanti dengan role dari API baru)
    const isAdmin = user?.role === 'admin' || user?.is_admin === 1

    // Route yang butuh login
    if (to.matched.some(record => record.meta.requiresAuth)) {
      if (!user) {
        // Belum login → ke halaman login
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
      if (user) {
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