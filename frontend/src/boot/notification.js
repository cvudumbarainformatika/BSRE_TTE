import { boot } from 'quasar/wrappers'
import { useNotificationStore } from '@/stores/notification'

// Plugin untuk menyediakan fungsi notifikasi global ke komponen Vue
export default boot(({ app }) => {
  // Tambahkan metode global untuk menampilkan notifikasi
  app.config.globalProperties.$notify = {
    success: (title, description) => {
      const notificationStore = useNotificationStore()
      notificationStore.showSuccess(title, description)
    },
    error: (title, description) => {
      const notificationStore = useNotificationStore()
      notificationStore.showError(title, description)
    },
    warning: (title, description) => {
      const notificationStore = useNotificationStore()
      notificationStore.showWarning(title, description)
    },
    info: (title, description) => {
      const notificationStore = useNotificationStore()
      notificationStore.showInfo(title, description)
    },
    custom: (notification) => {
      const notificationStore = useNotificationStore()
      notificationStore.addNotification(notification)
    }
  }

  // Juga tambahkan sebagai metode komponen
  app.provide('$notify', app.config.globalProperties.$notify)
})