import { boot } from 'quasar/wrappers'
import { useAuthStore } from '@/stores/auth' // Import store auth
import { useNotificationStore } from '@/stores/notification' // Import store notifikasi

// import axios
import axios from 'axios'

// Be careful when using SSR for cross-request state pollution
// due to creating a Singleton instance here;
// If any client changes this (global) instance, it might be a
// good idea to move this inside of the "export default () => {}"
// function below (which runs individually for each client)
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/', // Default ke '/' jika env kosong, bukan '/api'
  timeout: 60000, // Timeout 60 detik (untuk upload file besar)
  // headers: {
  //   'Content-Type': 'application/json'
  // }
})

// Interceptor untuk menambahkan token otomatis
api.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    if (authStore.accessToken) {
      config.headers.Authorization = `Bearer ${authStore.accessToken}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Interceptor untuk menangani error otomatis (misalnya token expired)
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    // Tangani error jaringan
    if (!error.response) {
      console.error('Network Error:', error.message || 'Network Error');
      console.error('Request details:', error.request);

      // Gunakan sistem notifikasi global
      const notificationStore = useNotificationStore();
      notificationStore.showError(
        'Kesalahan Jaringan',
        'Tidak dapat terhubung ke server. Pastikan backend sedang berjalan.'
      );
    } else if (error.response?.status === 401) {
      // Cek apakah ini permintaan login atau change password
      const isLoginRequest = error.response.config.url.includes('/login');
      const isChangePasswordRequest = error.response.config.url.includes('/auth/change-password');

      if (!isLoginRequest && !isChangePasswordRequest) {
        // Jika bukan permintaan login atau change password, mungkin token expired
        const authStore = useAuthStore()
        authStore.logout()

        // Beri notifikasi bahwa sesi telah habis
        const notificationStore = useNotificationStore();
        notificationStore.showInfo(
          'Sesi Anda telah habis',
          'Silakan login kembali.'
        );

        // Redirect ke halaman login
        window.location.href = '/login'
      }
      // Jika ini adalah permintaan login/change-password dan gagal (401), kita biarkan komponen menanganinya
    } else if (error.response?.status === 400 && error.response.config.url.includes('/login')) {
      // Jika permintaan login gagal karena kredensial salah (status 400 atau 401 tergantung implementasi backend)
      // Tapi umumnya login gagal menghasilkan 200 dengan data sukses: false atau 401
      // Dalam kasus ini, we need to handle login error in component LoginPage.vue, not here
    }
    return Promise.reject(error)
  }
)

export default boot(({ app }) => {
  // for use inside Vue files (Options API) through this.$axios and this.$api

  app.config.globalProperties.$axios = axios
  // ^ ^ ^ this will allow you to use this.$axios (for Vue Options API form)
  //       so you won't necessarily have to import axios in each vue file

  app.config.globalProperties.$api = api
  // ^ ^ ^ this will allow you to use this.$api (for Vue Options API form)
  //       so you can easily perform requests against your app's API
})

export { api }