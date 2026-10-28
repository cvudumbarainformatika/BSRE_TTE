<template>
  <AlertDialog :open="appLoadingStore.isLoading">
    <AlertDialogContent
      class="sm:max-w-md app-loading-dialog-content bg-transparent border-0 shadow-none"
      @interact-outside="(event) => event.preventDefault()"
    >
      <AlertDialogHeader class="flex flex-col items-center justify-center text-white mb-4">
        <AlertDialogTitle class="text-xl font-semibold tracking-wider text-center">
          PROCESSING
        </AlertDialogTitle>
        <AlertDialogDescription class="text-sm text-white/70 text-center">
          {{ appLoadingStore.loadingMessage }}
        </AlertDialogDescription>
      </AlertDialogHeader>
      
      <div class="flex flex-col items-center justify-center text-white">
        <!-- Animated Bars -->
        <div class="flex items-center justify-center space-x-2 h-16">
          <div class="loading-bar"></div>
          <div class="loading-bar"></div>
          <div class="loading-bar"></div>
          <div class="loading-bar"></div>
        </div>
      </div>
    </AlertDialogContent>
  </AlertDialog>
</template>

<script setup>
import {
  AlertDialog,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import { useAppLoadingStore } from '@/stores/appLoading'

const appLoadingStore = useAppLoadingStore()
</script>

<style scoped>
/* Remove default close button from shadcn's AlertDialogContent (if any, targeting the class as before) */
/* AlertDialogContent doesn't usually have a close button by default, but keeping this for robustness */
.app-loading-dialog-content :deep(button[aria-label="Close"]) {
  display: none !important;
}

.loading-bar {
  width: 8px;
  height: 32px;
  background-color: theme('colors.primary.DEFAULT');
  border-radius: 4px;
  animation: pulse 1.2s infinite ease-in-out;
  box-shadow: 0 0 10px theme('colors.primary.DEFAULT'), 0 0 20px theme('colors.primary.DEFAULT / 70%');
}

.loading-bar:nth-child(2) {
  animation-delay: 0.1s;
}

.loading-bar:nth-child(3) {
  animation-delay: 0.2s;
}

.loading-bar:nth-child(4) {
  animation-delay: 0.3s;
}

@keyframes pulse {
  0%, 80%, 100% {
    transform: scaleY(0.5);
    opacity: 0.7;
  }
  40% {
    transform: scaleY(1.0);
    opacity: 1;
  }
}
</style>
