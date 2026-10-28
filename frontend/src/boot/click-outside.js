import { boot } from 'quasar/wrappers'

// Directive untuk mendeteksi klik di luar elemen
const clickOutside = {
  mounted(el, binding) {
    // Tambahkan event listener ke dokumen untuk menangani klik di luar elemen
    el.clickOutsideEvent = function(event) {
      // Periksa apakah elemen target klik adalah tombol yang membuka dropdown
      // atau elemen dropdown itu sendiri
      if (!(el === event.target || el.contains(event.target))) {
        // Panggil fungsi yang dilewatkan sebagai argumen
        binding.value(event)
      }
    }

    // Gunakan setTimeout untuk mencegah masalah dengan event yang terjadi secara bersamaan
    setTimeout(() => {
      document.addEventListener('click', el.clickOutsideEvent)
    }, 0)
  },
  unmounted(el) {
    // Hapus event listener saat komponen di-unmount
    document.removeEventListener('click', el.clickOutsideEvent)
  }
}

export default boot(({ app }) => {
  app.directive('click-outside', clickOutside)
})