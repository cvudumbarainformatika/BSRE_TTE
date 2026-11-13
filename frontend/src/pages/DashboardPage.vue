<template>
  <AppPage :loading="isPageLoading">
    <!-- ===================================================================== -->
    <!-- 1. TAMPILAN KHUSUS MENU: DASHBOARD OVERVIEW                           -->
    <!-- HANYA di menu dashboard banner & 4 stat cards ini dimunculkan!        -->
    <!-- ===================================================================== -->
    <div v-if="currentNav === 'dashboard'" class="space-y-6">
      <!-- Banner Sambutan Futuristik (Glassmorphism Glow dari ui-mantap.html) -->
      <div class="relative p-6 rounded-2xl glass-panel-glow overflow-hidden flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div class="z-10">
          <div class="flex items-center gap-2 flex-wrap">
            <span class="text-xs font-mono px-2.5 py-1 rounded-full bg-primary/10 text-primary border border-primary/30">
              BSSN Certified Environment • BSrE Cloud Sync
            </span>
            <span v-if="currentUser?.nama" class="text-xs font-mono px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30 flex items-center gap-1.5 font-semibold">
              <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
              Selamat Bertugas, {{ currentUser.nama }}
            </span>
          </div>
          <h2 class="text-xl sm:text-2xl font-bold text-foreground mt-2">
            Sistem Tanda Tangan Elektronik BSrE
          </h2>
          <p class="text-xs sm:text-sm text-muted-foreground mt-1 max-w-2xl leading-relaxed">
            Pengelolaan keabsahan hukum, integritas berkas elektronik instansi, dan integrasi Rekam Medis Elektronik (E-RM) tersertifikasi Balai Sertifikasi Elektronik (BSrE BSSN).
          </p>
        </div>
        <!-- Tombol Aksi Cepat Berupa Icon Button Rapi di Sisi Kanan Header Banner -->
        <div class="z-10 flex items-center gap-2.5 self-start md:self-center shrink-0">
          <!-- Icon Tombol Inbox TTE -->
          <Button
            variant="outline"
            size="icon"
            class="h-10 w-10 rounded-xl border border-border/80 bg-background/80 hover:bg-primary/10 hover:border-primary/40 text-foreground transition-all shadow-xs relative cursor-pointer"
            title="Buka Inbox TTE Antrean"
            @click="navigateToNav('inbox')"
          >
            <Inbox class="w-4 h-4 text-primary" />
            <span
              v-if="pendingInboxCount > 0"
              class="absolute -top-1 -right-1 px-1.5 py-0.2 bg-destructive text-destructive-foreground text-[10px] font-bold rounded-full shadow-xs"
            >
              {{ pendingInboxCount }}
            </span>
          </Button>

          <!-- Icon Tombol Dokumen Sah TTE -->
          <Button
            variant="outline"
            size="icon"
            class="h-10 w-10 rounded-xl border border-border/80 bg-background/80 hover:bg-emerald-500/10 hover:border-emerald-500/40 text-foreground transition-all shadow-xs cursor-pointer"
            title="Buka Dokumen Sah Terverifikasi TTE"
            @click="navigateToNav('dokumen')"
          >
            <FileText class="w-4 h-4 text-emerald-500" />
          </Button>
        </div>
        <!-- Background Glow Decor -->
        <div class="absolute -right-10 -bottom-10 w-60 h-60 bg-primary/10 rounded-full blur-3xl pointer-events-none"></div>
      </div>

      <!-- 4 Stat Cards Real Database -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <!-- Card 1: Total Dokumen TTE -->
        <Card class="glass-panel hover:border-primary/40 transition-all border-border shadow-xs">
          <CardContent class="p-5">
            <div class="flex items-center justify-between text-muted-foreground">
              <span class="text-xs font-medium uppercase tracking-wider">Total Dokumen TTE</span>
              <div class="w-8 h-8 rounded-lg bg-primary/10 text-primary flex items-center justify-center">
                <FileCheck class="w-4 h-4" />
              </div>
            </div>
            <div class="mt-3 flex items-baseline justify-between">
              <span class="text-2xl font-bold text-foreground font-mono">{{ stats.total_dokumen.toLocaleString('id-ID') }}</span>
              <Badge variant="outline" class="text-[10px] text-emerald-500 border-emerald-500/30 font-medium">
                Terverifikasi BSrE
              </Badge>
            </div>
            <p class="text-[11px] text-muted-foreground mt-1">Total dokumen resmi terdaftar di sistem</p>
          </CardContent>
        </Card>

        <!-- Card 2: Verifikasi Sah -->
        <Card class="glass-panel hover:border-emerald-500/40 transition-all border-border shadow-xs">
          <CardContent class="p-5">
            <div class="flex items-center justify-between text-muted-foreground">
              <span class="text-xs font-medium uppercase tracking-wider">Verifikasi Sah (Valid)</span>
              <div class="w-8 h-8 rounded-lg bg-emerald-500/10 text-emerald-400 flex items-center justify-center">
                <CheckCircle2 class="w-4 h-4" />
              </div>
            </div>
            <div class="mt-3 flex items-baseline justify-between">
              <span class="text-2xl font-bold text-foreground font-mono">{{ stats.verifikasi_sah.toLocaleString('id-ID') }}</span>
              <span class="text-xs text-emerald-400 font-medium font-mono">{{ stats.persentase_sah }}%</span>
            </div>
            <p class="text-[11px] text-muted-foreground mt-1">Integritas hash SHA-256 terjaga</p>
          </CardContent>
        </Card>

        <!-- Card 3: Pending TTE -->
        <Card class="glass-panel hover:border-amber-500/40 transition-all border-border shadow-xs cursor-pointer" @click="navigateToNav('inbox')">
          <CardContent class="p-5">
            <div class="flex items-center justify-between text-muted-foreground">
              <span class="text-xs font-medium uppercase tracking-wider">Pending TTE</span>
              <div class="w-8 h-8 rounded-lg bg-amber-500/10 text-amber-500 flex items-center justify-center">
                <Clock class="w-4 h-4" />
              </div>
            </div>
            <div class="mt-3 flex items-baseline justify-between">
              <span class="text-2xl font-bold text-foreground font-mono">{{ stats.pending_tte.toLocaleString('id-ID') }}</span>
              <Badge variant="outline" class="text-[11px] border-amber-500/30 text-amber-500 font-medium">
                {{ stats.pending_tte > 0 ? 'Membutuhkan Paraf' : 'Antrean Bersih' }}
              </Badge>
            </div>
            <p class="text-[11px] text-muted-foreground mt-1">Antrean tanda tangan elektronik</p>
          </CardContent>
        </Card>

        <!-- Card 4: Sertifikat Elektronik BSrE -->
        <Card class="glass-panel hover:border-blue-500/40 transition-all border-border shadow-xs">
          <CardContent class="p-5">
            <div class="flex items-center justify-between text-muted-foreground">
              <span class="text-xs font-medium uppercase tracking-wider">Sertifikat Elektronik BSrE</span>
              <div class="w-8 h-8 rounded-lg bg-blue-500/10 text-blue-400 flex items-center justify-center">
                <Key class="w-4 h-4" />
              </div>
            </div>
            <div class="mt-3 flex items-baseline justify-between">
              <span class="text-2xl font-bold text-foreground">{{ stats.sertifikat.status }}</span>
              <span class="text-xs text-primary font-mono font-semibold">{{ stats.sertifikat.tipe }}</span>
            </div>
            <p class="text-[11px] text-muted-foreground mt-1">{{ stats.sertifikat.keterangan }}</p>
          </CardContent>
        </Card>
      </div>

      <!-- Quick Action Cards Dashboard -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2">
        <Card class="glass-panel border-border hover:border-amber-500/40 transition-all cursor-pointer" @click="navigateToNav('inbox')">
          <CardHeader class="pb-2">
            <div class="w-10 h-10 rounded-xl bg-amber-500/10 text-amber-500 flex items-center justify-center mb-2">
              <Inbox class="w-5 h-5" />
            </div>
            <CardTitle class="text-sm font-bold text-foreground">Inbox TTE</CardTitle>
            <CardDescription class="text-xs text-muted-foreground">
              {{ stats.pending_tte }} berkas/data dari E-RM yang belum di-TTE dan menunggu tanda tangan Anda.
            </CardDescription>
          </CardHeader>
          <CardContent class="pt-0">
            <span class="text-xs font-bold text-amber-500 flex items-center gap-1">Buka Inbox TTE →</span>
          </CardContent>
        </Card>

        <Card class="glass-panel border-border hover:border-emerald-500/40 transition-all cursor-pointer" @click="navigateToNav('dokumen')">
          <CardHeader class="pb-2">
            <div class="w-10 h-10 rounded-xl bg-emerald-500/10 text-emerald-500 flex items-center justify-center mb-2">
              <FileText class="w-5 h-5" />
            </div>
            <CardTitle class="text-sm font-bold text-foreground">Dokumen (Sudah TTE)</CardTitle>
            <CardDescription class="text-xs text-muted-foreground">
              {{ stats.verifikasi_sah }} dokumen yang sah memiliki PDF & TTE BSrE resmi, lengkap dengan fitur versioning & verifikasi.
            </CardDescription>
          </CardHeader>
          <CardContent class="pt-0">
            <span class="text-xs font-bold text-emerald-500 flex items-center gap-1">Buka Dokumen Sah →</span>
          </CardContent>
        </Card>

        <Card class="glass-panel border-border hover:border-cyan-500/40 transition-all cursor-pointer" @click="navigateToNav('upload')">
          <CardHeader class="pb-2">
            <div class="w-10 h-10 rounded-xl bg-cyan-500/10 text-cyan-400 flex items-center justify-center mb-2">
              <UploadCloud class="w-5 h-5" />
            </div>
            <CardTitle class="text-sm font-bold text-foreground">Upload & TTE PDF</CardTitle>
            <CardDescription class="text-xs text-muted-foreground">
              Unggah berkas PDF, Word, atau EPUB dengan kanvas penempatan stempel QR presisi.
            </CardDescription>
          </CardHeader>
          <CardContent class="pt-0">
            <span class="text-xs font-bold text-cyan-400 flex items-center gap-1">Unggah Dokumen →</span>
          </CardContent>
        </Card>
      </div>
    </div>

    <!-- ===================================================================== -->
    <!-- 2. TAMPILAN KHUSUS MENU: INBOX TTE (DOKUMEN BELUM DI-TTE)             -->
    <!-- ===================================================================== -->
    <div v-else-if="currentNav === 'inbox'" class="space-y-4">
      <PendingTteInbox
        ref="inboxRef"
        @preview-doc="openViewer"
        @document-signed="onDocumentSigned"
      />
    </div>

    <!-- ===================================================================== -->
    <!-- 3. TAMPILAN KHUSUS MENU: DOKUMEN (SUDAH ADA PDF & SUDAH DI-TTE)       -->
    <!-- ===================================================================== -->
    <div v-else-if="currentNav === 'dokumen'" class="space-y-4">
      <DocumentList
        ref="docListRef"
        :user-role="currentUser?.role || 'dokter'"
        @view-document="openViewer"
      />
    </div>

    <!-- ===================================================================== -->
    <!-- 4. TAMPILAN KHUSUS MENU: UPLOAD & TTE INTERAKTIF                       -->
    <!-- ===================================================================== -->
    <div v-else-if="currentNav === 'upload'" class="space-y-4">
      <UploadTteInteractive
        @document-signed="onDocumentSigned"
        @navigate-to="navigateToNav"
      />
    </div>

    <!-- MODAL INLINE VIEWER MENGGUNAKAN KOMPONEN MODULAR AppDialog -->
    <AppDialog
      v-model="isViewerOpen"
      :title="selectedDoc?.title || selectedDoc?.filename || 'Preview Dokumen PDF'"
      max-width="sm:max-w-5xl"
      :hide-footer="true"
    >
      <div class="h-[80vh]">
        <DocumentViewer
          v-if="selectedDoc"
          :document="selectedDoc"
          :closable="true"
          @close="isViewerOpen = false"
        />
      </div>
    </AppDialog>
  </AppPage>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, watch } from 'vue'
