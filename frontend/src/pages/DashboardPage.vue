<template>
  <AppPage :loading="isPageLoading">
    <!-- Banner Sambutan Futuristik (Glassmorphism Glow dari ui-mantap.html) -->
    <div class="relative p-6 rounded-2xl glass-panel-glow overflow-hidden flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
      <div class="z-10">
        <span class="text-xs font-mono px-2.5 py-1 rounded-full bg-primary/10 text-primary border border-primary/30">
          BSSN Certified Environment • BSrE Cloud Sync
        </span>
        <h2 class="text-xl sm:text-2xl font-bold text-foreground mt-2">
          Sistem Pengarsipan & Verifikasi Dokumen TTE BSrE
        </h2>
        <p class="text-xs sm:text-sm text-muted-foreground mt-1 max-w-2xl leading-relaxed">
          Mengelola keabsahan hukum, integritas berkas elektronik instansi, dan sinkronisasi otomatis SIMRS via koneksi <strong>MySQL Read-Only (SELECT-only)</strong>.
        </p>
      </div>
      <div class="z-10 flex items-center gap-3">
        <Button
          class="rounded-xl bg-gradient-to-r from-cyan-500 to-emerald-400 text-slate-950 font-semibold text-xs sm:text-sm shadow-md hover:shadow-cyan-500/20 gap-2 h-10 px-4"
          @click="selectTab('inbox')"
        >
          <FileSignature class="w-4 h-4" />
          <span>Tanda Tangani Batch TTE ({{ pendingInboxCount }})</span>
        </Button>
      </div>
      <!-- Background Glow Decor -->
      <div class="absolute -right-10 -bottom-10 w-60 h-60 bg-primary/10 rounded-full blur-3xl pointer-events-none"></div>
    </div>

    <!-- 4 Stat Cards Futuristik (ui-mantap.html) Menggunakan Komponen Modular Card & Badge -->
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
            <span class="text-2xl font-bold text-foreground font-mono">1,842</span>
            <Badge variant="outline" class="text-[11px] text-emerald-500 border-emerald-500/30 font-medium flex items-center gap-1">
              <ArrowUpRight class="w-3 h-3" /> +12%
            </Badge>
          </div>
          <p class="text-[11px] text-muted-foreground mt-1">Terdaftar di server BSrE BSSN</p>
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
            <span class="text-2xl font-bold text-foreground font-mono">1,839</span>
            <span class="text-xs text-emerald-400 font-medium font-mono">99.8%</span>
          </div>
          <p class="text-[11px] text-muted-foreground mt-1">Integritas hash SHA-256 terjaga</p>
        </CardContent>
      </Card>

      <!-- Card 3: Pending TTE -->
      <Card class="glass-panel hover:border-amber-500/40 transition-all border-border shadow-xs cursor-pointer" @click="selectTab('inbox')">
        <CardContent class="p-5">
          <div class="flex items-center justify-between text-muted-foreground">
            <span class="text-xs font-medium uppercase tracking-wider">Pending TTE</span>
            <div class="w-8 h-8 rounded-lg bg-amber-500/10 text-amber-500 flex items-center justify-center">
              <Clock class="w-4 h-4" />
            </div>
          </div>
          <div class="mt-3 flex items-baseline justify-between">
            <span class="text-2xl font-bold text-foreground font-mono">{{ pendingInboxCount }}</span>
            <Badge variant="outline" class="text-[11px] border-amber-500/30 text-amber-500 font-medium">
              Membutuhkan Paraf
            </Badge>
          </div>
          <p class="text-[11px] text-muted-foreground mt-1">Antrean tanda tangan elektronik</p>
        </CardContent>
      </Card>

      <!-- Card 4: Sertifikat Digital P12 -->
      <Card class="glass-panel hover:border-blue-500/40 transition-all border-border shadow-xs">
        <CardContent class="p-5">
          <div class="flex items-center justify-between text-muted-foreground">
            <span class="text-xs font-medium uppercase tracking-wider">Sertifikat Digital P12</span>
            <div class="w-8 h-8 rounded-lg bg-blue-500/10 text-blue-400 flex items-center justify-center">
              <Key class="w-4 h-4" />
            </div>
          </div>
          <div class="mt-3 flex items-baseline justify-between">
            <span class="text-2xl font-bold text-foreground">Aktif</span>
            <span class="text-xs text-primary font-mono font-semibold">RSA 2048-bit</span>
          </div>
          <p class="text-[11px] text-muted-foreground mt-1">BSrE BSSN CA Valid</p>
        </CardContent>
      </Card>
    </div>

    <!-- Navigation Menggunakan Komponen Modular AppTabs -->
    <AppTabs
      v-model="currentTab"
      :tabs="tabItems"
      :default-tab="currentTab"
      @tab-change="onTabChanged"
    >
      <!-- TAB 1: SURAT KEMATIAN RANAP (PRIORITAS TTE) -->
      <template #kematian_ranap>
        <SuratKematianRanapWidget
          @document-created="onDocumentCreated"
          @view-generated="openViewer"
        />
      </template>

      <!-- TAB 2: SIGNATURE INBOX (BATCH SIGN) -->
      <template #inbox>
        <PendingTteInbox
          ref="inboxRef"
          @preview-doc="openViewer"
          @batch-signed="onBatchSigned"
        />
      </template>

      <!-- TAB 3: LEMBAR KONSULTASI SIMRS -->
      <template #simrs>
        <SimrsDocWidget
          @document-created="onDocumentCreated"
          @view-generated="openViewer"
        />
      </template>

      <!-- TAB 4: DAFTAR SEMUA DOKUMEN & RIWAYAT TTE -->
      <template #list>
        <DocumentList
          ref="docListRef"
          :user-role="currentUser?.role || 'dokter'"
          @view-document="openViewer"
        />
      </template>

      <!-- TAB 5: PENCARIAN VEKTOR (PGVECTOR AI) -->
      <template #vector>
        <Card class="glass-panel border-border shadow-sm">
          <CardHeader>
            <CardTitle class="text-base font-bold text-foreground">
              Pencarian Semantik Rekam Medis (PostgreSQL pgvector)
            </CardTitle>
            <CardDescription class="text-xs text-muted-foreground">
              Cari dokumen rekam medis atau surat kematian berdasarkan kemiripan makna penyebab kematian, keluhan klinis, atau diagnosa menggunakan representasi vektor 1536-dimensi.
            </CardDescription>
          </CardHeader>

          <CardContent class="space-y-4">
            <div class="grid grid-cols-1 md:grid-cols-12 gap-3 items-end">
              <div class="md:col-span-10">
                <AppInput
                  id="vector-search-query"
                  label="Kata Kunci Klinis / Diagnosa ICD-10"
                  v-model="vectorQuery"
                  placeholder="Ketik penyebab kematian atau diagnosa (contoh: 'Cardiac arrest Respiratory arrest')..."
                  @keyup.enter="doVectorSearch"
                />
              </div>
              <div class="md:col-span-2">
                <Button
                  class="w-full bg-primary text-primary-foreground text-xs font-bold h-9 rounded-xl"
                  :disabled="isSearchingVector"
                  @click="doVectorSearch"
                >
                  {{ isSearchingVector ? 'Mencari...' : 'Cari Vektor' }}
                </Button>
              </div>
            </div>

            <div v-if="vectorResults.length > 0" class="space-y-2 pt-2">
              <div class="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Hasil Kemiripan Vektor:</div>
              <Card
                v-for="res in vectorResults"
                :key="res.id"
                class="glass-panel hover:border-primary/40 border-border cursor-pointer transition-colors"
                @click="openViewer(res)"
              >
                <CardContent class="p-4 flex items-center justify-between">
                  <div>
                    <div class="font-bold text-foreground text-sm">{{ res.title || res.filename }}</div>
                    <div class="text-xs text-muted-foreground mt-0.5">{{ res.description || 'Tanpa deskripsi' }}</div>
                    <div class="text-[10px] text-muted-foreground mt-1">
                      Kunjungan #{{ res.kunjungan_id }} • Tipe: {{ res.document_type }} • Status TTE: {{ res.tte_status }}
                    </div>
                  </div>
                  <Badge variant="outline" class="border-primary/40 text-primary font-bold text-xs">
                    Lihat PDF
                  </Badge>
                </CardContent>
              </Card>
            </div>
            <div v-else-if="hasSearchedVector" class="text-center py-8 text-xs text-muted-foreground">
              Tidak ditemukan dokumen yang cocok dengan vektor pencarian.
            </div>
          </CardContent>
        </Card>
      </template>
    </AppTabs>

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
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
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
  ArrowUpRight
} from 'lucide-vue-next'

