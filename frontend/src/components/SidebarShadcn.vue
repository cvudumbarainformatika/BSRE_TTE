<template>
  <Sidebar collapsible="icon">
    <SidebarHeader>
      <SidebarMenu>
        <SidebarMenuItem>
          <SidebarMenuButton size="lg" as-child>
            <a href="#">
              <div class="flex aspect-square size-8 items-center justify-center rounded-lg bg-gradient-to-br from-primary to-primary/50 text-sidebar-primary-foreground">
                <span class="font-bold">JM</span>
              </div>
              <div class="grid flex-1 text-left text-sm leading-tight">
                <span class="truncate font-semibold">SI JUWITA MALAM</span>
                <span class="truncate text-xs">Admin Dashboard</span>
              </div>
            </a>
          </SidebarMenuButton>
        </SidebarMenuItem>
      </SidebarMenu>
    </SidebarHeader>

    <SidebarContent>
      <SidebarGroup>
        <SidebarGroupLabel>Main Menu</SidebarGroupLabel>
        <SidebarGroupContent>
          <SidebarMenu>
            <SidebarMenuItem v-for="item in navigationLinks" :key="item.path">
              <SidebarMenuButton as-child :tooltip="item.label" class="hover:bg-primary/50 hover:text-primary-foreground hover:pl-3" active-class="bg-primary text-primary-foreground font-medium px-2 py-1.5">
                <router-link :to="item.path" >
                  <component :is="item.icon" />
                  <span>{{ item.label }}</span>
                  <span
                    v-if="item.badge"
                    class="ml-auto text-xs rounded-full bg-primary text-primary-foreground px-2 py-0.5"
                  >
                    {{ item.badge }}
                  </span>
                </router-link>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarGroupContent>
      </SidebarGroup>

      <SidebarSeparator />

      <SidebarGroup>
        <SidebarGroupLabel>Settings</SidebarGroupLabel>
        <SidebarGroupContent>
          <SidebarMenu>
            <SidebarMenuItem v-for="item in settingsLinks" :key="item.path">
              <SidebarMenuButton as-child :tooltip="item.label" class="hover:bg-primary/50 hover:text-primary-foreground hover:pl-3" active-class="bg-primary text-primary-foreground font-medium px-2 py-1.5">
                <router-link :to="item.path" >
                  <component :is="item.icon" />
                  <span>{{ item.label }}</span>
                </router-link>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarGroupContent>
      </SidebarGroup>
    </SidebarContent>

    <SidebarFooter>
      <!-- Countdown Timer (hidden when collapsed) -->
      <div v-if="state === 'expanded'" class="px-2 pb-2">
        <CountdownTimer variant="sidebar" />
      </div>
    </SidebarFooter>
    <SidebarRail />
  </Sidebar>
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
  Map,
  Bed,
  TrainFront,
  Ship,
  Calendar,
  CalendarClock,
  CalendarDays,

} from 'lucide-vue-next'

import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarFooter,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarRail,
  SidebarSeparator,
  useSidebar,
} from "@/components/ui/sidebar"

import CountdownTimer from '@/components/CountdownTimer.vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { computed } from 'vue'

const { state } = useSidebar()
const authStore = useAuthStore()

const allNavigationLinks = [
  {
    path: '/beranda',
    label: 'Beranda',
    icon: LayoutDashboard,
    roles: ['Administrator', 'Kepala Dinas', 'Hotel', 'Wisata', 'Pip', 'Kapal Pesiar', 'Kereta Api']
  },
  {
    path: '/akomodasi',
    label: 'Akomodasi',
    icon: Bed,
    roles: ['Administrator', 'Kepala Dinas', 'Hotel']
  },
  {
    path: '/dtw',
    label: 'DTW',
    icon: Map,
    roles: ['Administrator', 'Kepala Dinas', 'Wisata']
  },
  {
    path: '/pip',
    label: 'PIP',
    icon: Map,
    roles: ['Administrator', 'Kepala Dinas', 'Pip']
  },
  {
    path: '/kapal-pesiar',
    label: 'Kapal Pesiar',
    icon: Ship,
    roles: ['Administrator', 'Kepala Dinas', 'Kapal Pesiar']
  },
  {
    path: '/kereta-api',
    label: 'Kereta Api',
    icon: TrainFront,
    roles: ['Administrator', 'Kepala Dinas', 'Kereta Api']
  },
  {
    path: '/nataru',
    label: 'NATARU',
    icon: CalendarClock,
    roles: ['Administrator', 'Kepala Dinas', 'Hotel', 'Wisata', 'Pip', 'Kapal Pesiar', 'Kereta Api']
  },
  {
    path: '/idul-fitri',
    label: 'Idul Fitri',
    icon: CalendarDays,
    roles: ['Administrator', 'Kepala Dinas', 'Hotel', 'Wisata', 'Pip', 'Kapal Pesiar', 'Kereta Api']
  },
  {
    path: '/events',
    label: 'Events',
    icon: Calendar,
    roles: ['Administrator', 'Kepala Dinas']
  },
]

const allSettingsLinks = [
  {
    path: '/users',
    label: 'Users',
    icon: Users,
    roles: ['Administrator', 'Kepala Dinas']
  },
  {
    path: '/laporan',
    label: 'Laporan',
    icon: BarChart3,
    roles: ['Administrator', 'Kepala Dinas', 'Hotel', 'Wisata', 'Pip', 'Kapal Pesiar', 'Kereta Api']
  },
  {
    path: '/settings',
    label: 'Settings',
    icon: Settings,
    roles: ['Administrator', 'Kepala Dinas']
  }
]

// Filter menu berdasarkan role user
const navigationLinks = computed(() => {
  const userRole = authStore.user?.role
  if (!userRole) return []
  
  return allNavigationLinks.filter(link => 
    link.roles.includes(userRole)
  )
})

const settingsLinks = computed(() => {
  const userRole = authStore.user?.role
  if (!userRole) return []
  
  return allSettingsLinks.filter(link => 
    link.roles.includes(userRole)
  )
})

const route = useRoute()
</script>