import { documentApi } from '@/services/api'
import AppPage from '@/components/AppPage.vue'
import AppTabs from '@/components/AppTabs.vue'
import AppInput from '@/components/AppInput.vue'
import AppDialog from '@/components/AppDialog.vue'
import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import {
  FileCheck,
  CheckCircle2,
  Clock,
  Key,
  FileSignature,
  FileText,
  Inbox,
  Archive,
  ArrowUpRight,
  UploadCloud
} from 'lucide-vue-next'

import PendingTteInbox from '@/widgets/PendingTteInbox.vue'
import DocumentList from '@/widgets/DocumentList.vue'
import DocumentViewer from '@/widgets/DocumentViewer.vue'
import UploadTteInteractive from '@/widgets/UploadTteInteractive.vue'

const props = defineProps({
  currentUser: {
    type: Object,
    default: () => ({ role: 'dokter', nama: 'dr. RIA NURMALA SETYANINGRUM' })
  },
  pendingCount: {
    type: Number,
    default: 0
  },
  activeNav: {
    type: String,
    default: 'dashboard'
  }
})

const emit = defineEmits(['refresh-notifications', 'switch-tab'])

const isPageLoading = ref(false)
const currentNav = ref(props.activeNav || 'dashboard')

const inboxRef = ref(null)
const docListRef = ref(null)
const selectedDoc = ref(null)
const isViewerOpen = ref(false)
const pendingInboxCount = ref(props.pendingCount || 0)

