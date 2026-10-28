# Catatan Tugas - Frontend Juwita

## Tugas Selesai

### 1. Meningkatkan Kontras dalam Mode Light (6 Desember 2025)
- **Deskripsi**: Mengubah konfigurasi warna dalam mode light agar background, card, dan sidebar memiliki perbedaan kontras yang lebih jelas
- **Perubahan yang dilakukan**:
  - Mengubah warna background utama dari `0 0% 100%` (putih murni) menjadi `0 0% 98%` (sedikit lebih gelap dari putih murni)
  - Mengatur warna card dan popover tetap putih (`0 0% 100%`) untuk kontras maksimum dengan background
  - Menyesuaikan warna sidebar menjadi `0 0% 96%` (lebih gelap dari background utama)
  - Memperhalus warna border, secondary, muted, dan accent agar lebih kontras
- **File yang diubah**: `/src/css/tailwind.css`
- **Hasil**: Sekarang mode light memiliki kontras yang lebih baik antar elemen, sementara mode dark tetap seperti sebelumnya karena Anda menyukai tampilannya

### 2. Mengatur Mode Light sebagai Default (6 Desember 2025)
- **Deskripsi**: Mengubah logika tema agar mode light menjadi default, bukan mode dark
- **Perubahan yang dilakukan**:
  - Memperbarui fungsi `onMounted` di komponen Header.vue untuk mengabaikan preferensi sistem pengguna untuk mode gelap
  - Mengatur mode light sebagai default kecuali pengguna secara eksplisit memilih mode gelap sebelumnya
  - Menambahkan komentar dalam bahasa Indonesia di kode
- **File yang diubah**: `/src/components/Header.vue`
- **Hasil**: Sekarang aplikasi akan selalu dimulai dalam mode light kecuali pengguna sebelumnya memilih mode dark dan menyimpan preferensi tersebut

### 3. Implementasi Sistem Otentikasi dan Redirect Otomatis (6 Desember 2025)
- **Deskripsi**: Membuat sistem otentikasi sederhana dan mengimplementasikan redirect otomatis berdasarkan status login pengguna
- **Perubahan yang dilakukan**:
  - Membuat store autentikasi menggunakan Pinia untuk menyimpan status login
  - Menambahkan guard otentikasi global di router untuk menangani redirect
  - Memperbarui semua route utama untuk memerlukan otentikasi
  - Memperbarui komponen LoginPage.vue untuk menggunakan store autentikasi
  - Memperbarui komponen Header.vue untuk menggunakan fungsi logout dari store
  - Menambahkan komentar dalam bahasa Indonesia di kode
- **File yang diubah**:
  - `/src/stores/auth.js` (baru)
  - `/src/router/index.js`
  - `/src/router/routes.js`
  - `/src/pages/LoginPage.vue`
  - `/src/components/Header.vue`
- **Hasil**: Sekarang aplikasi akan:
  - Mengarahkan pengguna yang belum login ke halaman `/auth/login`
  - Mencegah pengguna yang sudah login untuk mengakses halaman `/auth`
  - Menggunakan sistem otentikasi sederhana berbasis store dan localStorage

### 4. Perbaikan Error Pinia di Router (6 Desember 2025)
- **Deskripsi**: Memperbaiki error "getActivePinia() was called but there was no active Pinia" yang terjadi ketika menggunakan store di router
- **Perubahan yang dilakukan**:
  - Mengganti penggunaan store auth langsung di router index.js dengan akses localStorage
  - Menyesuaikan komponen LoginPage.vue untuk menggunakan localStorage langsung
  - Menyesuaikan komponen Header.vue untuk menggunakan localStorage saat logout
  - Menambahkan komentar dalam bahasa Indonesia di kode
- **File yang diubah**:
  - `/src/router/index.js`
  - `/src/pages/LoginPage.vue`
  - `/src/components/Header.vue`
- **Hasil**: Error Pinia telah teratasi dan sistem otentikasi tetap berfungsi dengan menggunakan localStorage sebagai alternatif

### 5. Implementasi Store Pinia dengan Struktur State/Actions/Getters dan Persist (6 Desember 2025)
- **Deskripsi**: Mengubah struktur store auth ke format state/actions/getters dan menambahkan persist untuk menyimpan data secara otomatis
- **Perubahan yang dilakukan**:
  - Mengganti struktur store dari function-based ke object-based (state, actions, getters)
  - Menginstal plugin `pinia-plugin-persistedstate` untuk menyimpan state di localStorage
  - Mengkonfigurasi Pinia di main.js untuk menggunakan plugin persist
  - Mengembalikan penggunaan store auth di router, LoginPage, dan Header
  - Menambahkan komentar dalam bahasa Indonesia di kode
- **File yang diubah**:
  - `/src/stores/auth.js`
  - `/src/main.js`
  - `/src/router/index.js`
  - `/src/pages/LoginPage.vue`
  - `/src/components/Header.vue`
