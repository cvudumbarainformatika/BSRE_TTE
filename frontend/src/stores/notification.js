import { defineStore } from 'pinia'

// Generate ID unik untuk setiap notifikasi
function generateId() {
  return Math.random().toString(36).substr(2, 9)
}

export const useNotificationStore = defineStore('notification', {
  state: () => ({
    notifications: []
  }),

  actions: {
    // Tambah notifikasi
    addNotification(notification) {
      const newNotification = {
        id: generateId(),
        title: notification.title || 'Pemberitahuan',
        description: notification.description || '',
        variant: notification.variant || 'default', // 'default', 'destructive', 'success', 'warning', 'info'
        duration: notification.duration || 5000 // dalam milidetik, 0 untuk tidak otomatis hilang
      }

      this.notifications.push(newNotification)

      // Hapus notifikasi otomatis setelah durasi
      if (newNotification.duration > 0) {
        setTimeout(() => {
          this.removeNotification(newNotification.id)
        }, newNotification.duration)
      }
    },

    // Hapus notifikasi berdasarkan ID
    removeNotification(id) {
      this.notifications = this.notifications.filter(notification => notification.id !== id)
    },

    // Hapus semua notifikasi
    clearAllNotifications() {
      this.notifications = []
    },

    // Shortcut methods untuk berbagai jenis notifikasi
    showSuccess(title, description) {
      this.addNotification({
        title,
        description,
        variant: 'success'
      })
    },

    showError(title, description) {
      this.addNotification({
        title,
        description,
        variant: 'destructive'
      })
    },

    showWarning(title, description) {
      this.addNotification({
        title,
        description,
        variant: 'warning'
      })
    },

    showInfo(title, description) {
      this.addNotification({
        title,
        description,
        variant: 'info'
      })
    }
  }
})