// Data Statistik Riil dari Database PostgreSQL
const stats = reactive({
  total_dokumen: 0,
  verifikasi_sah: 0,
  pending_tte: 0,
  persentase_sah: 100,
  sertifikat: {
    status: 'Aktif',
    keterangan: 'BSrE BSSN CA Valid',
    tipe: 'RSA 2048-bit'
  }
})

const loadDashboardStats = async () => {
  try {
    const res = await documentApi.getDashboardStats()
    if (res.data) {
      stats.total_dokumen = res.data.total_dokumen || 0
      stats.verifikasi_sah = res.data.verifikasi_sah || 0
      stats.pending_tte = res.data.pending_tte || 0
      stats.persentase_sah = res.data.persentase_sah || 100
      if (res.data.sertifikat) {
        stats.sertifikat = res.data.sertifikat
      }
      if (res.data.pending_tte !== undefined) {
        pendingInboxCount.value = res.data.pending_tte
      }
    }
  } catch (err) {
    console.warn('Gagal memuat statistik riil dashboard:', err)
  }
}

watch(
  () => props.pendingCount,
  (val) => {
    pendingInboxCount.value = val
  }
)

watch(
  () => props.activeNav,
  (val) => {
    if (val && val !== currentNav.value) {
      currentNav.value = val
    }
  }
)