import PendingTteInbox from '@/widgets/PendingTteInbox.vue'
import SuratKematianRanapWidget from '@/widgets/SuratKematianRanapWidget.vue'
import SimrsDocWidget from '@/widgets/SimrsDocWidget.vue'
import DocumentList from '@/widgets/DocumentList.vue'
import DocumentViewer from '@/widgets/DocumentViewer.vue'

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
    default: 'kematian_ranap'
  }
})

const emit = defineEmits(['refresh-notifications', 'switch-tab'])

const isPageLoading = ref(false)
const currentTab = ref(props.activeNav || 'kematian_ranap')
const inboxRef = ref(null)
const docListRef = ref(null)
const selectedDoc = ref(null)
const isViewerOpen = ref(false)
const pendingInboxCount = ref(props.pendingCount || 0)

const tabItems = computed(() => [
  { value: 'kematian_ranap', label: '🏥 Surat Kematian Ranap (Prioritas TTE)' },
  { value: 'inbox', label: `📥 Signature Inbox (${pendingInboxCount.value})` },
  { value: 'simrs', label: '📋 Lembar Konsultasi SIMRS' },
  { value: 'list', label: '📂 Daftar Semua Dokumen & TTE' },
  { value: 'vector', label: '🧠 Pencarian Semantik (AI pgvector)' }
])

