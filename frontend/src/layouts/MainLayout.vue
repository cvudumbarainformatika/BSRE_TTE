<template>
  <div class="h-screen overflow-hidden flex bg-background text-foreground font-sans">
    <!-- SIDEBAR NAV (Mengikuti Desain ui-mantap.html) -->
    <aside class="w-64 glass-panel border-r border-border hidden md:flex flex-col justify-between z-20 shrink-0">
      <div class="flex flex-col flex-1 overflow-y-auto">
        <!-- Logo & Brand Header -->
        <div class="p-5 flex items-center space-x-3 border-b border-border">
          <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-emerald-400 flex items-center justify-center text-slate-950 font-bold text-lg shadow-lg shadow-cyan-500/20">
            <ShieldCheck class="w-6 h-6" />
          </div>
          <div>
            <div class="font-bold text-sm tracking-wide text-foreground flex items-center gap-1.5">
              E-ARCHIVE <Badge variant="outline" class="text-[10px] px-1.5 py-0 rounded bg-primary/10 text-primary border-primary/30">BSrE</Badge>
            </div>
            <p class="text-[10px] text-muted-foreground tracking-wider uppercase font-mono">BSSN Verified TTE</p>
          </div>
        </div>

        <!-- Instansi Sub-Header -->
        <div class="px-5 py-2.5 bg-muted/40 border-b border-border text-[11px] text-muted-foreground">
          UOBK RSUD dr. Mohamad Saleh
        </div>

        <!-- Navigation Links (Modular via Button & Route Navigation) -->
        <nav class="p-4 space-y-1.5 flex-1">
          <Button
            v-for="item in navMenuItems"
            :key="item.id"
            :variant="activeNav === item.id ? 'secondary' : 'ghost'"
            class="w-full justify-start gap-3 h-11 px-3 text-xs font-medium rounded-xl transition-all"
            :class="activeNav === item.id ? 'bg-primary/15 text-primary border border-primary/25 font-semibold shadow-xs' : 'text-muted-foreground hover:text-foreground'"
            @click="navigateTo(item.id)"
          >
            <component :is="item.icon" class="w-4 h-4 shrink-0" :class="activeNav === item.id ? 'text-primary' : 'text-muted-foreground'" />
            <span class="truncate">{{ item.label }}</span>
            <Badge
              v-if="item.id === 'inbox' && pendingCount > 0"
              class="ml-auto px-1.5 py-0.2 bg-destructive text-destructive-foreground text-[10px] font-bold rounded-full"
            >
              {{ pendingCount }}
            </Badge>
          </Button>
        </nav>
      </div>

      <!-- BSrE Status Badge at Bottom Sidebar (ui-mantap.html) -->
      <div class="p-4 m-3 rounded-xl glass-panel border border-emerald-500/30 bg-emerald-500/5">
        <div class="flex items-center justify-between mb-2">
          <span class="text-xs font-semibold text-emerald-400 flex items-center gap-1.5">
            <span class="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
            BSrE Service Connected
          </span>
          <Activity class="w-3.5 h-3.5 text-emerald-400" />
        </div>
        <p class="text-[11px] text-muted-foreground">
          ID Sertifikat: <span class="font-mono text-foreground font-semibold">BSRE-20261027-83FC</span>
        </p>
        <p class="text-[10px] text-muted-foreground mt-0.5">RSA 2048 • Exp: 14 Nov 2027</p>
      </div>
    </aside>

    <!-- MAIN CONTENT AREA -->
    <div class="flex-1 flex flex-col h-screen overflow-hidden">
      <!-- HEADER TOP BAR -->
      <header class="h-16 glass-panel border-b border-border px-4 sm:px-6 flex items-center justify-between z-10 shrink-0">
        <!-- Brand on Mobile / Quick Title on Desktop -->
        <div class="flex items-center gap-3">
          <div class="md:hidden flex items-center gap-2">
            <div class="w-8 h-8 rounded-lg bg-gradient-to-tr from-cyan-500 to-emerald-400 flex items-center justify-center text-slate-950 font-bold text-sm">
              <ShieldCheck class="w-5 h-5" />
            </div>
            <span class="font-bold text-xs tracking-wide">E-ARCHIVE BSrE</span>
          </div>

          <!-- Indikator Integrasi SIMRS MySQL -->
          <div class="hidden lg:flex items-center gap-2 text-xs text-muted-foreground font-medium">
            <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
            <span>SIMRS MySQL Read-Only Sync: <strong class="text-foreground">Aktif</strong></span>
          </div>
        </div>

        <!-- Right Controls: Role Switcher, Dark/Light Mode, Notif, User Profile -->
        <div class="flex items-center space-x-2 sm:space-x-3">
          <!-- Role Switcher Modular -->
          <div class="hidden sm:flex items-center gap-1 bg-muted/60 p-1 rounded-lg border border-border text-xs">
            <span class="text-[11px] text-muted-foreground font-semibold px-2">Role:</span>
            <Button
              v-for="r in roles"
              :key="r.id"
              size="sm"
              :variant="activeUser?.username === r.username ? 'default' : 'ghost'"
              class="h-7 px-2.5 text-xs rounded-md"
              @click="switchRole(r)"
            >
              {{ r.label }}
            </Button>
          </div>

          <!-- Dark / Light Mode Toggle Button -->
          <Button
            variant="ghost"
            size="icon"
            class="h-9 w-9 rounded-xl border border-border/50 text-foreground hover:bg-muted"
            title="Ganti Mode Gelap / Terang"
            @click="toggleDarkMode"
          >
            <Sun v-if="isDark" class="w-4 h-4 text-amber-400 transition-transform duration-300 rotate-0" />
            <Moon v-else class="w-4 h-4 text-slate-700 transition-transform duration-300" />
          </Button>

          <!-- Lonceng Notifikasi Interaktif -->
          <div class="relative">
            <Button
              variant="ghost"
              size="icon"
              class="relative h-9 w-9 rounded-xl border border-border/50 text-foreground hover:bg-muted"
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
                  <span>Notifikasi TTE BSrE</span>
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
                      class="h-7 px-3 bg-primary text-primary-foreground text-[10px] font-bold"
                      @click="goToBatchSign()"
                    >
                      Buka Antrean & Sign Sekarang →
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

          <div class="h-6 w-px bg-border"></div>

          <!-- User Profile Pill -->
          <div class="flex items-center gap-2 pl-1">
            <div class="w-8 h-8 rounded-full bg-gradient-to-tr from-cyan-500 to-blue-600 border border-primary/30 text-white font-bold text-xs flex items-center justify-center shadow-xs">
              {{ activeUser?.nama?.charAt(0) || 'D' }}
            </div>
            <div class="text-left hidden lg:block">
              <div class="text-xs font-bold text-foreground leading-none truncate max-w-[170px]">{{ activeUser?.nama }}</div>
              <div class="text-[10px] text-muted-foreground capitalize mt-0.5">{{ activeUser?.role }} DPJP</div>
            </div>
          </div>
        </div>
      </header>

      <!-- DYNAMIC CONTENT CONTAINER -->
      <main class="flex-1 overflow-y-auto p-4 sm:p-6 bg-background/50">
        <router-view
          :current-user="activeUser"
          :pending-count="pendingCount"
          :active-nav="activeNav"
          @refresh-notifications="loadNotifications"
          @switch-tab="onChildSwitchTab"
        />
      </main>

      <!-- FOOTER -->
      <footer class="h-9 glass-panel border-t border-border px-6 flex items-center justify-between text-[11px] text-muted-foreground shrink-0">
        <div>SIMRS Microservice TTE BSrE BSSN • UOBK RSUD dr. Mohamad Saleh</div>
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
  FileText,
  Inbox,
  Stethoscope,
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
  { id: 'kematian_ranap', label: 'Surat Kematian Ranap', icon: FileText },
  { id: 'inbox', label: 'Signature Inbox (Batch)', icon: Inbox },
  { id: 'simrs', label: 'Lembar Konsultasi', icon: Stethoscope },
  { id: 'list', label: 'Arsip & Verifikasi Dokumen', icon: Archive },
  { id: 'vector', label: 'Pencarian Semantik AI', icon: Sparkles }
]

const activeNav = ref('kematian_ranap')
const isDark = ref(true)

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
      nama: target.role === 'dokter' ? 'dr. RIA NURMALA SETYANINGRUM' : 'Petugas SIMRS',
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
  // Inisialisasi Tema Dark / Light
  const savedTheme = localStorage.getItem('theme') || 'dark'
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
