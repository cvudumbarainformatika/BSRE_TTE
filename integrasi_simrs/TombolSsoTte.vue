<template>
  <!-- Tombol Aksi Membuka Aplikasi TTE BSrE dari SIMRS -->
  <div class="inline-block">
    <button
      type="button"
      @click="handleOpenTte"
      class="inline-flex items-center gap-2 px-3.5 py-2 text-sm font-medium text-white bg-teal-600 hover:bg-teal-700 rounded-lg shadow-sm transition-all focus:outline-none focus:ring-2 focus:ring-teal-500 focus:ring-offset-1"
    >
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      <span>{{ label }}</span>
    </button>
  </div>
</template>

<script setup>
/**
 * Komponen Tombol SSO TTE BSrE untuk SIMRS
 * 
 * Props:
 * - nip: NIP dokter / pegawai yang sedang login di SIMRS (Wajib)
 * - mode: 'redirect' | 'deeplink' | 'popup' (Default: 'redirect')
 * - tteBackendUrl: URL Microservice Backend TTE (Default: 'http://localhost:8005/api/v1')
 * - tteFrontendUrl: URL Frontend TTE (Default: 'http://localhost:3000')
 */
const props = defineProps({
  nip: {
    type: String,
    required: true
  },
  label: {
    type: String,
    default: 'Buka E-DOC TTE BSrE'
  },
  mode: {
    type: String,
    default: 'redirect' // 'redirect' atau 'deeplink' atau 'popup'
  },
  tteBackendUrl: {
    type: String,
    default: 'http://192.168.150.114:8005/api/v1'
  },
  tteFrontendUrl: {
    type: String,
    default: 'http://192.168.150.114'
  }
})

const handleOpenTte = () => {
  if (!props.nip) {
    alert('NIP Pegawai tidak ditemukan untuk otorisasi SSO')
    return
  }

  if (props.mode === 'redirect') {
    // Mode 1: 1-Klik Redirect Backend (Membuat token JWT resmi lalu redirect ke frontend)
    const url = `${props.tteBackendUrl}/auth/sso/redirect?nip=${encodeURIComponent(props.nip)}`
    window.open(url, '_blank')
  } else if (props.mode === 'deeplink') {
    // Mode 2: Direct Frontend Hash Deeplink
    const url = `${props.tteFrontendUrl}/#/?nip=${encodeURIComponent(props.nip)}`
    window.open(url, '_blank')
  } else if (props.mode === 'popup') {
    // Mode 3: Popup Window ukuran khusus
    const url = `${props.tteBackendUrl}/auth/sso/redirect?nip=${encodeURIComponent(props.nip)}`
    const w = 1200
    const h = 800
    const left = (window.screen.width - w) / 2
    const top = (window.screen.height - h) / 2
    window.open(url, 'TTE_BSRE_WINDOW', `width=${w},height=${h},top=${top},left=${left},resizable=yes,scrollbars=yes`)
  }
}
</script>
