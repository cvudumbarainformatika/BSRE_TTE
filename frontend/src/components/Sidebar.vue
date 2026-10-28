<template>
  <aside 
    :class="[
      'fixed inset-y-0 left-0 z-50 h-screen flex flex-col bg-background border-r border-border transition-all duration-300 ease-in-out',
      isOpen ? 'translate-x-0' : '-translate-x-full',
      'lg:translate-x-0',
      isMini ? 'lg:w-20' : 'lg:w-64',
      isMini ? 'w-20' : 'w-64'
    ]"
  >
    <!-- Sidebar Header -->
    <div class="h-16 flex items-center justify-between px-4 border-b border-border">
      <transition name="fade" mode="out-in">
        <div v-if="!isMini" class="flex items-center space-x-2">
          <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
            <span class="text-white font-bold text-sm">QS</span>
          </div>
          <span class="font-semibold">Admin</span>
        </div>
        <div v-else class="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center mx-auto">
          <span class="text-white font-bold text-sm">QS</span>
        </div>
      </transition>
      
      <button
        v-if="!isMini"
        @click="$emit('close')"
        class="lg:hidden p-2 rounded-md hover:bg-accent"
        aria-label="Close sidebar"
      >
        <X class="w-5 h-5" />
      </button>
    </div>

    <!-- Toggle Mini Button (Desktop only) -->
    <div class="hidden lg:flex justify-end px-2 py-2 border-b border-border">
      <button
        @click="$emit('toggle-mini')"
        class="p-2 rounded-md hover:bg-accent transition-colors"
        :aria-label="isMini ? 'Expand sidebar' : 'Collapse sidebar'"
      >
        <ChevronLeft v-if="!isMini" class="w-4 h-4" />
        <ChevronRight v-else class="w-4 h-4" />
      </button>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 p-2 space-y-1 overflow-y-auto">
      <div v-if="!isMini" class="px-3 py-2">
        <h3 class="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
          Main Menu
        </h3>
      </div>

      <router-link
        v-for="link in navigationLinks"
        :key="link.path"
        :to="link.path"
        @click="$emit('navigate')"
        :class="[
          'flex items-center rounded-lg text-sm font-medium transition-all',
          'hover:bg-accent hover:text-accent-foreground',
          isMini ? 'justify-center p-3' : 'space-x-3 px-3 py-2.5'
        ]"
        active-class="bg-accent text-accent-foreground"
        :title="isMini ? link.label : ''"
      >
        <component :is="link.icon" :class="isMini ? 'w-5 h-5' : 'w-5 h-5'" />
        <span v-if="!isMini">{{ link.label }}</span>
        <span 
          v-if="link.badge && !isMini" 
          class="ml-auto px-2 py-0.5 text-xs rounded-full bg-primary text-primary-foreground"
        >
          {{ link.badge }}
        </span>
      </router-link>

      <!-- Divider -->
      <div class="py-2">
        <div class="border-t border-border"></div>
      </div>

      <div v-if="!isMini" class="px-3 py-2">
        <h3 class="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
          Settings
        </h3>
      </div>

      <router-link
        v-for="link in settingsLinks"
        :key="link.path"
        :to="link.path"
        @click="$emit('navigate')"
        :class="[
          'flex items-center rounded-lg text-sm font-medium transition-all',
          'hover:bg-accent hover:text-accent-foreground',
          isMini ? 'justify-center p-3' : 'space-x-3 px-3 py-2.5'
        ]"
        active-class="bg-accent text-accent-foreground"
        :title="isMini ? link.label : ''"
      >
        <component :is="link.icon" :class="isMini ? 'w-5 h-5' : 'w-5 h-5'" />
        <span v-if="!isMini">{{ link.label }}</span>
      </router-link>
    </nav>

    <!-- Countdown Timer -->
    <div v-if="!isMini" class="shrink-0 px-4 py-3 border-t border-border">
      <CountdownTimer variant="sidebar" />
    </div>

    <!-- Footer Info -->
    <div class="shrink-0 p-4 border-t border-border bg-background">
      <transition name="fade" mode="out-in">
        <div v-if="!isMini" class="text-xs text-muted-foreground">
          <p class="font-semibold mb-1">Quasar ShadCN</p>
          <p>v1.0.0</p>
        </div>
        <div v-else class="flex justify-center">
          <div class="w-2 h-2 rounded-full bg-green-500"></div>
        </div>
      </transition>
    </div>
  </aside>

  <!-- Overlay for mobile -->
  <div
    v-if="isOpen"
    @click="$emit('close')"
    class="fixed inset-0 bg-black/50 z-40 lg:hidden"
  />
</template>

<script setup>
import { 
  LayoutDashboard, 
  Blocks, 
  FileText, 
  Sparkles,
  Settings,
  Users,
  BarChart3,
  ChevronLeft,
  ChevronRight,
  X
} from 'lucide-vue-next'
import CountdownTimer from '@/components/CountdownTimer.vue'

defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  isMini: {
    type: Boolean,
    default: false
  }
})

defineEmits(['close', 'navigate', 'toggle-mini'])

const navigationLinks = [
  {
    path: '/',
    label: 'Dashboard',
    icon: LayoutDashboard
  },
  {
    path: '/components',
    label: 'Components',
    icon: Blocks
  },
  {
    path: '/forms',
    label: 'Forms',
    icon: FileText
  },
  {
    path: '/full-shadcn',
    label: 'Full ShadCN',
    icon: Sparkles,
    badge: 'New'
  }
]

const settingsLinks = [
  {
    path: '/users',
    label: 'Users',
    icon: Users
  },
  {
    path: '/analytics',
    label: 'Analytics',
    icon: BarChart3
  },
  {
    path: '/settings',
    label: 'Settings',
    icon: Settings
  }
]
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
