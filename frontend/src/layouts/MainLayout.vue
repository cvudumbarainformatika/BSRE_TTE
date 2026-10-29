<template>
  <div class="h-screen overflow-hidden flex bg-background text-foreground font-sans">
    <!-- SIDEBAR NAV (Mendukung Normal & Mini Sidebar Modern) -->
    <aside
      :class="[
        'bg-sidebar border-r border-border hidden md:flex flex-col justify-between z-20 shrink-0 shadow-xs transition-all duration-300 ease-in-out',
        isSidebarMini ? 'w-[72px]' : 'w-64'
      ]"
    >
      <div class="flex flex-col flex-1 overflow-y-auto overflow-x-hidden">
        <!-- Logo & Brand Header (Klik Logo untuk Toggle Mini/Normal Sidebar) -->
        <div
          class="border-b border-border bg-sidebar transition-all duration-300"
          :class="isSidebarMini ? 'p-3 flex justify-center' : 'p-5 flex items-center space-x-3'"
        >
          <button
            type="button"
            class="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-emerald-400 flex items-center justify-center text-slate-950 font-bold text-lg shadow-lg shadow-cyan-500/20 shrink-0 cursor-pointer hover:scale-105 active:scale-95 transition-all duration-200 focus:outline-none"
            :title="isSidebarMini ? 'Klik untuk Melebarkan Sidebar' : 'Klik untuk Mempersempit (Mini Sidebar)'"
            @click="toggleSidebar"
          >
            <ShieldCheck class="w-6 h-6" />
          </button>
          
          <div v-show="!isSidebarMini" class="min-w-0 transition-opacity duration-200">
            <div class="font-bold text-sm tracking-wide text-foreground flex items-center gap-1.5 whitespace-nowrap">
              E-DOC <Badge variant="outline" class="text-[10px] px-1.5 py-0 rounded bg-primary/10 text-primary border-primary/30">BSrE</Badge>
            </div>
            <p class="text-[10px] text-muted-foreground tracking-wider uppercase font-mono whitespace-nowrap">BSSN Verified TTE</p>
          </div>
        </div>

        <!-- Instansi Sub-Header (Hanya di mode normal) -->
        <div
          v-show="!isSidebarMini"
          class="px-5 py-2.5 bg-muted/40 border-b border-border text-[11px] text-muted-foreground font-medium truncate transition-all duration-200"
        >
          UOBK RSUD dr. Mohamad Saleh
        </div>

        <!-- Navigation Links (Center Match saat Mini Sidebar) -->
        <nav
          class="space-y-1.5 flex-1 transition-all duration-300"
          :class="isSidebarMini ? 'p-2 flex flex-col items-center' : 'p-4'"
        >
          <Button
            v-for="item in navMenuItems"
            :key="item.id"
            :variant="activeNav === item.id ? 'secondary' : 'ghost'"
            class="transition-all cursor-pointer relative"
            :class="[
              isSidebarMini
                ? 'w-11 h-11 p-0 flex items-center justify-center rounded-xl mx-auto'
                : 'w-full justify-start gap-3 h-11 px-3 text-xs font-medium rounded-xl',
              activeNav === item.id
                ? 'bg-primary/15 text-primary border border-primary/30 font-semibold shadow-xs'
                : 'text-muted-foreground hover:text-foreground hover:bg-muted/60'
            ]"
            :title="item.label"
            @click="navigateTo(item.id)"
          >
            <component
              :is="item.icon"
              :class="[
                isSidebarMini ? 'w-5 h-5' : 'w-4 h-4 shrink-0',
                activeNav === item.id ? 'text-primary' : 'text-muted-foreground'
              ]"
            />
            <span v-if="!isSidebarMini" class="truncate">{{ item.label }}</span>
            
            <!-- Badge Angka di Mode Normal -->
            <Badge
              v-if="!isSidebarMini && item.id === 'inbox' && pendingCount > 0"
              class="ml-auto px-1.5 py-0.2 bg-destructive text-destructive-foreground text-[10px] font-bold rounded-full"
            >
              {{ pendingCount }}
            </Badge>

            <!-- Lampu Dot Merah di Mode Mini -->
            <span
              v-if="isSidebarMini && item.id === 'inbox' && pendingCount > 0"
              class="absolute top-2 right-2 w-2.5 h-2.5 bg-destructive rounded-full border-2 border-sidebar animate-pulse"
              :title="`${pendingCount} Dokumen Menunggu TTE`"
            ></span>
          </Button>
        </nav>
      </div>

      <!-- BSrE Status Footer at Bottom Sidebar (Mode Normal vs Mode Mini Berlampu Kedip) -->
      <div v-if="!isSidebarMini" class="p-4 m-3 rounded-xl glass-panel border border-emerald-500/30 bg-emerald-500/10 transition-all duration-300">
        <div class="flex items-center justify-between mb-2">
          <span class="text-xs font-semibold text-emerald-600 dark:text-emerald-400 flex items-center gap-1.5">
            <span class="w-2 h-2 rounded-full bg-emerald-500 animate-ping"></span>
            BSrE Service Connected
          </span>
          <Activity class="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
        </div>
        <p class="text-[11px] text-muted-foreground">
          ID Sertifikat: <span class="font-mono text-foreground font-semibold">BSRE-20261027-83FC</span>
        </p>
        <p class="text-[10px] text-muted-foreground mt-0.5">RSA 2048 • Exp: 14 Nov 2027</p>
      </div>

      <!-- Indikator Lampu Kedip Futuristik Center saat Mini Sidebar -->
      <div
        v-else
        class="my-4 mx-auto p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center cursor-pointer hover:bg-emerald-500/20 transition-all shadow-xs"
        title="BSrE Service Connected (Online) • ID: BSRE-20261027-83FC • RSA 2048"
      >
        <div class="relative flex items-center justify-center w-5 h-5">
          <span class="absolute w-4 h-4 rounded-full bg-emerald-500 animate-ping opacity-75"></span>
          <span class="relative w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
        </div>
      </div>
    </aside>

    <!-- MAIN CONTENT AREA -->
    <div class="flex-1 flex flex-col h-screen overflow-hidden">
      <!-- HEADER TOP BAR -->
      <header class="h-16 bg-sidebar border-b border-border px-4 sm:px-6 flex items-center justify-between z-10 shrink-0 shadow-xs">
        <!-- Brand on Mobile / Quick Title on Desktop -->
        <div class="flex items-center gap-3">
          <div class="md:hidden flex items-center gap-2">
            <div class="w-8 h-8 rounded-lg bg-gradient-to-tr from-cyan-500 to-emerald-400 flex items-center justify-center text-slate-950 font-bold text-sm">
              <ShieldCheck class="w-5 h-5" />
            </div>
            <span class="font-bold text-xs tracking-wide">E-DOC BSrE</span>
          </div>

          <!-- Indikator Integrasi E-RM -->
          <div class="hidden lg:flex items-center gap-2 text-xs text-muted-foreground font-medium">
            <span class="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
            <span>E-RM Microservice TTE BSrE BSSN • <strong class="text-foreground">UOBK RSUD dr. Mohamad Saleh</strong></span>
          </div>
        </div>

        <!-- Right Controls: Status Portal Global, Dark/Light Mode, Notif -->
        <div class="flex items-center space-x-2 sm:space-x-3">
          <!-- Badge Mode Global -->
          <Badge variant="outline" class="hidden sm:flex items-center gap-1.5 px-3 py-1 text-[11px] bg-primary/10 text-primary border-primary/30 rounded-lg font-semibold">
            <ShieldCheck class="w-3.5 h-3.5" />
            <span>Mode Global • Otorisasi & Arsip TTE</span>
          </Badge>

          <!-- Dark / Light Mode Toggle Button -->
          <Button
            variant="ghost"
            size="icon"
            class="h-9 w-9 rounded-xl border border-border text-foreground hover:bg-muted"
            title="Ganti Mode Gelap / Terang"
            @click="toggleDarkMode"
          >
            <Sun v-if="isDark" class="w-4 h-4 text-amber-400 transition-transform duration-300" />
            <Moon v-else class="w-4 h-4 text-slate-700 transition-transform duration-300" />
          </Button>

          <!-- Lonceng Notifikasi Interaktif -->
          <div class="relative">
            <Button
              variant="ghost"
              size="icon"
              class="relative h-9 w-9 rounded-xl border border-border text-foreground hover:bg-muted"
              title="Notifikasi Dokumen Pending TTE"
              @click="toggleNotificationDropdown"
            >
              <Bell class="w-4 h-4 text-foreground" />
              <Badge
                v-if="pendingCount > 0"
                class="absolute -top-1 -right-1 px-1.5 py-0.5 bg-destructive text-destructive-foreground text-[10px] font-black rounded-full"
              >
                {{ pendingCount }}
              </Badge>
            </Button>

            <!-- Dropdown Notifikasi Menggunakan Card Modular -->
            <Card
              v-if="showNotifDropdown"
              class="absolute right-0 mt-2 w-80 sm:w-96 glass-panel rounded-2xl shadow-2xl border-border z-50 p-4 text-xs"
            >
              <div class="flex items-center justify-between pb-3 border-b border-border">
                <div class="font-bold text-foreground text-sm flex items-center gap-1.5">
                  <Bell class="w-4 h-4 text-amber-500" />
                  <span>Notifikasi Antrean TTE</span>
                </div>
                <Badge variant="destructive" class="text-[10px]">
                  {{ pendingCount }} Menunggu TTE
                </Badge>
              </div>

              <div class="mt-3 space-y-2.5 max-h-72 overflow-y-auto">
                <div v-if="notifications.length === 0" class="text-center py-6 text-muted-foreground">
                  Tidak ada antrean dokumen yang pending.
                </div>

                <div
                  v-for="n in notifications"
                  :key="n.id"
                  class="p-3 bg-muted/60 border border-border rounded-xl space-y-1.5"
                >
                  <div class="font-bold text-foreground flex items-center justify-between">
                    <span>{{ n.title }}</span>
                    <Badge variant="outline" class="text-[10px]">
                      {{ n.pending_count }} Dokumen
                    </Badge>
                  </div>
                  <p class="text-muted-foreground text-[11px] leading-relaxed">
                    {{ n.message }}
                  </p>
                  <div class="pt-1 flex justify-end">
                    <Button
                      size="sm"
                      class="h-7 px-3 bg-primary text-primary-foreground text-[10px] font-bold rounded-lg"
                      @click="goToBatchSign()"
                    >
                      Buka Inbox TTE →
                    </Button>
                  </div>
                </div>
              </div>

              <div class="mt-3 pt-2 border-t border-border text-center">
                <Button variant="ghost" size="sm" class="h-7 text-[11px]" @click="showNotifDropdown = false">
                  Tutup
                </Button>
              </div>
            </Card>
          </div>
        </div>
      </header>

      <!-- DYNAMIC CONTENT CONTAINER (Background kontras slate-200 dengan Akselerasi Scroll & Observer) -->
      <main class="flex-1 overflow-y-auto p-4 sm:p-6 bg-background will-change-scroll">
        <router-view
          :current-user="activeUser"
          :pending-count="pendingCount"
          :active-nav="activeNav"
          @refresh-notifications="loadNotifications"
          @switch-tab="onChildSwitchTab"
        />
      </main>

      <!-- FOOTER -->
      <footer class="h-9 bg-sidebar border-t border-border px-6 flex items-center justify-between text-[11px] text-muted-foreground shrink-0 shadow-xs">
        <div>E-RM Microservice TTE BSrE BSSN • UOBK RSUD dr. Mohamad Saleh</div>
        <div class="font-mono text-[10px]">Permenkes No. 24/2022 • UU ITE</div>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { authApi, notificationApi } from '@/services/api'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card } from '@/components/ui/card'
