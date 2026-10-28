<template>
  <header class="sticky top-0 z-30 h-16 bg-background border-b border-border backdrop-blur-sm bg-background/95">
    <div class="h-full px-4 flex items-center justify-between gap-4">
      <!-- Left: Menu button + Breadcrumbs -->
      <div class="flex items-center space-x-4 flex-1">
        <SidebarTrigger class="-ml-2" />

        <!-- Breadcrumbs -->
        <nav class="hidden md:flex items-center space-x-2 text-sm">
          <Home class="w-4 h-4 text-muted-foreground" />
          <template v-if="currentRouteName">
            <ChevronRight class="w-4 h-4 text-muted-foreground" />
            <span class="font-medium">{{ currentRouteName?.toUpperCase() }}</span>
          </template>
        </nav>
      </div>

      <!-- Center: Search Bar -->
      <!-- <div class="hidden lg:flex flex-1 max-w-md">
        <div class="relative w-full">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            type="search"
            placeholder="Search... (Ctrl+K)"
            class="pl-10 pr-4 w-full"
          />
        </div>
      </div> -->

      <!-- Right: Actions -->
      <div class="flex items-center space-x-2">
        <!-- Search Button (Mobile) -->
        <Button
          variant="ghost"
          size="icon"
          class="lg:hidden"
          aria-label="Search"
        >
          <Search class="h-5 w-5" />
        </Button>

        <!-- Notifications -->
        <div class="relative">
          <!-- <Button
            variant="ghost"
            size="icon"
            @click="showNotifications = !showNotifications"
            aria-label="Notifications"
          >
            <Bell class="h-5 w-5" />
            <span class="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
          </Button> -->

          <!-- Notifications Dropdown -->
          <transition name="dropdown">
            <div
              v-if="showNotifications"
              v-click-outside="() => showNotifications = false"
              class="absolute right-0 mt-2 w-80 bg-background border border-border rounded-lg shadow-lg overflow-hidden"
            >
              <div class="p-4 border-b border-border">
                <h3 class="font-semibold">Notifications</h3>
                <p class="text-xs text-muted-foreground">You have 3 unread messages</p>
              </div>
              <div class="max-h-96 overflow-y-auto">
                <div
                  v-for="notif in notifications"
                  :key="notif.id"
                  class="p-4 border-b border-border hover:bg-accent/50 cursor-pointer transition-colors"
                >
                  <div class="flex items-start space-x-3">
                    <div :class="['p-2 rounded-lg', notif.color]">
                      <component :is="notif.icon" class="w-4 h-4" />
                    </div>
                    <div class="flex-1 min-w-0">
                      <p class="text-sm font-medium">{{ notif.title }}</p>
                      <p class="text-xs text-muted-foreground">{{ notif.message }}</p>
                      <p class="text-xs text-muted-foreground mt-1">{{ notif.time }}</p>
                    </div>
                  </div>
                </div>
              </div>
              <div class="p-3 border-t border-border">
                <Button variant="ghost" size="sm" class="w-full">
                  View all notifications
                </Button>
              </div>
            </div>
          </transition>
        </div>

        <!-- Countdown Timer (Header compact) -->
        <CountdownTimer variant="header" />


        <!-- User Menu -->
        <div class="relative">
          <button
            @click="showUserMenu = !showUserMenu"
            class="flex items-center space-x-3 p-1.5 rounded-lg hover:bg-accent transition-colors"
          >
            <div class="flex items-center space-x-2">
              
              <div class="hidden md:block text-right -space-y-1">
                <p class="text-sm font-medium">{{ authStore?.user?.name }}</p>
                <p class="text-xs text-muted-foreground">{{ authStore?.user?.role }}</p>
              </div>
              <div class="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                <span class="text-white text-sm font-semibold">JD</span>
              </div>
            </div>
            <!-- <ChevronDown class="w-4 h-4 text-muted-foreground hidden md:block" /> -->
          </button>

          <!-- User Dropdown -->
          <transition name="dropdown">
            <div
              v-if="showUserMenu"
              v-click-outside="() => showUserMenu = false"
              class="absolute right-0 mt-2 w-56 bg-background border border-border rounded-lg shadow-lg overflow-hidden"
            >
              <div class="p-3 border-b border-border">
                <p class="text-sm font-medium">{{ authStore?.user?.name }}</p>
                <p class="text-xs text-muted-foreground">{{ authStore?.user?.role }}</p>
              </div>
              <div class="p-2">
                <button
                  v-for="item in userMenuItems"
                  :key="item.label"
                  @click="handleUserMenuClick(item.action)"
                  class="w-full flex items-center space-x-3 px-3 py-2 rounded-md hover:bg-accent transition-colors text-left"
                >
                  <component :is="item.icon" class="w-4 h-4" />
                  <span class="text-sm">{{ item.label }}</span>
                </button>
              </div>
              <div class="p-2 border-t border-border">
                <button
                  @click="handleLogout"
                  class="w-full flex items-center space-x-3 px-3 py-2 rounded-md hover:bg-destructive/10 text-destructive transition-colors text-left"
                >
                  <LogOut class="w-4 h-4" />
                  <span class="text-sm">Logout</span>
                </button>
              </div>
            </div>
          </transition>
        </div>

        <!-- Dark Mode Toggle (Absolute Right - FORCED VISIBILITY) -->
        <button
          @click="toggleDarkMode"
          class="flex items-center gap-2 px-3 py-1.5 bg-slate-800 hover:bg-slate-900 text-white rounded-full shadow-lg transition-all z-50 ml-4 border-2 border-white/20"
        >
          <div class="flex items-center justify-center p-1 bg-white/20 rounded-full">
            <Sun v-if="isDark" class="h-3 w-3 text-yellow-400" />
            <Moon v-else class="h-3 w-3 text-blue-200" />
          </div>
          <span class="text-[10px] font-bold uppercase tracking-tight">{{ isDark ? 'Siang' : 'Malam' }}</span>
        </button>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth' // Import store autentikasi