- **Hasil**: Sekarang sistem otentikasi menggunakan struktur Pinia yang lebih lengkap dan data login otomatis tersimpan/persisten tanpa perlu mengelola localStorage secara manual

### 6. Penyesuaian Konfigurasi Pinia sesuai Panduan Quasar (6 Desember 2025)
- **Deskripsi**: Mengikuti panduan resmi Quasar untuk mengkonfigurasi Pinia dengan benar menggunakan boot file
- **Perubahan yang dilakukan**:
  - Membuat boot file baru `/src/boot/pinia.js` untuk menginisialisasi Pinia dengan plugin persist
  - Mengembalikan file main.js ke konfigurasi standar tanpa konfigurasi Pinia
  - Mengupdate quasar.config.js untuk menambahkan boot file pinia ke dalam daftar boot files
  - Menambahkan komentar dalam bahasa Indonesia di kode
- **File yang diubah**:
  - `/src/boot/pinia.js` (baru)
  - `/src/main.js`
  - `/quasar.config.js`
- **Hasil**: Sekarang sistem otentikasi mengikuti panduan resmi Quasar Framework dan menggunakan konfigurasi boot file yang benar

### 7. Perluasan State dan Getter pada Store Auth (6 Desember 2025)
- **Deskripsi**: Memperluas state store auth untuk menyimpan informasi dari response backend dan menghapus penggunaan localStorage manual
- **Perubahan yang dilakukan**:
  - Menambahkan field-field baru ke state: user, accessToken, refreshToken, tokenType
  - Menghapus penggunaan localStorage.setItem/removeItem karena sudah menggunakan persist
  - Memperbarui getter untuk mengakses informasi user, access token, dan refresh token
  - Memperbarui fungsi login untuk menyimpan data dari response backend ke state
  - Memperbarui konfigurasi persist untuk menyimpan semua informasi penting
  - Menambahkan komentar dalam bahasa Indonesia di kode
- **File yang diubah**:
  - `/src/stores/auth.js`
- **Hasil**: Store auth sekarang dapat menyimpan informasi lengkap dari response backend dan semua data otentikasi tersimpan secara persisten

### 8. Implementasi Login API ke Backend Go (6 Desember 2025)
- **Deskripsi**: Menghubungkan sistem login ke backend Go API dan memperbarui validasi form agar tidak memvalidasi format email
- **Perubahan yang dilakukan**:
  - Memperbarui store auth untuk menggunakan axios API ke backend Go
  - Mengganti baseURL axios ke http://localhost:8080/api/v1
  - Memperbarui LoginPage untuk tidak memvalidasi format email (karena hanya nama bukan email sungguhan)
  - Mengganti type input email dari "email" menjadi "text" dan placeholder dari email ke username
  - Menyesuaikan skema validasi hanya untuk memastikan email tidak kosong
  - Menambahkan komentar dalam bahasa Indonesia di kode
- **File yang diubah**:
  - `/src/stores/auth.js`
  - `/src/boot/axios.js`
  - `/src/pages/LoginPage.vue`
- **Hasil**: Login sekarang terhubung ke backend Go API dan form hanya memvalidasi bahwa email tidak kosong, bukan format email

### 9. Konfigurasi Axios Profesional dengan Environment Variable dan Interceptor (6 Desember 2025)
- **Deskripsi**: Memperbarui konfigurasi axios dengan environment variable dan interceptor untuk otomatisasi token dan penanganan error
- **Perubahan yang dilakukan**:
  - Mengganti baseURL dengan environment variable VITE_API_BASE_URL
  - Menambahkan request interceptor untuk otomatisasi Bearer token
  - Menambahkan response interceptor untuk menangani error otentikasi (status 401)
  - Menambahkan penanganan error jaringan
  - Memperbarui file .env.example dengan URL backend default
  - Menambahkan timeout 10 detik pada konfigurasi axios
  - Menambahkan komentar dalam bahasa Indonesia di kode
- **File yang diubah**:
  - `/src/boot/axios.js`
  - `/src/.env.example`
- **Hasil**: Axios sekarang menggunakan environment variable dan otomatis menangani token, error otentikasi, serta error jaringan

### 10. Penanganan Error Jaringan Lebih Lengkap (6 Desember 2025)
- **Deskripsi**: Menambahkan informasi dan notifikasi lebih lengkap untuk error jaringan
- **Perubahan yang dilakukan**:
  - Memperbarui interceptor axios untuk menangani error jaringan dengan pesan yang lebih informatif
  - Menambahkan notifikasi untuk pengguna saat terjadi error jaringan
  - Menambahkan informasi lebih detail tentang request yang gagal
  - Menambahkan komentar dalam bahasa Indonesia di kode
- **File yang diubah**:
  - `/src/boot/axios.js`
- **Hasil**: Sekarang aplikasi memberikan informasi lebih jelas saat terjadi error jaringan dan memberikan notifikasi kepada pengguna