const vectorQuery = ref('Cardiac arrest Respiratory arrest')
const vectorResults = ref([])
const isSearchingVector = ref(false)
const hasSearchedVector = ref(false)

watch(
  () => props.pendingCount,
  (val) => {
    pendingInboxCount.value = val
  }
)

watch(
  () => props.activeNav,
  (val) => {
    if (val && val !== currentTab.value) {
      currentTab.value = val
    }
  }
)

const selectTab = (tabVal) => {
  currentTab.value = tabVal
  emit('switch-tab', tabVal)
}

const onTabChanged = (val) => {
  currentTab.value = val
  emit('switch-tab', val)
}

const openViewer = (doc) => {
  selectedDoc.value = doc
  isViewerOpen.value = true
}

const onBatchSigned = (result) => {
  pendingInboxCount.value = Math.max(0, pendingInboxCount.value - (result.signed_count || 0))
  emit('refresh-notifications')
  if (docListRef.value) {
    docListRef.value.loadDocuments()
  }
}

const onDocumentCreated = () => {
  emit('refresh-notifications')
  if (inboxRef.value) {
    inboxRef.value.loadPendingDocs()
  }
  if (docListRef.value) {
    docListRef.value.loadDocuments()
  }
}

const doVectorSearch = async () => {
  if (!vectorQuery.value) return
  isSearchingVector.value = true
  hasSearchedVector.value = true
  try {
    const res = await documentApi.semanticSearch(vectorQuery.value, 5)
    vectorResults.value = res.data.data
  } catch (err) {
    console.error('Vector search error:', err)
  } finally {
    isSearchingVector.value = false
  }
}

const handleOpenInbox = () => {
  selectTab('inbox')
  if (inboxRef.value) {
    inboxRef.value.loadPendingDocs()
  }
}

const handleNavTabChange = (e) => {
  if (e.detail) {
    if (e.detail === 'dashboard') {
      currentTab.value = 'kematian_ranap'
      window.scrollTo({ top: 0, behavior: 'smooth' })
    } else {
      currentTab.value = e.detail
      if (e.detail === 'inbox' && inboxRef.value) {
        inboxRef.value.loadPendingDocs()
      }
    }
    emit('switch-tab', e.detail)
  }
}

onMounted(() => {
  window.addEventListener('open-inbox-tte', handleOpenInbox)
  window.addEventListener('nav-tab-change', handleNavTabChange)
})

onUnmounted(() => {
  window.removeEventListener('open-inbox-tte', handleOpenInbox)
  window.removeEventListener('nav-tab-change', handleNavTabChange)
})
</script>
