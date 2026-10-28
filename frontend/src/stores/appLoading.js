import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppLoadingStore = defineStore('appLoading', () => {
  const isLoading = ref(true)
  const loadingMessage = ref('Memuat...')

  function startLoading(message = 'Memuat...') {
    isLoading.value = true
    loadingMessage.value = message
  }

  function stopLoading() {
    isLoading.value = false
    loadingMessage.value = 'Memuat...' // Reset pesan ke default
  }

  function setLoadingMessage(message) {
    loadingMessage.value = message
  }

  return {
    isLoading,
    loadingMessage,
    startLoading,
    stopLoading,
    setLoadingMessage,
  }
})
