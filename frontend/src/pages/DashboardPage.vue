<template>
  <div class="space-y-6">
    <!-- Hero / Status Banner Menggunakan Komponen Modular Card & Badge -->
    <Card class="bg-gradient-to-r from-blue-700 via-indigo-700 to-slate-800 border-none text-white shadow-md">
      <CardContent class="p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <Badge class="bg-blue-500/30 text-blue-100 border border-blue-400/30 mb-2">
            SIMRS MySQL Read-Only Sync & Batch TTE BSrE Active
          </Badge>
          <h2 class="text-xl md:text-2xl font-black tracking-tight">
            Layanan Dokumen & TTE BSrE (Otomatisasi SIMRS)
          </h2>
          <p class="text-xs md:text-sm text-blue-100/85 mt-1 max-w-2xl leading-relaxed">
            Dokumen SIMRS (Surat Keterangan Kematian Ranap, Lembar Konsultasi, Resume Medis) ditarik otomatis melalui koneksi <strong>MySQL Read-Only (SELECT-only)</strong> ke Signature Inbox tanpa mengubah kode SIMRS.
          </p>
        </div>

        <div class="text-right hidden sm:block">
          <div class="text-[11px] text-emerald-300 uppercase font-bold">Penandatangan Aktif</div>
          <div class="text-sm font-bold">{{ currentUser?.nama }}</div>
          <div class="text-[11px] text-blue-100">Sertifikat Elektronik BSrE BSSN Terhubung</div>
        </div>
      </CardContent>
    </Card>

    <!-- Navigation Menggunakan Komponen Modular AppTabs -->
    <AppTabs
      :tabs="tabItems"
      :default-tab="currentTab"
      @tab-change="(val) => (currentTab = val)"
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
        <Card class="border-slate-200 shadow-sm bg-white">
          <CardHeader>
            <CardTitle class="text-base font-bold text-slate-800">
              Pencarian Semantik Rekam Medis (PostgreSQL pgvector)
            </CardTitle>
            <CardDescription class="text-xs text-slate-500">
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
                  class="w-full bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold h-9"
                  :disabled="isSearchingVector"
                  @click="doVectorSearch"
                >
                  {{ isSearchingVector ? 'Mencari...' : 'Cari Vektor' }}
                </Button>
              </div>
            </div>

            <div v-if="vectorResults.length > 0" class="space-y-2 pt-2">
              <div class="text-xs font-semibold text-slate-500 uppercase tracking-wider">Hasil Kemiripan Vektor:</div>
              <Card
                v-for="res in vectorResults"
                :key="res.id"
                class="bg-slate-50 hover:bg-indigo-50/60 border-slate-200 cursor-pointer transition-colors"
                @click="openViewer(res)"
              >
                <CardContent class="p-4 flex items-center justify-between">
                  <div>
                    <div class="font-bold text-slate-800 text-sm">{{ res.title || res.filename }}</div>
                    <div class="text-xs text-slate-500 mt-0.5">{{ res.description || 'Tanpa deskripsi' }}</div>
                    <div class="text-[10px] text-slate-400 mt-1">
                      Kunjungan #{{ res.kunjungan_id }} • Tipe: {{ res.document_type }} • Status TTE: {{ res.tte_status }}
                    </div>
                  </div>
                  <Badge class="bg-indigo-100 text-indigo-700 font-bold text-xs">
                    Lihat PDF
                  </Badge>
                </CardContent>
              </Card>
            </div>
            <div v-else-if="hasSearchedVector" class="text-center py-8 text-xs text-slate-400">
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { documentApi } from '@/services/api'
import AppTabs from '@/components/AppTabs.vue'
import AppInput from '@/components/AppInput.vue'
import AppDialog from '@/components/AppDialog.vue'
import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

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
  }
})

const emit = defineEmits(['refresh-notifications'])

const currentTab = ref('kematian_ranap')
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
  currentTab.value = 'inbox'
  if (inboxRef.value) {
    inboxRef.value.loadPendingDocs()
  }
}

onMounted(() => {
  window.addEventListener('open-inbox-tte', handleOpenInbox)
})

onUnmounted(() => {
  window.removeEventListener('open-inbox-tte', handleOpenInbox)
})
</script>
