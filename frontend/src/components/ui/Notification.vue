<template>
  <Teleport to="body">
    <div
      class="fixed top-4 right-4 z-[1000] flex flex-col items-end gap-2 w-full max-w-sm"
      :class="positionClass"
    >
      <TransitionGroup
        name="notification"
        tag="div"
        class="flex flex-col gap-2"
      >
        <div
          v-for="notification in notifications"
          :key="notification.id"
          :class="[
            'flex w-full max-w-sm items-start gap-3 rounded-lg border p-4 shadow-lg transition-all',
            'data-[state=closed]:animate-out data-[state=open]:animate-in',
            'data-[state=open]:fade-in data-[state=closed]:fade-out',
            'data-[state=open]:slide-in-from-top-full data-[state=open]:sm:slide-in-from-top-full',
            'border-border bg-background text-foreground',
            notification.variant === 'destructive' && 'bg-red-50 border-red-200 text-red-700',
            notification.variant === 'success' && 'bg-green-50 border-green-200 text-green-700',
            notification.variant === 'warning' && 'bg-amber-50 border-amber-200 text-amber-700',
            notification.variant === 'info' && 'bg-blue-50 border-blue-200 text-blue-700',
          ]"
          role="alert"
          data-state="open"
        >
          <div class="flex-1">
            <div class="flex items-center gap-1.5">
              <span class="font-medium text-sm">{{ notification.title }}</span>
              <div v-if="notification.variant === 'destructive'" class="ml-2">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <circle cx="12" cy="12" r="10"></circle>
                  <line x1="15" y1="9" x2="9" y2="15"></line>
                  <line x1="9" y1="9" x2="15" y2="15"></line>
                </svg>
              </div>
              <div v-else-if="notification.variant === 'success'" class="ml-2">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <circle cx="12" cy="12" r="10"></circle>
                  <path d="M5 12l5 5l10 -10"></path>
                </svg>
              </div>
              <div v-else-if="notification.variant === 'warning'" class="ml-2">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M12 9v2m0 4v.01"></path>
                  <path d="M5 19h14a2 2 0 0 0 1.84 -2.75l-7.1 -12.25a2 2 0 0 0 -3.5 0l-7.1 12.25a2 2 0 0 0 1.75 2.75"></path>
                </svg>
              </div>
              <div v-else-if="notification.variant === 'info'" class="ml-2">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <circle cx="12" cy="12" r="10"></circle>
                  <path d="M12 16v-4m0 -4v.01"></path>
                </svg>
              </div>
            </div>
            <p v-if="notification.description" class="mt-1.5 text-sm opacity-80">
              {{ notification.description }}
            </p>
          </div>
          <button
            @click="removeNotification(notification.id)"
            class="opacity-70 hover:opacity-100 rounded-md transition-opacity focus:outline-none focus:ring-1 focus:ring-ring"
            :aria-label="`Tutup notifikasi ${notification.title}`"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup>
import { computed } from 'vue'
import { useNotificationStore } from '@/stores/notification'

const notificationStore = useNotificationStore()

const notifications = computed(() => notificationStore.notifications)

const positionClass = computed(() => {
  // Menggunakan posisi default di kanan atas
  return 'top-4 right-4'
})

const removeNotification = (id) => {
  notificationStore.removeNotification(id)
}
</script>

<style scoped>
.notification-enter-active,
.notification-leave-active {
  transition: all 0.3s ease;
}
.notification-enter-from,
.notification-leave-to {
  opacity: 0;
  transform: translateX(100%);
}
</style>