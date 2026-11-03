<template>
  <!-- Komponen Modal / Dialog iFrame Tersemat untuk SIMRS Quasar / Vue -->
  <div v-if="modelValue" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
    <div class="relative w-full max-w-6xl h-[88vh] bg-white rounded-2xl shadow-2xl overflow-hidden flex flex-col border border-gray-200">
      
      <!-- Header Dialog -->
      <div class="flex items-center justify-between px-6 py-3.5 bg-gray-50 border-b border-gray-200">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded-lg bg-teal-600 flex items-center justify-center text-white font-bold text-sm">
            TTE
          </div>
          <div>
            <h3 class="text-sm font-semibold text-gray-800">Sistem Tanda Tangan Elektronik BSrE</h3>
            <p class="text-xs text-gray-500">Terhubung secara aman via SIMRS Single Sign-On</p>
          </div>
        </div>

        <button
          type="button"
          @click="closeDialog"
          class="p-1.5 text-gray-400 hover:text-gray-700 hover:bg-gray-200 rounded-lg transition-colors"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- iFrame Viewer Aplikasi TTE -->
      <div class="flex-1 w-full h-full relative bg-gray-100">
        <iframe
          ref="iframeRef"
          :src="iframeUrl"
          class="w-full h-full border-none"
          @load="onIframeLoaded"
        ></iframe>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  nip: {
    type: String,
    required: true
  },
  tteFrontendUrl: {
    type: String,
    default: 'http://192.168.150.114'
  }
})

const emit = defineEmits(['update:modelValue', 'close'])

const iframeRef = ref(null)

const iframeUrl = computed(() => {
  return `${props.tteFrontendUrl}/#/`
})

const onIframeLoaded = () => {
  // Kirimkan identitas SSO lewat postMessage begitu iframe selesai dimuat
  if (iframeRef.value && iframeRef.value.contentWindow) {
    iframeRef.value.contentWindow.postMessage({
      type: 'SIMRS_SSO_AUTH',
      nip: props.nip
    }, '*')
  }
}

const closeDialog = () => {
  emit('update:modelValue', false)
  emit('close')
}
</script>