import {
  ShieldCheck,
  LayoutDashboard,
  FileText,
  Inbox,
  Archive,
  Sparkles,
  Sun,
  Moon,
  Bell,
  Activity
} from 'lucide-vue-next'

const roles = [
  { id: 'dr_a', username: 'dr_rizki', role: 'dokter', label: 'DPJP (Dokter)' },
  { id: 'pr', username: 'perawat_dinda', role: 'perawat', label: 'Perawat Ranap' },
  { id: 'adm', username: 'admin', role: 'admin', label: 'Admin RM' }
]

const navMenuItems = [
  { id: 'dashboard', label: 'Dashboard Overview', icon: LayoutDashboard },
  { id: 'inbox', label: 'Inbox TTE', icon: Inbox },
  { id: 'dokumen', label: 'Dokumen', icon: FileText },
  { id: 'vector', label: 'Pencarian Semantik AI', icon: Sparkles }
]

const activeNav = ref('dashboard') // Menu pertama yang aktif adalah dashboard!
const isDark = ref(false) // Default Light Mode!
const isSidebarMini = ref(localStorage.getItem('sidebar-mini') === 'true')

const toggleSidebar = () => {
  isSidebarMini.value = !isSidebarMini.value
  localStorage.setItem('sidebar-mini', isSidebarMini.value ? 'true' : 'false')
}

