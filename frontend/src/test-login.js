// File uji sederhana untuk menguji permintaan login ke backend
import { api } from './boot/axios'

export async function testLogin() {
  try {
    console.log('Mencoba login...')
    console.log('Base URL:', api.defaults.baseURL)

    // Kirim permintaan login
    const response = await api.post('/auth/login', {
      email: 'yahyaric',
      password: 'yahya2019@@'
    })

    console.log('Login berhasil:', response.data)

    // Jika berhasil, simpan token ke localStorage untuk digunakan di permintaan berikutnya
    if (response.data.success && response.data.data.access_token) {
      localStorage.setItem('access_token', response.data.data.access_token)
      console.log('Token disimpan ke localStorage')
    }
  } catch (error) {
    console.error('Login gagal:', error.message)

    // Log error tambahan jika tersedia
    if (error.response) {
      console.error('Response error:', error.response.status, error.response.data)
    } else if (error.request) {
      console.error('Request error:', error.request)
      console.error('Kemungkinan besar ini adalah masalah CORS atau jaringan')
      console.error('Periksa konsol jaringan (Network tab) di developer tools untuk detail lebih lanjut')
    } else {
      console.error('Error lain:', error)
    }
  }
}

// Ekspor fungsi untuk penggunaan dalam lingkungan browser
window.testLogin = testLogin