import { Input } from '@/components/ui/input'

import { Button } from '@/components/ui/button'
import { SidebarTrigger } from '@/components/ui/sidebar'
import {
  Sun,
  Moon,
  Bell,
  Search,
  Home,
  ChevronRight,
  ChevronDown,
  User,
  Settings,
  HelpCircle,
  LogOut,
  UserCircle,
  CreditCard,
  Mail,
  MessageSquare,
  AlertCircle
} from 'lucide-vue-next'
import CountdownTimer from '@/components/CountdownTimer.vue'

defineEmits(['toggle-sidebar'])

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore() // Gunakan store autentikasi
const isDark = ref(false)
const showNotifications = ref(false)
const showUserMenu = ref(false)

// Route name mapping for breadcrumbs
const routeNames = {
  'dashboard': 'Dashboard',
  'data-table': 'Data Table',
  'forms': 'Forms',
  'full-shadcn': 'Components',
  'login': 'Login',
  'users': 'Users',
  'analytics': 'Analytics',
  'settings': 'Settings'
}

const currentRouteName = computed(() => {
  return routeNames[route.name] || route.name || 'Home'
})

const notifications = [
  {
    id: 1,
    icon: Mail,
    title: 'New message',
    message: 'You have a new message from Sarah',
    time: '5 minutes ago',
    color: 'bg-blue-500/10 text-blue-500'
  },
  {
    id: 2,
    icon: MessageSquare,
    title: 'New comment',
    message: 'John commented on your post',
    time: '1 hour ago',
    color: 'bg-green-500/10 text-green-500'
  },
  {
    id: 3,
    icon: AlertCircle,
    title: 'System update',
    message: 'System will be updated tonight',
    time: '2 hours ago',
    color: 'bg-orange-500/10 text-orange-500'
  }
]

const userMenuItems = [
  { icon: UserCircle, label: 'Profil Saya', action: 'profile' }
]

// Check initial dark mode state - set light mode as default
onMounted(() => {
  const savedTheme = localStorage.getItem('theme')

  // Jika tidak ada tema yang disimpan, gunakan light sebagai default
  isDark.value = savedTheme === 'dark'

  if (isDark.value) {
    document.documentElement.classList.add('dark')
  }
})

function toggleDarkMode() {
  isDark.value = !isDark.value

  if (isDark.value) {
    document.documentElement.classList.add('dark')
    localStorage.setItem('theme', 'dark')
  } else {
    document.documentElement.classList.remove('dark')
    localStorage.setItem('theme', 'light')
  }
}

function handleUserMenuClick(action) {
  showUserMenu.value = false
  if (action === 'profile') {
    router.push('/profile')
  }
}

function handleLogout() {
  showUserMenu.value = false
  authStore.logout() // Gunakan fungsi logout dari store
  // Redirect ke halaman login
  window.location.href = '/login'
}
</script>

<style scoped>
.mode-switch-enter-active,
.mode-switch-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.mode-switch-enter-from {
  opacity: 0;
  transform: rotate(-90deg) scale(0);
}

.mode-switch-leave-to {
  opacity: 0;
  transform: rotate(90deg) scale(0);
}

.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.2s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