const activeUser = ref({
  id: 1,
  username: 'dr_rizki',
  nama: 'dr. RIA NURMALA SETYANINGRUM',
  role: 'dokter'
})

const pendingCount = ref(0)
const notifications = ref([])
const showNotifDropdown = ref(false)

const applyTheme = (dark) => {
  isDark.value = dark
  if (dark) {
    document.documentElement.classList.add('dark')
    localStorage.setItem('theme', 'dark')
  } else {
    document.documentElement.classList.remove('dark')
    localStorage.setItem('theme', 'light')
  }
}

const toggleDarkMode = () => {
  applyTheme(!isDark.value)
}

const navigateTo = (navId) => {
  activeNav.value = navId
  window.dispatchEvent(new CustomEvent('nav-tab-change', { detail: navId }))
}

const onChildSwitchTab = (tabId) => {
  activeNav.value = tabId
}

const toggleNotificationDropdown = () => {
  showNotifDropdown.value = !showNotifDropdown.value
  if (showNotifDropdown.value) {
    loadNotifications()
  }
}

const loadNotifications = async () => {
  try {
    const res = await notificationApi.getMyNotifications()
    notifications.value = res.data.notifications || []
    pendingCount.value = res.data.unread_count || 0
  } catch (err) {
    pendingCount.value = 0
    notifications.value = []
  }
}

const switchRole = async (target) => {
  try {
    const res = await authApi.login({
      username: target.username,
      password: 'password123'
    })
    localStorage.setItem('access_token', res.data.access_token)
    activeUser.value = res.data.user
  } catch (err) {
    activeUser.value = {
      id: 1,
      username: target.username,
      nama: target.role === 'dokter' ? 'dr. RIA NURMALA SETYANINGRUM' : 'Petugas E-RM',
      role: target.role
    }
  }
  loadNotifications()
}

const goToBatchSign = () => {
  showNotifDropdown.value = false
  navigateTo('inbox')
  window.dispatchEvent(new CustomEvent('open-inbox-tte'))
}

onMounted(() => {
  // Inisialisasi Tema: DEFAULT LIGHT MODE sesuai instruksi pengguna
  const savedTheme = localStorage.getItem('theme') || 'light'
  applyTheme(savedTheme === 'dark')

  // Listen event perubahan tab dari widget jika ada
  window.addEventListener('set-active-tab', (e) => {
    if (e.detail) {
      activeNav.value = e.detail
    }
  })

  switchRole(roles[0])
})
</script>
