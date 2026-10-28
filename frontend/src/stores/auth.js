import { defineStore } from 'pinia'
import axios from 'axios'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('user')) || null,
    loading: false,
    error: null
  }),

  getters: {
    isAuthenticated: (state) => !!state.user,
    isAdmin: (state) => state.user?.role === 'admin' || state.user?.is_admin === 1,
    accessToken: (state) => state.user?.token
  },

  actions: {
    async login(username, password) {
      this.loading = true
      this.error = null
      try {
        const response = await axios.post('/api/front/login', { username, password })
        if (response.data.success) {
          this.user = response.data.data
          localStorage.setItem('user', JSON.stringify(this.user))
          return true
        }
        return false
      } catch (err) {
        this.error = err.response?.data?.message || 'Terjadi kesalahan saat login'
        return false
      } finally {
        this.loading = false
      }
    },

    logout() {
      this.user = null
      localStorage.removeItem('user')
    }
  }
})