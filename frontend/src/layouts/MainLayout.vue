<template>
  <div class="min-h-screen bg-slate-50 text-slate-800 flex flex-col font-sans">
    <!-- Navbar Atas -->
    <header class="bg-white border-b border-slate-200 sticky top-0 z-40 px-4 lg:px-8 py-3 flex items-center justify-between shadow-xs">
      <div class="flex items-center gap-3">
        <Badge class="h-9 px-3 rounded-lg bg-blue-600 text-white font-black text-sm shadow-sm">
          BSrE
        </Badge>
        <div>
          <h1 class="text-sm font-bold tracking-tight text-slate-900 leading-tight">
            SIMRS Document & TTE Service
          </h1>
          <p class="text-[10px] text-slate-500 font-medium">UOBK RSUD DOKTER MOHAMAD SALEH KOTA PROBOLINGGO</p>
        </div>
      </div>

      <!-- Quick Role Switcher & Notifikasi Lonceng Menggunakan Komponen Modular Button & Badge -->
      <div class="flex items-center gap-3">
        <div class="hidden sm:flex items-center gap-1.5 bg-slate-100 p-1 rounded-lg border border-slate-200 text-xs">
          <span class="text-[11px] text-slate-500 font-semibold px-2">Role:</span>
          <Button
            v-for="r in roles"
            :key="r.id"
            size="sm"
            :variant="activeUser?.username === r.username ? 'default' : 'ghost'"
            class="h-7 px-2.5 text-xs"
            @click="switchRole(r)"
          >
            {{ r.label }}
          </Button>
        </div>

        <!-- Lonceng Notifikasi Interaktif -->
        <div class="relative">
          <Button
            variant="ghost"
            size="icon"
            class="relative h-9 w-9"
            title="Notifikasi Dokumen Pending TTE"
            @click="toggleNotificationDropdown"
          >
            <Bell class="w-5 h-5 text-slate-600" />
            <Badge
              v-if="pendingCount > 0"
              class="absolute -top-1 -right-1 px-1.5 py-0.5 bg-rose-600 text-white text-[10px] font-black rounded-full"
            >
              {{ pendingCount }}
            </Badge>
          </Button>

          <!-- Popover Dropdown Notifikasi Menggunakan Card Modular -->
          <Card
            v-if="showNotifDropdown"
            class="absolute right-0 mt-2 w-80 md:w-96 bg-white rounded-2xl shadow-2xl border-slate-200 z-50 p-4 text-xs"
          >
            <div class="flex items-center justify-between pb-3 border-b border-slate-100">
              <div class="font-bold text-slate-900 text-sm flex items-center gap-1.5">
                <Bell class="w-4 h-4 text-amber-600" />
                <span>Notifikasi TTE BSrE</span>
              </div>
              <Badge variant="destructive" class="text-[10px]">
                {{ pendingCount }} Menunggu TTE
              </Badge>
            </div>

            <div class="mt-3 space-y-2.5 max-h-72 overflow-y-auto">
              <div v-if="notifications.length === 0" class="text-center py-6 text-slate-400">
                Tidak ada notifikasi dokumen yang pending.
              </div>

              <div
                v-for="n in notifications"
                :key="n.id"
                class="p-3 bg-amber-50/70 border border-amber-200/80 rounded-xl space-y-1.5"
              >
                <div class="font-bold text-amber-900 flex items-center justify-between">
                  <span>{{ n.title }}</span>
                  <Badge variant="outline" class="text-[10px] border-amber-300 text-amber-800">
                    {{ n.pending_count }} Dokumen
                  </Badge>
                </div>
                <p class="text-amber-800 text-[11px] leading-relaxed">
                  {{ n.message }}
                </p>
                <div class="pt-1 flex justify-end">
                  <Button
                    size="sm"
                    class="h-7 px-3 bg-amber-600 hover:bg-amber-700 text-white text-[10px] font-bold"
                    @click="goToBatchSign()"
                  >
                    Buka Antrean & Sign Sekarang →
                  </Button>
                </div>
              </div>
            </div>

            <div class="mt-3 pt-2 border-t border-slate-100 text-center">
              <Button variant="ghost" size="sm" class="h-7 text-[11px]" @click="showNotifDropdown = false">
                Tutup
              </Button>
            </div>
          </Card>
        </div>

        <!-- User Profile Pill -->
        <div class="flex items-center gap-2 pl-2 border-l border-slate-200">
          <div class="w-8 h-8 rounded-full bg-blue-100 border border-blue-200 text-blue-700 font-bold text-xs flex items-center justify-center">
            {{ activeUser?.nama?.charAt(0) || 'D' }}
          </div>
          <div class="text-left hidden md:block">
            <div class="text-xs font-bold text-slate-800 leading-none truncate max-w-[160px]">{{ activeUser?.nama }}</div>
            <div class="text-[10px] text-slate-400 capitalize mt-0.5">{{ activeUser?.role }}</div>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content Area -->
    <main class="flex-1 p-4 lg:p-8 max-w-7xl mx-auto w-full">
      <router-view
        :current-user="activeUser"
        :pending-count="pendingCount"
        @refresh-notifications="loadNotifications"
      />
    </main>

    <!-- Footer -->
    <footer class="bg-white border-t border-slate-200 py-3 px-6 text-center text-xs text-slate-400">
      SIMRS Microservice Dokumen & TTE BSrE BSSN • UOBK RSUD Dokter Mohamad Saleh Kota Probolinggo • Sesuai Permenkes No. 24/2022
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { authApi, notificationApi } from '@/services/api'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card } from '@/components/ui/card'
import { Bell } from 'lucide-vue-next'

const roles = [
  { id: 'dr_a', username: 'dr_rizki', role: 'dokter', label: 'Dokter Pemeriksa / DPJP' },
  { id: 'pr', username: 'perawat_dinda', role: 'perawat', label: 'Perawat Ranap' },
  { id: 'adm', username: 'admin', role: 'admin', label: 'Admin RM' }
]

const activeUser = ref({
  id: 1,
  username: 'dr_rizki',
  nama: 'dr. RIA NURMALA SETYANINGRUM',
  role: 'dokter'
})

const pendingCount = ref(0)
const notifications = ref([])
const showNotifDropdown = ref(false)

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
  window.dispatchEvent(new CustomEvent('open-inbox-tte'))
}

onMounted(() => {
  switchRole(roles[0])
})
</script>