const navigateToNav = (navId) => {
  currentNav.value = navId
  emit('switch-tab', navId)
  if (navId === 'inbox' && inboxRef.value) {
    inboxRef.value.loadPendingDocs()
  }
}

const openViewer = (doc) => {
  selectedDoc.value = doc
  isViewerOpen.value = true
}

const onDocumentSigned = (result) => {
  pendingInboxCount.value = Math.max(0, pendingInboxCount.value - 1)
  emit('refresh-notifications')
  loadDashboardStats()
  if (docListRef.value?.loadDocuments) {
    docListRef.value.loadDocuments()
  }
}

const onDocumentCreated = () => {
  emit('refresh-notifications')
  loadDashboardStats()
  if (inboxRef.value) {
    inboxRef.value.loadPendingDocs()
  }
  if (docListRef.value) {
    docListRef.value.loadDocuments()
  }
}

const handleOpenInbox = () => {
  navigateToNav('inbox')
}

const handleNavTabChange = (e) => {
  if (e.detail) {
    currentNav.value = e.detail
    if (e.detail === 'inbox' && inboxRef.value) {
      inboxRef.value.loadPendingDocs()
    }
  }
}

onMounted(() => {
  loadDashboardStats()
  window.addEventListener('open-inbox-tte', handleOpenInbox)
  window.addEventListener('nav-tab-change', handleNavTabChange)
})

onUnmounted(() => {
  window.removeEventListener('open-inbox-tte', handleOpenInbox)
  window.removeEventListener('nav-tab-change', handleNavTabChange)
})
</script>
